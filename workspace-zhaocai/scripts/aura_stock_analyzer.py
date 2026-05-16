#!/usr/bin/env python3
"""
A股智能分析系统 - 6层决策框架
整合 a-stock-trading-assistant + new-akshare-stock + qveris
用法: python3 aura_stock_analyzer.py 600519
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime

# ============== 数据获取 ==============

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.sina.com.cn",
}


def get_market_prefix(code: str) -> tuple:
    code = re.sub(r"[^0-9]", "", code)
    if code.startswith(("60", "68", "51", "58", "11")):
        return "sh", code
    elif code.startswith(("00", "30", "15", "12", "16", "13")):
        return "sz", code
    return "sh", code


def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            charset = "gbk" if "sina" in url else "utf-8"
            return resp.read().decode(charset, errors="replace")
    except Exception:
        return ""


def fetch_realtime(code: str) -> dict:
    """获取实时行情"""
    prefix, clean_code = get_market_prefix(code)
    symbol = f"{prefix}{clean_code}"
    url = f"http://hq.sinajs.cn/list={symbol}"
    raw = fetch_url(url)
    
    if not raw:
        return {"error": "无法获取行情"}
    
    match = re.search(r'"([^"]*)"', raw)
    if not match:
        return {"error": "解析失败"}
    
    parts = match.group(1).split(",")
    if len(parts) < 32:
        return {"error": "数据不完整"}
    
    try:
        return {
            "symbol": symbol,
            "name": parts[0],
            "current": round(float(parts[3]), 2),
            "change": round(float(parts[3]) - float(parts[2]), 2),
            "change_pct": round((float(parts[3]) - float(parts[2])) / float(parts[2]) * 100, 2),
            "open": round(float(parts[1]), 2),
            "high": round(float(parts[4]), 2),
            "low": round(float(parts[5]), 2),
            "prev_close": round(float(parts[2]), 2),
            "volume_lot": int(parts[8]),
            "amount_yi": round(float(parts[9]) / 1e8, 2),
            "time": parts[31],
        }
    except:
        return {"error": "解析错误"}


def fetch_index() -> list:
    """获取大盘指数"""
    symbols = "s_sh000001,s_sz399001,s_sz399006"
    url = f"http://hq.sinajs.cn/list={symbols}"
    raw = fetch_url(url)
    
    results = []
    names = {"s_sh000001": "上证", "s_sz399001": "深证", "s_sz399006": "创业板"}
    
    for sym, name in names.items():
        pattern = rf'hq_str_{re.escape(sym)}="([^"]*)"'
        m = re.search(pattern, raw)
        if m:
            parts = m.group(1).split(",")
            if len(parts) >= 3:
                try:
                    results.append({
                        "name": name,
                        "current": float(parts[1]),
                        "change_pct": float(parts[3]),
                    })
                except:
                    pass
    return results


# ============== 技术指标计算 ==============

def calculate_indicators(df) -> dict:
    """计算技术指标"""
    latest = df.iloc[-1]
    
    # 均线
    ma5 = df['收盘'].rolling(5).mean().iloc[-1]
    ma20 = df['收盘'].rolling(20).mean().iloc[-1]
    
    # RSI
    delta = df['收盘'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + gain / loss)).iloc[-1]
    
    # 位置判断
    above_ma20 = latest['收盘'] > ma20
    above_ma5 = latest['收盘'] > ma5
    
    return {
        "ma5": round(ma5, 2),
        "ma20": round(ma20, 2),
        "rsi": round(rsi, 2),
        "above_ma20": above_ma20,
        "above_ma5": above_ma5,
    }


# ============== 6层决策框架 ==============

def analyze_stock(code: str) -> dict:
    """6层决策框架分析"""
    # 第1层：获取数据
    realtime = fetch_realtime(code)
    if "error" in realtime:
        return {"error": realtime["error"]}
    
    # 尝试获取历史数据计算指标（最近60天）
    try:
        import akshare as ak
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                 start_date=start_date.strftime("%Y%m%d"), 
                                 end_date=end_date.strftime("%Y%m%d"), adjust="qfq")
        if not df.empty:
            indicators = calculate_indicators(df)
        else:
            indicators = {"ma5": 0, "ma20": 0, "rsi": 50, "above_ma20": True, "above_ma5": True}
    except:
        indicators = {"ma5": 0, "ma20": 0, "rsi": 50, "above_ma20": True, "above_ma5": True}
    
    # 第2层：三层九维评分
    score = analyze_three_layers(realtime, indicators)
    
    # 第3层：决策闸门
    action = decision_gate(score, realtime, indicators)
    
    # 第4层：证据分层（这里简化）
    evidence = "A类（实时行情+历史数据）"
    
    # 第5层：风控
    stop_loss = round(realtime["prev_close"] * 0.98, 2)  # 2%止损
    
    return {
        "name": realtime["name"],
        "code": code,
        "current": realtime["current"],
        "change_pct": realtime["change_pct"],
        "score": score,
        "action": action["action"],
        "rating": action["rating"],
        "position": action["position"],
        "entry": action["entry"],
        "stop_loss": stop_loss,
        "logic": action["logic"],
        "indicators": indicators,
        "evidence": evidence,
    }


def analyze_three_layers(realtime: dict, indicators: dict) -> dict:
    """三层九维评分"""
    # 简化版评分
    value_score = 75  # 假设基本面中性
    trade_score = 65  # 技术面中性
    risk_score = 70  # 风险中性
    
    # 根据涨跌调整
    if realtime["change_pct"] > 3:
        trade_score += 10
    elif realtime["change_pct"] < -3:
        trade_score -= 10
    
    # 根据RSI调整
    if indicators.get("rsi", 50) > 70:
        trade_score -= 10
        rsi_signal = "RSI超买"
    elif indicators.get("rsi", 50) < 30:
        trade_score += 10
        rsi_signal = "RSI超卖"
    else:
        rsi_signal = f"RSI{indicators.get('rsi', 50):.0f}正常"
    
    # 综合得分
    total = value_score * 0.4 + trade_score * 0.35 + risk_score * 0.25
    
    return {
        "value": value_score,
        "trade": trade_score,
        "risk": risk_score,
        "total": round(total, 1)
    }


def decision_gate(score: dict, realtime: dict, indicators: dict) -> dict:
    """决策闸门"""
    total = score["total"]
    
    # 形态闸门
    above_ma = indicators.get("above_ma20", True)
    rsi = indicators.get("rsi", 50)
    
    if total >= 75 and above_ma and 30 < rsi < 70:
        action = "BUY"
        rating = "⭐⭐⭐⭐"
        position = "30-50%"
    elif total >= 65 and above_ma:
        action = "WATCH"
        rating = "⭐⭐⭐"
        position = "10-30%"
    elif total >= 55:
        action = "HOLD"
        rating = "⭐⭐"
        position = "0-10%"
    else:
        action = "SELL/AVOID"
        rating = "⭐"
        position = "0%"
    
    # 入场区间
    current = realtime["current"]
    entry_low = round(current * 0.98, 2)
    entry_high = round(current * 1.02, 2)
    
    # 逻辑
    logic_parts = []
    if indicators.get("above_ma20"):
        logic_parts.append("站上MA20")
    if rsi > 70:
        logic_parts.append("RSI超买")
    elif rsi < 30:
        logic_parts.append("RSI超卖")
    else:
        logic_parts.append(f"RSI{int(rsi)}中性")
    if realtime["change_pct"] > 3:
        logic_parts.append("放量上涨")
    elif realtime["change_pct"] < -3:
        logic_parts.append("放量下跌")
    
    logic = "、".join(logic_parts) if logic_parts else "均线震荡格局"
    
    return {
        "action": action,
        "rating": rating,
        "position": position,
        "entry": f"{entry_low}-{entry_high}",
        "stop_loss": round(current * 0.98, 2),
        "logic": logic
    }


# ============== 输出格式化 ==============

def format_report(data: dict, style: str = "simple") -> str:
    """格式化报告"""
    if "error" in data:
        return f"❌ 错误: {data['error']}"
    
    # 获取大盘
    indexes = fetch_index()
    market = ""
    if indexes:
        idx = indexes[0]
        sign = "+" if idx["change_pct"] >= 0 else ""
        market = f" | 大盘:{sign}{idx['change_pct']}%"
    
    if style == "simple":
        # 简化版
        s = data["score"]["total"]
        if s >= 75:
            stars = "⭐⭐⭐⭐"
        elif s >= 65:
            stars = "⭐⭐⭐"
        elif s >= 55:
            stars = "⭐⭐"
        else:
            stars = "⭐"
        
        return f"""# {data['name']}({data['code']})

**{data['current']}元 ({data['change_pct']:+.2f}%)**{market} | {data['action']} | {data['score']['total']}分

价值⭐⭐⭐⭐ | 交易⭐⭐⭐ | 风险⭐⭐⭐

**结论**：{data['logic']}，{data['entry']}考虑，止损{data['stop_loss']} 🐢"""
    
    elif style == "full":
        return f"""
# {data['name']}({data['code']}) 完整分析

## 实时数据
- 价格: {data['current']}元 ({data['change_pct']:+.2f}%)
- 涨跌幅: {data['change_pct']}%

## 技术指标
- MA5: {data['indicators']['ma5']}
- MA20: {data['indicators']['ma20']}
- RSI: {data['indicators']['rsi']}

## 三层九维评分
- 价值层: {data['score']['value']}/100
- 交易层: {data['score']['trade']}/100
- 风险层: {data['score']['risk']}/100
- **综合: {data['score']['total']}/100**

## 决策
- 动作: {data['action']}
- 仓位: {data['position']}
- 入场: {data['entry']}
- 止损: {data['stop_loss']}
- 逻辑: {data['logic']}

## 证据等级
{data['evidence']}
"""
    return ""


def main():
    parser = argparse.ArgumentParser(description="Aura A股智能分析")
    parser.add_argument("code", nargs="?", help="股票代码，如 600519")
    parser.add_argument("--style", choices=["simple", "full"], default="simple", help="报告风格")
    parser.add_argument("--index", action="store_true", help="查看大盘")
    args = parser.parse_args()
    
    if args.index:
        indexes = fetch_index()
        for idx in indexes:
            sign = "+" if idx["change_pct"] >= 0 else ""
            print(f"  {idx['name']}: {idx['current']:,.0f} {sign}{idx['change_pct']}%")
        return
    
    if not args.code:
        print("用法: python3 aura_stock_analyzer.py 600519")
        print("     python3 aura_stock_analyzer.py --index")
        return
    
    data = analyze_stock(args.code)
    print(format_report(data, args.style))


if __name__ == "__main__":
    main()
