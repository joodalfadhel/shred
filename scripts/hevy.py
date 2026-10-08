import os

import pandas as pd
import requests
from dotenv import load_dotenv

OUT = "data/hevy.csv"     # where the data is saved

load_dotenv()
API_KEY = os.getenv("HEVY_API_KEY")
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")   # falls back to Eastern if not set

# 1. get every workout, page by page, until hit the last page
workouts = []
page = 1

while True:
    response = requests.get(
        "https://api.hevyapp.com/v1/workouts",
        headers={"api-key": API_KEY},
        params={"page": page, "pageSize": 10},
    )
    response.raise_for_status()      # stop with a clear error if the key is wrong
    data = response.json()
    workouts = workouts + data["workouts"]

    if page >= data["page_count"]:
        break
    page += 1

print(f"got {len(workouts)} workouts")

# 2. flatten: one row per set
rows = []

for workout in workouts:
    for exercise in workout["exercises"]:
        for s in exercise["sets"]:
            rows.append({
                "date": workout["start_time"],
                "start_time": workout["start_time"],
                "end_time": workout["end_time"],
                "workout": workout["title"],
                "exercise": exercise["title"],
                "weight_kg": s["weight_kg"],
                "reps": s["reps"],
            })

df = pd.DataFrame(rows)

# 3. clean
# workout length in minutes = end time - start time
df["duration_min"] = (
    pd.to_datetime(df["end_time"]) - pd.to_datetime(df["start_time"])
).dt.total_seconds() / 60

# kg → lbs (Hevy always stores kg, even if the app shows lbs)
df["weight_lbs"] = (df["weight_kg"] * 2.20462).round(1)

# UTC → your time zone, then keep just the day
df["date"] = pd.to_datetime(df["date"]).dt.tz_convert(TIMEZONE).dt.date

# 4. save
os.makedirs("data", exist_ok=True)
df.to_csv(OUT, index=False)
print(f"saved {len(df)} sets → {OUT}")