import logging
import sys
import traceback
from typing import Union, Optional, List

import discord
from discord.app_commands import CheckFailure
from discord.ext import commands

from bot.conf import bot_conf
from bot.texts.maps import ERROR_TEXT_MAP
from bot.utils.exceptions import MyInteractionError, MyCustomError, MyAppCommandError
from bot.utils.ui import MyEmbed
from bot.utils.logger import setup_logger

logger = logging.getLogger('bot')
setup_logger(logger)


class CustomContext(commands.Context):

    async def say_as_embed(
            self,
            description=None, title='',
            embed=None, color=None,
            view=None,
            delete_after=None,
            footer_text=None,
            image_url=None,
            thumb_url=None,
            reply=True,
    ):
        """Make the bot say as an Embed.
        Passing an 'embed' will send it instead.
        Shortcut for color kwarg: 'info' (default), 'warning', 'error', 'success'
        """
        if color == 'info':
            color = discord.Color.teal()
        elif color == 'warning':
            color = discord.Color.gold()
        elif color == 'error':
            color = discord.Color.red()
        elif color == 'success':
            color = discord.Color.green()
        else:
            color = bot_conf.EMBED_DEFAULT_COLOR

        if embed is None:

            embed = discord.Embed(
                title=title,
                description=description,
                colour=color)

            if image_url:
                embed.set_image(url=image_url)

            if thumb_url:
                embed.set_thumbnail(url=thumb_url)

            if footer_text:
                embed.set_footer(text=footer_text)

        if self.message and reply is True:
            # handle exception where the message is deleted before the bot could reply
            try:
                message = await self.reply(embed=embed, view=view, delete_after=delete_after)
            except discord.HTTPException:
                message = await self.send(
                    content=f'{self.author.mention}',
                    embed=embed, view=view,
                    delete_after=delete_after
                )
        else:
            message = await self.send(embed=embed, view=view, delete_after=delete_after)

        return message


class ImportantChannelList:
    images: Optional[discord.TextChannel] = None
    log_message: Optional[discord.TextChannel] = None

    def is_valid(self):
        return \
            self.images \
            and self.log_message


class CustomBot(commands.Bot):
    ignored = (
        commands.CommandNotFound,
        commands.PrivateMessageOnly,
        commands.CheckAnyFailure,
        commands.CheckFailure,
        commands.CommandOnCooldown,
        commands.MissingRequiredArgument,
    )
    shout_outs = (
        commands.BadArgument,
    )

    def __init__(self, initial_extensions: list, *args, **kwargs):
        self.logger = logger
        self.channels = ImportantChannelList()
        self.working_guilds: List[discord.Guild] = []
        self.initial_extensions = initial_extensions

        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        self.logger.info(f'Logged in as: {self.user.name} (ID: {self.user.id})')
        if not bot_conf.DEBUG:
            presence = f'Prefix: {bot_conf.PREFIX}'
        else:
            presence = 'sensei anone'
        await self.change_presence(activity=discord.Game(name=presence))
        self.prepare_working_guilds()
        self.prepare_channels()

    async def get_context(self, message, *, cls=CustomContext) -> CustomContext:
        return await super().get_context(message, cls=cls)

    def prepare_working_guilds(self):
        self.working_guilds = []
        for guild_id in bot_conf.ALLOWED_GUILDS:
            guild = self.get_guild(guild_id)
            if not guild:
                self.logger.critical(f'Missing one of the ALLOWED_GUILDS: {guild_id}')
                continue
            self.working_guilds.append(guild)

    def prepare_channels(self):
        self.channels.images = self.get_channel(bot_conf.IMAGE_LIST_CHANNEL)
        self.channels.log_message = self.get_channel(bot_conf.LOG_MESSAGE_CHANNEL)

        if not self.channels.is_valid():
            self.logger.critical('Missing one of the important channels.')

    async def on_error(self, event_method: str, *args, **kwargs):

        _, exc, tb_obj = sys.exc_info()
        # handle generic interaction errors
        if event_method == 'on_interaction':
            if isinstance(exc, MyInteractionError) and exc.custom:
                error_text = str(exc)
            else:
                error_text = ERROR_TEXT_MAP['uncaught_error']
            await self.on_interaction_error(*args, error_text=error_text)

        # only log non-custom errors
        if isinstance(exc, MyCustomError) and exc.custom:
            return
        self.logger.debug(f'{exc} | Event method: {event_method}',
                          exc_info=True)

    async def on_interaction_error(self, interaction: discord.Interaction, error_text: str):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                embed=MyEmbed(description=error_text, color='error'),
                ephemeral=True
            )
        else:
            await interaction.edit_original_response(
                embed=MyEmbed(description=error_text, color='error'),
                view=None
            )

    async def on_app_command_error(
            self,
            interaction: discord.Interaction,
            error: Union[discord.app_commands.AppCommandError, MyAppCommandError]
    ):
        # explicitly handled exceptions
        if isinstance(error, MyAppCommandError):
            # explicit error message as response
            err_resp_text = str(error)

        elif isinstance(error, CheckFailure):
            err_resp_text = ERROR_TEXT_MAP['check_failed']
        # not explicitly handled exceptions
        else:
            # generic report error message
            err_resp_text = ERROR_TEXT_MAP['uncaught_error']

        # log when error is uncaught
        if err_resp_text == ERROR_TEXT_MAP['uncaught_error']:
            self.logger.debug(
                f'{error} | Interaction: data- {interaction.data} extras-{interaction.extras} | '
                f'By: {interaction.user.id}',
                exc_info=True
            )
        await self.on_interaction_error(interaction, error_text=err_resp_text)
