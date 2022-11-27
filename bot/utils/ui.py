import discord

from bot.conf import bot_conf


class MyEmbed(discord.Embed):
    def __init__(self, **kwargs):
        footer_text = kwargs.pop('footer_text', None)
        footer_url = kwargs.pop('footer_url', None)
        thumbnail_url = kwargs.pop('thumbnail_url', None)
        image_url = kwargs.pop('image_url', None)
        fields = kwargs.pop('fields', [])

        # quick select for colors
        color = kwargs.pop('color', None)
        if color == 'info':
            kwargs['color'] = discord.Color.teal()
        elif color == 'warning':
            kwargs['color'] = discord.Color.gold()
        elif color == 'error':
            kwargs['color'] = discord.Color.red()
        elif color == 'success':
            kwargs['color'] = discord.Color.green()
        elif isinstance(color, (discord.Color, int)):
            kwargs['color'] = color
        else:
            kwargs['color'] = bot_conf.EMBED_DEFAULT_COLOR

        super().__init__(**kwargs)

        if footer_text:
            self.set_footer(text=footer_text, icon_url=footer_url)
        if thumbnail_url:
            self.set_thumbnail(url=thumbnail_url)
        if image_url:
            self.set_image(url=image_url)
        for field in fields:
            self.add_field(**field)

class MyView(discord.ui.View):
    def __init__(self, **kwargs):
        items = kwargs.pop('items', [])
        super().__init__(**kwargs)
        for item in items:
            self.add_item(item)
