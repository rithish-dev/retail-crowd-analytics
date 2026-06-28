from live_data import live_metrics


def get_latest_summary():
    return {
        "total_visits": live_metrics["visitors"],
        "current_occupancy": live_metrics["occupancy"],
        "peak_hour": live_metrics["peak_hour"],
        "avg_dwell": round(live_metrics["avg_dwell"], 1),
        "risk_score": round(live_metrics["risk_score"], 2),
    }