# 紫微斗数skill - suanming-ziwei

## 介绍
基于 iztro-py 的紫微斗数排盘工具，为沛柔提供紫微斗数命盘分析。

## 核心依赖
- `vendor/iztro_py` (Python紫微斗数排盘库)

## 调用方式
```bash
python3 bin/ziwei --year 1990 --month 1 --day 8 --hour 14 --minute 54 --gender female --city 上海 --mode full
```

## 参数说明
- `--year` 出生年
- `--month` 出生月
- `--day` 出生日
- `--hour` 出生小时（24小时制）
- `--minute` 出生分钟
- `--gender` male/female
- `--city` 出生城市（用于时区校准）
- `--mode` full（完整命盘）/ quick（仅排盘）

## 输出
JSON格式，包含：
- 四柱信息
- 紫微斗数十二宫星曜
- 主星、副星、化曜分布

## ⚠️ Self-Verify 输出前核查

发出结论前，对照原始输出逐项核查：

1. **结论溯源**：所有命理判断必须能在 JSON 输出里找到对应字段
2. **五行/宫位术语**：星曜名、化曜、宫名必须与 iztro-py 输出一致，禁止自行发明
3. **不确定结论降级**：出现"绝对/肯定/永远"→ 改写为"可能/通常/大概率"
4. **通过检查后再输出**

## 状态
⚠️ 框架已搭建，bin/ziwei 入口脚本待编写
