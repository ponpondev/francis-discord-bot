from ...bot import CustomBot
from .tasks import RelayDiscordLogCog
from .listeners import LogListenerCog


async def setup(bot: CustomBot):
    await bot.add_cog(LogListenerCog(bot))
    await bot.add_cog(RelayDiscordLogCog(bot))
