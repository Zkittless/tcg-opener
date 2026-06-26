"""
core/tcg_api.py
Async wrapper around the Pokémon TCG API (pokemontcg.io).
All data is cached in-memory after first fetch to minimize API calls.
"""

import aiohttp
import asyncio
import logging
from typing import Optional
from config import POKEMON_TCG_API_KEY

log = logging.getLogger("tcg_api")

BASE_URL = "https://api.pokemontcg.io/v2"
HEADERS  = {"X-Api-Key": POKEMON_TCG_API_KEY} if POKEMON_TCG_API_KEY else {}

# ── In-memory caches ─────────────────────────────────────────────────────────
_set_cache:  dict[str, dict] = {}   # set_id  -> set object
_card_cache: dict[str, list] = {}   # set_id  -> [card, ...]
_session:    Optional[aiohttp.ClientSession] = None


async def get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        timeout = aiohttp.ClientTimeout(total=30)
        _session = aiohttp.ClientSession(headers=HEADERS, timeout=timeout)
    return _session


async def close_session():
    global _session
    if _session and not _session.closed:
        await _session.close()


# ── Sets ─────────────────────────────────────────────────────────────────────

async def fetch_all_sets() -> list[dict]:
    """Return every set from the API, sorted by release date descending."""
    if _set_cache:
        return sorted(_set_cache.values(), key=lambda s: s.get("releaseDate", ""), reverse=True)

    session = await get_session()
    page, page_size = 1, 250
    all_sets = []

    while True:
        params = {"page": page, "pageSize": page_size, "orderBy": "-releaseDate"}
        try:
            async with session.get(f"{BASE_URL}/sets", params=params) as resp:
                if resp.status != 200:
                    log.error(f"Sets fetch failed: HTTP {resp.status}")
                    break
                data = await resp.json()
        except Exception as e:
            log.error(f"Sets fetch error: {e}")
            break

        sets = data.get("data", [])
        all_sets.extend(sets)
        for s in sets:
            _set_cache[s["id"]] = s

        if len(sets) < page_size:
            break
        page += 1

    log.info(f"Fetched {len(all_sets)} sets from TCG API.")
    return all_sets


async def fetch_set(set_id: str) -> Optional[dict]:
    if set_id in _set_cache:
        return _set_cache[set_id]
    session = await get_session()
    try:
        async with session.get(f"{BASE_URL}/sets/{set_id}") as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            s = data.get("data")
            if s:
                _set_cache[set_id] = s
            return s
    except Exception as e:
        log.error(f"fetch_set({set_id}) error: {e}")
        return None


# ── Cards ─────────────────────────────────────────────────────────────────────

async def fetch_cards_for_set(set_id: str) -> list[dict]:
    """Fetch every card in a set, cached after first call."""
    if set_id in _card_cache:
        return _card_cache[set_id]

    session  = await get_session()
    page     = 1
    page_size = 250
    all_cards: list[dict] = []

    while True:
        params = {
            "q":        f"set.id:{set_id}",
            "page":     page,
            "pageSize": page_size,
            "orderBy":  "number",
        }
        try:
            async with session.get(f"{BASE_URL}/cards", params=params) as resp:
                if resp.status != 200:
                    log.error(f"Cards fetch failed for {set_id}: HTTP {resp.status}")
                    break
                data = await resp.json()
        except Exception as e:
            log.error(f"Cards fetch error for {set_id}: {e}")
            break

        cards = data.get("data", [])
        all_cards.extend(cards)
        if len(cards) < page_size:
            break
        page += 1

    _card_cache[set_id] = all_cards
    log.info(f"Fetched {len(all_cards)} cards for set {set_id}.")
    return all_cards


async def fetch_card(card_id: str) -> Optional[dict]:
    session = await get_session()
    try:
        async with session.get(f"{BASE_URL}/cards/{card_id}") as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("data")
    except Exception as e:
        log.error(f"fetch_card({card_id}) error: {e}")
        return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_card_image(card: dict, hires: bool = True) -> str:
    """Return the best available image URL for a card."""
    images = card.get("images", {})
    if hires and images.get("large"):
        return images["large"]
    return images.get("small", "")


def get_set_logo(s: dict) -> str:
    return s.get("images", {}).get("logo", "")


def get_set_symbol(s: dict) -> str:
    return s.get("images", {}).get("symbol", "")


def card_rarity(card: dict) -> str:
    return card.get("rarity", "Common")


def card_number(card: dict) -> str:
    return card.get("number", "0")


def card_name(card: dict) -> str:
    return card.get("name", "Unknown")


def is_secret_rare(card: dict, set_total: int) -> bool:
    """Cards numbered above the printed set total are secret rares."""
    try:
        return int(card.get("number", 0)) > set_total
    except (ValueError, TypeError):
        return False


def get_card_price(card: dict) -> tuple[float | None, str]:
    """
    Return (price_usd, source_label) for the best available market price.

    Priority order:
      1. TCGPlayer market price  (most cards, most up-to-date)
      2. TCGPlayer low price     (fallback if no market)
      3. Cardmarket avg sell     (European market, used when TCGPlayer absent)

    Returns (None, "") when no price data exists.

    TCGPlayer price buckets tried, in order:
      holofoil → reverseHolofoil → 1stEditionHolofoil → normal → unlimited
    """
    # ── TCGPlayer ────────────────────────────────────────────────────────────
    tcg = card.get("tcgplayer", {}).get("prices", {})
    bucket_order = [
        "holofoil",
        "reverseHolofoil",
        "1stEditionHolofoil",
        "normal",
        "unlimited",
        "1stEdition",
    ]
    for bucket in bucket_order:
        b = tcg.get(bucket, {})
        if b:
            market = b.get("market")
            if market is not None:
                return float(market), "TCGPlayer"
            low = b.get("low")
            if low is not None:
                return float(low), "TCGPlayer (low)"

    # ── Cardmarket ───────────────────────────────────────────────────────────
    cm = card.get("cardmarket", {}).get("prices", {})
    avg = cm.get("averageSellPrice") or cm.get("avg1")
    if avg is not None:
        return float(avg), "Cardmarket"

    return None, ""


def format_price(card: dict) -> str:
    """Return a formatted price string like '$4.25' or '' if unknown."""
    price, source = get_card_price(card)
    if price is None:
        return ""
    if price == 0.0:
        return "~$0.00"
    return f"${price:,.2f}"
