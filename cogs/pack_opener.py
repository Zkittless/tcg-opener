"""
cogs/pack_opener.py

PackOpenerView — the card-by-card reveal after ripping a pack.

Features:
  • One card shown per embed with full art image
  • Previous / Next buttons to flip through
  • Slot label + rarity shown for each card
  • "Rip Another" button at the end of the pack
  • Saves all cards to the user's collection via core.db
  • Logs the pack opening
"""

import discord
from discord.ext import commands
import logging

from config import PACK_TIMEOUT
from core.set_data import ERA_COLORS
from core.set_data import SetMeta
from core.pack_engine import rip_pack, slot_excitement, rarity_tier
from core.tcg_api import card_rarity, card_name, card_number, get_card_image, format_price, get_card_price
from core.db import (
    ensure_user,
    add_cards_to_collection,
    increment_packs_opened,
    log_pack_open,
)

log = logging.getLogger("pack_opener")


# ─────────────────────────────────────────────────────────────────────────────
#  Embed builders
# ─────────────────────────────────────────────────────────────────────────────

def build_loading_embed(meta: SetMeta, api_set: dict) -> discord.Embed:
    name  = api_set.get("name", meta.set_id)
    color = ERA_COLORS.get(meta.era, 0xFFCC00)
    embed = discord.Embed(
        title=f"🎴  Ripping {name}...",
        description="Pulling cards from the pack...",
        color=color,
    )
    return embed


def _rarity_color(rarity: str) -> int:
    tier = rarity_tier(rarity)
    colors = {
        0: 0x9E9E9E,   # common  — grey
        1: 0x4CAF50,   # uncommon — green
        2: 0x2196F3,   # rare holo — blue
        3: 0x9C27B0,   # ultra rare — purple
        4: 0xFFD700,   # special / secret — gold
    }
    return colors.get(tier, 0x9E9E9E)


def build_card_embed(
    card: dict,
    card_index: int,
    total_cards: int,
    set_name: str,
    pack_art_url: str,
) -> discord.Embed:
    slot    = card.get("_slot", "common")
    rarity  = card_rarity(card)
    tier    = rarity_tier(rarity)
    name    = card_name(card)
    number  = card_number(card)
    image   = get_card_image(card, hires=True)
    slot_lbl = slot_excitement(card)
    color   = _rarity_color(rarity)

    # ── Energy card (bonus/trick card) ────────────────────────────────────────
    if slot == "energy":
        embed = discord.Embed(
            title="⚡  Basic Energy",
            description=(
                "The **pack trick card** — moved from the back to the front.\n"
                "This is your guaranteed Basic Energy card, included as a bonus "
                "in every Scarlet & Violet pack."
            ),
            color=0x78C850,  # grass green
        )
        progress = "".join(
            "🟨" if i == card_index else ("🟩" if i < card_index else "⬛")
            for i in range(total_cards)
        )
        embed.set_footer(text=f"Card {card_index + 1} of {total_cards}  {progress}")
        return embed

    # ── Regular card ──────────────────────────────────────────────────────────

    # Title with excitement scaling for hits
    if tier >= 4:
        title = f"🌟✨  {name}  ✨🌟"
    elif tier == 3:
        title = f"💫  {name}  💫"
    elif tier == 2:
        title = f"⭐  {name}"
    else:
        title = name

    embed = discord.Embed(title=title, color=color)

    if image:
        embed.set_image(url=image)

    embed.add_field(name="Rarity",  value=f"`{rarity}`",   inline=True)
    embed.add_field(name="Number",  value=f"`{number}`",   inline=True)
    embed.add_field(name="Set",     value=f"`{set_name}`", inline=True)
    embed.add_field(name="Slot",    value=slot_lbl,        inline=False)

    # Price — pokemontcg.io only returns price data with a paid API key.
    # We build a TCGPlayer search URL from the card name + set as a fallback.
    price_str = format_price(card)
    tcg_data  = card.get("tcgplayer") or {}
    tcg_url   = tcg_data.get("url", "")
    if not tcg_url:
        # Build a search URL from card name
        safe_name = card_name(card).replace(" ", "+")
        tcg_url = f"https://www.tcgplayer.com/search/pokemon/product?q={safe_name}&productLineName=pokemon"

    if price_str:
        embed.add_field(name="💵 Market Value", value=f"**{price_str}**\n[TCGPlayer]({tcg_url})", inline=True)
    else:
        embed.add_field(name="💵 Market Value", value=f"[Check TCGPlayer]({tcg_url})", inline=True)

    progress = "".join(
        "🟨" if i == card_index else ("🟩" if i < card_index else "⬛")
        for i in range(total_cards)
    )
    embed.set_footer(text=f"Card {card_index + 1} of {total_cards}  {progress}")

    return embed


def get_pack_retail_cost(set_id: str) -> float:
    """
    MSRP per booster pack by era.
    Sources: Official Pokemon TCG pricing, retailer listings.
      - Scarlet & Violet era: $4.49 (raised from $3.99 with SV launch)
      - Sword & Shield era:   $3.99
      - Sun & Moon era:       $3.99
      - XY era:               $3.99
      - Older eras:           $3.99
      - Special/mini sets (no booster box): slightly higher per-pack cost
        through ETBs/bundles, roughly $4.50-$5.00
    """
    sid = set_id.lower()

    # Mega Evolution era — sold only through ETBs/bundles ~$4.99/pack
    if sid.startswith("me"):
        return 4.99

    # SV special sets (no booster box, higher cost through bundles)
    if sid in {"sv8pt5", "sv4pt5", "sv3pt5", "sv6pt5"}:
        return 4.99

    # Standard SV sets
    if sid.startswith("sv"):
        return 4.49

    # SwSh, SM, XY, older
    return 3.99


def build_pack_summary_embed(
    cards: list[dict],
    set_name: str,
    username: str,
    set_id: str = "",
) -> discord.Embed:
    """Final embed shown after viewing all cards."""

    embed = discord.Embed(
        title=f"📦  Pack Summary — {set_name}",
        description=f"**{username}** just opened a pack!\nHere's what you got:",
        color=0xFFCC00,
    )

    # Filter out synthetic energy placeholder
    real_cards = [c for c in cards if c.get("_slot") != "energy"]

    # Separate hits from bulk
    hits   = [c for c in real_cards if rarity_tier(card_rarity(c)) >= 3]
    others = [c for c in real_cards if rarity_tier(card_rarity(c)) < 3]

    # Calculate total pulled value
    total_value   = 0.0
    has_any_price = False
    for c in real_cards:
        price, _ = get_card_price(c)
        if price is not None:
            total_value  += price
            has_any_price = True

    if hits:
        hit_lines = "\n".join(
            f"🌟 **{card_name(c)}** — `{card_rarity(c)}`  {format_price(c) or '`N/A`'}"
            for c in hits
        )
        embed.add_field(name="✨ Hits!", value=hit_lines, inline=False)

    card_lines = "\n".join(
        f"`{card_number(c):>4}` {card_name(c)} — {format_price(c) or '`N/A`'}"
        for c in others
    )
    if card_lines:
        embed.add_field(name="Rest of the Pack", value=card_lines[:1024], inline=False)

    if has_any_price:
        retail_cost = get_pack_retail_cost(set_id)
        profit      = total_value - retail_cost
        profit_str  = f"+${profit:,.2f} 📈" if profit >= 0 else f"-${abs(profit):,.2f} 📉"
        color_note  = "profit" if profit >= 0 else "loss"

        embed.add_field(
            name="💵 Cards Pulled Value",
            value=f"**${total_value:,.2f}**",
            inline=True,
        )
        embed.add_field(
            name="🏷️ Pack Retail Cost",
            value=f"**${retail_cost:.2f}**",
            inline=True,
        )
        embed.add_field(
            name=f"{'📈 Profit' if profit >= 0 else '📉 Loss'}",
            value=f"**{profit_str}**",
            inline=True,
        )

    embed.set_footer(text="Use /collection to see your full binder!")
    return embed


# ─────────────────────────────────────────────────────────────────────────────
#  Pack Opener View
# ─────────────────────────────────────────────────────────────────────────────

class PackOpenerView(discord.ui.View):
    """
    Stateful view for flipping through the cards in a ripped pack.
    Create via `await PackOpenerView.create(...)`.
    """

    def __init__(
        self,
        cards:       list[dict],
        meta:        SetMeta,
        api_set:     dict,
        api_sets:    dict[str, dict],
        user:        discord.Member | discord.User,
    ):
        super().__init__(timeout=PACK_TIMEOUT)
        self.cards    = cards
        self.meta     = meta
        self.api_set  = api_set
        self.api_sets = api_sets
        self.user     = user
        self.index    = 0
        self.summary  = False  # whether we're on the summary screen

        self.set_name    = api_set.get("name", meta.set_id)
        self.pack_art    = meta.pack_arts[0] if meta.pack_arts else ""

        self._rebuild_buttons()

    @classmethod
    async def create(
        cls,
        meta:     SetMeta,
        api_set:  dict,
        api_sets: dict[str, dict],
        user:     discord.Member | discord.User,
    ) -> "PackOpenerView":
        """Rip the pack, save to DB, then return the ready view."""
        cards = await rip_pack(meta.set_id, meta.pack_size)

        # Persist to database
        try:
            uid = str(user.id)
            await ensure_user(uid, str(user))
            await add_cards_to_collection(uid, cards)
            await increment_packs_opened(uid)
            await log_pack_open(uid, meta.set_id, api_set.get("name", meta.set_id))
        except Exception as e:
            log.error(f"DB error saving pack for {user}: {e}")

        return cls(
            cards    = cards,
            meta     = meta,
            api_set  = api_set,
            api_sets = api_sets,
            user     = user,
        )

    # ── Button layout ──────────────────────────────────────────────────────

    def _rebuild_buttons(self):
        self.clear_items()

        if self.summary:
            # Rip another / store buttons
            rip_again = discord.ui.Button(
                label="🎴  Rip Another Pack",
                style=discord.ButtonStyle.danger,
                row=0,
            )
            rip_again.callback = self._rip_another
            self.add_item(rip_again)

            back_store = discord.ui.Button(
                label="🏪  Back to Store",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
            back_store.callback = self._back_to_store
            self.add_item(back_store)

            review = discord.ui.Button(
                label="◀ Review Cards",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
            review.callback = self._review_cards
            self.add_item(review)
            return

        # Normal card-flip buttons
        prev = discord.ui.Button(
            label="◀ Prev",
            style=discord.ButtonStyle.secondary,
            disabled=self.index == 0,
            row=0,
        )
        prev.callback = self._prev_card
        self.add_item(prev)

        nxt_label = "Next ▶" if self.index < len(self.cards) - 1 else "Summary ✅"
        nxt_style = discord.ButtonStyle.secondary if self.index < len(self.cards) - 1 else discord.ButtonStyle.success
        nxt = discord.ui.Button(
            label=nxt_label,
            style=nxt_style,
            row=0,
        )
        nxt.callback = self._next_card
        self.add_item(nxt)

        # Quick skip to summary
        if self.index < len(self.cards) - 1:
            skip = discord.ui.Button(
                label="Skip to Summary ⏭",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
            skip.callback = self._skip_to_summary
            self.add_item(skip)

        # Back to store shortcut
        back = discord.ui.Button(
            label="🏪 Store",
            style=discord.ButtonStyle.secondary,
            row=1,
        )
        back.callback = self._back_to_store
        self.add_item(back)

        # Rip another shortcut
        rip = discord.ui.Button(
            label="🎴 Rip Another",
            style=discord.ButtonStyle.danger,
            row=1,
        )
        rip.callback = self._rip_another
        self.add_item(rip)

    # ── Embed builders ─────────────────────────────────────────────────────

    def current_embed(self) -> discord.Embed:
        if self.summary:
            return build_pack_summary_embed(
                self.cards, self.set_name, str(self.user.display_name),
                set_id=self.meta.set_id,
            )
        return build_card_embed(
            card        = self.cards[self.index],
            card_index  = self.index,
            total_cards = len(self.cards),
            set_name    = self.set_name,
            pack_art_url= self.pack_art,
        )

    # ── Button callbacks ───────────────────────────────────────────────────

    async def _prev_card(self, interaction: discord.Interaction):
        self.index = max(0, self.index - 1)
        self._rebuild_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    async def _next_card(self, interaction: discord.Interaction):
        if self.index >= len(self.cards) - 1:
            self.summary = True
        else:
            self.index += 1
        self._rebuild_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    async def _skip_to_summary(self, interaction: discord.Interaction):
        self.summary = True
        self._rebuild_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    async def _review_cards(self, interaction: discord.Interaction):
        self.summary = False
        self._rebuild_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    async def _rip_another(self, interaction: discord.Interaction):
        from core.set_data import get_meta
        await interaction.response.edit_message(
            embed=build_loading_embed(self.meta, self.api_set),
            view=None,
        )
        new_view = await PackOpenerView.create(
            meta     = self.meta,
            api_set  = self.api_set,
            api_sets = self.api_sets,
            user     = interaction.user,
        )
        await interaction.edit_original_response(
            embed=new_view.current_embed(),
            view=new_view,
        )

    async def _back_to_store(self, interaction: discord.Interaction):
        from cogs.store import EraSelectorView, build_era_embed
        view  = EraSelectorView(api_sets=self.api_sets, user_id=interaction.user.id)
        embed = build_era_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "This pack belongs to someone else! Use `/store` to open your own.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


# ─────────────────────────────────────────────────────────────────────────────
#  Cog
# ─────────────────────────────────────────────────────────────────────────────

class PackOpenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot):
    await bot.add_cog(PackOpenerCog(bot))
