#!/usr/bin/env python3
"""获取基金资产配置比例（股票/债券/现金占净比）"""
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

url_template = "https://fundf10.eastmoney.com/zcpz_{code}.html"

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
            html = resp.read().decode('utf-8')
        
        # Find the asset allocation table
        # Table structure: <th>股票占净比</th><th>债券占净比</th><th>现金占净比</th>
        # Data rows: <tr><td>2026-03-31</td><td class="tor">88.50%</td><td class="tor">...</td>
        
        # Extract the first data row (most recent)
        row_pattern = r'<tr><td[^>]*>(\d{4}-\d{2}-\d{2})</td><td[^>]*>([\d.]+)%</td><td[^>]*>([\d.]+)%</td><td[^>]*>([\d.]+)%</td>'
        matches = re.findall(row_pattern, html)
        
        stock_ratio = None
        bond_ratio = None
        cash_ratio = None
        report_date = None
        
        if matches:
            # First match is most recent
            report_date, stock, bond, cash = matches[0]
            stock_ratio = float(stock) / 100
            bond_ratio = float(bond) / 100
            cash_ratio = float(cash) / 100
            print(f"  报告期: {report_date}")
            print(f"  股票占净比: {stock_ratio*100:.2f}%")
            print(f"  债券占净比: {bond_ratio*100:.2f}%")
            print(f"  现金占净比: {cash_ratio*100:.2f}%")
        else:
            print(f"  未匹配到表格数据")
        
        results[code] = {
            'name': name,
            'report_date': report_date,
            'stock_ratio': stock_ratio,
            'bond_ratio': bond_ratio,
            'cash_ratio': cash_ratio,
            'fetched': stock_ratio is not None
        }
        
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  Error: {e}")
        results[code] = {'name': name, 'fetched': False, 'error': str(e)}

output = {
    'update_time': '2026-05-11',
    'source': 'https://fundf10.eastmoney.com/zcpz_{FUND_CODE}.html',
    'funds': results
}

with open('/Users/georginalau/.openclaw/workspace-zhaocai/skills/market-alert/references/fund_asset_allocation.json', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n完成！成功: {sum(1 for v in results.values() if v['fetched'])}/{len(results)}")
print("保存到: references/fund_asset_allocation.json")
