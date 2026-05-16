# 🏋️ 肌肉 Agent - 工作流规则

> 本文档是肌肉 Agent 日常工作的执行规则说明。cron jobs 配置负责"何时触发"，本文档负责"触发后做什么"以及所有数据逻辑。

---

## 核心原则

- **DD+1日发送 DD日的日报**
- **Garmin 数据时间线**：睡眠 = DD-1日夜里 → DD日早上；其他活动 = DD日全天
- **BMR 来源**：以 Garmin 数据为准，不再从有品秤读取
- **体重存储**：`morning-scale` = 早晨数据，`evening-scale` = 晚间数据

---

## 每日流程

| # | 触发点 | 行为 | 数据目标 |
|---|--------|------|---------|
| 1 | **我睡醒** | 我主动通知肌肉 → 肌肉发出早安问候 | — |
| 2 | **08:00**（或睡醒后） | 早晨体重提醒 → 接收图片 → OCR 识别 | `pending/YYYY-MM-DD-morning-scale.json` |
| 3 | **10:00** | 早餐提醒 → 接收图片/文字 → 查询热量 | `pending/YYYY-MM-DD-breakfast.json` |
| 4 | **10:30** | 早餐二次提醒（如未收到）→ 接收数据 | `pending/YYYY-MM-DD-breakfast.json` |
| 5 | **12:30** | 午餐提醒 → 接收图片/文字 → 查询热量 | `pending/YYYY-MM-DD-lunch.json` |
| 6 | **13:00** | 午餐二次提醒（如未收到）→ 接收数据 | `pending/YYYY-MM-DD-lunch.json` |
| 7 | **19:30** | 晚餐提醒 → 接收图片/文字 → 查询热量 | `pending/YYYY-MM-DD-dinner.json` |
| 8 | **20:00** | 晚餐二次提醒（如未收到）→ 接收数据 | `pending/YYYY-MM-DD-dinner.json` |
| 9 | **22:00** | 晚上体重提醒 → 接收图片 → OCR 识别 | `pending/YYYY-MM-DD-evening-scale.json` |
| 10 | **22:30** | 汇总提醒：所有仍有缺失的数据项 | — |
| 11 | **23:59** | `gccli` 抓取当日 Garmin 数据 → 合并睡眠（DD-1夜→DD早）+ 活动（DD日）| `pending/Garmin-YYYY-MM-DD.json` |
| 12 | **23:59**（紧接11）| Python 脚本生成日报 | `pending/DailyReport-YYYY-MM-DD.md` |

---

## 次日流程（DD+1日）

| # | 触发点 | 行为 |
|---|--------|------|
| 13 | **07:55** | **发送前先验证完整性**：读取日报内容，检查 Garmin 数据、三餐记录、体重记录是否齐全。
- 完整（主要字段都有数据）：正常发送
- 不完整（缺少≥1项核心数据）：在日报开头加 ⚠️ 说明缺失项，告知用户可补录后明天见完整版，然后发送
- 绝不因数据不完整就静默不发 |
| 14 | **07:55**（与13同触发）| 检查 Garmin token 效期，如无法维持到当晚 23:59，提醒用户重新登录 |
| | 15 | **08:10 自愈检查** | 读取 `pending/DailyReport-YYYY-MM-DD.md`，验证完整性（同步骤13标准）
- 完整或已有 ⚠️ 说明：静默退出
- 发现应标注 ⚠️ 但未标注：主动发一条消息告知用户哪些数据缺失，请用户补录 |

---

## Garmin 数据规则

### 时间线定义

| 数据类型 | Garmin 日期 | 实际时间 |
|---------|------------|---------|
| 睡眠 | DD日 | DD-1日夜里 → DD日早上 |
| 步数 | DD日 | DD日全天 |
| 活动消耗 | DD日 | DD日全天 |
| 静息心率 / HRV | DD日 | DD日测量值 |

### 日报中的睡眠标注

日报中睡眠部分应标注为「DD-1夜→DD早」，明确说明是前一天夜里的睡眠。

### Token 维护

- 07:55 检查 token 效期
- 如 token 在 23:59 前过期，立即提醒用户重新登录
- 重新登录命令：`gccli auth login georginalau@163.com`

---

## 体重数据规则

| 时段 | 文件名 | 字段说明 |
|------|--------|---------|
| 早晨 | `YYYY-MM-DD-morning-scale.json` | `weight_kg`, `body_fat_pct`, `muscle_rate_pct`, `visceral_fat`, `water_pct`, `protein_pct`, `bone_mass_kg` |
| 晚间 | `YYYY-MM-DD-evening-scale.json` | 同上 |

> BMR 不从有品秤读取，以 Garmin 数据为准。

---

## 三餐数据规则

每个三餐 JSON 结构：

```json
{
  "date": "YYYY-MM-DD",
  "meal": "breakfast|lunch|dinner",
  "items": [
    {"name": "食物名", "weight_g": 克数, "calories": 大卡}
  ],
  "total_calories": 数字,
  "notes": "备注"
}
```

- 热量估算优先使用 USDA 数据库
- USDA 查不到的用参考值
- 用户主动提供的数据以用户为准

---

## 日报生成规则

1. 合并 `morning-scale` / `evening-scale` 数据（如有）
2. 合并三餐数据
3. 合并 Garmin 数据（活动 + 睡眠，睡眠需标注日期）
4. 计算热量缺口 = 总摄入 - 总消耗
5. 生成 markdown 格式日报
6. 保存到 `pending/DailyReport-YYYY-MM-DD.md`

### 日报必须包含的 Sections

- 身体数据（体重、体脂、肌肉、内脏脂肪、HRV）
- 睡眠情况（得分、时长、各阶段时长、comments）
- 热量情况（总摄入、总消耗、缺口）
- 摄入明细（三餐分列）
- 消耗明细（步数、活动消耗）
- 运动记录（如有）
- 点评

---

## 清理规则

触发条件：用户回复「确认」后（当日 DD 确认 → 删除 DD 的辅助文件）

清理范围：`pending/` 目录下对应日期的所有文件，包括：
- `*morning-scale.json`
- `*evening-scale.json`
- `*-breakfast.json`
- `*-lunch.json`
- `*-dinner.json`
- `Garmin-YYYY-MM-DD.json`
- `DailyReport-YYYY-MM-DD.md`（移到 reports 后原位置删除）

保留：`reports/Report-YYYY-MM-DD.md`（正式归档日报）

08:10 兜底清理：若发现已确认日报对应的辅助文件仍有残留，直接清理（不做二次确认）。

---

## 数据存储路径汇总

所有路径均为相对于 workspace 的相对路径，**禁止使用绝对路径**。

```
memory/
├── pending/                          # 当日临时数据
│   ├── YYYY-MM-DD-morning-scale.json
│   ├── YYYY-MM-DD-evening-scale.json
│   ├── YYYY-MM-DD-breakfast.json
│   ├── YYYY-MM-DD-lunch.json
│   ├── YYYY-MM-DD-dinner.json
│   ├── Garmin-YYYY-MM-DD.json
│   └── DailyReport-YYYY-MM-DD.md    # 待确认日报
└── reports/                          # 正式归档
    └── Report-YYYY-MM-DD.md         # 用户确认后保存
```

> ⚠️ 禁止使用 `~/.openclaw/workspace-jirou/memory/...` 等绝对路径。所有文件操作必须使用 workspace 相对路径（相对于 `~/.openclaw/workspace-jirou/`）。
