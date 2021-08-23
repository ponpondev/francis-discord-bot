# from pprint import pprint
# import json

import discord
from discord.ext import commands

from francis.bot import CustomBot
from web.apps.roles.models import DiscordRoleAssign


class GenshinAdmin(commands.Cog):
    """A cog for GenshinAdmin-only commands"""

    def __init__(self, bot: CustomBot):
        self.bot = bot

    @commands.command(name='addgirole', hidden=True)
    @commands.is_owner()
    async def _add_genshin_role_react(self, context, role: discord.Role, emoji: discord.Emoji):
        assign_obj, _ = DiscordRoleAssign.objects.update_or_create(
            role_id=role.id, defaults={'emoji_id': emoji.id, 'name': emoji.name}
        )
        self.bot.load_genshin_role_react()
        await context.say_as_embed(f'{role.mention} is added as reaction role when reacting to {emoji}.')

    @commands.command(name='rmgirole', hidden=True)
    @commands.is_owner()
    async def _remove_genshin_role_react(self, context, role: discord.Role):
        del_count, del_objs = DiscordRoleAssign.objects.filter(role_id=role.id).delete()
        self.bot.load_genshin_role_react()
        await context.say_as_embed(f'{del_count} entries with {role.mention} have been removed.')


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def setup(bot):
    bot.add_cog(GenshinAdmin(bot))
