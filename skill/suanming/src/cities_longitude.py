#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字精批分析系统 - 真太阳时校准工具

职责：
- 城市经度查询
- 均时差计算（支持闰年）
- 真太阳时修正
- 详细的修正信息返回

关键公式：
真太阳时 = 平太阳时 - (标准经线 - 实际经度) × 4分钟/度 + 均时差

标准经线：120°E（中国统一使用 UTC+8）
"""

import math
from typing import Dict, Optional, Union


# ─────────────────────────────────────────────────────────────────
# 第一部分：城市经度数据库
# ─────────────────────────────────────────────────────────────────

CITIES = {
    # 北京地区
    '北京': 120.15,
    '天津': 117.2,
    
    # 上海地区
    '上海': 121.47,
    '浙江': 120.15,
    '杭州': 120.15,
    
    # 广州地区
    '广州': 113.26,
    '深圳': 114.07,
    '珠海': 113.53,
    
    # 成都地区
    '成都': 104.07,
    '重庆': 106.55,
    
    # 西安地区
    '西安': 108.95,
    '西安碑林': 108.9533,
    
    # 江苏地区
    '南京': 118.8,
    '苏州': 120.59,
    '江阴': 120.58,
    
    # 武汉地区
    '武汉': 114.31,
    
    # 沈阳地区
    '沈阳': 123.43,
    '哈尔滨': 126.53,
    
    # 南昌地区
    '南昌': 115.86,
    
    # 福州地区
    '福州': 119.3,
    '厦门': 118.09,
    
    # 其他
    '长沙': 112.94,
    '郑州': 113.65,
    '青岛': 120.33,
    '大连': 121.62,
    '昆明': 102.87,
    '南宁': 108.33,
    '海口': 110.35,
    '石家庄': 114.57,
    '太原': 112.55,
    '兰州': 103.83,
    '西宁': 101.77,
    '银川': 106.27,
    '乌鲁木齐': 87.68,
}


def get_longitude(city_name: str) -> Optional[float]:
    """获取城市经度"""
    if city_name in CITIES:
        return CITIES[city_name]
    
    for key in CITIES.keys():
        if city_name.startswith(key) or key.startswith(city_name):
            return CITIES[key]
    
    return None


def is_leap_year(year: int) -> bool:
    """判断闰年"""
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    if year % 4 == 0:
        return True
    return False


def calculate_equation_of_time(year: int, month: int, day: int) -> float:
    """计算均时差（分钟）"""
    days_in_month = [0, 31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    n = sum(days_in_month[:month]) + day
    
    B = 2 * math.pi * (n - 81) / 365
    EoT = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    
    return EoT


def calculate_solar_time(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    longitude: float,
    timezone_offset: int = 8
) -> Dict[str, Union[int, float, str]]:
    """计算真太阳时"""
    try:
        total_seconds = hour * 3600 + minute * 60 + second
        
        longitude_offset_minutes = (120 - longitude) * 4
        eot = calculate_equation_of_time(year, month, day)
        total_offset_minutes = longitude_offset_minutes - eot
        
        total_offset_seconds = total_offset_minutes * 60
        adjusted_seconds = total_seconds - total_offset_seconds
        
        if adjusted_seconds < 0:
            adjusted_seconds += 24 * 3600
        elif adjusted_seconds >= 24 * 3600:
            adjusted_seconds -= 24 * 3600
        
        new_hour = int(adjusted_seconds // 3600)
        new_minute = int((adjusted_seconds % 3600) // 60)
        new_second = int(adjusted_seconds % 60)
        
        return {
            'original_hour': hour,
            'original_minute': minute,
            'original_second': second,
            'corrected_hour': new_hour,
            'corrected_minute': new_minute,
            'corrected_second': new_second,
            'longitude': longitude,
            'longitude_offset_minutes': round(longitude_offset_minutes, 2),
            'equation_of_time_minutes': round(eot, 2),
            'total_offset_minutes': round(total_offset_minutes, 2),
            'timezone': f'UTC+{timezone_offset}',
            'status': 'success',
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'status': 'error',
        }


if __name__ == '__main__':
    print("=" * 60)
    print("真太阳时校准工具 - 测试")
    print("=" * 60)
    
    print("\n【测试】1995-09-04 21:48 江阴（120.58°）")
    result = calculate_solar_time(1995, 9, 4, 21, 48, 0, 120.58)
    for key, value in result.items():
        print(f"  {key}: {value}")
    print(f"  期望结果：约 21:44")
