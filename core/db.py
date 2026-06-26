"""
core/db.py
All database operations. Uses aiosqlite for async access.
"""

import aiosqlite
import logging
import os
from config import DB_PATH

log = logging.getLogger("db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Schema
# ─────────────────────────────────────────────────────────────────────────────

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
    discord_id  TEXT PRIMARY KEY,
    username    TEXT,
    packs_opened INTEGER DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS collection (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id  TEXT NOT NULL,
    card_id     TEXT NOT NULL,
    card_name   TEXT,
    set_id      TEXT,
    set_name    TEXT,
    rarity      TEXT,
    image_url   TEXT,
    count       INTEGER DEFAULT 1,
    obtained_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discord_id) REFERENCES users(discord_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_card
    ON collection(discord_id, card_id);

CREATE TABLE IF NOT EXISTS pack_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id  TEXT NOT NULL,
    set_id      TEXT NOT NULL,
    set_name    TEXT,
    opened_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()
    log.info(f"DB ready at {DB_PATH}")


# ─────────────────────────────────────────────────────────────────────────────
#  User ops
# ─────────────────────────────────────────────────────────────────────────────

async def ensure_user(discord_id: str, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (discord_id, username)
            VALUES (?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET username=excluded.username
            """,
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
        async with db.execute(
            "SELECT * FROM users WHERE discord_id = ?", (discord_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


# ─────────────────────────────────────────────────────────────────────────────
#  Collection ops
# ─────────────────────────────────────────────────────────────────────────────

async def add_cards_to_collection(discord_id: str, cards: list[dict]):
    """
    Upsert a batch of cards into the user's collection.
    Each card dict should have: id, name, set.id, set.name, rarity, images.large
    """
    async with aiosqlite.connect(DB_PATH) as db:
        for card in cards:
            card_id   = card.get("id", "")
            card_name = card.get("name", "")
            set_id    = card.get("set", {}).get("id", "")
            set_name  = card.get("set", {}).get("name", "")
            rarity    = card.get("rarity", "")
            image_url = card.get("images", {}).get("large", "")

            await db.execute(
                """
                INSERT INTO collection
                    (discord_id, card_id, card_name, set_id, set_name, rarity, image_url, count)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(discord_id, card_id)
                DO UPDATE SET count = count + 1, obtained_at = CURRENT_TIMESTAMP
                """,
                (discord_id, card_id, card_name, set_id, set_name, rarity, image_url),
            )
        await db.commit()


async def get_collection(
    discord_id: str,
    set_id: str | None = None,
    page: int = 1,
    per_page: int = 10,
) -> tuple[list[dict], int]:
    """Return (cards, total_count) for pagination."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        offset = (page - 1) * per_page

        where = "WHERE discord_id = ?"
        params: list = [discord_id]
        if set_id:
            where += " AND set_id = ?"
            params.append(set_id)

        async with db.execute(
            f"SELECT COUNT(*) FROM collection {where}", params
        ) as cur:
            total = (await cur.fetchone())[0]

        params_paged = params + [per_page, offset]
        async with db.execute(
            f"""
            SELECT * FROM collection {where}
            ORDER BY set_id, card_id
            LIMIT ? OFFSET ?
            """,
            params_paged,
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows], total


async def get_collection_summary(discord_id: str) -> list[dict]:
    """Return per-set card counts for the collection overview."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT set_id, set_name,
                   COUNT(DISTINCT card_id) AS unique_cards,
                   SUM(count)              AS total_cards
            FROM collection
            WHERE discord_id = ?
            GROUP BY set_id
            ORDER BY set_name
            """,
            (discord_id,),
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def get_collection_card_count(discord_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT SUM(count) FROM collection WHERE discord_id = ?",
            (discord_id,),
        ) as cur:
            row = await cur.fetchone()
            return row[0] or 0


async def get_unique_card_count(discord_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(DISTINCT card_id) FROM collection WHERE discord_id = ?",
            (discord_id,),
        ) as cur:
            row = await cur.fetchone()
            return row[0] or 0


# ─────────────────────────────────────────────────────────────────────────────
#  Pack history
# ─────────────────────────────────────────────────────────────────────────────

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
            """
            SELECT set_name, COUNT(*) as packs, MAX(opened_at) as last_opened
            FROM pack_history
            WHERE discord_id = ?
            GROUP BY set_id, set_name
            ORDER BY last_opened DESC
            LIMIT ?
            """,
            (discord_id, limit),
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]
