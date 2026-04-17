#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字精批分析系统 - 原局排盘模块

职责：
- 接收���太阳时后的出生信息
- 推导四柱干支（含正确的时柱计算）
- 计算地支藏干、十神、五行、空亡等所有元信息
- 输出标准的原局盘信息

依赖：lunar_python
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from lunar_python import Solar, Lunar
except ImportError:
    Solar = None
    Lunar = None

# 导入节气模块
try:
    from jieqi import get_jieqi_info
except ImportError:
    from .jieqi import get_jieqi_info


# ─────────────────────────────────────────────────────────────────
# 数据常量
# ─────────────────────────────────────────────────────────────────

Gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
Zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 12时辰对应表（真太阳时）
SHICHEN_RANGES = [
    (23, 1, '子'),
    (1, 3, '丑'),
    (3, 5, '寅'),
    (5, 7, '卯'),
    (7, 9, '辰'),
    (9, 11, '巳'),
    (11, 13, '午'),
    (13, 15, '未'),
    (15, 17, '申'),
    (17, 19, '酉'),
    (19, 21, '戌'),
    (21, 23, '亥'),
]

# 五鼠遁口诀 - 根据日干推时干的起点
WUSHU_DUN = {
    '甲': '甲',  # 甲己还生甲
    '己': '甲',
    '乙': '丙',  # 乙庚生丙作
    '庚': '丙',
    '丙': '戊',  # 丙辛生戊去
    '辛': '戊',
    '丁': '庚',  # 丁壬生庚起
    '壬': '庚',
    '戊': '壬',  # 戊癸生壬来
    '癸': '壬',
}

# 地支藏干表
ZHI_CANGYGAN = {
    '子': ['癸'],
    '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'],
    '卯': ['乙'],
    '辰': ['戊', '乙', '癸'],
    '巳': ['丙', '戊', '庚'],
    '午': ['丁', '己'],
    '未': ['己', '丁', '乙'],
    '申': ['庚', '壬', '戊'],
    '酉': ['辛'],
    '戌': ['戊', '辛', '丁'],
    '亥': ['壬', '甲'],
}

# 十神映射表（已简化）
TEN_DEITIES = {
    '甲': {'甲': '比', '乙': '劫', '丙': '食', '丁': '伤', '戊': '才', '己': '财', '庚': '杀', '辛': '官', '壬': '枭', '癸': '印'},
    '乙': {'甲': '劫', '乙': '比', '丙': '伤', '丁': '食', '戊': '财', '己': '才', '庚': '官', '辛': '杀', '壬': '印', '癸': '枭'},
    '丙': {'甲': '枭', '乙': '印', '丙': '比', '丁': '劫', '戊': '食', '己': '伤', '庚': '才', '辛': '财', '壬': '杀', '癸': '官'},
    '丁': {'甲': '印', '乙': '枭', '丙': '劫', '丁': '比', '戊': '伤', '己': '食', '庚': '财', '辛': '才', '壬': '官', '癸': '杀'},
    '戊': {'甲': '杀', '乙': '官', '丙': '枭', '丁': '印', '戊': '比', '己': '劫', '庚': '食', '辛': '伤', '壬': '才', '癸': '财'},
    '己': {'甲': '官', '乙': '杀', '丙': '印', '丁': '枭', '戊': '劫', '己': '比', '庚': '伤', '辛': '食', '壬': '财', '癸': '才'},
    '庚': {'甲': '才', '乙': '财', '丙': '杀', '丁': '官', '戊': '枭', '己': '印', '庚': '比', '辛': '劫', '壬': '食', '癸': '伤'},
    '辛': {'甲': '财', '乙': '才', '丙': '官', '丁': '杀', '戊': '印', '己': '枭', '庚': '劫', '辛': '比', '壬': '伤', '癸': '食'},
    '壬': {'甲': '食', '乙': '伤', '丙': '才', '丁': '财', '戊': '杀', '己': '官', '庚': '枭', '辛': '印', '壬': '比', '癸': '劫'},
    '癸': {'甲': '伤', '乙': '食', '丙': '财', '丁': '才', '戊': '官', '己': '杀', '庚': '印', '辛': '枭', '壬': '劫', '癸': '比'},
}

# 五行映射
GAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
}

ZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
    '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 纳音
NAYIN = {
    '甲子': '海中金', '乙丑': '海中金',
    '丙寅': '炉中火', '丁卯': '炉中火',
    '戊辰': '大林木', '己巳': '大林木',
    '庚午': '路旁土', '辛未': '路旁土',
    '壬申': '剑锋金', '癸酉': '剑锋金',
    '甲戌': '山头火', '乙亥': '山头火',
    '丙子': '沙中土', '丁丑': '沙中土',
    '戊寅': '城头土', '己卯': '城头土',
    '庚辰': '白腊金', '辛巳': '白腊金',
    '壬午': '杨柳木', '癸未': '杨柳木',
    '甲申': '泉中水', '乙酉': '泉中水',
    '丙戌': '屋上土', '丁亥': '屋上土',
    '戊子': '霹雳火', '己丑': '霹雳火',
    '庚寅': '松柏木', '辛卯': '松柏木',
    '壬辰': '长流水', '癸巳': '长流水',
    '甲午': '砂石土', '乙未': '砂石土',
    '丙申': '山下火', '丁酉': '山下火',
    '戊戌': '平地木', '己亥': '平地木',
    '庚子': '壁上土', '辛丑': '壁上土',
    '壬寅': '金箔金', '癸卯': '金箔金',
    '甲辰': '覆灯火', '乙巳': '覆灯火',
    '丙午': '天河水', '丁未': '天河水',
    '戊申': '大驿土', '己酉': '大驿土',
    '庚戌': '钗钏金', '辛亥': '钗钏金',
    '壬子': '桑柘木', '癸丑': '桑柘木',
    '甲寅': '大溪水', '乙卯': '大溪水',
    '丙辰': '沙中土', '丁巳': '沙中土',
    '戊午': '天上火', '己未': '天上火',
    '庚申': '石榴木', '辛酉': '石榴木',
    '壬戌': '大海水', '癸亥': '大海水'
}


# ─────────────────────────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────────────────────────

def get_shichen_zhi(hour: int, minute: int) -> str:
    """
    根据真太阳时的小时和分钟获取时支
    
    参数:
        hour: 小时(0-23)
        minute: 分钟(0-59)
    
    返回:
        时支（子、丑、寅...亥）
    """
    for start_hour, end_hour, zhi in SHICHEN_RANGES:
        if start_hour <= 23:  # 正常范围
            if start_hour <= hour < end_hour:
                return zhi
        else:  # 跨越午夜（23:00-01:00为子时）
            if hour >= start_hour or hour < end_hour:
                return zhi
    
    return '子'  # 默认


def get_time_gan(day_gan: str, time_zhi: str) -> str:
    """
    根据日干和时支推导时干（五鼠遁口诀）
    
    参数:
        day_gan: 日干
        time_zhi: 时支
    
    返回:
        时干
    """
    # 先获取起始天干
    start_gan = WUSHU_DUN.get(day_gan, '甲')
    
    # 根据时支推导
    start_gan_idx = Gan.index(start_gan)
    zhi_idx = Zhi.index(time_zhi)
    
    # 时干 = 起始天干 + 时支偏移量
    time_gan_idx = (start_gan_idx + zhi_idx) % 10
    
    return Gan[time_gan_idx]


def get_ten_deity(day_gan: str, target_gan_or_zhi: str) -> str:
    """获取十神"""
    if day_gan not in TEN_DEITIES:
        return ''
    if target_gan_or_zhi not in TEN_DEITIES[day_gan]:
        return ''
    return TEN_DEITIES[day_gan][target_gan_or_zhi]


def get_cangygan(zhi: str) -> List[str]:
    """获取地支藏干"""
    return ZHI_CANGYGAN.get(zhi, [])


def get_nayin(gan: str, zhi: str) -> str:
    """获取纳音"""
    ganzhi = gan + zhi
    return NAYIN.get(ganzhi, '')


# ─────────────────────────────────────────────────────────────────
# 核心排盘函数
# ─────────────────────────────────────────────────────────────────

def calculate_yuanju(birth_info: Dict) -> Dict:
    """
    计算原局排盘
    """
    
    if Solar is None:
        return {
            'success': False,
            'error': '未安装 lunar_python 库，请执行: pip install lunar_python',
            'generated_at': datetime.now().isoformat()
        }
    
    try:
        year = birth_info['year']
        month = birth_info['month']
        day = birth_info['day']
        hour = birth_info['hour']
        minute = birth_info['minute']
        gender = birth_info.get('gender', 'male')
        city = birth_info.get('city', '')
        
        # 第一步：构建阳历日期，通过 lunar_python 推导四柱干支
        solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        lunar = solar.getLunar()
        eight_char = lunar.getEightChar()
        
        # 提取四柱干支
        year_gz = eight_char.getYear()
        month_gz = eight_char.getMonth()
        day_gz = eight_char.getDay()
        hour_gz = eight_char.getTime()
        
        # 分离干支
        year_gan, year_zhi = year_gz[0], year_gz[1]
        month_gan, month_zhi = month_gz[0], month_gz[1]
        day_gan, day_zhi = day_gz[0], day_gz[1]
        hour_gan = hour_gz[0]
        
        # 第二步：纠正时支和时干
        # lunar_python 的时支可能不准确，需要手工计算
        correct_hour_zhi = get_shichen_zhi(hour, minute)
        correct_hour_gan = get_time_gan(day_gan, correct_hour_zhi)
        correct_hour_gz = correct_hour_gan + correct_hour_zhi
        
        # 第三步：查询节气获取准确的月支
        jieqi_info = get_jieqi_info(year, month, day)
        correct_month_zhi = jieqi_info['month_zhi']
        # 月干从 lunar_python 获取（应该是对的）
        correct_month_gz = month_gan + correct_month_zhi
        
        # 第四步：生成四柱详细信息
        pillars = []
        
        pillar_names = ['年柱', '月柱', '日柱', '时柱']
        ganzhi_list = [
            (year_gan, year_zhi, '年'),
            (month_gan, correct_month_zhi, '月'),
            (day_gan, day_zhi, '日'),
            (correct_hour_gan, correct_hour_zhi, '时')
        ]
        
        for idx, (gan, zhi, pillar_type) in enumerate(ganzhi_list):
            pillar = {
                'index': idx,
                'name': pillar_names[idx],
                'gan': gan,
                'zhi': zhi,
                'ganzhi': gan + zhi,
                'gan_wuxing': GAN_WUXING.get(gan, ''),
                'zhi_wuxing': ZHI_WUXING.get(zhi, ''),
                'cangygan': get_cangygan(zhi),
                'nayin': get_nayin(gan, zhi),
                'shengxiao': get_ten_deity(day_gan, zhi),
                'yinyang': '阳' if Gan.index(gan) % 2 == 0 else '阴'
            }
            
            # 计算地支中每个藏干的十神
            cangygan_deities = []
            for canyggan_item in pillar['cangygan']:
                deity = get_ten_deity(day_gan, canyggan_item)
                cangygan_deities.append({
                    'gan': canyggan_item,
                    'wuxing': GAN_WUXING.get(canyggan_item, ''),
                    'shishen': deity
                })
            pillar['cangygan_details'] = cangygan_deities
            
            pillars.append(pillar)
        
        # 第五步：构建完整返回结构
        result = {
            'success': True,
            'birth': {
                'solar_year': year,
                'solar_month': month,
                'solar_day': day,
                'solar_time': f'{hour:02d}:{minute:02d}:00',
                'solar_date': f'{year}-{month:02d}-{day:02d}',
                'lunar_year': lunar.getYear(),
                'lunar_month': lunar.getMonth(),
                'lunar_day': lunar.getDay(),
                'lunar_date': f'{lunar.getYear()}年{abs(lunar.getMonth())}月{lunar.getDay()}日',
                'gender': gender,
                'city': city,
                'solar_time_applied': birth_info.get('solar_time_applied', False)
            },
            'ganzhi': {
                'year': year_gz,
                'month': correct_month_gz,
                'day': day_gz,
                'hour': correct_hour_gz
            },
            'pillars': pillars,
            'day_gan': day_gan,
            'jieqi_info': jieqi_info,
            'generated_at': datetime.now().isoformat()
        }
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': f'排盘计算失败: {str(e)}',
            'generated_at': datetime.now().isoformat()
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='八字原局排盘')
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--day', type=int, required=True)
    parser.add_argument('--hour', type=int, required=True)
    parser.add_argument('--minute', type=int, default=0)
    parser.add_argument('--gender', type=str, default='male')
    parser.add_argument('--city', type=str, default='')
    parser.add_argument('--solar-time-applied', action='store_true')
    
    args = parser.parse_args()
    
    birth_info = {
        'year': args.year,
        'month': args.month,
        'day': args.day,
        'hour': args.hour,
        'minute': args.minute,
        'gender': args.gender,
        'city': args.city,
        'solar_time_applied': args.solar_time_applied
    }
    
    result = calculate_yuanju(birth_info)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
