import io
import json
from typing import Union

import discord
from discord.ext import commands

from bot.bot import CustomBot
from bot.converters.arguments import EmbedDataConverter, UniversalMessageConverter


class EmbedCog(commands.Cog):

    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.__cog_name__ = 'Embed Commands'

    @commands.command(name='say')
    @commands.is_owner()
    async def _create_embed(self, context, channel: Union[discord.TextChannel, discord.Thread], *, content: str = None):
        # must be put here to convert empty argument uwu
        parsed_content, embeds, parsed = await EmbedDataConverter().convert(context, content)
        message = await channel.send(content=parsed_content, embeds=embeds)
        await context.say_as_embed(
            title='Message sent~',
            description=f'[>>Check it out<<]({message.jump_url} "{message.jump_url}")',
            footer_text=f'JSON was parsed successfully.' if parsed else
            'Failed to parse JSON data. If it\'s supposed to parse, check your data for mistakes.'
        )

    @commands.command(name='edit')
    @commands.is_owner()
    async def _edit_embed(self, context, message: discord.PartialMessage, *, content: str = None):
        parsed_content, embeds, parsed = await EmbedDataConverter().convert(context, content)
        try:
            await message.edit(content=parsed_content, embeds=[embed for embed in embeds])
            await context.say_as_embed(
                title='Message edited~',
                description=f'[>>Check it out<<]({message.jump_url} "{message.jump_url}")',
                footer_text=f'JSON was parsed successfully.' if parsed else
                'Failed to parse JSON data. If it\'s supposed to parse, check your data for mistakes.'
            )
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
            raise commands.BadArgument(e.text if e.text else 'Unknown error.')

    @commands.command(name='mdata')
    @commands.is_owner()
    async def _get_embed_data(self, context, message: UniversalMessageConverter):
        message: discord.Message
        embeds = []
        for embed in message.embeds:
            clean_dict = {}
            for k, v in embed.to_dict().items():
                if k in ['type']:
                    continue
                if k in ['image', 'thumbnail', 'author', 'footer']:
                    for ignored in ['proxy_url', 'proxy_icon_url', 'height', 'width']:
                        try:
                            del v[ignored]
                        except KeyError:
                            continue
                clean_dict[k] = v
            embeds.append(clean_dict)
        data = {
            'content': message.content or None,
            'embeds': embeds if embeds else None
        }
        json_data = json.dumps(data, indent=2, sort_keys=True)
        json_data_io = io.BytesIO(json_data.encode())
        await context.send(file=discord.File(json_data_io, f'{message.id}.json'))


async def setup(bot):
    await bot.add_cog(EmbedCog(bot))
