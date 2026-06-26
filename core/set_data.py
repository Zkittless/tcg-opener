"""
core/set_data.py

Pack art URLs from pokesymbols.com — verified public image hosting, consistent pattern:
https://pokesymbols.com/images/tcg/sets/booster-pack-art/{slug}-pack-{n}.jpg

Every URL on this page was confirmed from:
https://pokesymbols.com/tcg/booster-pack-art
"""

from dataclasses import dataclass

PS = "https://pokesymbols.com/images/tcg/sets/booster-pack-art"


def _ps(slug: str, count: int, ext: str = "jpg") -> list[str]:
    return [f"{PS}/{slug}-pack-{i}.{ext}" for i in range(count)]


@dataclass
class SetMeta:
    set_id:    str
    era:       str
    pack_arts: list[str]
    pack_size: int = 10


# ── Mega Evolution ────────────────────────────────────────────────────────────
ME_SETS: list[SetMeta] = [
    SetMeta("me2pt5", "Mega Evolution", _ps("ascended-heroes",   1, "png")),
    SetMeta("me2",    "Mega Evolution", _ps("phantasmal-flames", 4, "png")),
    SetMeta("me1",    "Mega Evolution", _ps("mega-evolution",    4, "png")),
]

# ── Scarlet & Violet ──────────────────────────────────────────────────────────
SV_SETS: list[SetMeta] = [
    SetMeta("sv10",   "Scarlet & Violet", _ps("destined-rivals",       4)),
    SetMeta("sv9",    "Scarlet & Violet", _ps("journey-together",      4)),
    SetMeta("sv8pt5", "Scarlet & Violet", _ps("prismatic-evolutions",  4)),
    SetMeta("sv8",    "Scarlet & Violet", _ps("surging-sparks",        4)),
    SetMeta("sv7",    "Scarlet & Violet", _ps("stellar-crown",         4)),
    SetMeta("sv6pt5", "Scarlet & Violet", _ps("shrouded-fable",        4)),
    SetMeta("sv6",    "Scarlet & Violet", _ps("twilight-masquerade",   4)),
    SetMeta("sv5",    "Scarlet & Violet", _ps("temporal-forces",       4)),
    SetMeta("sv4pt5", "Scarlet & Violet", _ps("paldean-fates",         2)),
    SetMeta("sv4",    "Scarlet & Violet", _ps("paradox-rift",          4)),
    SetMeta("sv3pt5", "Scarlet & Violet", _ps("pokemon-card-151",      3)),
    SetMeta("sv3",    "Scarlet & Violet", _ps("obsidian-flames",       3)),
    SetMeta("sv2",    "Scarlet & Violet", _ps("paldea-evolved",        3)),
    SetMeta("sv1",    "Scarlet & Violet", _ps("scarlet-violet",        3)),
]

# ── Sword & Shield ────────────────────────────────────────────────────────────
SWSH_SETS: list[SetMeta] = [
    SetMeta("swsh12pt5", "Sword & Shield", _ps("crown-zenith",      4)),
    SetMeta("swsh12",    "Sword & Shield", _ps("silver-tempest",    3)),
    SetMeta("swsh11",    "Sword & Shield", _ps("lost-origin",       4)),
    SetMeta("pgo",       "Sword & Shield", _ps("pokemon-go",        3)),
    SetMeta("swsh10",    "Sword & Shield", _ps("astral-radiance",   4)),
    SetMeta("swsh9",     "Sword & Shield", _ps("brilliant-stars",   4)),
    SetMeta("swsh8",     "Sword & Shield", _ps("fusion-strike",     4)),
    SetMeta("swsh7",     "Sword & Shield", _ps("evolving-skies",    4)),
    SetMeta("swsh6",     "Sword & Shield", _ps("chilling-reign",    4)),
    SetMeta("swsh5",     "Sword & Shield", _ps("battle-styles",     4)),
    SetMeta("swsh4",     "Sword & Shield", _ps("vivid-voltage",     4)),
    SetMeta("swsh3",     "Sword & Shield", _ps("darkness-ablaze",   3)),
    SetMeta("swsh2",     "Sword & Shield", _ps("rebel-clash",       4)),
    SetMeta("swsh1",     "Sword & Shield", _ps("sword-shield",      3)),
]

# ── Sun & Moon ────────────────────────────────────────────────────────────────
SM_SETS: list[SetMeta] = [
    SetMeta("sm12",  "Sun & Moon", _ps("cosmic-eclipse",    4)),
    SetMeta("sm11",  "Sun & Moon", _ps("unified-minds",     4)),
    SetMeta("sm10",  "Sun & Moon", _ps("unbroken-bonds",    4)),
    SetMeta("sm9",   "Sun & Moon", _ps("team-up",           3)),
    SetMeta("sm8",   "Sun & Moon", _ps("lost-thunder",      4)),
    SetMeta("sm7",   "Sun & Moon", _ps("celestial-storm",   4)),
    SetMeta("sm6",   "Sun & Moon", _ps("forbidden-light",   3)),
    SetMeta("sm5",   "Sun & Moon", _ps("ultra-prism",       4)),
    SetMeta("sm4",   "Sun & Moon", _ps("crimson-invasion",  3)),
    SetMeta("sm3",   "Sun & Moon", _ps("burning-shadows",   3)),
    SetMeta("sm2",   "Sun & Moon", _ps("guardians-rising",  4)),
    SetMeta("sm1",   "Sun & Moon", _ps("sun-moon",          3)),
]

# ── XY ───────────────────────────────────────────────────────────────────────
XY_SETS: list[SetMeta] = [
    SetMeta("xy12", "XY", _ps("evolutions",      3)),
    SetMeta("xy11", "XY", _ps("steam-siege",     3)),
    SetMeta("xy10", "XY", _ps("fates-collide",   3)),
    SetMeta("xy9",  "XY", _ps("breakpoint",      3)),
    SetMeta("xy8",  "XY", _ps("breakthrough",    3)),
    SetMeta("xy7",  "XY", _ps("ancient-origins", 3)),
    SetMeta("xy6",  "XY", _ps("roaring-skies",   3)),
    SetMeta("xy5",  "XY", _ps("primal-clash",    4)),
    SetMeta("xy4",  "XY", _ps("phantom-forces",  3)),
    SetMeta("xy3",  "XY", _ps("furious-fists",   3)),
    SetMeta("xy2",  "XY", _ps("flashfire",       3)),
    SetMeta("xy1",  "XY", _ps("xy",              3)),
]

# ── Black & White ─────────────────────────────────────────────────────────────
BW_SETS: list[SetMeta] = [
    SetMeta("bw11", "Black & White", _ps("legendary-treasures", 3)),
    SetMeta("bw10", "Black & White", _ps("plasma-blast",        3)),
    SetMeta("bw9",  "Black & White", _ps("plasma-freeze",       3)),
    SetMeta("bw8",  "Black & White", _ps("plasma-storm",        3)),
    SetMeta("bw7",  "Black & White", _ps("boundaries-crossed",  3)),
    SetMeta("bw6",  "Black & White", _ps("dragons-exalted",     3)),
    SetMeta("bw5",  "Black & White", _ps("dark-explorers",      3)),
    SetMeta("bw4",  "Black & White", _ps("next-destinies",      3)),
    SetMeta("bw3",  "Black & White", _ps("noble-victories",     3)),
    SetMeta("bw2",  "Black & White", _ps("emerging-powers",     3)),
    SetMeta("bw1",  "Black & White", _ps("black-white",         3)),
]

# ── HeartGold & SoulSilver ────────────────────────────────────────────────────
HGSS_SETS: list[SetMeta] = [
    SetMeta("col1",  "HeartGold & SoulSilver", _ps("call-of-legends",   3)),
    SetMeta("hgss4", "HeartGold & SoulSilver", _ps("triumphant",        3)),
    SetMeta("hgss3", "HeartGold & SoulSilver", _ps("undaunted",         3)),
    SetMeta("hgss2", "HeartGold & SoulSilver", _ps("unleashed",         3)),
    SetMeta("hgss1", "HeartGold & SoulSilver", _ps("heartgold-soulsilver", 3)),
]

# ── Platinum ──────────────────────────────────────────────────────────────────
PL_SETS: list[SetMeta] = [
    SetMeta("pl4", "Platinum", _ps("arceus",         3)),
    SetMeta("pl3", "Platinum", _ps("supreme-victors", 3)),
    SetMeta("pl2", "Platinum", _ps("rising-rivals",  3)),
    SetMeta("pl1", "Platinum", _ps("platinum",       3)),
]

# ── Diamond & Pearl ───────────────────────────────────────────────────────────
DP_SETS: list[SetMeta] = [
    SetMeta("dp7", "Diamond & Pearl", _ps("stormfront",          3)),
    SetMeta("dp6", "Diamond & Pearl", _ps("legends-awakened",    3)),
    SetMeta("dp5", "Diamond & Pearl", _ps("majestic-dawn",       3)),
    SetMeta("dp4", "Diamond & Pearl", _ps("great-encounters",    3)),
    SetMeta("dp3", "Diamond & Pearl", _ps("secret-wonders",      3)),
    SetMeta("dp2", "Diamond & Pearl", _ps("mysterious-treasures", 3)),
    SetMeta("dp1", "Diamond & Pearl", _ps("diamond-pearl",       3)),
]

# ── Classic / WotC ────────────────────────────────────────────────────────────
CLASSIC_SETS: list[SetMeta] = [
    SetMeta("neo4",  "Classic", _ps("neo-destiny",          3), pack_size=9),
    SetMeta("neo3",  "Classic", _ps("neo-revelation",       3), pack_size=9),
    SetMeta("neo2",  "Classic", _ps("neo-discovery",        3), pack_size=9),
    SetMeta("neo1",  "Classic", _ps("neo-genesis",          3), pack_size=9),
    SetMeta("gym2",  "Classic", _ps("gym-challenge",        3), pack_size=9),
    SetMeta("gym1",  "Classic", _ps("gym-heroes",           3), pack_size=9),
    SetMeta("base5", "Classic", _ps("team-rocket",          3), pack_size=9),
    SetMeta("base4", "Classic", _ps("base-set-2",           3), pack_size=9),
    SetMeta("base3", "Classic", _ps("fossil",               3), pack_size=9),
    SetMeta("base2", "Classic", _ps("jungle",               3), pack_size=9),
    SetMeta("base1", "Classic", _ps("base-set",             3), pack_size=9),
]

# ── Master lookup ─────────────────────────────────────────────────────────────
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
