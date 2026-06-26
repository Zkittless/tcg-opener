import os

# ── Bot credentials ──────────────────────────────────────────────────────────
# Set DISCORD_TOKEN in your environment, or paste it directly (not recommended)
TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ── Pokémon TCG API ───────────────────────────────────────────────────────────
# Free key from https://pokemontcg.io — gives 20k requests/day instead of 1k
POKEMON_TCG_API_KEY = os.getenv("POKEMON_TCG_API_KEY", "")

# ── Bot settings ──────────────────────────────────────────────────────────────
PREFIX = "!"           # Legacy prefix (slash commands are primary)
DB_PATH = "data/collection.db"

# ── Store / UI settings ───────────────────────────────────────────────────────
SETS_PER_PAGE    = 4   # How many sets shown per store page
STORE_TIMEOUT    = 180 # Seconds before store UI goes inactive
PACK_TIMEOUT     = 300 # Seconds before pack viewer goes inactive

# ── Era ordering (shown in this order in the store) ──────────────────────────
ERA_ORDER = [
    "Scarlet & Violet",
    "Sword & Shield",
    "Sun & Moon",
    "XY",
    "Black & White",
    "HeartGold & SoulSilver",
    "Platinum",
    "Diamond & Pearl",
    "EX",
    "Classic",
]

# ── Era colours for embeds ────────────────────────────────────────────────────
ERA_COLORS = {
    "Scarlet & Violet":        0xE3350D,
    "Sword & Shield":          0x2E6DB4,
    "Sun & Moon":              0xF5A623,
    "XY":                      0x0072BC,
    "Black & White":           0x4A4A4A,
    "HeartGold & SoulSilver":  0xC8A951,
    "Platinum":                0x7B7B9E,
    "Diamond & Pearl":         0x4B6EAF,
    "EX":                      0xA00000,
    "Classic":                 0xFFCC00,
}

ERA_EMOJIS = {
    "Scarlet & Violet":        "🔴",
    "Sword & Shield":          "🛡️",
    "Sun & Moon":              "☀️",
    "XY":                      "⚡",
    "Black & White":           "⬛",
    "HeartGold & SoulSilver":  "🌟",
    "Platinum":                "🔷",
    "Diamond & Pearl":         "💎",
    "EX":                      "🌀",
    "Classic":                 "🎴",
}
