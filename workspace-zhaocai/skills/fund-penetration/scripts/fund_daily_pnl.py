#!/usr/bin/env python3
"""
fund_daily_pnl.py - 收盘后持仓盈亏扫描
用法: python3 fund_daily_pnl.py

功能:
  - 场外基金: 穿透Q1重仓股 × 今日个股涨跌 → 估算今日盈亏
  - 场内ETF:  用 fundgz 接口获取实时预估净值 × 今日涨跌
  - 个股持仓: 手动输入（暂无实时行情接口，需自行填写收盘价）
"""

import requests
import json
import re
import sys
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# 用户持仓（调仓后手动同步这里）
# ──────────────────────────────────────────────────────────────
OFF_FUNDS = {
    "166002": {"name": "中欧新蓝筹混合A",           "shares": 37630.83,  "cost": 2.3199},
    "006751": {"name": "富国互联科技股票A",           "shares": 23739.17,  "cost": 2.9683},
    "163402": {"name": "兴全趋势投资混合(LOF)",       "shares": 134513.34, "cost": 0.7324},
    "004477": {"name": "嘉实沪港深回报混合",          "shares": 35096.95,  "cost": 1.7096},
    "001371": {"name": "富国沪港深价值混合A",          "shares": 33887.86,  "cost": 1.5485},
    "166005": {"name": "中欧价值发现混合A",           "shares": 11491.47,  "cost": 2.5236},
    "001668": {"name": "汇添富全球移动互联(QDII)",     "shares": 4206.06,   "cost": 3.4530},
    "000979": {"name": "景顺长城沪港深精选股票A",      "shares": 4638.32,   "cost": 2.6598},
    "118001": {"name": "易方达亚洲精选",               "shares": 5978.46,   "cost": 1.3381},
    "004965": {"name": "泓德致远混合A",               "shares": 2415.48,   "cost": 2.0700},
    "450009": {"name": "国富中小盘股票A",              "shares": 1706.26,   "cost": 2.9304},
    "519069": {"name": "汇添富价值精选混合",           "shares": 1127.23,   "cost": 4.4357},
    "006113": {"name": "汇添富创新医药混合A",          "shares": 1508.31,   "cost": 3.3150},
}

# 场内ETF用fundgz接口
ON_ETFS = {
    "516650": {"name": "有色金属ETF华夏",             "shares": 8000, "cost": 2.449},
    "159566": {"name": "储能电池ETF易方达",            "shares": 3000, "cost": 2.085},
    "161725": {"name": "招商中证白酒指数(LOF)A",       "shares": 5000, "cost": 1.355},
}

# 个股持仓（来自MEMORY.md）
STOCKS = {
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

H_EAST = {"User-Agent": "Mozilla/5.0", "Referer": "https://fund.eastmoney.com/"}
H_SINA = {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}


# ──────────────────────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────────────────────
def parse_fundgz(code: str) -> dict:
    """通过 fundgz.1234567.com.cn 获取基金实时预估净值"""
    url = f"https://fundgz.1234567.com.cn/js/{code}.js?rt={int(datetime.now().timestamp())}"
    try:
        r = requests.get(url, headers=H_EAST, timeout=8)
        text = r.text.strip()
        if "jsonpgz" not in text:
            return {}
        m = re.search(r"jsonpgz\((.+)\)", text)
        if not m:
            return {}
        d = json.loads(m.group(1))
        return {
            "name": d.get("name", ""),
            "nav":  float(d.get("dwjz", 0)),    # 昨日单位净值
            "est":  float(d.get("gsz", 0)),    # 今日预估净值
            "chg":  float(d.get("gszzl", 0)),  # 今日涨跌幅%
            "date": d.get("jzrq", ""),
        }
    except Exception:
        return {}


def get_stock_prices(codes: list) -> dict:
    """新浪实时行情批量接口 → {code: (cur, prev, chg%)}"""
    if not codes:
        return {}
    batch = ",".join(
        f"sh{c}" if c[0] in "56" else f"sz{c}" for c in codes
    )
    try:
        r = requests.get(f"https://hq.sinajs.cn/list={batch}", headers=H_SINA, timeout=10)
        r.encoding = "gbk"
        res = {}
        for line in r.text.strip().split("\n"):
            if "=" not in line:
                continue
            k = line.split("=")[0].split("_")[-1].strip()  # e.g. sz300308
            k_code = k.replace("sh", "").replace("sz", "")
            try:
                p = line.split('"')[1].split(",")
                cur  = float(p[1])
                prev = float(p[2])
                res[k_code] = (cur, prev, round((cur - prev) / prev * 100, 2))
            except Exception:
                pass
        return res
    except Exception:
        return {}


def get_fund_holdings(code: str) -> list:
    """
    解析东方财富 Q1（2026-03-31）前10大重仓股
    返回 [{code, name, pct, mv}]，pct=占净值%，mv=万元
    """
    try:
        url = (
            f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx"
            f"?type=jjcc&code={code}&topline=10&year=2026&month=03"
        )
        r = requests.get(url, headers=H_EAST, timeout=10)
        r.encoding = "utf-8"
        text = r.text

        rows = text.split("</tr>")
        holdings = []
        for row in rows[1:11]:  # 前10条
            code_m = re.search(r"unify/r/\d\.(\d{6})'", row)
            name_m = re.search(r"class='tol'[^>]*><a[^>]*>([^<]+)</a>", row)
            pct_m  = re.search(r'class=.tor.>([\d.]+)%', row)
            mv_m   = re.search(r'class=.tor.>([\d,]+\.\d+)</td>\s*$', row.replace("\n", ""))
            if code_m and name_m and pct_m:
                holdings.append({
                    "code": code_m.group(1),
                    "name": name_m.group(1),
                    "pct":  float(pct_m.group(1)),
                    "mv":   float(mv_m.group(1).replace(",", "")) if mv_m else 0.0,
                })
        return holdings
    except Exception as e:
        print(f"  [WARN] {code} holdings: {e}", file=sys.stderr)
        return []


# ──────────────────────────────────────────────────────────────
# 主逻辑
# ──────────────────────────────────────────────────────────────
def main():
    now = datetime.now()
    print(f"\n{'='*60}")
    print(f"  💰 沛柔持仓日报  {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    # ── 1. 场内ETF ─────────────────────────────────────────────
    print("📊 场内ETF（实时预估）")
    print("-"*50)
    etf_details  = []
    etf_today    = 0.0
    etf_mv       = 0.0
    etf_cost_tot = 0.0
    etf_unreal   = 0.0

    for code, info in ON_ETFS.items():
        d = parse_fundgz(code)
        if not d or d["est"] == 0:
            print(f"  ⚠️  {info['name']} 无法获取净值")
            continue
        price = d["est"]
        chg   = d["chg"]
        mv    = info["shares"] * price
        cost  = info["shares"] * info["cost"]
        today = info["shares"] * price * chg / 100
        unreal = mv - cost
        etf_today    += today
        etf_mv       += mv
        etf_cost_tot += cost
        etf_unreal   += unreal
        etf_details.append({
            "name": info["name"], "code": code,
            "price": price, "chg": chg,
            "mv": mv, "cost": cost,
            "today": today, "unreal": unreal,
        })
        print(f"  {info['name']}（{code}）")
        print(f"    预估净值={price}(今日{chg:+.2f}%) 持有={mv:,.0f}元")
        print(f"    成本={cost:,.0f} 浮盈亏={unreal:+,.0f}({unreal/cost*100:+.2f}%)")
        print(f"    ⚡ 今日盈亏={today:+,.0f}元")

    # ── 2. 场外基金 ───────────────────────────────────────────
    print(f"\n📊 场外基金穿透估算（Q1重仓股）")
    print("-"*50)

    # 批量获取净值
    fund_navs = {code: parse_fundgz(code) for code in OFF_FUNDS}

    # 收集所有重仓股
    all_codes = set()
    holdings_map = {}
    for code in OFF_FUNDS:
        h = get_fund_holdings(code)
        holdings_map[code] = h
        all_codes.update(x["code"] for x in h)

    print(f"  正在抓取 {len(all_codes)} 只重仓股收盘价...")
    prices = get_stock_prices(list(all_codes))

    off_mv_tot    = 0.0
    off_cost_tot  = 0.0
    off_unreal_tot= 0.0
    off_today_tot = 0.0
    fund_details  = []
    all_top_holds = []  # 全局重仓股盈亏排行

    for code, info in OFF_FUNDS.items():
        nav_data = fund_navs.get(code, {})
        if not nav_data or nav_data.get("nav") == 0:
            print(f"\n  ⚠️  {info['name']} 净值获取失败，跳过")
            continue

        nav      = nav_data["nav"]
        holdings = holdings_map.get(code, [])
        mv       = info["shares"] * nav
        cost_mv  = info["shares"] * info["cost"]
        unreal   = mv - cost_mv

        fund_chg  = 0.0
        top_pnl   = []
        for h in holdings:
            pd = prices.get(h["code"])
            if pd:
                cur, prev, chg_s = pd
                user_mv = mv * (h["pct"] / 100)
                pnl     = user_mv * chg_s / 100
                fund_chg  += (h["pct"] / 100) * chg_s
                top_pnl.append({"name": h["name"], "code": h["code"],
                                 "chg": chg_s, "pct": h["pct"],
                                 "user_mv": user_mv, "pnl": pnl})
                all_top_holds.append({"name": h["name"], "code": h["code"],
                                       "chg": chg_s, "pct": h["pct"],
                                       "user_mv": user_mv, "pnl": pnl,
                                       "fund": info["name"]})

        today_pnl = mv * fund_chg / 100
        off_mv_tot     += mv
        off_cost_tot   += cost_mv
        off_unreal_tot += unreal
        off_today_tot  += today_pnl

        top5 = sorted(top_pnl, key=lambda x: abs(x["pnl"]), reverse=True)[:5]
        print(f"\n  【{info['name']}】（净值={nav} 持有={mv:,.0f} 成本={cost_mv:,.0f} 浮盈亏={unreal:+,.0f}）")
        print(f"    ⚡ 穿透估算今日: {fund_chg:+.2f}%  盈亏={today_pnl:+,.0f}元")
        for h in top5:
            print(f"    {h['chg']:+.2f}% {h['name']} 占{h['pct']}% 占用={h['user_mv']:,.0f} 盈亏={h['pnl']:+,.0f}")

        fund_details.append({
            "name": info["name"], "code": code,
            "nav": nav, "chg": fund_chg,
            "mv": mv, "cost": cost_mv,
            "unreal": unreal, "today": today_pnl,
            "holdings": top_pnl[:5],
        })

    # ── 3. 个股持仓 ───────────────────────────────────────────
    print(f"\n📊 个股持仓（收盘价）")
    print("-"*50)
    stock_prices = get_stock_prices(list(STOCKS.keys()))
    stock_details = []
    stock_today = 0.0
    stock_mv = 0.0
    stock_cost = 0.0
    stock_unreal = 0.0

    for code, info in STOCKS.items():
        pd = stock_prices.get(code)
        if pd:
            cur, prev, chg_s = pd
        else:
            cur, chg_s = 0.0, 0.0
        mv    = info["shares"] * cur
        cost  = info["shares"] * info["cost"]
        today = info["shares"] * cur * chg_s / 100
        unreal = mv - cost
        stock_today   += today
        stock_mv      += mv
        stock_cost    += cost
        stock_unreal  += unreal
        stock_details.append({
            "name": info["name"], "code": code,
            "price": cur, "chg": chg_s,
            "shares": info["shares"], "cost_unit": info["cost"],
            "mv": mv, "cost": cost, "today": today, "unreal": unreal,
        })
        print(f"  {info['name']}（{code}）")
        print(f"    现价={cur}(今日{chg_s:+.2f}%) 持有市值={mv:,.0f} 成本={cost:,.0f} 浮盈亏={unreal:+,.0f} 今日盈亏={today:+,.0f}")

    # ── 4. 全局汇总 ───────────────────────────────────────────
    total_mv    = etf_mv    + off_mv_tot    + stock_mv
    total_cost  = etf_cost_tot + off_cost_tot + stock_cost
    total_unreal= etf_unreal + off_unreal_tot + stock_unreal
    total_today = etf_today + off_today_tot + stock_today

    print(f"\n{'='*60}")
    print(f"  📈 持仓汇总  {now.strftime('%Y-%m-%d')}")
    print(f"{'='*60}")
    print(f"  场内ETF:   持有={etf_mv:,.0f} 成本={etf_cost_tot:,.0f} 浮盈亏={etf_unreal:+,.0f}({etf_unreal/etf_cost_tot*100:+.2f}%) 今日={etf_today:+,.0f}")
    print(f"  场外基金:  持有={off_mv_tot:,.0f} 成本={off_cost_tot:,.0f} 浮盈亏={off_unreal_tot:+,.0f}({off_unreal_tot/off_cost_tot*100:+.2f}%) 穿透今日={off_today_tot:+,.0f}")
    print(f"  个股:      持有={stock_mv:,.0f} 成本={stock_cost:,.0f} 浮盈亏={stock_unreal:+,.0f}({stock_unreal/stock_cost*100:+.2f}%) 今日={stock_today:+,.0f}")
    print(f"  ─────────────────────────────────")
    print(f"  合计:     持有={total_mv:,.0f} 成本={total_cost:,.0f}")
    print(f"            浮盈亏={total_unreal:+,.0f}({total_unreal/total_cost*100:+.2f}%)")
    print(f"            今日总盈亏={total_today:+,.0f}元")
    print(f"{'='*60}\n")

    # ── 5. 今日全局重仓股贡献TOP8 ───────────────────────────────
    top8 = sorted(all_top_holds, key=lambda x: abs(x["pnl"]), reverse=True)[:8]
    print("🔝 今日重仓股盈亏贡献TOP8：")
    for i, h in enumerate(top8, 1):
        print(f"  {i}. {h['fund']}｜{h['name']} {h['chg']:+.2f}% → {h['pnl']:+,.0f}元")

    # ── 6. 飞书友好格式 ────────────────────────────────────────
    msg = f"""💰 **沛柔持仓日报 {now.strftime('%Y-%m-%d %H:%M')}**

**📊 今日总盈亏：{total_today:+,.0f}元**
（浮盈 {total_unreal:+,.0f}元 / {total_unreal/total_cost*100:+.2f}%）

**📈 场内ETF**
{"".join(f"- {d['name']} {d['chg']:+.2f}% 今日{d['today']:+,.0f}元" + chr(10) for d in etf_details)}

**📊 场外基金穿透法估算**
{"".join(f"- {fd['name']} {fd['chg']:+.2f}% 今日{fd['today']:+,.0f}元" + chr(10) for fd in fund_details)}

**📉 个股持仓**
{"".join(f"- {sd['name']} {sd['chg']:+.2f}% 今日{sd['today']:+,.0f}元" + chr(10) for sd in stock_details)}

🔝 **今日贡献TOP3重仓股**
{"".join(f"{i+1}. {h['name']} {h['chg']:+.2f}% → {h['pnl']:+,.0f}元（{h['fund']}）" + chr(10) for i, h in enumerate(top8[:3]))}
"""
    print("\n[飞书格式预览]")
    print(msg)

    return {
        "total": {"mv": total_mv, "cost": total_cost,
                  "unreal": total_unreal, "today": total_today},
        "etf":   {"mv": etf_mv, "cost": etf_cost_tot,
                  "unreal": etf_unreal, "today": etf_today, "details": etf_details},
        "off":   {"mv": off_mv_tot, "cost": off_cost_tot,
                  "unreal": off_unreal_tot, "today": off_today_tot,
                  "details": fund_details},
        "stock": {"mv": stock_mv, "cost": stock_cost,
                  "unreal": stock_unreal, "today": stock_today,
                  "details": stock_details},
    }


if __name__ == "__main__":
    result = main()