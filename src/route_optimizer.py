import math
from itertools import permutations


LOCATION_COORDS = {
    "정문 앞": (37.300111, 126.837517),
    "셔틀콕 앞": (37.298777, 126.837896),
    "학술정보관 앞": (37.296945, 126.843523),
    "학생복지관 앞": (37.304842, 126.829274),
    "호수공원 앞": (37.297345, 126.833943),
    "본관 앞": (37.299519, 126.833379),
    "컨퍼런스홀 앞": (37.304192, 126.840394),
    "체육관 앞": (37.296161, 126.833417),
    "기숙사 앞": (37.294532, 126.835934),
    "경상관 앞": (37.300023, 126.836109),
    "글로벌문화통상관 앞": (37.299674, 126.835358),
    "언론정보관 앞": (37.300347, 126.834881),
    "제1과학기술관 앞": (37.299614, 126.836012),
    "제2과학기술관 앞": (37.298809, 126.837326),
    "제1학술관 앞": (37.298416, 126.835964),
    "융합교육관 앞": (37.296001, 126.838167),
    "약학대학 앞": (37.296426, 126.838565),
    "제1공학관 앞": (37.297712, 126.837485),
    "제2공학관 앞": (37.297321, 126.832706),
    "제3공학관 앞": (37.297524, 126.836357),
    "제4공학관 앞": (37.297635, 126.837255),
    "제5공학관 앞": (37.297440, 126.837220),
    "디자인교육관 앞": (37.297542, 126.831048),
    "예체능대학 앞": (37.296102, 126.833903),
    "학연산 클러스터 앞": (37.296575, 126.838448),
    "카카오데이터센터 앞": (37.293721, 126.830899),
}


START_LOCATION = "본관 앞"
PICKUP_SCORE_THRESHOLD = 50


def get_score(event):
    try:
        score = float(event.get("risk_score", event.get("violation_score", 0)) or 0)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    # Invalid confidence-derived scores must never become pickup candidates.
    return score if math.isfinite(score) and 0 <= score <= 100 else 0.0


def distance_meters(a, b):
    lat1, lon1 = a
    lat2, lon2 = b

    dlat = (lat2 - lat1) * 111000
    dlon = (lon2 - lon1) * 88000

    return math.sqrt(dlat ** 2 + dlon ** 2)


def normalize_event(event):
    item = dict(event)
    score = get_score(item)

    item["risk_score"] = score
    item["violation_score"] = score

    return item


def get_priority_list(events: list) -> list:
    valid = []

    for event in events:
        item = normalize_event(event)
        score = get_score(item)

        if item.get("location") not in LOCATION_COORDS:
            continue

        if item.get("prediction") != "abnormal":
            continue

        if item.get("status") == "처리 완료":
            continue

        if score < PICKUP_SCORE_THRESHOLD:
            continue

        valid.append(item)

    return sorted(
        valid,
        key=lambda x: get_score(x),
        reverse=True
    )


def calculate_route_distance(order, start_coords):
    total = 0.0
    current = start_coords

    for item in order:
        coords = LOCATION_COORDS[item["location"]]
        total += distance_meters(current, coords)
        current = coords

    return total


def find_shortest_order(items, start_coords):
    if len(items) <= 1:
        return items

    if len(items) <= 8:
        best_order = None
        best_distance = float("inf")

        for order in permutations(items):
            total_distance = calculate_route_distance(order, start_coords)

            if total_distance < best_distance:
                best_distance = total_distance
                best_order = list(order)

        return best_order

    return find_nearest_order(items, start_coords)


def find_nearest_order(items, start_coords):
    remaining = list(items)
    route = []
    current = start_coords

    while remaining:
        remaining.sort(
            key=lambda x: distance_meters(
                current,
                LOCATION_COORDS[x["location"]]
            )
        )

        nearest = remaining.pop(0)
        route.append(nearest)
        current = LOCATION_COORDS[nearest["location"]]

    return route


def optimize_route(priority_list: list, start: tuple = None) -> list:
    if not priority_list:
        return []

    # Keep eligibility consistent even when called outside the dashboard.
    remaining = get_priority_list(priority_list)

    if not remaining:
        return []

    start_coords = LOCATION_COORDS[START_LOCATION] if start is None else start
    try:
        lat, lon = (float(value) for value in start_coords)
        if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("start must contain a finite latitude and longitude in valid ranges") from exc
    start_coords = (lat, lon)

    ordered_items = find_shortest_order(remaining, start_coords)

    route = []
    current = start_coords

    for i, item in enumerate(ordered_items):
        coords = LOCATION_COORDS[item["location"]]

        routed_item = dict(item)
        routed_item["visit_order"] = i + 1
        routed_item["distance_from_prev"] = round(distance_meters(current, coords), 1)

        route.append(routed_item)
        current = coords

    return route


def get_total_distance(route: list) -> float:
    return round(
        sum(float(item.get("distance_from_prev", 0) or 0) for item in route),
        1
    )
