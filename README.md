# 🎴 Pokémon Pack Bot

A Discord bot that lets you rip Pokémon TCG packs with **real pull rates**, browse packs by set in a visual store, and track your collection — all with card images pulled live from the official Pokémon TCG API.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| `/store` | Browse sets by era, view pack art, choose your pack, rip it |
| Card-by-card reveal | Flip through each card one at a time with full art images |
| Real pull rates | Accurate slot weights for SV, Sword & Shield, and Classic eras |
| `/collection` | Overview of every set you have cards from |
| `/binder [set]` | Page through your cards one at a time with full images |
| `/stats` | Packs opened, total cards, unique cards, recent sets |
| Collection DB | SQLite — every card you pull is saved per user |

---

## 🛠️ Setup

### 1. Clone / download the bot

```
pokemon-pack-bot/
├── bot.py
├── config.py
├── requirements.txt
├── cogs/
│   ├── store.py
│   ├── pack_opener.py
│   └── collection.py
├── core/
│   ├── tcg_api.py
│   ├── pack_engine.py
│   ├── set_data.py
│   └── db.py
└── data/               ← auto-created, holds collection.db
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Requires **Python 3.11+**.

### 3. Create your Discord bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. New Application → Bot → Add Bot
3. Enable **Message Content Intent** under Privileged Gateway Intents
4. Copy the **Token**
5. OAuth2 → URL Generator → `bot` + `applications.commands` scopes
6. Permissions: `Send Messages`, `Embed Links`, `Attach Files`, `Use Slash Commands`
7. Invite the bot to your server using the generated URL

### 4. Get a Pokémon TCG API key (recommended, free)

Without a key you get **1,000 requests/day**. With a free key from [pokemontcg.io](https://pokemontcg.io) you get **20,000/day** — highly recommended.

1. Sign up at [pokemontcg.io](https://pokemontcg.io)
2. Copy your API key from the dashboard

### 5. Set environment variables

**Linux / macOS:**
```bash
export DISCORD_TOKEN="your-bot-token-here"
export POKEMON_TCG_API_KEY="your-tcg-api-key-here"   # optional but recommended
```

**Windows (PowerShell):**
```powershell
$env:DISCORD_TOKEN="your-bot-token-here"
$env:POKEMON_TCG_API_KEY="your-tcg-api-key-here"
```

Or edit `config.py` directly (not recommended for shared servers):
```python
TOKEN = "your-bot-token-here"
POKEMON_TCG_API_KEY = "your-tcg-api-key-here"
```

### 6. Run the bot

```bash
python bot.py
```

On first run the bot will:
- Create `data/collection.db` automatically
- Fetch all set data from the TCG API (cached in memory after first call)
- Sync slash commands with Discord (may take a minute to appear)

---

## 🎮 Commands

| Command | Description |
|---------|-------------|
| `/store` | Open the pack store — browse eras, sets, pack art, and rip! |
| `/collection` | See your card collection grouped by set |
| `/binder` | Page through all your cards with images |
| `/binder set_filter:sv1` | Filter your binder to a specific set |
| `/stats` | Your pack opening history and card counts |

---

## 🃏 Pack Structure & Pull Rates

### Modern (Scarlet & Violet era) — 10 cards
| Slot | Contents |
|------|----------|
| 1–5 | Commons |
| 6–7 | Commons / Uncommons |
| 8 | Uncommon |
| 9 | **Reverse Holo** (any rarity, foil treatment) |
| 10 | **Rare Slot** — see rates below |

**Rare slot rates (SV):**
| Result | Approx. Rate |
|--------|-------------|
| Rare Holo | ~1 in 4.5 packs |
| Double Rare (Rare ex) | ~1 in 3 packs |
| Illustration Rare | ~1 in 6 packs |
| Ultra Rare (Full Art) | ~1 in 8 packs |
| Special Illustration Rare | ~1 in 11 packs |
| Hyper Rare (Gold) | ~1 in 25 packs |
| Shiny Rare | ~1 in 67 packs |
| Shiny Ultra Rare | ~1 in 200 packs |

### Sword & Shield era — 10 cards
Similar slot structure with V, VMAX/VSTAR, Rainbow Rare, Trainer Gallery hits.

### Classic (Base Set era) — 10 cards
| Slot | Contents |
|------|----------|
| 1–5 | Commons |
| 6–8 | Uncommons |
| 9–10 | Rare slot (Rare Holo ~1 in 3, Rare otherwise) |

---

## 🗃️ Supported Sets

### Scarlet & Violet
Prismatic Evolutions, Surging Sparks, Stellar Crown, Shrouded Fable, Twilight Masquerade, Temporal Forces, Paradox Rift, 151, Obsidian Flames, Paldea Evolved, Scarlet & Violet Base

### Sword & Shield
Crown Zenith, Silver Tempest, Lost Origin, Pokémon GO, Brilliant Stars, Fusion Strike, Evolving Skies, Chilling Reign, Battle Styles, Vivid Voltage, Darkness Ablaze, Rebel Clash, Sword & Shield Base

### Classic
Base Set, Jungle, Fossil, Base Set 2, Team Rocket, Gym Heroes, Gym Challenge, Neo Genesis, Neo Discovery, Neo Revelation, Neo Destiny

---

## 🔧 Customisation

**Add more sets:** Edit `core/set_data.py` — add a `SetMeta` entry with the TCG API set ID and pack art URLs from [limitlesstcg.com](https://limitlesstcg.com).

**Tune pull rates:** Edit `core/pack_engine.py` — the `RARE_SLOT_MODERN`, `RARE_SLOT_SWSH`, and `RARE_SLOT_CLASSIC` tables control exact weights.

**Add an economy:** The store is set up without costs intentionally, but you could hook into the `/store` flow in `cogs/store.py` to add a currency check before `_rip_pack`.

---

## 📝 Notes

- Card images are served directly from the Pokémon TCG API CDN — no images are stored locally.
- Pack art images are sourced from Limitless TCG and Wikimedia (publicly accessible).
- The bot uses Discord's slash command system — old `!` prefix commands are not the primary interface.
- The `data/collection.db` SQLite file stores all user collections. Back it up regularly!

---

## 🐛 Troubleshooting

**Slash commands not appearing?**
Slash commands can take up to 1 hour to propagate globally. For instant updates during development, add your server's Guild ID and use `bot.tree.sync(guild=discord.Object(id=YOUR_GUILD_ID))` in `setup_hook`.

**"Missing Access" errors?**
Make sure the bot has `Embed Links`, `Send Messages`, and `Use Application Commands` permissions in the channel.

**Images not showing?**
Some pack art URLs from older sets (Classic era) may be less reliable. The bot will still work — the embed will just show without an image.

**API rate limits?**
Get a free API key from [pokemontcg.io](https://pokemontcg.io) — it raises the limit from 1,000 to 20,000 requests/day. Set data is cached in memory after first fetch, so repeated pack openings from the same set won't re-hit the API for cards.
