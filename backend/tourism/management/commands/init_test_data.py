from django.core.management.base import BaseCommand
from tourism.models import ScenicSpot

class Command(BaseCommand):
    help = '初始化测试用的景点数据'

    def handle(self, *args, **options):
        # 清空现有数据
        ScenicSpot.objects.all().delete()
        
        # 测试数据
        test_spots = [
            {
                'name': '宽窄巷子',
                'longitude': 104.0621,
                'latitude': 30.6737,
                'description': '成都著名的历史文化街区，由宽巷子、窄巷子和井巷子组成，是清朝时期的老成都缩影。',
                'category': '历史文化',
                'address': '成都市青羊区宽窄巷子',
                'opening_hours': '全天开放',
                'ticket_price': 0.0,
                'images': ['https://pic3.zhimg.com/80/v2-8fa1772a13e3f0f3f8f2a1e7273a1d16_720w.webp']
            },
            {
                'name': '锦里古街',
                'longitude': 104.0428,
                'latitude': 30.6429,
                'description': '锦里古街是成都武侯祠博物馆的一部分，是一条仿古商业街，以三国文化和成都民俗为主题。',
                'category': '历史文化',
                'address': '成都市武侯区武侯祠大街231号',
                'opening_hours': '10:00-22:00',
                'ticket_price': 0.0,
                'images': ['https://pic1.zhimg.com/80/v2-c8e2d8da3a8c4f528ac3b9e7d8f7d67c_720w.webp']
            },
            {
                'name': '都江堰',
                'longitude': 103.6193,
                'latitude': 31.0040,
                'description': '世界文化遗产，全国重点文物保护单位，是中国古代建设的大型水利工程。',
                'category': '历史文化',
                'address': '成都市都江堰市都江堰景区',
                'opening_hours': '08:00-18:00',
                'ticket_price': 90.0,
                'images': ['https://youimg1.c-ctrip.com/target/100h0z000000nk7zy9A7F.jpg']
            }
        ]
        
        for spot_data in test_spots:
            try:
                ScenicSpot.objects.create(**spot_data)
                self.stdout.write(self.style.SUCCESS(f'成功创建景点: {spot_data["name"]}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'创建景点失败 {spot_data["name"]}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('测试数据初始化完成')) 