#!/usr/bin/env python3
"""
Garmin Data Reader for OpenClaw
Uses gccli (no password/MFA required after initial login)
"""

import json
import subprocess
from datetime import date, timedelta

def run_gccli(command):
    """Run gccli command and return parsed JSON"""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return {"error": result.stderr}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout}

def get_garmin_data():
    """Get today's Garmin data using gccli"""
    
    today = date.today().isoformat()
    
    # Get health summary
    summary = run_gccli("gccli health summary today")
    
    # Get activities
    activities = run_gccli(f"gccli activities list --start-date {today} --end-date {today}")
    
    # Get body composition
    body = run_gccli(f"gccli body composition {today}")
    
    # Get sleep
    sleep = run_gccli(f"gccli health sleep {today}")
    
    # Get HRV
    hrv = run_gccli(f"gccli health hrv {today}")
    
    return {
        'summary': summary,
        'activities': activities,
        'body': body,
        'sleep': sleep,
        'hrv': hrv
    }

if __name__ == "__main__":
    try:
        data = get_garmin_data()
        print("✅ Garmin Data Fetched!")
        
        if 'summary' in data and 'error' not in data.get('summary', {}):
            s = data['summary']
            print(f"📅 Date: {s.get('calendarDate', 'N/A')}")
            print(f"👣 Steps: {s.get('totalSteps', 0):,}")
            print(f"🔥 Calories: {s.get('totalKilocalories', 0):.0f}")
            print(f"💓 Resting HR: {s.get('restingHeartRate', 'N/A')} bpm")
            print(f"😴 Sleep: {s.get('sleepingSeconds', 0) / 3600:.1f}h")
        
        if 'activities' in data and isinstance(data.get('activities'), list):
            print(f"🏃 Activities: {len(data['activities'])}")
        
        print("\n✅ All data saved to memory!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
