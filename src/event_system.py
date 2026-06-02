import random
from datetime import datetime

LOCATIONS = [
    "정문 앞",
    "학술정보관 앞",
    "제1공학관 앞",
    "제2공학관 앞",
    "학생복지관 앞",
    "기숙사 앞",
    "컨퍼런스홀 앞",
    "체육관 앞",
    "셔틀콕 앞",
]

event_log = []


def create_detection_event(
    image_path,
    location=None,
    source="image",
    detection_result=None,
    score_result=None
):
    event = {
        "event_id": len(event_log) + 1,
        "timestamp": str(datetime.now()),
        "location": location if location else random.choice(LOCATIONS),
        "image_path": str(image_path),
        "source": source
    }

    if detection_result:
        event.update({
            "prediction": detection_result.get("prediction", "none"),
            "confidence": detection_result.get("confidence", 0.0),
            "abnormal_confidence": detection_result.get("abnormal_confidence", 0.0),
            "detections": detection_result.get("detections", [])
        })

    if score_result:
        event.update(score_result)

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
