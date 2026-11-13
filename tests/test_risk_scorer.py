import math

import pytest

from src.event_system import create_detection_event
from src.risk_scorer import RiskScorer
from src.route_optimizer import get_priority_list


INVALID = [float("nan"), float("inf"), float("-inf"), None, "invalid", -0.1, 1.1, 10**400]


@pytest.mark.parametrize("confidence", INVALID)
@pytest.mark.parametrize("source", ["summary", "detection"])
def test_invalid_confidence_stays_indeterminate_through_event_creation(confidence, source):
    kwargs = {"abnormal_confidence": confidence} if source == "summary" else {
        "abnormal_confidence": .9,
        "detections": [{"label": "abnormal", "confidence": confidence}],
    }
    result = RiskScorer().score(prediction="abnormal", **kwargs)
    assert result["level"] == "판단 불가"
    assert result["risk_score"] == result["violation_score"] == 0
    assert math.isfinite(result["abnormal_confidence"])
    event = create_detection_event("photo.jpg", "본관 앞",
                                   detection_result={"prediction": "abnormal"}, score_result=result)
    assert get_priority_list([event]) == []


@pytest.mark.parametrize("confidence,score,level", [
    (0, 0, "정상 ⚪"), (.3, 30, "낮음 🟢"), (.5, 50, "높음 🟡"),
    (.8, 80, "매우 높음 🔴"), (1, 100, "매우 높음 🔴"), ("0.9", 90, "매우 높음 🔴"),
])
def test_valid_confidence_thresholds_are_preserved(confidence, score, level):
    result = RiskScorer().score(prediction="abnormal", abnormal_confidence=confidence)
    assert (result["risk_score"], result["level"]) == (score, level)


def test_valid_detection_maximum_and_legacy_class_name_are_preserved():
    result = RiskScorer().score(prediction="abnormal", abnormal_confidence=.5, detections=[
        {"label": "abnormal", "confidence": .7},
        {"class_name": "abnormal", "confidence": .9},
        {"label": "normal", "confidence": 1},
    ])
    assert result["risk_score"] == 90
