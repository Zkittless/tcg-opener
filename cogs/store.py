"""
cogs/store.py

The /store command.  Flow:
  1. Era selector  — buttons for each era
  2. Set browser   — paginated embeds of sets in that era (logo + name)
  3. Pack picker   — choose which pack art variant to rip
  4. Hand off to PackOpenerView in cogs/pack_opener.py
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional

from config import ERA_COLORS, ERA_EMOJIS, ERA_ORDER, SETS_PER_PAGE, STORE_TIMEOUT
from core.set_data import sets_by_era, SetMeta, get_meta
from core.tcg_api import fetch_all_sets, fetch_set, get_set_logo

log = logging.getLogger("store")


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def era_color(era: str) -> int:
    return ERA_COLORS.get(era, 0xFFCC00)


def era_emoji(era: str) -> str:
    return ERA_EMOJIS.get(era, "🎴")


def build_era_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🏪  Pokémon TCG Store",
        description=(
            "Welcome to the Pokémon card shop!\n"
            "Choose an **era** below to browse available sets.\n"
            "Every pack is free — rip as many as you want. 🎉"
        ),
        color=0xFFCC00,
    )
    embed.set_footer(text="Pokémon TCG Bot • /collection to view your cards")
    return embed


def build_set_embed(
    era: str,
    sets_meta: list[SetMeta],
    api_sets: dict[str, dict],
    page: int,
    total_pages: int,
) -> discord.Embed:
    color = era_color(era)
    emoji = era_emoji(era)
    embed = discord.Embed(
        title=f"{emoji}  {era} Sets",
        description=f"Page {page}/{total_pages} — Pick a set to browse its packs.",
        color=color,
    )

    for meta in sets_meta:
        api = api_sets.get(meta.set_id, {})
        name    = api.get("name", meta.set_id)
        release = api.get("releaseDate", "?")
        total   = api.get("total", "?")
        series  = api.get("series", era)
        n_arts  = len(meta.pack_arts)

        embed.add_field(
            name=f"**{name}**",
            value=(
                f"Released: `{release}`\n"
                f"Cards: `{total}`\n"
                f"Pack variants: `{n_arts}`"
            ),
            inline=True,
        )

    # Show logo of first set on page as thumbnail
    first_meta = sets_meta[0] if sets_meta else None
    if first_meta:
        api = api_sets.get(first_meta.set_id, {})
        logo = get_set_logo(api)
        if logo:
            embed.set_thumbnail(url=logo)

    embed.set_footer(text=f"{emoji} {era}  •  Page {page}/{total_pages}")
    return embed


def build_pack_embed(
    meta: SetMeta,
    api_set: dict,
    art_index: int,
) -> discord.Embed:
    name    = api_set.get("name", meta.set_id)
    release = api_set.get("releaseDate", "?")
    total   = api_set.get("total", "?")
    era     = meta.era
    color   = era_color(era)
    emoji   = era_emoji(era)
    n_arts  = len(meta.pack_arts)

    embed = discord.Embed(
        title=f"🎴  {name}",
        description=(
            f"**Era:** {emoji} {era}\n"
            f"**Released:** {release}\n"
            f"**Set size:** {total} cards\n"
            f"**Pack size:** {meta.pack_size} cards\n\n"
            f"Pack art **{art_index + 1} of {n_arts}** — hit **Rip Pack!** to open this one."
        ),
        color=color,
    )

    art_url = meta.pack_arts[art_index] if meta.pack_arts else ""
    if art_url:
        embed.set_image(url=art_url)

    logo = get_set_logo(api_set)
    if logo:
        embed.set_thumbnail(url=logo)

    embed.set_footer(text="Use ◀ ▶ to flip between pack art variants")
    return embed


# ─────────────────────────────────────────────────────────────────────────────
#  Era Selector View
# ─────────────────────────────────────────────────────────────────────────────

class EraButton(discord.ui.Button):
    def __init__(self, era: str, api_sets: dict[str, dict]):
        emoji = ERA_EMOJIS.get(era, "🎴")
        super().__init__(
            label=era,
            emoji=emoji,
            style=discord.ButtonStyle.primary,
            custom_id=f"era_{era}",
        )
        self.era      = era
        self.api_sets = api_sets

    async def callback(self, interaction: discord.Interaction):
        view = SetBrowserView(
            era=self.era,
            api_sets=self.api_sets,
            user_id=interaction.user.id,
        )
        embed = view.build_embed()
        await interaction.response.edit_message(embed=embed, view=view)


class EraSelectorView(discord.ui.View):
    def __init__(self, api_sets: dict[str, dict], user_id: int):
        super().__init__(timeout=STORE_TIMEOUT)
        self.user_id  = user_id
        self.api_sets = api_sets

        era_map = sets_by_era()
        available_eras = [e for e in ERA_ORDER if e in era_map]

        # Row them in groups of 4
        for i, era in enumerate(available_eras):
            btn = EraButton(era, api_sets)
            btn.row = i // 4
            self.add_item(btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Open your own store with `/store`!", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


# ─────────────────────────────────────────────────────────────────────────────
#  Set Browser View  (paginated list of sets in one era)
# ─────────────────────────────────────────────────────────────────────────────

class SetBrowserView(discord.ui.View):
    def __init__(self, era: str, api_sets: dict[str, dict], user_id: int):
        super().__init__(timeout=STORE_TIMEOUT)
        self.era      = era
        self.api_sets = api_sets
        self.user_id  = user_id
        self.page     = 0

        era_map = sets_by_era()
        self.sets_meta = era_map.get(era, [])
        self.total_pages = max(1, -(-len(self.sets_meta) // SETS_PER_PAGE))  # ceil div

        self._rebuild_buttons()

    def current_page_sets(self) -> list[SetMeta]:
        start = self.page * SETS_PER_PAGE
        return self.sets_meta[start : start + SETS_PER_PAGE]

    def build_embed(self) -> discord.Embed:
        return build_set_embed(
            era        = self.era,
            sets_meta  = self.current_page_sets(),
            api_sets   = self.api_sets,
            page       = self.page + 1,
            total_pages= self.total_pages,
        )

    def _rebuild_buttons(self):
        self.clear_items()

        # Set selection buttons (row 0-1)
        for i, meta in enumerate(self.current_page_sets()):
            api  = self.api_sets.get(meta.set_id, {})
            name = api.get("name", meta.set_id)
            btn  = SetSelectButton(label=name, meta=meta, api_sets=self.api_sets, user_id=self.user_id)
            btn.row = i // 2
            self.add_item(btn)

        # Navigation row (row 3)
        back_era = discord.ui.Button(
            label="◀ Back to Eras", style=discord.ButtonStyle.secondary, row=3
        )
        back_era.callback = self._back_to_eras
        self.add_item(back_era)

        if self.page > 0:
            prev = discord.ui.Button(label="◀ Prev", style=discord.ButtonStyle.secondary, row=3)
            prev.callback = self._prev_page
            self.add_item(prev)

        if self.page < self.total_pages - 1:
            nxt = discord.ui.Button(label="Next ▶", style=discord.ButtonStyle.secondary, row=3)
            nxt.callback = self._next_page
            self.add_item(nxt)

        page_indicator = discord.ui.Button(
            label=f"Page {self.page + 1}/{self.total_pages}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
            row=3,
        )
        self.add_item(page_indicator)

    async def _back_to_eras(self, interaction: discord.Interaction):
        view  = EraSelectorView(api_sets=self.api_sets, user_id=self.user_id)
        embed = build_era_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    async def _prev_page(self, interaction: discord.Interaction):
        self.page -= 1
        self._rebuild_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def _next_page(self, interaction: discord.Interaction):
        self.page += 1
        self._rebuild_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Open your own store with `/store`!", ephemeral=True
            )
            return False
        return True


class SetSelectButton(discord.ui.Button):
    def __init__(self, label: str, meta: SetMeta, api_sets: dict[str, dict], user_id: int):
        super().__init__(
            label=label[:80],
            style=discord.ButtonStyle.success,
        )
        self.meta     = meta
        self.api_sets = api_sets
        self.user_id  = user_id

    async def callback(self, interaction: discord.Interaction):
        view = PackPickerView(
            meta      = self.meta,
            api_sets  = self.api_sets,
            user_id   = self.user_id,
        )
        api   = self.api_sets.get(self.meta.set_id, {})
        embed = build_pack_embed(self.meta, api, 0)
        await interaction.response.edit_message(embed=embed, view=view)


# ─────────────────────────────────────────────────────────────────────────────
#  Pack Picker View  (choose which pack art variant to rip)
# ─────────────────────────────────────────────────────────────────────────────

class PackPickerView(discord.ui.View):
    def __init__(self, meta: SetMeta, api_sets: dict[str, dict], user_id: int):
        super().__init__(timeout=STORE_TIMEOUT)
        self.meta      = meta
        self.api_sets  = api_sets
        self.user_id   = user_id
        self.art_index = 0

        self._rebuild()

    def _rebuild(self):
        self.clear_items()
        n = len(self.meta.pack_arts)

        # Prev art button
        prev = discord.ui.Button(
            label="◀ Pack Art",
            style=discord.ButtonStyle.secondary,
            disabled=self.art_index == 0,
            row=0,
        )
        prev.callback = self._prev_art
        self.add_item(prev)

        # Art indicator
        ind = discord.ui.Button(
            label=f"{self.art_index + 1} / {n}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
            row=0,
        )
        self.add_item(ind)

        # Next art button
        nxt = discord.ui.Button(
            label="Pack Art ▶",
            style=discord.ButtonStyle.secondary,
            disabled=self.art_index >= n - 1,
            row=0,
        )
        nxt.callback = self._next_art
        self.add_item(nxt)

        # Rip Pack button
        rip = discord.ui.Button(
            label="🎴  Rip Pack!",
            style=discord.ButtonStyle.danger,
            row=1,
        )
        rip.callback = self._rip_pack
        self.add_item(rip)

        # Back button
        back = discord.ui.Button(
            label="◀ Back to Sets",
            style=discord.ButtonStyle.secondary,
            row=1,
        )
        back.callback = self._back_to_sets
        self.add_item(back)

    async def _prev_art(self, interaction: discord.Interaction):
        self.art_index -= 1
        self._rebuild()
        api   = self.api_sets.get(self.meta.set_id, {})
        embed = build_pack_embed(self.meta, api, self.art_index)
        await interaction.response.edit_message(embed=embed, view=self)

    async def _next_art(self, interaction: discord.Interaction):
        self.art_index += 1
        self._rebuild()
        api   = self.api_sets.get(self.meta.set_id, {})
        embed = build_pack_embed(self.meta, api, self.art_index)
        await interaction.response.edit_message(embed=embed, view=self)

    async def _back_to_sets(self, interaction: discord.Interaction):
        view  = SetBrowserView(era=self.meta.era, api_sets=self.api_sets, user_id=self.user_id)
        embed = view.build_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    async def _rip_pack(self, interaction: discord.Interaction):
        from cogs.pack_opener import PackOpenerView, build_loading_embed

        await interaction.response.edit_message(
            embed=build_loading_embed(self.meta, self.api_sets.get(self.meta.set_id, {})),
            view=None,
        )

        view = await PackOpenerView.create(
            meta      = self.meta,
            api_set   = self.api_sets.get(self.meta.set_id, {}),
            api_sets  = self.api_sets,
            user      = interaction.user,
        )

        embed = view.current_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Open your own store with `/store`!", ephemeral=True
            )
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
#  Cog
# ─────────────────────────────────────────────────────────────────────────────

class StoreCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="store", description="Browse Pokémon TCG sets and rip packs!")
    async def store(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False, thinking=True)

        # Fetch all sets from the API once
        all_sets_list = await fetch_all_sets()
        api_sets: dict[str, dict] = {s["id"]: s for s in all_sets_list}

        view  = EraSelectorView(api_sets=api_sets, user_id=interaction.user.id)
        embed = build_era_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(StoreCog(bot))
