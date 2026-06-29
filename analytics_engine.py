from statistics import mean

def calculate_metrics(people, enter_count, current_occupancy):
    dwell = []

    for p in people.values():
        if p["total_time"] > 0:
            dwell.append(p["total_time"])

    avg_dwell = mean(dwell) if dwell else 0
    max_dwell = max(dwell) if dwell else 0

    occupancy_score = min(current_occupancy / 20, 1.0) * 40
    dwell_score = min(avg_dwell / 60, 1.0) * 30
    flow_score = min(enter_count / 100, 1.0) * 30

    risk = round(
        occupancy_score +
        dwell_score +
        flow_score,
        1
    )

    return {
        "avg_dwell": avg_dwell,
        "max_dwell": max_dwell,
        "risk": risk
    }