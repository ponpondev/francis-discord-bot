from django.db import models


class DiscordRoleAssign(models.Model):
    role_id = models.BigIntegerField()
    emoji_id = models.BigIntegerField()
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = ('role_id', 'emoji_id')

    def __str__(self):
        return self.name
