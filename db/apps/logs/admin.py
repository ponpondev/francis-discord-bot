from django.contrib import admin
from django.utils.safestring import mark_safe

from db.apps.logs.models import DiscordLog


@admin.register(DiscordLog)
class DiscordLogAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'sent_at',
        'type',
        'action',
        'subject',
        'user_id',
        'user_display_name',
        'user_discriminator',
        '_user_avatar',
        'description_text',
        'before',
        'after',
    )

    list_filter = (
        'type',
        'action',
        'subject',
    )

    search_fields = (
        'user_id',
        'user_display_name',
        'user_discriminator',
    )

    def _user_avatar(self, obj: DiscordLog):
        return mark_safe(f'<img src="{obj.user_display_avatar}" height="35">')
