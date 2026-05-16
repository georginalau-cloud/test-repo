# MEMORY.md - 长期记忆

## 用户信息
- **用户名:** 沛柔
- **飞书 Open ID:** `ou_aaf284a8365c85e8b792bb77b9bc8d59`
- **时区:** Asia/Shanghai

## 健康目标
- 体重目标: 55kg（当前58.3kg）
- 体脂目标: 22-24%（当前24.7%，已接近）
- 内脏脂肪: 5（已达标，正常）
- 身体年龄: 35岁（比实际36岁年轻，已逆转）

## 健身偏好
- 使用有品智能秤 + Garmin (georginalau@163.com, garmin.cn)
- **BMR 以 Garmin 数据为准**（已记录在技术配置）
- 早餐有时不吃（需提醒）
- 晚餐倾向健康家常菜
- 偶尔吃快餐/甜点

## 技术配置
- **BMR 以 Garmin 数据为准**（Garmin BMR = 1543 kcal，有品秤仅作参考）
- Garmin CLI: `gccli auth login georginalau@163.com`（中国区域名）
- 用户ID曾配置错误（`ou_e62c3623b382df683370c131baf8f4c8`），已修复为正确ID

## 关键事件
- 2026-03-30: Garmin重新连接成功，体脂从27.8%降到24.7%，减脂效果显著
- 2026-03-30: 修复所有消息转发任务的错误用户ID

## 2026-05-13 发现并修复的 Bug

### 日报 BMR 数据源错误（已修复）
- 体重与身体成分表中的 BMR 错误使用了有品秤数据（1316 kcal）
- 正确做法：直接使用 Garmin BMR（1475 kcal）
- 原因：MEMORY.md 和 SOUL.md 都明确写了"BMR 以 Garmin 数据为准"
- 修复：日报生成时，BMR 统一从 Garmin 数据读取，不再从有品秤数据获取
1. `load_meal_data`：检查 `data.get('success')` 但存储数据无此字段 → 改为只检查 `items`
2. `load_scale_data`：字段名映射错误（存储用 `weight_kg`，脚本期望 `weight`）→ 增加映射层
3. `format_meal_section`：用 `food_name` 但存储用 `name` → 兼容两个字段

### 输出路径bug（已修复）
- 脚本默认输出到 `memory/reports/`，但 OpenClaw cron 在 `memory/pending/` 找
- 修复：改为默认 `memory/pending/`

### 体脂异常
- 2026-04-16 早晨体脂 29.3%（昨天傍晚 25.3%）→ 可能是测量误差，继续观察
