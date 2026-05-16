#!/usr/bin/env python3
"""
Fetch Garmin data for a date, accounting for GMT+8 timezone.
For sleep, the night sleep is stored under the PREVIOUS calendar date in GMT.
So we need to check both date and date-1 for sleep.
"""
import subprocess
import json
import os
from datetime import datetime, timedelta

WORKSPACE = os.path.expanduser("~/.openclaw/workspace-jirou/memory/pending")
TIMEZONE_OFFSET_HOURS = 8  # GMT+8

def gccli(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    try:
        return json.loads(result.stdout)
    except:
        return {"error": "parse error", "raw": result.stdout[:200]}

def date_minus_one(date_str):
    """Subtract one day from YYYY-MM-DD"""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return (d - timedelta(days=1)).strftime("%Y-%m-%d")

dates = ["2026-04-13", "2026-04-14"]

for date in dates:
    print(f"\n=== Fetching {date} ===")
    
    # Activities (may span midnight, but we query the target date)
    acts = gccli(f"gccli activities search --start-date {date} --end-date {date} --json")
    print(f"Activities: {len(acts) if isinstance(acts, list) else 'error'}")
    
    # Summary
    summary = gccli(f"gccli health summary {date} --json")
    if "error" not in summary:
        print(f"Summary OK - Steps: {summary.get('totalSteps','N/A')}, "
              f"ActiveCal: {summary.get('activeKilocalories','N/A')}, "
              f"TotalCal: {summary.get('totalKilocalories','N/A')}, "
              f"BMR: {summary.get('bmrKilocalories','N/A')}, "
              f"RestingHR: {summary.get('restingHeartRate','N/A')}")
    else:
        print(f"Summary ERROR: {summary.get('error')}")
    
    # Sleep: For GMT+8, night sleep (e.g. 10PM-7AM) starts at 14:00 GMT
    # So the "date" in Garmin's API is the LOCAL midnight date, which is GMT date - 1
    # E.g., night of April 13 local = April 12 in Garmin's stored date
    # Also query the same date for any daytime sleep/naps
    sleep_same_day = gccli(f"gccli health sleep {date} --json")
    sleep_prev_day = gccli(f"gccli health sleep {date_minus_one(date)} --json")
    
    def parse_sleep(dto):
        if not dto: return None
        total = dto.get("sleepTimeSeconds", 0)
        deep = dto.get("deepSleepSeconds", 0)
        light = dto.get("lightSleepSeconds", 0)
        rem = dto.get("remSleepSeconds", 0)
        awake = dto.get("awakeSleepSeconds", 0)
        if total > 0:
            return {
                "total_hours": round(total/3600, 1),
                "deep_hours": round(deep/3600, 1),
                "light_hours": round(light/3600, 1),
                "rem_hours": round(rem/3600, 1),
                "awake_min": round(awake/60),
                "avgSpO2": dto.get("averageSpO2Value"),
                "lowestSpO2": dto.get("lowestSpO2Value"),
                "startGMT": dto.get("sleepStartTimestampGMT"),
                "endGMT": dto.get("sleepEndTimestampGMT"),
            }
        return None
    
    dto_same = sleep_same_day.get("dailySleepDTO") if isinstance(sleep_same_day, dict) else None
    dto_prev = sleep_prev_day.get("dailySleepDTO") if isinstance(sleep_prev_day, dict) else None
    
    sleep_night = parse_sleep(dto_prev)  # Night sleep stored under prev date
    sleep_same = parse_sleep(dto_same)   # Same-day sleep (nap or same-night if timezone aligned)
    
    if sleep_night:
        print(f"Night sleep (from {date_minus_one(date)} record): {sleep_night['total_hours']}h total, "
              f"deep {sleep_night['deep_hours']}h, light {sleep_night['light_hours']}h, "
              f"REM {sleep_night['rem_hours']}h")
    if sleep_same:
        print(f"Same-day sleep (from {date} record): {sleep_same['total_hours']}h total")
    
    # Build combined sleep data - use the night sleep primarily
    combined_sleep = {
        "night_sleep": sleep_night,
        "same_day_sleep": sleep_same,
        "source_night_date": date_minus_one(date),
        "source_same_date": date,
    }
    
    out = {
        "date": date,
        "activities": acts,
        "summary": summary,
        "sleep": combined_sleep,
        "sleep_raw_same_day": sleep_same_day,
        "sleep_raw_prev_day": sleep_prev_day,
    }
    
    outpath = os.path.join(WORKSPACE, f"Garmin-{date}.json")
    with open(outpath, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Saved to {outpath}")
