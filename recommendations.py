def get_recommendation(data):

    recommendations = []

    visitors = data["visitors"]
    occupancy = data["occupancy"]
    dwell = data["avg_dwell"]
    risk = data["risk_score"]

    if visitors < 20:
        recommendations.append(
            "🔵 Foot traffic is low. Consider running promotions."
        )

    if occupancy >= 5:
        recommendations.append(
            "🟠 Store occupancy is increasing. Monitor checkout queues."
        )

    if dwell > 120:
        recommendations.append(
            "🟠 Customers are spending a long time inside. Check for bottlenecks."
        )

    if risk >= 70:
        recommendations.append(
            "🔴 High congestion risk detected."
        )

    if not recommendations:
        recommendations.append(
            "🟢 Store operations look healthy."
        )

    return recommendations