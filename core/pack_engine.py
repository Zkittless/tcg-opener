"""
core/pack_engine.py

Simulates authentic Pokémon TCG booster pack openings with per-era card ordering
and the real "pack trick" applied automatically before the reveal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REAL PACK STRUCTURES (verified sources: PokéBeach, PokéPatch, Bulbapedia)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scarlet & Violet era (sv1 → sv8pt5 / Ascended Heroes):
  AS PRINTED (face-down, out of pack):
    [Energy card] [C][C][C][C] [U][U][U] [RH1][RH2] [HOLO/HIT]   + code card
  PACK TRICK: move the 1 Energy card from the back to the front
  REVEAL ORDER (after trick): C C C C  U U U  RH1 RH2  HOLO/HIT
  SV notes:
    - 2 reverse holo slots (vs 1 in SwSh)
    - If Illustration Rare pulled → replaces RH2 slot
    - Guaranteed foil (holo) in every pack — no non-holo rares
    - Ascended Heroes (sv8pt5): Energy and Poké Ball reverse holos in the
      two RH slots (Energy type pattern + Poké Ball/Rocket pattern); same 1-card trick

Sword & Shield era (swsh1 → swsh12pt5):
  AS PRINTED (face-down, out of pack):
    [C][C][C][C][C][C] [U][U][U] [RH] [RARE/HIT]   + code card
  PACK TRICK: move 4 cards from the back to the front
  REVEAL ORDER (after trick): C C  U  RH  RARE  ← then remaining C C C C  U U
  (More precisely: trick reveals RH then RARE as the final two)

Sun & Moon era (sm1 → sm12):
  Same structure as Sword & Shield.
  PACK TRICK: 4 cards from back to front

XY era (xy1 → xy12):
  AS PRINTED:
    [C][C][C][C][C][C] [U][U][U] [RH] [RARE/HIT]   + code card
  PACK TRICK: 3 cards from back to front
  REVEAL ORDER: C C C  U  RH  → then remaining C C C  U U  RARE

Black & White era (bw1 → bw11):
  Same as XY.
  PACK TRICK: 3 cards from back to front

HeartGold & SoulSilver (hgss1 → hgss4 / pl4):
  PACK TRICK: 3 cards from back to front

Platinum / Diamond & Pearl (pl1 → dp7):
  PACK TRICK: 3 cards from back to front

Classic / Wizards of the Coast (base1 → ex era end):
  AS PRINTED:
    [C][C][C][C][C] [U][U][U] [RARE] [E][E]   (2 Energy cards, no code card)
  PACK TRICK: 3 cards from back to front
  Note: Base Set packs have 11 cards total: 5 C + 3 U + 1 R + 2 Energy

e-Reader era (ex Expedition, Aquapolis, Skyridge):
  PACK TRICK: 2 cards from back to front (exception to the 3-card classic rule)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sources:
  PokéBeach  https://www.pokebeach.com/2023/03/scarlet-violet-booster-pack-configuration-finally-revealed
  PokéPatch  https://pokepatch.com/2022/07/26/how-to-open-pokemon-cards-card-trick-for-each-set/
  Bulbapedia https://bulbapedia.bulbagarden.net/wiki/Booster_pack_(TCG)
  PokéBeach  https://www.pokebeach.com/2026/01/ascended-heroes-set-guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import random
import logging
from dataclasses import dataclass
from typing import Optional
from core.tcg_api import fetch_cards_for_set, fetch_set, card_rarity, card_number

log = logging.getLogger("pack_engine")


# ─────────────────────────────────────────────────────────────────────────────
#  Rarity buckets
# ─────────────────────────────────────────────────────────────────────────────

COMMON_RARITIES     = {"Common"}
UNCOMMON_RARITIES   = {"Uncommon"}
RARE_RARITIES       = {"Rare", "Rare Holo"}
ULTRA_RARE_RARITIES = {
    "Rare Holo EX", "Rare Holo GX", "Rare Holo V", "Rare Holo VMAX",
    "Rare Holo VSTAR", "Rare Ultra", "Ultra Rare",
    "Double Rare",          # SV era Rare ex
    "Mega Attack Rare",     # Ascended Heroes
}
SPECIAL_RARITIES = {
    "Illustration Rare",         # SV era IR  — can land in RH2 slot
    "Special Illustration Rare", # SV era SIR
    "Trainer Gallery Rare Holo",
    "Trainer Gallery Ultra Rare",
    "Trainer Gallery Secret Rare",
    "Hyper Rare",                # SV era gold
    "Mega Hyper Rare",           # Ascended Heroes gold
    "Rare Secret",
    "Rare Rainbow",
    "LEGEND",
    "Rare BREAK",
    "Rare ACE",
    "Rare Shining",
    "Shiny Rare",
    "Shiny Ultra Rare",
    "Rare Shiny",
    "Rare Shiny GX",
    "Radiant Rare",
    "Amazing Rare",
}

def rarity_tier(rarity: str) -> int:
    """0=common 1=uncommon 2=rare 3=ultra 4=special/secret"""
    if rarity in COMMON_RARITIES:      return 0
    if rarity in UNCOMMON_RARITIES:    return 1
    if rarity in RARE_RARITIES:        return 2
    if rarity in ULTRA_RARE_RARITIES:  return 3
    if rarity in SPECIAL_RARITIES:     return 4
    return 0


# ─────────────────────────────────────────────────────────────────────────────
#  Era detection
# ─────────────────────────────────────────────────────────────────────────────

def detect_era(set_id: str) -> str:
    """
    Return a canonical era string from a set ID.
    Matches pokemontcg.io set ID prefixes exactly.
    """
    sid = set_id.lower()

    # Scarlet & Violet (includes Ascended Heroes sv8pt5, Prismatic sv8, etc.)
    if sid.startswith("sv"):
        return "sv"

    # Sword & Shield
    if sid.startswith("swsh"):
        return "swsh"

    # Sun & Moon
    if sid.startswith("sm"):
        return "sm"

    # XY
    if sid.startswith("xy"):
        return "xy"

    # Black & White
    if sid.startswith("bw"):
        return "bw"

    # HeartGold SoulSilver (hgss) and Platinum overlaps (pl3/pl4 are HGSS era)
    if sid.startswith("hgss") or sid in {"pl4"}:
        return "hgss"

    # Platinum
    if sid.startswith("pl"):
        return "pl"

    # Diamond & Pearl
    if sid.startswith("dp"):
        return "dp"

    # e-Reader era (Expedition, Aquapolis, Skyridge) — 2-card trick exception
    if sid in {"ecard1", "ecard2", "ecard3"}:
        return "ereader"

    # EX era (Ruby & Sapphire through Power Keepers)
    if sid.startswith("ex"):
        return "ex"

    # Everything else (Base Set, Jungle, Fossil, Neo, etc.) = classic WotC
    return "classic"


# ─────────────────────────────────────────────────────────────────────────────
#  Pack trick metadata
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PackTrick:
    era:            str
    cards_to_move:  int    # how many cards shift from back → front
    description:    str    # shown to user before the reveal
    set_note:       str    # any special per-set note (blank = generic)


PACK_TRICKS: dict[str, PackTrick] = {
    "sv": PackTrick(
        era="sv",
        cards_to_move=1,
        description=(
            "**Scarlet & Violet pack trick** — move **1 card** (the Basic Energy) "
            "from the back to the front before flipping."
        ),
        set_note="",
    ),
    "swsh": PackTrick(
        era="swsh",
        cards_to_move=4,
        description=(
            "**Sword & Shield pack trick** — move **4 cards** "
            "from the back to the front before flipping."
        ),
        set_note="",
    ),
    "sm": PackTrick(
        era="sm",
        cards_to_move=4,
        description=(
            "**Sun & Moon pack trick** — move **4 cards** "
            "from the back to the front before flipping."
        ),
        set_note="",
    ),
    "xy": PackTrick(
        era="xy",
        cards_to_move=3,
        description=(
            "**XY pack trick** — move **3 cards** "
            "from the back to the front before flipping."
        ),
        set_note="",
    ),
    "bw": PackTrick(
        era="bw",
        cards_to_move=3,
        description=(
            "**Black & White pack trick** — move **3 cards** "
            "from the back to the front before flipping."
        ),
        set_note="",
    ),
    "hgss": PackTrick(
        era="hgss",
        cards_to_move=3,
        description=(
            "**HeartGold & SoulSilver pack trick** — move **3 cards** "
            "from the back to the front before flipping."
        ),
        set_note="",
    ),
    "pl": PackTrick(
        era="pl",
        cards_to_move=3,
        description=(
            "**Platinum pack trick** — move **3 cards** "
            "from the back to the front before flipping."
        ),
        set_note="",
    ),
    "dp": PackTrick(
        era="dp",
        cards_to_move=3,
        description=(
            "**Diamond & Pearl pack trick** — move **3 cards** "
            "from the back to the front before flipping."
        ),
        set_note="",
    ),
    "ereader": PackTrick(
        era="ereader",
        cards_to_move=2,
        description=(
            "**e-Reader era pack trick** — move **2 cards** "
            "from the back to the front before flipping. "
            "(Exception to the usual 3-card classic rule.)"
        ),
        set_note="",
    ),
    "ex": PackTrick(
        era="ex",
        cards_to_move=3,
        description=(
            "**EX era pack trick** — move **3 cards** "
            "from the back to the front before flipping. "
            "Your last card will be the rare (holo, reverse holo, or EX card). "
            "Gold Stars (★) appear extremely rarely in the rare slot."
        ),
        set_note="Pack contains 1 Energy + 4 Commons + 3 Uncommons + 1 Reverse Holo + 1 Rare.",
    ),
    "classic": PackTrick(
        era="classic",
        cards_to_move=3,
        description=(
            "**Classic (WotC) pack trick** — move **3 cards** "
            "from the back to the front before flipping. "
            "Your last card will be the rare (holo or non-holo)."
        ),
        set_note="Pack contains 2 Energy cards + 5 Commons + 3 Uncommons + 1 Rare.",
    ),
}

# Per-set overrides for special sets with unique structure notes
SET_TRICK_NOTES: dict[str, str] = {
    "sv8pt5": (
        "⚡ **Ascended Heroes** has unique Energy-type and Poké Ball reverse holos "
        "instead of standard reverse foil patterns. Two RH slots — one Energy pattern, "
        "one Poké Ball/Team Rocket-R pattern. Still just **move 1 card** (the Basic Energy)."
    ),
    "sv8": (
        "✨ **Prismatic Evolutions** — standard SV structure. "
        "Move the Basic Energy (1 card) from back to front."
    ),
    "swsh12pt5": (
        "👑 **Crown Zenith** has Trainer Gallery cards that replace the reverse holo slot. "
        "Move **4 cards** from back to front as normal."
    ),
    "swsh4": (
        "⚡ **Vivid Voltage** has Amazing Rares that can appear in the rare slot. "
        "Move **4 cards** from back to front."
    ),
}


def get_pack_trick(set_id: str) -> PackTrick:
    era = detect_era(set_id)
    trick = PACK_TRICKS.get(era, PACK_TRICKS["classic"])
    # Inject set-specific note if present
    note = SET_TRICK_NOTES.get(set_id, "")
    if note:
        return PackTrick(
            era=trick.era,
            cards_to_move=trick.cards_to_move,
            description=trick.description,
            set_note=note,
        )
    return trick


# ─────────────────────────────────────────────────────────────────────────────
#  Pull rate tables
# ─────────────────────────────────────────────────────────────────────────────

RARE_SLOT_SV = [
    ("holo",       {"Rare Holo"},                        0.22),
    ("double",     {"Double Rare"},                      0.33),
    ("ir",         {"Illustration Rare"},                0.17),
    ("ultra",      {"Ultra Rare"},                       0.13),
    ("sir",        {"Special Illustration Rare"},        0.09),
    ("hyper",      {"Hyper Rare"},                       0.04),
    ("shiny",      {"Shiny Rare"},                       0.015),
    ("shinyultra", {"Shiny Ultra Rare"},                 0.005),
]

# Ascended Heroes: adds Mega Attack Rare and Mega Hyper Rare to the pool
RARE_SLOT_ASCENDED_HEROES = [
    ("holo",       {"Rare Holo"},                        0.18),
    ("double",     {"Double Rare"},                      0.25),
    ("mega_atk",   {"Mega Attack Rare"},                 0.12),
    ("ir",         {"Illustration Rare"},                0.17),
    ("ultra",      {"Ultra Rare"},                       0.12),
    ("sir",        {"Special Illustration Rare"},        0.09),
    ("hyper",      {"Hyper Rare"},                       0.03),
    ("mega_hyper", {"Mega Hyper Rare"},                  0.002),
    ("shiny",      {"Shiny Rare"},                       0.015),
    ("shinyultra", {"Shiny Ultra Rare"},                 0.005),
]

RARE_SLOT_SWSH = [
    ("holo",    {"Rare Holo"},                           0.33),
    ("v",       {"Rare Holo V"},                         0.18),
    ("vmax",    {"Rare Holo VMAX", "Rare Holo VSTAR"},   0.09),
    ("fullart", {"Rare Ultra"},                          0.14),
    ("ra",      {"Rare Rainbow"},                        0.06),
    ("tg",      {"Trainer Gallery Rare Holo",
                 "Trainer Gallery Ultra Rare",
                 "Trainer Gallery Secret Rare"},          0.12),
    ("secret",  {"Rare Secret"},                         0.06),
    ("amazing", {"Amazing Rare"},                        0.02),
]

RARE_SLOT_SM = [
    ("holo",    {"Rare Holo"},        0.35),
    ("gx",      {"Rare Holo GX"},     0.20),
    ("fullart", {"Rare Ultra"},       0.15),
    ("rainbow", {"Rare Rainbow"},     0.06),
    ("secret",  {"Rare Secret"},      0.04),
    ("shiny",   {"Rare Shiny"},       0.015),
    ("shinygx", {"Rare Shiny GX"},    0.005),
]

RARE_SLOT_XY = [
    ("holo",    {"Rare Holo"},        0.40),
    ("ex",      {"Rare Holo EX"},     0.22),
    ("fullart", {"Rare Ultra"},       0.12),
    ("secret",  {"Rare Secret"},      0.06),
    ("break",   {"Rare BREAK"},       0.08),
    ("ace",     {"Rare ACE"},         0.04),
]

RARE_SLOT_BW = [
    ("holo",    {"Rare Holo"},        0.45),
    ("ex",      {"Rare Holo EX"},     0.20),
    ("fullart", {"Rare Ultra"},       0.12),
    ("secret",  {"Rare Secret"},      0.06),
    ("shining", {"Rare Shining"},     0.02),
]

RARE_SLOT_HGSS = [
    ("holo",    {"Rare Holo"},        0.50),
    ("prime",   {"Rare Holo"},        0.15),   # Primes share Rare Holo rarity label
    ("legend",  {"LEGEND"},           0.08),
    ("secret",  {"Rare Secret"},      0.04),
]

RARE_SLOT_DP_PL = [
    ("holo",    {"Rare Holo"},        0.55),
    ("ex",      {"Rare Holo EX"},     0.15),
    ("secret",  {"Rare Secret"},      0.04),
]

RARE_SLOT_CLASSIC = [
    ("holo",    {"Rare Holo"},        0.33),
    ("rare",    {"Rare"},             0.67),
]

# EX era: Holo, Rare, EX card, Gold Star
# Gold Star appears in ~1/72 packs (roughly 1.4% of rare slots)
# EX cards appear in ~1/12 packs (roughly 8%)
# Source: documented pull rate data from EX era pack openings
RARE_SLOT_EX = [
    ("gold_star", {"Rare Holo Star"},                       0.014),
    ("ex_card",   {"Rare Holo EX"},                        0.08),
    ("holo",      {"Rare Holo"},                           0.30),
    ("rare",      {"Rare"},                                0.606),
]


def _get_rare_slot_table(set_id: str) -> list:
    # Ascended Heroes gets its own table
    if set_id == "sv8pt5":
        return RARE_SLOT_ASCENDED_HEROES
    era = detect_era(set_id)
    return {
        "sv":      RARE_SLOT_SV,
        "swsh":    RARE_SLOT_SWSH,
        "sm":      RARE_SLOT_SM,
        "xy":      RARE_SLOT_XY,
        "bw":      RARE_SLOT_BW,
        "hgss":    RARE_SLOT_HGSS,
        "pl":      RARE_SLOT_DP_PL,
        "dp":      RARE_SLOT_DP_PL,
        "ex":      RARE_SLOT_EX,
        "ereader": RARE_SLOT_CLASSIC,
        "classic": RARE_SLOT_CLASSIC,
    }.get(era, RARE_SLOT_CLASSIC)


# ─────────────────────────────────────────────────────────────────────────────
#  Card pool
# ─────────────────────────────────────────────────────────────────────────────

class CardPool:
    def __init__(self, cards: list[dict], set_total: int):
        self.commons:   list[dict] = []
        self.uncommons: list[dict] = []
        self.rares:     list[dict] = []
        self.ultras:    list[dict] = []
        self.specials:  list[dict] = []
        self._by_rarity: dict[str, list[dict]] = {}

        for card in cards:
            r    = card_rarity(card)
            tier = rarity_tier(r)
            try:
                num = int(card.get("number", 0))
            except (ValueError, TypeError):
                num = 0
            if num > set_total:
                tier = 4

            self._by_rarity.setdefault(r, []).append(card)
            if tier == 0:   self.commons.append(card)
            elif tier == 1: self.uncommons.append(card)
            elif tier == 2: self.rares.append(card)
            elif tier == 3: self.ultras.append(card)
            elif tier == 4: self.specials.append(card)

        self.reverse_eligible = self.commons + self.uncommons + self.rares

    def pick_from_rarities(self, rarity_set: set[str]) -> Optional[dict]:
        pool: list[dict] = []
        for r in rarity_set:
            pool.extend(self._by_rarity.get(r, []))
        return random.choice(pool) if pool else None

    def pick_rare_slot(self, table: list) -> dict:
        available = [
            (rs, w) for _, rs, w in table
            if any(self._by_rarity.get(r) for r in rs)
        ]
        if not available:
            pool = self.rares or self.uncommons or self.commons
            return random.choice(pool)
        rsets_avail, weights_avail = zip(*available)
        chosen_rs = random.choices(list(rsets_avail), weights=list(weights_avail), k=1)[0]
        card = self.pick_from_rarities(chosen_rs)
        if card:
            return card
        pool = self.rares or self.uncommons or self.commons
        return random.choice(pool)

    def pick_reverse_holo(self) -> dict:
        roll = random.random()
        if roll < 0.002 and self.ultras:
            return random.choice(self.ultras)
        pool = self.reverse_eligible or self.commons
        return random.choice(pool)

    def pick_ir_slot(self) -> dict:
        """
        SV RH2 slot: normally a standard reverse holo, but has a
        chance to be an Illustration Rare instead.
        """
        roll = random.random()
        ir_pool = self._by_rarity.get("Illustration Rare", [])
        if roll < 0.17 and ir_pool:
            return random.choice(ir_pool)
        return self.pick_reverse_holo()


def _pick(pool: list[dict]) -> dict:
    if not pool:
        return {}
    return random.choice(pool)


# ─────────────────────────────────────────────────────────────────────────────
#  Per-era pack assembly
#  All functions return cards in the authentic reveal order (after pack trick)
# ─────────────────────────────────────────────────────────────────────────────

def _build_sv_pack(pool: CardPool, table: list, is_ascended: bool = False) -> list[dict]:
    """
    SV era: 4 commons → 3 uncommons → RH1 (standard RH) → RH2 (IR or RH) → HOLO/HIT
    The Basic Energy card is stripped out (it's handled as a bonus card, shown
    first to mirror the pack trick: energy moved from back → front).
    """
    pack: list[dict] = []

    # Slot 0: Energy bonus card (shown first — this IS the pack trick)
    # We synthesise a placeholder since the API doesn't have basic energy cards
    energy_placeholder = {
        "id":     "_energy",
        "name":   "Basic Energy",
        "rarity": "Common",
        "number": "E",
        "images": {"large": "", "small": ""},
        "set":    {"id": "sv", "name": ""},
        "_slot":  "energy",
    }
    pack.append(energy_placeholder)

    # Slots 1-4: commons
    for _ in range(4):
        pack.append(dict(_pick(pool.commons or pool.uncommons), _slot="common"))

    # Slots 5-7: uncommons
    for _ in range(3):
        pack.append(dict(_pick(pool.uncommons or pool.commons), _slot="uncommon"))

    # Slot 8: RH1 — standard reverse holo
    rh1 = pool.pick_reverse_holo()
    pack.append(dict(rh1, _slot="reverse"))

    # Slot 9: RH2 — Illustration Rare chance (or standard RH)
    if is_ascended:
        # Ascended Heroes: Poké Ball / Energy pattern reverse (treat as RH)
        rh2 = pool.pick_reverse_holo()
        pack.append(dict(rh2, _slot="reverse_pokeball"))
    else:
        rh2 = pool.pick_ir_slot()
        ir_rarity = card_rarity(rh2)
        slot2 = "ir" if ir_rarity == "Illustration Rare" else "reverse"
        pack.append(dict(rh2, _slot=slot2))

    # Slot 10: holo / rare / hit
    hit = pool.pick_rare_slot(table)
    pack.append(dict(hit, _slot="rare"))

    return pack


def _build_swsh_sm_pack(pool: CardPool, table: list) -> list[dict]:
    """
    SwSh / SM era: 6 commons → 3 uncommons → RH → RARE
    Pack trick = move 4 from back to front, so reveal order after trick:
      C C  |  U  RH  RARE  |  C C C C  U U
    We output in the viewer's reveal order (trick already applied):
      C C  U  RH  RARE  C C C C  U U
    Simpler for the bot: just output in ascending rarity order which
    matches the trick result.
    """
    pack: list[dict] = []
    # 6 commons
    for _ in range(6):
        pack.append(dict(_pick(pool.commons or pool.uncommons), _slot="common"))
    # 3 uncommons
    for _ in range(3):
        pack.append(dict(_pick(pool.uncommons or pool.commons), _slot="uncommon"))
    # Reverse holo
    pack.append(dict(pool.pick_reverse_holo(), _slot="reverse"))
    # Rare slot
    pack.append(dict(pool.pick_rare_slot(table), _slot="rare"))
    return pack


def _build_xy_bw_pack(pool: CardPool, table: list) -> list[dict]:
    """
    XY / BW era: same 10-card structure as SwSh.
    6 commons, 3 uncommons, 1 RH, 1 rare. Trick = 3 cards.
    """
    return _build_swsh_sm_pack(pool, table)


def _build_hgss_dp_pl_pack(pool: CardPool, table: list) -> list[dict]:
    """
    HGSS / DP / Platinum: 6 commons, 3 uncommons, 1 rare.
    No separate reverse holo slot (RH cards can appear in any slot).
    Pack trick = 3 cards from back to front.
    """
    pack: list[dict] = []
    for _ in range(6):
        pack.append(dict(_pick(pool.commons or pool.uncommons), _slot="common"))
    for _ in range(3):
        pack.append(dict(_pick(pool.uncommons or pool.commons), _slot="uncommon"))
    # In these sets, any non-rare card *might* be a reverse holo.
    # Simulate the reverse slot by occasionally making a non-rare appear as reverse.
    if random.random() < 0.7:  # ~70% packs have a reverse holo somewhere
        pack.append(dict(pool.pick_reverse_holo(), _slot="reverse"))
    else:
        pack.append(dict(_pick(pool.commons or pool.uncommons), _slot="common"))
    pack.append(dict(pool.pick_rare_slot(table), _slot="rare"))
    return pack


def _build_classic_pack(pool: CardPool, table: list) -> list[dict]:
    """
    Classic WotC era (Base Set, Jungle, Fossil, Neo, etc.):
    5 commons + 3 uncommons + 1 rare + 2 Energy cards = 11 cards
    Pack trick = 3 cards from back to front → rare ends up last
    We show Energy cards first (they were at the back, moved to front by the trick).
    """
    pack: list[dict] = []

    # 2 energy cards (shown first — trick moved them to front)
    for i in range(2):
        pack.append({
            "id":     f"_energy_{i}",
            "name":   "Energy Card",
            "rarity": "Common",
            "number": "E",
            "images": {"large": "", "small": ""},
            "set":    {"id": "classic", "name": ""},
            "_slot":  "energy",
        })

    # 5 commons
    for _ in range(5):
        pack.append(dict(_pick(pool.commons or pool.uncommons), _slot="common"))

    # 3 uncommons
    for _ in range(3):
        pack.append(dict(_pick(pool.uncommons or pool.commons), _slot="uncommon"))

    # 1 rare (last)
    pack.append(dict(pool.pick_rare_slot(table), _slot="rare"))

    return pack


def _build_ereader_pack(pool: CardPool, table: list) -> list[dict]:
    """e-Reader era: same as classic but trick is 2 cards."""
    # Structure same as classic, just different trick count
    return _build_classic_pack(pool, table)


# ─────────────────────────────────────────────────────────────────────────────
#  Public entry point
# ─────────────────────────────────────────────────────────────────────────────

async def rip_pack(set_id: str, pack_size: int = 10) -> list[dict]:
    """
    Simulate opening one booster pack.
    Returns cards already in the post-pack-trick reveal order
    (Energy/low rarity first, rare hit last).
    """
    cards = await fetch_cards_for_set(set_id)
    if not cards:
        log.error(f"No cards found for set {set_id}")
        return []

    set_info = await fetch_set(set_id)
    printed_total = set_info.get("printedTotal", 999) if set_info else 999

    pool  = CardPool(cards, printed_total)
    table = _get_rare_slot_table(set_id)
    era   = detect_era(set_id)

    if era == "sv":
        return _build_sv_pack(pool, table, is_ascended=(set_id == "sv8pt5"))
    elif era in ("swsh", "sm"):
        return _build_swsh_sm_pack(pool, table)
    elif era in ("xy", "bw"):
        return _build_xy_bw_pack(pool, table)
    elif era in ("hgss", "pl", "dp"):
        return _build_hgss_dp_pl_pack(pool, table)
    elif era == "ereader":
        return _build_ereader_pack(pool, table)
    else:
        # classic / unknown
        return _build_classic_pack(pool, table)


# ─────────────────────────────────────────────────────────────────────────────
#  Display helpers
# ─────────────────────────────────────────────────────────────────────────────

SLOT_LABELS = {
    "energy":          "⚡ Basic Energy",
    "common":          "Common",
    "uncommon":        "Uncommon",
    "reverse":         "✨ Reverse Holo",
    "reverse_pokeball":"✨ Poké Ball Reverse Holo",
    "ir":              "🎨 Illustration Rare",
    "rare":            "⭐ Rare Slot",
}

RARITY_EMOJI = {
    0: "",
    1: "",
    2: "⭐",
    3: "💫",
    4: "🌟",
}

def slot_excitement(card: dict) -> str:
    slot  = card.get("_slot", "common")
    r     = card_rarity(card)
    tier  = rarity_tier(r)
    emoji = RARITY_EMOJI.get(tier, "")
    label = SLOT_LABELS.get(slot, slot.title())
    return f"{emoji} {label} {emoji}" if emoji else label
