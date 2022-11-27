import re

from discord.ext import commands


class HelpCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = 'Help Commands'

    @commands.command(name='help')
    @commands.is_owner()
    async def _help_message(self, context, *, args: str):
        cmd_list = re.split('\s+', args, maxsplit=1)
        # support only up to 1 level deep of subcommands
        if len(cmd_list) == 1:
            cmd_name = cmd_list[0]
            group_obj = None
            command_obj = context.bot.get_command(cmd_name)
            is_sub = False
        else:
            cmd_name = f'{cmd_list[0]} {cmd_list[1]}'
            group_obj = context.bot.get_command(cmd_list[0])
            command_obj = group_obj.get_command(cmd_list[1]) if group_obj else None
            is_sub = True

        # no command or cannot be run
        try:
            if not command_obj:
                raise commands.CommandError('Command not found.')
            # verify on group level if it's a subcommand
            if is_sub and group_obj:
                if not await group_obj.can_run(context):
                    raise commands.CommandError('Nope.')
            # otherwise verify the command/group itself
            else:
                if not await command_obj.can_run(context):
                    raise commands.CommandError('Nope.')
        except commands.CommandError:
            await context.say_as_embed(
                f'There are no commands named `{args}`.', color='error')
            return

        if not command_obj.help:
            message = 'No further help information provided.'
        else:
            if isinstance(command_obj, commands.Group):
                subcommands = '\n'.join([
                    f'{subcommand.name:<10}: {subcommand.brief}'
                    for subcommand in command_obj.commands
                ])
                _format = dict(command_name=cmd_name, prefix=context.prefix, subcommands=subcommands)
            else:
                _format = dict(command_name=cmd_name, prefix=context.prefix)
            message = command_obj.help.format(**_format)
        await context.say_as_embed(message)

    @_help_message.error
    async def _error_handler(self, context, error):

        if isinstance(error, commands.MissingRequiredArgument):

            available_commands_txt = ''
            for cog_name, cog in context.bot.cogs.items():
                cog_commands_txt = ''
                for c in cog.get_commands():
                    # ignores if hidden
                    if c.hidden:
                        continue
                    # ignore all commands that user cannot run
                    try:
                        if not await c.can_run(context):
                            continue
                    except commands.CommandError:
                        continue

                    command_brief = c.brief if c.brief else '-'
                    cog_commands_txt += f'• {c.qualified_name:<10} : {command_brief}\n'
                if cog_commands_txt:
                    available_commands_txt += f'{cog.qualified_name}\n{cog_commands_txt}\n'

            await context.say_as_embed(
                title='List of available commands',
                description=
                f'Prefix: `{context.prefix}`\n'
                f'```\n{available_commands_txt}```\n'
                f'Type `{context.prefix}{context.invoked_with} [command name]`'
                f' for more details on the command.\n\n'
                f'Please contact a mod if you have any questions.')


async def setup(bot):
    await bot.add_cog(HelpCommands(bot))
