import discord
from discord.ext import commands
from django.conf import settings

from bot.bot import CustomBot, CustomContext


class OwnerLoggingCog(commands.Cog):
    """Owner-only commands that make the bot dynamic."""

    def __init__(self, bot: CustomBot):
        self.bot = bot

    @commands.command(hidden=True, name='cache')
    @commands.is_owner()
    async def _cache(self, ctx):
        await ctx.send(
            f'Cached guild count: {len(self.bot.guilds)}\n'
            f'Cached message count: {len(self.bot.cached_messages)}\n'
            f'Cached user count: {len(self.bot.users)}',
        )

    @commands.group(name='log', hidden=True)
    @commands.is_owner()
    async def _logging(self, context: CustomContext):
        if context.invoked_subcommand is not None:
            return
        if not isinstance(context.command, commands.Group):
            return
        txt = '\n'.join(f'`{context.prefix}{cmd.qualified_name}`' for cmd in context.command.commands)
        await context.say_as_embed(txt)

    @_logging.command(name='get', hidden=True)
    @commands.is_owner()
    async def _get_log(self, context, *, filename='bot.log'):
        if filename not in ['bot.log', ]:
            return
        await context.send(file=discord.File(settings.BASE_DIR / filename))

    @_logging.command(name='flush', hidden=True)
    @commands.is_owner()
    async def _flush_log(self, context, *, filename='bot.log'):
        if filename not in ['bot.log', ]:
            return
        # self.bot.logger.handlers
        with open(settings.BASE_DIR / filename, 'w'):
            pass
        await context.send('\N{OK HAND SIGN}')
