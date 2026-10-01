import os
from datetime import date, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

# log in (first time uses email + password, then saves a token so you don't have to again)
client = Garmin(
    os.getenv("GARMIN_EMAIL"),
    os.getenv("GARMIN_PASSWORD"),
    prompt_mfa=lambda: input("MFA code: "),
)
client.login("~/.garminconnect")
import time
import pandas as pd

rows = []

# go back 180 days, one day at a time
for i in range(1, 181):
    day = (date.today() - timedelta(days=i)).isoformat()

    try:
        s = client.get_stats(day)
        rows.append({
            "date": s["calendarDate"],
            "steps": s["totalSteps"],
            "resting_hr": s["restingHeartRate"],
            "stress_avg": s["averageStressLevel"],
            "body_battery_wake": s["bodyBatteryAtWakeTime"],
            "body_battery_high": s["bodyBatteryHighestValue"],
            "body_battery_low": s["bodyBatteryLowestValue"],
            "active_cal": s["activeKilocalories"],
            "sleep_hours": round((s["sleepingSeconds"] or 0) / 3600, 1),
        })
        print("got", day)
    except Exception as e:
        print("skipped", day, e)

    # wait 1 second between requests so Garmin doesn't block 
    time.sleep(1)

df = pd.DataFrame(rows)
df.to_csv("data/garmin.csv", index=False)
print(f"saved {len(df)} days")