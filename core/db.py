"""
core/db.py — All database operations.
"""

import aiosqlite
import logging
import os
from config import DB_PATH

log = logging.getLogger("db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
    discord_id   TEXT PRIMARY KEY,
    username     TEXT,
    packs_opened INTEGER DEFAULT 0,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS collection (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id   TEXT NOT NULL,
    card_id      TEXT NOT NULL,
    card_name    TEXT,
    set_id       TEXT,
    set_name     TEXT,
    rarity       TEXT,
    image_url    TEXT,
    market_price REAL,
    count        INTEGER DEFAULT 1,
    keep         INTEGER DEFAULT 1,
    obtained_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discord_id) REFERENCES users(discord_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_card
    ON collection(discord_id, card_id);

CREATE TABLE IF NOT EXISTS pack_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    set_id     TEXT NOT NULL,
    set_name   TEXT,
    opened_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

# Migration: add columns to existing DBs that predate these fields
MIGRATIONS = [
    "ALTER TABLE collection ADD COLUMN market_price REAL",
    "ALTER TABLE collection ADD COLUMN keep INTEGER DEFAULT 1",
    # Normalize NULLs that exist before the column was added
    "UPDATE collection SET keep = 1 WHERE keep IS NULL",
]


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        # Run migrations safely (ignore if column already exists)
        for sql in MIGRATIONS:
            try:
                await db.execute(sql)
            except Exception:
                pass
        await db.commit()
    log.info(f"DB ready at {DB_PATH}")


# ── User ops ──────────────────────────────────────────────────────────────────

async def ensure_user(discord_id: str, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO users (discord_id, username) VALUES (?, ?)
               ON CONFLICT(discord_id) DO UPDATE SET username=excluded.username""",
            (discord_id, username),
        )
        await db.commit()


async def increment_packs_opened(discord_id: str, count: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET packs_opened = packs_opened + ? WHERE discord_id = ?",
            (count, discord_id),
        )
        await db.commit()


async def get_user_stats(discord_id: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


# ── Collection ops ────────────────────────────────────────────────────────────

async def add_cards_to_collection(discord_id: str, cards: list[dict]):
    from core.tcg_api import get_card_price
    async with aiosqlite.connect(DB_PATH) as db:
        for card in cards:
            if card.get("_slot") == "energy":
                continue
            card_id   = card.get("id", "")
            card_name = card.get("name", "")
            set_id    = card.get("set", {}).get("id", "")
            set_name  = card.get("set", {}).get("name", "")
            rarity    = card.get("rarity", "")
            image_url = card.get("images", {}).get("large", "")
            price, _  = get_card_price(card)

            await db.execute(
                """INSERT INTO collection
                       (discord_id, card_id, card_name, set_id, set_name, rarity, image_url, market_price, count)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                   ON CONFLICT(discord_id, card_id)
                   DO UPDATE SET count = count + 1,
                                 market_price = excluded.market_price,
                                 obtained_at = CURRENT_TIMESTAMP""",
                (discord_id, card_id, card_name, set_id, set_name, rarity, image_url, price),
            )
        await db.commit()


async def get_collection(
    discord_id: str,
    set_id: str | None = None,
    min_value: float | None = None,
    keep: bool | None = None,          # True=keep, False=discard, None=all
    page: int = 1,
    per_page: int = 1,
) -> tuple[list[dict], int]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        offset = (page - 1) * per_page

        where  = "WHERE discord_id = ?"
        params: list = [discord_id]

        if set_id:
            where += " AND set_id = ?"
            params.append(set_id)
        if min_value is not None:
            where += " AND market_price >= ?"
            params.append(min_value)
        if keep is True:
            where += " AND keep = 1"
        elif keep is False:
            where += " AND keep = 0"

        async with db.execute(f"SELECT COUNT(*) FROM collection {where}", params) as cur:
            total = (await cur.fetchone())[0]

        async with db.execute(
            f"SELECT * FROM collection {where} ORDER BY card_name, card_id LIMIT ? OFFSET ?",
            params + [per_page, offset],
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows], total


async def set_card_keep(discord_id: str, card_id: str, keep: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE collection SET keep = ? WHERE discord_id = ? AND card_id = ?",
            (1 if keep else 0, discord_id, card_id),
        )
        await db.commit()


async def bulk_set_keep_by_value(discord_id: str, min_keep_value: float):
    """Mark keep=1 for cards >= threshold, keep=0 for cards below."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE collection SET keep = 1 WHERE discord_id = ? AND market_price >= ?",
            (discord_id, min_keep_value),
        )
        await db.execute(
            "UPDATE collection SET keep = 0 WHERE discord_id = ? AND (market_price < ? OR market_price IS NULL)",
            (discord_id, min_keep_value),
        )
        await db.commit()


async def get_collection_summary(discord_id: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT set_id, set_name,
                      COUNT(DISTINCT card_id)          AS unique_cards,
                      SUM(count)                       AS total_cards,
                      ROUND(SUM(COALESCE(market_price,0) * count), 2) AS set_value
               FROM collection WHERE discord_id = ?
               GROUP BY set_id ORDER BY set_value DESC""",
            (discord_id,),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_collection_card_count(discord_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT SUM(count) FROM collection WHERE discord_id = ?", (discord_id,)
        ) as cur:
            return (await cur.fetchone())[0] or 0


async def get_unique_card_count(discord_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(DISTINCT card_id) FROM collection WHERE discord_id = ?", (discord_id,)
        ) as cur:
            return (await cur.fetchone())[0] or 0


async def get_collection_total_value(discord_id: str) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT ROUND(SUM(COALESCE(market_price,0) * count), 2) FROM collection WHERE discord_id = ?",
            (discord_id,),
        ) as cur:
            return (await cur.fetchone())[0] or 0.0


async def get_discard_pile(discord_id: str) -> list[dict]:
    """All cards marked keep=0, sorted by value desc."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM collection WHERE discord_id = ? AND keep = 0
               ORDER BY COALESCE(market_price,0) DESC""",
            (discord_id,),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def log_pack_open(discord_id: str, set_id: str, set_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO pack_history (discord_id, set_id, set_name) VALUES (?, ?, ?)",
            (discord_id, set_id, set_name),
        )
        await db.commit()


async def get_pack_history(discord_id: str, limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT set_name, COUNT(*) as packs, MAX(opened_at) as last_opened
               FROM pack_history WHERE discord_id = ?
               GROUP BY set_id, set_name ORDER BY last_opened DESC LIMIT ?""",
            (discord_id, limit),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]
