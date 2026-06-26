"""
cogs/collection.py

Commands for viewing your collection:
  /collection          — overview by set with total unique cards
  /binder [set_id]     — paginated card list, one per embed with image
  /stats               — your pack opening history and rarity breakdown
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging

from config import ERA_COLORS, PACK_TIMEOUT
from core.db import (
    get_collection,
    get_collection_summary,
    get_collection_card_count,
    get_unique_card_count,
    get_user_stats,
    get_pack_history,
    ensure_user,
)
from core.tcg_api import fetch_set

log = logging.getLogger("collection")


CARDS_PER_BINDER_PAGE = 1   # One card per embed (with full image)


# ─────────────────────────────────────────────────────────────────────────────
#  /collection — set-level overview
# ─────────────────────────────────────────────────────────────────────────────

class CollectionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="collection", description="View your Pokémon card collection")
    async def collection(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = str(interaction.user.id)
        await ensure_user(uid, str(interaction.user))

        summary = await get_collection_summary(uid)
        total   = await get_collection_card_count(uid)
        unique  = await get_unique_card_count(uid)
        stats   = await get_user_stats(uid)

        if not summary:
            embed = discord.Embed(
                title="📦  Your Collection",
                description=(
                    "You haven't opened any packs yet!\n"
                    "Use `/store` to browse sets and rip your first pack. 🎴"
                ),
                color=0xFFCC00,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"📦  {interaction.user.display_name}'s Collection",
            description=(
                f"**{unique}** unique cards  •  **{total}** total cards\n"
                f"**{stats['packs_opened'] if stats else 0}** packs opened\n\n"
                "Use `/binder <set>` to view cards from a specific set."
            ),
            color=0xFFCC00,
        )

        for row in summary[:20]:  # Discord field limit
            embed.add_field(
                name=row["set_name"] or row["set_id"],
                value=f"`{row['unique_cards']}` unique  •  `{row['total_cards']}` total",
                inline=True,
            )

        if len(summary) > 20:
            embed.set_footer(text=f"…and {len(summary) - 20} more sets. Use /binder to explore!")

        await interaction.followup.send(embed=embed)

    # ──────────────────────────────────────────────────────────────────────────
    #  /binder — paginated card viewer
    # ──────────────────────────────────────────────────────────────────────────

    @app_commands.command(name="binder", description="Flip through your collected cards")
    @app_commands.describe(set_filter="Optional: filter by set name or ID (e.g. sv1, 'Scarlet & Violet')")
    async def binder(
        self,
        interaction: discord.Interaction,
        set_filter: str | None = None,
    ):
        await interaction.response.defer()
        uid = str(interaction.user.id)
        await ensure_user(uid, str(interaction.user))

        # Resolve set_filter to a set_id if possible
        set_id = None
        if set_filter:
            set_id = set_filter.lower().strip()

        cards, total = await get_collection(uid, set_id=set_id, page=1, per_page=1)

        if not cards:
            msg = (
                f"No cards found for set `{set_filter}`."
                if set_filter else
                "Your binder is empty! Open some packs with `/store` first. 🎴"
            )
            await interaction.followup.send(msg)
            return

        view  = BinderView(uid=uid, set_id=set_id, total=total, user_id=interaction.user.id)
        embed = await view.build_embed()
        await interaction.followup.send(embed=embed, view=view)

    # ──────────────────────────────────────────────────────────────────────────
    #  /stats — pack history & rarity breakdown
    # ──────────────────────────────────────────────────────────────────────────

    @app_commands.command(name="stats", description="View your pack opening stats")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = str(interaction.user.id)
        await ensure_user(uid, str(interaction.user))

        user_stats  = await get_user_stats(uid)
        history     = await get_pack_history(uid, limit=10)
        total_cards = await get_collection_card_count(uid)
        unique      = await get_unique_card_count(uid)

        packs = user_stats["packs_opened"] if user_stats else 0

        embed = discord.Embed(
            title=f"📊  {interaction.user.display_name}'s Stats",
            color=0x7B68EE,
        )
        embed.add_field(name="Packs Opened", value=f"`{packs}`",       inline=True)
        embed.add_field(name="Total Cards",  value=f"`{total_cards}`", inline=True)
        embed.add_field(name="Unique Cards", value=f"`{unique}`",      inline=True)

        if history:
            lines = "\n".join(
                f"`{row['packs']:>3}` packs  →  {row['set_name']}"
                for row in history
            )
            embed.add_field(name="Recent Sets", value=lines, inline=False)

        await interaction.followup.send(embed=embed)


# ─────────────────────────────────────────────────────────────────────────────
#  Binder paginator view
# ─────────────────────────────────────────────────────────────────────────────

class BinderView(discord.ui.View):
    def __init__(self, uid: str, set_id: str | None, total: int, user_id: int):
        super().__init__(timeout=PACK_TIMEOUT)
        self.uid      = uid
        self.set_id   = set_id
        self.total    = total
        self.page     = 1          # 1-indexed
        self.user_id  = user_id

        self._rebuild_buttons()

    async def build_embed(self) -> discord.Embed:
        cards, _ = await get_collection(
            self.uid, set_id=self.set_id, page=self.page, per_page=1
        )
        if not cards:
            return discord.Embed(title="No cards found.", color=0x9E9E9E)

        card = cards[0]
        rarity    = card.get("rarity", "?")
        card_name = card.get("card_name", "Unknown")
        set_name  = card.get("set_name", "?")
        count     = card.get("count", 1)
        image_url = card.get("image_url", "")

        # Colour by rarity tier
        from core.pack_engine import rarity_tier
        tier   = rarity_tier(rarity)
        colors = {0: 0x9E9E9E, 1: 0x4CAF50, 2: 0x2196F3, 3: 0x9C27B0, 4: 0xFFD700}
        color  = colors.get(tier, 0x9E9E9E)

        embed = discord.Embed(title=card_name, color=color)
        if image_url:
            embed.set_image(url=image_url)
        embed.add_field(name="Rarity",  value=f"`{rarity}`",  inline=True)
        embed.add_field(name="Set",     value=f"`{set_name}`", inline=True)
        embed.add_field(name="Owned",   value=f"`×{count}`",  inline=True)

        progress = f"Card {self.page} of {self.total}"
        embed.set_footer(text=progress)
        return embed

    def _rebuild_buttons(self):
        self.clear_items()

        prev = discord.ui.Button(
            label="◀ Prev",
            style=discord.ButtonStyle.secondary,
            disabled=self.page <= 1,
            row=0,
        )
        prev.callback = self._prev
        self.add_item(prev)

        ind = discord.ui.Button(
            label=f"{self.page} / {self.total}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
            row=0,
        )
        self.add_item(ind)

        nxt = discord.ui.Button(
            label="Next ▶",
            style=discord.ButtonStyle.secondary,
            disabled=self.page >= self.total,
            row=0,
        )
        nxt.callback = self._next
        self.add_item(nxt)

    async def _prev(self, interaction: discord.Interaction):
        self.page = max(1, self.page - 1)
        self._rebuild_buttons()
        embed = await self.build_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def _next(self, interaction: discord.Interaction):
        self.page = min(self.total, self.page + 1)
        self._rebuild_buttons()
        embed = await self.build_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This binder belongs to someone else!", ephemeral=True
            )
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
#  Setup
# ─────────────────────────────────────────────────────────────────────────────

async def setup(bot: commands.Bot):
    await bot.add_cog(CollectionCog(bot))
