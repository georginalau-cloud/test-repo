#!/usr/bin/env python3
"""基金持仓完整穿透计算 - 使用真实季报数据"""
import json
import akshare as ak

# ===== 1. 获取今日实时股价 =====
print("获取今日A股实时数据...")
all_stocks = ak.stock_zh_a_spot()
stocks = {row['名称']: {'price': float(row['最新价']), 'chg': float(row['涨跌幅'])} for _, row in all_stocks.iterrows()}
print(f"获取到 {len(stocks)} 只股票")

# ===== 2. 用户持仓数据 =====
user_funds = {
    '006751': {'name': '富国互联科技A', 'shares': 23739.17, 'cost': 2.9683},
    '166002': {'name': '中欧新蓝筹A', 'shares': 37630.83, 'cost': 2.3199},
    '163402': {'name': '兴全趋势投资', 'shares': 134513.34, 'cost': 0.7324},
    '004477': {'name': '嘉实沪港深回报', 'shares': 35096.95, 'cost': 1.7096},
    '001371': {'name': '富国沪港深价值精选A', 'shares': 33887.86, 'cost': 1.5485},
    '166005': {'name': '中欧价值发现A', 'shares': 11491.47, 'cost': 2.5236},
    '001668': {'name': '汇添富全球移动互联A', 'shares': 4206.06, 'cost': 3.4530},
    '000979': {'name': '景顺长城沪港深精选A', 'shares': 4638.32, 'cost': 2.6598},
    '118001': {'name': '易方达亚洲精选', 'shares': 5978.46, 'cost': 1.3381},
    '004965': {'name': '泓德致远混合A', 'shares': 2415.48, 'cost': 2.0700},
    '450009': {'name': '国富中小盘A', 'shares': 1706.26, 'cost': 2.9304},
    '519069': {'name': '汇添富价值精选A', 'shares': 1127.23, 'cost': 4.4357},
    '006113': {'name': '汇添富创新医药A', 'shares': 1508.31, 'cost': 3.3150},
}

nav_data = {
    '006751': {'nav': 5.9686, 'growth': -0.13},
    '166002': {'nav': 3.4048, 'growth': -0.20},
    '163402': {'nav': 0.9101, 'growth': 0.23},
    '004477': {'nav': 1.9312, 'growth': -0.87},
    '166005': {'nav': 3.4073, 'growth': -0.33},
    '000979': {'nav': 4.9630, 'growth': -0.04},
    '519069': {'nav': 3.4360, 'growth': -0.58},
    '006113': {'nav': 1.6907, 'growth': -1.93},
    '001371': {'nav': 1.5281, 'growth': -0.52},
    '001668': {'nav': 3.4690, 'growth': 0.23},
    '118001': {'nav': 1.2450, 'growth': 0.48},
    '004965': {'nav': 2.0650, 'growth': -0.18},
    '450009': {'nav': 2.7497, 'growth': -0.07},
}

etfs = [
    ('有色金属ETF', '516650', 8000, 2.449, 2.161, 0.09),
    ('储能电池ETF', '159566', 3000, 2.085, 2.424, 1.72),
    ('招商中证白酒A', '161725', 5000, 1.355, 0.6159, -0.48),
]

with open('/Users/georginalau/.openclaw/workspace-zhaocai/skills/market-alert/references/fund_holdings_realtime.json') as f:
    holdings_data = json.load(f)['funds']

grand_mkt = grand_cost = grand_nav_pnl = grand_pnl = 0

for code, info in user_funds.items():
    name = info['name']
    shares = info['shares']
    cost = info['cost']
    nav_info = nav_data.get(code, {'nav': 0, 'growth': 0})
    nav = nav_info['nav']
    growth = nav_info['growth']
    mkt = shares * nav if nav > 0 else 0
    cost_total = shares * cost
    fpl = mkt - cost_total
    nav_pnl = mkt * (growth / 100) if nav > 0 else 0
    holdings = holdings_data.get(code, {}).get('holdings', [])

    print(f"\n{'='*70}")
    print(f"【{name}({code})】 份额={shares:,.2f} 净值={nav:.4f}(05-08) 昨日涨跌={growth:+.2f}%")
    print(f"  市值={mkt:,.0f}元 成本={cost_total:,.0f}元 浮盈亏={fpl:+,.0f}元")
    print(f"  净值法: {nav_pnl:+,.0f}元")

    penetrate_pnl = 0
    if holdings and nav > 0:
        print(f"  {'股票':<12} {'占比':>6} {'今日涨跌':>8} {'占用资金':>10} {'预估盈亏':>8}")
        print(f"  {'-'*50}")
        for h in holdings:
            sname = h['name']
            pct = h['percent']
            sdata = stocks.get(sname, {})
            chg = sdata.get('chg', 0)
            user_money = mkt * (pct / 100)
            pnl = user_money * (chg / 100) if chg != 0 else 0
            penetrate_pnl += pnl
            if chg != 0:
                print(f"  {sname:<12} {pct:>5.2f}% {chg:>+7.2f}% {user_money:>10,.0f} {pnl:>+8,.0f}")
        total_money = sum(mkt * (h['percent']/100) for h in holdings)
        print(f"  {'合计':<12} {'':>5} {'':>7} {total_money:>10,.0f} {penetrate_pnl:>+8,.0f}")
        print(f"  ★ 穿透法: {penetrate_pnl:+,.0f}元 | 净值法: {nav_pnl:+,.0f}元")
    else:
        print(f"  (无持仓明细，穿透法=净值法: {nav_pnl:+,.0f}元)")
        penetrate_pnl = nav_pnl

    grand_mkt += mkt
    grand_cost += cost_total
    grand_nav_pnl += nav_pnl
    grand_pnl += penetrate_pnl

print(f"\n{'='*70}")
print("ETF:")
for ename, code, qty, cost, price, chg in etfs:
    mkt_e = qty * price
    cost_e = qty * cost
    pnl_e = mkt_e * (chg / 100)
    print(f"  {ename}: {qty}份 现价={price}({chg:+.2f}%) 市值={mkt_e:,.0f} 成本={cost_e:,.0f} 浮={mkt_e-cost_e:+,.0f} 预估={pnl_e:+,.0f}")
    grand_mkt += mkt_e
    grand_cost += cost_e
    grand_pnl += pnl_e

print(f"\n{'='*70}")
print("汇总")
print(f"  总市值: {grand_mkt:,.0f}元")
print(f"  总成本: {grand_cost:,.0f}元")
print(f"  总浮盈亏: {grand_mkt-grand_cost:+,.0f}元 ({(grand_mkt/grand_cost-1)*100:+.2f}%)")
print(f"  净值法总预估: {grand_nav_pnl:+,.0f}元 (05-08，最准确)")
print(f"  穿透法总预估: {grand_pnl:+,.0f}元 (今日实时)")
