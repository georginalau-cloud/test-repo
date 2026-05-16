#!/bin/bash
# 健康日报自动生成脚本
# 每天 9:00 自动执行

WORKSPACE="/Users/georginalau/.openclaw/workspace-jiroumiao"
DATE=$(date -v-1d +%Y-%m-%d)  # 昨天
YEAR=$(date -v-1d +%Y)
MONTH=$(date -v-1d +%m)
DAY=$(date -v-1d +%d)
WEEKDAY=$(date -v-1d +%u)
WEEKS=("一" "二" "三" "四" "五" "六" "日")

echo "📊 生成健康日报 for ${DATE}"

# 1. 获取 Garmin 数据
cd "$WORKSPACE"
YESTERDAY_GARMIN=$(gccli health summary ${DATE} 2>/dev/null)
YESTERDAY_SLEEP=$(gccli health sleep ${DATE} 2>/dev/null)
YESTERDAY_HRV=$(gccli health hrv ${DATE} 2>/dev/null)

# Garmin 数据提取
RESTING_HR=$(echo "$YESTERDAY_GARMIN" | grep -o '"restingHeartRate":[0-9]*' | cut -d: -f2)
HRV=$(echo "$YESTERDAY_HRV" | grep -o '"lastNightAvg":[0-9]*' | cut -d: -f2)
TOTAL_CAL=$(echo "$YESTERDAY_GARMIN" | grep -o '"totalKilocalories":[0-9]*' | cut -d: -f2)
ACTIVE_CAL=$(echo "$YESTERDAY_GARMIN" | grep -o '"activeKilocalories":[0-9]*' | cut -d: -f2)
STEPS=$(echo "$YESTERDAY_GARMIN" | grep -o '"totalSteps":[0-9]*' | cut -d: -f2)
DISTANCE=$(echo "$YESTERDAY_GARMIN" | grep -o '"totalDistanceMeters":[0-9]*' | cut -d: -f2 | awk '{print $1/1000}')

# 睡眠数据
SLEEP_SCORE=$(echo "$YESTERDAY_SLEEP" | grep -o '"overall":{"value":[0-9]*' | cut -d: -f2 | tail -1)
SLEEP_DURATION=$(echo "$YESTERDAY_SLEEP" | grep -o '"sleepTimeSeconds":[0-9]*' | cut -d: -f2 | awk '{print $1/3600}')
DEEP_SLEEP=$(echo "$YESTERDAY_SLEEP" | grep -o '"deepSleepSeconds":[0-9]*' | cut -d: -f2 | awk '{print $1/3600}')
LIGHT_SLEEP=$(echo "$YESTERDAY_SLEEP" | grep -o '"lightSleepSeconds":[0-9]*' | cut -d: -f2 | awk '{print $1/3600}')
REM_SLEEP=$(echo "$YESTERDAY_SLEEP" | grep -o '"remSleepSeconds":[0-9]*' | cut -d: -f2 | awk '{print $1/3600}')
AWAKE_SLEEP=$(echo "$YESTERDAY_SLEEP" | grep -o '"awakeSleepSeconds":[0-9]*' | cut -d: -f2 | awk '{print $1/3600}')

# 2. 生成健康日报 (完整模板格式)
REPORT_FILE="$WORKSPACE/memory/Health ${YEAR}-${MONTH}-${DAY}.md"

cat > "$REPORT_FILE" << EOF
📊 ${YEAR}年${MONTH}月${DAY}日 星期${WEEKS[$((WEEKDAY-1))]} 健康日报

## ⚖️ 身体数据
  - 体重: - kg（白）/ - kg（晚）
  - 体脂: -%（白）/ -%（晚）
  - 肌肉：-%（白）/ -%（晚）
  - 储肌能力：-（白）/-（晚）
  - 内脏脂肪：-（白）/-（晚）
  - 水分：-%（白）/ -%（晚）
  - 蛋白质：-%（白）/ -%（晚）
  - 骨量：- kg（白）/ - kg（晚）
  - 静息心率: ${RESTING_HR:- -} bpm
  - HRV: ${HRV:- -} ms
  - BMR: 1543 kcal
  - 最大摄氧量: -

## 😴 睡眠情况
  - 得分: ${SLEEP_SCORE:- -}
  - 时长: ${SLEEP_DURATION:- -}h
  - 阶段：深睡${DEEP_SLEEP:- -}h / 浅睡${LIGHT_SLEEP:- -}h / REM ${REM_SLEEP:- -}h / 清醒${AWAKE_SLEEP:- -}h

## 🔥 热量情况
  - 总摄入: - kcal
  - 总消耗: ${TOTAL_CAL:- -} kcal
  - 缺口: - kcal

### 🍽️ 昨日摄入
  - 早餐：- ~ kcal
  - 午餐：- ~ kcal
  - 晚餐：- ~ kcal
  - 零食：-

### 💪 昨日消耗
#### 🏃 日常活动（支出1）
  - 步数: ${STEPS:- -}步
  - 距离: ${DISTANCE:- -} km
  - 活动消耗: ${ACTIVE_CAL:- -} kcal

#### 🏋️ 昨日运动（支出2）
  - [运动详情]：-
  - 运动时长：-
  - 运动消耗：-
  - 平均心率：-
  - 最大心率：-

*消耗 = 支出1 + 支出2 = ${TOTAL_CAL:- -} kcal
EOF

echo "✅ 日报已生成: $REPORT_FILE"