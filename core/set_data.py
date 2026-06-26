"""
core/set_data.py

Static metadata for every supported set:
  - Era grouping
  - Pack art image URL (official art where possible)
  - Set banner / logo fallback
  - Pack size and slot layout override (defaults handled by pack_engine)

Pack art URLs are sourced from Limitless TCG, Bulbapedia, and the official
Pokémon website — all publicly accessible images used for display only.
"""

from dataclasses import dataclass, field


@dataclass
class SetMeta:
    set_id:      str            # Matches pokemontcg.io set ID
    era:         str            # Era label (must match ERA_ORDER in config.py)
    pack_arts:   list[str]      # One or more pack face image URLs
    pack_size:   int   = 10     # Cards per pack (10 modern, 9 classic)
    set_banner:  str   = ""     # Wide banner image URL (optional override)


# ─────────────────────────────────────────────────────────────────────────────
#  Scarlet & Violet era
# ─────────────────────────────────────────────────────────────────────────────
SV_SETS: list[SetMeta] = [
    SetMeta(
        set_id="sv8pt5",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV8pt5/SV8pt5_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV8pt5/SV8pt5_en_packart_2.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV8pt5/SV8pt5_en_packart_3.png",
        ],
    ),
    SetMeta(
        set_id="sv8",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV8/SV8_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV8/SV8_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="sv7",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV7/SV7_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV7/SV7_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="sv6pt5",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV6pt5/SV6pt5_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV6pt5/SV6pt5_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="sv6",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV6/SV6_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV6/SV6_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="sv5",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV5/SV5_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV5/SV5_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="sv4pt5",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV4pt5/SV4pt5_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV4pt5/SV4pt5_en_packart_2.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV4pt5/SV4pt5_en_packart_3.png",
        ],
    ),
    SetMeta(
        set_id="sv4",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV4/SV4_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV4/SV4_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="sv3pt5",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV3pt5/SV3pt5_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV3pt5/SV3pt5_en_packart_2.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV3pt5/SV3pt5_en_packart_3.png",
        ],
    ),
    SetMeta(
        set_id="sv3",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV3/SV3_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV3/SV3_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="sv2",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV2/SV2_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV2/SV2_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="sv1",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV1/SV1_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV1/SV1_en_packart_2.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SV1/SV1_en_packart_3.png",
        ],
    ),
    SetMeta(
        set_id="svp",
        era="Scarlet & Violet",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SVP/SVP_en_packart_1.png",
        ],
        pack_size=10,
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Sword & Shield era
# ─────────────────────────────────────────────────────────────────────────────
SWSH_SETS: list[SetMeta] = [
    SetMeta(
        set_id="swsh12pt5",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/CRZ/CRZ_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/CRZ/CRZ_en_packart_2.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/CRZ/CRZ_en_packart_3.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/CRZ/CRZ_en_packart_4.png",
        ],
    ),
    SetMeta(
        set_id="swsh12",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SIT/SIT_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SIT/SIT_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="swsh11",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/LOR/LOR_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/LOR/LOR_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="swsh10",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/PGO/PGO_en_packart_1.png",
        ],
    ),
    SetMeta(
        set_id="swsh9",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/BRS/BRS_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/BRS/BRS_en_packart_2.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/BRS/BRS_en_packart_3.png",
        ],
    ),
    SetMeta(
        set_id="swsh8",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/FST/FST_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/FST/FST_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="swsh7",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/EVS/EVS_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/EVS/EVS_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="swsh6",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/CRE/CRE_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/CRE/CRE_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="swsh5",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/BST/BST_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/BST/BST_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="swsh4",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/VIV/VIV_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/VIV/VIV_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="swsh3",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/DAA/DAA_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/DAA/DAA_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="swsh2",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/RCL/RCL_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/RCL/RCL_en_packart_2.png",
        ],
    ),
    SetMeta(
        set_id="swsh1",
        era="Sword & Shield",
        pack_arts=[
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SSH/SSH_en_packart_1.png",
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SSH/SSH_en_packart_2.png",
        ],
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Classic era (Base Set through Legendary Collection)
# ─────────────────────────────────────────────────────────────────────────────
CLASSIC_SETS: list[SetMeta] = [
    SetMeta(
        set_id="base1",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/9/9a/Pokemon_Base_Set_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="jungle",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/4/46/Pokemon_Jungle_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="fossil",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/0/0e/Pokemon_Fossil_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="base2",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/2/2e/Pokemon_Base_Set_2_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="teamrocket",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/c/c9/Team_Rocket_Set_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="gym1",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/7/71/Pokemon_Gym_Heroes_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="gym2",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/3/3e/Pokemon_Gym_Challenge_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="neo1",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/4/4e/Pokemon_Neo_Genesis_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="neo2",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/9/97/Pokemon_Neo_Discovery_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="neo3",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/f/f9/Pokemon_Neo_Revelation_pack.jpg",
        ],
        pack_size=10,
    ),
    SetMeta(
        set_id="neo4",
        era="Classic",
        pack_arts=[
            "https://upload.wikimedia.org/wikipedia/en/f/f6/Pokemon_Neo_Destiny_pack.jpg",
        ],
        pack_size=10,
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Master lookup
# ─────────────────────────────────────────────────────────────────────────────
ALL_SET_META: dict[str, SetMeta] = {
    s.set_id: s for s in (SV_SETS + SWSH_SETS + CLASSIC_SETS)
}


def get_meta(set_id: str) -> SetMeta | None:
    return ALL_SET_META.get(set_id)


def sets_by_era() -> dict[str, list[SetMeta]]:
    """Return a dict of era -> [SetMeta, ...] in the order sets are defined."""
    result: dict[str, list[SetMeta]] = {}
    for s in (SV_SETS + SWSH_SETS + CLASSIC_SETS):
        result.setdefault(s.era, []).append(s)
    return result
