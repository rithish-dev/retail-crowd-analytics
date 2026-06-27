import csv
import os


def get_latest_summary():

    if not os.path.exists("daily_summary.csv"):
        return None

    with open("daily_summary.csv", "r") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return None

    data = rows[-1]

    peak = data.get("peak_hour", "")
    if peak.isdigit():
        hour = int(peak)
    else:
        hour = None

    if hour is None:
        data["peak_hour"] = "N/A"
    else:
        suffix = "AM" if hour < 12 else "PM"
        display = hour % 12
        if display == 0:
            display = 12

        data["peak_hour"] = f"{display} {suffix}"

    return data

