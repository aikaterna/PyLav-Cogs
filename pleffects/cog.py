from __future__ import annotations

from pathlib import Path

import discord
from discord import app_commands
from discord.app_commands import Range
from red_commons.logging import getLogger
from redbot.core import Config, commands
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.utils.chat_formatting import box
from tabulate import tabulate

import pylavcogs_shared
from pylav.filters import Equalizer
from pylav.types import BotT, InteractionT
from pylav.utils import PyLavContext
from pylav.utils.theme import EightBitANSI
from pylavcogs_shared.utils.decorators import invoker_is_dj, requires_player

LOGGER = getLogger("red.3pt.PyLavEffects")

_ = Translator("PyLavEffects", Path(__file__))


@cog_i18n(_)
class PyLavEffects(commands.Cog):
    """Apply filters and effects to the PyLav player"""

    __version__ = "0.0.1.0a"

    slash_fx = app_commands.Group(name="fx", description="Apply or remove bundled filters")

    def __init__(self, bot: BotT, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self._config = Config.get_conf(self, identifier=208903205982044161)
        self._config.register_global(enable_slash=True)
        self._config.register_guild(persist_fx=False)

    @commands.group(name="fxset")
    @commands.guild_only()
    @commands.guildowner_or_permissions(manage_guild=True)
    async def command_fxset(self, ctx: PyLavContext) -> None:
        """Configure the Player behaviour when an effect is set"""

    @command_fxset.command(name="version")
    async def command_fxset_version(self, context: PyLavContext) -> None:
        """Show the version of the Cog and its PyLav dependencies"""
        if isinstance(context, discord.Interaction):
            context = await self.bot.get_context(context)
        if context.interaction and not context.interaction.response.is_done():
            await context.defer(ephemeral=True)
        data = [
            (EightBitANSI.paint_white(self.__class__.__name__), EightBitANSI.paint_blue(self.__version__)),
            (EightBitANSI.paint_white("PyLavCogs-Shared"), EightBitANSI.paint_blue(pylavcogs_shared.__VERSION__)),
            (EightBitANSI.paint_white("PyLav"), EightBitANSI.paint_blue(context.lavalink.lib_version)),
        ]

        await context.send(
            embed=await context.lavalink.construct_embed(
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Library/Cog"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Version"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
                messageable=context,
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="nightcore", description=_("Apply a Nightcore preset to the player"))
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_nightcore(self, interaction: InteractionT) -> None:
        """Apply a Nightcore filter to the player"""

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)

        if context.player.equalizer.name == "Nightcore":
            await context.player.remove_nightcore(requester=context.author)
            await context.send(
                embed=await self.lavalink.construct_embed(
                    messageable=context,
                    description=_("Nightcore effect has been disabled"),
                ),
                ephemeral=True,
            )
        else:
            await context.player.apply_nightcore(requester=context.author)
            await context.send(
                embed=await self.lavalink.construct_embed(
                    messageable=context,
                    description=_("Nightcore effect has been enabled"),
                ),
                ephemeral=True,
            )

    @slash_fx.command(name="vibrato", description=_("Apply a vibrato filter to the player"))
    @app_commands.describe(
        frequency=_("The vibrato frequency"),
        depth=_("The vibrato depth value"),
        reset=_("Reset any existing effects currently applied to the player"),
    )
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_vibrato(
        self,
        interaction: InteractionT,
        frequency: Range[float, 0.01, 14.0] = None,
        depth: Range[float, 0.01, 1.0] = None,
        reset: bool = False,
    ) -> None:
        """Apply a vibrato filter to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)
        context.player.vibrato.frequency = frequency or context.player.vibrato.frequency
        context.player.vibrato.depth = depth or context.player.vibrato.depth
        await context.player.set_vibrato(vibrato=context.player.vibrato, requester=context.author, forced=reset)
        default = _("Not changed")

        data = [
            (
                EightBitANSI.paint_white(_("Frequency")),
                EightBitANSI.paint_blue(context.player.vibrato.frequency or default),
            ),
            (EightBitANSI.paint_white(_("Depth")), EightBitANSI.paint_blue(context.player.vibrato.depth or default)),
            (
                EightBitANSI.paint_white(_("Reset previous filters")),
                EightBitANSI.paint_red(_("Yes")) if reset else EightBitANSI.paint_green(_("No")),
            ),
        ]
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context,
                title=_("New vibrato effect applied to the player"),
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Setting"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Value"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="tremolo", description=_("Apply a tremolo filter to the player"))
    @app_commands.describe(
        frequency=_("The tremolo frequency"),
        depth=_("The tremolo depth value"),
        reset=_("Reset any existing effects currently applied to the player"),
    )
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_tremolo(
        self,
        interaction: InteractionT,
        frequency: Range[float, 0.01, None] = None,
        depth: Range[float, 0.01, 1.0] = None,
        reset: bool = False,
    ) -> None:
        """Apply a tremolo filter to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)
        context.player.tremolo.frequency = frequency or context.player.tremolo.frequency
        context.player.tremolo.depth = depth or context.player.tremolo.depth
        await context.player.set_tremolo(tremolo=context.player.tremolo, requester=context.author, forced=reset)
        default = _("Not changed")

        data = [
            (
                EightBitANSI.paint_white(_("Frequency")),
                EightBitANSI.paint_blue(context.player.tremolo.frequency or default),
            ),
            (EightBitANSI.paint_white(_("Depth")), EightBitANSI.paint_blue(context.player.tremolo.depth or default)),
            (
                EightBitANSI.paint_white(_("Reset previous filters")),
                EightBitANSI.paint_red(_("Yes")) if reset else EightBitANSI.paint_green(_("No")),
            ),
        ]
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context,
                title=_("New tremolo effect applied to the player"),
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Setting"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Value"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="timescale", description=_("Apply a timescale filter to the player"))
    @app_commands.describe(
        speed=_("The timescale speed value"),
        pitch=_("The timescale pitch value"),
        rate=_("The timescale rate value"),
        reset=_("Reset any existing effects currently applied to the player"),
    )
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_timescale(
        self,
        interaction: InteractionT,
        speed: Range[float, 0.0, None] = None,
        pitch: Range[float, 0.0, None] = None,
        rate: Range[float, 0.0, None] = None,
        reset: bool = False,
    ) -> None:
        """Apply a timescale filter to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)
        context.player.timescale.speed = speed or context.player.timescale.speed
        context.player.timescale.pitch = pitch or context.player.timescale.pitch
        context.player.timescale.rate = rate or context.player.timescale.rate
        await context.player.set_timescale(timescale=context.player.timescale, requester=context.author, forced=reset)
        default = _("Not changed")
        data = [
            (EightBitANSI.paint_white(_("Speed")), EightBitANSI.paint_blue(context.player.timescale.speed or default)),
            (EightBitANSI.paint_white(_("Pitch")), EightBitANSI.paint_blue(context.player.timescale.pitch or default)),
            (EightBitANSI.paint_white(_("Rate")), EightBitANSI.paint_blue(context.player.timescale.rate or default)),
            (
                EightBitANSI.paint_white(_("Reset previous filters")),
                EightBitANSI.paint_red(_("Yes")) if reset else EightBitANSI.paint_green(_("No")),
            ),
        ]
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context,
                title=_("New timescale effect applied to the player"),
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Setting"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Value"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="rotation", description=_("Apply a rotation filter to the player"))
    @app_commands.describe(
        hertz=_("The rotation hertz frequency"), reset=_("Reset any existing effects currently applied to the player")
    )
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_rotation(
        self, interaction: InteractionT, hertz: Range[float, 0.0, None] = None, reset: bool = False
    ) -> None:
        """Apply a rotation filter to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)
        context.player.rotation.hertz = hertz or context.player.rotation.hertz
        await context.player.set_rotation(rotation=context.player.rotation, requester=context.author, forced=reset)
        default = _("Not changed")

        data = [
            (
                EightBitANSI.paint_white(_("Frequency hertz")),
                EightBitANSI.paint_blue(context.player.rotation.hertz or default),
            ),
            (
                EightBitANSI.paint_white(_("Reset previous filters")),
                EightBitANSI.paint_red(_("Yes")) if reset else EightBitANSI.paint_green(_("No")),
            ),
        ]
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context,
                title=_("New rotation effect applied to the player"),
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Setting"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Value"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="lowpass", description=_("Apply a low pass filter to the player"))
    @app_commands.describe(
        smoothing=_("The low pass smoothing value"),
        reset=_("Reset any existing effects currently applied to the player"),
    )
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_lowpass(
        self, interaction: InteractionT, smoothing: Range[float, 0.0, None] = None, reset: bool = False
    ) -> None:
        """Apply a low pass filter to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)
        context.player.low_pass.smoothing = smoothing or context.player.low_pass.smoothing
        await context.player.set_low_pass(low_pass=context.player.low_pass, requester=context.author, forced=reset)
        default = _("Not changed")

        data = [
            (
                EightBitANSI.paint_white(_("Smoothing factor")),
                EightBitANSI.paint_blue(context.player.low_pass.smoothing or default),
            ),
            (
                EightBitANSI.paint_white(_("Reset previous filters")),
                EightBitANSI.paint_red(_("Yes")) if reset else EightBitANSI.paint_green(_("No")),
            ),
        ]
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context,
                title=_("New low pass effect applied to the player"),
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Setting"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Value"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="karaoke", description=_("Apply a karaoke filter to the player"))
    @app_commands.describe(
        level=_("The level value"),
        mono_level=_("The mono level value"),
        filter_band=_("The filter band"),
        filter_width=_("The filter width value"),
        reset=_("Reset any existing effects currently applied to the player"),
    )
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_karaoke(
        self,
        interaction: InteractionT,
        level: Range[float, 0.0, None] = None,
        mono_level: Range[float, 0.0, None] = None,
        filter_band: Range[float, 0.0, None] = None,
        filter_width: Range[float, 0.0, None] = None,
        reset: bool = False,
    ) -> None:
        """Apply a karaoke filter to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)
        context.player.karaoke.level = level or context.player.karaoke.level
        context.player.karaoke.mono_level = mono_level or context.player.karaoke.mono_level
        context.player.karaoke.filter_band = filter_band or context.player.karaoke.filter_band
        context.player.karaoke.filter_width = filter_width or context.player.karaoke.filter_width
        await context.player.set_karaoke(karaoke=context.player.karaoke, requester=context.author, forced=reset)
        default = _("Not changed")
        data = [
            (EightBitANSI.paint_white(_("Level")), EightBitANSI.paint_blue(context.player.karaoke.level or default)),
            (
                EightBitANSI.paint_white(_("Mono Level")),
                EightBitANSI.paint_blue(context.player.karaoke.mono_level or default),
            ),
            (
                EightBitANSI.paint_white(_("Filter Band")),
                EightBitANSI.paint_blue(context.player.karaoke.filter_band or default),
            ),
            (
                EightBitANSI.paint_white(_("Filter Width")),
                EightBitANSI.paint_blue(context.player.karaoke.filter_width or default),
            ),
            (
                EightBitANSI.paint_white(_("Reset previous filters")),
                EightBitANSI.paint_red(_("Yes")) if reset else EightBitANSI.paint_green(_("No")),
            ),
        ]
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context,
                title=_("New karaoke effect applied to the player"),
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Setting"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Value"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="channelmix", description=_("Apply a channel mix filter to the player"))
    @app_commands.describe(
        left_to_left=_("The channel mix left to left weight"),
        left_to_right=_("The channel mix left to right weight"),
        right_to_left=_("The channel mix right to left weight"),
        right_to_right=_("The channel mix right to right weight"),
        reset=_("Reset any existing effects currently applied to the player"),
    )
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_channelmix(
        self,
        interaction: InteractionT,
        left_to_left: Range[float, 0.0, None] = None,
        left_to_right: Range[float, 0.0, None] = None,
        right_to_left: Range[float, 0.0, None] = None,
        right_to_right: Range[float, 0.0, None] = None,
        reset: bool = False,
    ) -> None:
        """Apply a channel mix filter to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)
        context.player.channel_mix.left_to_left = left_to_left or context.player.channel_mix.left_to_left
        context.player.channel_mix.left_to_right = left_to_right or context.player.channel_mix.left_to_right
        context.player.channel_mix.right_to_left = right_to_left or context.player.channel_mix.right_to_left
        context.player.channel_mix.right_to_right = right_to_right or context.player.channel_mix.right_to_right
        await context.player.set_channel_mix(
            channel_mix=context.player.channel_mix, requester=context.author, forced=reset
        )
        default = _("Not changed")

        data = [
            (
                EightBitANSI.paint_white(_("Left to Left")),
                EightBitANSI.paint_blue(context.player.channel_mix.left_to_left or default),
            ),
            (
                EightBitANSI.paint_white(_("Left to Right")),
                EightBitANSI.paint_blue(context.player.channel_mix.left_to_right or default),
            ),
            (
                EightBitANSI.paint_white(_("Right to Left")),
                EightBitANSI.paint_blue(context.player.channel_mix.right_to_left or default),
            ),
            (
                EightBitANSI.paint_white(_("Right to Right")),
                EightBitANSI.paint_blue(context.player.channel_mix.right_to_right or default),
            ),
            (
                EightBitANSI.paint_white(_("Reset previous filters")),
                EightBitANSI.paint_red(_("Yes")) if reset else EightBitANSI.paint_green(_("No")),
            ),
        ]
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context,
                title=_("New channel mix effect applied to the player"),
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Setting"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Value"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="distortion", description=_("Apply a distortion filter to the player"))
    @app_commands.describe(
        sin_offset=_("The distortion Sine offset"),
        sin_scale=_("The distortion Sine scale"),
        cos_offset=_("The distortion Cosine offset"),
        cos_scale=_("The distortion Cosine scale"),
        tan_offset=_("The distortion Tangent offset"),
        tan_scale=_("The distortion Tangent scale"),
        offset=_("The distortion offset"),
        scale=_("The distortion scale"),
        reset=_("Reset any existing effects currently applied to the player"),
    )
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_distortion(
        self,
        interaction: InteractionT,
        sin_offset: Range[float, 0.0, None] = None,
        sin_scale: Range[float, 0.0, None] = None,
        cos_offset: Range[float, 0.0, None] = None,
        cos_scale: Range[float, 0.0, None] = None,
        tan_offset: Range[float, 0.0, None] = None,
        tan_scale: Range[float, 0.0, None] = None,
        offset: Range[float, 0.0, None] = None,
        scale: Range[float, 0.0, None] = None,
        reset: bool = False,
    ) -> None:
        """Apply a distortion filter to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)
        context.player.distortion.sin_offset = sin_offset or context.player.distortion.sin_offset
        context.player.distortion.sin_scale = sin_scale or context.player.distortion.sin_scale
        context.player.distortion.cos_offset = cos_offset or context.player.distortion.cos_offset
        context.player.distortion.cos_scale = cos_scale or context.player.distortion.cos_scale
        context.player.distortion.tan_offset = tan_offset or context.player.distortion.tan_offset
        context.player.distortion.tan_scale = tan_scale or context.player.distortion.tan_scale
        context.player.distortion.offset = offset or context.player.distortion.offset
        context.player.distortion.scale = scale or context.player.distortion.scale
        await context.player.set_distortion(
            distortion=context.player.distortion, requester=context.author, forced=reset
        )
        default = _("Not changed")
        data = [
            (
                EightBitANSI.paint_white(_("Sine Offset")),
                EightBitANSI.paint_blue(context.player.distortion.sin_offset or default),
            ),
            (
                EightBitANSI.paint_white(_("Sine Scale")),
                EightBitANSI.paint_blue(context.player.distortion.sin_scale or default),
            ),
            (
                EightBitANSI.paint_white(_("Cosine Offset")),
                EightBitANSI.paint_blue(context.player.distortion.cos_offset or default),
            ),
            (
                EightBitANSI.paint_white(_("Cosine Scale")),
                EightBitANSI.paint_blue(context.player.distortion.cos_scale or default),
            ),
            (
                EightBitANSI.paint_white(_("Tangent Offset")),
                EightBitANSI.paint_blue(context.player.distortion.tan_offset or default),
            ),
            (
                EightBitANSI.paint_white(_("Tangent Scale")),
                EightBitANSI.paint_blue(context.player.distortion.tan_scale or default),
            ),
            (
                EightBitANSI.paint_white(_("Offset")),
                EightBitANSI.paint_blue(context.player.distortion.offset or default),
            ),
            (EightBitANSI.paint_white(_("Scale")), EightBitANSI.paint_blue(context.player.distortion.scale or default)),
            (
                EightBitANSI.paint_white(_("Reset previous filters")),
                EightBitANSI.paint_red(_("Yes")) if reset else EightBitANSI.paint_green(_("No")),
            ),
        ]
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context,
                title=_("New distortion effect applied to the player"),
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Setting"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Value"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="echo", description=_("Apply a echo filter to the player"))
    @app_commands.describe(
        delay=_("The delay of the echo"),
        decay=_("The decay of the echo"),
        reset=_("Reset any existing effects currently applied to the player"),
    )
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_echo(
        self,
        interaction: InteractionT,
        delay: Range[float, 0.0, None] = None,
        decay: Range[float, 0.0, 1.0] = None,
        reset: bool = False,
    ) -> None:
        """Apply a echo filter to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)
        context.player.echo.delay = delay or context.player.echo.delay
        context.player.echo.decay = decay or context.player.echo.decay
        await context.player.set_echo(echo=context.player.echo, requester=context.author, forced=reset)
        default = _("Not changed")

        data = [
            (EightBitANSI.paint_white(_("Delay")), EightBitANSI.paint_blue(context.player.echo.delay or default)),
            (EightBitANSI.paint_white(_("Decay")), EightBitANSI.paint_blue(context.player.echo.decay or default)),
            (
                EightBitANSI.paint_white(_("Reset previous filters")),
                EightBitANSI.paint_red(_("Yes")) if reset else EightBitANSI.paint_green(_("No")),
            ),
        ]
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context,
                title=_("New echo effect applied to the player"),
                description=box(
                    tabulate(
                        data,
                        headers=(
                            EightBitANSI.paint_yellow(_("Setting"), bold=True, underline=True),
                            EightBitANSI.paint_yellow(_("Value"), bold=True, underline=True),
                        ),
                        tablefmt="fancy_grid",
                    ),
                    lang="ansi",
                ),
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="show", description=_("Show the current filters applied to the player"))
    @app_commands.guild_only()
    @requires_player(slash=True)
    async def slash_fx_show(self, interaction: InteractionT) -> None:
        """Show the current filters applied to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)

        t_effect = EightBitANSI.paint_yellow(_("Effect"), bold=True, underline=True)
        t_values = EightBitANSI.paint_yellow(_("Values"), bold=True, underline=True)
        default = _("Not changed")

        data = []
        for effect in (
            context.player.karaoke,
            context.player.timescale,
            context.player.tremolo,
            context.player.vibrato,
            context.player.rotation,
            context.player.distortion,
            context.player.low_pass,
            context.player.channel_mix,
            context.player.echo,
        ):
            data_ = {t_effect: effect.__class__.__name__}

            if effect:
                values = effect.to_dict()
                if not isinstance(effect, Equalizer):
                    data_[t_values] = "\n".join(
                        f"{EightBitANSI.paint_white(k.title())}: {EightBitANSI.paint_green(v or default)}"
                        for k, v in values.items()
                    )
                else:
                    values = values["equalizer"]
                    data_[t_values] = "\n".join(
                        [
                            f"{EightBitANSI.paint_white('Band ' + band['band'])}: {EightBitANSI.paint_green(band['gain'])}"
                            for band in values
                            if band["gain"]
                        ]
                    )
            else:
                data_[t_values] = EightBitANSI.paint_blue(_("N/A"))
            data.append(data_)

        await context.send(
            embed=await self.lavalink.construct_embed(
                title=_("Current filters applied to the player"),
                description="__**{translation}:**__\n{data}".format(
                    data=box(tabulate(data, headers="keys", tablefmt="fancy_grid", maxcolwidths=[10, 18]), lang="ansi")  # type: ignore
                    if data
                    else _("None"),
                    translation=discord.utils.escape_markdown(_("Currently Applied")),
                ),
                messageable=context,
            ),
            ephemeral=True,
        )

    @slash_fx.command(name="reset", description=_("Reset any existing filters currently applied to the player"))
    @app_commands.guild_only()
    @requires_player(slash=True)
    @invoker_is_dj(slash=True)
    async def slash_fx_reset(self, interaction: InteractionT) -> None:
        """Reset any existing filters currently applied to the player"""
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        context = await self.bot.get_context(interaction)

        await context.player.set_filters(requester=context.author, reset_not_set=True)
        await context.send(
            embed=await self.lavalink.construct_embed(
                messageable=context, description=_("Reset any existing filters currently applied to the player")
            ),
            ephemeral=True,
        )
