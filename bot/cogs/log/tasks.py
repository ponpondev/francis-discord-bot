from typing import List

import discord
from asgiref.sync import sync_to_async
from discord.ext import commands, tasks
from django.utils import timezone

from bot.bot import CustomBot
from bot.conf import bot_conf
from db.apps.logs.models import DiscordLog


class RelayDiscordLogCog(commands.Cog):

    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.relay_message_logs.start()
        self.clear_logs.start()

    async def cog_unload(self):
        self.relay_message_logs.cancel()
        self.clear_logs.cancel()

    @tasks.loop(seconds=5)
    async def relay_message_logs(self):
        if not bot_conf.LOG_ON:
            return
        logs = await self._get_discord_logs('message', 'reaction')
        await self._process_logs(logs, self.bot.channels.log_message)

    async def _process_logs(self, logs: List[DiscordLog], destination_channel: discord.TextChannel):
        if not logs:
            return
        embeds = []
        now = timezone.now()
        for log in logs:
            embed = log.create_embed()
            log.sent_at = now
            embeds.append(embed)
        await destination_channel.send(embeds=embeds)
        await sync_to_async(DiscordLog.objects.bulk_update)(logs, fields=['sent_at'], batch_size=10)

    @sync_to_async
    def _get_discord_logs(self, *type) -> List[DiscordLog]:
        # fetch earliest 10 warns
        logs = DiscordLog.objects.filter(sent_at__isnull=True, type__in=type)[:10]
        return list(logs)

    @tasks.loop(seconds=10)
    async def clear_logs(self):
        if not bot_conf.LOG_ON:
            return
        await self._clear_clearable_logs()

    @sync_to_async
    def _clear_clearable_logs(self):
        one_month_old = timezone.now() - timezone.timedelta(days=30)
        DiscordLog.objects.filter(sent_at__isnull=False, created_at__lt=one_month_old).delete()

    @relay_message_logs.before_loop
    async def before_looping_task(self):
        self.bot.logger.info('[Relay Discord Logs] Waiting for bot ready...')
        await self.bot.wait_until_ready()
        self.bot.logger.info('[Relay Discord Logs] Ready and running!')

    @clear_logs.before_loop
    async def _before_looping_task(self):
        await self.bot.wait_until_ready()
