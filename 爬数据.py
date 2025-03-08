import requests
import pandas as pd
import time
from typing import List, Dict
import math
# 高德地图GCJ02转WGS84  
def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    """
    PI = 3.1415926535897932384626
    ee = 0.00669342162296594323
    a = 6378245.0
    
    if out_of_china(lng, lat):
        return [lng, lat]
    
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def transform_lat(lng, lat):
    PI = 3.1415926535897932384626
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 *
            math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 *
            math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret

def transform_lng(lng, lat):
    PI = 3.1415926535897932384626
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 *
            math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 *
            math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret

def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)
# 爬取POI数据并保存到Excel
class POICrawler:
    def __init__(self):
        self.key = '27cef49b3ef8fd40f763d9191fd5a637'  # 替换为你的高德API密钥
        self.city = '成都'
        self.base_url = 'https://restapi.amap.com/v3/place/text'
        
    def crawl_poi(self, keywords: str, types: str, output_file: str) -> None:
        """
        爬取POI数据并保存到Excel
        :param keywords: 关键词
        :param types: POI类型
        :param output_file: 输出文件名
        """
        all_pois = []
        page = 1
        
        while True:
            params = {
                'key': self.key,
                'keywords': keywords,
                'types': types,
                'city': self.city,
                'offset': 25,  # 每页记录数
                'page': page,
                'extensions': 'all'  # 返回详细信息
            }
            
            try:
                response = requests.get(self.base_url, params=params)
                result = response.json()
                
                if result['status'] == '1':  # 请求成功
                    pois = result['pois']
                    if not pois:  # 没有更多数据
                        break
                    
                    for poi in pois:
                        lng, lat = map(float, poi['location'].split(','))
                        wgs84_lng, wgs84_lat = gcj02_to_wgs84(lng, lat)
                        
                        poi_info = {
                            '名称': poi['name'],
                            '地址': poi['address'],
                            '经度_GCJ02': lng,  # 高德地图坐标
                            '纬度_GCJ02': lat,
                            '经度_WGS84': wgs84_lng,  # ArcGIS使用的坐标
                            '纬度_WGS84': wgs84_lat,
                            '电话': poi.get('tel', ''),
                            '类型': poi['type'],
                            '营业时间': poi.get('business_hours', ''),
                            '评分': poi.get('biz_ext', {}).get('rating', ''),
                        }
                        all_pois.append(poi_info)
                    
                    print(f"已获取第{page}页数据，当前总计{len(all_pois)}条")
                    page += 1
                    time.sleep(0.5)  # 避免请求过于频繁
                else:
                    print(f"请求失败: {result['info']}")
                    break
                    
            except Exception as e:
                print(f"发生错误: {str(e)}")
                break
        
        if all_pois:
            df = pd.DataFrame(all_pois)
            df.to_excel(f'data/{output_file}.xlsx', index=False)
            print(f"数据已保存到 data/{output_file}.xlsx")
# 主函数
def main():
    crawler = POICrawler()
    
    # 定义要爬取的POI类型
    poi_configs = [
        # 住宿类
        {'keywords': '酒店', 'types': '100100', 'output': 'hotels'},
        {'keywords': '民宿', 'types': '100100', 'output': 'homestays'},
        
        # 交通类
        {'keywords': '地铁站', 'types': '150500', 'output': 'metro_stations'},
        {'keywords': '公交站', 'types': '150700', 'output': 'bus_stops'},
        {'keywords': '停车场', 'types': '150904', 'output': 'parking_lots'},
        
        # 餐饮类
        {'keywords': '川菜', 'types': '050100', 'output': 'sichuan_food'},
        {'keywords': '火锅', 'types': '050100', 'output': 'hotpot'},
        {'keywords': '小吃', 'types': '050100', 'output': 'snacks'},
        {'keywords': '西餐', 'types': '050100', 'output': 'western_food'},
    ]
    
    # 选择要爬取的POI类型（取消注释需要爬取的类型）
    for config in poi_configs:
        # 通过注释控制要爬取的数据类型
        if config['output'] != 'western_food':  # 只爬取酒店数据
          continue
        
        print(f"\n开始爬取{config['keywords']}数据...")
        crawler.crawl_poi(
            keywords=config['keywords'],
            types=config['types'],
            output_file=config['output']
        )

if __name__ == '__main__':
    main()