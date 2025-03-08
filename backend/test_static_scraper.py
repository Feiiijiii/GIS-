"""
成都景点静态数据测试脚本
使用高德地图POI搜索API获取景点信息并保存到数据库
"""

import json
import logging
import sys
import os
import requests
import time
from pathlib import Path

# 设置Django环境
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from tourism.models import ScenicSpot
from django.contrib.gis.geos import Point

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("static_scraper_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('static_scraper_test')

def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / 'config.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

class AmapSpotScraper:
    def __init__(self):
        # 优先从环境变量获取API密钥
        self.amap_key = os.getenv('AMAP_KEY')
        
        # 如果环境变量中没有，则从配置文件获取
        if not self.amap_key:
            config = load_config()
            self.amap_key = config.get('amap_key')
            
        if not self.amap_key:
            raise ValueError("请设置高德地图API密钥！可以通过环境变量AMAP_KEY或config.json文件设置。")
            
        self.city = '成都'
        self.keywords = ['景点', '旅游景点', '名胜古迹']
        
    def search_pois(self, keyword, page=1):
        """搜索POI信息"""
        try:
            # 构建POI搜索URL
            url = 'https://restapi.amap.com/v3/place/text'
            params = {
                'key': self.amap_key,
                'keywords': keyword,
                'city': self.city,
                'offset': 20,  # 每页结果数
                'page': page,
                'extensions': 'all'  # 返回详细信息
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data['status'] == '1':
                return data['pois']
            else:
                logger.error(f"POI搜索失败: {data['info']}")
                return []
                
        except Exception as e:
            logger.error(f'POI搜索出错: {str(e)}')
            return []
            
    def get_spots_data(self, max_pages=3):
        """获取所有景点数据"""
        all_spots = []
        
        for keyword in self.keywords:
            logger.info(f"正在搜索关键词: {keyword}")
            
            for page in range(1, max_pages + 1):
                pois = self.search_pois(keyword, page)
                
                for poi in pois:
                    try:
                        # 提取营业时间
                        opening_hours = poi.get('business_hours', ['09:00-17:00'])[0] if poi.get('business_hours') else '09:00-17:00'
                        
                        # 提取经纬度
                        location = poi['location'].split(',')
                        lng, lat = float(location[0]), float(location[1])
                        
                        # 构建景点数据
                        spot_data = {
                            'name': poi['name'],
                            'location_lng': lng,
                            'location_lat': lat,
                            'description': poi.get('tag', ''),
                            'category': poi.get('type', '景点'),
                            'address': poi['address'] if poi.get('address') else poi['pname'] + poi['cityname'] + poi.get('adname', '') + poi.get('address', ''),
                            'opening_hours': opening_hours,
                            'ticket_price': 0.0,  # POI数据中没有票价信息
                            'images': []  # POI数据中没有图片信息
                        }
                        
                        # 检查是否已存在相同名称的景点
                        if not any(spot['name'] == spot_data['name'] for spot in all_spots):
                            all_spots.append(spot_data)
                            logger.info(f"已添加景点: {spot_data['name']}")
                        
                    except Exception as e:
                        logger.error(f'处理POI数据出错: {str(e)}')
                        continue
                
                # 添加延时避免请求过快
                time.sleep(0.5)
                
        logger.info(f"处理完成，共获取 {len(all_spots)} 个景点信息")
        return all_spots

    def save_to_database(self, spots_data):
        """将景点数据保存到数据库"""
        saved_count = 0
        updated_count = 0
        
        for spot in spots_data:
            try:
                # 创建Point对象
                location = Point(spot['location_lng'], spot['location_lat'])
                
                # 检查是否已存在
                existing_spot = ScenicSpot.objects.filter(name=spot['name']).first()
                
                if existing_spot:
                    # 更新现有记录
                    existing_spot.location = location
                    existing_spot.description = spot['description']
                    existing_spot.category = spot['category']
                    existing_spot.address = spot['address']
                    existing_spot.opening_hours = spot['opening_hours']
                    existing_spot.ticket_price = spot['ticket_price']
                    existing_spot.images = spot['images']
                    existing_spot.save()
                    updated_count += 1
                    logger.info(f"更新景点: {spot['name']}")
                else:
                    # 创建新记录
                    ScenicSpot.objects.create(
                        name=spot['name'],
                        location=location,
                        description=spot['description'],
                        category=spot['category'],
                        address=spot['address'],
                        opening_hours=spot['opening_hours'],
                        ticket_price=spot['ticket_price'],
                        images=spot['images']
                    )
                    saved_count += 1
                    logger.info(f"新增景点: {spot['name']}")
                    
            except Exception as e:
                logger.error(f'保存景点 {spot["name"]} 时出错: {str(e)}')
                continue
        
        return saved_count, updated_count

def main():
    """测试景点数据获取和保存"""
    logger.info("开始获取景点数据")
    try:
        scraper = AmapSpotScraper()
        spots_data = scraper.get_spots_data()
        
        if not spots_data:
            logger.warning("未获取到任何景点数据")
            return
            
        logger.info(f"成功获取 {len(spots_data)} 个景点数据")
        
        # 保存到JSON文件
        with open('amap_spots_data.json', 'w', encoding='utf-8') as f:
            json.dump(spots_data, f, ensure_ascii=False, indent=2)
            
        # 保存到数据库
        saved_count, updated_count = scraper.save_to_database(spots_data)
        logger.info(f"数据库操作完成: 新增 {saved_count} 个景点，更新 {updated_count} 个景点")
        
        # 打印前三个景点的信息
        for i, spot in enumerate(spots_data[:3]):
            logger.info(f"景点 {i+1} 信息: {json.dumps(spot, ensure_ascii=False, indent=2)}")
            
    except Exception as e:
        logger.error(f"获取景点数据时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 