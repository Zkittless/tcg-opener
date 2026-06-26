"""
cogs/collection.py

/collection  — overview with total value + filter button that opens a modal
/binder      — paginated card viewer with value, keep/discard toggle
/stats       — pack history

Filter modal lets you set a minimum $ value. Cards above it are marked Keep,
cards below are marked Discard. You can then view Keep or Discard piles
separately and toggle individual cards.
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
    set_card_keep,
    bulk_set_keep_by_value,
)
from core.pack_engine import rarity_tier

log = logging.getLogger("collection")


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def rarity_color(rarity: str) -> int:
    tier = rarity_tier(rarity)
    return {0: 0x9E9E9E, 1: 0x4CAF50, 2: 0x2196F3, 3: 0x9C27B0, 4: 0xFFD700}.get(tier, 0x9E9E9E)


def fmt_price(price) -> str:
    if price is None:
        return "`N/A`"
    return f"**${float(price):,.2f}**"


# ─────────────────────────────────────────────────────────────────────────────
#  Filter Modal
# ─────────────────────────────────────────────────────────────────────────────

class FilterModal(discord.ui.Modal, title="Set Collection Filter"):
    min_value = discord.ui.TextInput(
        label="Minimum value to KEEP (USD)",
        placeholder="e.g. 1.00  — cards below this go to Discard",
        required=True,
        max_length=10,
    )

    def __init__(self, uid: str, user_id: int):
        super().__init__()
        self.uid     = uid
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.min_value.value.strip().lstrip("$")
        try:
            threshold = float(raw)
            if threshold < 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter a valid dollar amount (e.g. `1.00`).", ephemeral=True
            )
            return

        await bulk_set_keep_by_value(self.uid, threshold)

        # Count results
        _, keep_total    = await get_collection(self.uid, keep=True,  page=1, per_page=1)
        _, discard_total = await get_collection(self.uid, keep=False, page=1, per_page=1)

        embed = discord.Embed(
            title="✅  Filter Applied",
            description=(
                f"Cards **≥ ${threshold:.2f}** → ✅ Keep  (`{keep_total}` cards)\n"
                f"Cards **< ${threshold:.2f}** → 🗑️ Discard  (`{discard_total}` cards)\n\n"
                "Use the buttons below to browse each pile, or flip individual cards."
            ),
            color=0x57F287,
        )

        view = CollectionView(uid=self.uid, user_id=self.user_id, mode="all")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


# ─────────────────────────────────────────────────────────────────────────────
#  Collection overview view (buttons for Keep / Discard / All / Filter)
# ─────────────────────────────────────────────────────────────────────────────

class CollectionView(discord.ui.View):
    def __init__(self, uid: str, user_id: int, mode: str = "all"):
        super().__init__(timeout=PACK_TIMEOUT)
        self.uid     = uid
        self.user_id = user_id
        self.mode    = mode  # "all" | "keep" | "discard"
        self._rebuild()

    def _rebuild(self):
        self.clear_items()

        styles = {
            "all":     discord.ButtonStyle.primary,
            "keep":    discord.ButtonStyle.success,
            "discard": discord.ButtonStyle.danger,
        }

        for label, mode in [("📦 All Cards", "all"), ("✅ Keep", "keep"), ("🗑️ Discard", "discard")]:
            btn = discord.ui.Button(
                label=label,
                style=styles[mode],
                disabled=(self.mode == mode),
                row=0,
            )
            btn.callback = self._make_mode_cb(mode)
            self.add_item(btn)

        filter_btn = discord.ui.Button(label="⚙️ Set Filter", style=discord.ButtonStyle.secondary, row=0)
        filter_btn.callback = self._open_filter
        self.add_item(filter_btn)

        browse_btn = discord.ui.Button(label="🔍 Browse Cards", style=discord.ButtonStyle.secondary, row=1)
        browse_btn.callback = self._browse
        self.add_item(browse_btn)

    def _make_mode_cb(self, mode: str):
        async def cb(interaction: discord.Interaction):
            self.mode = mode
            self._rebuild()
            embed = await build_collection_embed(self.uid, interaction.user.display_name, mode)
            await interaction.response.edit_message(embed=embed, view=self)
        return cb

    async def _open_filter(self, interaction: discord.Interaction):
        await interaction.response.send_modal(FilterModal(uid=self.uid, user_id=self.user_id))

    async def _browse(self, interaction: discord.Interaction):
        keep_filter = {"all": None, "keep": True, "discard": False}[self.mode]
        _, total = await get_collection(self.uid, keep=keep_filter, page=1, per_page=1)
        if total == 0:
            await interaction.response.send_message("No cards in this pile!", ephemeral=True)
            return
        view  = BinderView(uid=self.uid, user_id=self.user_id, keep_filter=keep_filter, total=total)
        embed = await view.build_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your collection!", ephemeral=True)
            return False
        return True


async def build_collection_embed(uid: str, display_name: str, mode: str = "all") -> discord.Embed:
    summary      = await get_collection_summary(uid)
    total_cards  = await get_collection_card_count(uid)
    unique       = await get_unique_card_count(uid)
    total_value  = await get_collection_total_value(uid)
    stats        = await get_user_stats(uid)
    packs        = stats["packs_opened"] if stats else 0

    _, keep_total    = await get_collection(uid, keep=True,  page=1, per_page=1)
    _, discard_total = await get_collection(uid, keep=False, page=1, per_page=1)

    mode_labels = {"all": "📦 Full Collection", "keep": "✅ Keep Pile", "discard": "🗑️ Discard Pile"}
    colors      = {"all": 0xFFCC00, "keep": 0x57F287, "discard": 0xED4245}

    embed = discord.Embed(
        title=f"{mode_labels[mode]} — {display_name}",
        color=colors[mode],
    )

    embed.add_field(name="Unique Cards",   value=f"`{unique}`",          inline=True)
    embed.add_field(name="Total Cards",    value=f"`{total_cards}`",     inline=True)
    embed.add_field(name="Packs Opened",   value=f"`{packs}`",           inline=True)
    embed.add_field(name="💵 Total Value", value=f"**${total_value:,.2f}**", inline=True)
    embed.add_field(name="✅ Keep",        value=f"`{keep_total}`",      inline=True)
    embed.add_field(name="🗑️ Discard",    value=f"`{discard_total}`",   inline=True)

    if summary:
        top = summary[:8]
        lines = "\n".join(
            f"**{r['set_name'] or r['set_id']}** — "
            f"`{r['unique_cards']}` cards  •  **${r['set_value'] or 0:,.2f}**"
            for r in top
        )
        embed.add_field(name="Sets (by value)", value=lines, inline=False)

    embed.set_footer(text="Use ⚙️ Set Filter to auto-sort by value  •  Browse Cards to flip through")
    return embed


# ─────────────────────────────────────────────────────────────────────────────
#  Binder — paginated card viewer with Keep/Discard toggle
# ─────────────────────────────────────────────────────────────────────────────

class BinderView(discord.ui.View):
    def __init__(
        self,
        uid:         str,
        user_id:     int,
        keep_filter: bool | None = None,
        total:       int = 0,
        set_id:      str | None = None,
        min_value:   float | None = None,
    ):
        super().__init__(timeout=PACK_TIMEOUT)
        self.uid         = uid
        self.user_id     = user_id
        self.keep_filter = keep_filter
        self.set_id      = set_id
        self.min_value   = min_value
        self.total       = total
        self.page        = 1
        self._rebuild()

    async def build_embed(self) -> discord.Embed:
        cards, _ = await get_collection(
            self.uid,
            set_id=self.set_id,
            min_value=self.min_value,
            keep=self.keep_filter,
            page=self.page,
            per_page=1,
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
        keep      = card.get("keep", 1)
        card_id   = card.get("card_id", "")

        color = rarity_color(rarity)
        embed = discord.Embed(title=name, color=color)

        if image_url:
            embed.set_image(url=image_url)

        embed.add_field(name="Rarity",         value=f"`{rarity}`",    inline=True)
        embed.add_field(name="Set",            value=f"`{set_name}`",  inline=True)
        embed.add_field(name="Owned",          value=f"`×{count}`",    inline=True)

        if price is not None:
            price_val = f"**${float(price):,.2f}**"
        else:
            safe_name = name.replace(" ", "+")
            tcg_url   = f"https://www.tcgplayer.com/search/pokemon/product?q={safe_name}&productLineName=pokemon"
            price_val = f"[Check TCGPlayer]({tcg_url})"
        embed.add_field(name="💵 Market Value", value=price_val,        inline=True)
        embed.add_field(name="Status",         value="✅ Keep" if keep else "🗑️ Discard", inline=True)

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

        keep_btn = discord.ui.Button(label="✅ Keep", style=discord.ButtonStyle.success, row=1)
        keep_btn.callback = self._mark_keep
        self.add_item(keep_btn)

        discard_btn = discord.ui.Button(label="🗑️ Discard", style=discord.ButtonStyle.danger, row=1)
        discard_btn.callback = self._mark_discard
        self.add_item(discard_btn)

        back_btn = discord.ui.Button(label="◀ Collection", style=discord.ButtonStyle.secondary, row=1)
        back_btn.callback = self._back_to_collection
        self.add_item(back_btn)

    async def _prev(self, interaction: discord.Interaction):
        self.page = max(1, self.page - 1)
        self._rebuild()
        await interaction.response.edit_message(embed=await self.build_embed(), view=self)

    async def _next(self, interaction: discord.Interaction):
        self.page = min(self.total, self.page + 1)
        self._rebuild()
        await interaction.response.edit_message(embed=await self.build_embed(), view=self)

    async def _mark_keep(self, interaction: discord.Interaction):
        await self._toggle(interaction, keep=True)

    async def _mark_discard(self, interaction: discord.Interaction):
        await self._toggle(interaction, keep=False)

    async def _toggle(self, interaction: discord.Interaction, keep: bool):
        # Fetch current card with NO filter so we always get it regardless of keep status
        cards, total_unfiltered = await get_collection(
            self.uid, set_id=self.set_id, min_value=self.min_value,
            keep=None, page=self.page, per_page=1
        )
        if cards:
            card_id = cards[0]["card_id"]
            await set_card_keep(self.uid, card_id, keep)

        # Recalculate total for this view's filter mode
        _, self.total = await get_collection(
            self.uid, set_id=self.set_id, min_value=self.min_value,
            keep=self.keep_filter, page=1, per_page=1
        )
        if self.total == 0:
            self.total = 1  # avoid div-by-zero
        self.page = min(self.page, self.total)
        self._rebuild()
        await interaction.response.edit_message(embed=await self.build_embed(), view=self)

    async def _back_to_collection(self, interaction: discord.Interaction):
        view  = CollectionView(uid=self.uid, user_id=self.user_id)
        embed = await build_collection_embed(self.uid, interaction.user.display_name)
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

    @app_commands.command(name="collection", description="View your card collection, values, and keep/discard filter")
    async def collection(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = str(interaction.user.id)
        await ensure_user(uid, str(interaction.user))

        summary = await get_collection_summary(uid)
        if not summary:
            embed = discord.Embed(
                title="📦  Your Collection",
                description="You haven't opened any packs yet!\nUse `/store` to rip your first pack. 🎴",
                color=0xFFCC00,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = await build_collection_embed(uid, interaction.user.display_name)
        view  = CollectionView(uid=uid, user_id=interaction.user.id)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="binder", description="Flip through your collected cards")
    @app_commands.describe(set_filter="Filter by set ID (e.g. sv8pt5)", min_value="Only show cards worth at least this $ amount")
    async def binder(self, interaction: discord.Interaction, set_filter: str | None = None, min_value: float | None = None):
        await interaction.response.defer()
        uid = str(interaction.user.id)
        await ensure_user(uid, str(interaction.user))

        set_id = set_filter.lower().strip() if set_filter else None
        _, total = await get_collection(uid, set_id=set_id, min_value=min_value, page=1, per_page=1)

        if total == 0:
            await interaction.followup.send("No cards found with those filters.", ephemeral=True)
            return

        view  = BinderView(uid=uid, user_id=interaction.user.id, set_id=set_id, min_value=min_value, total=total)
        embed = await view.build_embed()
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
        embed.add_field(name="Packs Opened",   value=f"`{packs}`",              inline=True)
        embed.add_field(name="Total Cards",    value=f"`{total_cards}`",        inline=True)
        embed.add_field(name="Unique Cards",   value=f"`{unique}`",             inline=True)
        embed.add_field(name="💵 Total Value", value=f"**${total_value:,.2f}**", inline=False)

        if history:
            lines = "\n".join(f"`{r['packs']:>3}` packs  →  {r['set_name']}" for r in history)
            embed.add_field(name="Recent Sets", value=lines, inline=False)

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CollectionCog(bot))
