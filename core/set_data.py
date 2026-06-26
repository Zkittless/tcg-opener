"""
core/set_data.py

Pack art URLs:
- Verified Bulbagarden Archives images for major sets (confirmed filenames)
- TCGdex asset CDN logos as fallback: https://assets.tcgdex.net/en/{series}/{set_id}/logo
  These are confirmed public and Discord can embed them.
"""

from dataclasses import dataclass

BULBA  = "https://archives.bulbagarden.net/media/upload"
TCGDEX = "https://assets.tcgdex.net/en"


def _b(*filenames: str) -> list[str]:
    return [f"{BULBA}/{f}" for f in filenames]


def _t(series: str, set_id: str) -> list[str]:
    """TCGdex set logo — always public, Discord embeds fine."""
    return [f"{TCGDEX}/{series}/{set_id}/logo"]


@dataclass
class SetMeta:
    set_id:    str
    era:       str
    pack_arts: list[str]
    pack_size: int = 10


ME_SETS: list[SetMeta] = [
    SetMeta("me2pt5", "Mega Evolution", _t("me", "me2pt5")),
    SetMeta("me2",    "Mega Evolution", _t("me", "me2")),
    SetMeta("me1",    "Mega Evolution", _t("me", "me1")),
]

SV_SETS: list[SetMeta] = [
    SetMeta("sv10",   "Scarlet & Violet", _t("sv", "sv10")),
    SetMeta("sv9",    "Scarlet & Violet", _t("sv", "sv9")),
    # Prismatic Evolutions — verified Bulbagarden filenames
    SetMeta("sv8pt5", "Scarlet & Violet", _b(
        "Prismatic_Evolutions_Booster_Eevee_Sylveon.png",
        "Prismatic_Evolutions_Booster_Espeon_Umbreon.png",
        "Prismatic_Evolutions_Booster_Leafeon_Glaceon.png",
        "Prismatic_Evolutions_Booster_Vaporeon_Jolteon_Flareon.png",
    )),
    # Surging Sparks — verified
    SetMeta("sv8",    "Scarlet & Violet", _b(
        "SV8_Booster_Pikachu.png",
        "SV8_Booster_Archaludon.png",
        "SV8_Booster_Alolan_Exeggutor.png",
        "SV8_Booster_Latias.png",
    )),
    # Stellar Crown — verified
    SetMeta("sv7",    "Scarlet & Violet", _b(
        "SV7_Booster_Terapagos.png",
        "SV7_Booster_Cinderace.png",
        "SV7_Booster_Lapras.png",
        "SV7_Booster_Galvantula.png",
    )),
    SetMeta("sv6pt5", "Scarlet & Violet", _t("sv", "sv6pt5")),
    SetMeta("sv6",    "Scarlet & Violet", _t("sv", "sv6")),
    SetMeta("sv5",    "Scarlet & Violet", _t("sv", "sv5")),
    SetMeta("sv4pt5", "Scarlet & Violet", _t("sv", "sv4pt5")),
    SetMeta("sv4",    "Scarlet & Violet", _t("sv", "sv4")),
    SetMeta("sv3pt5", "Scarlet & Violet", _t("sv", "sv3pt5")),
    SetMeta("sv3",    "Scarlet & Violet", _t("sv", "sv3")),
    SetMeta("sv2",    "Scarlet & Violet", _t("sv", "sv2")),
    SetMeta("sv1",    "Scarlet & Violet", _t("sv", "sv1")),
]

SWSH_SETS: list[SetMeta] = [
    # Crown Zenith — verified
    SetMeta("swsh12pt5", "Sword & Shield", _b("Crown_Zenith_Booster.jpg")),
    SetMeta("swsh12",    "Sword & Shield", _t("swsh", "swsh12")),
    SetMeta("swsh11",    "Sword & Shield", _t("swsh", "swsh11")),
    SetMeta("pgo",       "Sword & Shield", _t("swsh", "pgo")),
    SetMeta("swsh10",    "Sword & Shield", _t("swsh", "swsh10")),
    SetMeta("swsh9",     "Sword & Shield", _t("swsh", "swsh9")),
    SetMeta("swsh8",     "Sword & Shield", _t("swsh", "swsh8")),
    SetMeta("swsh7",     "Sword & Shield", _t("swsh", "swsh7")),
    SetMeta("swsh6",     "Sword & Shield", _t("swsh", "swsh6")),
    SetMeta("swsh5",     "Sword & Shield", _t("swsh", "swsh5")),
    SetMeta("swsh4",     "Sword & Shield", _t("swsh", "swsh4")),
    SetMeta("swsh3",     "Sword & Shield", _t("swsh", "swsh3")),
    SetMeta("swsh2",     "Sword & Shield", _t("swsh", "swsh2")),
    SetMeta("swsh1",     "Sword & Shield", _t("swsh", "swsh1")),
]

SM_SETS: list[SetMeta] = [
    SetMeta("sm12",  "Sun & Moon", _t("sm", "sm12")),
    SetMeta("sm11",  "Sun & Moon", _t("sm", "sm11")),
    SetMeta("sm10",  "Sun & Moon", _t("sm", "sm10")),
    SetMeta("sm9",   "Sun & Moon", _t("sm", "sm9")),
    SetMeta("sm8",   "Sun & Moon", _t("sm", "sm8")),
    SetMeta("sm7",   "Sun & Moon", _t("sm", "sm7")),
    SetMeta("sm6",   "Sun & Moon", _t("sm", "sm6")),
    SetMeta("sm5",   "Sun & Moon", _t("sm", "sm5")),
    SetMeta("sm4",   "Sun & Moon", _t("sm", "sm4")),
    SetMeta("sm3",   "Sun & Moon", _t("sm", "sm3")),
    SetMeta("sm2",   "Sun & Moon", _t("sm", "sm2")),
    SetMeta("sm1",   "Sun & Moon", _t("sm", "sm1")),
]

XY_SETS: list[SetMeta] = [
    SetMeta("xy12", "XY", _t("xy", "xy12")),
    SetMeta("xy11", "XY", _t("xy", "xy11")),
    SetMeta("xy10", "XY", _t("xy", "xy10")),
    SetMeta("xy9",  "XY", _t("xy", "xy9")),
    SetMeta("xy8",  "XY", _t("xy", "xy8")),
    SetMeta("xy7",  "XY", _t("xy", "xy7")),
    SetMeta("xy6",  "XY", _t("xy", "xy6")),
    SetMeta("xy5",  "XY", _t("xy", "xy5")),
    SetMeta("xy4",  "XY", _t("xy", "xy4")),
    SetMeta("xy3",  "XY", _t("xy", "xy3")),
    SetMeta("xy2",  "XY", _t("xy", "xy2")),
    SetMeta("xy1",  "XY", _t("xy", "xy1")),
]

BW_SETS: list[SetMeta] = [
    SetMeta("bw11", "Black & White", _t("bw", "bw11")),
    SetMeta("bw10", "Black & White", _t("bw", "bw10")),
    SetMeta("bw9",  "Black & White", _t("bw", "bw9")),
    SetMeta("bw8",  "Black & White", _t("bw", "bw8")),
    SetMeta("bw7",  "Black & White", _t("bw", "bw7")),
    SetMeta("bw6",  "Black & White", _t("bw", "bw6")),
    SetMeta("bw5",  "Black & White", _t("bw", "bw5")),
    SetMeta("bw4",  "Black & White", _t("bw", "bw4")),
    SetMeta("bw3",  "Black & White", _t("bw", "bw3")),
    SetMeta("bw2",  "Black & White", _t("bw", "bw2")),
    SetMeta("bw1",  "Black & White", _t("bw", "bw1")),
]

HGSS_SETS: list[SetMeta] = [
    SetMeta("col1",  "HeartGold & SoulSilver", _t("hgss", "col1")),
    SetMeta("hgss4", "HeartGold & SoulSilver", _t("hgss", "hgss4")),
    SetMeta("hgss3", "HeartGold & SoulSilver", _t("hgss", "hgss3")),
    SetMeta("hgss2", "HeartGold & SoulSilver", _t("hgss", "hgss2")),
    SetMeta("hgss1", "HeartGold & SoulSilver", _t("hgss", "hgss1")),
]

PL_SETS: list[SetMeta] = [
    SetMeta("pl4", "Platinum", _t("pl", "pl4")),
    SetMeta("pl3", "Platinum", _t("pl", "pl3")),
    SetMeta("pl2", "Platinum", _t("pl", "pl2")),
    SetMeta("pl1", "Platinum", _t("pl", "pl1")),
]

DP_SETS: list[SetMeta] = [
    SetMeta("dp7", "Diamond & Pearl", _t("dp", "dp7")),
    SetMeta("dp6", "Diamond & Pearl", _t("dp", "dp6")),
    SetMeta("dp5", "Diamond & Pearl", _t("dp", "dp5")),
    SetMeta("dp4", "Diamond & Pearl", _t("dp", "dp4")),
    SetMeta("dp3", "Diamond & Pearl", _t("dp", "dp3")),
    SetMeta("dp2", "Diamond & Pearl", _t("dp", "dp2")),
    SetMeta("dp1", "Diamond & Pearl", _t("dp", "dp1")),
]

CLASSIC_SETS: list[SetMeta] = [
    SetMeta("neo4",  "Classic", _t("base", "neo4"),  pack_size=9),
    SetMeta("neo3",  "Classic", _t("base", "neo3"),  pack_size=9),
    SetMeta("neo2",  "Classic", _t("base", "neo2"),  pack_size=9),
    SetMeta("neo1",  "Classic", _t("base", "neo1"),  pack_size=9),
    SetMeta("gym2",  "Classic", _t("base", "gym2"),  pack_size=9),
    SetMeta("gym1",  "Classic", _t("base", "gym1"),  pack_size=9),
    SetMeta("base5", "Classic", _t("base", "base5"), pack_size=9),
    SetMeta("base4", "Classic", _t("base", "base4"), pack_size=9),
    SetMeta("base3", "Classic", _t("base", "base3"), pack_size=9),
    SetMeta("base2", "Classic", _t("base", "base2"), pack_size=9),
    SetMeta("base1", "Classic", _t("base", "base1"), pack_size=9),
]

ALL_SETS: list[SetMeta] = (
    ME_SETS + SV_SETS + SWSH_SETS + SM_SETS +
    XY_SETS + BW_SETS + HGSS_SETS + PL_SETS + DP_SETS + CLASSIC_SETS
)

ALL_SET_META: dict[str, SetMeta] = {s.set_id: s for s in ALL_SETS}

ERA_ORDER = [
    "Mega Evolution", "Scarlet & Violet", "Sword & Shield", "Sun & Moon",
    "XY", "Black & White", "HeartGold & SoulSilver", "Platinum",
    "Diamond & Pearl", "Classic",
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
