# run django for standalone DB and the main bot

if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db.config.settings')
    django.setup()

    from django.conf import settings
    from bot.conf import bot_conf
    from bot.launch import run

    initial_extensions = [
        'bot.cogs.embed',
        'bot.cogs.help',
        'bot.cogs.log',
        'bot.cogs.owner',
        'bot.cogs.role',
        'bot.cogs.runtime',
        'bot.tasks.socials',
        'bot.tasks.crawlers'
    ]
    if bot_conf.DEBUG:
        initial_extensions += [
        ]
    run(bot_conf.PREFIX, settings.DISCORD_BOT_TOKEN, initial_extensions)
