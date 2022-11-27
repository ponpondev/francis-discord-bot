from .commands import RoleCommandCog
from .listeners import RoleListenerCog
from .managers import RoleManager
from ...bot import CustomBot


class RoleCog(RoleCommandCog):
    def __init__(self, bot: CustomBot, manager: RoleManager):
        super().__init__(bot, manager)


async def setup(bot):
    manager = RoleManager(bot)
    await bot.add_cog(RoleCog(bot, manager=manager))
    await bot.add_cog(RoleListenerCog(bot, manager=manager))
