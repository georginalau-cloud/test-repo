#!/usr/bin/env python3
"""
close_analysis.py
收盘分析：持仓个股 + 基金穿透，两部分合一
每天14:50自动运行，推送飞书
"""
import requests, re, time, json

# ── 用户持仓 ──────────────────────────────────────────────
MY_STOCKS = {
    "300896": {"name": "爱美客",   "shares": 420,  "cost": 478.847},
    "600309": {"name": "万华化学", "shares": 300,  "cost": 88.690},
    "600352": {"name": "浙江龙盛", "shares": 1000, "cost": 12.924},
    "688363": {"name": "华熙生物", "shares": 300,  "cost": 238.043},
    "002176": {"name": "江特电机", "shares": 1000, "cost": 25.506},
    "002172": {"name": "澳洋健康", "shares": 2000, "cost": 6.530},
    "000652": {"name": "泰达股份", "shares": 1000, "cost": 10.105},
    "002551": {"name": "尚荣医疗", "shares": 1000, "cost": 4.600},
    "600221": {"name": "海航控股", "shares": 1000, "cost": 6.236},
}

MY_FUNDS = {
    "163402": {"name": "兴全趋势投资",       "shares": 134513.34},
    "006113": {"name": "汇添富创新医药A",     "shares": 1508.31},
    "519069": {"name": "汇添富价值精选A",    "shares": 1127.23},
    "166002": {"name": "中欧新蓝筹A",         "shares": 37630.83},
    "000979": {"name": "景顺长城沪港深精选A", "shares": 4638.32},
    "006751": {"name": "富国互联科技A",       "shares": 23739.17},
    "004477": {"name": "嘉实沪港深回报",      "shares": 35096.95},
    "001371": {"name": "富国沪港深价值精选A", "shares": 33887.86},
    "166005": {"name": "中欧价值发现A",       "shares": 11491.47},
    "160706": {"name": "沪深300LOF",         "shares": 18541.19},
    "001668": {"name": "汇添富全球移动互联A", "shares": 4206.06},
    "118001": {"name": "易方达亚洲精选",      "shares": 5978.46},
    "004965": {"name": "泓德致远混合A",        "shares": 2415.48},
    "450009": {"name": "国富中小盘A",         "shares": 1706.26},
}

FUND_HOLDINGS_PATH = __import__('pathlib').Path(__file__).parent.parent.parent / "market-alert" / "references" / "fund_holdings.json"

# ── 价格获取 ──────────────────────────────────────────────
def get_sina_prices(codes):
    batch = ",".join([f"sh{c}" if c.startswith(("6","688")) else f"sz{c}" for c in codes])
    headers = {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(f"https://hq.sinajs.cn/list={batch}", headers=headers, timeout=10)
        r.encoding = "gbk"
    except: return {}
    result = {}
    for line in r.text.strip().split('\n'):
        if '=' not in line: continue
        k = line.split('=')[0].split('_')[-1].strip().lstrip('sh').lstrip('sz')
        v = line.split('"')[1].split(',')
        if len(v) < 6: continue
        try:
            cur = float(v[1]); prev = float(v[2])
            result[k] = (cur, prev, (cur-prev)/prev*100)
        except: pass
    return result

def get_fund_nav(fund_code):
    try:
        url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js?rt={int(time.time())}"
        r = requests.get(url, headers={"Referer": "https://fund.eastmoney.com/","User-Agent":"Mozilla/5.0"}, timeout=8)
        m = re.search(r'jsonpgz\((.+)\)', r.text)
        if m:
            d = json.loads(m.group(1))
            return float(d['dwjz']), float(d['gszzl'])
    except: pass
    return None, None

# ── 主逻辑 ──────────────────────────────────────────────
def run():
    today = time.strftime("%Y-%m-%d")

    # ── Part 1: 持仓个股 ──
    codes = list(MY_STOCKS.keys())
    prices = get_sina_prices(codes)

    print(f"\n{'='*60}")
    print(f"📊 持仓个股当日情况 | {today}")
    print(f"{'='*60}")
    print(f"{'代码':<8}{'名称':<8}{'持仓':>5}{'成本':>8}{'当前价':>8}{'涨跌':>7}{'持仓市值':>10}{'今日盈亏':>10}{'总盈亏':>12}")
    print(f"{'-'*75}")

    total_pnl_today = 0
    total_mv = 0
    total_cost = 0
    lines_out = []

    for code, info in MY_STOCKS.items():
        p = prices.get(code)
        if not p:
            lines_out.append(f"{code:<8}{info['name']:<8}{info['shares']:>5} — 暂无数据 —")
            continue
        cur, prev, chg = p
        mv = cur * info['shares']
        cost_total = info['cost'] * info['shares']
        pnl_today = (cur - prev) * info['shares']
        pnl_total = mv - cost_total
        total_pnl_today += pnl_today
        total_mv += mv
        total_cost += cost_total
        flag = "🔴" if chg < -2 else ("🟢" if chg > 2 else "  ")
        print(f"{flag}{code:<7}{info['name']:<8}{info['shares']:>5}{info['cost']:>8.3f}{cur:>8.3f}{chg:>+6.2f}%{mv:>10,.0f}{pnl_today:>+10,.0f}{pnl_total:>+12,.0f}")
        lines_out.append((code, info['name'], info['shares'], info['cost'], cur, chg, mv, pnl_today, pnl_total))

    print(f"{'-'*75}")
    print(f"{'持仓总市值':>45}  {total_mv:>10,.0f}元")
    print(f"{'今日个股合计':>45}  {total_pnl_today:>+10,.0f}元")
    print(f"{'持仓总盈亏':>45}  {total_mv-total_cost:>+12,.0f}元")

    # ── Part 2: 基金穿透 ──
    print(f"\n{'='*60}")
    print(f"📊 基金穿透重仓股 | {today}")
    print(f"{'='*60}")

    fund_holdings = {}
    if FUND_HOLDINGS_PATH.exists():
        with open(FUND_HOLDINGS_PATH) as f:
            raw = json.load(f)
        for fid, finfo in raw.get('fund_holdings', {}).items():
            holdings = [{'code': h['code'], 'name': h['name'],
                         'mv': h['market_value'], 'pct': h['percent']}
                        for h in finfo.get('holdings', [])]
            fund_holdings[fid] = {'name': finfo.get('name',''), 'holdings': holdings}

    # Collect all fund stock codes
    all_codes = set()
    for fid, finfo in fund_holdings.items():
        for h in finfo['holdings']:
            all_codes.add(h['code'])
    fund_prices = get_sina_prices(list(all_codes))

    grand_total = 0
    for fid, info in MY_FUNDS.items():
        nav, nav_chg = get_fund_nav(fid)
        if nav is None: continue
        my_value = info['shares'] * nav
        holdings = fund_holdings.get(fid, {}).get('holdings', [])
        fund_pnl = 0
        rows = []
        for h in holdings:
            chg = fund_prices.get(h['code'], (0,0,0))[2]
            my_mv = my_value * (h['pct'] / 100)
            pnl = my_mv * chg / 100
            fund_pnl += pnl
            rows.append((h['code'], h['name'], h['pct'], my_mv, chg, pnl))
        grand_total += fund_pnl
        top3 = sorted(rows, key=lambda x: -x[5])[:3]
        print(f"\n【{info['name']}】市值 {my_value:,.0f}元  NAV={nav} ({nav_chg:+.2f}%)")
        for code, name, pct, my_mv, chg, pnl in top3:
            print(f"  {code} {name} {chg:>+5.2f}% 占用{my_mv:,.0f}元  {pnl:>+7,.0f}元")
        print(f"  基金穿透合计: {fund_pnl:>+8,.0f}元")

    print(f"\n{'='*60}")
    print(f"📈 基金穿透总计: {grand_total:>+,.0f}元")
    print(f"📈 今日全量（个股+穿透）: {total_pnl_today + grand_total:>+,.0f}元")
    print(f"{'='*60}")

if __name__ == "__main__":
    run()
