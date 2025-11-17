from discord.ext import commands

from bot.bot import CustomBot
from bot.utils.ui import MyEmbed


class OwnerListenersCog(commands.Cog):

    def __init__(self, bot: CustomBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, context, error):
        # missing required argument of a non-help command
        if isinstance(error, commands.MissingRequiredArgument) and context.command.qualified_name != 'help':
            if context.command.parent:
                command_name = f'{context.command.parent.name} {context.invoked_with}'
            else:
                command_name = context.invoked_with

            _format = dict(command_name=command_name, prefix=context.prefix)

            if isinstance(context.command, commands.Group):
                _format['subcommands'] = '\n'.join(
                    [
                        f'{subcommand.name:<10}: {subcommand.brief}'
                        for subcommand in context.command.commands
                    ]
                )

            await context.send(
                embed=MyEmbed(
                    title=f'How to use the `{command_name}` command',
                    description=context.command.help.format(**_format),
                )
            )
