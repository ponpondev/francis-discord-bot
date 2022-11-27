import json
import re
from inspect import Parameter

import discord
from discord.ext import commands
from discord.ext.commands import PartialMessageConverter

from bot.conf import bot_conf

sub_command = Parameter(name='subcommand', kind=Parameter.POSITIONAL_ONLY)


class EmbedDataConverter(commands.Converter):
    async def convert(self, context, argument):
        if not argument:
            attachments = context.message.attachments
            if not attachments:
                raise commands.BadArgument('No attachments found.')

            file: discord.Attachment = attachments[0]
            # try to convert .txt too!
            if all(mime not in file.content_type for mime in ['application/json', 'text/plain']):
                raise commands.BadArgument('Attached file is not a JSON-like file.')

            try:
                bytes_data = await file.read()
            except (discord.HTTPException, discord.Forbidden, discord.NotFound) as e:
                raise commands.BadArgument(e.text if e.text else 'Unknown error.')
            try:
                bytes_data = bytes_data.decode('utf-8')
                message_data = json.loads(bytes_data, strict=False)
                parsed = True
            except json.JSONDecodeError as e:
                raise commands.BadArgument('**Failed to parse the supplied JSON file**\n'
                                           f'Error(s): `{e.msg if e.msg else "Unknown"}`.')
        else:
            try:
                message_data = json.loads(argument, strict=False)
                # forced parsing of int and float
                if isinstance(message_data, (int, float)):
                    message_data = {'content': argument}
                parsed = True
            except json.JSONDecodeError:
                message_data = {'content': argument}
                parsed = False

        embeds_data = message_data.pop('embeds', None) or []
        embeds = []
        for embed_data in embeds_data:
            embed_data['color'] = embed_data.get('color', None) or bot_conf.EMBED_DEFAULT_COLOR
            embeds.append(discord.Embed.from_dict(embed_data))

        content = message_data.pop('content', None)
        if not content and not embeds:
            message_data['color'] = message_data.get('color', None) or bot_conf.EMBED_DEFAULT_COLOR
            embeds.append(discord.Embed.from_dict(message_data))

        return content, embeds, parsed


class ButtonRoleConverter(commands.Converter):
    async def convert(self, context, argument):
        data = re.split('\s+', argument, maxsplit=2)
        if len(data) != 3:
            raise commands.BadArgument('A button needs: **a role**, **an emoji** (that bot can see), and **label** (text).')
        role_text, emoji_text, label = data

        try:
            role = await commands.RoleConverter().convert(context, role_text)
        except discord.HTTPException as e:
            raise commands.BadArgument(str(e))

        if role.id not in bot_conf.SELF_ASSIGN_ROLES:
            raise commands.BadArgument(f'{role.mention} is not self-assignable. Check `SELF_ASSIGN_ROLES` settings.')

        emoji = discord.PartialEmoji.from_str(emoji_text)

        return role, emoji, label


class UniversalMessageConverter(commands.MessageConverter):
    """
    A Message converter that tries to fetch message in an archived thread also.
    """

    async def convert(self, context, argument):
        try:
            message = await super().convert(context, argument)
            return message
        except commands.ChannelNotFound as e:
            guild_id, message_id, channel_id = PartialMessageConverter._get_id_matches(context, argument)
            try:
                channel = await context.bot.fetch_channel(channel_id)
                return await channel.fetch_message(message_id)
            except commands.ChannelNotFound:
                raise commands.BadArgument(*e.argument)
