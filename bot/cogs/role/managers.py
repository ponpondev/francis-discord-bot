from django.utils import timezone

from bot.bot import CustomBot
from bot.utils.mixins import CooldownMixin


class RoleManager:
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.interaction_prefix = 'role_btn_'
        self.cooldown = CooldownMixin(threshold=5, amount=timezone.timedelta(seconds=6))
