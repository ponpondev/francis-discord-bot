from django.contrib import admin

from .models import DiscordRoleAssign


@admin.register(DiscordRoleAssign)
class DiscordRoleAssignAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'name',
        'role_id',
        'emoji_id',
    )

    list_editable = (
        'name',
        'role_id',
        'emoji_id',
    )
