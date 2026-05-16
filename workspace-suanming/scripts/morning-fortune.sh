#!/bin/bash

# 算命喵 - 每日运势推送 v2
# 沛柔八字: 女命 1990年1月8日 14:54（真太阳时14:03）西安
# 推送时间: 每天 08:00
# 格式: 新版日运（full_report + 本喵发挥合并输出）

# 确保 cron 环境有完整 PATH（解决 env: node: No such file or directory）
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

LOG_FILE="$HOME/.openclaw/workspace-suanming/logs/morning-fortune.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "==========================================" >> "$LOG_FILE"
echo "开始执行每日运势推送: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

# 通过openclaw agent触发算命喵运行日运分析
# 目标用户：沛柔（ou_f9095feb1adeb3f3997725460bcdd87d）
MESSAGE="沛柔早安！🐱🔮 请帮我跑一下今天的日运分析，用新版格式输出（阳历+阴历+干支 + full_report加粗 + 本喵发挥融入每个模块）"

echo "触发算命喵agent..." >> "$LOG_FILE"

/usr/local/bin/openclaw agent \
    --agent suanming \
    --channel feishu \
    --message "$MESSAGE" \
    --deliver \
    --reply-account suanming \
    --reply-to ou_f9095feb1adeb3f3997725460bcdd87d >> "$LOG_FILE" 2>&1

# 如果上面失败，尝试用 PATH 中的 openclaw
if [ $? -ne 0 ]; then
    echo "主命令失败，尝试备用方式..." >> "$LOG_FILE"
    openclaw agent \
        --agent suanming \
        --channel feishu \
        --message "$MESSAGE" \
        --deliver \
        --reply-account suanming \
        --reply-to ou_f9095feb1adeb3f3997725460bcdd87d >> "$LOG_FILE" 2>&1
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "每日运势已成功发送: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
else
    echo "错误: 发送失败，退出码: $EXIT_CODE" >> "$LOG_FILE"
fi

echo "执行结束: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"

exit $EXIT_CODE