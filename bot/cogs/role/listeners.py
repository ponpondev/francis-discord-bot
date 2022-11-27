import discord
from discord.ext import commands

from bot.bot import CustomBot
from bot.conf import bot_conf
from bot.utils.exceptions import MyInteractionError
from bot.utils.time import to_timestamp
from bot.utils.ui import MyEmbed
from .managers import RoleManager


class RoleListenerCog(commands.Cog):

    def __init__(self, bot: CustomBot, manager: RoleManager):
        self.bot = bot
        self.manager = manager

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # nothing's ready yet
        if not self.bot.is_ready():
            return
        if not interaction.guild:
            return
        # get the custom interaction ID
        iid: str = interaction.data.get('custom_id', '')
        # not the desired interaction prefix
        if not iid.startswith(self.manager.interaction_prefix):
            return
        # get the role ID
        role_id = int(iid.replace(self.manager.interaction_prefix, ''))
        # check against assignable role list
        if role_id not in bot_conf.SELF_ASSIGN_ROLES:
            raise MyInteractionError(f'<@&{role_id}> is no longer assignable.')

        if interaction.guild not in self.bot.working_guilds:
            raise MyInteractionError(f'This server cannot use this feature.')

        role_obj = interaction.guild.get_role(role_id)
        if not role_obj:
            raise MyInteractionError(f'Role with ID `{role_id}` does not exist.')
        # convert user into the server member
        member_obj = interaction.guild.get_member(interaction.user.id)
        if not member_obj:
            raise MyInteractionError(f'You\'re not a member of the server.')

        # cooldown checking
        can_proceed = self.manager.cooldown.check()
        if not can_proceed:
            raise MyInteractionError(
                f'Too many roles are being given right now. Please try again {to_timestamp(self.manager.cooldown.until, "R")}.'
            )

        # role already exists
        if role_obj in member_obj.roles:
            await member_obj.remove_roles(role_obj)
            message = f'The {role_obj.mention} role has been removed from you.'
        # role not exist
        else:
            # add the role
            await member_obj.add_roles(role_obj)
            message = f'The {role_obj.mention} role has been given to you.'

        # respond to the interaction
        await interaction.response.send_message(
            embed=MyEmbed(description=message),
            ephemeral=True
        )
