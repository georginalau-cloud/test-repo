#!/usr/bin/env python3
"""基金穿透精确计算 - 含港股/美股持仓"""
import json
import akshare as ak
import urllib.request
import re

# ===== 今日A股实时数据 =====
all_stocks = ak.stock_zh_a_spot()
stocks_dict = {row['名称']: {'price': float(row['最新价']), 'chg': float(row['涨跌幅'])} for _, row in all_stocks.iterrows()}
print(f"A股数据: {len(stocks_dict)} 只")

# ===== 获取港股/美股今日涨跌 - 从天天基金持仓页面抓取 =====
def get_hk_us_chg(code, fund_code):
    """从持仓页面抓取港股/美股今日涨跌幅"""
    url = f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={fund_code}&topline=10&year=2026&month=3"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode('utf-8')
    
    idx1 = raw.find("content:\"")
    if idx1 < 0:
        return {}
    start = idx1 + len("content:\"")
    end = raw.find('";', start)
    if end < 0:
        end = raw.find('"', start)
    content = raw[start:end]
    content = content.replace('\\"', '"').replace('\\n', '').replace('\\t', '')
    
    # Extract today's change from the page
    # For each stock, find the change % in the row
    chg_dict = {}
    
    # Pattern: 涨跌幅 column has the change %
    # The format is like: <td>8.22%</td> for 占净值, and the NEXT td after has the 涨跌幅
    # But looking at the raw HTML, the 涨跌幅 is in a <td> with a span that has data-id
    # Let's find all stock name + change pairs
    
    # Find all rows with stock data
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 4:
            continue
        
        def get_text(c):
            return re.sub(r'<[^>]+>', '', c).strip()
        
        texts = [get_text(c) for c in cells]
        
        # Find stock name (cell containing Chinese or known name)
        stock_name = ''
        for t in texts:
            if re.search(r'[\u4e00-\u9fff]', t) and len(t) >= 2 and t not in ['变动详情', '股吧', '行情', '合计']:
                stock_name = t
                break
        
        # Find change % - look for a cell with pattern like "+x.xx%" or "-x.xx%"
        chg = None
        for t in texts:
            # Match percentage like +1.23% or -0.45% (not 占净值 ratio)
            m = re.match(r'^([+-]?\d+\.?\d*)%$', t.strip())
            if m:
                val = float(m.group(1))
                if abs(val) < 30:  # reasonable range for daily change
                    chg = val
                    break
        
        if stock_name and chg is not None:
            chg_dict[stock_name] = chg
    
    return chg_dict

print("\n获取港股/美股持仓页面实时涨跌...")
hk_us_chg = {}
for code, name, market in [('001371', '富国沪港深价值', 'hk'), ('001668', '汇添富全球移动互联', 'us'), ('118001', '易方达亚洲', 'us')]:
    chg = get_hk_us_chg(code, code)
    hk_us_chg[code] = chg
    print(f"  {name}: {list(chg.items())[:3]}...")

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

# 资产配置比例
asset_data = {
    '006751': {'stock_ratio': 0.853, 'report': 'Q1(用户提供)'},
    '166002': {'stock_ratio': 0.7103, 'report': '2026-03-31'},
    '163402': {'stock_ratio': 0.8921, 'report': '2026-03-31'},
    '004477': {'stock_ratio': 0.8652, 'report': '2026-03-31'},
    '001371': {'stock_ratio': 0.7844, 'report': '2023-12-31(旧)'},
    '166005': {'stock_ratio': 0.8259, 'report': '2026-03-31'},
    '001668': {'stock_ratio': 0.6684, 'report': '2019-12-31(旧)'},
    '000979': {'stock_ratio': 0.8190, 'report': '2025-12-31'},
    '118001': {'stock_ratio': 0.8320, 'report': '2012-06-30(旧)'},
    '004965': {'stock_ratio': 0.4719, 'report': '2026-03-31'},
    '450009': {'stock_ratio': 0.8763, 'report': '2026-03-31'},
    '519069': {'stock_ratio': 0.8539, 'report': '2026-03-31'},
    '006113': {'stock_ratio': 0.8974, 'report': '2026-03-31'},
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

grand_mkt = grand_cost = grand_nav_pnl = grand_pnl = grand_fpl = 0

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
    stock_ratio = asset.get('stock_ratio', 1.0)
    holdings = holdings_data.get(code, {}).get('holdings', [])
    
    # Get today's changes for this fund's holdings
    fund_chg = 0.0
    user_pnl_from_holdings = 0.0
    
    if holdings and nav > 0:
        for h in holdings:
            sname = h['name']
            pct_fund = h['percent'] / 100
            
            # Get today's change
            if sname in stocks_dict:
                chg = stocks_dict[sname]['chg']
            elif code in hk_us_chg and sname in hk_us_chg[code]:
                chg = hk_us_chg[code][sname]
            else:
                chg = 0  # No data (e.g., US stocks after hours)
            
            contribution = (chg / 100) * pct_fund * stock_ratio
            fund_chg += contribution
            money_in_stock = mkt * pct_fund * stock_ratio
            pnl = money_in_stock * (chg / 100)
            user_pnl_from_holdings += pnl

    grand_mkt += mkt
    grand_cost += cost_total
    grand_fpl += fpl
    grand_nav_pnl += nav_pnl
    
    print(f"\n【{name}({code})】")
    print(f"  份额={shares:,.2f} 净值={nav:.4f} 股票配置={stock_ratio*100:.1f}%")
    print(f"  市值={mkt:,.0f} 成本={cost_total:,.0f} 浮盈亏={fpl:+,.0f}")
    
    if holdings and nav > 0:
        nav_today_est = nav * (1 + fund_chg)
        user_pnl = (nav_today_est - nav) * shares
        grand_pnl += user_pnl
        print(f"  穿透法估算: 净值{nav:.4f}→{nav_today_est:.4f} ({fund_chg*100:+.4f}%) 用户盈亏={user_pnl:+,.0f}元")
    else:
        user_pnl = nav_pnl
        grand_pnl += nav_pnl
        print(f"  (无持仓明细) 净值法: {nav_pnl:+,.0f}元")

# ETF
print(f"\n{'='*75}")
print("ETF:")
for ename, code, qty, cost, price, chg in etfs:
    mkt_e = qty * price
    cost_e = qty * cost
    pnl_e = mkt_e * (chg / 100)
    print(f"  {ename}: 市值={mkt_e:,.0f} 浮={mkt_e-cost_e:+,.0f} 预估={pnl_e:+,.0f}")
    grand_mkt += mkt_e
    grand_cost += cost_e
    grand_fpl += (mkt_e - cost_e)
    grand_pnl += pnl_e

print(f"\n{'='*75}")
print("汇总")
print(f"  总市值: {grand_mkt:,.0f}元")
print(f"  总成本: {grand_cost:,.0f}元")
print(f"  总浮盈亏: {grand_fpl:+,.0f}元 ({(grand_fpl/grand_cost)*100:+.2f}%)")
print(f"  净值法总预估: {grand_nav_pnl:+,.0f}元")
print(f"  穿透法(精确A)总预估: {grand_pnl:+,.0f}元")
