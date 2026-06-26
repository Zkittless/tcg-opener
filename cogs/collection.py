"""
cogs/collection.py

/collection — paginated card browser with delete button per card + bulk delete by value
/stats      — pack opening stats
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging

from config import PACK_TIMEOUT
from core.db import (
    get_collection,
    get_collection_summary,
    get_collection_card_count,
    get_unique_card_count,
    get_collection_total_value,
    get_user_stats,
    get_pack_history,
    ensure_user,
    delete_card,
    delete_cards_below_value,
)
from core.pack_engine import rarity_tier

log = logging.getLogger("collection")


def rarity_color(rarity: str) -> int:
    tier = rarity_tier(rarity)
    return {0: 0x9E9E9E, 1: 0x4CAF50, 2: 0x2196F3, 3: 0x9C27B0, 4: 0xFFD700}.get(tier, 0x9E9E9E)


# ─────────────────────────────────────────────────────────────────────────────
#  Threshold modal
# ─────────────────────────────────────────────────────────────────────────────

class ThresholdModal(discord.ui.Modal, title="Delete cards below value"):
    amount = discord.ui.TextInput(
        label="Delete all cards worth less than (USD)",
        placeholder="e.g. 1.00",
        required=True,
        max_length=10,
    )

    def __init__(self, uid: str, user_id: int):
        super().__init__()
        self.uid     = uid
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.amount.value.strip().lstrip("$")
        try:
            threshold = float(raw)
            if threshold < 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ Enter a valid dollar amount e.g. `1.00`", ephemeral=True
            )
            return

        await delete_cards_below_value(self.uid, threshold)
        _, total = await get_collection(self.uid, page=1, per_page=1)
        embed = await build_overview_embed(self.uid, interaction.user.display_name)
        view  = CollectionView(uid=self.uid, user_id=self.user_id, total=total)
        await interaction.response.edit_message(embed=embed, view=view)


# ─────────────────────────────────────────────────────────────────────────────
#  Overview embed
# ─────────────────────────────────────────────────────────────────────────────

async def build_overview_embed(uid: str, display_name: str) -> discord.Embed:
    total_cards = await get_collection_card_count(uid)
    unique      = await get_unique_card_count(uid)
    total_value = await get_collection_total_value(uid)
    stats       = await get_user_stats(uid)
    packs       = stats["packs_opened"] if stats else 0
    summary     = await get_collection_summary(uid)

    embed = discord.Embed(title=f"📦  {display_name}'s Collection", color=0xFFCC00)
    embed.add_field(name="Unique Cards",   value=f"`{unique}`",              inline=True)
    embed.add_field(name="Total Cards",    value=f"`{total_cards}`",         inline=True)
    embed.add_field(name="Packs Opened",   value=f"`{packs}`",               inline=True)
    embed.add_field(name="💵 Total Value", value=f"**${total_value:,.2f}**", inline=False)

    if summary:
        lines = "\n".join(
            f"**{r['set_name'] or r['set_id']}** — `{r['unique_cards']}` cards  •  **${r['set_value'] or 0:,.2f}**"
            for r in summary[:8]
        )
        embed.add_field(name="Sets", value=lines, inline=False)

    embed.set_footer(text="Browse Cards to view and delete  •  🗑️ Delete Below $X to bulk delete")
    return embed


# ─────────────────────────────────────────────────────────────────────────────
#  Collection overview view
# ─────────────────────────────────────────────────────────────────────────────

class CollectionView(discord.ui.View):
    def __init__(self, uid: str, user_id: int, total: int = 0):
        super().__init__(timeout=PACK_TIMEOUT)
        self.uid     = uid
        self.user_id = user_id
        self.total   = total
        self._rebuild()

    def _rebuild(self):
        self.clear_items()

        browse = discord.ui.Button(label="🔍 Browse Cards", style=discord.ButtonStyle.primary, row=0)
        browse.callback = self._browse
        self.add_item(browse)

        bulk = discord.ui.Button(label="🗑️ Delete Below $X", style=discord.ButtonStyle.danger, row=0)
        bulk.callback = self._bulk_delete
        self.add_item(bulk)

    async def _browse(self, interaction: discord.Interaction):
        _, total = await get_collection(self.uid, page=1, per_page=1)
        if total == 0:
            await interaction.response.send_message("No cards yet — open some packs! 🎴", ephemeral=True)
            return
        view  = BinderView(uid=self.uid, user_id=self.user_id, total=total)
        embed = await view.build_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    async def _bulk_delete(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ThresholdModal(uid=self.uid, user_id=self.user_id))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your collection!", ephemeral=True)
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
#  Binder — card by card with delete button
# ─────────────────────────────────────────────────────────────────────────────

class BinderView(discord.ui.View):
    def __init__(self, uid: str, user_id: int, total: int = 0,
                 set_id: str | None = None, min_value: float | None = None):
        super().__init__(timeout=PACK_TIMEOUT)
        self.uid       = uid
        self.user_id   = user_id
        self.total     = total
        self.set_id    = set_id
        self.min_value = min_value
        self.page      = 1
        self._rebuild()

    async def build_embed(self) -> discord.Embed:
        cards, _ = await get_collection(
            self.uid, set_id=self.set_id, min_value=self.min_value,
            page=self.page, per_page=1,
        )
        if not cards:
            return discord.Embed(title="No cards found.", color=0x9E9E9E)

        card      = cards[0]
        name      = card.get("card_name", "Unknown")
        rarity    = card.get("rarity", "?")
        set_name  = card.get("set_name", "?")
        count     = card.get("count", 1)
        image_url = card.get("image_url", "")
        price     = card.get("market_price")
        card_id   = card.get("card_id", "")

        embed = discord.Embed(title=name, color=rarity_color(rarity))
        if image_url:
            embed.set_image(url=image_url)
        embed.add_field(name="Rarity", value=f"`{rarity}`",   inline=True)
        embed.add_field(name="Set",    value=f"`{set_name}`", inline=True)
        embed.add_field(name="Owned",  value=f"`×{count}`",   inline=True)
        if price is not None:
            price_val = f"**${float(price):,.2f}**"
        else:
            safe = name.replace(" ", "+")
            price_val = f"[Check TCGPlayer](https://www.tcgplayer.com/search/pokemon/product?q={safe}&productLineName=pokemon)"
        embed.add_field(name="💵 Market Value", value=price_val, inline=True)
        embed.set_footer(text=f"Card {self.page} of {self.total}  •  ID: {card_id}")
        return embed

    def _rebuild(self):
        self.clear_items()

        prev = discord.ui.Button(label="◀", style=discord.ButtonStyle.secondary, disabled=self.page <= 1, row=0)
        prev.callback = self._prev
        self.add_item(prev)

        ind = discord.ui.Button(label=f"{self.page}/{self.total}", style=discord.ButtonStyle.secondary, disabled=True, row=0)
        self.add_item(ind)

        nxt = discord.ui.Button(label="▶", style=discord.ButtonStyle.secondary, disabled=self.page >= self.total, row=0)
        nxt.callback = self._next
        self.add_item(nxt)

        del_btn = discord.ui.Button(label="🗑️ Delete", style=discord.ButtonStyle.danger, row=1)
        del_btn.callback = self._delete
        self.add_item(del_btn)

        back = discord.ui.Button(label="◀ Collection", style=discord.ButtonStyle.secondary, row=1)
        back.callback = self._back
        self.add_item(back)

    async def _prev(self, interaction: discord.Interaction):
        self.page = max(1, self.page - 1)
        self._rebuild()
        await interaction.response.edit_message(embed=await self.build_embed(), view=self)

    async def _next(self, interaction: discord.Interaction):
        self.page = min(self.total, self.page + 1)
        self._rebuild()
        await interaction.response.edit_message(embed=await self.build_embed(), view=self)

    async def _delete(self, interaction: discord.Interaction):
        # Get current card
        cards, _ = await get_collection(
            self.uid, set_id=self.set_id, min_value=self.min_value,
            page=self.page, per_page=1,
        )
        if not cards:
            await interaction.response.edit_message(embed=await self.build_embed(), view=self)
            return

        card_id = cards[0]["card_id"]
        log.info(f"delete: uid={self.uid} card={card_id}")
        await delete_card(self.uid, card_id)

        # Recalculate total and clamp page
        _, self.total = await get_collection(
            self.uid, set_id=self.set_id, min_value=self.min_value,
            page=1, per_page=1,
        )
        if self.total == 0:
            # No cards left — go back to overview
            embed = await build_overview_embed(self.uid, interaction.user.display_name)
            view  = CollectionView(uid=self.uid, user_id=self.user_id, total=0)
            await interaction.response.edit_message(embed=embed, view=view)
            return

        self.page = min(self.page, self.total)
        self._rebuild()
        await interaction.response.edit_message(embed=await self.build_embed(), view=self)

    async def _back(self, interaction: discord.Interaction):
        embed = await build_overview_embed(self.uid, interaction.user.display_name)
        _, total = await get_collection(self.uid, page=1, per_page=1)
        view  = CollectionView(uid=self.uid, user_id=self.user_id, total=total)
        await interaction.response.edit_message(embed=embed, view=view)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your binder!", ephemeral=True)
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
#  Cog
# ─────────────────────────────────────────────────────────────────────────────

class CollectionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="collection", description="View your card collection")
    async def collection(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = str(interaction.user.id)
        await ensure_user(uid, str(interaction.user))
        _, total = await get_collection(uid, page=1, per_page=1)
        if total == 0:
            await interaction.followup.send(embed=discord.Embed(
                title="📦  Your Collection",
                description="You haven't opened any packs yet!\nUse `/store` to rip your first pack. 🎴",
                color=0xFFCC00,
            ))
            return
        embed = await build_overview_embed(uid, interaction.user.display_name)
        view  = CollectionView(uid=uid, user_id=interaction.user.id, total=total)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="stats", description="Your pack opening stats")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = str(interaction.user.id)
        await ensure_user(uid, str(interaction.user))
        user_stats  = await get_user_stats(uid)
        history     = await get_pack_history(uid, limit=10)
        total_cards = await get_collection_card_count(uid)
        unique      = await get_unique_card_count(uid)
        total_value = await get_collection_total_value(uid)
        packs       = user_stats["packs_opened"] if user_stats else 0
        embed = discord.Embed(title=f"📊  {interaction.user.display_name}'s Stats", color=0x7B68EE)
        embed.add_field(name="Packs Opened",   value=f"`{packs}`",               inline=True)
        embed.add_field(name="Total Cards",    value=f"`{total_cards}`",         inline=True)
        embed.add_field(name="Unique Cards",   value=f"`{unique}`",              inline=True)
        embed.add_field(name="💵 Total Value", value=f"**${total_value:,.2f}**", inline=False)
        if history:
            lines = "\n".join(f"`{r['packs']:>3}` packs  →  {r['set_name']}" for r in history)
            embed.add_field(name="Recent Sets", value=lines, inline=False)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CollectionCog(bot))
