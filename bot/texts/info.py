from bot.conf import bot_conf

CONFIG_CURRENT_VALUE_HINT = '*Current values are bracketed* `[` `]`'

"""OWNER COMMAND INFO"""


class RestartInfo:
    brief = 'Restart the bot.'
    help = (
        'Format:\n```{prefix}{command_name}```\n'
        'Use this command and the bot will be killed and revived in a brief moment.'
    )


class ConfigGroupInfo:
    brief = 'Set various configs for the bot.'
    help = (
        'Format:\n```{prefix}{command_name} <config section> <config name> <config value>```\n'
        'Use this command to set various configuration parameters of the bot. '
        'See below for available `<config section>`s.\n'
        '```{subcommands}```\n'
        'Use `{prefix}help {command_name} <config section>` for detailed explanation of each config section.\n\n'
        'Eg. Use `{prefix}{command_name} bot prefix !` to change bot prefix to `!`\n\n'
        '*Use with care, let me know if things go wrong!*'
    )


class ConfigBotInfo:
    brief = 'Update configs related to bot functionalities.'

    @classmethod
    def help(cls):
        return (
            'Format:\n```{prefix}{command_name} <config name> <config value>```\n'
            'Available config names:\n'
            f'• `PREFIX` - Bot\'s prefix. [`{bot_conf.PREFIX}`]\n'
            '• `EMBED_DEFAULT_COLOR` - Default color of embeds sent by the bot. '
            f'Update this by giving a hex code (eg. `0x00FFFF`). [`{bot_conf.EMBED_DEFAULT_COLOR}`]\n'
            f'• `ALLOWED_GUILDS` - Server IDs the bot can accept some commands. [`{bot_conf.ALLOWED_GUILDS}`]\n'
            f'• `DEBUG` - Debug mode for additional error texts. Spooky. [`{bot_conf.DEBUG}`]\n'
            f'\n'
            f'{CONFIG_CURRENT_VALUE_HINT}\n'
        )


class ConfigLogInfo:
    brief = 'Update Log Module configs.'

    @classmethod
    def help(cls):
        return (
            'Format:\n```{prefix}{command_name} <config name> <config value>```\n'
            'Available config names:\n'
            f'• `LOG_ON` - Turn Log Module on or off. This affects both '
            f'Listeners AND Relayers. [`{bot_conf.LOG_ON}`]\n'
            f'• `LOG_MESSAGE_CHANNEL` - Channel to relay message edit/delete logs. '
            f'[<#{bot_conf.LOG_MESSAGE_CHANNEL}>]\n'
            f'\n'
            f'{CONFIG_CURRENT_VALUE_HINT}\n'
            f' <#{bot_conf.IMAGE_LIST_CHANNEL}> is where images from message logs are stored. '
            'Configurable using `{prefix}conf bot IMAGE_LIST_CHANNEL`'
        )


class ConfigRoleInfo:
    brief = 'Update role configurations.'

    @classmethod
    def help(cls):
        return (
            'Format:\n```{prefix}{command_name} <config name> <config value>```\n'
            'Available config names:\n'
            f'• `SELF_ASSIGN_ROLES` - List of self-assignable roles. '
            f'[{" ".join(f"<@&{role_id}>" for role_id in bot_conf.SELF_ASSIGN_ROLES)}]\n'
            f'\n'
            f'{CONFIG_CURRENT_VALUE_HINT}'
        )


class ButtonRolesInfo:
    brief = 'Create buttons that can give roles.'
    help = (
        'Format:\n```{prefix}{command_name} <channel> <buttons:[role emoji label]...> <content>```\n'
        'Send buttons that can give roles into the destination `<channel>` '
        'with message data specified in `<content>` (or a JSON message data file).\n'
        '`<buttons:[role emoji label]...>` is a list of (`role` `emoji` `label`)s.\n'
        '• The specified `role` must exist in `SELF_ASSIGN_ROLES` bot config.\n'
        '• The bot should be able to see the specified `emoji`.\n'
        '• The `label` is the button\'s label.\n'
        '\n'
        'Example: ```{prefix}{command_name} #somewhere\n'
        '"role_id1 :emoji2: Label Texts Here 1"\n'
        '"role_id2 :emoji2: Label Texts Here 2"\n'
        'Content is here to go with the buttons.'
        '```\n'
        'You can specify up to 25 button roles.'
    )
