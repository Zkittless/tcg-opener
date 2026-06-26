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


# ── TCGdex Price Fetcher ──────────────────────────────────────────────────────
# Completely free, no API key, no rate limit for reasonable use.
# Returns TCGPlayer USD market prices + Cardmarket EUR prices.
# Endpoint: GET https://api.tcgdex.net/v2/en/cards/{card_id}
# Pricing is embedded in the card response — no separate call needed.
#
# card_id format: same as pokemontcg.io (e.g. "sv8pt5-75", "swsh3-136")
#
# In-process cache means each unique card ID is only fetched once per
# bot session regardless of how many times it's pulled.

_TCGDEX_BASE   = "https://api.tcgdex.net/v2/en/cards"
_tcgdex_session: Optional[aiohttp.ClientSession] = None
_tcgdex_cache:   dict[str, float | None] = {}   # card_id -> USD price


async def _get_tcgdex_session() -> aiohttp.ClientSession:
    global _tcgdex_session
    if _tcgdex_session is None or _tcgdex_session.closed:
        _tcgdex_session = aiohttp.ClientSession(
            headers={"User-Agent": "PokemonPackBot/1.0"},
            timeout=aiohttp.ClientTimeout(total=10),
        )
    return _tcgdex_session


async def fetch_tcgdex_price(card_id: str) -> float | None:
    """
    Fetch USD market price for a card from TCGdex (free, no key).
    card_id is the pokemontcg.io ID e.g. 'sv8pt5-75'.
    Returns USD market price or None if unavailable.
    Results are cached in-process for the bot's lifetime.
    """
    if card_id in _tcgdex_cache:
        return _tcgdex_cache[card_id]

    try:
        session = await _get_tcgdex_session()
        url     = f"{_TCGDEX_BASE}/{card_id}"
        async with session.get(url) as resp:
            if resp.status == 404:
                _tcgdex_cache[card_id] = None
                return None
            if resp.status != 200:
                log.warning(f"TCGdex returned {resp.status} for {card_id}")
                return None  # don't cache errors — retry next time
            data = await resp.json()

        pricing = data.get("pricing", {})

        # Prefer TCGPlayer USD market price
        tcgp = pricing.get("tcgplayer", {})
        for variant in ("holo", "normal", "reverse"):
            v = tcgp.get(variant, {})
            if v.get("marketPrice") is not None:
                price = float(v["marketPrice"])
                _tcgdex_cache[card_id] = price
                log.info(f"TCGdex: {card_id} = ${price:.2f} (TCGPlayer {variant})")
                return price

        # Fall back to Cardmarket EUR (convert roughly — 1 EUR ≈ 1.08 USD)
        cm = pricing.get("cardmarket", {})
        for field in ("avg7", "trend", "avg30", "avg"):
            val = cm.get(field)
            if val is not None:
                price = round(float(val) * 1.08, 2)
                _tcgdex_cache[card_id] = price
                log.info(f"TCGdex: {card_id} = ${price:.2f} (Cardmarket EUR→USD)")
                return price

        _tcgdex_cache[card_id] = None
        return None

    except Exception as e:
        log.error(f"TCGdex fetch error for {card_id}: {e}")
        return None
