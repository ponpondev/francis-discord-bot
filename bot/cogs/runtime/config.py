import discord
from discord.ext import commands

from bot.bot import CustomBot
from bot.conf import bot_conf
from bot.converters.arguments import sub_command
from bot.texts.info import ConfigBotInfo, ConfigRoleInfo, ConfigGroupInfo, ConfigLogInfo


class ConfigCommandCog(commands.Cog):
    """Commands to update the bot's configurations of various aspects."""

    def __init__(self, bot: CustomBot):
        self.bot = bot

    @commands.group(name='config', aliases=['conf'], case_insensitive=True,
                    brief=ConfigGroupInfo.brief, help=ConfigGroupInfo.help)
    @commands.is_owner()
    async def _admin_config(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.MissingRequiredArgument(sub_command)

    @_admin_config.command(name='bot', brief=ConfigBotInfo.brief, help=ConfigBotInfo.help())
    @commands.is_owner()
    async def _admin_bot_config(self, ctx, attr, *, value):
        await self._update_config(ctx, 'bot', attr, value)

    @_admin_config.command(name='log', brief=ConfigLogInfo.brief, help=ConfigLogInfo.help())
    @commands.is_owner()
    async def _admin_log_config(self, ctx, attr, *, value):
        await self._update_config(ctx, 'log', attr, value)

    @_admin_config.command(name='role', brief=ConfigRoleInfo.brief, help=ConfigRoleInfo.help())
    @commands.is_owner()
    async def _admin_role_config(self, ctx, attr, *, value):
        await self._update_config(ctx, 'role', attr, value)

    async def _update_config(self, ctx, _type, _attr, _value):
        conf_attr = _attr.replace('-', '_').upper()
        if conf_attr not in getattr(bot_conf, f'__{_type}__', []):
            raise commands.BadArgument(f'Invalid {_type} config attribute.')

        value = bot_conf.process_value(conf_attr, _value)

        if value in [None, []]:
            raise commands.BadArgument(
                f'Unable to parse `{_value}` for {_type} config attribute `{conf_attr}`. '
                f'Make sure to enter acceptable values!'
            )

        # set the config
        setattr(bot_conf, conf_attr, value)
        bot_conf.save()

        # handle case by case
        if conf_attr == 'PREFIX':
            await self.bot.change_presence(activity=discord.Game(name=f'Prefix: {bot_conf.PREFIX}'))
        elif conf_attr == 'ALLOWED_GUILDS':
            self.bot.prepare_working_guilds()
        elif conf_attr in bot_conf.__channels__:
            self.bot.prepare_channels()
        preview = bot_conf.process_preview(conf_attr, value)

        # notify the invoker
        desc = f'`{conf_attr}` is updated to `{value}`.'
        if preview:
            desc += f'\n\nPreview: {preview}'

        desc += '\n\nSome changes will take effect only after bot restart.\n' \
                f'Use `{bot_conf.PREFIX}restart` to restart the bot.'
        # update the help text, hopefully
        await self.bot.unload_extension('bot.cogs.runtime')
        await self.bot.load_extension('bot.cogs.runtime')
        await ctx.say_as_embed(
            title=f'{_type.capitalize()} config updated',
            description=desc
        )
