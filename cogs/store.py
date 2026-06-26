"""
cogs/store.py

/store command — fully redesigned UI.

Flow:
  1. Era selector  — one button per era, clean row layout
  2. Set browser   — paginated, PACK ART as the main image, proper set name
  3. Pack picker   — flip between pack art variants, see pack value estimate
  4. Rip → PackOpenerView
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging

from config import SETS_PER_PAGE, STORE_TIMEOUT
from core.set_data import (
    sets_by_era, SetMeta, get_meta,
    ERA_ORDER, ERA_COLORS, ERA_EMOJIS,
)
from core.tcg_api import fetch_all_sets, get_set_logo

log = logging.getLogger("store")


def era_color(era: str) -> int:
    return ERA_COLORS.get(era, 0xFFCC00)


def era_emoji(era: str) -> str:
    return ERA_EMOJIS.get(era, "🎴")


# ─────────────────────────────────────────────────────────────────────────────
#  Era selector
# ─────────────────────────────────────────────────────────────────────────────

def build_era_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🏪  Pokémon TCG Pack Store",
        description=(
            "Choose an era below to browse packs.\n"
            "Every pack is free — rip as many as you want! 🎉"
        ),
        color=0xFFCC00,
    )
    embed.set_footer(text="Pokémon TCG Bot  •  /collection to see your binder")
    return embed


class EraButton(discord.ui.Button):
    def __init__(self, era: str, api_sets: dict, row: int):
        super().__init__(
            label=era,
            emoji=ERA_EMOJIS.get(era, "🎴"),
            style=discord.ButtonStyle.primary,
            row=row,
        )
        self.era      = era
        self.api_sets = api_sets

    async def callback(self, interaction: discord.Interaction):
        view  = SetBrowserView(era=self.era, api_sets=self.api_sets, user_id=interaction.user.id)
        embed = view.build_embed()
        await interaction.response.edit_message(embed=embed, view=view)


class EraSelectorView(discord.ui.View):
    def __init__(self, api_sets: dict, user_id: int):
        super().__init__(timeout=STORE_TIMEOUT)
        self.user_id = user_id
        era_map      = sets_by_era()
        available    = [e for e in ERA_ORDER if e in era_map]
        for i, era in enumerate(available):
            self.add_item(EraButton(era, api_sets, row=i // 4))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Open your own store with `/store`!", ephemeral=True)
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
#  Set browser  — shows pack art as embed image
# ─────────────────────────────────────────────────────────────────────────────

class SetBrowserView(discord.ui.View):
    def __init__(self, era: str, api_sets: dict, user_id: int):
        super().__init__(timeout=STORE_TIMEOUT)
        self.era      = era
        self.api_sets = api_sets
        self.user_id  = user_id
        self.page     = 0

        era_map          = sets_by_era()
        self.sets_meta   = era_map.get(era, [])
        self.total_pages = max(1, -(-len(self.sets_meta) // SETS_PER_PAGE))
        self._rebuild()

    def current_sets(self) -> list[SetMeta]:
        s = self.page * SETS_PER_PAGE
        return self.sets_meta[s: s + SETS_PER_PAGE]

    def build_embed(self) -> discord.Embed:
        emoji = era_emoji(self.era)
        color = era_color(self.era)
        page_sets = self.current_sets()

        embed = discord.Embed(
            title=f"{emoji}  {self.era}",
            description=f"Page {self.page + 1} of {self.total_pages} — tap a set to choose your pack.",
            color=color,
        )

        for meta in page_sets:
            api      = self.api_sets.get(meta.set_id, {})
            name     = api.get("name", meta.set_id)
            release  = api.get("releaseDate", "?")
            total    = api.get("total", "?")
            n_arts   = len(meta.pack_arts)
            embed.add_field(
                name=f"**{name}**",
                value=f"📅 {release}  •  🃏 {total} cards  •  🎨 {n_arts} pack art{'s' if n_arts != 1 else ''}",
                inline=False,
            )

        # Show logo of first set on this page — comes from pokemontcg.io, always embeds
        first = page_sets[0] if page_sets else None
        if first:
            api_first = self.api_sets.get(first.set_id, {})
            logo = get_set_logo(api_first)
            if logo:
                embed.set_image(url=logo)

        embed.set_footer(text=f"{emoji} {self.era}  •  Page {self.page + 1}/{self.total_pages}")
        return embed

    def _rebuild(self):
        self.clear_items()
        page_sets = self.current_sets()

        # Set selection buttons
        for i, meta in enumerate(page_sets):
            api  = self.api_sets.get(meta.set_id, {})
            name = api.get("name", meta.set_id)
            btn  = SetSelectButton(label=name, meta=meta, api_sets=self.api_sets, user_id=self.user_id)
            btn.row = i // 2
            self.add_item(btn)

        # Nav row
        back = discord.ui.Button(label="◀ Eras", style=discord.ButtonStyle.secondary, row=3)
        back.callback = self._back
        self.add_item(back)

        if self.page > 0:
            prev = discord.ui.Button(label="◀ Prev", style=discord.ButtonStyle.secondary, row=3)
            prev.callback = self._prev
            self.add_item(prev)

        ind = discord.ui.Button(
            label=f"{self.page + 1}/{self.total_pages}",
            style=discord.ButtonStyle.secondary, disabled=True, row=3,
        )
        self.add_item(ind)

        if self.page < self.total_pages - 1:
            nxt = discord.ui.Button(label="Next ▶", style=discord.ButtonStyle.secondary, row=3)
            nxt.callback = self._next
            self.add_item(nxt)

    async def _back(self, interaction: discord.Interaction):
        view  = EraSelectorView(api_sets=self.api_sets, user_id=self.user_id)
        embed = build_era_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    async def _prev(self, interaction: discord.Interaction):
        self.page -= 1
        self._rebuild()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def _next(self, interaction: discord.Interaction):
        self.page += 1
        self._rebuild()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Open your own store with `/store`!", ephemeral=True)
            return False
        return True


class SetSelectButton(discord.ui.Button):
    def __init__(self, label: str, meta: SetMeta, api_sets: dict, user_id: int):
        super().__init__(label=label[:80], style=discord.ButtonStyle.success)
        self.meta     = meta
        self.api_sets = api_sets
        self.user_id  = user_id

    async def callback(self, interaction: discord.Interaction):
        api   = self.api_sets.get(self.meta.set_id, {})
        view  = PackPickerView(meta=self.meta, api_sets=self.api_sets, user_id=self.user_id)
        embed = view.build_embed()
        await interaction.response.edit_message(embed=embed, view=view)


# ─────────────────────────────────────────────────────────────────────────────
#  Pack picker  — big pack art image, flip between variants, show pack value
# ─────────────────────────────────────────────────────────────────────────────

class PackPickerView(discord.ui.View):
    def __init__(self, meta: SetMeta, api_sets: dict, user_id: int):
        super().__init__(timeout=STORE_TIMEOUT)
        self.meta      = meta
        self.api_sets  = api_sets
        self.user_id   = user_id
        self.art_index = 0
        self._rebuild()

    def build_embed(self) -> discord.Embed:
        api     = self.api_sets.get(self.meta.set_id, {})
        name    = api.get("name", self.meta.set_id)
        release = api.get("releaseDate", "?")
        total   = api.get("total", "?")
        color   = era_color(self.meta.era)
        emoji   = era_emoji(self.meta.era)
        logo    = get_set_logo(api)

        embed = discord.Embed(
            title=f"🎴  {name}",
            description=(
                f"{emoji} **{self.meta.era}**\n"
                f"📅 Released: {release}\n"
                f"🃏 {total} cards  •  {self.meta.pack_size} cards/pack"
            ),
            color=color,
        )

        if logo:
            embed.set_image(url=logo)

        embed.set_footer(text="Hit Rip Pack! to open")
        return embed

    def _rebuild(self):
        self.clear_items()

        rip = discord.ui.Button(label="🎴  Rip Pack!", style=discord.ButtonStyle.danger, row=0)
        rip.callback = self._rip
        self.add_item(rip)

        back = discord.ui.Button(label="◀ Back to Sets", style=discord.ButtonStyle.secondary, row=0)
        back.callback = self._back
        self.add_item(back)

    async def _prev_art(self, interaction: discord.Interaction):
        self.art_index -= 1
        self._rebuild()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def _next_art(self, interaction: discord.Interaction):
        self.art_index += 1
        self._rebuild()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def _back(self, interaction: discord.Interaction):
        view  = SetBrowserView(era=self.meta.era, api_sets=self.api_sets, user_id=self.user_id)
        embed = view.build_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    async def _rip(self, interaction: discord.Interaction):
        from cogs.pack_opener import PackOpenerView, build_loading_embed
        api = self.api_sets.get(self.meta.set_id, {})
        await interaction.response.edit_message(embed=build_loading_embed(self.meta, api), view=None)
        view  = await PackOpenerView.create(meta=self.meta, api_set=api, api_sets=self.api_sets, user=interaction.user)
        await interaction.edit_original_response(embed=view.current_embed(), view=view)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Open your own store with `/store`!", ephemeral=True)
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
#  Cog
# ─────────────────────────────────────────────────────────────────────────────

class StoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="store", description="Browse Pokémon TCG sets and rip packs!")
    async def store(self, interaction: discord.Interaction):
        await interaction.response.defer()
        all_sets_list = await fetch_all_sets()
        api_sets      = {s["id"]: s for s in all_sets_list}
        view  = EraSelectorView(api_sets=api_sets, user_id=interaction.user.id)
        embed = build_era_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(StoreCog(bot))
