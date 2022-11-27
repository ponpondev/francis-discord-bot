from bot.bot import CustomBot
from bot.cogs.runtime.config import ConfigCommandCog
from bot.cogs.runtime.quit import QuitCommandCog


class RuntimeCog(ConfigCommandCog, QuitCommandCog):
    """Command package to manage bot's runtime"""

    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.__cog_name__ = 'Runtime Commands'
        super().__init__(bot)


async def setup(bot):
    await bot.add_cog(RuntimeCog(bot))
