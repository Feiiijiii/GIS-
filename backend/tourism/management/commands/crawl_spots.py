from django.core.management.base import BaseCommand
from tourism.scraper import SimpleSpotScraper

class Command(BaseCommand):
    help = '从携程网爬取成都景点数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=40,
            help='要爬取的页数'
        )

    def handle(self, *args, **options):
        self.stdout.write('开始爬取景点数据...')
        try:
            scraper = SimpleSpotScraper()
            pages = options['pages']
            self.stdout.write(f'将爬取 {pages} 页数据')
            scraper.scrape(pages)
            self.stdout.write(self.style.SUCCESS('爬取完成！'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'爬取失败: {str(e)}')) 