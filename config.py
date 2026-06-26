import os

TOKEN              = os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN_HERE")
POKEMON_TCG_API_KEY= os.getenv("POKEMON_TCG_API_KEY", "")
GUILD_ID           = int(os.getenv("GUILD_ID", 0))
PREFIX             = "!"
DB_PATH            = "data/collection.db"

SETS_PER_PAGE = 4
STORE_TIMEOUT = 180
PACK_TIMEOUT  = 300
