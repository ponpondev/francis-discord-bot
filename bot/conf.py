import json
import re

from django.conf import settings

fp = f'{settings.BOT_DIR}/configs.json'


class DiscordBotSettings:
    with open(fp, 'r') as configfile:
        conf = json.load(configfile)
    # bot
    DEBUG = conf.get('DEBUG', False)
    PREFIX = conf.get('PREFIX', '!')
    ALLOWED_GUILDS = conf.get('ALLOWED_GUILDS', [])
    EMBED_DEFAULT_COLOR = conf.get('EMBED_DEFAULT_COLOR', 0xf900e5)
    IMAGE_LIST_CHANNEL = conf['IMAGE_LIST_CHANNEL']

    # log config
    LOG_ON = conf['LOG_ON']
    LOG_MESSAGE_CHANNEL = conf['LOG_MESSAGE_CHANNEL']
    # role
    SELF_ASSIGN_ROLES = conf.get('SELF_ASSIGN_ROLES', [])

    # can be generated from dir(settings)
    __attributes__ = [
        'DEBUG',
        'SELF_ASSIGN_ROLES',
        'ALLOWED_GUILDS',
        'EMBED_DEFAULT_COLOR',
        'IMAGE_LIST_CHANNEL',
        'PREFIX',
        'LOG_MESSAGE_CHANNEL',
        'LOG_ON',
    ]

    __channels__ = [
        'IMAGE_LIST_CHANNEL',
        'LOG_MESSAGE_CHANNEL'
    ]

    __booleans__ = [
        'DEBUG', 'LOG_ON',
    ]

    __lists__ = [
        'SELF_ASSIGN_ROLES',
        'ALLOWED_GUILDS',
    ]

    __hexes__ = [
        'EMBED_DEFAULT_COLOR',
    ]

    __strs__ = [
        'PREFIX',
    ]

    __ints__ = [
        'IMAGE_LIST_CHANNEL', 'LOG_MESSAGE_CHANNEL',
    ]

    __floats__ = [
    ]

    __bot__ = [
        'PREFIX', 'EMBED_DEFAULT_COLOR', 'DEBUG',
        'ALLOWED_GUILDS', 'IMAGE_LIST_CHANNEL',
    ]

    __log__ = [
        'LOG_ON', 'LOG_MESSAGE_CHANNEL',
    ]

    __role__ = [
        'SELF_ASSIGN_ROLES'
    ]

    def to_dict(self):
        return {key: getattr(self, key) for key in self.__attributes__}

    def save(self):
        with open(fp, 'w') as configfile:
            json.dump(self.to_dict(), configfile, indent=2)

    NUMBER_REGEX = re.compile('\d+')

    @classmethod
    def to_int(cls, text):
        results = cls.NUMBER_REGEX.findall(text)
        if not results:
            return None
        return int(results[0])

    @classmethod
    def to_float(cls, text):
        try:
            return float(text)
        except ValueError:
            return None

    @classmethod
    def to_bool(cls, text):
        return text.strip().lower() == 'true'

    @classmethod
    def hex_to_int(cls, text):
        try:
            return int(text, 16)
        except ValueError:
            return None

    @classmethod
    def process_value(cls, conf_attr, original_value):
        value = original_value
        # parse value
        if conf_attr in cls.__ints__:
            value = cls.to_int(original_value)
        elif conf_attr in cls.__hexes__:
            value = cls.hex_to_int(original_value)
        elif conf_attr in cls.__booleans__:
            value = cls.to_bool(original_value)
        elif conf_attr in cls.__floats__:
            value = cls.to_float(original_value)
        elif conf_attr in cls.__lists__:
            # convert to channel IDs
            _val = []
            for _id in re.split('\s+', original_value):
                _id = cls.to_int(_id)
                if _id:
                    _val.append(_id)
            value = _val
        return value

    @classmethod
    def process_preview(cls, conf_attr, value):
        preview = ''
        if conf_attr == 'ALLOWED_GUILDS':
            preview = 'Not Available'
        elif conf_attr in cls.__lists__:
            if 'CHANNEL' in conf_attr:
                prefix, suffix = '<#', '>'
            elif 'ROLE' in conf_attr:
                prefix, suffix = '<@&', '>'
            else:
                prefix, suffix = '', ''
            preview = ' '.join(f"{prefix}{item}{suffix}" for item in value)
        elif 'CHANNEL' in conf_attr:
            preview = f'<#{value}>'
        elif 'ROLE' in conf_attr:
            preview = f'<@&{value}>'
        elif 'EMOJI' in conf_attr:
            preview = value
        return preview


bot_conf = DiscordBotSettings()
