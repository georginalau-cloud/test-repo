#!/usr/bin/env python3
"""
tail_screen.py
尾盘候选股筛选——前4个硬条件

用法：
    python3 tail_screen.py                    # 标准筛选
    python3 tail_screen.py --chg-min 3      # 最小涨幅（默认3）
    python3 tail_screen.py --chg-max 5      # 最大涨幅（默认5）
    python3 tail_screen.py --top 20         # 显示前N只（默认30）
    python3 tail_screen.py --json           # JSON输出
"""
import argparse
import json
from datetime import datetime


def get_realtime_data():
    """用akshare获取全A股实时行情"""
    import akshare as ak

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 获取全A股实时数据...")
    df = ak.stock_zh_a_spot_em()
    # 过滤ST、退市、停牌
    df = df[~df['名称'].str.contains('ST|退|停', na=False)]
    # 过滤涨跌停（涨跌停次日无溢价空间）
    df = df[df['涨跌幅'] > 0]  # 排除下跌
    print(f"  共有 {len(df)} 只股票")
    return df


def filter_stocks(df, chg_min=3.0, chg_max=5.0, top=30):
    """前4个硬条件筛选"""
    # 量比、换手率、流通市值列名检查
    vol_ratio_col = '量比' if '量比' in df.columns else None
    hs_col = '换手率' if '换手率' in df.columns else None
    mkt_cap_col = None
    for col in df.columns:
        if '流通' in col and '市值' in col:
            mkt_cap_col = col
            break

    print(f"\n筛选条件: 涨幅{chg_min}-{chg_max}%", end="")
    if vol_ratio_col:
        print(f" · 量比>1", end="")
    if hs_col:
        print(f" · 换手率>5%", end="")
    if mkt_cap_col:
        print(f" · 流通市值50-500亿", end="")
    print()

    # 基础条件：涨幅区间
    cond = (df['涨跌幅'] >= chg_min) & (df['涨跌幅'] <= chg_max)

    # 量比>1
    if vol_ratio_col:
        cond = cond & (df[vol_ratio_col] > 1)

    # 换手率>5
    if hs_col:
        cond = cond & (df[hs_col] > 5)

    # 流通市值50-500亿（单位：元 → /1e8换算为亿）
    if mkt_cap_col:
        cond = cond & (df[mkt_cap_col] >= 50e8) & (df[mkt_cap_col] <= 500e8)

    df_filtered = df[cond].copy()

    # 按换手率排序
    sort_col = hs_col if hs_col else '涨跌幅'
    df_filtered = df_filtered.sort_values(sort_col, ascending=False).head(top)

    # 整理输出列
    out_cols = ['代码', '名称', '最新价', '涨跌幅']
    if vol_ratio_col:
        out_cols.append(vol_ratio_col)
    if hs_col:
        out_cols.append(hs_col)
    if mkt_cap_col:
        df_filtered['流通市值(亿)'] = df_filtered[mkt_cap_col] / 1e8
        out_cols.append('流通市值(亿)')

    result = df_filtered[out_cols].copy()
    result['涨跌幅'] = result['涨跌幅'].apply(lambda x: f"{x:+.2f}%")
    for col in out_cols[3:]:
        if col != '涨跌幅' and col != '流通市值(亿)':
            result[col] = result[col].apply(lambda x: f"{x:.2f}")

    return result, out_cols


def run(chg_min=3.0, chg_max=5.0, top=30, json_output=False):
    import akshare as ak

    df = get_realtime_data()
    result, out_cols = filter_stocks(df, chg_min, chg_max, top)

    if json_output:
        out = result.to_dict(orient='records')
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    now = datetime.now().strftime('%H:%M')
    print(f"\n{'='*65}")
    print(f"  ⚡ 尾盘候选股 | {now}")
    print(f"  条件: 涨幅{chg_min}-{chg_max}% · 量比>1 · 换手率>5% · 流通50-500亿")
    print(f"{'='*65}")

    if result.empty:
        print("  暂无符合条件股票")
        return

    print(f"\n候选股（共{len(result)}只，按换手率排序）：\n")

    # 表头
    header = f"  {'代码':<8}{'名称':<10}{'最新价':>8}{'涨跌幅':>8}",
    if '量比' in out_cols:
        header += f"{'量比':>6}",
    if '换手率' in out_cols:
        header += f"{'换手率':>8}",
    if '流通市值(亿)' in out_cols:
        header += f"{'流通市值':>10}",
    print("  " + "".join(f"{'代码':<8}{'名称':<10}{'最新价':>8}{'涨跌幅':>8}{'量比':>6}{'换手率':>8}{'流通市值':>10}"))
    print("  " + "-"*62)

    for _, row in result.iterrows():
        code = row['代码']
        name = row['名称']
        price = row['最新价']
        chg = row['涨跌幅']
        vr = row.get('量比', '-')
        hs = row.get('换手率', '-')
        mc = f"{row['流通市值(亿)']:.0f}" if '流通市值(亿)' in row else '-'
        print(f"  {code:<8}{name:<10}{price:>8}{chg:>8}{vr:>6}{hs:>8}{mc:>10}")

    print(f"\n{'='*65}")
    print(f"  ⚠️ 人工复核项（选股后需确认）：")
    print(f"  □ 成交量是否持续放大（>5日均量20%以上）")
    print(f"  □ K线是否在重要均线上方（MA5/MA10/MA20多头）")
    print(f"  □ 分时图是否在均价线上方")
    print(f"  □ 2:30左右是否创当天新高后回踩")
    print(f"  ⚠️ 尾盘异动可能是主力骗线，严格复核第5-8步！")
    print(f"{'='*65}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="尾盘候选股筛选")
    parser.add_argument('--chg-min', type=float, default=3.0, help='最小涨幅（默认3）')
    parser.add_argument('--chg-max', type=float, default=5.0, help='最大涨幅（默认5）')
    parser.add_argument('--top', type=int, default=30, help='显示数量（默认30）')
    parser.add_argument('--json', action='store_true', help='JSON输出')
    args = parser.parse_args()
    run(chg_min=args.chg_min, chg_max=args.chg_max, top=args.top, json_output=args.json)
