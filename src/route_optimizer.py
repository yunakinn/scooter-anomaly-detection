import math

LOCATION_COORDS = {
    "정문 앞": (0, 0),
    "학술정보관 앞": (120, 90),
    "제1공학관 앞": (200, 60),
    "제2공학관 앞": (240, 130),
    "학생복지관 앞": (80, 150),
    "기숙사 앞": (310, 40),
    "컨퍼런스홀 앞": (170, 200),
    "체육관 앞": (280, 190),
    "셔틀콕 앞": (60, 80),
}


def get_priority_list(events: list) -> list:
    valid = [
        e for e in events
        if e.get("location") in LOCATION_COORDS
        and e.get("prediction") == "abnormal"
    ]

    return sorted(
        valid,
        key=lambda x: x.get("violation_score", 0),
        reverse=True
    )


def optimize_route(priority_list: list, start: tuple = (0, 0)) -> list:
    if not priority_list:
        return []

    def dist(a: tuple, b: tuple) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    high_priority = [
        e for e in priority_list
        if e.get("violation_score", 0) >= 80
    ]

    others = [
        e for e in priority_list
        if e.get("violation_score", 0) < 80
    ]

    route = []
    current = start

    for item in sorted(high_priority, key=lambda x: x.get("violation_score", 0), reverse=True):
        coords = LOCATION_COORDS[item["location"]]
        route.append({
            **item,
            "distance_from_prev": round(dist(current, coords), 1)
        })
        current = coords

    remaining = list(others)

    while remaining:
        remaining.sort(key=lambda x: dist(current, LOCATION_COORDS[x["location"]]))
        nearest = remaining.pop(0)
        coords = LOCATION_COORDS[nearest["location"]]

        route.append({
            **nearest,
            "distance_from_prev": round(dist(current, coords), 1)
        })

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
        {"location": "정문 앞", "prediction": "normal", "violation_score": 0.0, "level": "정상 ⚪", "action": "정상 주차 가능성 높음"}
    ]

    priority = get_priority_list(mock_events)
    route = optimize_route(priority)
    print(f"총 이동 거리: {get_total_distance(route)} m")
    for item in route:
        print(item)
