#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字精批分析系统 - 节气模块

职责：
- 根据日期获取当前农历月的月支
- 支持 lunar_python 库的节气查询
"""

try:
    from lunar_python import Solar, Lunar
except ImportError:
    Solar = None
    Lunar = None


# 12节气及其对应的农历月支（关键！不是24节气）
# 12节气是决定月支的关键
JIEQI_TO_MONTH_ZHI = {
    '立春': '寅',   # 农历正月 (立春后)
    '惊蛰': '卯',   # 农历二月 (惊蛰后)
    '清明': '辰',   # 农历三月 (清明后)
    '立夏': '午',   # 农历四月 (立夏后)
    '芒种': '未',   # 农历五月 (芒种后)
    '小暑': '申',   # 农历六月 (小暑后)
    '立秋': '酉',   # 农历七月 (立秋后)
    '白露': '戌',   # 农历八月 (白露后)
    '寒露': '亥',   # 农历九月 (寒露后)
    '立冬': '子',   # 农历十月 (立冬后)
    '大雪': '丑',   # 农历十一月 (大雪后)
    '冬至': '寅',   # 农历十二月 (冬至后，下一年正月开始)
}


def get_month_zhi_by_solar_date(year: int, month: int, day: int) -> str:
    """
    根据公历日期获取农历月的月支
    
    原理：使用 lunar_python 库的 getPrevJieQi() 和 getNextJieQi() 方法
    找到当前日期前后的节气，判断所在的农历月份
    
    参数:
        year: 年
        month: 月(1-12)
        day: 日(1-31)
    
    返回:
        月支（子、丑、寅...亥）
    """
    if Solar is None:
        return '卯'  # 默认返回卯月
    
    try:
        solar = Solar.fromYmdHms(year, month, day, 12, 0, 0)
        lunar = solar.getLunar()
        
        # 获取下一个节气（更准确）
        next_jieqi = lunar.getNextJieQi(True)
        
        if next_jieqi:
            jieqi_name = next_jieqi.getName()
            # 根据下一个节气推断当前月支
            for jieqi_key, zhi in JIEQI_TO_MONTH_ZHI.items():
                if jieqi_key in jieqi_name:
                    return zhi
        
        # 备选方案：根据农历月份推导
        lunar_month = lunar.getMonth()
        zhi_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        lunar_month_abs = abs(lunar_month)
        month_zhi_idx = (lunar_month_abs - 1 + 2) % 12  # 农历正月 -> 寅月
        return zhi_list[month_zhi_idx]
    
    except Exception as e:
        print(f"节气查询失败: {e}")
        return '卯'


def get_jieqi_info(year: int, month: int, day: int) -> dict:
    """获取当前日期的节气信息"""
    if Solar is None:
        return {
            'prev_jieqi': None,
            'next_jieqi': None,
            'month_zhi': '卯'
        }
    
    try:
        solar = Solar.fromYmdHms(year, month, day, 12, 0, 0)
        lunar = solar.getLunar()
        
        prev_jieqi_obj = lunar.getPrevJieQi(True)
        next_jieqi_obj = lunar.getNextJieQi(True)
        
        prev_jieqi = None
        next_jieqi = None
        
        if prev_jieqi_obj:
            prev_solar = prev_jieqi_obj.getSolar()
            prev_jieqi = {
                'name': prev_jieqi_obj.getName(),
                'date': f'{prev_solar.getYear()}-{prev_solar.getMonth():02d}-{prev_solar.getDay():02d}'
            }
        
        if next_jieqi_obj:
            next_solar = next_jieqi_obj.getSolar()
            next_jieqi = {
                'name': next_jieqi_obj.getName(),
                'date': f'{next_solar.getYear()}-{next_solar.getMonth():02d}-{next_solar.getDay():02d}'
            }
        
        month_zhi = get_month_zhi_by_solar_date(year, month, day)
        
        return {
            'prev_jieqi': prev_jieqi,
            'next_jieqi': next_jieqi,
            'month_zhi': month_zhi
        }
    
    except Exception as e:
        print(f"节气信息获取失败: {e}")
        return {
            'prev_jieqi': None,
            'next_jieqi': None,
            'month_zhi': '卯'
        }


if __name__ == '__main__':
    print("【测试】1995年09月04日的月支和节气信息")
    info = get_jieqi_info(1995, 9, 4)
    print(f"  前一个节气: {info['prev_jieqi']}")
    print(f"  下一个节气: {info['next_jieqi']}")
    print(f"  月支: {info['month_zhi']}")
    print(f"  期望月支: 申")
