#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试后端API是否正常工作的脚本
"""

import requests
import json
import sys
from urllib.parse import urljoin

# 配置
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = [
    "/api/tourism/scenic_spots/",
    "/api/tourism/scenic_spots/geojson/",
    "/api/tourism/scenic_spots/categories/",
]

def test_endpoint(url, description):
    """测试单个API端点"""
    print(f"\n测试 {description} ({url})...")
    try:
        response = requests.get(url, headers={"Accept": "application/json"})
        status_code = response.status_code
        
        if status_code == 200:
            print(f"✅ 成功! 状态码: {status_code}")
            try:
                data = response.json()
                if isinstance(data, dict) and "count" in data:
                    print(f"   数据项数量: {data['count']}")
                elif isinstance(data, dict) and "type" in data and data["type"] == "FeatureCollection":
                    features_count = len(data.get("features", []))
                    print(f"   GeoJSON特征数量: {features_count}")
                else:
                    print(f"   响应大小: {len(response.content)} 字节")
            except json.JSONDecodeError:
                print("   警告: 响应不是有效的JSON")
        else:
            print(f"❌ 失败! 状态码: {status_code}")
            print(f"   响应: {response.text[:200]}...")
        
        return status_code == 200
    except requests.RequestException as e:
        print(f"❌ 请求错误: {e}")
        return False

def check_cors_headers(url):
    """检查CORS头信息"""
    print("\n测试CORS设置...")
    try:
        # 发送OPTIONS请求模拟CORS预检
        response = requests.options(
            url, 
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # 检查CORS头信息
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        
        if cors_headers["Access-Control-Allow-Origin"]:
            print("✅ CORS头信息存在:")
            for key, value in cors_headers.items():
                print(f"   {key}: {value}")
            return True
        else:
            print("❌ CORS头信息不存在或不完整:")
            for key, value in cors_headers.items():
                print(f"   {key}: {value}")
            return False
    except requests.RequestException as e:
        print(f"❌ CORS测试请求错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("后端API测试")
    print("=" * 60)
    
    # 测试服务器是否在线
    try:
        response = requests.get(BASE_URL)
        print(f"✅ 服务器在线! 状态码: {response.status_code}")
    except requests.RequestException:
        print("❌ 服务器离线或无法连接!")
        print("请确保Django服务器正在运行 (python manage.py runserver)")
        sys.exit(1)
    
    # 测试各个API端点
    success_count = 0
    for endpoint in API_ENDPOINTS:
        url = urljoin(BASE_URL, endpoint)
        if test_endpoint(url, endpoint):
            success_count += 1
    
    # 测试CORS设置
    cors_success = check_cors_headers(urljoin(BASE_URL, API_ENDPOINTS[0]))
    
    # 总结
    print("\n" + "=" * 60)
    print(f"测试结果: {success_count}/{len(API_ENDPOINTS)} 个API端点测试成功")
    print(f"CORS设置: {'✅ 正确' if cors_success else '❌ 有问题'}")
    print("=" * 60)
    
    if success_count == len(API_ENDPOINTS) and cors_success:
        print("🎉 所有测试通过! 后端API正常工作。")
    else:
        print("⚠️ 部分测试失败，请检查上述错误信息。")

if __name__ == "__main__":
    main() 