import random
from datetime import datetime


LOCATIONS = [
    "정문 앞",
    "셔틀콕 앞",
    "학술정보관 앞",
    "학생복지관 앞",
    "호수공원 앞",
    "본관 앞",
    "컨퍼런스홀 앞",
    "체육관 앞",
    "기숙사 앞",
    "경상관 앞",
    "글로벌문화통상관 앞",
    "언론정보관 앞",
    "제1과학기술관 앞",
    "제2과학기술관 앞",
    "제1학술관 앞",
    "융합교육관 앞",
    "약학대학 앞",
    "제1공학관 앞",
    "제2공학관 앞",
    "제3공학관 앞",
    "제4공학관 앞",
    "제5공학관 앞",
    "디자인교육관 앞",
    "예체능대학 앞",
    "학연산 클러스터 앞",
    "카카오데이터센터 앞",
]


event_log = []


def get_next_event_id(existing_events=None):
    ids = []

    for event in event_log:
        event_id = event.get("event_id")
        if isinstance(event_id, int):
            ids.append(event_id)

    if existing_events:
        for event in existing_events:
            event_id = event.get("event_id")
            if isinstance(event_id, int):
                ids.append(event_id)

    return max(ids) + 1 if ids else 1


def create_detection_event(
    image_path,
    location=None,
    source="image",
    detection_result=None,
    score_result=None,
    existing_events=None
):
    event = {
        "event_id": get_next_event_id(existing_events),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": location if location else random.choice(LOCATIONS),
        "image_path": str(image_path),
        "source": source,
        "prediction": "none",
        "confidence": 0.0,
        "abnormal_confidence": 0.0,
        "risk_score": 0.0,
        "violation_score": 0.0,
        "level": "정상 ⚪",
        "action": "정상 주차 가능성 높음",
        "detections": []
    }

    if detection_result:
        event.update({
            "prediction": detection_result.get("prediction", "none"),
            "confidence": float(detection_result.get("confidence", 0.0) or 0.0),
            "abnormal_confidence": float(detection_result.get("abnormal_confidence", 0.0) or 0.0),
            "detections": detection_result.get("detections", [])
        })

    if score_result:
        score = float(
            score_result.get(
                "risk_score",
                score_result.get("violation_score", 0.0)
            ) or 0.0
        )

        event.update(score_result)
        event["risk_score"] = score
        event["violation_score"] = score
        event["level"] = score_result.get("level", event["level"])
        event["action"] = score_result.get("action", event["action"])

    event_log.append(event)
    return event


def get_events():
    return event_log


def clear_events():
    event_log.clear()


if __name__ == "__main__":
    event = create_detection_event(
        image_path="data/demo_images/abnormal/sample.jpg",
        location="학술정보관 앞",
        source="demo_image"
    )
    print(event)