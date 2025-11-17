from .commands import OwnerBaseCog
from .logging import OwnerLoggingCog
from .listeners import OwnerListenersCog
from ...bot import CustomBot


class OwnerCog(OwnerBaseCog, OwnerLoggingCog):
    def __init__(self, bot: CustomBot):
        self.__cog_name__ = 'Owner Commands'
        super().__init__(bot)
        OwnerLoggingCog.__init__(self, bot)


async def setup(bot):
    await bot.add_cog(OwnerCog(bot))
    await bot.add_cog(OwnerListenersCog(bot))
