# 💓 肌肉 - HEARTBEAT.md

**heartbeat 只做系统健康检查，不检查数据文件，不主动发提醒。**
数据提醒和日报全部由 cron 负责。

---

## ⚠️ 禁止产生"检查清单状态"类消息
- 禁止在 heartbeat 中生成或发送数据完整性报告
- 禁止生成带有"✅ ❌ 🧹 📊"等 emoji 的状态列表
- 如发现此类消息正在发出，立即停止并静默

---

## 每次 heartbeat 检查以下两项

### 1. Garmin Token 状态
```bash
gccli auth status
```
- 正常：静默，回复 HEARTBEAT_OK
- 已过期：**立即**发送提醒给用户（飞书 open_id: ou_aaf284a8365c85e8b792bb77b9bc8d59，accountId: jirou）

> 注意：cron 在每天 21:00 也会专门检查一次 token，heartbeat 是额外保障。

### 2. 关键 API Key 存在性
检查 `.env` 中以下 key 是否非空：
- `GOOGLE_VISION_API_KEY`
- `MINIMAX_API_KEY`
- `USDA_API_KEY`

有缺失：发送提醒给用户。全部正常：静默。

---

## 原则
- 没有问题：只回复 HEARTBEAT_OK，不发任何消息
- 有问题：发一条简洁的提醒，不重复发（同一问题 1 小时内只提醒一次）
- 绝不操作其他 agent 的 workspace 或数据
