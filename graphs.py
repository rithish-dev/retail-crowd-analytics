import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def save_hourly_graph():

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"people_log_{today}.csv"

    try:
        df = pd.read_csv(filename)

    except:
        return

    if len(df) == 0:
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["hour"] = df["timestamp"].dt.hour

    
    

   # Keep only rows where a NEW visitor entered
    df["new_visit"] = df["entered"].diff().fillna(df["entered"])

    entries = df[df["new_visit"] > 0]

    hourly = entries.groupby("hour").size()



    hours = list(range(24))

    counts = [hourly.get(h, 0) for h in hours]

    plt.figure(figsize=(10,4))

    plt.bar(hours, counts)

    plt.xticks(hours)

    plt.xlabel("Hour")

    plt.ylabel("Visitors")

    plt.title("Hourly Visitors")

    plt.tight_layout()

    plt.savefig("static/hourly_visitors.png")

    plt.close()