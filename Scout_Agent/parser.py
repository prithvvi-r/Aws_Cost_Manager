

def parse_cost_response(response):
    costs = {}

    for time_bucket in response.get("ResultsByTime", []):
        for group in time_bucket.get("Groups", []):
            service, region = group["Keys"]

            amount = float(
                group["Metrics"]["UnblendedCost"]["Amount"]
            )

            key = (service, region)
            costs[key] = costs.get(key, 0.0) + amount

    return costs