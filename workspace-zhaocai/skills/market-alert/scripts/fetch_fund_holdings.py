#!/usr/bin/env python3
"""获取基金持仓明细（支持A股/港股/美股）"""
import urllib.request
import re
import json
import time

FUNDS = {
    '006751': '富国互联科技A',
    '166002': '中欧新蓝筹A',
    '163402': '兴全趋势投资',
    '004477': '嘉实沪港深回报',
    '001371': '富国沪港深价值精选A',
    '166005': '中欧价值发现A',
    '001668': '汇添富全球移动互联A',
    '000979': '景顺长城沪港深精选A',
    '118001': '易方达亚洲精选',
    '004965': '泓德致远混合A',
    '450009': '国富中小盘A',
    '519069': '汇添富价值精选A',
    '006113': '汇添富创新医药A',
}

url_template = "https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10&year=2026&month=3"

results = {}

for code, name in FUNDS.items():
    url = url_template.format(code=code)
    print(f"Fetching {name}({code})...")
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://fundf10.eastmoney.com/'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode('utf-8')
        
        # Extract content from var apidata={ content:"..." }
        idx1 = raw.find("content:\"")
        if idx1 < 0:
            print(f"  未找到content字段")
            results[code] = {'name': name, 'holdings': [], 'error': 'no content field'}
            continue
        
        start = idx1 + len("content:\"")
        # Find closing quote - look for '";' pattern
        end = raw.find('";', start)
        if end < 0:
            end = raw.find('"', start)
        content = raw[start:end]
        # Unescape
        content = content.replace('\\"', '"').replace('\\n', '').replace('\\t', '')
        
        holdings = []
        # Find all table rows
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL)
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) < 6:
                continue
            
            # Extract text content from cells
            def get_text(c):
                return re.sub(r'<[^>]+>', '', c).strip()
            
            texts = [get_text(c) for c in cells]
            
            # Find stock name (cell after code) and stock code
            stock_code = ''
            stock_name = ''
            pct = 0.0
            shares = 0.0
            mkt_value = 0.0
            
            # Code is usually a 4-6 char identifier (digits or letters)
            # Look for cell with numeric/alphanumeric code that looks like a stock code
            for i, t in enumerate(texts):
                t_clean = t.strip()
                # Match stock code patterns: 6 digits (CN), 5 digits (HK), 4-5 letters (US)
                if re.match(r'^\d{5,6}$', t_clean) or re.match(r'^[A-Z]{3,5}$', t_clean):
                    stock_code = t_clean
                    if i + 1 < len(texts):
                        stock_name = texts[i + 1]
                    break
            
            # Find 占净值比例 - cell containing '%' (not '--')
            for t in texts:
                if '%' in t and '--' not in t:
                    try:
                        pct = float(t.replace('%', '').strip())
                    except:
                        pass
            
            # Find 持股数 (万股) - number with possible comma, not percentage
            for t in texts:
                t_clean = t.strip().replace(',', '')
                if re.match(r'^[\d.]+$', t_clean):
                    try:
                        val = float(t_clean)
                        if 0 < val < 100000:  # reasonable range for shares (万股)
                            shares = val
                    except:
                        pass
            
            # Find 持仓市值 (万元)
            found_mkt = False
            for t in reversed(texts):  # reversed since mkt is usually last
                t_clean = t.strip().replace(',', '')
                if re.match(r'^[\d.]+$', t_clean):
                    try:
                        val = float(t_clean)
                        if val > 100:  # larger values for market cap in 万元
                            mkt_value = val
                            found_mkt = True
                            break
                    except:
                        pass
            
            if stock_name and pct > 0:
                holdings.append({
                    'code': stock_code,
                    'name': stock_name,
                    'percent': pct,
                    'shares': shares,
                    'market_value': mkt_value
                })
        
        results[code] = {
            'name': name,
            'holdings': holdings,
            'num_holdings': len(holdings),
            'fetched': True
        }
        print(f"  ✓ {len(holdings)} 只持仓: {[h['name'] for h in holdings[:5]]}")
        
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results[code] = {'name': name, 'holdings': [], 'error': str(e)}

output = {
    'update_time': '2026-05-11',
    'quarter': 'Q1 2026',
    'source': 'https://fundf10.eastmoney.com/FundArchivesDatas.aspx',
    'funds': results
}

with open('/Users/georginalau/.openclaw/workspace-zhaocai/skills/market-alert/references/fund_holdings_realtime.json', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n完成！成功: {sum(1 for v in results.values() if v.get('fetched'))}/{len(results)}")
print("保存到: fund_holdings_realtime.json")
