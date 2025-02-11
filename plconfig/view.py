from __future__ import annotations

import contextlib
from pathlib import Path

import discord
from redbot.core.i18n import Translator
from redbot.core.utils.chat_formatting import box
from tabulate import tabulate

from pylav.types import CogT, InteractionT
from pylav.utils import PyLavContext, get_true_path
from pylav.utils.theme import EightBitANSI

_ = Translator("PyLavConfigurator", Path(__file__))


class EmbedGenerator:
    def __init__(self, cog: CogT, context: PyLavContext):
        self.cog = cog
        self.context = context

    async def generate_pylav_config_embed(self) -> discord.Embed:
        enabled = EightBitANSI.paint_green(_("Enabled"), bold=True, italic=True)
        disabled = EightBitANSI.paint_red(_("Disabled"), bold=True, italic=True)
        pylav_config = await self.cog.lavalink.lib_db_manager.get_config().fetch_all()
        data = [
            (
                EightBitANSI.paint_white(_("Use Managed Node")),
                enabled if pylav_config["enable_managed_node"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Update\nManaged Node")),
                enabled if pylav_config["auto_update_managed_nodes"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Change Bot activity")),
                enabled if pylav_config["update_bot_activity"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Use Bundled\nPyLav Nodes")),
                enabled if pylav_config["use_bundled_pylav_external"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Use Bundled\nlava.link Nodes")),
                enabled if pylav_config["use_bundled_lava_link_external"] else disabled,
            ),
        ]
        return await self.cog.lavalink.construct_embed(
            description=box(
                tabulate(
                    data,
                    headers=(
                        EightBitANSI.paint_yellow(_("PyLav Config"), underline=True, bold=True),
                        EightBitANSI.paint_yellow(_("Value"), underline=True, bold=True),
                    ),
                    tablefmt="fancy_grid",
                ),
                lang="ansi",
            ),
            messageable=self.context,
        )

    async def generate_global_player_config_embed(self) -> discord.Embed:

        enabled = EightBitANSI.paint_green(_("Enabled"), bold=True, italic=True)
        disabled = EightBitANSI.paint_red(_("Disabled"), bold=True, italic=True)
        global_config = await self.cog.lavalink.player_config_manager.get_global_config().fetch_all()

        (EightBitANSI.paint_white(_("Volume")), EightBitANSI.paint_cyan(global_config["volume"]))
        data = [
            (EightBitANSI.paint_white(_("Maximum Volume")), EightBitANSI.paint_cyan(global_config["max_volume"])),
            (
                EightBitANSI.paint_white(_("AutoPlay")),
                enabled if global_config["auto_play"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Shuffling")),
                enabled if global_config["shuffle"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Shuffle")),
                enabled if global_config["auto_shuffle"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Deafen")),
                enabled if global_config["self_deaf"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Disconnect")),
                EightBitANSI.paint_green(
                    _("{enabled}\n{timer} seconds").format(enabled=enabled, timer=global_config["empty_queue_dc"].time)
                )
                if global_config["empty_queue_dc"].enabled
                else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Alone Pause")),
                EightBitANSI.paint_green(
                    _("{enabled}\n{timer} seconds").format(enabled=enabled, timer=global_config["alone_pause"].time)
                )
                if global_config["alone_pause"].enabled
                else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Alone Disconnect")),
                EightBitANSI.paint_green(
                    _("{enabled}\n{timer} seconds").format(enabled=enabled, timer=global_config["alone_dc"].time)
                )
                if global_config["alone_dc"].enabled
                else disabled,
            ),
        ]

        return await self.cog.lavalink.construct_embed(
            description=box(
                tabulate(
                    data,
                    headers=(
                        EightBitANSI.paint_yellow(_("Global Player Config"), underline=True, bold=True),
                        EightBitANSI.paint_yellow(_("Value"), underline=True, bold=True),
                    ),
                    tablefmt="fancy_grid",
                ),
                lang="ansi",
            ),
            messageable=self.context,
        )

    async def generate_context_player_config_embed(self) -> discord.Embed:
        if not self.context.guild:
            return await self.cog.lavalink.construct_embed(
                messageable=self.context,
                description=_("You need to be in a server to be able to show this page."),
            )

        enabled = EightBitANSI.paint_green(_("Enabled"), bold=True, italic=True)
        disabled = EightBitANSI.paint_red(_("Disabled"), bold=True, italic=True)

        ac_max_volume = await self.cog.lavalink.player_config_manager.get_max_volume(self.context.guild.id)
        ac_volume = await self.cog.lavalink.player_config_manager.get_volume(self.context.guild.id)
        ac_alone_dc = await self.cog.lavalink.player_config_manager.get_alone_dc(self.context.guild.id)
        ac_alone_pause = await self.cog.lavalink.player_config_manager.get_alone_pause(self.context.guild.id)
        ac_empty_queue_dc = await self.cog.lavalink.player_config_manager.get_empty_queue_dc(self.context.guild.id)
        ac_shuffle = await self.cog.lavalink.player_config_manager.get_shuffle(self.context.guild.id)
        ac_auto_shuffle = await self.cog.lavalink.player_config_manager.get_auto_shuffle(self.context.guild.id)
        ac_self_deaf = await self.cog.lavalink.player_config_manager.get_self_deaf(self.context.guild.id)
        ac_auto_play = await self.cog.lavalink.player_config_manager.get_auto_play(self.context.guild.id)

        data = [
            (EightBitANSI.paint_white(_("Volume")), EightBitANSI.paint_cyan(ac_volume)),
            (EightBitANSI.paint_white(_("Maximum Volume")), EightBitANSI.paint_cyan(ac_max_volume)),
            (
                EightBitANSI.paint_white(_("AutoPlay")),
                EightBitANSI.paint_green(enabled) if ac_auto_play else EightBitANSI.paint_red(disabled),
            ),
            (EightBitANSI.paint_white(_("Shuffling")), enabled if ac_shuffle else disabled),
            (EightBitANSI.paint_white(_("Auto Shuffle")), enabled if ac_auto_shuffle else disabled),
            (EightBitANSI.paint_white(_("Auto Deafen")), enabled if ac_self_deaf else disabled),
            (
                EightBitANSI.paint_white(_("Auto Disconnect")),
                EightBitANSI.paint_green(
                    _("{enabled}\n{timer} seconds").format(enabled=enabled, timer=ac_empty_queue_dc.time)
                )
                if ac_empty_queue_dc.enabled
                else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Alone Pause")),
                EightBitANSI.paint_green(
                    _("{enabled}\n{timer} seconds").format(enabled=enabled, timer=ac_alone_pause.time)
                )
                if ac_alone_pause.enabled
                else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Alone Disconnect")),
                EightBitANSI.paint_green(
                    _("{enabled}\n{timer} seconds").format(enabled=enabled, timer=ac_alone_dc.time)
                )
                if ac_alone_dc.enabled
                else disabled,
            ),
        ]

        return await self.cog.lavalink.construct_embed(
            description=box(
                tabulate(
                    data,
                    headers=(
                        EightBitANSI.paint_yellow(_("Context Player Config"), underline=True, bold=True),
                        EightBitANSI.paint_yellow(_("Value"), underline=True, bold=True),
                    ),
                    tablefmt="fancy_grid",
                ),
                lang="ansi",
            ),
            messageable=self.context,
        )

    async def generate_server_player_config_embed(self) -> discord.Embed:
        if not self.context.guild:
            return await self.cog.lavalink.construct_embed(
                messageable=self.context,
                description=_("You need to be in a server to be able to show this page."),
            )

        enabled = EightBitANSI.paint_green(_("Enabled"), bold=True, italic=True)
        disabled = EightBitANSI.paint_red(_("Disabled"), bold=True, italic=True)

        config = await self.cog.lavalink.player_config_manager.get_config(self.context.guild.id).fetch_all()

        dj_user_str = (
            "\n".join(
                [
                    EightBitANSI.colorize(
                        discord.utils.escape_markdown(str(member_obj)),
                        color=EightBitANSI.closest_color(*member_obj.color.to_rgb()),
                    )
                    if (member_obj := self.context.guild.get_member(user))
                    else EightBitANSI.paint_green(user)
                    for user in config["dj_users"]
                ]
            )
            if len(config["dj_users"]) <= 5
            else _("Too many to show ({count})").format(count=len(config["dj_users"]))
        )

        dj_role_str = (
            "\n".join(
                [
                    EightBitANSI.colorize(
                        discord.utils.escape_markdown(str(role_obj)),
                        color=EightBitANSI.closest_color(*role_obj.color.to_rgb()),
                    )
                    if (role_obj := self.context.guild.get_role(role))
                    else EightBitANSI.paint_green(role)
                    for role in config["dj_roles"]
                ]
            )
            if len(config["dj_roles"]) <= 5
            else _("Too many to show ({count})").format(count=len(config["dj_roles"]))
        )
        if len(config["dj_users"]) == 0:
            dj_user_str = EightBitANSI.paint_red(_("None"))
        else:
            dj_user_str = EightBitANSI.paint_green(dj_user_str)

        if len(config["dj_roles"]) == 0:
            dj_role_str = EightBitANSI.paint_red(_("None"))
        else:
            dj_role_str = EightBitANSI.paint_green(dj_role_str)

        data = [
            (EightBitANSI.paint_white(_("Volume")), EightBitANSI.paint_cyan(config["volume"])),
            (EightBitANSI.paint_white(_("Maximum Volume")), EightBitANSI.paint_cyan(config["max_volume"])),
            (
                EightBitANSI.paint_white(_("AutoPlay")),
                enabled if config["auto_play"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("AutoPlay Playlist")),
                EightBitANSI.paint_green(config["auto_play_playlist_id"]) if config["auto_play"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Loop track")),
                enabled if config["repeat_current"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Loop Queue")),
                enabled if config["repeat_queue"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Shuffling")),
                enabled if config["shuffle"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Shuffle")),
                enabled if config["auto_shuffle"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Deafen")),
                enabled if config["self_deaf"] else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Disconnect")),
                EightBitANSI.paint_green(
                    _("{enabled}\n{timer} seconds").format(enabled=enabled, timer=config["empty_queue_dc"].time)
                )
                if config["empty_queue_dc"].enabled
                else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Alone Pause")),
                EightBitANSI.paint_green(
                    _("{enabled}\n{timer} seconds").format(enabled=enabled, timer=config["alone_pause"].time)
                )
                if config["alone_pause"].enabled
                else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Auto Alone Disconnect")),
                EightBitANSI.paint_green(
                    _("{enabled}\n{timer} seconds").format(enabled=enabled, timer=config["alone_dc"].time)
                )
                if config["alone_dc"].enabled
                else disabled,
            ),
            (
                EightBitANSI.paint_white(_("Forced Voice Channel")),
                EightBitANSI.paint_green(config["forced_channel_id"])
                if config["forced_channel_id"] != 0
                else EightBitANSI.paint_red(_("None")),
            ),
            (
                EightBitANSI.paint_white(_("Forced Command Channel")),
                EightBitANSI.paint_green(config["text_channel_id"])
                if config["text_channel_id"] != 0
                else EightBitANSI.paint_red(_("None")),
            ),
            (
                EightBitANSI.paint_white(_("Forced Notification Channel")),
                EightBitANSI.paint_green(config["notify_channel_id"])
                if config["notify_channel_id"] != 0
                else EightBitANSI.paint_red(_("None")),
            ),
            (EightBitANSI.paint_white(_("DJ Users")), dj_user_str),
            (EightBitANSI.paint_white(_("DJ Roles")), dj_role_str),
        ]

        return await self.cog.lavalink.construct_embed(
            description=box(
                tabulate(
                    data,
                    headers=(
                        EightBitANSI.paint_yellow(_("Server Player Config"), underline=True, bold=True),
                        EightBitANSI.paint_yellow(_("Value"), underline=True, bold=True),
                    ),
                    tablefmt="fancy_grid",
                ),
                lang="ansi",
            ),
            messageable=self.context,
        )

    async def generate_playlist_tasks_embed(self) -> discord.Embed:
        pylav_config = await self.cog.lavalink.lib_db_manager.get_config().fetch_all()

        data = [
            (
                EightBitANSI.paint_white(_("Next Bundled\nPlaylist Update")),
                EightBitANSI.paint_blue(
                    pylav_config["next_execution_update_bundled_playlists"].strftime("%Y/%m/%d\n%H:%M:%S UTC")
                ),
            ),
            (
                EightBitANSI.paint_white(_("Next Bundled External\nPlaylist Update")),
                EightBitANSI.paint_blue(
                    pylav_config["next_execution_update_bundled_external_playlists"].strftime("%Y/%m/%d\n%H:%M:%S UTC")
                ),
            ),
            (
                EightBitANSI.paint_white(_("Next External\nPlaylist Update")),
                EightBitANSI.paint_blue(
                    pylav_config["next_execution_update_external_playlists"].strftime("%Y/%m/%d\n%H:%M:%S UTC")
                ),
            ),
        ]

        return await self.cog.lavalink.construct_embed(
            description=box(
                tabulate(
                    data,
                    headers=(
                        EightBitANSI.paint_yellow(_("Playlist Tasks"), underline=True, bold=True),
                        EightBitANSI.paint_yellow(_("Date and Time (UTC)"), underline=True, bold=True),
                    ),
                    tablefmt="fancy_grid",
                ),
                lang="ansi",
            ),
            messageable=self.context,
        )

    async def generate_pylav_paths_embed(self) -> discord.Embed:
        if not await self.cog.bot.is_owner(self.context.author):
            return await self.cog.lavalink.construct_embed(
                messageable=self.context,
                description=_("You need to be the bot owner to be able to show this page."),
            )

        pylav_config = await self.cog.lavalink.lib_db_manager.get_config().fetch_all()

        data = [
            (EightBitANSI.paint_white(_("Config Folder")), EightBitANSI.paint_magenta(pylav_config["config_folder"])),
            (
                EightBitANSI.paint_white(_("Local Tracks")),
                EightBitANSI.paint_magenta(pylav_config["localtrack_folder"]),
            ),
            (
                EightBitANSI.paint_white(_("Java Executable")),
                (
                    EightBitANSI.paint_magenta(jpath)
                    if (jpath := get_true_path(pylav_config["java_path"]))
                    else EightBitANSI.paint_red(_("Not Found"))
                ),
            ),
        ]

        return await self.cog.lavalink.construct_embed(
            description=box(
                tabulate(
                    data,
                    headers=(
                        EightBitANSI.paint_yellow(_("Paths"), underline=True, bold=True),
                        EightBitANSI.paint_yellow(_("Path"), underline=True, bold=True),
                    ),
                    tablefmt="plain",
                ),
                lang="ansi",
            ),
            messageable=self.context,
        )

    async def generate_managed_node_config_embed(self) -> discord.Embed:
        enabled = EightBitANSI.paint_green(_("Enabled"), bold=True, italic=True)
        disabled = EightBitANSI.paint_red(_("Disabled"), bold=True, italic=True)
        build_date, build_time = self.cog.lavalink.managed_node_controller._buildtime.split(" ", 1)
        build_data = build_date.split("/")
        build_date = f"{build_data[2]}/{build_data[1]}/{build_data[0]}\n{build_time}"

        data = [
            (
                EightBitANSI.paint_white(_("Java")),
                EightBitANSI.paint_blue(self.cog.lavalink.managed_node_controller._jvm),
            ),
            (
                EightBitANSI.paint_white(_("Lavaplayer")),
                EightBitANSI.paint_blue(self.cog.lavalink.managed_node_controller._lavaplayer),
            ),
            (
                EightBitANSI.paint_white(_("Lavalink Branch")),
                EightBitANSI.paint_blue(self.cog.lavalink.managed_node_controller._lavalink_branch),
            ),
            (
                EightBitANSI.paint_white(_("Lavalink Version")),
                EightBitANSI.paint_blue(self.cog.lavalink.managed_node_controller._version),
            ),
            (
                EightBitANSI.paint_white(_("Lavalink Build")),
                EightBitANSI.paint_blue(self.cog.lavalink.managed_node_controller._lavalink_build),
            ),
            (EightBitANSI.paint_white(_("Build Time")), EightBitANSI.paint_blue(build_date)),
            (
                EightBitANSI.paint_white(_("Commit")),
                EightBitANSI.paint_blue(self.cog.lavalink.managed_node_controller._commit),
            ),
            (
                EightBitANSI.paint_white(_("Auto Update")),
                enabled if await self.cog.lavalink.managed_node_controller.should_auto_update() else disabled,
            ),
        ]

        return await self.cog.lavalink.construct_embed(
            description=box(
                tabulate(
                    data,
                    headers=(
                        EightBitANSI.paint_yellow(_("Managed Node Config"), underline=True, bold=True),
                        EightBitANSI.paint_yellow(_("Value"), underline=True, bold=True),
                    ),
                    tablefmt="fancy_grid",
                ),
                lang="ansi",
            ),
            messageable=self.context,
        )

    async def get_embed(self, key: str) -> discord.Embed:
        if key == "pylav_config":
            return await self.generate_pylav_config_embed()
        elif key == "global_player_config":
            return await self.generate_global_player_config_embed()
        elif key == "context_player_config":
            return await self.generate_context_player_config_embed()
        elif key == "server_player_config":
            return await self.generate_server_player_config_embed()
        elif key == "playlist_tasks":
            return await self.generate_playlist_tasks_embed()
        elif key == "pylav_paths":
            return await self.generate_pylav_paths_embed()
        elif key == "managed_node_config":
            return await self.generate_managed_node_config_embed()
        else:
            return await self.cog.lavalink.construct_embed(
                messageable=self.context,
                description=_("Select an option from the dropdown menu below."),
            )


class InfoSelector(discord.ui.Select):
    def __init__(
        self,
        cog: CogT,
        context: PyLavContext,
        options: list[discord.SelectOption],
    ):

        super().__init__(min_values=1, max_values=1, options=options, placeholder=_("Pick an option to view"))
        self.cog = cog
        self.embed_maker = EmbedGenerator(cog=cog, context=context)

    async def callback(self, interaction: InteractionT):
        await interaction.response.defer()
        if self.view.author.id != interaction.user.id:
            await interaction.response.send_message(
                embed=await self.cog.lavalink.construct_embed(
                    messageable=interaction, description=_("You are not authorized to interact with this option")
                ),
                ephemeral=True,
            )
            return
        embed_key = self.values[0]
        embed = await self.embed_maker.get_embed(key=embed_key)
        if not interaction.response.is_done():
            await interaction.response.edit_message(embed=embed, view=self.view)
        else:
            await interaction.edit_original_response(embed=embed, view=self.view)


class InfoView(discord.ui.View):
    def __init__(self, cog: CogT, context: PyLavContext, options: list[discord.SelectOption]):
        super().__init__(timeout=180.0)
        self.delete_after_timeout = True
        self.current_page = 0
        self._running = True
        self.bot = cog.bot
        self.cog = cog
        self.context = context
        self.author = context.author
        self.selector = InfoSelector(cog=cog, context=context, options=options)
        self.add_item(self.selector)

    async def interaction_check(self, interaction: InteractionT):
        """Just extends the default reaction_check to use owner_ids"""
        if (not await self.bot.allowed_by_whitelist_blacklist(interaction.user, guild=interaction.guild)) or (
            self.author and (interaction.user.id != self.author.id)
        ):
            await interaction.response.send_message(
                content=_("You are not authorized to interact with this"), ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        self._running = False
        if self.message is None:
            return
        with contextlib.suppress(discord.HTTPException):
            if self.delete_after_timeout and not self.message.flags.ephemeral:
                await self.message.delete()
            else:
                await self.message.edit(view=None)

    async def send_initial_message(self):
        embed = await self.selector.embed_maker.get_embed(key="fallback")
        self.message = await self.context.send(embed=embed, view=self, ephemeral=True)
        return self.message

    async def prepare(self):
        return

    async def start(self):
        await self.send_initial_message()
