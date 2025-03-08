import requests
import logging
import os
import sys
import django
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from tourism.models import ScenicSpot
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

# 配置日志
# 在文件开头的日志配置部分
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('tourism_scraper')

# 当直接运行脚本时设置Django环境
def setup_django():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
            logger.info(f"添加目录到Python路径: {backend_dir}")
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()
        logger.info("Django环境初始化完成")
    except Exception as e:
        logger.error(f"Django环境初始化失败: {str(e)}")
        raise

class SimpleSpotScraper:
    # 初始化
    def __init__(self):
        self.base_url = "https://m.ctrip.com/restapi/soa2/18109/json/getAttractionList"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Referer": "https://you.ctrip.com/",
            "Content-Type": "application/json",
            "Cookie": "GUID=09031125217831840516; _bfaStatusPVSend=1; UBT_VID=1741166096005.3tgkx4; Hm_lvt_a8d6737197d542432f4ff4abc6e06384=1741166102; MKT_CKID=1741166102270.kf217.54e3; _RSG=P8qdnLWgKi7FbWEqIt6w_B; _RDG=2814541fd0855a283c2f86fbc3adddc768; _RGUID=7b14aa05-719f-4219-bffa-1b74b43a094f; MKT_Pagesource=PC; _bfaStatus=send; _ubtstatus=%7B%22vid%22%3A%221741166096005.3tgkx4%22%2C%22sid%22%3A2%2C%22pvid%22%3A3%2C%22pid%22%3A600001375%7D; nfes_isSupportWebP=1; _RF1=2409%3A8762%3A470%3A1%3A1622%3A%3A57ac; _bfa=1.1741166096005.3tgkx4.1.1741317948617.1741317974345.7.2.0; _jzqco=%7C%7C%7C%7C1741307769738%7C1.504249150.1741166102268.1741317949218.1741317974999.1741317949218.1741317974999.undefined.0.0.14.14",
            "Origin": "https://you.ctrip.com",
            "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        self.session = requests.Session()

    def fetch_page(self, page):
        """获取单页数据"""
        try:
            # 设置请求参数
            params = {
                "_fxpcqlniredt": "09031125217831840516",
                "x-traceID": f"09031125217831840516-{int(time.time() * 1000)}-{random.randint(1000000, 9999999)}"
            }
            
            # 设置请求数据
            data = {
                'count': 10,
                'districtId': 104,
                'filter': {'filterItems': []},
                'head': {
                    'cid': "09031125217831840516",
                    'ctok': "",
                    'cver': "1.0",
                    'lang': "01",
                    'sid': "8888",
                    'syscode': "999",
                    'auth': "",
                    'xsid': "",
                    'extension': []
                },
                'index': page,  # 页码从1开始
                'returnModuleType': "product",
                'scene': "online",
                'sortType': 1
            }
            
            # 添加随机延时避免被封
            time.sleep(random.uniform(1, 3))
            
            # 发送请求          
            response = self.session.post(self.base_url, headers=self.headers, params=params, json=data)
            response.raise_for_status()
            
            # 打印响应内容以便调试
            logger.debug(f"Response content: {response.text}")
            
            response_data = response.json()
            
            # 检查响应数据
            if response_data and 'attractionList' in response_data:
                return response_data
            else:
                logger.error(f"API返回数据格式不正确: {response_data}")
                return None
            
        except Exception as e:
            logger.error(f"获取第 {page} 页数据失败: {e}")
            return None

    def get_coordinates(self, address):
        """获取地址的经纬度（高德地图坐标系）"""
        try:
            # 使用高德地图API获取经纬度
            url = "https://restapi.amap.com/v3/geocode/geo"
            params = {
                'address': f"成都市{address}",  # 添加城市名以提高准确度
                'key': '51240cb9ba6ef146a2d3ea6f3f73d563',  # 替换为你的高德地图API密钥
                'city': '成都',
                'output': 'JSON'
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == '1' and data['geocodes']:
                # 高德地图返回的坐标格式为"经度,纬度"
                location = data['geocodes'][0]['location'].split(',')
                return float(location[0]), float(location[1])
            else:
                logger.error(f"获取经纬度失败: {data.get('info', '未知错误')}")
                return None, None
        except Exception as e:
            logger.error(f"获取经纬度失败: {e}")
            return None, None

    def parse_page(self, data):
        """解析单页数据"""
        try:
            attractions = []
            if not data or 'attractionList' not in data:
                logger.error(f"返回的数据无效: {data}")
                return attractions
            
            for item in data['attractionList']:
                try:
                    card = item.get('card', {})
                    spot_id = card.get('poiId')
                    name = card.get('poiName')
                    image_url = card.get('coverImageUrl')
                    address = card.get('address', card.get('zoneName', ''))
                    price_type = card.get('priceTypeDesc')
                    price = self.parse_price(str(price_type))
                    category = self.classify_category(name)
                    
                    # 优先使用高德地图获取坐标
                    longitude, latitude = self.get_coordinates(f"{name}")
                    
                    # 如果高德地图获取失败，则使用原始坐标
                    if not longitude or not latitude:
                        coordinate = card.get('coordinate', {})
                        longitude = coordinate.get('longitude')
                        latitude = coordinate.get('latitude')
                    
                    description = ', '.join(card.get('shortFeatures', []))

                    if name and spot_id:
                        attractions.append((
                            spot_id, name, image_url, address,
                            price, category, longitude, latitude, description
                        ))
                        logger.info(f"解析到景点: {name}, ID: {spot_id}, 地址: {address}, 价格: {price}, 分类: {category}")
                except Exception as e:
                    logger.error(f"解析单个景点失败: {e}")
                    continue
            return attractions
        except Exception as e:
            logger.error(f"解析页面失败: {e}")
            return []

    def parse_price(self, price_info):
        """解析价格信息"""
        try:
            if not price_info:
                return 0.0
            
            # 处理免费情况
            if isinstance(price_info, str) and '免费' in price_info:
                return 0.0
            
            # 从字符串中提取数字
            import re
            if isinstance(price_info, str):
                # 匹配价格范围中的最小值
                pattern = r'(?:￥|¥)?(\d+(?:\.\d+)?)'
                matches = re.findall(pattern, price_info)
                if matches:
                    prices = [float(p) for p in matches]
                    return min(prices)  # 返回最低价格
            return 0.0
        except Exception as e:
            logger.error(f"解析价格失败: {e}, 价格信息: {price_info}")
            return 0.0

    def parse_description(self, card):
        """解析景点描述"""
        descriptions = []
        
        # 获取短特征
        short_features = card.get('shortFeatures', [])
        if short_features:
            descriptions.extend(short_features)
        
        # 获取标签
        tags = card.get('tagList', [])
        if tags:
            tag_names = [tag.get('tagName', '') for tag in tags if tag.get('tagName')]
            descriptions.extend(tag_names)
        
        # 获取亮点描述
        highlights = card.get('highlights', '')
        if highlights:
            descriptions.append(highlights)
            
        return ' | '.join(filter(None, descriptions))

    def is_similar_spot(self, spot1, spot2, name_threshold=0.6, distance_threshold=0.5):
        """判断两个景点是否相似"""
        from difflib import SequenceMatcher
        from math import radians, sin, cos, sqrt, atan2
        
        # 计算名称相似度
        name_similarity = SequenceMatcher(None, spot1[1], spot2[1]).ratio()
        
        # 计算地理距离（km）
        def haversine_distance(lat1, lon1, lat2, lon2):
            R = 6371  # 地球半径（km）
            
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        
        # 如果有经纬度信息，计算距离
        if all([spot1[6], spot1[7], spot2[6], spot2[7]]):
            distance = haversine_distance(spot1[7], spot1[6], spot2[7], spot2[6])
            # 如果名称相似度高且距离近，认为是相似景点
            return name_similarity > name_threshold and distance < distance_threshold
        
        # 如果没有经纬度信息，仅通过名称判断
        return name_similarity > name_threshold

    def parse_page(self, data):
        """解析单页数据"""
        try:
            attractions = []
            if not data or 'attractionList' not in data:
                logger.error(f"返回的数据无效: {data}")
                return attractions
            
            for item in data['attractionList']:
                try:
                    card = item.get('card', {})
                    spot_id = card.get('poiId')
                    name = card.get('poiName')
                    image_url = card.get('coverImageUrl')
                    address = card.get('address', card.get('zoneName', ''))
                    
                    # 修改价格获取逻辑
                    price = 0.0
                    if 'price' in card:
                        price = float(card['price'])
                    elif 'marketPrice' in card:
                        price = float(card['marketPrice'])
                    elif 'priceTypeDesc' in card:
                        price = self.parse_price(card['priceTypeDesc'])
                    
                    category = self.classify_category(name)
                    description = self.parse_description(card)
                    
                    # 获取经纬度
                    longitude, latitude = self.get_coordinates(f"{name}")
                    if not longitude or not latitude:
                        coordinate = card.get('coordinate', {})
                        longitude = coordinate.get('longitude')
                        latitude = coordinate.get('latitude')

                    if name and spot_id:
                        new_spot = (spot_id, name, image_url, address,
                                  price, category, longitude, latitude, description)
                        
                        # 检查是否与已有景点相似
                        is_similar = False
                        for existing_spot in attractions:
                            if self.is_similar_spot(new_spot, existing_spot):
                                is_similar = True
                                break
                        
                        if not is_similar:
                            attractions.append(new_spot)
                            logger.info(f"解析到景点: {name}, ID: {spot_id}, 地址: {address}, 价格: {price}, 分类: {category}")
                        else:
                            logger.info(f"跳过相似景点: {name}")
                            
                except Exception as e:
                    logger.error(f"解析单个景点失败: {e}")
                    continue
            return attractions
        except Exception as e:
            logger.error(f"解析页面失败: {e}")
            return []

    def classify_category(self, name):
        """根据景点名称自动归类"""
        CATEGORY_MAP = {
            '历史文化': ['文化', '历史', '古镇', '遗址', '博物馆', '古迹', '历史遗址', '祠', '寺'],
            '美食探索': ['美食', '餐厅', '小吃', '美味', '特色', '美食街'],
            '自然风光': ['自然', '风景', '山', '湖', '公园', '景区', '风光', '草原'],
            '购物娱乐': ['购物', '娱乐', '商场', '购物中心', '夜市', '游乐场'],
            '艺术展馆': ['艺术', '博物馆', '展览', '画廊', '艺术馆', '文化展', '剧院', '川剧'],
            '古镇民俗': ['古镇', '民俗', '传统', '民间', '风俗'],
            '主题乐园': ['乐园', '游乐场', '主题公园', '游乐设施'],
            '休闲度假': ['度假', '休闲', '温泉', '度假村', '休闲中心'],
            '宗教文化': ['寺庙', '教堂', '宗教', '信仰', '庙会'],
            '城市景观': ['广场', '天际线', '摩天大楼', '城市公园'],
            '动物观赏': ['动物', '熊猫', '动物园', '基地']
        }
        
        # 将景点名称转换为小写以进行匹配
        name = name.lower()
        
        # 遍历类别映射进行匹配
        for category, keywords in CATEGORY_MAP.items():
            if any(keyword in name for keyword in keywords):
                return category
                
        # 如果没有匹配到任何类别，返回"其他"
        return '其他'

    # 修改 scrape 方法以支持分页
    def scrape(self, pages=40):
        """爬取景点数据并保存到数据库"""
        total_spots = 0
        processed_ids = set()  # 用于跟踪已处理的景点ID
    
        try:
            for page in range(1, pages + 1):
                logger.info(f"正在爬取第 {page} 页数据")
                data = self.fetch_page(page)
                if not data:
                    logger.warning(f"第 {page} 页数据获取失败，跳过")
                    continue
    
                attractions = self.parse_page(data)
                if not attractions:
                    logger.warning(f"第 {page} 页未解析到景点数据，可能需要检查")
                    continue
    
                new_spots = 0  # 记录本页新增的景点数
                for attr in attractions:
                    try:
                        spot_id = attr[0]
                        if spot_id in processed_ids:  # 检查是否已处理
                            logger.info(f"景点ID {spot_id} 已处理，跳过")
                            continue
    
                        # 添加到已处理集合
                        processed_ids.add(spot_id)
    
                        # 检查是否已存在
                        existing_spot = ScenicSpot.objects.filter(id=spot_id).first()
    
                        if existing_spot:
                            # 更新现有记录
                            for key, value in zip(['name', 'address', 'ticket_price', 'category', 'longitude', 'latitude', 'description'], [attr[1], attr[3], attr[4], attr[5], attr[6], attr[7], attr[8]]):
                                setattr(existing_spot, key, value)
                            if attr[2]:  # 如果有图片URL
                                existing_spot.images = [attr[2]]
                            existing_spot.save()
                            logger.info(f"更新景点: {attr[1]}")
                        else:
                            # 创建新记录
                            ScenicSpot.objects.create(
                                id=spot_id,
                                name=attr[1],
                                images=[attr[2]] if attr[2] else [],
                                address=attr[3],
                                ticket_price=attr[4],
                                category=attr[5],
                                longitude=attr[6],
                                latitude=attr[7],
                                description=attr[8]
                            )
                            new_spots += 1
                            total_spots += 1
                            logger.info(f"新增景点: {attr[1]}")
                    except Exception as e:
                        logger.error(f"保存景点失败: {e}")
                        continue
    
                logger.info(f"第 {page} 页处理完成，新增 {new_spots} 个景点")
    
                # 如果连续两页都没有新增景点，可能已经到达末尾
                if new_spots == 0:
                    logger.info("当前页面没有新增景点，继续检查下一页")
    
        except Exception as e:
            logger.error(f"爬取过程发生错误: {e}")
        finally:
            logger.info(f"爬虫结束，共获取 {total_spots} 个景点")

def update_scenic_spots(page_count=3):
    """更新景点数据的主函数"""
    logger.info("开始更新景点数据")
    try:
        scraper = SimpleSpotScraper()
        scraper.scrape(pages=page_count)  # 调用爬取方法
    except Exception as e:
        logger.error(f"更新景点数据时出错: {str(e)}")
        raise

if __name__ == '__main__':
    setup_django()  # 设置Django环境
    update_scenic_spots()  # 更新景点数据