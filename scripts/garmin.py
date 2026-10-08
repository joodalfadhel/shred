import os
import time
from datetime import date, timedelta

import pandas as pd
from dotenv import load_dotenv
from garminconnect import Garmin

OUT = "data/garmin.csv"     # where the data is saved

load_dotenv()

# first day to pull, read from .env (falls back to 2025-01-01 if not set)
START = date.fromisoformat(os.getenv("GARMIN_START_DATE", "2025-01-01"))

# log in (first time uses email + password, then saves a token)
client = Garmin(
    os.getenv("GARMIN_EMAIL"),
    os.getenv("GARMIN_PASSWORD"),
    prompt_mfa=lambda: input("MFA code: "),
)
client.login("~/.garminconnect")

# if we already have data, only pull days since the last saved date
if os.path.exists(OUT):
    old = pd.read_csv(OUT)
    last = date.fromisoformat(old["date"].max())
    days_back = (date.today() - last).days    # re-pulls the last day too, just in case
    print(f"last saved day: {last} → pulling {days_back} days")
else:
    old = pd.DataFrame()
    days_back = (date.today() - START).days
    print(f"no saved data → pulling {days_back} days since {START}")

rows = []

# go back one day at a time
for i in range(1, days_back + 1):
    day = (date.today() - timedelta(days=i)).isoformat()

    try:
        # daily stats: steps, resting HR, stress, body battery
        s = client.get_stats(day)

        # sleep data (also includes HRV)
        sl = client.get_sleep_data(day)
        d = sl.get("dailySleepDTO") or {}
        scores = d.get("sleepScores") or {}

        rows.append({
            "date": s["calendarDate"],

            # daily stats
            "steps": s["totalSteps"],
            "resting_hr": s["restingHeartRate"],
            "stress_avg": s["averageStressLevel"],
            "body_battery_wake": s["bodyBatteryAtWakeTime"],
            "body_battery_high": s["bodyBatteryHighestValue"],
            "body_battery_low": s["bodyBatteryLowestValue"],
            "active_cal": s["activeKilocalories"],

            # sleep (the night before this date, Garmin files it under the day you woke up)
            "sleep_score": (scores.get("overall") or {}).get("value"),
            "sleep_hours": round((d.get("sleepTimeSeconds") or 0) / 3600, 1),
            "deep_hours": round((d.get("deepSleepSeconds") or 0) / 3600, 1),
            "rem_hours": round((d.get("remSleepSeconds") or 0) / 3600, 1),
            "awake_count": d.get("awakeCount"),

            # recovery
            "hrv": sl.get("avgOvernightHrv"),
            "hrv_status": sl.get("hrvStatus"),
            "battery_recharge": sl.get("bodyBatteryChange"),
        })
        print("got", day)
    except Exception as e:
        print("skipped", day, e)

    # wait 1 second between days so Garmin doesn't block us
    time.sleep(1)

# combine old + new, keep the newest version of any repeated day, sort by date
new = pd.DataFrame(rows)
df = (
    pd.concat([old, new])
      .drop_duplicates(subset="date", keep="last")
      .sort_values("date")
)

df.to_csv(OUT, index=False)
print(f"added {len(new)} days → {len(df)} total")