from typing import Union, List, Tuple

import discord
from discord.ext import commands
from discord.ext.commands import Greedy

from bot.bot import CustomBot
from bot.converters.arguments import EmbedDataConverter, ButtonRoleConverter
from bot.utils.ui import MyView
from .managers import RoleManager
from ...texts.info import ButtonRolesInfo


class RoleCommandCog(commands.Cog):

    def __init__(self, bot: CustomBot, manager: RoleManager):
        self.__cog_name__ = 'Role Commands'
        self.bot = bot
        self.manager = manager

    @commands.command(name='buttonroles', brief=ButtonRolesInfo.brief, help=ButtonRolesInfo.help)
    @commands.is_owner()
    async def _button_roles_message(
            self, context,
            channel: Union[discord.TextChannel, discord.Thread],
            button_datas: Greedy[ButtonRoleConverter],
            *, content: str = None):

        if not button_datas:
            raise commands.BadArgument('No buttons to create. Check `SELF_ASSIGN_ROLES` config option.')

        # must be put here to convert empty argument uwu
        parsed_content, embeds, parsed = await EmbedDataConverter().convert(context, content)
        # noinspection PyTypeChecker
        view = MyView(items=self._create_role_buttons(button_datas))
        message = await channel.send(content=parsed_content, embeds=embeds, view=view)
        await context.say_as_embed(
            title='Message sent~',
            description=f'[>>Check it out<<]({message.jump_url} "{message.jump_url}")',
            footer_text=f'JSON was parsed successfully.' if parsed else
            'Failed to parse JSON data. If it\'s supposed to parse, check your data for mistakes.'
        )

    def _create_role_buttons(self, button_datas: List[Tuple[discord.Role, discord.PartialEmoji, str]]):
        return [
            discord.ui.Button(
                label=label,
                emoji=emoji,
                custom_id=f'{self.manager.interaction_prefix}{role.id}'
            )
            for role, emoji, label in button_datas
        ]
