#!/usr/bin/env python3
import subprocess
import json
import os

WORKSPACE = os.path.expanduser("~/.openclaw/workspace-jirou/memory/pending")

def gccli(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    try:
        return json.loads(result.stdout)
    except:
        return {"error": "parse error", "raw": result.stdout[:500]}

dates = ["2026-04-13", "2026-04-14"]

for date in dates:
    print(f"\n=== Fetching {date} ===")
    
    # Activities search (returns list)
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
    
    # Sleep
    sleep = gccli(f"gccli health sleep {date} --json")
    if "error" not in sleep:
        total_sleep = sleep.get("totalSleepSeconds", 0)
        deep = sleep.get("deepSleepSeconds", 0)
        light = sleep.get("lightSleepSeconds", 0)
        rem = sleep.get("remSleepSeconds", 0)
        awake = sleep.get("awakeSleepSeconds", 0)
        print(f"Sleep OK - Total: {total_sleep/3600:.1f}h, "
              f"Deep: {deep/3600:.1f}h, Light: {light/3600:.1f}h, "
              f"REM: {rem/3600:.1f}h, Awake: {awake/60:.0f}m, "
              f"AvgSpO2: {sleep.get('averageSpO2Value','N/A')}")
    
    out = {
        "date": date,
        "activities": acts,
        "summary": summary,
        "sleep": sleep
    }
    
    outpath = os.path.join(WORKSPACE, f"Garmin-{date}.json")
    with open(outpath, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Saved to {outpath}")
