import discord

from bot.bot import CustomBot


# runtime
def run(prefix, token, initial_extensions):
    def get_prefix(_bot, msg):
        return prefix

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    bot = CustomBot(
        initial_extensions=initial_extensions,
        command_prefix=get_prefix,
        intents=intents,
        max_messages=1000
    )
    # remove the 'help' command
    bot.remove_command('help')

    # app command error handler
    bot.tree.on_error = bot.on_app_command_error

    bot.run(token)
