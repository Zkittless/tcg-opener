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
    Return (price_usd, source_label).

    NOTE: pokemontcg.io only returns price data when an API key is provided.
    Without a key the tcgplayer/cardmarket fields are present but empty dicts.
    We try all known bucket names and fall through gracefully.
    """
    # ── TCGPlayer ─────────────────────────────────────────────────────────────
    tcg = card.get("tcgplayer", {})
    prices = tcg.get("prices", {}) if tcg else {}
    bucket_order = [
        "holofoil", "reverseHolofoil", "1stEditionHolofoil",
        "1stEditionNormal", "normal", "unlimited",
    ]
    for bucket in bucket_order:
        b = prices.get(bucket, {})
        if not b:
            continue
        market = b.get("market")
        if market is not None:
            return float(market), "TCGPlayer"
        mid = b.get("mid")
        if mid is not None:
            return float(mid), "TCGPlayer (mid)"
        low = b.get("low")
        if low is not None:
            return float(low), "TCGPlayer (low)"

    # ── Cardmarket ────────────────────────────────────────────────────────────
    cm = card.get("cardmarket", {})
    cm_prices = cm.get("prices", {}) if cm else {}
    for field in ("averageSellPrice", "trendPrice", "avg7", "avg30", "avg1"):
        val = cm_prices.get(field)
        if val is not None:
            return float(val), "Cardmarket"

    return None, ""


def format_price(card: dict) -> str:
    """Return formatted price string like '$4.25' or '' if unavailable."""
    price, _ = get_card_price(card)
    if price is None:
        return ""
    return f"${price:,.2f}"



# ── TCGCSV Price Fetcher ──────────────────────────────────────────────────────
# tcgcsv.com is a free public mirror of TCGPlayer's price data, updated daily.
# No API key, no credits, no limits.
#
# Flow:
#   1. Fetch all Pokemon groups (sets) from TCGCSV — cached in memory
#   2. Match pokemontcg.io set_id to a TCGPlayer groupId via set name/abbreviation
#   3. Fetch all products + prices for that group in one call
#   4. Match cards by card number, cache all prices in DB
#
# This means the first pack from a new set costs ~2 HTTP calls total,
# and every subsequent pull from that set costs 0.

_TCGCSV_BASE = "https://tcgcsv.com/tcgplayer"
_POKEMON_CAT = 3   # TCGPlayer categoryId for Pokemon

_tcgcsv_session:  Optional[aiohttp.ClientSession] = None
_tcgcsv_groups:   Optional[list[dict]] = None   # cached group list
_tcgcsv_fetched:  set[str] = set()              # set_ids already fetched


async def _get_tcgcsv_session() -> aiohttp.ClientSession:
    global _tcgcsv_session
    if _tcgcsv_session is None or _tcgcsv_session.closed:
        _tcgcsv_session = aiohttp.ClientSession(
            headers={"User-Agent": "PokemonPackBot/1.0"},
            timeout=aiohttp.ClientTimeout(total=15),
        )
    return _tcgcsv_session


async def _get_tcgcsv_groups() -> list[dict]:
    """Fetch and cache the full list of Pokemon groups from TCGCSV."""
    global _tcgcsv_groups
    if _tcgcsv_groups is not None:
        return _tcgcsv_groups
    try:
        session = await _get_tcgcsv_session()
        async with session.get(f"{_TCGCSV_BASE}/{_POKEMON_CAT}/groups") as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            _tcgcsv_groups = data.get("results", [])
            log.info(f"TCGCSV: loaded {len(_tcgcsv_groups)} Pokemon groups")
            return _tcgcsv_groups
    except Exception as e:
        log.error(f"TCGCSV groups fetch error: {e}")
        return []


def _find_group_id(groups: list[dict], api_set: dict) -> Optional[int]:
    """
    Match a pokemontcg.io set object to a TCGPlayer groupId.
    Tries abbreviation match first, then name substring match.
    """
    ptcgo   = (api_set.get("ptcgoCode") or "").upper()
    name    = (api_set.get("name") or "").lower()

    for g in groups:
        abbr = (g.get("abbreviation") or "").upper()
        gname = (g.get("name") or "").lower()
        if ptcgo and abbr == ptcgo:
            return g["groupId"]
        if name and name in gname:
            return g["groupId"]
    return None


async def fetch_set_prices_tcgcsv(set_id: str) -> dict[str, float]:
    """
    Fetch all card prices for a set from TCGCSV.
    Returns {card_number: price} dict.
    """
    # Get the pokemontcg.io set object (already cached in memory)
    api_set = await fetch_set(set_id)
    if not api_set:
        return {}

    groups   = await _get_tcgcsv_groups()
    group_id = _find_group_id(groups, api_set)
    if not group_id:
        log.warning(f"TCGCSV: no group found for set {set_id}")
        return {}

    try:
        session = await _get_tcgcsv_session()

        # Fetch products (cards) — gives us productId → card number mapping
        async with session.get(f"{_TCGCSV_BASE}/{_POKEMON_CAT}/{group_id}/products") as resp:
            if resp.status != 200:
                return {}
            prod_data = await resp.json(content_type=None)
            products  = prod_data.get("results", [])

        # Build productId → card number map
        # extendedData contains [{name: "Number", value: "001/198"}, ...]
        prod_to_num: dict[int, str] = {}
        for p in products:
            pid  = p.get("productId")
            exts = p.get("extendedData", [])
            for ext in exts:
                if ext.get("name") == "Number":
                    # TCGPlayer stores "001/198" — we just want "1"
                    raw_num = ext.get("value", "").split("/")[0].lstrip("0") or "0"
                    prod_to_num[pid] = raw_num
                    break

        # Fetch prices
        async with session.get(f"{_TCGCSV_BASE}/{_POKEMON_CAT}/{group_id}/prices") as resp:
            if resp.status != 200:
                return {}
            price_data = await resp.json(content_type=None)
            prices     = price_data.get("results", [])

        # Build card_number → best market price
        num_to_price: dict[str, float] = {}
        for p in prices:
            pid    = p.get("productId")
            num    = prod_to_num.get(pid)
            if not num:
                continue
            market = p.get("marketPrice") or p.get("midPrice") or p.get("lowPrice")
            if market is not None:
                # Keep the highest price if multiple printings
                existing = num_to_price.get(num, 0.0)
                num_to_price[num] = max(existing, float(market))

        log.info(f"TCGCSV: fetched {len(num_to_price)} prices for {set_id} (group {group_id})")
        return num_to_price

    except Exception as e:
        log.error(f"TCGCSV price fetch error for {set_id}: {e}")
        return {}


async def fetch_tcgdex_price(card_id: str) -> float | None:
    """
    Look up a single card price via TCGCSV.
    Fetches the whole set's prices on first call, caches everything.
    card_id format: sv8pt5-75 (set_id-number)
    """
    if "-" not in card_id:
        return None

    set_id, number = card_id.rsplit("-", 1)
    # Strip leading zeros to match TCGPlayer's format
    number = number.lstrip("0") or "0"

    # Fetch entire set if not already done
    if set_id not in _tcgcsv_fetched:
        prices = await fetch_set_prices_tcgcsv(set_id)
        if prices:
            _tcgcsv_fetched.add(set_id)
            # Store all prices in the DB cache
            from core.db import store_cached_price
            for num, price in prices.items():
                await store_cached_price(f"{set_id}-{num}", price)
            # Also cache zero-padded variants (e.g. sv8pt5-075 → 75)
            # since pokemontcg.io uses unpadded numbers
            log.info(f"TCGCSV: cached {len(prices)} prices for {set_id}")

    # Now look up from DB cache
    from core.db import get_cached_price
    return await get_cached_price(card_id)
