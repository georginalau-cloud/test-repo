#!/usr/bin/env python3
"""
沛柔基金组合深度分析
- 持仓穿透（十大重仓股重叠度）
- 业绩诊断（多时段收益+同类排名百分位）
- 组合优化建议
"""

import akshare as ak
import pandas as pd
import numpy as np
import warnings, time, re
from collections import Counter
warnings.filterwarnings('ignore')

FUNDS = [
    ("166002", "中欧新蓝筹A",        37630.83, 2.3199),
    ("006751", "富国互联科技A",      23739.17, 2.9683),
    ("163402", "兴全趋势投资",       134513.34, 0.7324),
    ("004477", "嘉实沪港深回报",     35096.95, 1.7096),
    ("001371", "富国沪港深价值精选A", 33887.86, 1.5485),
    ("166005", "中欧价值发现A",      11491.47, 2.5236),
    ("160706", "沪深300LOF",         18541.19, 1.0631),
    ("001668", "汇添富全球移动互联A", 4206.06, 3.4530),
    ("000979", "景顺长城沪港深精选A", 4638.32, 2.6598),
    ("118001", "易方达亚洲精选",      5978.46, 1.3381),
    ("004965", "泓德致远混合A",       2415.48, 2.0700),
    ("450009", "国富中小盘A",         1706.26, 2.9304),
    ("519069", "汇添富价值精选A",     1127.23, 4.4357),
    ("006113", "汇添富创新医药A",      1508.31, 3.3150),
]
FUNDS_DICT = {code: name for code, name, _, _ in FUNDS}

# ═══════════════════════════════════════════════════════════════════════════
# Section A: 最新净值 & 成本盈亏
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 80)
print("沛柔基金组合深度分析报告  |  生成时间: 2026-04-29")
print("=" * 80)

print("\n\n【A】基金净值与成本盈亏分析")
print("-" * 80)

def get_nav(code):
    """获取最新单位净值和日期"""
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator='单位净值走势', period='近1月')
        time.sleep(0.3)
        row = df.iloc[-1]
        return float(row['单位净值']), str(row['净值日期'])
    except:
        return None, None

nav_rows = []
for code, name, shares, cost in FUNDS:
    nav, date = get_nav(code)
    if nav:
        mv   = shares * nav
        cv   = shares * cost
        pnl  = mv - cv
        ret  = (nav - cost) / cost * 100
        nav_rows.append({
            '基金代码': code, '基金名称': name,
            '持有份额': shares, '单位成本': cost,
            '最新净值': nav, '净值日期': date,
            '最新市值': mv, '成本总额': cv,
            '累计盈亏额': pnl, '累计盈亏率': ret,
        })
    else:
        cv = shares * cost
        nav_rows.append({
            '基金代码': code, '基金名称': name,
            '持有份额': shares, '单位成本': cost,
            '最新净值': None, '净值日期': None,
            '最新市值': None, '成本总额': cv,
            '累计盈亏额': None, '累计盈亏率': None,
        })

nav_df = pd.DataFrame(nav_rows)
for _, r in nav_df.iterrows():
    status = "✅" if r['累计盈亏率'] and r['累计盈亏率'] > 0 else "🔴"
    print(f"  {status} {r['基金名称']}({r['基金代码']})  "
          f"成本={r['单位成本']:.4f}  最新净值={r['最新净值']}  "
          f"盈亏={r['累计盈亏率']:.2f}%" if r['累计盈亏率'] is not None
          else f"  {r['基金名称']}({r['基金代码']})  净值获取失败")

# ═══════════════════════════════════════════════════════════════════════════
# Section B: 持仓穿透 — 十大重仓股 & 重叠度
# ═══════════════════════════════════════════════════════════════════════════
print("\n\n【B】基金持仓穿透分析")
print("-" * 80)

def get_top10(code, name):
    """获取最新一期十大重仓股"""
    try:
        df = ak.fund_portfolio_hold_em(symbol=code)
        time.sleep(0.4)
        # 取最新季度
        quarters = df['季度'].unique()
        latest_q = sorted(quarters, reverse=True)[0]
        qdf = df[df['季度'] == latest_q].head(10)
        return latest_q, qdf[['股票代码','股票名称','占净值比例']].values.tolist()
    except Exception as e:
        print(f"  ⚠️ {name}({code}) 持仓获取失败: {e}")
        return None, []

all_holdings = {}      # code -> {stock_code: (name, pct)}
fund_quarter = {}      # code -> latest quarter str
for code, name, _, _ in FUNDS:
    q, stocks = get_top10(code, name)
    fund_quarter[code] = q
    all_holdings[code] = {s[0]: (s[1], s[2]) for s in stocks}  # code -> (name, pct)
    if stocks:
        top3 = ", ".join([f"{s[1]}({s[2]}%)" for s in stocks[:3]])
        print(f"  ✅ {name}({code}) [{q}]  Top3: {top3}")

# ── 持仓重叠度矩阵 ────────────────────────────────────────────────────────────
print("\n  【持仓重叠度】同一只股票被多只基金持有:")
# 收集所有股票
stock_funds = Counter()
for code, holdings in all_holdings.items():
    for scode in holdings:
        stock_funds[scode] += 1

overlap_stocks = {k: v for k, v in stock_funds.items() if v >= 2}
# 找股票名称
stock_names = {}
for holdings in all_holdings.values():
    for scode, (sname, _) in holdings.items():
        stock_names[scode] = sname

overlap_list = []
for scode, count in sorted(overlap_stocks.items(), key=lambda x: -x[1]):
    funds_holding = [code for code, h in all_holdings.items() if scode in h]
    pcts = [all_holdings[code][scode][1] for code in funds_holding]
    overlap_list.append({
        '股票代码': scode, '股票名称': stock_names.get(scode,'?'),
        '持有基金数': count,
        '涉及基金': ", ".join([f"{FUNDS_DICT.get(c,c)}" for c in funds_holding]),
        '占净值比范围': f"{min(pcts):.2f}% ~ {max(pcts):.2f}%",
    })


if overlap_list:
    ov_df = pd.DataFrame(overlap_list)
    print(ov_df.to_string(index=False))
else:
    print("  未发现明显重叠（标准：≥2只基金共同持有）")

# ── 集中风险识别 ─────────────────────────────────────────────────────────────
print("\n  【集中风险提示】")
risk_stocks = {k: v for k, v in overlap_stocks.items() if v >= 4}
for scode, count in risk_stocks.items():
    funds_holding = [code for code, h in all_holdings.items() if scode in h]
    print(f"  🔴 {stock_names.get(scode,'?')}({scode}) 被{count}只基金共同重仓: {[FUNDS_DICT.get(c,c) for c in funds_holding]}")

# ═══════════════════════════════════════════════════════════════════════════
# Section C: 业绩筛选诊断
# ═══════════════════════════════════════════════════════════════════════════
print("\n\n【C】基金业绩筛选诊断")
print("-" * 80)

# 获取全部基金排名数据（按类型）
def get_fund_category(code):
    """通过天天基金网获取基金类型"""
    try:
        df = ak.fund_individual_detail_xq(symbol=code)
        time.sleep(0.3)
        # 返回基金类型字段
        cols = list(df.columns)
        print(f"    [{code}] 详细列: {cols}")
        return df
    except Exception as e:
        return None

# 获取基金排名数据（一次性拉全量，再过滤目标基金）
rank_cache = {}
for cat in ['股票型', '混合型', '指数型', '债券型', 'QDII']:
    try:
        df = ak.fund_open_fund_rank_em(symbol=cat)
        time.sleep(0.5)
        rank_cache[cat] = df
        print(f"  [{cat}] 获取到 {len(df)} 只基金")
    except Exception as e:
        print(f"  [{cat}] 获取失败: {e}")

# 为每只持仓基金找排名
fund_rank_data = []
for code, name, _, _ in FUNDS:
    found = False
    for cat, df in rank_cache.items():
        match = df[df['基金代码'] == code]
        if not match.empty:
            row = match.iloc[0]
            # 计算排名百分位
            def pctile(col):
                vals = pd.to_numeric(df[col], errors='coerce')
                val  = pd.to_numeric(row[col], errors='coerce')
                if pd.isna(val):
                    return None
                valid = vals.dropna()
                if len(valid) == 0:
                    return None
                return (valid < val).sum() / len(valid) * 100

            r1y  = pctile('近1年');  r6m  = pctile('近6月');  r3m = pctile('近3月')
            fund_rank_data.append({
                '基金代码': code, '基金名称': name, '类型': cat,
                '近1年收益': row['近1年'], '近1年百分位': r1y,
                '近6月收益': row['近6月'], '近6月百分位': r6m,
                '近3月收益': row['近3月'], '近3月百分位': r3m,
                '今年来': row['今年来'],
            })
            found = True
            break
    if not found:
        fund_rank_data.append({
            '基金代码': code, '基金名称': name, '类型': '待确认',
            '近1年收益': None, '近1年百分位': None,
            '近6月收益': None, '近6月百分位': None,
            '近3月收益': None, '近3月百分位': None,
            '今年来': None,
        })

rank_df = pd.DataFrame(fund_rank_data)
print("\n  基金业绩一览:")
print(f"  {'基金名称':<20} {'类型':<6} {'近1年':>8} {'排名%':>6} {'近6月':>8} {'排名%':>6} {'近3月':>8} {'排名%':>6} {'建议':>6}")
print("  " + "-" * 80)
for _, r in rank_df.iterrows():
    def fmt_pct(v): return f"{v:.1f}%" if v is not None else "N/A"
    def fmt_ret(v): return f"{v:.2f}%" if v is not None else "N/A"

    # 给出操作建议
    scores = []
    for col, name in [('近1年百分位','1年'), ('近6月百分位','6月'), ('近3月百分位','3月')]:
        if r[col] is not None:
            scores.append(r[col])
    if scores:
        avg_pct = np.mean(scores)
        best_pct = min(scores)
        if avg_pct >= 80:
            signal = "🟢加仓"
        elif avg_pct >= 50:
            signal = "🟡持有"
        elif avg_pct >= 30:
            signal = "🟠减仓"
        else:
            signal = "🔴清仓"
    else:
        signal = "⚪待确认"

    print(f"  {r['基金名称']:<16} {r['类型']:<6} {fmt_ret(r['近1年收益']):>8} {fmt_pct(r['近1年百分位']):>6} "
          f"{fmt_ret(r['近6月收益']):>8} {fmt_pct(r['近6月百分位']):>6} "
          f"{fmt_ret(r['近3月收益']):>8} {fmt_pct(r['近3月百分位']):>6} {signal:>6}")

# ═══════════════════════════════════════════════════════════════════════════
# Section D: 组合配置优化
# ═══════════════════════════════════════════════════════════════════════════
print("\n\n【D】组合配置优化建议")
print("-" * 80)

# 分析重叠情况
print("\n  1️⃣ 持仓重叠问题:")
for scode, count in sorted(overlap_stocks.items(), key=lambda x: -x[1]):
    funds_list = [code for code, h in all_holdings.items() if scode in h]
    if count >= 3:
        pcts = [all_holdings[code][scode][1] for code in funds_list]
        print(f"     🔴 {stock_names.get(scode,'?')} 被{count}只基金重仓，"
              f"合计占净值比约 {sum(pcts):.1f}%+，建议减至1只")

# 相似策略基金识别（基于重仓股重叠度）
from itertools import combinations
print("\n  2️⃣ 策略相似基金（重仓股高度重叠）:")
fund_codes = [code for code, _, _, _ in FUNDS]
sim_pairs = []
for c1, c2 in combinations(fund_codes, 2):
    if c1 not in all_holdings or c2 not in all_holdings:
        continue
    h1 = set(all_holdings[c1].keys())
    h2 = set(all_holdings[c2].keys())
    if not h1 or not h2:
        continue
    overlap_count = len(h1 & h2)
    union_count   = len(h1 | h2)
    jaccard = overlap_count / union_count if union_count > 0 else 0
    if jaccard >= 0.3 and overlap_count >= 3:
        n1 = dict(FUNDS).get(c1, c1)
        n2 = dict(FUNDS).get(c2, c2)
        sim_pairs.append((c1, n1, c2, n2, jaccard, overlap_count, list(h1 & h2)))

for c1, n1, c2, n2, jc, oc, common in sorted(sim_pairs, key=lambda x: -x[4]):
    cs = [stock_names.get(s, s) for s in common]
    print(f"     🟠 {n1} ↔ {n2}")
    print(f"        Jaccard重叠度={jc:.1%}，共同重仓股{oc}只: {', '.join(cs[:5])}")

# 精简建议
print("\n  3️⃣ 精简建议:")
print("""
  • 166002 中欧新蓝筹A & 166005 中欧价值发现A：
    两只均为中欧基金旗下价值/蓝筹策略，持仓重叠度预计较高，保留其一即可（建议保留规模更大、跟踪更久的166002）

  • 004477 嘉实沪港深回报 & 001371 富国沪港深价值精选A & 000979 景顺长城沪港深精选A：
    三只均为沪港深主题，高度重叠，建议保留001371（富国，规模/业绩更优）

  • 001668 汇添富全球移动互联A & 006751 富国互联科技A：
    两只均为科技/互联网主题，重叠度高，建议保留006751（业绩排名更靠前）

  • 519069 汇添富价值精选A 份额极小（1127份），贡献有限，可考虑清仓

  • 118001 易方达亚洲精选（QDII）作为亚洲市场分散配置，保留

  • 160706 沪深300LOF 作为A股大盘基准，保留

  精简后可从14只→9只，有效降低重叠风险
""")

# ═══════════════════════════════════════════════════════════════════════════
# Section E: 汇总评分
# ═══════════════════════════════════════════════════════════════════════════
print("\n\n【E】综合诊断汇总")
print("-" * 80)

# 计算各基金综合评分（百分位越低越好）
summary = []
for _, r in rank_df.iterrows():
    pcts = [v for v in [r['近1年百分位'], r['近6月百分位'], r['近3月百分位']] if v is not None]
    avg_p = np.mean(pcts) if pcts else None
    # 持仓重叠惩罚
    code = r['基金代码']
    overlap_penalty = 0
    if code in fund_codes:
        scode_idx = fund_codes.index(code)
    else:
        overlap_penalty = 0
    # 计算持有该基金重仓股的股票被多少其他基金也持有
    penalty = 0
    if code in all_holdings:
        for sc in all_holdings[code]:
            cnt = overlap_stocks.get(sc, 1)
            if cnt >= 4:
                penalty += 5  # 每只高度重叠股票扣5分

    score = (100 - avg_p - penalty) if (avg_p is not None) else None
    signal = "加仓" if (score and score >= 80) else ("持有" if (score and score >= 60) else ("减仓" if (score and score >= 40) else "待观察"))
    summary.append({
        '基金名称': r['基金名称'],
        '基金代码': code,
        '近1年百分位': f"{r['近1年百分位']:.1f}%" if r['近1年百分位'] else "N/A",
        '近3月百分位': f"{r['近3月百分位']:.1f}%" if r['近3月百分位'] else "N/A",
        '综合评分': f"{score:.0f}" if score is not None else "N/A",
        '操作建议': signal,
    })

sum_df = pd.DataFrame(summary)
sum_df = sum_df.sort_values('综合评分', ascending=False)
print(sum_df.to_string(index=False))

print("\n" + "=" * 80)
print("分析完毕  |  数据来源: 天天基金网(akshare)  |  仅供参考，不构成投资建议")
print("=" * 80)
