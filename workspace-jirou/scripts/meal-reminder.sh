#!/bin/bash
# 饮食提醒 - 每天三餐时间提醒用户记录饮食

MESSAGE=$1
LOGFILE="/Users/georginalau/.openclaw/workspace-jiroumiao/memory/meal-reminder.log"

# 记录提醒时间
echo "$(date '+%Y-%m-%d %H:%M:%S'): $MESSAGE" >> "$LOGFILE"

# 可选：发送飞书消息（需要配置webhook）
# curl -X POST "YOUR_WEBHOOK_URL" -H "Content-Type: application/json" -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"$MESSAGE\"}}" 2>/dev/null

echo "Reminder logged: $MESSAGE"
