from dataclasses import dataclass


def _lim(code: str, n: int) -> list[str]:
    base = f"https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/{code}"
    return [f"{base}/{code}_en_packart_{i}.png" for i in range(1, n + 1)]


def _ptcg(set_id: str) -> list[str]:
    return [f"https://images.pokemontcg.io/{set_id}/logo.png"]


@dataclass
class SetMeta:
    set_id:    str
    era:       str
    pack_arts: list[str]
    pack_size: int = 10


ME_SETS: list[SetMeta] = [
    SetMeta("me2pt5", "Mega Evolution", _lim("ME2PT5", 3)),
    SetMeta("me2",    "Mega Evolution", _lim("ME2",    2)),
    SetMeta("me1",    "Mega Evolution", _lim("ME1",    3)),
]

SV_SETS: list[SetMeta] = [
    SetMeta("sv10",   "Scarlet & Violet", _lim("SV10",   3)),
    SetMeta("sv9",    "Scarlet & Violet", _lim("SV9",    3)),
    SetMeta("sv8pt5", "Scarlet & Violet", _lim("SV8PT5", 5)),
    SetMeta("sv8",    "Scarlet & Violet", _lim("SV8",    3)),
    SetMeta("sv7",    "Scarlet & Violet", _lim("SV7",    2)),
    SetMeta("sv6pt5", "Scarlet & Violet", _lim("SV6PT5", 2)),
    SetMeta("sv6",    "Scarlet & Violet", _lim("SV6",    3)),
    SetMeta("sv5",    "Scarlet & Violet", _lim("SV5",    3)),
    SetMeta("sv4pt5", "Scarlet & Violet", _lim("SV4PT5", 2)),
    SetMeta("sv4",    "Scarlet & Violet", _lim("SV4",    3)),
    SetMeta("sv3pt5", "Scarlet & Violet", _lim("SV3PT5", 3)),
    SetMeta("sv3",    "Scarlet & Violet", _lim("SV3",    3)),
    SetMeta("sv2",    "Scarlet & Violet", _lim("SV2",    3)),
    SetMeta("sv1",    "Scarlet & Violet", _lim("SV1",    3)),
]

SWSH_SETS: list[SetMeta] = [
    SetMeta("swsh12pt5", "Sword & Shield", _lim("CRZ",  4)),
    SetMeta("swsh12",    "Sword & Shield", _lim("SIT",  2)),
    SetMeta("swsh11",    "Sword & Shield", _lim("LOR",  2)),
    SetMeta("pgo",       "Sword & Shield", _lim("PGO",  1)),
    SetMeta("swsh10",    "Sword & Shield", _lim("ASR",  3)),
    SetMeta("swsh9",     "Sword & Shield", _lim("BRS",  3)),
    SetMeta("swsh8",     "Sword & Shield", _lim("FST",  4)),
    SetMeta("swsh7",     "Sword & Shield", _lim("EVS",  3)),
    SetMeta("swsh6",     "Sword & Shield", _lim("CRE",  3)),
    SetMeta("swsh5",     "Sword & Shield", _lim("BST",  3)),
    SetMeta("swsh4",     "Sword & Shield", _lim("VIV",  3)),
    SetMeta("swsh3",     "Sword & Shield", _lim("DAA",  3)),
    SetMeta("swsh2",     "Sword & Shield", _lim("RCL",  3)),
    SetMeta("swsh1",     "Sword & Shield", _lim("SSH",  3)),
]

SM_SETS: list[SetMeta] = [
    SetMeta("sm12",  "Sun & Moon", _lim("CEC",  3)),
    SetMeta("sm11",  "Sun & Moon", _lim("UNM",  3)),
    SetMeta("sm10",  "Sun & Moon", _lim("UNB",  3)),
    SetMeta("sm9",   "Sun & Moon", _lim("TEU",  3)),
    SetMeta("sm8",   "Sun & Moon", _lim("LOT",  3)),
    SetMeta("sm7",   "Sun & Moon", _lim("CES",  3)),
    SetMeta("sm6",   "Sun & Moon", _lim("FLI",  2)),
    SetMeta("sm5",   "Sun & Moon", _lim("UPR",  3)),
    SetMeta("sm4",   "Sun & Moon", _lim("CIN",  2)),
    SetMeta("sm3",   "Sun & Moon", _lim("BUS",  3)),
    SetMeta("sm2",   "Sun & Moon", _lim("GRI",  3)),
    SetMeta("sm1",   "Sun & Moon", _lim("SUM",  3)),
]

XY_SETS: list[SetMeta] = [
    SetMeta("xy12", "XY", _lim("EVO",  3)),
    SetMeta("xy11", "XY", _lim("STS",  2)),
    SetMeta("xy10", "XY", _lim("FAC",  2)),
    SetMeta("xy9",  "XY", _lim("BKP",  2)),
    SetMeta("xy8",  "XY", _lim("BKT",  3)),
    SetMeta("xy7",  "XY", _lim("AOR",  2)),
    SetMeta("xy6",  "XY", _lim("ROS",  3)),
    SetMeta("xy5",  "XY", _lim("PRC",  3)),
    SetMeta("xy4",  "XY", _lim("PHF",  2)),
    SetMeta("xy3",  "XY", _lim("FFI",  2)),
    SetMeta("xy2",  "XY", _lim("FLF",  3)),
    SetMeta("xy1",  "XY", _lim("XY",   3)),
]

BW_SETS: list[SetMeta] = [
    SetMeta("bw11", "Black & White", _lim("LTR",  3)),
    SetMeta("bw10", "Black & White", _lim("PLB",  2)),
    SetMeta("bw9",  "Black & White", _lim("PLF",  2)),
    SetMeta("bw8",  "Black & White", _lim("PLS",  3)),
    SetMeta("bw7",  "Black & White", _lim("BCR",  3)),
    SetMeta("bw6",  "Black & White", _lim("DRX",  3)),
    SetMeta("bw5",  "Black & White", _lim("DEX",  2)),
    SetMeta("bw4",  "Black & White", _lim("NXD",  3)),
    SetMeta("bw3",  "Black & White", _lim("NVI",  3)),
    SetMeta("bw2",  "Black & White", _lim("EPO",  2)),
    SetMeta("bw1",  "Black & White", _lim("BLW",  3)),
]

HGSS_SETS: list[SetMeta] = [
    SetMeta("col1",  "HeartGold & SoulSilver", _lim("CL",  2)),
    SetMeta("hgss4", "HeartGold & SoulSilver", _lim("TM",  3)),
    SetMeta("hgss3", "HeartGold & SoulSilver", _lim("UD",  2)),
    SetMeta("hgss2", "HeartGold & SoulSilver", _lim("UL",  3)),
    SetMeta("hgss1", "HeartGold & SoulSilver", _lim("HS",  3)),
]

PL_SETS: list[SetMeta] = [
    SetMeta("pl4", "Platinum", _lim("AR",  3)),
    SetMeta("pl3", "Platinum", _lim("SV",  3)),
    SetMeta("pl2", "Platinum", _lim("RR",  3)),
    SetMeta("pl1", "Platinum", _lim("PT",  3)),
]

DP_SETS: list[SetMeta] = [
    SetMeta("dp7", "Diamond & Pearl", _lim("SF",  2)),
    SetMeta("dp6", "Diamond & Pearl", _lim("LA",  3)),
    SetMeta("dp5", "Diamond & Pearl", _lim("MD",  2)),
    SetMeta("dp4", "Diamond & Pearl", _lim("GE",  3)),
    SetMeta("dp3", "Diamond & Pearl", _lim("SW",  3)),
    SetMeta("dp2", "Diamond & Pearl", _lim("MT",  3)),
    SetMeta("dp1", "Diamond & Pearl", _lim("DP",  3)),
]

CLASSIC_SETS: list[SetMeta] = [
    SetMeta("neo4",  "Classic", _ptcg("neo4"),  pack_size=9),
    SetMeta("neo3",  "Classic", _ptcg("neo3"),  pack_size=9),
    SetMeta("neo2",  "Classic", _ptcg("neo2"),  pack_size=9),
    SetMeta("neo1",  "Classic", _ptcg("neo1"),  pack_size=9),
    SetMeta("gym2",  "Classic", _ptcg("gym2"),  pack_size=9),
    SetMeta("gym1",  "Classic", _ptcg("gym1"),  pack_size=9),
    SetMeta("base5", "Classic", _ptcg("base5"), pack_size=9),
    SetMeta("base4", "Classic", _ptcg("base4"), pack_size=9),
    SetMeta("base3", "Classic", _ptcg("base3"), pack_size=9),
    SetMeta("base2", "Classic", _ptcg("base2"), pack_size=9),
    SetMeta("base1", "Classic", _ptcg("base1"), pack_size=9),
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
