import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("HEVY_API_KEY")

workouts = []

for page in range(1, 15):
    response = requests.get(
        "https://api.hevyapp.com/v1/workouts",
        headers={"api-key": API_KEY},
        params={"page": page, "pageSize": 10},
    )
    data = response.json()
    workouts = workouts + data["workouts"]

print(len(workouts))

import pandas as pd

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

# workout length in minutes = end time - start time
df["duration_min"] = (
    pd.to_datetime(df["end_time"]) - pd.to_datetime(df["start_time"])
).dt.total_seconds() / 60

print(df.head(10))

df["weight_lbs"] = (df["weight_kg"] * 2.2).round(1)

df["date"] = pd.to_datetime(df["date"]).dt.tz_convert("America/New_York").dt.date

df.to_csv("data/hevy.csv", index=False)
print("saved")