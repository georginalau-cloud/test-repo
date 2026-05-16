# Trending Now Memory - ZhaoCai

## Status
status: pending
version: 1.0.0
last: 2026-03-24
integration: pending

## Activation Preferences
- 当用户询问"今天股市怎么样"或"有啥投资机会"时激活
- 开盘时间（A股 09:30-15:00）增加检查频率
- 重大政策或市场异动立即提醒

## Monitoring Scope
primary_topics:
- A股大盘走势
- 宏观经济政策
- 金融市场重大事件
- 热门概念板块
exclude_topics:
- 个股日常涨跌（除非有重大消息）
- 娱乐八卦
geography: 中国A股为主，港股美股为辅
language_scope: chinese

## Source Priorities
x_priority: low
community_sources: 雪球、同花顺股吧
publisher_sources: 财联社、东方财富、新浪财经
trend_tools: 资金流向数据、ETF申购数据

## Alert Policy
strictness: balanced
min_score_to_alert: 65
active_hours: 09:00-16:00
timezone: Asia/Shanghai

## Outcomes
- 待记录

## Notes
- 需要至少 2 个独立来源确认
- 警惕假消息和庄家陷阱

---
*Updated: 2026-03-24*
