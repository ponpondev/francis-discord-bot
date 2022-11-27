from typing import Union, List, Literal

import discord.utils
from asgiref.sync import sync_to_async
from discord.ext import commands

from bot.bot import CustomBot
from bot.conf import bot_conf
from bot.utils.time import to_timestamp
from bot.utils.ui import MyEmbed
from db.apps.logs.models import DiscordLog


class LogListenerCog(commands.Cog):

    def __init__(self, bot: CustomBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not self._loggable(user_id=member.id, guild_id=member.guild.id):
            return
        ts = to_timestamp(member.created_at)
        after = f'Account created: <t:{ts}:R> (<t:{ts}:f>)'
        await self._record_log(
            _type='member',
            action='join',
            user=member,
            after=after
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not self._loggable(user_id=member.id, guild_id=member.guild.id):
            return
        after = ''
        if member.joined_at:
            ts = to_timestamp(member.joined_at)
            after += f'\nJoined: <t:{ts}:R> (<t:{ts}:f>)'
        role_txt = ' '.join(f'<@&{role.id}>' for role in member.roles if role.name != '@everyone')
        if role_txt:
            after += f'\nRoles: {role_txt}'

        await self._record_log(
            _type='member',
            action='leave',
            user=member,
            after=after
        )

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: Union[discord.User, discord.Member]):
        if not self._loggable(user_id=user.id, guild_id=guild.id):
            return
        ban_entry = await guild.fetch_ban(user)
        await self._record_log(
            _type='member',
            action='ban',
            user=user,
            after=ban_entry.reason or 'Not provided'
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: Union[discord.User, discord.Member]):
        if not self._loggable(user_id=user.id, guild_id=guild.id):
            return
        await self._record_log(
            _type='member',
            action='unban',
            user=user,
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not self._loggable(
                user_id=before.author.id if before.author else None,
                guild_id=before.guild.id if before.guild else None,
                channel_id=before.channel.id if before.channel else None
        ):
            return
        await self._record_log(
            _type='message',
            action='edit',
            user=before.author,
            before=before,
            after=after,
            origin=before.jump_url,
            subjects=['content']
        )

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        # special case
        if not payload.cached_message or not payload.cached_message.attachments:
            return
        if not self._loggable(user_id=payload.cached_message.author.id, guild_id=payload.guild_id, channel_id=payload.channel_id):
            return
        # content unchanged means attachment edit
        if payload.data.get('content') != payload.cached_message.content:
            return

        try:
            reuploaded = await self.log_attachments(payload.cached_message, message_delete=False)
            attachment_message_url = reuploaded.jump_url if reuploaded else ''
        except discord.HTTPException as e:
            att_info = ' | '.join(f'{att.filename} ({att.size})' for att in payload.cached_message.attachments)
            self.bot.logger.error(f'Unable to upload file(s). File info: {att_info}. Error: {e}.')
            attachment_message_url = ''

        await self._record_log(
            _type='message',
            action='edit',
            user=payload.cached_message.author,
            before=payload.cached_message,
            after=payload.cached_message,
            origin=payload.cached_message.jump_url,
            subjects=['attachments'],
            attachment_message_url=attachment_message_url,
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):

        if not self._loggable(user_id=message.author.id, guild_id=message.guild.id, channel_id=message.channel.id):
            return

        try:
            reuploaded = await self.log_attachments(message, message_delete=True)
            attachment_message_url = reuploaded.jump_url if reuploaded else ''
        except discord.HTTPException as e:
            att_info = ' | '.join(f'{att.filename} ({att.size})' for att in message.attachments)
            self.bot.logger.error(f'Unable to upload file(s). File info: {att_info}. Error: {e}.')
            attachment_message_url = ''

        await self._record_log(
            _type='message',
            action='delete',
            user=message.author,
            after=discord.utils.escape_markdown(text=message.content),
            attachment_message_url=attachment_message_url,
            origin=message.channel.id
        )

    def _loggable(
            self,
            user_id: int,
            guild_id: int,
            channel_id: int = None):
        if not bot_conf.LOG_ON:
            return False
        if not self.bot.is_ready():
            return False
        if not guild_id:
            return False
        # only work in ALLOWED_GUILDS
        if guild_id not in bot_conf.ALLOWED_GUILDS:
            return False
        if user_id == self.bot.user.id:
            return False
        return True

    @sync_to_async
    def _record_log(
            self,
            _type: Literal['member', 'user', 'message', 'voice', 'reaction'],
            action: Literal['update', 'remove', 'ban', 'unban', 'join', 'leave', 'edit', 'delete', 'stop', 'start'],
            user: Union[discord.User, discord.Member],
            before: Union[str, discord.VoiceState] = '',
            after: Union[str, discord.VoiceState] = '',
            subjects: List[str] = None,
            origin: Union[str, int] = '',
            attachment_message_url: str = '',
    ):

        # no subjects
        if not subjects:
            DiscordLog.objects.create(
                type=_type,
                action=action,
                before=before,
                after=after,
                user_id=user.id,
                user_display_avatar=user.display_avatar,
                user_display_name=user.display_name,
                user_discriminator=user.discriminator,
                attachment_message_url=attachment_message_url,
                origin=origin
            )
            return

        for subject in subjects:
            if (_b := getattr(before, subject)) != (_a := getattr(after, subject)):
                # parse before and after
                if subject == 'roles':
                    _b = ' '.join(f'<@&{role.id}>' for role in _b if role.name != '@everyone')
                    _a = ' '.join(f'<@&{role.id}>' for role in _a if role.name != '@everyone')
                DiscordLog.objects.create(
                    type=_type,
                    action=action,
                    subject=subject,
                    before=_b or '', after=_a or '',
                    user_id=user.id,
                    user_display_avatar=user.display_avatar,
                    user_display_name=user.display_name,
                    user_discriminator=user.discriminator,
                    origin=origin
                )
            # attachment edit is special case because on_message_edit doesn't trigger
            elif subject == 'attachments':
                _b = getattr(before, 'content', '')
                _a = getattr(after, 'content', '')

                DiscordLog.objects.create(
                    type=_type,
                    action=action,
                    subject=subject,
                    before=_b or '', after=_a or '',
                    user_id=user.id,
                    user_display_avatar=user.display_avatar,
                    user_display_name=user.display_name,
                    user_discriminator=user.discriminator,
                    origin=origin,
                    attachment_message_url=attachment_message_url,
                )

    async def log_attachments(self, message: discord.Message, message_delete: bool = True):
        if not message.attachments:
            return None
        embed = MyEmbed(
            title=f'Message content',
            description=discord.utils.escape_markdown(message.content) or 'N/A'
        )
        embed.set_author(
            name=f'{message.author.display_name}#{message.author.discriminator}',
            icon_url=message.author.display_avatar.url
        )
        ts = to_timestamp(message.created_at)
        embed.add_field(
            name='Additional Info',
            value=f'• Logged on: **<t:{ts}:D> <t:{ts}:T>**\n'
                  f'• Origin: {message.channel.mention if message_delete else f"[Jump to Origin]({message.jump_url})"}',
        )
        embed.set_footer(text=message.author.id)
        files = []
        for att in message.attachments:
            try:
                f = await att.to_file()
            except discord.NotFound:
                f = await att.to_file(use_cached=True)
            files.append(f)
        return await self.bot.channels.images.send(embed=embed, files=files)
