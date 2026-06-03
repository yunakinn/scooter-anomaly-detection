import math

LOCATION_COORDS = {
    "정문 앞":        (37.2985, 126.8385),
    "학술정보관 앞":  (37.2993, 126.8398),
    "제1공학관 앞":   (37.2999, 126.8412),
    "제2공학관 앞":   (37.3002, 126.8420),
    "학생복지관 앞":  (37.2990, 126.8405),
    "기숙사 앞":      (37.3010, 126.8430),
    "컨퍼런스홀 앞":  (37.2997, 126.8415),
    "체육관 앞":      (37.3005, 126.8425),
    "셔틀콕 앞":      (37.2988, 126.8392),
}


def get_priority_list(events: list) -> list:
    valid = [
        e for e in events
        if e.get("location") in LOCATION_COORDS
        and e.get("prediction") == "abnormal"
    ]
    return sorted(valid, key=lambda x: x.get("violation_score", 0), reverse=True)


def optimize_route(priority_list: list, start: tuple = (37.2985, 126.8385)) -> list:
    if not priority_list:
        return []

    def dist(a, b):
        lat1, lon1 = a
        lat2, lon2 = b
        dlat = (lat2 - lat1) * 111000
        dlon = (lon2 - lon1) * 88000
        return math.sqrt(dlat**2 + dlon**2)

    high_priority = [e for e in priority_list if e.get("violation_score", 0) >= 80]
    others = [e for e in priority_list if e.get("violation_score", 0) < 80]

    route = []
    current = start

    for item in sorted(high_priority, key=lambda x: x.get("violation_score", 0), reverse=True):
        coords = LOCATION_COORDS[item["location"]]
        route.append({**item, "distance_from_prev": round(dist(current, coords), 1)})
        current = coords

    remaining = list(others)
    while remaining:
        remaining.sort(key=lambda x: dist(current, LOCATION_COORDS[x["location"]]))
        nearest = remaining.pop(0)
        coords = LOCATION_COORDS[nearest["location"]]
        route.append({**nearest, "distance_from_prev": round(dist(current, coords), 1)})
        current = coords

    for i, item in enumerate(route):
        item["visit_order"] = i + 1

    return route


def get_total_distance(route: list) -> float:
    return round(sum(item.get("distance_from_prev", 0) for item in route), 1)


if __name__ == "__main__":
    mock_events = [
        {"location": "학술정보관 앞", "prediction": "abnormal", "violation_score": 92.0, "level": "매우 높음 🔴", "action": "우선 단속/수거"},
        {"location": "기숙사 앞", "prediction": "abnormal", "violation_score": 86.0, "level": "매우 높음 🔴", "action": "우선 단속/수거"},
        {"location": "학생복지관 앞", "prediction": "abnormal", "violation_score": 63.0, "level": "높음 🟡", "action": "현장 확인 필요"},
    ]
    priority = get_priority_list(mock_events)
    route = optimize_route(priority)
    print(f"총 이동 거리: {get_total_distance(route)} m")
    for item in route:
        print(f"[{item['visit_order']}] {item['location']} → {item['level']} ({item['distance_from_prev']}m)")