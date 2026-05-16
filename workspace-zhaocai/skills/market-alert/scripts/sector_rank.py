#!/usr/bin/env python3
"""
A股板块涨跌排行 - sector_rank.py
使用 akshare 获取东方财富行业板块数据
"""

import sys
import json
from datetime import datetime

def get_industry_sectors(limit=20):
    """获取行业板块涨跌排行"""
    try:
        import akshare as ak
        df = ak.stock_sector_spot()
        
        sectors = []
        for _, row in df.iterrows():
            change_pct = row.get('涨跌幅', 0)
            sectors.append({
                'name': row.get('板块', ''),
                'change_percent': float(change_pct) if change_pct else 0,
                'change': row.get('涨跌额', 0),
                'volume': row.get('总成交量', 0),
                'amount': row.get('总成交额', 0),
                'stocks': row.get('公司家数', 0),
                'lead_stock': row.get('股票名称', ''),
                'lead_code': row.get('股票代码', ''),
                'lead_change': row.get('个股-涨跌幅', 0),
            })
        
        sectors.sort(key=lambda x: x['change_percent'], reverse=True)
        return sectors[:limit]
    except Exception as e:
        return {'error': str(e)}

def format_industry_report(sectors, limit=15):
    """格式化行业板块报告"""
    if isinstance(sectors, dict) and 'error' in sectors:
        return f"❌ 获取失败: {sectors['error']}"
    
    now = datetime.now()
    time_str = now.strftime("%m月%d日 %H:%M")
    
    top = sectors[:10]
    bottom = sectors[-5:] if len(sectors) > 5 else []
    
    lines = []
    lines.append(f"📊 A股行业板块涨跌（{time_str}）")
    lines.append("=" * 50)
    lines.append("🔥 涨幅TOP10")
    for i, s in enumerate(top, 1):
        sign = '+' if s['change_percent'] >= 0 else ''
        medal = '🥇' if i == 1 else '🥈' if i == 2 else '🥉' if i == 3 else '  '
        lines.append(f" {medal}{i:2d}. {s['name']:<10s} {sign}{s['change_percent']:>6.2f}%  领涨:{s['lead_stock']}({s['lead_change']:+.2f}%)")
    if bottom:
        lines.append("")
        lines.append("❄️ 跌幅TOP5")
        for i, s in enumerate(bottom, 1):
            sign = '+' if s['change_percent'] >= 0 else ''
            lines.append(f"    {i}. {s['name']:<10s} {sign}{s['change_percent']:>6.2f}%")
    lines.append("=" * 50)
    lines.append("💡 数据来源：东方财富 | 延迟约15分钟")
    return '\n'.join(lines)

def output_json(sectors):
    """输出JSON格式"""
    result = {
        'type': 'industry',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sectors': sectors if isinstance(sectors, list) else []
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='A股板块涨跌查询')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    
    sectors = get_industry_sectors(args.limit)
    if args.json:
        output_json(sectors)
    else:
        print(format_industry_report(sectors, args.limit))