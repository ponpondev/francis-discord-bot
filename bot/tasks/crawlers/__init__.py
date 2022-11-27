from discord.ext import tasks, commands

from .genshin import GenshinCrawler
from .gms import GMSCrawler
from .honkai import HonkaiWikiCrawler, HonkaiWebCrawler


class WebCralers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('Initializing [Genshin Crawler: Web API]')
        self.genshin_crawler = GenshinCrawler(bot)
        print('Initializing [Honkai Crawler: Web | Wiki]')
        # self.honkai_wiki_crawler = HonkaiWikiCrawler(bot)
        self.honkai_web_crawler = HonkaiWebCrawler(bot)
        print('Initializing [GMS Crawler: Web]')
        self.gms_crawler = GMSCrawler(bot)
        self.crawl_gms_site.start()
        self.crawl_honkai_site.start()
        self.crawl_genshin_site.start()

    def cog_unload(self):
        self.crawl_gms_site.cancel()
        self.crawl_honkai_site.cancel()
        self.crawl_genshin_site.cancel()

    @tasks.loop(seconds=60.0)
    async def crawl_genshin_site(self):
        await self.genshin_crawler.do_crawl()

    @tasks.loop(seconds=60.0)
    async def crawl_honkai_site(self):
        await self.honkai_web_crawler.do_crawl()

    @tasks.loop(seconds=60.0)
    async def crawl_gms_site(self):
        await self.gms_crawler.do_crawl()

    @crawl_gms_site.before_loop
    async def before_loop(self):
        self.bot.logger.info('[Web Crawlers] Waiting for ready state...')

        await self.bot.wait_until_ready()

        self.bot.logger.info('[Web Crawlers] Ready and running!')

    @crawl_honkai_site.before_loop
    @crawl_genshin_site.before_loop
    async def _before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(WebCralers(bot))
