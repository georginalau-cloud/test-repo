#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[22] lib/daily_fortune.py - 日运分析模块
调用层级：被 bin/bazi（daily 模式）调用
依赖：vendor/lunar_python

功能：
  1. 计算当日干支（年/月/日/时）
  2. 获取黄历宜忌、建除十二值星、吉神方位
  3. 分析当日干支与命局（原局 + 大运 + 流年 + 流月）的关系
  4. 生成日运 prompt 供 MiniMax 润色

层级：原局 → 大运 → 流年 → 流月 → 流日（完整五层）
"""

import os
import sys
from datetime import date
from typing import Dict

_LIB_DIR   = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_LIB_DIR)
sys.path.insert(0, os.path.join(_SKILL_DIR, 'vendor'))
sys.path.insert(0, os.path.join(_SKILL_DIR, 'src'))

try:
    from lunar_python import Solar
    HAS_LUNAR = True
except ImportError:
    HAS_LUNAR = False

# ─────────────────────────────────────────────────────────────────
# 常量
# ─────────────────────────────────────────────────────────────────

ZHI_CANGYGAN = {
    '子':['癸'],'丑':['己','癸','辛'],'寅':['甲','丙','戊'],
    '卯':['乙'],'辰':['戊','乙','癸'],'巳':['丙','戊','庚'],
    '午':['丁','己'],'未':['己','丁','乙'],'申':['庚','壬','戊'],
    '酉':['辛'],'戌':['戊','辛','丁'],'亥':['壬','甲'],
}
CHONG = {
    '子':'午','午':'子','丑':'未','未':'丑',
    '寅':'申','申':'寅','卯':'酉','酉':'卯',
    '辰':'戌','戌':'辰','巳':'亥','亥':'巳',
}
HE6 = {
    '子':'丑','丑':'子','寅':'亥','亥':'寅',
    '卯':'戌','戌':'卯','辰':'酉','酉':'辰',
    '巳':'申','申':'巳','午':'未','未':'午',
}
XING = {
    '子':'卯','卯':'子',
    '寅':'巳','巳':'申','申':'寅',
    '丑':'戌','戌':'未','未':'丑',
}
SANHE = [
    ({'申','子','辰'}, '水局'),
    ({'寅','午','戌'}, '火局'),
    ({'巳','酉','丑'}, '金局'),
    ({'亥','卯','未'}, '木局'),
]
DIRECTION_CN = {
    '艮':'东北','震':'正东','巽':'东南','离':'正南',
    '坤':'西南','兑':'正西','乾':'西北','坎':'正北','中':'中央',
}
LUCKY_COLORS = {
    '木':['绿色','青色'],'火':['红色','橙色','紫色'],
    '土':['黄色','棕色','米色'],'金':['白色','金色','银色'],
    '水':['黑色','深蓝色','灰色'],
}
# 按十神大类的幸运色优先级（用于流日动态调整）
SHISHEN_COLOR_HINTS = {
    '官': '金（白色、金色、银色），提升贵气与决策力',
    '杀': '金+水组合，白色金色纳气，紫黑色化煞',
    '财': '火（红橙紫）旺财，赤红色系开运',
    '才': '火（红橙紫）旺偏财，忌绿色青色的散财色',
    '食': '土（黄色、棕色）生金，忌辛辣冲胃',
    '伤': '金（白色、金色）制伤，忌红色橙色过旺',
    '印': '金水（白、黑）养印，忌土色过重沉闷',
    '枭': '水（黑、深蓝）化枭，忌土色克水',
    '比': '金水（白、黑）润比，忌火色过旺冲动',
    '劫': '水（黑、深蓝）化劫，忌红色冲动色',
}
# 食物按十神推荐
SHISHEN_FOOD_HINTS = {
    '官': '清淡养胃（小米粥、莲子、山药），忌辛辣',
    '杀': '白色食物（银耳、百合、梨）化煞，忌红油重口',
    '财': '红色系食物（红枣、枸杞、红豆）旺财',
    '才': '红色系+高蛋白（羊肉、牛肉、红椒）旺偏财',
    '食': '黄色系（玉米、南瓜、黄豆）养脾，忌生冷',
    '伤': '白色润肺（梨、银耳、百合），忌辛辣刺激',
    '印': '黑色系（黑豆、黑木耳、海带）养印，忌过咸',
    '枭': '水润食品（莲子心茶、薏米水）化枭，忌油炸',
    '比': '黑色食品（黑芝麻糊、黑豆）润比，忌熬夜',
    '劫': '水+收敛（蜂蜜水、百合、梨）化躁，忌刺激性',
}
# 流日干支五行权重（用于判断当日能量侧重）
STEM_WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WUXING = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
SHISHEN_FULL = {
    '比':'比肩','劫':'劫财','食':'食神','伤':'伤官',
    '才':'偏财','财':'正财','杀':'七杀','官':'正官',
    '枭':'偏印','印':'正印','日主':'日主',
}


# ─────────────────────────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────────────────────────

def _get_interactions(zhi_a, zhi_set):
    notes = []
    for zhi_b in zhi_set:
        if zhi_b == zhi_a:
            continue
        if CHONG.get(zhi_a) == zhi_b:
            notes.append({'type':'冲','desc':f'{zhi_a}冲{zhi_b}','effect':'动荡变化，需防意外'})
        if HE6.get(zhi_a) == zhi_b:
            notes.append({'type':'合','desc':f'{zhi_a}合{zhi_b}','effect':'有助力，贵人相助'})
        if XING.get(zhi_a) == zhi_b:
            notes.append({'type':'刑','desc':f'{zhi_a}刑{zhi_b}','effect':'摩擦压力，需谨慎'})
    for members, ju_name in SANHE:
        if zhi_a in members and members.issubset(zhi_set | {zhi_a}):
            notes.append({'type':'三合','desc':f'三合{ju_name}','effect':'力量聚合，大有助益'})
            break
    return notes


def _score_day(day_gz, day_gan, all_zhis):
    from .ten_gods_analyzer import get_ten_god
    if not day_gz or len(day_gz) < 2:
        return {}
    gan, zhi = day_gz[0], day_gz[1]
    shishen_gan  = get_ten_god(day_gan, gan)
    cangygan     = ZHI_CANGYGAN.get(zhi, [])
    shishen_zhi  = get_ten_god(day_gan, cangygan[0]) if cangygan else ''
    interactions = _get_interactions(zhi, all_zhis)

    score = 0
    notes = []
    GOOD = {'印','枭','官','财','才','食'}
    BAD  = {'杀','劫','伤'}
    if shishen_gan in GOOD:
        score += 1
        notes.append(f'日干{gan}（{SHISHEN_FULL.get(shishen_gan,shishen_gan)}）对命局有利')
    elif shishen_gan in BAD:
        score -= 1
        notes.append(f'日干{gan}（{SHISHEN_FULL.get(shishen_gan,shishen_gan)}）需注意压力')

    for inter in interactions:
        if inter['type'] == '冲':
            score -= 2
            notes.append(f"{inter['desc']}，{inter['effect']}")
        elif inter['type'] == '合':
            score += 1
            notes.append(f"{inter['desc']}，{inter['effect']}")
        elif inter['type'] == '刑':
            score -= 1
            notes.append(f"{inter['desc']}，{inter['effect']}")
        elif inter['type'] == '三合':
            score += 2
            notes.append(f"{inter['desc']}，{inter['effect']}")

    rating = '吉' if score >= 2 else ('需防' if score < 0 else '平')
    return {
        'score': score, 'rating': rating,
        'shishen_gan': shishen_gan, 'shishen_zhi': shishen_zhi,
        'interactions': interactions, 'notes': notes,
    }


# ─────────────────────────────────────────────────────────────────
# 动态幸运色/食物计算
# ─────────────────────────────────────────────────────────────────

def _compute_lucky(day_gan, day_gan_shishen, day_zhi_shishen, day_zhi, day_cangygan,
                   yong_shen, yong_wuxing,
                   has_chong, has_xing, has_he, has_sanhe,
                   day_analysis):
    """
    根据流日十神与命局的互动关系，动态计算当日幸运色、食物、方位说明。

    核心思路：
    - 流日天干决定当日能量主轴（财？官？食？伤？）
    - 流日地支与命局的冲合决定能量强弱（冲则强刑则压力，合则稳定）
    - 用神色为基础底色，流日十神色为当日强化色，忌神色为规避色
    """
    add_colors = []    # 需要加强的颜色
    avoid_colors = []  # 需要规避的颜色
    foods = []         # 食物建议
    note_parts = []    # 说明文字片段

    # 基础底色：用神五行对应色
    base_colors = LUCKY_COLORS.get(yong_shen, [])

    # ── 1. 流日天干十神主导 ──────────────────────────────────────────
    gan_hint = SHISHEN_COLOR_HINTS.get(day_gan_shishen, '')
    if gan_hint:
        note_parts.append(f'今日天干{day_gan_shishen}当令，{gan_hint}')

    food_hint = SHISHEN_FOOD_HINTS.get(day_gan_shishen, '')
    if food_hint:
        foods.append(food_hint)

    # ── 2. 流日地支藏干副十神（影响藏干食物） ─────────────────────────
    if day_cangygan and len(day_cangygan) > 1:
        # 多藏干（杂气月），说明日子能量复杂，提醒注意
        cang_shishen = [get_ten_god_cached(day_cangygan[i])(day_gan) for i in range(len(day_cangygan))]
        note_parts.append(f'地支{day_zhi}藏多气（{"、".join(cang_shishen)}），今日能量多元，需抓主要矛盾')

    # ── 3. 刑冲合影响幸运色强度 ──────────────────────────────────────
    if has_chong:
        # 有冲 → 能量强且动荡，颜色要收敛一些，不宜过旺
        # 冲代表变化和压力，可加强金水色（白、黑）来稳定
        add_colors += ['白色','金色']
        avoid_colors += ['大红色','正红色']
        note_parts.append('今日地支与命局有冲，能量强动，宜静不宜躁，白金色系可稳住气场')
    elif has_xing:
        # 有刑 → 压力和摩擦，加强金色化煞
        add_colors += ['白色','银色']
        avoid_colors += ['红色','橙色']
        note_parts.append('今日地支与命局有刑，压力略重，白银色系化煞，忌火色过旺冲动')
    elif has_he or has_sanhe:
        # 合/三合 → 能量稳定汇聚，可适当加强用神色
        note_parts.append('今日地支与命局有合，运势稳聚，用神火色可以发挥')

    # ── 4. 用神忌神动态调整 ──────────────────────────────────────────
    # 如果流日十神是用神相关的，强化之；是忌神相关的，规避之
    GOOD_SHISHEN = {'官','财','才','食','印','比'}  # 用神常见十神
    BAD_SHISHEN  = {'杀','劫','伤','枭'}             # 忌神常见十神

    if day_gan_shishen in GOOD_SHISHEN:
        # 用神相关的十神，可以加强对应色
        yong_colors = LUCKY_COLORS.get(yong_shen, [])
        add_colors += yong_colors
        note_parts.append(f'今日天干{day_gan_shishen}与命局用神相和，运势佳，用神色可以放心用')
    elif day_gan_shishen in BAD_SHISHEN:
        # 忌神相关的十神，需要用相克色来化解
        # 如杀重→白金；伤重→金色；劫重→水色
        if day_gan_shishen == '杀':
            add_colors += ['白色','金色','黑色']
            avoid_colors += ['红色','橙色']
            note_parts.append('七杀当令日，白金黑色系化杀，忌红色火色激化')
        elif day_gan_shishen == '伤':
            add_colors += ['白色','金色']
            avoid_colors += ['红色','紫色']
            note_parts.append('伤官当令日，金白色制伤，忌火色过旺')
        elif day_gan_shishen == '劫':
            add_colors += ['黑色','深蓝色']
            avoid_colors += ['红色','橙色']
            note_parts.append('劫财当令日，黑深蓝色收敛，忌冲动火色')
        elif day_gan_shishen == '枭':
            add_colors += ['黑色','深蓝色']
            avoid_colors += ['黄色','棕色']
            note_parts.append('枭神当令日，水黑色化枭，忌土色克水')

    # ── 5. 综合颜色优先级合并 ────────────────────────────────────────
    final_colors = base_colors.copy()
    for c in add_colors:
        if c not in final_colors:
            final_colors.append(c)
    # 避免色从结果中移除
    final_colors = [c for c in final_colors if c not in avoid_colors]
    # 限制最多4种
    final_colors = final_colors[:4]

    note = '；'.join(note_parts) if note_parts else f'今日能量平稳，用神{yong_shen}色为主'
    return {
        'add_colors':  add_colors,
        'avoid_colors': avoid_colors,
        'foods':       '；'.join(foods) if foods else f'今日饮食清淡为宜',
        'note':         note,
    }


def _merge_lucky_colors(base_colors, add_colors, avoid_colors):
    """合并用神底色 + 流日动态调整色，避免色移除 """
    merged = list(base_colors)
    for c in add_colors:
        if c not in merged:
            merged.append(c)
    merged = [c for c in merged if c not in avoid_colors]
    return merged[:4]   # 最多4种


def get_ten_god_cached(stem):
    """已知天干查十神（供藏干分析用）"""
    from .ten_gods_analyzer import get_ten_god as _gtg
    return lambda day_gan: _gtg(day_gan, stem)


# ─────────────────────────────────────────────────────────────────
# 主分析器
# ─────────────────────────────────────────────────────────────────

class DailyFortune:
    """日运分析器，接收 bazi_chart 完整输出。"""

    def __init__(self, chart):
        self.chart   = chart
        self.day_gan = chart.get('day_gan', '')
        gender_raw   = chart.get('meta', {}).get('gender', 'male')
        self.gender  = 'male' if gender_raw.lower() in ('male','m','男') else 'female'
        pillars      = chart.get('pillars', [])
        self.yuanju_zhis = {p['zhi'] for p in pillars if 'zhi' in p}
        current          = chart.get('current', {})
        self.dayun_gz    = current.get('dayun', {}).get('ganzhi', '') if current else ''
        liuyear          = current.get('liuyear', {}) if current else {}
        self.year_gz     = liuyear.get('ganzhi', '') if liuyear else ''
        self.liu_yue     = liuyear.get('liu_yue', []) if liuyear else []

    def _get_day_data(self, target_date, hour=8):
        if not HAS_LUNAR:
            return {'error': 'vendor/lunar_python 未找到'}
        try:
            y, m, d = [int(x) for x in target_date.split('-')]
            solar   = Solar.fromYmdHms(y, m, d, hour, 0, 0)
            lunar   = solar.getLunar()
            pos     = {
                'xi':  f"{lunar.getDayPositionXi()}（{DIRECTION_CN.get(lunar.getDayPositionXi(),'')}）",
                'cai': f"{lunar.getDayPositionCai()}（{DIRECTION_CN.get(lunar.getDayPositionCai(),'')}）",
                'fu':  f"{lunar.getDayPositionFu()}（{DIRECTION_CN.get(lunar.getDayPositionFu(),'')}）",
            }
            return {
                'date':       target_date,
                'lunar_date': f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
                'ganzhi': {
                    'year':  lunar.getYearInGanZhi(),
                    'month': lunar.getMonthInGanZhi(),
                    'day':   lunar.getDayInGanZhi(),
                    'hour':  lunar.getTime().getGanZhi(),
                },
                'huangli': {
                    'yi':       lunar.getDayYi(),
                    'ji':       lunar.getDayJi(),
                    'zhi_xing': lunar.getZhiXing(),
                    'chong':    lunar.getDayChong(),
                    'sha':      lunar.getDaySha(),
                    'nayin':    lunar.getDayNaYin(),
                },
                'positions': pos,
            }
        except Exception as e:
            return {'error': str(e)}

    def _get_month_gz(self, target_date):
        if not self.liu_yue:
            return ''
        try:
            month = int(target_date.split('-')[1])
            idx   = (month - 2) % 12
            if idx < len(self.liu_yue):
                return self.liu_yue[idx].get('ganzhi', '')
        except Exception:
            pass
        return ''

    def analyze(self, target_date=None, hour=8):
        """
        分析指定日期的日运。

        参数：
          target_date: 'YYYY-MM-DD'，默认今天
          hour: 时辰（0-23），默认早8点
        """
        if not target_date:
            target_date = date.today().strftime('%Y-%m-%d')

        day_data = self._get_day_data(target_date, hour)
        if 'error' in day_data:
            return {'success': False, 'error': day_data['error']}

        day_gz   = day_data['ganzhi']['day']
        month_gz = self._get_month_gz(target_date)

        # 所有层级地支集合
        all_zhis = set(self.yuanju_zhis)
        for gz in [self.dayun_gz, self.year_gz, month_gz]:
            if gz and len(gz) >= 2:
                all_zhis.add(gz[1])

        day_analysis  = _score_day(day_gz, self.day_gan, all_zhis)
        yong_shen     = (
            self.chart.get('yong_shen', {}).get('yong_shen', '')
            or self.chart.get('analysis', {}).get('format_analysis', {}).get('yong_shen', '')
        )
        ji_shen       = (
            self.chart.get('yong_shen', {}).get('ji_shen', [])
            or self.chart.get('analysis', {}).get('format_analysis', {}).get('ji_shen', [])
        )

        # ── 流日干支分析（用于动态幸运色/食物/方位）─────────────────────
        day_gan = day_gz[0] if len(day_gz) >= 1 else ''
        day_zhi = day_gz[1] if len(day_gz) >= 2 else ''
        day_cangygan = ZHI_CANGYGAN.get(day_zhi, [])
        # 计算流日对日主构成的十神（主十神 = 天干十神；副十神 = 藏干十神，取旺者）
        from .ten_gods_analyzer import get_ten_god
        day_gan_shishen = get_ten_god(self.day_gan, day_gan) if day_gan else ''
        # 藏干十神取最旺者（按通根程度简化：第一个藏干为主）
        day_zhi_shishen = get_ten_god(self.day_gan, day_cangygan[0]) if day_cangygan else ''
        # 流日地支与命局的冲合（有冲则能量强，可加重某色）
        day_zhi_interacts = _get_interactions(day_zhi, all_zhis) if day_zhi else []
        has_chong = any(i['type'] == '冲' for i in day_zhi_interacts)
        has_xing  = any(i['type'] == '刑' for i in day_zhi_interacts)
        has_he    = any(i['type'] == '合' for i in day_zhi_interacts)
        has_sanhe = any(i['type'] == '三合' for i in day_zhi_interacts)

        # 用神/忌神五行
        yong_wuxing = STEM_WUXING.get(yong_shen, '') if len(yong_shen) == 1 else ''

        # ── 动态幸运色：根据流日十神 + 命局互动 综合判断 ─────────────────
        lucky_result = _compute_lucky(
            day_gan_shishen=day_gan_shishen,
            day_zhi_shishen=day_zhi_shishen,
            day_cangygan=day_cangygan,
            yong_shen=yong_shen,
            yong_wuxing=yong_wuxing,
            has_chong=has_chong,
            has_xing=has_xing,
            has_he=has_he,
            has_sanhe=has_sanhe,
            day_analysis=day_analysis,
        )
        lucky_colors_base = LUCKY_COLORS.get(yong_shen, [])
        # 最终幸运色 = 用神底色 + 流日动态调整（合并去重，保留优先级）
        lucky_colors = _merge_lucky_colors(lucky_colors_base, lucky_result['add_colors'], lucky_result['avoid_colors'])
        lucky_dir = day_data['positions'].get('xi', '')
        lucky_foods = lucky_result['foods']

        layers = []
        if self.dayun_gz: layers.append(f"{self.dayun_gz}大运")
        if self.year_gz:  layers.append(f"{self.year_gz}流年")
        if month_gz:      layers.append(f"{month_gz}流月")
        layers.append(f"{day_gz}流日")

        return {
            'success':      True,
            'date':         target_date,
            'day_data':     day_data,
            'month_gz':     month_gz,
            'day_analysis': day_analysis,
            'lucky': {
                'colors':    lucky_colors,
                'direction': lucky_dir,
                'cai_pos':   day_data['positions'].get('cai', ''),
                'fu_pos':    day_data['positions'].get('fu', ''),
                'foods':     lucky_foods,
                'day_gan_shishen': day_gan_shishen,
                'day_zhi_shishen': day_zhi_shishen,
                'lucky_note': lucky_result['note'],
            },
            'layer_desc':   ' → '.join(layers),
            'prompt_for_llm': self._build_prompt(
                target_date, day_data, day_analysis, month_gz, lucky_colors, lucky_dir, lucky_foods
            ),
        }

    def _build_prompt(self, target_date, day_data, day_analysis, month_gz, lucky_colors, lucky_dir, lucky_foods):
        meta    = self.chart.get('meta', {})
        gz      = self.chart.get('ganzhi', {})
        fmt     = self.chart.get('yong_shen', {})
        yong    = fmt.get('yong_shen', '') or self.chart.get('analysis', {}).get('format_analysis', {}).get('yong_shen', '')
        ji      = fmt.get('ji_shen', []) or self.chart.get('analysis', {}).get('format_analysis', {}).get('ji_shen', [])
        huangli = day_data.get('huangli', {})
        pos     = day_data.get('positions', {})
        gender_cn = '男' if meta.get('gender','').lower() in ('male','m','男') else '女'
        day_gz    = day_data['ganzhi']['day']
        rating    = day_analysis.get('rating', '平')
        notes     = day_analysis.get('notes', [])
        yi_str    = '、'.join(huangli.get('yi', [])[:5])
        ji_str    = '、'.join(huangli.get('ji', [])[:4])
        # 从lucky对象拿额外信息（由 analyze 新增）
        lucky     = getattr(self, '_last_lucky', {})
        day_gan_shishen = lucky.get('day_gan_shishen', '')
        day_zhi_shishen = lucky.get('day_zhi_shishen', '')
        lucky_note      = lucky.get('lucky_note', '')

        lucky_colors_str = ''.join(lucky_colors) if lucky_colors else ''
        lucky_note_block = f'\n## 今日幸运提示说明\n  {lucky_note}' if lucky_note else ''
        notes_block = '\n'.join(f'- {n}' for n in notes) if notes else '- 今日干支与命局无明显刑冲，运势平稳'
        ji_str_joined = '、'.join(ji) if ji else ''
        month_gz_block = f' × {month_gz}流月' if month_gz else ''

        return f"""你是一位精通子平八字的命理师，请为以下用户写一份简洁有温度的日运分析。

## 用户命盘
- 四柱：年{gz.get('year','')} 月{gz.get('month','')} 日{gz.get('day','')} 时{gz.get('hour','')}（{gender_cn}命）
- 日主：{self.day_gan}  用神：{yong}  忌神：{ji_str_joined}
- 当前：{self.dayun_gz}大运 × {self.year_gz}流年{month_gz_block}

## 今日信息（{target_date}）
- 农历：{day_data.get('lunar_date','')}
- 今日干支：{day_gz}  建除：{huangli.get('zhi_xing','')}日  纳音：{huangli.get('nayin','')}
- 冲：{huangli.get('chong','')}  煞：{huangli.get('sha','')}方
- 黄历宜：{yi_str}
- 黄历忌：{ji_str}
- 喜神方位：{pos.get('xi','')}  财神方位：{pos.get('cai','')}  福神方位：{pos.get('fu','')}

## 今日干支十神分析（命盘层面）
- 今日天干 {day_gz[0]}：{day_gan_shishen}（对日主的关系）
- 今日地支 {day_gz[1]} 主藏干：{day_zhi_shishen}
{lucky_note_block}

## 命盘与今日干支的关系
今日综合评级：【{rating}】
{notes_block}

## 写作要求
请写一份300-500字的日运分析，包含：

1. **今日整体运势**：结合命盘和今日干支，说明今天的整体气场（2句话）

2. **重点提示**：今日最值得关注的一个命盘互动，用通俗语言解释对今天的影响

3. **黄历建议**：结合宜忌，给出1-2条今天适合/不适合做的事

4. **幸运提示**（基于今日干支与命局的互动综合给出，不是固定值）：
   - 幸运色：{lucky_colors_str}
   - 幸运方位：{lucky_dir}
   - 今日食物建议：{lucky_foods or ''}

语气轻松亲切，像朋友发早安消息，结尾加一句鼓励的话。
"""''