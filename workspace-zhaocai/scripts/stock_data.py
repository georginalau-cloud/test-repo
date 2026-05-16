#!/usr/bin/env python3
"""
A股持仓行情查询脚本
数据来源：新浪财经（国内股票/ETF通用）
原因：东方财富接口对Python爬虫有反爬限制，新浪接口稳定可用
"""
import requests
from datetime import datetime

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.sina.com.cn/",
})

SINA_URL = "https://hq.sinajs.cn/list="

# 持仓数据（代码需加 sh/sz 前缀）
HOLDINGS = {
    "sz300896": {"name": "爱美客",       "qty": 420,  "cost": 478.847},
    "sh600309": {"name": "万华化学",     "qty": 300,  "cost": 88.690},
    "sh600352": {"name": "浙江龙盛",     "qty": 1000, "cost": 12.924},
    "sh688363": {"name": "华熙生物",     "qty": 300,  "cost": 238.043},
    "sz002176": {"name": "江特电机",     "qty": 1000, "cost": 25.506},
    "sz002172": {"name": "澳洋健康",     "qty": 2000, "cost": 6.530},
    "sz000652": {"name": "泰洋股份",     "qty": 1000, "cost": 10.105},
    "sz002551": {"name": "尚荣医疗",     "qty": 1000, "cost": 4.600},
    "sh600221": {"name": "海航控股",     "qty": 1000, "cost": 6.236},
    "sh516650": {"name": "有色金属ETF",  "qty": 8000, "cost": 2.449},
    "sz159566": {"name": "储能电池ETF",  "qty": 3000, "cost": 2.085},
    "sz161725": {"name": "招商中证白酒A","qty": 5000, "cost": 1.355},
    "sh400201": {"name": "海投5",        "qty": 3000, "cost": 0.750},  # 可能停牌
}


def fetch_prices(codes_str: str) -> dict:
    """批量获取新浪行情，返回 {code: {name, current, prev_close, pct}}"""
    r = SESSION.get(SINA_URL + codes_str, timeout=15)
    r.encoding = 'gbk'
    result = {}
    for line in r.text.strip().split('\n'):
        if '=' not in line or len(line.split('"')) < 2:
            continue
        raw_code = line.split('=')[0].split('_')[-1]
        data = line.split('"')[1]
        fields = data.split(',')
        if len(fields) < 4 or not fields[0]:
            continue
        code_key = raw_code  # e.g. "sz300896"
        result[code_key] = {
            "name": fields[0],
            "current": float(fields[3]),
            "prev_close": float(fields[2]),
        }
    return result


def main():
    codes_str = ",".join(HOLDINGS.keys())
    prices = fetch_prices(codes_str)

    print(f"📊 持仓快照 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 55)

    total_pl = 0
    for code_key, info in HOLDINGS.items():
        if code_key not in prices:
            print(f"❌ {info['name']}({code_key}): 数据不可用")
            continue
        p = prices[code_key]
        current = p['current']
        pct = (current - p['prev_close']) / p['prev_close'] * 100
        pl = (current - info['cost']) * info['qty']
        total_pl += pl
        emoji = "📈" if pl >= 0 else "📉"
        print(f"{emoji} {info['name']}: 现价={current:.3f} {pct:+.2f}% | 浮盈{pl:+,.0f}")

    print("=" * 55)
    emoji = "💰" if total_pl >= 0 else "💸"
    print(f"{emoji} 合计浮盈: {total_pl:+,.0f} 元")


if __name__ == "__main__":
    main()
