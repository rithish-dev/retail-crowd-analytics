import os
import matplotlib.pyplot as plt


def save_hourly_graph(hour_counts):

    os.makedirs("reports", exist_ok=True)

    hours = list(range(24))
    values = [hour_counts.get(h, 0) for h in hours]

    plt.figure(figsize=(10,4))

    plt.bar(hours, values)

    plt.title("Hourly Visitors")
    plt.xlabel("Hour")
    plt.ylabel("Visitors")

    plt.xticks(hours)

    plt.tight_layout()

    plt.savefig("reports/hourly_visitors.png")

    plt.close()