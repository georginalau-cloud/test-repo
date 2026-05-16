#!/usr/bin/env python3
"""基金持仓穿透计算 - 精确算法（方法A）"""
import json
import akshare as ak

# ===== 今日实时股价 =====
all_stocks = ak.stock_zh_a_spot()
stocks_dict = {row['名称']: {'price': float(row['最新价']), 'chg': float(row['涨跌幅'])} for _, row in all_stocks.iterrows()}
print(f"今日股票数据: {len(stocks_dict)} 只")

# ===== 用户持仓 =====
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

# 净值（05-08）
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

# 资产配置比例（来自天天基金网，Q1 2026优先）
asset_data = {
    '006751': {'stock_ratio': 0.853, 'bond_ratio': 0.0, 'cash_ratio': 0.0, 'report': 'Q1 2026(用户提供)'},
    '166002': {'stock_ratio': 0.7103, 'bond_ratio': 0.1161, 'cash_ratio': 0.1694, 'report': '2026-03-31'},
    '163402': {'stock_ratio': 0.8921, 'bond_ratio': 0.0234, 'cash_ratio': 0.0906, 'report': '2026-03-31'},
    '004477': {'stock_ratio': 0.8652, 'bond_ratio': 0.0169, 'cash_ratio': 0.0960, 'report': '2026-03-31'},
    '001371': {'stock_ratio': 0.7844, 'bond_ratio': 0.0005, 'cash_ratio': 0.1559, 'report': '2023-12-31(旧)'},
    '166005': {'stock_ratio': 0.8259, 'bond_ratio': 0.0250, 'cash_ratio': 0.1504, 'report': '2026-03-31'},
    '001668': {'stock_ratio': 0.6684, 'bond_ratio': 0.0003, 'cash_ratio': 0.0945, 'report': '2019-12-31(旧)'},
    '000979': {'stock_ratio': 0.8190, 'bond_ratio': 0.0006, 'cash_ratio': 0.1883, 'report': '2025-12-31'},
    '118001': {'stock_ratio': 0.8320, 'bond_ratio': 0.0000, 'cash_ratio': 0.0744, 'report': '2012-06-30(旧)'},
    '004965': {'stock_ratio': 0.4719, 'bond_ratio': 0.2939, 'cash_ratio': 0.2369, 'report': '2026-03-31'},
    '450009': {'stock_ratio': 0.8763, 'bond_ratio': 0.0544, 'cash_ratio': 0.0725, 'report': '2026-03-31'},
    '519069': {'stock_ratio': 0.8539, 'bond_ratio': 0.0465, 'cash_ratio': 0.0712, 'report': '2026-03-31'},
    '006113': {'stock_ratio': 0.8974, 'bond_ratio': 0.0000, 'cash_ratio': 0.1097, 'report': '2026-03-31'},
}

# 持仓明细
with open('/Users/georginalau/.openclaw/workspace-zhaocai/skills/market-alert/references/fund_holdings_realtime.json') as f:
    holdings_data = json.load(f)['funds']

# ETF
etfs = [
    ('有色金属ETF', '516650', 8000, 2.449, 2.161, 0.09),
    ('储能电池ETF', '159566', 3000, 2.085, 2.424, 1.72),
    ('招商中证白酒A', '161725', 5000, 1.355, 0.6159, -0.48),
]

print("\n" + "="*75)
print("基金穿透精确计算（方法A）| 2026-05-11")
print("="*75)
print("公式: 基金净值变化 = Σ(个股涨跌% × 占净值比例% × 股票配置比例)")
print("     用户盈亏 = (今日净值 - 昨日净值) × 持有份额")
print()

grand_mkt = grand_cost = grand_nav_pnl = grand_pnl = 0
grand_fpl = 0

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
    asset = asset_data.get(code, {})
    stock_ratio = asset.get('stock_ratio', 1.0)  # 默认100%股票
    holdings = holdings_data.get(code, {}).get('holdings', [])

    print(f"\n【{name}({code})】")
    print(f"  份额={shares:,.2f} 净值={nav:.4f}(05-08) 股票配置={stock_ratio*100:.1f}%(报告:{asset.get('report','')})")
    print(f"  市值={mkt:,.0f}元 成本={cost_total:,.0f}元 浮盈亏={fpl:+,.0f}元")
    
    fund_chg = 0.0
    if holdings and nav > 0:
        print(f"  {'股票':<12} {'占净值%':>8} {'今日涨跌%':>10} {'贡献净值%':>12} {'占用资金':>10} {'个人盈亏':>8}")
        print(f"  {'-'*60}")
        for h in holdings:
            sname = h['name']
            pct_fund = h['percent'] / 100
            chg = stocks_dict.get(sname, {}).get('chg', 0)
            contribution = (chg / 100) * pct_fund * stock_ratio
            fund_chg += contribution
            money_in_stock = mkt * pct_fund * stock_ratio
            pnl = money_in_stock * (chg / 100)
            if chg != 0:
                print(f"  {sname:<12} {pct_fund*100:>7.2f}% {chg:>+9.2f}% {contribution*100:>+11.4f}% {money_in_stock:>10,.0f} {pnl:>+8,.0f}")
        
        nav_today_est = nav * (1 + fund_chg)
        user_pnl = (nav_today_est - nav) * shares
        print(f"  {'合计':<12} {'':>7} {'':>9} {fund_chg*100:>+11.4f}%")
        print(f"  ★ 穿透法估算今日净值: {nav:.4f} → {nav_today_est:.4f}  ({fund_chg*100:+.4f}%)")
        print(f"  ★ 用户今日盈亏: {user_pnl:>+,.0f}元")
    else:
        user_pnl = nav_pnl
        print(f"  (无持仓明细，穿透法=净值法: {nav_pnl:+,.0f}元)")

    grand_mkt += mkt
    grand_cost += cost_total
    grand_fpl += fpl
    grand_nav_pnl += nav_pnl
    grand_pnl += user_pnl

# ETF
print(f"\n{'='*75}")
print("ETF（场内实时）:")
for ename, code, qty, cost, price, chg in etfs:
    mkt_e = qty * price
    cost_e = qty * cost
    pnl_e = mkt_e * (chg / 100)
    print(f"  {ename}: {qty}份 现价={price}({chg:+.2f}%) 市值={mkt_e:,.0f} 成本={cost_e:,.0f} 浮={mkt_e-cost_e:+,.0f} 预估={pnl_e:+,.0f}")
    grand_mkt += mkt_e
    grand_cost += cost_e
    grand_fpl += (mkt_e - cost_e)
    grand_pnl += pnl_e

print(f"\n{'='*75}")
print("汇总")
print(f"  总市值: {grand_mkt:,.0f}元")
print(f"  总成本: {grand_cost:,.0f}元")
print(f"  总浮盈亏: {grand_fpl:+,.0f}元 ({(grand_fpl/grand_cost)*100:+.2f}%)")
print(f"  净值法总预估: {grand_nav_pnl:+,.0f}元 (05-08，最准确)")
print(f"  穿透法(精确A)总预估: {grand_pnl:+,.0f}元 (今日盘中)")
