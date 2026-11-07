from src.event_system import create_detection_event
from src.risk_scorer import RiskScorer
from src.report_state import report_key, is_duplicate_report
from src.route_optimizer import get_priority_list


def test_no_detection_is_not_normal():
    result = RiskScorer().score(prediction="none", abnormal_confidence=0, detections=[])
    assert result["level"] == "판단 불가"
    event = create_detection_event("photo.jpg", "본관 앞", detection_result={"prediction": "none"}, score_result=result)
    assert event["level"] == "판단 불가"
    assert get_priority_list([event]) == []


def test_event_ids_are_scoped_to_explicit_session_history():
    first = create_detection_event("a.jpg")
    second = create_detection_event("b.jpg", existing_events=[first])
    separate_session = create_detection_event("c.jpg")
    assert (first["event_id"], second["event_id"], separate_session["event_id"]) == (1, 2, 1)
    assert first["location"] == "미지정"


def test_same_photo_and_location_are_deduplicated():
    key = report_key("imagehash", "본관 앞")
    submitted = {key}
    assert is_duplicate_report(key, submitted)
    assert not is_duplicate_report(report_key("imagehash", "정문 앞"), submitted)
    assert not is_duplicate_report(None, submitted)


def test_normal_and_abnormal_results_still_score():
    scorer = RiskScorer()
    assert scorer.score(prediction="normal")["level"] == "정상 ⚪"
    assert scorer.score(prediction="abnormal", abnormal_confidence=.9)["risk_score"] == 90
