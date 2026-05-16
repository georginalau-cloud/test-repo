#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补生成历史日报脚本"""
import json, os
from datetime import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace-jirou")
PENDING = os.path.join(WORKSPACE, "memory", "pending")
REPORTS = os.path.join(WORKSPACE, "memory", "reports")

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

def safe_int(v):
    try:
        return int(float(v))
    except:
        return 0

def day_name(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return ["周一","周二","周三","周四","周五","周六","周日"][d.weekday()]

def fmt(v, suffix=""):
    try:
        return f"{float(v):.1f}{suffix}"
    except:
        return "?"

DATES = ["2026-04-11", "2026-04-13", "2026-04-14"]

for DATE in DATES:
    print(f"\n=== Generating {DATE} ===")

    # Meals
    bm = load_json(f"{PENDING}/{DATE}-breakfast.json")
    lu = load_json(f"{PENDING}/{DATE}-lunch.json")
    di = load_json(f"{PENDING}/{DATE}-dinner.json")

    def meal_cal(m):
        if not m: return 0
        return m.get("total_calories") or m.get("total_calories_kcal") or 0
    def meal_desc(m):
        if not m: return "无记录"
        return " / ".join([f"{i.get('name','?')}" for i in m.get("items",[])])[:50]

    bm_cal = safe_int(meal_cal(bm))
    lu_cal = safe_int(meal_cal(lu))
    di_cal = safe_int(meal_cal(di))
    total_in = bm_cal + lu_cal + di_cal

    # Scale
    sm = load_json(f"{PENDING}/{DATE}-morning-scale.json")
    se = load_json(f"{PENDING}/{DATE}-evening-scale.json")

    def scale_val(s, k, pct=False):
        if not s: return "—"
        d = s.get("data") or s
        v = d.get(k) or d.get(k.replace("_pct","").replace("_kg",""))
        if not v or v == "未测量": return "—"
        suffix = "%" if pct else (" kg" if "kg" in k else "")
        return f"{v}{suffix}"

    # Garmin
    gar = load_json(f"{PENDING}/Garmin-{DATE}.json")

    if gar:
        # New format with summary key
        if "summary" in gar:
            s = gar.get("summary") or {}
            steps = safe_int(s.get("totalSteps") or s.get("steps") or 0)
            total_cal = safe_int(s.get("totalKilocalories") or s.get("total_calories") or 0)
            bmr = safe_int(s.get("bmrKilocalories") or s.get("bmr") or 1543)
            active_cal = safe_int(s.get("activeKilocalories") or s.get("active_calories") or 0)
            resting_hr = s.get("restingHeartRate") or s.get("resting_hr") or "?"
            avg_stress = s.get("averageStressLevel") or s.get("avg_stress") or "?"
            sleep_d = gar.get("sleep") or {}
            night = sleep_d.get("night_sleep") if isinstance(sleep_d, dict) else None
        elif "totalSteps" in gar or "steps" in gar:
            steps = safe_int(gar.get("totalSteps") or gar.get("steps") or 0)
            total_cal = safe_int(gar.get("totalCalories") or gar.get("total_calories") or 0)
            bmr = safe_int(gar.get("bmrCalories") or gar.get("bmr") or 1543)
            active_cal = safe_int(gar.get("activeCalories") or gar.get("active_calories") or 0)
            resting_hr = gar.get("restingHeartRate") or "?"
            avg_stress = "?"
            slp = gar.get("sleep") or {}
            total_s = slp.get("duration_s") or 0
            deep_s = slp.get("deep_s") or 0
            light_s = slp.get("light_s") or 0
            rem_s = slp.get("rem_s") or 0
            awake_s = slp.get("awake_s") or 0
            night = {
                "total_h": round(total_s/3600, 1),
                "deep_h": round(deep_s/3600, 1),
                "light_h": round(light_s/3600, 1),
                "rem_h": round(rem_s/3600, 1),
                "awake_m": round(awake_s/60),
            }
        else:
            gar = None

    if not gar:
        steps, total_cal, bmr, active_cal, resting_hr, avg_stress = 0, 0, 1543, 0, "?", "?"
        night = None
        print(f"  WARNING: No Garmin data for {DATE}")

    deficit = total_in - total_cal if total_cal else 0
    weekday = day_name(DATE)
    d = datetime.strptime(DATE, "%Y-%m-%d")
    datename = f"{d.month}月{d.day}日"

    # Sleep section
    sleep_md = ""
    if night:
        sleep_md = f"""  - 时长: {night.get('total_h', night.get('total_hours','—'))}h
  - 深睡: {night.get('deep_h', night.get('deep_hours','—'))}h / 浅睡 {night.get('light_h', night.get('light_hours','—'))}h / REM {night.get('rem_h', night.get('rem_hours','—'))}h / 清醒 {night.get('awake_m','—')}m
"""
    else:
        sleep_md = "  无数据\n"

    deficit_sign = "⚠️摄入不足" if deficit < -200 else ("💪热量缺口良好" if deficit > 0 else "基本平衡")
    if not gar:
        total_cal_str = "?"
    else:
        total_cal_str = str(total_cal)

    report = f"""📊 {datename} {weekday} 健康日报

---

## ⚖️ 身体数据
  - 体重: {scale_val(sm, 'weight_kg')} kg（晨）/ {scale_val(se, 'weight_kg')} kg（晚）
  - 体脂: {scale_val(sm, 'body_fat_pct', pct=True)}（晨）/ {scale_val(se, 'body_fat_pct', pct=True)}（晚）
  - 肌肉：{scale_val(sm, 'muscle_rate_pct', pct=True)}（晨）/ {scale_val(se, 'muscle_rate_pct', pct=True)}（晚）
  - 储肌能力：{scale_val(sm, 'muscle_level')}（晨）/ {scale_val(se, 'muscle_level')}（晚）
  - 内脏脂肪：{scale_val(sm, 'visceral_fat')}（晨）/ {scale_val(se, 'visceral_fat')}（晚）
  - 水分：{scale_val(sm, 'water_pct', pct=True)}（晨）/ {scale_val(se, 'water_pct', pct=True)}（晚）
  - 蛋白质：{scale_val(sm, 'protein_pct', pct=True)}（晨）/ {scale_val(se, 'protein_pct', pct=True)}（晚）
  - 骨量：{scale_val(sm, 'bone_mass_kg')} kg（晨）/ {scale_val(se, 'bone_mass_kg')} kg（晚）
"""
    if gar and resting_hr != "?":
        report += f"  - 静息心率: {resting_hr} bpm\n"
    if gar and avg_stress != "?":
        report += f"  - 压力得分: {avg_stress}\n"
    if gar:
        report += f"  - BMR: {bmr} kcal\n"

    report += f"""
## 😴 睡眠情况
{sleep_md}## 🔥 热量情况
  - 总摄入: ~{total_in} kcal
  - 总消耗: {total_cal_str} kcal
  - 缺口: {deficit} kcal（{deficit_sign}）

### 🍽️ 昨日摄入
  - 早餐：{bm_cal} kcal · {meal_desc(bm)}
  - 午餐：{lu_cal} kcal · {meal_desc(lu)}
  - 晚餐：{di_cal} kcal · {meal_desc(di)}
  - 零食：-

### 💪 消耗情况
"""
    if gar:
        report += f"""  - 步数: {steps:,}步
  - 活动消耗: {active_cal} kcal
  - 全天消耗: {total_cal} kcal
"""
    else:
        report += "  Garmin 数据缺失\n"

    report += "\n---\n*数据来源：有品智能秤 + 用户记录 + Garmin Connect*\n"

    outpath = f"{REPORTS}/{DATE}.md"
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {outpath}")
