import sys

from discord.ext import commands

from bot.bot import CustomBot
from bot.texts.info import RestartInfo


class QuitCommandCog(commands.Cog):
    """Command package to manage bot's runtime"""

    def __init__(self, bot: CustomBot):
        self.bot = bot

    @commands.command(name='restart', aliases=['q'], brief=RestartInfo.brief, help=RestartInfo.help)
    @commands.is_owner()
    async def restart(self, ctx):
        """Restarts the bot and exit the system"""
        await ctx.send('Sayonara, I\'ll be back in 10 seconds~')
        await self.bot.close()
        sys.exit()
