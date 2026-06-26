"""
core/set_data.py

Authoritative set metadata.

Set IDs verified against:
  - pokemontcg.io API (https://api.pokemontcg.io/v2/sets)
  - ptcg-assets repo (https://github.com/1niceroli/ptcg-assets)

Pack art URLs sourced from the ptcg-assets GitHub repo (raw content).
Base URL: https://raw.githubusercontent.com/1niceroli/ptcg-assets/main/{set_id}/

The store only shows sets that have actual booster packs (no promos,
trainer kits, promo-only sets, McD's collections, etc.).
"""

from dataclasses import dataclass, field

ASSETS = "https://raw.githubusercontent.com/1niceroli/ptcg-assets/main"


@dataclass
class SetMeta:
    set_id:     str
    era:        str
    pack_arts:  list[str]
    pack_size:  int = 10


def _pack(set_id: str, filenames: list[str]) -> list[str]:
    """Build raw GitHub URLs for pack art images."""
    return [f"{ASSETS}/{set_id}/{f}" for f in filenames]


# ─────────────────────────────────────────────────────────────────────────────
#  Mega Evolution era
# ─────────────────────────────────────────────────────────────────────────────
ME_SETS: list[SetMeta] = [
    SetMeta("me2pt5", "Mega Evolution", _pack("me2pt5", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("me2",    "Mega Evolution", _pack("me2",    ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("me1",    "Mega Evolution", _pack("me1",    ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Scarlet & Violet era
# ─────────────────────────────────────────────────────────────────────────────
SV_SETS: list[SetMeta] = [
    SetMeta("sv10",    "Scarlet & Violet", _pack("sv10",    ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sv9",     "Scarlet & Violet", _pack("sv9",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sv8pt5",  "Scarlet & Violet", _pack("sv8pt5",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png", "en_packshot_4.png", "en_packshot_5.png"])),
    SetMeta("sv8",     "Scarlet & Violet", _pack("sv8",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sv7",     "Scarlet & Violet", _pack("sv7",     ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("sv6pt5",  "Scarlet & Violet", _pack("sv6pt5",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("sv6",     "Scarlet & Violet", _pack("sv6",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sv5",     "Scarlet & Violet", _pack("sv5",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sv4pt5",  "Scarlet & Violet", _pack("sv4pt5",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("sv4",     "Scarlet & Violet", _pack("sv4",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sv3pt5",  "Scarlet & Violet", _pack("sv3pt5",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sv3",     "Scarlet & Violet", _pack("sv3",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sv2",     "Scarlet & Violet", _pack("sv2",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sv1",     "Scarlet & Violet", _pack("sv1",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Sword & Shield era
# ─────────────────────────────────────────────────────────────────────────────
SWSH_SETS: list[SetMeta] = [
    SetMeta("swsh12pt5", "Sword & Shield", _pack("swsh12pt5", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png", "en_packshot_4.png"])),
    SetMeta("swsh12",    "Sword & Shield", _pack("swsh12",    ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("swsh11",    "Sword & Shield", _pack("swsh11",    ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("pgo",       "Sword & Shield", _pack("pgo",       ["en_packshot_1.png"])),
    SetMeta("swsh10",    "Sword & Shield", _pack("swsh10",    ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("swsh9",     "Sword & Shield", _pack("swsh9",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("swsh8",     "Sword & Shield", _pack("swsh8",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png", "en_packshot_4.png"])),
    SetMeta("swsh7",     "Sword & Shield", _pack("swsh7",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("swsh6",     "Sword & Shield", _pack("swsh6",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("swsh5",     "Sword & Shield", _pack("swsh5",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("swsh4",     "Sword & Shield", _pack("swsh4",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("swsh3",     "Sword & Shield", _pack("swsh3",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("swsh2",     "Sword & Shield", _pack("swsh2",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("swsh1",     "Sword & Shield", _pack("swsh1",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Sun & Moon era
# ─────────────────────────────────────────────────────────────────────────────
SM_SETS: list[SetMeta] = [
    SetMeta("sm12",  "Sun & Moon", _pack("sm12",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sm11",  "Sun & Moon", _pack("sm11",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sm10",  "Sun & Moon", _pack("sm10",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sm9",   "Sun & Moon", _pack("sm9",   ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sm8",   "Sun & Moon", _pack("sm8",   ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sm7",   "Sun & Moon", _pack("sm7",   ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sm6",   "Sun & Moon", _pack("sm6",   ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("sm5",   "Sun & Moon", _pack("sm5",   ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sm4",   "Sun & Moon", _pack("sm4",   ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("sm3",   "Sun & Moon", _pack("sm3",   ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sm2",   "Sun & Moon", _pack("sm2",   ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("sm1",   "Sun & Moon", _pack("sm1",   ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
]

# ─────────────────────────────────────────────────────────────────────────────
#  XY era
# ─────────────────────────────────────────────────────────────────────────────
XY_SETS: list[SetMeta] = [
    SetMeta("xy12", "XY", _pack("xy12", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("xy11", "XY", _pack("xy11", ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("xy10", "XY", _pack("xy10", ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("xy9",  "XY", _pack("xy9",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("xy8",  "XY", _pack("xy8",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("xy7",  "XY", _pack("xy7",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("xy6",  "XY", _pack("xy6",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("xy5",  "XY", _pack("xy5",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("xy4",  "XY", _pack("xy4",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("xy3",  "XY", _pack("xy3",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("xy2",  "XY", _pack("xy2",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("xy1",  "XY", _pack("xy1",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Black & White era
# ─────────────────────────────────────────────────────────────────────────────
BW_SETS: list[SetMeta] = [
    SetMeta("bw11", "Black & White", _pack("bw11", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("bw10", "Black & White", _pack("bw10", ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("bw9",  "Black & White", _pack("bw9",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("bw8",  "Black & White", _pack("bw8",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("bw7",  "Black & White", _pack("bw7",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("bw6",  "Black & White", _pack("bw6",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("bw5",  "Black & White", _pack("bw5",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("bw4",  "Black & White", _pack("bw4",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("bw3",  "Black & White", _pack("bw3",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("bw2",  "Black & White", _pack("bw2",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("bw1",  "Black & White", _pack("bw1",  ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
]

# ─────────────────────────────────────────────────────────────────────────────
#  HeartGold & SoulSilver era
# ─────────────────────────────────────────────────────────────────────────────
HGSS_SETS: list[SetMeta] = [
    SetMeta("col1",  "HeartGold & SoulSilver", _pack("col1",  ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("hgss4", "HeartGold & SoulSilver", _pack("hgss4", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("hgss3", "HeartGold & SoulSilver", _pack("hgss3", ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("hgss2", "HeartGold & SoulSilver", _pack("hgss2", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("hgss1", "HeartGold & SoulSilver", _pack("hgss1", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Platinum era
# ─────────────────────────────────────────────────────────────────────────────
PL_SETS: list[SetMeta] = [
    SetMeta("pl4", "Platinum", _pack("pl4", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("pl3", "Platinum", _pack("pl3", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("pl2", "Platinum", _pack("pl2", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("pl1", "Platinum", _pack("pl1", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Diamond & Pearl era
# ─────────────────────────────────────────────────────────────────────────────
DP_SETS: list[SetMeta] = [
    SetMeta("dp7", "Diamond & Pearl", _pack("dp7", ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("dp6", "Diamond & Pearl", _pack("dp6", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("dp5", "Diamond & Pearl", _pack("dp5", ["en_packshot_1.png", "en_packshot_2.png"])),
    SetMeta("dp4", "Diamond & Pearl", _pack("dp4", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("dp3", "Diamond & Pearl", _pack("dp3", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("dp2", "Diamond & Pearl", _pack("dp2", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
    SetMeta("dp1", "Diamond & Pearl", _pack("dp1", ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"])),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Classic / WotC era
# ─────────────────────────────────────────────────────────────────────────────
CLASSIC_SETS: list[SetMeta] = [
    SetMeta("neo4",      "Classic", _pack("neo4",      ["en_packshot_1.png", "en_packshot_2.png"]), pack_size=9),
    SetMeta("neo3",      "Classic", _pack("neo3",      ["en_packshot_1.png", "en_packshot_2.png"]), pack_size=9),
    SetMeta("neo2",      "Classic", _pack("neo2",      ["en_packshot_1.png", "en_packshot_2.png"]), pack_size=9),
    SetMeta("neo1",      "Classic", _pack("neo1",      ["en_packshot_1.png", "en_packshot_2.png"]), pack_size=9),
    SetMeta("gym2",      "Classic", _pack("gym2",      ["en_packshot_1.png", "en_packshot_2.png"]), pack_size=9),
    SetMeta("gym1",      "Classic", _pack("gym1",      ["en_packshot_1.png", "en_packshot_2.png"]), pack_size=9),
    SetMeta("base5",     "Classic", _pack("base5",     ["en_packshot_1.png", "en_packshot_2.png"]), pack_size=9),
    SetMeta("base4",     "Classic", _pack("base4",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"]), pack_size=9),
    SetMeta("base3",     "Classic", _pack("base3",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"]), pack_size=9),
    SetMeta("base2",     "Classic", _pack("base2",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"]), pack_size=9),
    SetMeta("base1",     "Classic", _pack("base1",     ["en_packshot_1.png", "en_packshot_2.png", "en_packshot_3.png"]), pack_size=9),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Master lookup
# ─────────────────────────────────────────────────────────────────────────────

ALL_SETS: list[SetMeta] = (
    ME_SETS + SV_SETS + SWSH_SETS + SM_SETS +
    XY_SETS + BW_SETS + HGSS_SETS + PL_SETS + DP_SETS + CLASSIC_SETS
)

ALL_SET_META: dict[str, SetMeta] = {s.set_id: s for s in ALL_SETS}

ERA_ORDER = [
    "Mega Evolution",
    "Scarlet & Violet",
    "Sword & Shield",
    "Sun & Moon",
    "XY",
    "Black & White",
    "HeartGold & SoulSilver",
    "Platinum",
    "Diamond & Pearl",
    "Classic",
]

ERA_COLORS = {
    "Mega Evolution":          0xFF6B6B,
    "Scarlet & Violet":        0xE3350D,
    "Sword & Shield":          0x2E6DB4,
    "Sun & Moon":              0xF5A623,
    "XY":                      0x0072BC,
    "Black & White":           0x4A4A4A,
    "HeartGold & SoulSilver":  0xC8A951,
    "Platinum":                0x7B7B9E,
    "Diamond & Pearl":         0x4B6EAF,
    "Classic":                 0xFFCC00,
}

ERA_EMOJIS = {
    "Mega Evolution":          "⚡",
    "Scarlet & Violet":        "🔴",
    "Sword & Shield":          "🛡️",
    "Sun & Moon":              "☀️",
    "XY":                      "🔵",
    "Black & White":           "⬛",
    "HeartGold & SoulSilver":  "🌟",
    "Platinum":                "🔷",
    "Diamond & Pearl":         "💎",
    "Classic":                 "🎴",
}


def get_meta(set_id: str) -> "SetMeta | None":
    return ALL_SET_META.get(set_id)


def sets_by_era() -> dict[str, list[SetMeta]]:
    result: dict[str, list[SetMeta]] = {}
    for s in ALL_SETS:
        result.setdefault(s.era, []).append(s)
    return result
