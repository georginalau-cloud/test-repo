# 市场异动监控 - Cron 定时任务配置

## 方案一：OpenClaw 内置 Cron（推荐）

在 OpenClaw 配置中添加 Cron 任务，扫描到异动后直接推送飞书：

```
# 每30分钟扫描一次（交易时段）
*/30 9-14 * * 1-5  openclaw exec --name market-alert "cd ~/.openclaw/workspace-zhaocai/skills/market-alert && python3 scripts/scan_alert.py --announce"

# 14:30-15:00 最后扫一次（收盘前）
30 14 * * 1-5  openclaw exec --name market-alert "cd ~/.openclaw/workspace-zhaocai/skills/market-alert && python3 scripts/scan_alert.py --announce"
```

`--announce` 参数确保结果推送给沛柔。

---

## 方案二：直接用 openclaw cron 命令

```bash
# 添加心跳任务（每30分钟，自动推送结果）
openclaw cron add \
  --name "市场异动监控" \
  --schedule "*/30 9-14 * * 1-5" \
  --task "exec" \
  -- "cd /Users/georginalau/.openclaw/workspace-zhaocai/skills/market-alert && python3 scripts/scan_alert.py" \
  --announce

# 查看已配置的cron任务
openclaw cron list
```

---

## 方案三：作为心跳任务（HEARTBEAT）的一部分

在 `HEARTBEAT.md` 中加入市场异动检查作为心跳的一部分。

---

## 手动触发测试

```bash
# 测试模式（不推送）
python3 scripts/scan_alert.py --dry-run

# 单标的扫描
python3 scripts/scan_alert.py --stock 300896

# JSON格式输出（便于程序处理）
python3 scripts/scan_alert.py --json
```

---

## 依赖安装

确保已安装 akshare：
```bash
pip install akshare
```
