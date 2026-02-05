
def detect_spikes(current, previous, pct_threshold=30, abs_threshold=1000):
    suspects = []

    for key, current_cost in current.items():
        prev_cost = previous.get(key, 0.0)

        # Avoid noise
        if prev_cost == 0:
            continue

        change_pct = ((current_cost - prev_cost) / prev_cost) * 100

        if change_pct > pct_threshold or current_cost > abs_threshold:
            service, region = key

            suspects.append({
                "service": service,
                "region": region,
                "current_cost": round(current_cost, 2),
                "previous_cost": round(prev_cost, 2),
                "change_pct": round(change_pct, 2),
                "time_window": "last_14_days"
            })

    return suspects


