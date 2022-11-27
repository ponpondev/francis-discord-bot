from .base import OwnerBaseCog
from .logging import OwnerLoggingCog
from ...bot import CustomBot


class OwnerCog(OwnerBaseCog, OwnerLoggingCog):
    def __init__(self, bot: CustomBot):
        self.__cog_name__ = 'Owner Commands'
        super().__init__(bot)
        OwnerLoggingCog.__init__(self, bot)


async def setup(bot):
    await bot.add_cog(OwnerCog(bot))
