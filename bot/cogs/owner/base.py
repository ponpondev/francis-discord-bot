from typing import Optional, Literal

import discord
from discord.ext import commands

from bot.bot import CustomBot, CustomContext
from bot.converters.arguments import EmbedDataConverter


class OwnerBaseCog(commands.Cog):
    """Owner-only commands that make the bot dynamic."""

    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.path = 'bot.cogs.'
        self.path2 = 'bot.tasks.'

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, context, *, module):
        """Loads a module."""
        try:
            await self.bot.load_extension(f'{self.path}{module}')
        except commands.ExtensionError:
            await self.bot.load_extension(f'{self.path2}{module}')

        await context.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, context, *, module):
        """Unloads a module."""
        try:
            await self.bot.unload_extension(f'{self.path}{module}')
        except commands.ExtensionError:
            await self.bot.unload_extension(f'{self.path2}{module}')

        await context.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, context, *, module):
        """Reloads a module."""
        try:
            await self.bot.unload_extension(f'{self.path}{module}')
            await self.bot.load_extension(f'{self.path}{module}')
        except commands.ExtensionError:
            await self.bot.unload_extension(f'{self.path2}{module}')
            await self.bot.load_extension(f'{self.path2}{module}')

        await context.send('\N{OK HAND SIGN}')

    @commands.command(name='dm', hidden=True)
    @commands.is_owner()
    async def _send_a_dm(self, context, channel: discord.User, *, content: str = None):
        # must be put here to convert empty argument uwu
        parsed_content, embeds, parsed = await EmbedDataConverter().convert(context, content)
        message = await channel.send(content=parsed_content, embeds=embeds)
        await context.say_as_embed(
            title='Message sent~',
            description=f'[>>Check it out<<]({message.jump_url} "{message.jump_url}")',
            footer_text=f'JSON was parsed successfully.' if parsed else
            'Failed to parse JSON data. If it\'s supposed to parse, check your data for mistakes.'
        )

    @commands.command(hidden=True, name='sync')
    @commands.is_owner()
    async def _app_command_sync(self, ctx: CustomContext, spec: Optional[Literal["~"]] = None) -> None:
        if spec == "~":
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        else:
            fmt = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(fmt)} commands {'globally' if spec is None else 'to the current guild'}."
        )
        return

    @commands.command(hidden=True, name='test')
    @commands.is_owner()
    async def _test_command(self, context: CustomContext):
        pass
