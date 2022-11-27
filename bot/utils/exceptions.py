import discord


class MyCustomError(Exception):
    def __init__(self, error: str, custom: bool = True):
        self.error = error
        self.custom = custom

    def __str__(self) -> str:
        return self.error


class MyAppCommandError(discord.app_commands.AppCommandError, MyCustomError):
    pass


class MyInteractionError(discord.DiscordException, MyCustomError):
    pass
