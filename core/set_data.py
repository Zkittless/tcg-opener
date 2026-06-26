"""
core/set_data.py

Pack art URLs use Bulbagarden Archives — publicly accessible, verified filenames.
Base: https://archives.bulbagarden.net/media/upload/{filename}

For sets where we have verified filenames from Bulbagarden, we use those.
For others we fall back to the set logo from pokemontcg.io (always works).
"""

from dataclasses import dataclass, field

BULBA = "https://archives.bulbagarden.net/media/upload"


def _b(*filenames: str) -> list[str]:
    """Bulbagarden Archives URLs."""
    return [f"{BULBA}/{f}" for f in filenames]


def _logo(set_id: str) -> list[str]:
    """pokemontcg.io logo — reliable fallback, Discord can embed these."""
    return [f"https://images.pokemontcg.io/{set_id}/logo.png"]


@dataclass
class SetMeta:
    set_id:    str
    era:       str
    pack_arts: list[str]
    pack_size: int = 10


# ─────────────────────────────────────────────────────────────────────────────
#  Mega Evolution era
# ─────────────────────────────────────────────────────────────────────────────
ME_SETS: list[SetMeta] = [
    SetMeta("me2pt5", "Mega Evolution", _b(
        "Ascended_Heroes_Booster_Mega_Charizard_Y.png",
        "Ascended_Heroes_Booster_Mega_Dragonite.png",
        "Ascended_Heroes_Booster_Mega_Gengar.png",
    )),
    SetMeta("me2", "Mega Evolution", _b(
        "Phantasmal_Flames_Booster_Mega_Charizard_X.png",
        "Phantasmal_Flames_Booster_Mega_Mewtwo_Y.png",
    )),
    SetMeta("me1", "Mega Evolution", _b(
        "Mega_Evolution_Booster_Mega_Lucario.png",
        "Mega_Evolution_Booster_Mega_Gardevoir.png",
        "Mega_Evolution_Booster_Mega_Rayquaza.png",
    )),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Scarlet & Violet era  — verified filenames from Bulbagarden Archives
# ─────────────────────────────────────────────────────────────────────────────
SV_SETS: list[SetMeta] = [
    SetMeta("sv10",   "Scarlet & Violet", _logo("sv10")),   # Destined Rivals
    SetMeta("sv9",    "Scarlet & Violet", _logo("sv9")),    # Journey Together
    SetMeta("sv8pt5", "Scarlet & Violet", _b(               # Prismatic Evolutions ✓ verified
        "Prismatic_Evolutions_Booster_Eevee_Sylveon.png",
        "Prismatic_Evolutions_Booster_Espeon_Umbreon.png",
        "Prismatic_Evolutions_Booster_Leafeon_Glaceon.png",
        "Prismatic_Evolutions_Booster_Vaporeon_Jolteon_Flareon.png",
    )),
    SetMeta("sv8",    "Scarlet & Violet", _b(               # Surging Sparks ✓ verified
        "SV8_Booster_Pikachu.png",
        "SV8_Booster_Archaludon.png",
        "SV8_Booster_Alolan_Exeggutor.png",
        "SV8_Booster_Latias.png",
    )),
    SetMeta("sv7",    "Scarlet & Violet", _b(               # Stellar Crown ✓ verified
        "SV7_Booster_Terapagos.png",
        "SV7_Booster_Cinderace.png",
        "SV7_Booster_Lapras.png",
        "SV7_Booster_Galvantula.png",
    )),
    SetMeta("sv6pt5", "Scarlet & Violet", _logo("sv6pt5")), # Shrouded Fable
    SetMeta("sv6",    "Scarlet & Violet", _logo("sv6")),    # Twilight Masquerade
    SetMeta("sv5",    "Scarlet & Violet", _logo("sv5")),    # Temporal Forces
    SetMeta("sv4pt5", "Scarlet & Violet", _logo("sv4pt5")), # Paldean Fates
    SetMeta("sv4",    "Scarlet & Violet", _logo("sv4")),    # Paradox Rift
    SetMeta("sv3pt5", "Scarlet & Violet", _logo("sv3pt5")), # 151
    SetMeta("sv3",    "Scarlet & Violet", _logo("sv3")),    # Obsidian Flames
    SetMeta("sv2",    "Scarlet & Violet", _logo("sv2")),    # Paldea Evolved
    SetMeta("sv1",    "Scarlet & Violet", _logo("sv1")),    # Scarlet & Violet base
]

# ─────────────────────────────────────────────────────────────────────────────
#  Sword & Shield era
# ─────────────────────────────────────────────────────────────────────────────
SWSH_SETS: list[SetMeta] = [
    SetMeta("swsh12pt5", "Sword & Shield", _b("Crown_Zenith_Booster.jpg")),  # Crown Zenith ✓
    SetMeta("swsh12",    "Sword & Shield", _logo("swsh12")),
    SetMeta("swsh11",    "Sword & Shield", _logo("swsh11")),
    SetMeta("pgo",       "Sword & Shield", _logo("pgo")),
    SetMeta("swsh10",    "Sword & Shield", _logo("swsh10")),
    SetMeta("swsh9",     "Sword & Shield", _logo("swsh9")),
    SetMeta("swsh8",     "Sword & Shield", _logo("swsh8")),
    SetMeta("swsh7",     "Sword & Shield", _logo("swsh7")),
    SetMeta("swsh6",     "Sword & Shield", _logo("swsh6")),
    SetMeta("swsh5",     "Sword & Shield", _logo("swsh5")),
    SetMeta("swsh4",     "Sword & Shield", _logo("swsh4")),
    SetMeta("swsh3",     "Sword & Shield", _logo("swsh3")),
    SetMeta("swsh2",     "Sword & Shield", _logo("swsh2")),
    SetMeta("swsh1",     "Sword & Shield", _logo("swsh1")),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Sun & Moon era
# ─────────────────────────────────────────────────────────────────────────────
SM_SETS: list[SetMeta] = [
    SetMeta("sm12",  "Sun & Moon", _logo("sm12")),
    SetMeta("sm11",  "Sun & Moon", _logo("sm11")),
    SetMeta("sm10",  "Sun & Moon", _logo("sm10")),
    SetMeta("sm9",   "Sun & Moon", _logo("sm9")),
    SetMeta("sm8",   "Sun & Moon", _logo("sm8")),
    SetMeta("sm7",   "Sun & Moon", _logo("sm7")),
    SetMeta("sm6",   "Sun & Moon", _logo("sm6")),
    SetMeta("sm5",   "Sun & Moon", _logo("sm5")),
    SetMeta("sm4",   "Sun & Moon", _logo("sm4")),
    SetMeta("sm3",   "Sun & Moon", _logo("sm3")),
    SetMeta("sm2",   "Sun & Moon", _logo("sm2")),
    SetMeta("sm1",   "Sun & Moon", _logo("sm1")),
]

# ─────────────────────────────────────────────────────────────────────────────
#  XY era
# ─────────────────────────────────────────────────────────────────────────────
XY_SETS: list[SetMeta] = [
    SetMeta("xy12", "XY", _logo("xy12")),
    SetMeta("xy11", "XY", _logo("xy11")),
    SetMeta("xy10", "XY", _logo("xy10")),
    SetMeta("xy9",  "XY", _logo("xy9")),
    SetMeta("xy8",  "XY", _logo("xy8")),
    SetMeta("xy7",  "XY", _logo("xy7")),
    SetMeta("xy6",  "XY", _logo("xy6")),
    SetMeta("xy5",  "XY", _logo("xy5")),
    SetMeta("xy4",  "XY", _logo("xy4")),
    SetMeta("xy3",  "XY", _logo("xy3")),
    SetMeta("xy2",  "XY", _logo("xy2")),
    SetMeta("xy1",  "XY", _logo("xy1")),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Black & White era
# ─────────────────────────────────────────────────────────────────────────────
BW_SETS: list[SetMeta] = [
    SetMeta("bw11", "Black & White", _logo("bw11")),
    SetMeta("bw10", "Black & White", _logo("bw10")),
    SetMeta("bw9",  "Black & White", _logo("bw9")),
    SetMeta("bw8",  "Black & White", _logo("bw8")),
    SetMeta("bw7",  "Black & White", _logo("bw7")),
    SetMeta("bw6",  "Black & White", _logo("bw6")),
    SetMeta("bw5",  "Black & White", _logo("bw5")),
    SetMeta("bw4",  "Black & White", _logo("bw4")),
    SetMeta("bw3",  "Black & White", _logo("bw3")),
    SetMeta("bw2",  "Black & White", _logo("bw2")),
    SetMeta("bw1",  "Black & White", _logo("bw1")),
]

# ─────────────────────────────────────────────────────────────────────────────
#  HeartGold & SoulSilver era
# ─────────────────────────────────────────────────────────────────────────────
HGSS_SETS: list[SetMeta] = [
    SetMeta("col1",  "HeartGold & SoulSilver", _logo("col1")),
    SetMeta("hgss4", "HeartGold & SoulSilver", _logo("hgss4")),
    SetMeta("hgss3", "HeartGold & SoulSilver", _logo("hgss3")),
    SetMeta("hgss2", "HeartGold & SoulSilver", _logo("hgss2")),
    SetMeta("hgss1", "HeartGold & SoulSilver", _logo("hgss1")),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Platinum era
# ─────────────────────────────────────────────────────────────────────────────
PL_SETS: list[SetMeta] = [
    SetMeta("pl4", "Platinum", _logo("pl4")),
    SetMeta("pl3", "Platinum", _logo("pl3")),
    SetMeta("pl2", "Platinum", _logo("pl2")),
    SetMeta("pl1", "Platinum", _logo("pl1")),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Diamond & Pearl era
# ─────────────────────────────────────────────────────────────────────────────
DP_SETS: list[SetMeta] = [
    SetMeta("dp7", "Diamond & Pearl", _logo("dp7")),
    SetMeta("dp6", "Diamond & Pearl", _logo("dp6")),
    SetMeta("dp5", "Diamond & Pearl", _logo("dp5")),
    SetMeta("dp4", "Diamond & Pearl", _logo("dp4")),
    SetMeta("dp3", "Diamond & Pearl", _logo("dp3")),
    SetMeta("dp2", "Diamond & Pearl", _logo("dp2")),
    SetMeta("dp1", "Diamond & Pearl", _logo("dp1")),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Classic / WotC era
# ─────────────────────────────────────────────────────────────────────────────
CLASSIC_SETS: list[SetMeta] = [
    SetMeta("neo4",  "Classic", _logo("neo4"),  pack_size=9),
    SetMeta("neo3",  "Classic", _logo("neo3"),  pack_size=9),
    SetMeta("neo2",  "Classic", _logo("neo2"),  pack_size=9),
    SetMeta("neo1",  "Classic", _logo("neo1"),  pack_size=9),
    SetMeta("gym2",  "Classic", _logo("gym2"),  pack_size=9),
    SetMeta("gym1",  "Classic", _logo("gym1"),  pack_size=9),
    SetMeta("base5", "Classic", _logo("base5"), pack_size=9),
    SetMeta("base4", "Classic", _logo("base4"), pack_size=9),
    SetMeta("base3", "Classic", _logo("base3"), pack_size=9),
    SetMeta("base2", "Classic", _logo("base2"), pack_size=9),
    SetMeta("base1", "Classic", _logo("base1"), pack_size=9),
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
