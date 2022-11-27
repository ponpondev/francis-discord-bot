import discord
from django.db import models
from django.template.defaultfilters import truncatechars

from bot.utils.time import to_timestamp
from bot.utils.ui import MyEmbed


class DiscordLog(models.Model):
    TYPE_CHOICES = (
        ('member', 'Member'),
        ('user', 'User'),
        ('message', 'Message'),
        ('voice', 'Voice'),
        ('reaction', 'Reaction'),
    )
    ACTION_CHOICES = (
        ('update', 'Updated'),
        ('remove', 'Removed'),
        ('ban', 'Banned'),
        ('unban', 'Unbanned'),
        ('join', 'Joined'),
        ('leave', 'Left'),
        ('edit', 'Edited'),
        ('delete', 'Deleted'),
        ('stop', 'Stopped'),
        ('start', 'Started'),
    )
    ACTION_COLORS = {
        'update': discord.Color.dark_blue(),
        'remove': discord.Color.dark_red(),
        'unban': discord.Color.dark_blue(),
        'ban': discord.Color.dark_red(),
        'join': discord.Color.dark_teal(),
        'leave': discord.Color.dark_red(),
        'edit': discord.Color.dark_blue(),
        'delete': discord.Color.dark_red(),
        'start': discord.Color.dark_teal(),
        'stop': discord.Color.dark_red(),
    }
    SUBJECT_CHOICES = (
        # guild-only subjects
        ('nick', 'Nickname'),
        ('roles', 'Roles'),
        ('guild_avatar', 'Server Avatar'),
        # user subjects
        ('name', 'Username'),
        ('discriminator', 'Discriminator'),
        ('avatar', 'Avatar'),
        # message subjects
        ('content', 'Content'),
        ('attachments', 'Attachments'),
        # voice subjects
        ('self_video', 'Screenshare'),
        ('self_stream', 'Livestream'),
        ('channel', 'Channel'),

    )

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, blank=True)
    user_display_name = models.CharField(max_length=32)
    user_discriminator = models.CharField(max_length=4)
    user_display_avatar = models.URLField(max_length=200)
    user_id = models.PositiveBigIntegerField()
    origin = models.CharField(max_length=200, blank=True)
    before = models.TextField(max_length=4096, blank=True)
    after = models.TextField(max_length=4096, blank=True)
    attachment_message_url = models.URLField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Log #{self.id}'

    @property
    def author_text(self):
        return f'{self.user_display_name}#{self.user_discriminator}'

    @property
    def before_text(self):
        return self._format_content(self.before)

    @property
    def after_text(self):
        return self._format_content(self.after)

    @property
    def title_text(self):
        return f'{self.get_type_display()} {self.get_subject_display()} {self.get_action_display()}'.replace('  ', ' ')

    @property
    def description_text(self):
        if self.action == 'ban':
            desc = f'**Reason:** {self.before or self.after or "N/A"}'
        elif self.subject in ['avatar', 'guild_avatar'] or self.action in ['unban']:
            desc = f'<@{self.user_id}>'
        elif self.before and self.after or self.subject in ['nick', 'content', 'roles']:
            if self.subject in ['content']:
                desc = f'**Before**\n{self.before_text}\n**After**\n{self.after_text}'
            else:
                desc = f'`Before:` {self.before_text}\n' \
                       f'`After :` {self.after_text}'

        elif self.before:
            desc = self.before_text
        elif self.after:
            desc = self.after_text
        else:
            desc = 'N/A'
        return desc

    def origin_text(self):
        if self.origin.startswith('https'):
            return f'[Jump to Origin]({self.origin})'
        else:
            return f'<#{self.origin}>'

    def extra_text(self):
        ts = to_timestamp(self.created_at)
        text = f'• Log ID: {self.id}' \
               f'\n• Logged on: **<t:{ts}:D> <t:{ts}:T>**'
        if self.origin:
            text += f'\n• Origin: {self.origin_text()}'
        if self.attachment_message_url:
            text += f'\n• Attachments: [Click here]({self.attachment_message_url})'
        return text

    def create_embed(self):
        embed = MyEmbed(
            title=self.title_text,
            description=self.description_text,
            color=self.ACTION_COLORS[self.action]
        )
        embed.set_author(
            name=self.author_text,
            icon_url=self.user_display_avatar
        )
        embed.add_field(
            name='Additional Info',
            value=self.extra_text(),
            inline=False
        )
        embed.set_footer(
            text=self.user_id
        )
        if self.subject in ['avatar', 'guild_avatar']:
            embed.set_thumbnail(url=self.after or self.user_display_avatar)
        return embed

    def _format_content(self, content):
        if not content:
            return '*Empty*'
        if self.subject in ['nick', 'name', 'discriminator']:
            return f'`{content}`'
        return truncatechars(content, 2000)
