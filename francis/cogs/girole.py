import discord
from discord.ext import commands

import config
from francis.bot import CustomBot


class GenshinRole(commands.Cog):

    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.role_channel_id = 759034043810578433

    def _check_valid_reactions(self, payload):
        ponpon_guild = self.bot.get_guild(config.PON_SERVER_ID)
        if not ponpon_guild:
            return False, False

        member = ponpon_guild.get_member(payload.user_id)
        if not member:
            return False, False

        if payload.emoji.id not in self.bot.gi_emoji_to_role:
            return False, False

        if payload.channel_id != self.role_channel_id:
            return False, False

        return ponpon_guild, member

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        ponpon_guild, member = self._check_valid_reactions(payload)
        if not ponpon_guild or not member:
            return

        channel = ponpon_guild.get_channel(payload.channel_id)

        character_role_count = 0
        for member_role in member.roles:
            if member_role.id in self.bot.gi_role_list:
                character_role_count += 1
                if character_role_count >= 4:
                    await channel.send(embed=discord.Embed(
                        title='',
                        description=
                        f'{member.mention}, you can only have up to 4 character roles.\n'
                        f'Try again after unassigning a role by:\n'
                        f'+ removing the respective reaction, or\n'
                        f'+ using command `{self.bot.command_prefix}rrole role_name`',
                        color=discord.Color.dark_red()),
                        delete_after=10
                    )
                    message = await channel.fetch_message(payload.message_id)
                    await message.remove_reaction(payload.emoji, member)
                    return

        role = self.bot.gi_emoji_to_role[payload.emoji.id]
        await member.add_roles(role)

        embed = discord.Embed(
            title='',
            description=
            f'{member.mention} obtained '
            f'{role.mention} role.',
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed, delete_after=5)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        ponpon_guild, member = self._check_valid_reactions(payload)
        if not ponpon_guild or not member:
            return

        role_remove = self.bot.gi_emoji_to_role[payload.emoji.id]
        # do nothing if there's nothing to remove
        if role_remove.id not in [member_role.id for member_role in member.roles]:
            return

        await member.remove_roles(role_remove)

        channel = ponpon_guild.get_channel(payload.channel_id)
        embed = discord.Embed(
            title='',
            description=
            f'{role_remove.mention} role '
            f'has been removed from {member.mention}.',
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed, delete_after=5)


def setup(bot):
    bot.add_cog(GenshinRole(bot))
