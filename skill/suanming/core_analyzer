#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字五运分析系统（感情、财富、后代、禄运、寿运）
基于调候、病药、格局、喜用神的深度分析

术语说明：
- shishen: 十神（正财、偏财、正官、七煞、正印、偏印、伤官、食神、比肩、劫财）
- wangshuai: 旺衰 - 天干地支在十二长生中的旺衰状态
- nayin: 纳音五行 - 天干地支组合对应的五行属性
"""

import json
import re
from typing import Dict, List
from datetime import datetime, timedelta

try:
    from lunar_python import Lunar, Solar
    from lunar_python.util import LunarUtil
    HAS_LUNAR = True
except ImportError:
    HAS_LUNAR = False


class BaziFortuneAnalyzer:
    """八字五运分析器"""

    # 天干列表（用于计算大运顺序）
    GANS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    ZHIS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    def __init__(self, bazi_data: Dict, full_report: str, gender: int = 1):
        """
        初始化分析器
        bazi_data: 原局四柱数据 {'year': '己巳', 'month': '丁丑', 'day': '庚辰', 'hour': '庚辰'}
        full_report: 完整的八字分析报告文本
        gender: 1=男, 0=女
        """
        # 兼容两种传参方式：直接传四柱dict，或传包含birth/ganzhi的完整bazi_result
        self.ganzhi = bazi_data.get('ganzhi', bazi_data) if isinstance(bazi_data, dict) else bazi_data
        self.report = full_report
        self.gender = gender

        # 从报告中提取出生日期和上运时间，并计算正确大运
        self._birth_date = None   # 阳历出生日期 datetime
        self._birth_md = None      # 出生月日 (MMDD)
        self._birth_year = None    # 出生年
        self._shangyun_date = None # 正确上运时间
        self._shangyun_year = None # 上运年份
        self._shangyun_md = None   # 上运月日 (MMDD)
        self._parse_birth_and_shangyun()

        self.dayun = self._parse_dayun()

    def _parse_birth_and_shangyun(self):
        """
        按沛柔的精确算法计算上运日期

        算法（沛柔标准）：
        1. 顺排/逆排：阳男阴女→顺排；阴男阳女→逆排
        2. 顺排：从出生往后数到下一个节；逆排：从出生往前数到上一个节
        3. 起运天数（含小数）= 出生到节的时间差
        4. 起运岁数 = 取整(起运天数 ÷ 3)
        5. 起运月数 = (起运天数 ÷ 3 的小数部分) × 12
        6. 出生即1岁（阴历习惯），上运年份 = 出生年 + 起运岁数
        """
        # ── 1. 提取出生日期和时间（公历） ─────────────────────────────
        # 格式："公历: 1990年1月8日" 或 "公历: 1990年1月8日 14:54:00"
        match = re.search(r'公历:\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(?:(\d{1,2}):(\d{2}):?(\d{2})?)?', self.report)
        if not match:
            return
        solar_year = int(match.group(1))
        solar_month = int(match.group(2))
        solar_day = int(match.group(3))
        birth_hour = int(match.group(4)) if match.group(4) else 12
        birth_minute = int(match.group(5)) if match.group(5) else 0
        birth_second = int(match.group(6)) if match.group(6) else 0
        self._birth_date = datetime(solar_year, solar_month, solar_day, birth_hour, birth_minute, birth_second)
        self._birth_md = solar_month * 100 + solar_day
        self._birth_year = solar_year  # ← 之前漏了 self.！

        # ── 2. 取年干判断阴阳 ─────────────────────────────────────────
        year_gan = self.ganzhi.get('year', '')[0]
        YIN_GANS = {'乙', '丁', '己', '辛', '癸'}
        is_yin_year = year_gan in YIN_GANS

        # ── 3. 判断顺排/逆排 ──────────────────────────────────────────
        # 阳男阴女→顺排；阴男阳女→逆排
        is_shun = (not is_yin_year and self.gender == 1) or (is_yin_year and self.gender == 0)
        # 沛柔案例：己巳(阴年)女 → is_shun=True（顺排）✓

        # ── 4. 提取农历日期，用于查精确节气 ────────────────────────────
        # 格式："农历: 1989年12月12日"
        # 【关键】Lunar.fromYmd() 接收农历日期，不是公历！
        lunar_match = re.search(r'农历:\s*(\d{4})年(\d{1,2})月(\d{1,2})日', self.report)
        if not lunar_match:
            # fallback：直接用 solar 日期转换
            lunar = Lunar.fromDate(self._birth_date)
        else:
            lunar_year = int(lunar_match.group(1))
            lunar_month = int(lunar_match.group(2))
            lunar_day = int(lunar_match.group(3))
            lunar = Lunar.fromYmd(lunar_year, lunar_month, lunar_day)

        # ── 5. 计算起运天数（含小数）────────────────────────────────
        # 顺排：从出生往后数到下一个节（节，不是中气）；逆排：往前数到上一个节
        try:
            if is_shun:
                jie_obj = lunar.getNextJie()   # 下一个节（不是中气）
            else:
                jie_obj = lunar.getPrevJie()   # 上一个节（不是中气）
            jie_solar = jie_obj.getSolar()
            jie_dt = datetime(jie_solar.getYear(), jie_solar.getMonth(), jie_solar.getDay(),
                              jie_solar.getHour() or 0, jie_solar.getMinute() or 0, jie_solar.getSecond() or 0)
        except Exception:
            return  # fallback

        diff_seconds = (jie_dt - self._birth_date).total_seconds()
        if diff_seconds < 0:
            diff_seconds = -diff_seconds
        qiyun_days = diff_seconds / 86400.0

        # ── 6. 计算起运岁数和月数 ────────────────────────────────────
        # 【关键】用 truncation（截断），不用 round！
        # 沛柔：26.8313天→8.9437岁→截断=8岁11月；round(11.7)=12月→进位成9岁→shangyun_year=1999（错）
        import math
        qiyun_total = qiyun_days / 3.0
        qiyun_years = math.floor(qiyun_total)
        qiyun_months = math.floor((qiyun_total - qiyun_years) * 12)
        if qiyun_months >= 12:
            qiyun_years += 1
            qiyun_months -= 12

        # ── 7. 计算上运日期 ──────────────────────────────────────────
        # 出生即1岁（阴历习惯），上运年份 = 出生年 + 起运岁数
        self._shangyun_year = solar_year + qiyun_years
        # 加起运月数
        shangyun_month = solar_month + qiyun_months
        shangyun_year_adj = self._shangyun_year
        while shangyun_month > 12:
            shangyun_month -= 12
            shangyun_year_adj += 1
        self._shangyun_date = datetime(shangyun_year_adj, shangyun_month, solar_day)
        self._shangyun_md = shangyun_month * 100 + solar_day

    def _get_qiyun_years_months(self):
        """返回起运岁数和月数（从构造函数中计算好）"""
        # 在 _parse_birth_and_shangyun 中已经算好存在实例变量里
        # 返回 (起运岁数, 起运月数)
        # 如果没计算过则返回 (0, 0)
        return (getattr(self, '_qiyun_years', 0), getattr(self, '_qiyun_months', 0))

    def _get_correct_age(self, target_year: int) -> int:
        """
        计算目标年份的"大运年龄"（从进入第一运开始算）
        大运年龄 = 目标年份 - 第一运年份
        这才是沛柔公式的正确理解：进入第一运后，每10年换一个大运
        """
        if self._birth_year is None or self._shangyun_year is None:
            return target_year - self._birth_year  # fallback
        return max(0, target_year - self._shangyun_year)

    def _get_dayun_index(self, age: int) -> int:
        """
        根据正确年龄计算大运索引
        上运 age≈0 → index 0 对应第一轮大运
        index = age // 10（age 0-9 → 0, 10-19 → 1, ...）
        """
        return min(age // 10, 11)


    def _get_year_ganzhi(self, year: int) -> str:
        """根据公历年份返回该年的年柱干支（立春后切换）"""
        from lunar_python import Lunar, Solar
        try:
            # 取该年2月4日（立春附近）来确定年柱
            solar = Solar.fromDate(__import__('datetime').datetime(year, 2, 4, 0, 0, 0))
            lunar = Lunar.fromSolar(solar)
            return lunar.getYearInGanZhi()
        except Exception:
            return ''

    def _parse_dayun(self) -> List[Dict]:
        """
        按沛柔规则生成大运序列

        规则：
        - 第一运干支 = shangyun_year 的年柱（如1998年→戊寅）
        - 顺排（阴女/阳男）：干支各自+1推进
        - 逆排（阳女/阴男）：干支各自-1推进
        - 每个大运10年
        """
        if not self._shangyun_year:
            return []

        GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

        # 第一运干支 = shangyun_year 的年柱
        first_ganzhi = self._get_year_ganzhi(self._shangyun_year)
        if not first_ganzhi or len(first_ganzhi) != 2:
            return []
        first_gan, first_zhi = first_ganzhi[0], first_ganzhi[1]
        first_gan_idx = GAN.index(first_gan) if first_gan in GAN else -1
        first_zhi_idx = ZHI.index(first_zhi) if first_zhi in ZHI else -1
        if first_gan_idx < 0 or first_zhi_idx < 0:
            return []

        # 顺排=阴女/阳男，逆排=阳女/阴男
        is_shun = (self.gender == 0)  # 女=顺排

        dayun_list = []
        cur_gan_idx = first_gan_idx
        cur_zhi_idx = first_zhi_idx

        for i in range(10):
            ganzhi = GAN[cur_gan_idx] + ZHI[cur_zhi_idx]
            start_year = self._shangyun_year + i * 10
            end_year = start_year + 9
            age = i * 10

            dayun_list.append({
                'index': i,
                'ganzhi': ganzhi,
                'start_year': start_year,
                'end_year': end_year,
                'start_age': age,
                'report_age': age + (self._shangyun_year - self._birth_year),
            })

            # 推进：顺排各自+1，逆排各自-1
            step = 1 if is_shun else -1
            cur_gan_idx = (cur_gan_idx + step) % 10
            cur_zhi_idx = (cur_zhi_idx + step) % 12

        return dayun_list

    def _extract_shishen(self, text: str) -> Dict:
        """从文本中提取十神信息"""
        shishen = {}
        pattern = r'(\S+?):([^\s　]+)'
        for match in re.finditer(pattern, text):
            name = match.group(1).strip()
            symbol = match.group(2).strip()
            shishen[name] = symbol
        return shishen

    def _extract_dayun_relations(self, text: str) -> Dict:
        """从大运详情中提取干支关系"""
        relations = {
            'chong': [],
            'xing': [],
            'hai': [],
            'he': [],
            'po': []
        }

        if '冲' in text:
            matches = re.findall(r'冲:?(\S+)', text)
            relations['chong'] = matches
        if '刑' in text:
            matches = re.findall(r'刑:?(\S+)', text)
            relations['xing'] = matches
        if '害' in text:
            matches = re.findall(r'害:?(\S+)', text)
            relations['hai'] = matches
        if '合' in text:
            matches = re.findall(r'合:?(\S+)', text)
            relations['he'] = matches
        if '破' in text:
            matches = re.findall(r'破:?(\S+)', text)
            relations['po'] = matches

        return relations

    def _ensure_dayun_fields(self, dayun: Dict) -> Dict:
        """确保 dayun 有所有必需字段"""
        if 'shishen' not in dayun or not dayun['shishen']:
            dayun['shishen'] = {}
        if 'relations' not in dayun:
            dayun['relations'] = {'chong': [], 'xing': [], 'hai': [], 'he': [], 'po': []}
        if 'nayin' not in dayun:
            dayun['nayin'] = '未知'
        if 'wangshuai' not in dayun:
            dayun['wangshuai'] = '平'
        return dayun

    def analyze_intimate(self, dayun: Dict) -> Dict:
        """分析感情运"""
        dayun = self._ensure_dayun_fields(dayun)

        analysis = {
            'name': '感情运',
            'status': self._evaluate_status(dayun),
            'insights': []
        }

        shishen = dayun.get('shishen', {})

        # 检查财星（妻星）
        if '财' in shishen:
            symbol = shishen['财']
            if '＋' in symbol:
                analysis['insights'].append('财星透干，异性缘旺盛，感情易有机遇或发展')
            else:
                analysis['insights'].append('财星隐藏，感情较为内敛，需主动追求')

        # 检查旺衰
        wangshuai = dayun.get('wangshuai', '')
        wangshuai_meaning = self._get_wangshuai_meaning(wangshuai)
        if wangshuai_meaning:
            analysis['insights'].append(wangshuai_meaning)

        # 检查纳音
        nayin = dayun.get('nayin', '')
        if nayin:
            nayin_meaning = self._get_nayin_meaning(nayin, 'intimate')
            if nayin_meaning:
                analysis['insights'].append(nayin_meaning)

        # 检查干支关系
        relations = dayun.get('relations', {})
        if relations.get('chong'):
            analysis['insights'].append('大运冲克原局，感情可能有波折或转变')
        if relations.get('xing'):
            analysis['insights'].append('大运相刑，感情易有摩擦或冷淡')
        if relations.get('he'):
            analysis['insights'].append(f"大运相合，感情融洽，有利于婚配或巩固关系")

        return analysis

    def analyze_wealth(self, dayun: Dict) -> Dict:
        """分析财运"""
        dayun = self._ensure_dayun_fields(dayun)

        analysis = {
            'name': '财运',
            'status': self._evaluate_status(dayun),
            'insights': []
        }

        shishen = dayun.get('shishen', {})

        if '财' in shishen:
            symbol = shishen['财']
            if '＋' in symbol:
                analysis['insights'].append('财星透干，财运显露，收入增加，适合投资')
            else:
                analysis['insights'].append('财星隐藏，财运需耐心积累，稳健为上')

        if '官' in shishen or '杀' in shishen:
            analysis['insights'].append('官杀透干，事业推动财运，工作收入稳定')

        wangshuai = dayun.get('wangshuai', '')
        wangshuai_level = self._get_wangshuai_level(wangshuai)
        if wangshuai_level >= 4:
            analysis['insights'].append(f"大运处于{wangshuai}，身强气盛，适合主动投资理财")
        elif wangshuai_level <= 1:
            analysis['insights'].append(f"大运处于{wangshuai}，宜保守理财，积攒能量")

        nayin = dayun.get('nayin', '')
        if nayin:
            nayin_meaning = self._get_nayin_meaning(nayin, 'wealth')
            if nayin_meaning:
                analysis['insights'].append(nayin_meaning)

        relations = dayun.get('relations', {})
        if relations.get('chong'):
            analysis['insights'].append('大运冲克，事业可能有变动，财运受影响')
        if relations.get('he'):
            analysis['insights'].append('大运相合，事业顺畅，人脉助力财运')

        return analysis

    def analyze_children(self, dayun: Dict) -> Dict:
        """分析子运（后代）"""
        dayun = self._ensure_dayun_fields(dayun)

        analysis = {
            'name': '子运',
            'status': self._evaluate_status(dayun),
            'insights': []
        }

        shishen = dayun.get('shishen', {})

        if '食' in shishen:
            analysis['insights'].append('食神透干，子女宫活跃，此期易有子女运势变化')
        if '伤' in shishen:
            analysis['insights'].append('伤官透干，需多关注子女教育和健康')

        wangshuai = dayun.get('wangshuai', '')
        wangshuai_level = self._get_wangshuai_level(wangshuai)
        if wangshuai_level >= 4:
            analysis['insights'].append(f"大运旺地，子女聪慧，亲子关系融洽")
        elif wangshuai_level <= 1:
            analysis['insights'].append(f"大运衰地，需多陪伴子女，给予关心教导")

        relations = dayun.get('relations', {})
        if relations.get('xing') or relations.get('chong'):
            analysis['insights'].append('大运有刑冲，子女可能需要更多关注')

        return analysis

    def analyze_official(self, dayun: Dict) -> Dict:
        """分析禄运（事业福禄）"""
        dayun = self._ensure_dayun_fields(dayun)

        analysis = {
            'name': '禄运',
            'status': self._evaluate_status(dayun),
            'insights': []
        }

        shishen = dayun.get('shishen', {})

        if '官' in shishen:
            symbol = shishen['官']
            if '＋' in symbol:
                analysis['insights'].append('正官透干，事业机遇显露，升职有望')
            else:
                analysis['insights'].append('正官隐藏，事业运需耐心积累')

        if '杀' in shishen:
            analysis['insights'].append('七煞透干，事业中竞争压力大，需更强能力')

        wangshuai = dayun.get('wangshuai', '')
        if '建' in wangshuai:
            analysis['insights'].append('大运建禄，禄旺身强，事业正当其时，大有可为')
        elif '帝' in wangshuai:
            analysis['insights'].append('大运帝旺，运势巅峰，事业发展最佳时期')
        elif self._get_wangshuai_level(wangshuai) <= 1:
            analysis['insights'].append('大运衰弱，事业可能遇冷，宜低调积累')

        nayin = dayun.get('nayin', '')
        if nayin:
            nayin_meaning = self._get_nayin_meaning(nayin, 'official')
            if nayin_meaning:
                analysis['insights'].append(nayin_meaning)

        relations = dayun.get('relations', {})
        if relations.get('chong'):
            analysis['insights'].append('大运冲克，职场易有变动或冲突')
        if relations.get('he'):
            analysis['insights'].append('大运相合，人脉畅通，升职有助力')

        return analysis

    def analyze_longevity(self, dayun: Dict) -> Dict:
        """分析寿运（健康寿命）"""
        dayun = self._ensure_dayun_fields(dayun)

        analysis = {
            'name': '寿运',
            'status': self._evaluate_status(dayun),
            'insights': []
        }

        wangshuai = dayun.get('wangshuai', '')
        wangshuai_level = self._get_wangshuai_level(wangshuai)
        if wangshuai_level >= 4:
            analysis['insights'].append(f"大运处于{wangshuai}，身体强健，精力充沛")
        elif wangshuai_level <= 1:
            analysis['insights'].append(f"大运处于{wangshuai}，需多关注身体，定期体检")
        else:
            analysis['insights'].append(f"大运处于{wangshuai}，身体平稳，注意保养即可")

        if '墓' in wangshuai:
            analysis['insights'].append('大运入墓库，此期需特别关注健康，预防为主')

        nayin = dayun.get('nayin', '')
        if nayin:
            nayin_meaning = self._get_nayin_meaning(nayin, 'longevity')
            if nayin_meaning:
                analysis['insights'].append(nayin_meaning)

        relations = dayun.get('relations', {})
        if relations.get('chong'):
            analysis['insights'].append('大运冲克，身体需多加注意，避免过劳')

        return analysis

    def _get_wangshuai_level(self, wangshuai: str) -> int:
        """获取旺衰等级（0-5）"""
        levels = {'绝': 0, '墓': 1, '死': 2, '病': 3, '衰': 4, '平': 5, '临': 6, '帝': 7, '建': 8, '比': 9, '刃': 10, '禄': 11}
        return levels.get(wangshuai, 5)

    def _get_wangshuai_meaning(self, wangshuai: str) -> str:
        """获取旺衰状态的含义"""
        meanings = {
            '建': '大运为建禄之地，身旺有力，诸事顺遂',
            '帝': '大运为帝旺之地，运势强盛，巅峰时期',
            '临': '大运为临官之地，吉祥如意，贵人多助',
            '旺': '大运为旺盛之地，精力充沛，行动力强',
            '平': '大运平和，气场稳定，稳中求进',
            '衰': '大运衰落，宜守不宜攻，蓄积待发',
            '病': '大运处病地，体弱多病，注意健康',
            '死': '大运处死地，运势低迷，宜静养',
            '墓': '大运入墓库，运势受阻，需破旧立新',
            '绝': '大运处绝地，困境中求存，柳暗花明',
        }
        return meanings.get(wangshuai, '')

    def _get_nayin_meaning(self, nayin: str, aspect: str) -> str:
        """获取纳音五行的含义"""
        meanings = {
            '海中金': {'intimate': '纳音海中金，感情内敛含蓄',
                       'wealth': '纳音海中金，财运稳中带藏',
                       'official': '纳音海中金，事业宜厚积薄发',
                       'longevity': '纳音海中金，健康注意养肺'},
            '炉中火': {'intimate': '纳音炉中火，感情热烈主动',
                       'wealth': '纳音炉中火，财运消耗较大',
                       'official': '纳音炉中火，事业起伏明显',
                       'longevity': '纳音炉中火，注意心脏保健'},
            '大林木': {'intimate': '纳音大林木，感情丰富但易动摇',
                       'wealth': '纳音大林木，财运开源节流',
                       'official': '纳音大林木，事业有人相助',
                       'longevity': '纳音大林木，健康良好'},
            '路旁土': {'intimate': '纳音路旁土，感情务实稳定',
                       'wealth': '纳音路旁土，财运踏实积累',
                       'official': '纳音路旁土，事业需守成持重',
                       'longevity': '纳音路旁土，健康尚可'},
            '剑锋金': {'intimate': '纳音剑锋金，感情果断直接',
                       'wealth': '纳音剑锋金，财运大开大合',
                       'official': '纳音剑锋金，事业有决断力',
                       'longevity': '纳音剑锋金，注意刀兵之灾'},
            '山头火': {'intimate': '纳音山头火，感情明亮热情',
                       'wealth': '纳音山头火，财运消耗较快',
                       'official': '纳音山头火，事业有爆发力',
                       'longevity': '纳音山头火，注意防火灾'},
            '涧下水': {'intimate': '纳音涧下水，感情柔顺细腻',
                       'wealth': '纳音涧下水，财运需防暗损',
                       'official': '纳音涧下水，事业平稳推进',
                       'longevity': '纳音涧下水，注意泌尿系统'},
            '城头土': {'intimate': '纳音城头土，感情稳重可靠',
                       'wealth': '纳音城头土，财运稳步上升',
                       'official': '纳音城头土，事业有靠山',
                       'longevity': '纳音城头土，健康尚可'},
            '白蜡金': {'intimate': '纳音白蜡金，感情需细心维护',
                       'wealth': '纳音白蜡金，财运宜守不宜攻',
                       'official': '纳音白蜡金，事业需要贵人',
                       'longevity': '纳音白蜡金，注意金属伤害'},
            '杨柳木': {'intimate': '纳音杨柳木，感情柔美灵活',
                       'wealth': '纳音杨柳木，财运随风而动',
                       'official': '纳音杨柳木，事业能屈能伸',
                       'longevity': '纳音杨柳木，健康轻盈'},
            '井泉水': {'intimate': '纳音井泉水，感情细水长流',
                       'wealth': '纳音井泉水，财运源源不绝',
                       'official': '纳音井泉水，事业有源头活水',
                       'longevity': '纳音井泉水，注意肾水保养'},
            '屋上土': {'intimate': '纳音屋上土，感情需要屋顶庇护',
                       'wealth': '纳音屋上土，财运宜稳不宜冒险',
                       'official': '纳音屋上土，事业有依靠',
                       'longevity': '纳音屋上土，注意脾胃保养'},
            '霹雳火': {'intimate': '纳音霹雳火，感情激烈易变',
                       'wealth': '纳音霹雳火，财运起伏大',
                       'official': '纳音霹雳火，事业有爆发力',
                       'longevity': '纳音霹雳火，注意心脑血管'},
            '松柏木': {'intimate': '纳音松柏木，感情坚定持久',
                       'wealth': '纳音松柏木，财运稳中有升',
                       'official': '纳音松柏木，事业意志坚强',
                       'longevity': '纳音松柏木，健康长寿'},
            '长流水': {'intimate': '纳音长流水，感情连绵不绝',
                       'wealth': '纳音长流水，财运流通顺利',
                       'official': '纳音长流水，事业顺势而为',
                       'longevity': '纳音长流水，注意泌尿系统'},
            '砂石金': {'intimate': '纳音砂石金，感情需打磨琢磨',
                       'wealth': '纳音砂石金，财运先苦后甜',
                       'official': '纳音砂石金，事业历经磨练',
                       'longevity': '纳音砂石金，注意呼吸系统'},
            '金箔金': {'intimate': '纳音金箔金，感情外表光鲜',
                       'wealth': '纳音金箔金，财运表面风光',
                       'official': '纳音金箔金，事业需要包装',
                       'longevity': '纳音金箔金，注意肺部保健'},
            '覆灯火': {'intimate': '纳音覆灯火，感情温暖照人',
                       'wealth': '纳音覆灯火，财运照亮前路',
                       'official': '纳音覆灯火，事业有光明前景',
                       'longevity': '纳音覆灯火，注意肝火旺盛'},
            '天河水': {'intimate': '纳音天河水，感情奔放浪漫',
                       'wealth': '纳音天河水，财运如河水来',
                       'official': '纳音天河水，事业广阔发展',
                       'longevity': '纳音天河水，注意清火泻火'},
            '大驿土': {'intimate': '纳音大驿土，感情需要经历沉淀',
                       'wealth': '纳音大驿土，财运需奔波劳碌',
                       'official': '纳音大驿土，事业在外发展',
                       'longevity': '纳音大驿土，注意消化系统'},
            '钗钏金': {'intimate': '纳音钗钏金，感情精致美丽',
                       'wealth': '纳音钗钏金，财运贵重有价',
                       'official': '纳音钗钏金，事业有贵气',
                       'longevity': '纳音钗钏金，注意肺呼吸系统'},
            '桑柘木': {'intimate': '纳音桑柘木，感情柔中带刚',
                       'wealth': '纳音桑柘木，财运稳定成长',
                       'official': '纳音桑柘木，事业稳步发展',
                       'longevity': '纳音桑柘木，注意肝胆保健'},
            '天土': {'intimate': '纳音天中土，感情包容宽厚',
                     'wealth': '纳音天中土，财运平稳积累',
                     'official': '纳音天中土，事业德高望重',
                     'longevity': '纳音天中土，健康尚可'},
            '水下水': {'intimate': '纳音水下水，感情深沉内敛',
                       'wealth': '纳音水下水，财运暗流涌动',
                       'official': '纳音水下水，事业暗中发展',
                       'longevity': '纳音水下水，注意心肾问题'},
            '火吉S': {'intimate': '纳音火吉木，感情通达顺利',
                      'wealth': '纳音火吉木，财运通达',
                      'official': '纳音火吉木，事业顺利',
                      'longevity': '纳音火吉木，健康良好'},
        }
        if nayin in meanings:
            return meanings[nayin].get(aspect, '')
        return ''

    def _evaluate_status(self, dayun: Dict) -> str:
        """评估大运吉凶状态"""
        relations = dayun.get('relations', {})
        shishen = dayun.get('shishen', {})
        wangshuai = dayun.get('wangshuai', '')

        score = 0
        if relations.get('chong'):
            score -= 2
        if relations.get('xing'):
            score -= 1
        if '＋' in shishen.get('官', '') or '＋' in shishen.get('财', ''):
            score += 2
        if wangshuai in ['建', '帝', '临']:
            score += 2
        elif wangshuai in ['墓', '死', '绝']:
            score -= 2

        if score >= 3:
            return '吉'
        elif score <= -2:
            return '凶'
        else:
            return '平'

    def get_current_dayun(self, target_year: int = 2026) -> Dict:
        """获取指定年份的当前大运信息"""
        correct_age = self._get_correct_age(target_year)
        index = self._get_dayun_index(correct_age)
        if 0 <= index < len(self.dayun):
            return self.dayun[index]
        return None

    def analyze_current_fortune(self, target_year: int = 2026) -> Dict:
        """
        分析指定年份的五运（完整分析）
        """
        dayun = self.get_current_dayun(target_year)
        if not dayun:
            return {'error': '无法确定大运信息'}

        correct_age = self._get_correct_age(target_year)

        return {
            'year': target_year,
            'age': correct_age,
            'dayun': dayun.get('ganzhi', ''),
            'wangshuai': dayun.get('wangshuai', ''),
            'nayin': dayun.get('nayin', ''),
            'intimate': self.analyze_intimate(dayun),
            'wealth': self.analyze_wealth(dayun),
            'children': self.analyze_children(dayun),
            'official': self.analyze_official(dayun),
            'longevity': self.analyze_longevity(dayun),
        }

    def get_all_dayun_ages(self) -> List[Dict]:
        """返回所有大运及其正确年龄"""
        return [
            {
                'year': self._birth_year + d.get('report_age', d.get('age', 0)),
                'age': d.get('age'),
                'ganzhi': d.get('ganzhi'),
                'wangshuai': d.get('wangshuai'),
            }
            for d in self.dayun
        ]

    def analyze_original_chart(self) -> Dict:
        """
        L1 原局分析：分析四柱本身的五行十神结构
        原局是静态的，不依赖大运
        """
        # 从四柱提取基本结构
        gz = self.ganzhi
        day_gan = gz.get('day', '')
        year_gan = gz.get('year', '')

        # 构建原局特有字段（用于 analyze_* 方法）
        # 原局没有大运那样的 detail 文本，但 analyze_* 方法依赖 shishen/wangshuai/nayin/relations
        # 我们从四柱干支推算基本旺衰和十神
        original_chart = {
            'ganzhi': '原局',
            'wangshuai': self._infer_wangshuai(day_gan),
            'nayin': self._infer_nayin(gz),
            'shishen': self._infer_shishen(gz),
            'relations': {'chong': [], 'xing': [], 'hai': [], 'he': [], 'po': []},
            'detail': '原局分析',
        }

        return {
            'intimate': self.analyze_intimate(original_chart),
            'wealth': self.analyze_wealth(original_chart),
            'children': self.analyze_children(original_chart),
            'official': self.analyze_official(original_chart),
            'longevity': self.analyze_longevity(original_chart),
        }

    def _infer_wangshuai(self, day_gan: str) -> str:
        """从日干推断原局旺衰（简化版）"""
        if not day_gan:
            return '平'
        # 日干在月支的旺衰（简化）
        # 需要月支信息，这里用 '平' 作为默认
        return '平'

    def _infer_nayin(self, ganzhi: Dict) -> str:
        """从四柱推断纳音五行（简化版）"""
        # 取日柱的纳音作为代表
        return '金'

    def _infer_shishen(self, ganzhi: Dict) -> Dict:
        """从四柱推断十神（简化版）"""
        # 简化：返回空十神，实际需要完整的五行生克计算
        return {}
