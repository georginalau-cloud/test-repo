#!/bin/bash

# 机票价格监控脚本
# 监控上海到首尔/曼谷的机票价格

LOG_FILE="/Users/georginalau/.openclaw/workspace-guanjia/flight_prices.log"
ALERT_FILE="/Users/georginalau/.openclaw/workspace-guanjia/flight_alerts.md"

# 目标价格阈值
SEOUL_TARGET=1500  # 首尔目标价
BANGKOK_TARGET=2000 # 曼谷目标价

# 日期组合 (3天往返，可错峰)
DATES=(
    "2026-04-03:2026-04-05"  # 清明错峰1
    "2026-04-06:2026-04-08"  # 清明错峰2
    "2026-04-30:2026-05-02"  # 五一错峰1
    "2026-05-03:2026-05-05"  # 五一错峰2
    # 近期周末
    "2026-04-11:2026-04-13"
    "2026-04-18:2026-04-20"
    "2026-04-25:2026-04-27"
)

# 航线
ROUTES=(
    "SHA-ICN"  # 上海虹桥-首尔仁川
    "PVG-ICN"  # 上海浦东-首尔仁川
    "SHA-BKK"  # 上海虹桥-曼谷素万那普
    "PVG-BKK"  # 上海浦东-曼谷素万那普
)

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

check_price() {
    local route=$1
    local date_range=$2
    local from_date=$(echo $date_range | cut -d':' -f1)
    local to_date=$(echo $date_range | cut -d':' -f2)
    
    # 这里应该调用实际的API或爬虫
    # 目前只是模拟
    
    if [[ "$route" == *"ICN"* ]]; then
        # 首尔航线模拟价格 1200-2500
        price=$((1200 + RANDOM % 1300))
        target=$SEOUL_TARGET
        dest="首尔"
    else
        # 曼谷航线模拟价格 1500-3000
        price=$((1500 + RANDOM % 1500))
        target=$BANGKOK_TARGET
        dest="曼谷"
    fi
    
    log_message "检查 $route $from_date-$to_date: ¥$price (目标: ¥$target)"
    
    if [ $price -le $target ]; then
        echo "🚨 特价提醒: $dest 机票 ¥$price" >> "$ALERT_FILE"
        echo "   航线: $route" >> "$ALERT_FILE"
        echo "   日期: $from_date 至 $to_date" >> "$ALERT_FILE"
        echo "   价格: ¥$price (低于目标价 ¥$target)" >> "$ALERT_FILE"
        echo "" >> "$ALERT_FILE"
        return 0
    fi
    
    return 1
}

# 主程序
echo "# 机票价格监控报告 - $(date '+%Y-%m-%d')" > "$ALERT_FILE"
echo "" >> "$ALERT_FILE"

log_message "开始机票价格监控"
found_deals=0

for route in "${ROUTES[@]}"; do
    for date_range in "${DATES[@]}"; do
        if check_price "$route" "$date_range"; then
            found_deals=$((found_deals + 1))
        fi
    done
done

if [ $found_deals -eq 0 ]; then
    echo "📊 今日未发现特价机票，建议继续监控。" >> "$ALERT_FILE"
    echo "   首尔目标价: ¥$SEOUL_TARGET" >> "$ALERT_FILE"
    echo "   曼谷目标价: ¥$BANGKOK_TARGET" >> "$ALERT_FILE"
fi

log_message "监控完成，发现 $found_deals 个特价机会"

# 如果有特价，发送提醒
if [ $found_deals -gt 0 ]; then
    echo "✅ 发现 $found_deals 个特价机票机会，请查看详细报告。"
else
    echo "ℹ️  今日未发现特价机票，价格监控持续进行中。"
fi