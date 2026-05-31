import math
from event_system import LOCATIONS

# 한양대 ERICA 캠퍼스 위치 좌표 (x, y) 단위: 미터 (수동 지정)
LOCATION_COORDS = {
    "정문 앞":        (0,   0),
    "학술정보관 앞":  (120, 90),
    "제1공학관 앞":   (200, 60),
    "제2공학관 앞":   (240, 130),
    "학생복지관 앞":  (80,  150),
    "기숙사 앞":      (310, 40),
    "컨퍼런스홀 앞":  (170, 200),
    "체육관 앞":      (280, 190),
    "셔틀콕 앞":      (60,  80),
}


def get_priority_list(scored_events: list) -> list:
    # 위치 좌표가 없는 항목은 제외
    valid = [e for e in scored_events if e.get("location") in LOCATION_COORDS]

    # risk_score 내림차순 정렬
    return sorted(valid, key=lambda x: x["risk_score"], reverse=True)


def optimize_route(priority_list: list, start: tuple = (0, 0)) -> list:
    if not priority_list:
        return []

    def dist(a: tuple, b: tuple) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    # 위험 🔴 vs 나머지 분리
    danger  = [e for e in priority_list if "위험" in e.get("level", "")]
    others  = [e for e in priority_list if "위험" not in e.get("level", "")]

    route   = []
    current = start

    # 1단계: 위험 지점 — risk_score 내림차순으로 무조건 먼저
    for item in sorted(danger, key=lambda x: x["risk_score"], reverse=True):
        coords = LOCATION_COORDS[item["location"]]
        route.append({**item, "distance_from_prev": round(dist(current, coords), 1)})
        current = coords

    # 2단계: 나머지 — Greedy Nearest-Neighbor
    remaining = list(others)
    while remaining:
        remaining.sort(key=lambda x: dist(current, LOCATION_COORDS[x["location"]]))
        nearest = remaining.pop(0)
        coords  = LOCATION_COORDS[nearest["location"]]
        route.append({**nearest, "distance_from_prev": round(dist(current, coords), 1)})
        current = coords

    # 방문 순서 번호 추가
    for i, item in enumerate(route):
        item["visit_order"] = i + 1

    return route


def get_total_distance(route: list) -> float:
    """최적 동선의 총 이동 거리 (미터) 반환"""
    return round(sum(item["distance_from_prev"] for item in route), 1)


# 테스트 실행
if __name__ == "__main__":
    mock_scored_events = [
        {"location": "정문 앞",       "risk_score": 25.0, "level": "낮음 🟢",  "action": "현장 확인 필요"},
        {"location": "학술정보관 앞", "risk_score": 82.5, "level": "위험 🔴",  "action": "즉시 수거 필요"},
        {"location": "제1공학관 앞",  "risk_score": 55.0, "level": "주의 🟡",  "action": "재배치 필요"},
        {"location": "기숙사 앞",     "risk_score": 91.0, "level": "위험 🔴",  "action": "즉시 수거 필요"},
        {"location": "체육관 앞",     "risk_score": 10.0, "level": "정상 ⚪",  "action": "정상 반납"},
        {"location": "학생복지관 앞", "risk_score": 63.0, "level": "주의 🟡",  "action": "재배치 필요"},
    ]

    priority = get_priority_list(mock_scored_events)
    route    = optimize_route(priority)
    total    = get_total_distance(route)

    print(f"총 이동 거리: {total} m\n")
    for item in route:
        print(
            f"[{item['visit_order']}] {item['location']:<15} "
            f"위험도: {item['risk_score']:5.1f}  "
            f"등급: {item['level']}  "
            f"이동: {item['distance_from_prev']}m  "
            f"조치: {item['action']}"
        )

"""
--- FOR TEST PURPOSES ONLY ---
from event_system import generate_mock_event
from risk_scorer  import RiskScorer

scorer = RiskScorer()
scored_events = []

for _ in range(9):
    event = generate_mock_event()
    result = scorer.score(
        detections=[],
        tilt_angle=event["tilt"],
        shock_detected=event["shock"]
    )
    scored_events.append({**event, **result})

priority = get_priority_list(scored_events)
route    = optimize_route(priority)
print("\n--- 실제 연동 테스트 ---")
print(f"총 이동 거리: {get_total_distance(route)} m")
for item in route:
    print(f"[{item['visit_order']}] {item['location']} → {item['level']}")
    """