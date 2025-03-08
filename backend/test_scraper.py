"""
大众点评爬虫测试脚本
不依赖Django的GeoDjango功能，可以独立运行
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import logging
import os
import sys
import fake_useragent  # 如果没有安装，需要先安装: pip install fake-useragent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('dianping_spider_test')

class DianpingSpiderTest:
    def __init__(self):
        # 使用随机User-Agent
        try:
            ua = fake_useragent.UserAgent()
            user_agent = ua.random
        except:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        self.headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'http://www.dianping.com/chengdu',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'DNT': '1',
        }
        self.base_url = 'http://www.dianping.com'
        self.proxies = None
        
        # 打印当前使用的User-Agent
        logger.info(f"使用User-Agent: {self.headers['User-Agent']}")
    
    def get_category_mapping(self, dianping_category):
        """将大众点评的分类映射到我们的系统分类"""
        mapping = {
            '古镇': '古镇',
            '风景名胜': '自然风光',
            '游乐场': '现代建筑',
            '文化古迹': '历史文化',
            '寺庙道观': '历史文化',
            '公园': '自然风光',
            '景点': '自然风光',
            '旅游景点': '自然风光',
        }
        return mapping.get(dianping_category, '其他')
    
    def parse_price(self, price_text):
        """解析价格文本，提取数字"""
        try:
            if not price_text or price_text == '免费':
                return None
            # 提取数字
            import re
            price_match = re.search(r'(\d+(\.\d+)?)', price_text)
            if price_match:
                return float(price_match.group(1))
            return None
        except Exception as e:
            logger.error(f"解析价格出错: {str(e)}, 原文本: {price_text}")
            return None
    
    def get_spot_details(self, url):
        """获取景点详细信息"""
        try:
            logger.info(f"正在获取景点详情: {url}")
            # 添加随机延时
            time.sleep(random.uniform(2, 5))
            
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
            if response.status_code != 200:
                logger.warning(f"请求失败，状态码: {response.status_code}, URL: {url}")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 打印HTML内容，用于调试
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
            # 提取基本信息
            name_element = soup.find('h1', class_='shop-name')
            if not name_element:
                logger.warning(f"无法找到景点名称，URL: {url}")
                # 尝试其他可能的选择器
                name_element = soup.select_one('.shop-title') or soup.select_one('.shop-header h1')
                if not name_element:
                    logger.error(f"无法找到景点名称，跳过此景点。URL: {url}")
                    return None
                
            name = name_element.text.strip()
            
            # 提取地址
            address_element = soup.find('span', class_='address')
            if not address_element:
                address_element = soup.select_one('.address') or soup.select_one('.shop-address')
            address = address_element.text.strip() if address_element else "成都市"
            
            # 提取描述
            description_element = soup.find('div', class_='desc-wrap')
            if not description_element:
                description_element = soup.select_one('.shop-desc') or soup.select_one('.intro-content')
            description = description_element.text.strip() if description_element else f"{name}是成都市的一个著名景点。"
            
            # 提取营业时间
            opening_hours = '全天开放'  # 默认值
            time_element = soup.find('span', class_='hours')
            if not time_element:
                time_element = soup.select_one('.hours') or soup.select_one('.shop-time')
            if time_element:
                opening_hours = time_element.text.strip()
            
            # 提取门票价格
            price_element = soup.find('span', class_='price')
            if not price_element:
                price_element = soup.select_one('.price') or soup.select_one('.shop-price')
            ticket_price = None
            if price_element:
                ticket_price = self.parse_price(price_element.text)
            
            # 提取分类
            category_element = soup.find('span', class_='category')
            if not category_element:
                category_element = soup.select_one('.category') or soup.select_one('.shop-category')
            category = '其他'
            if category_element:
                dianping_category = category_element.text.strip()
                category = self.get_category_mapping(dianping_category)
            
            # 提取图片
            images = []
            img_elements = soup.find_all('img', class_='J_photos')
            if not img_elements:
                # 尝试其他可能的图片选择器
                img_elements = soup.select('.pic-list img') or soup.select('.shop-pic img') or soup.select('.photos img')
                
            for img in img_elements[:5]:  # 最多保存5张图片
                if 'src' in img.attrs:
                    img_url = img['src']
                    if not img_url.startswith('http'):
                        img_url = 'https:' + img_url if img_url.startswith('//') else 'https://' + img_url
                    images.append(img_url)
            
            # 使用高德地图API获取经纬度
            try:
                # 构建地址字符串
                address_str = f'成都市{address}'
                # 高德地图API密钥（请替换为您的密钥）
                amap_key = '9b0e72c78d27f90e1d297e7af09d2c0e'
                # 调用地理编码API
                geocode_url = f'https://restapi.amap.com/v3/geocode/geo?address={address_str}&key={amap_key}&city=成都'
                geocode_response = requests.get(geocode_url, timeout=5)
                geocode_data = geocode_response.json()
                
                if geocode_data['status'] == '1' and geocode_data['geocodes']:
                    # 获取第一个匹配结果
                    location_str = geocode_data['geocodes'][0]['location']
                    lng, lat = map(float, location_str.split(','))
                    # 直接存储经纬度
                    location_lng = lng
                    location_lat = lat
                else:
                    # 如果无法获取位置，使用成都市中心坐标
                    location_lng = 104.07
                    location_lat = 30.67
                    logger.warning(f"无法获取位置信息，使用默认坐标。景点: {name}, 地址: {address}")
            except Exception as e:
                logger.error(f'获取位置信息出错，景点: {name}, 错误: {str(e)}')
                # 使用成都市中心坐标作为默认值
                location_lng = 104.07
                location_lat = 30.67
            
            # 构建返回数据
            spot_data = {
                'name': name,
                'location_lng': location_lng,
                'location_lat': location_lat,
                'description': description,
                'category': category,
                'address': address,
                'opening_hours': opening_hours,
                'ticket_price': ticket_price,
                'images': images
            }
            
            logger.info(f"成功获取景点信息: {name}")
            return spot_data
            
        except Exception as e:
            logger.error(f'获取景点详情出错: {str(e)}, URL: {url}')
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def crawl_spots(self, page_count=1):
        """爬取成都景点数据"""
        spots_data = []
        
        # 大众点评成都景点URL - 尝试不同的URL格式
        base_urls = [
            # 尝试使用不同的URL格式
            'https://www.dianping.com/chengdu/ch30/g119',  # 成都景点
            'https://www.dianping.com/chengdu/ch30',       # 成都旅游
            'https://www.dianping.com/chengdu/attraction', # 成都景点另一种URL
        ]
        
        for base_url in base_urls:
            try:
                # 先尝试访问首页，获取cookie
                logger.info(f"正在访问首页: {base_url}")
                
                # 添加较长的随机延时，模拟真实用户行为
                time.sleep(random.uniform(5, 10))
                
                response = requests.get(base_url, headers=self.headers, proxies=self.proxies, timeout=15)
                if response.status_code != 200:
                    logger.warning(f"请求失败，状态码: {response.status_code}, URL: {base_url}")
                    continue
                    
                # 保存cookie
                cookies = response.cookies
                
                # 保存HTML内容，用于调试
                with open(f'homepage.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # 解析首页，直接从首页获取景点信息
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 尝试多种可能的选择器
                spot_elements = (
                    soup.select('.shop-list .shop-item') or 
                    soup.select('.list-wrap .shop-info') or
                    soup.select('.poi-tile-nodeal') or
                    soup.select('.shop-wrap .shop-info') or
                    soup.select('.content-wrap .shop-list li')
                )
                
                if not spot_elements:
                    logger.warning(f"未找到景点列表，可能需要更新选择器。URL: {base_url}")
                    # 尝试查找任何可能的链接
                    all_links = soup.find_all('a', href=True)
                    logger.info(f"页面上找到 {len(all_links)} 个链接")
                    
                    # 查找可能的景点链接
                    potential_spot_links = []
                    for link in all_links:
                        href = link['href']
                        text = link.text.strip()
                        if '/shop/' in href or 'ch30' in href or 'attraction' in href:
                            logger.info(f"可能的景点链接: {text} -> {href}")
                            potential_spot_links.append(href)
                    
                    # 如果找到可能的景点链接，尝试访问
                    for i, link in enumerate(potential_spot_links[:5]):  # 只尝试前5个
                        if not link.startswith('http'):
                            link = self.base_url + link if link.startswith('/') else self.base_url + '/' + link
                        
                        logger.info(f"尝试访问可能的景点链接: {link}")
                        spot_data = self.get_spot_details(link)
                        if spot_data:
                            spots_data.append(spot_data)
                            logger.info(f"已爬取 {len(spots_data)} 个景点")
                        
                        # 添加较长的随机延时
                        time.sleep(random.uniform(8, 15))
                    
                    continue
                
                logger.info(f"找到 {len(spot_elements)} 个景点")
                
                # 只处理前几个景点，避免被封
                for spot_element in spot_elements[:3]:
                    try:
                        # 获取详情页链接
                        link_element = spot_element.find('a', href=True)
                        if not link_element:
                            continue
                            
                        detail_url = link_element['href']
                        if not detail_url.startswith('http'):
                            detail_url = self.base_url + detail_url if detail_url.startswith('/') else self.base_url + '/' + detail_url
                        
                        logger.info(f"找到景点链接: {detail_url}")
                        
                        # 获取景点详情
                        spot_data = self.get_spot_details(detail_url)
                        
                        if spot_data:
                            spots_data.append(spot_data)
                            logger.info(f"已爬取 {len(spots_data)} 个景点")
                        
                        # 添加较长的随机延时，避免被反爬
                        time.sleep(random.uniform(8, 15))
                        
                    except Exception as e:
                        logger.error(f"处理景点元素时出错: {str(e)}")
                        continue
                
            except Exception as e:
                logger.error(f'爬取页面出错: {str(e)}')
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"爬取完成，共获取 {len(spots_data)} 个景点信息")
        
        # 将结果保存到JSON文件
        with open('spots_data.json', 'w', encoding='utf-8') as f:
            json.dump(spots_data, f, ensure_ascii=False, indent=2)
            
        return spots_data

def main():
    """测试爬虫功能"""
    logger.info("开始测试爬虫")
    try:
        spider = DianpingSpiderTest()
        # 只爬取1页进行测试
        spots_data = spider.crawl_spots(page_count=1)
        
        if not spots_data:
            logger.warning("未获取到任何景点数据")
            return
            
        logger.info(f"成功爬取 {len(spots_data)} 个景点数据")
        
        # 打印第一个景点的信息
        if spots_data:
            logger.info(f"第一个景点信息: {json.dumps(spots_data[0], ensure_ascii=False, indent=2)}")
            
    except Exception as e:
        logger.error(f"爬虫测试出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 