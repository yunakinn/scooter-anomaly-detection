from copy import deepcopy

import pytest

from src import route_optimizer as routes


def event(location="본관 앞", score=75, **overrides):
    return {"location": location, "risk_score": score, "prediction": "abnormal", **overrides}


@pytest.mark.parametrize("score,eligible", [(49.9, False), (50, True), (100, True), ("75", True)])
def test_pickup_score_boundary(score, eligible):
    assert bool(routes.get_priority_list([event(score=score)])) is eligible


@pytest.mark.parametrize("score", [None, "invalid", float("nan"), float("inf"), float("-inf"), -1, 101, 10**400])
def test_invalid_scores_cannot_enter_a_route(score):
    assert routes.optimize_route([event(score=score)]) == []


@pytest.mark.parametrize("overrides", [
    {"location": "unknown"}, {"prediction": "normal"},
    {"prediction": "none"}, {"status": "처리 완료"},
])
def test_ineligible_reports_cannot_enter_a_route(overrides):
    assert routes.optimize_route([event(**overrides)]) == []


def test_priority_is_descending_and_legacy_scores_are_supported():
    legacy = {"location": "본관 앞", "violation_score": "80", "prediction": "abnormal"}
    selected = routes.get_priority_list([event(score=50), legacy, event(score=95)])
    assert [e["risk_score"] for e in selected] == [95, 80, 50]
    assert all(e["risk_score"] == e["violation_score"] for e in selected)


def test_shortest_open_path_and_distances_do_not_follow_score_order(monkeypatch):
    monkeypatch.setattr(routes, "LOCATION_COORDS", {"near": (0, .001), "far": (0, .003), "middle": (0, .002)})
    events = [event("far", 95), event("near", 50), event("middle", 80)]
    original = deepcopy(events)
    result = routes.optimize_route(events, start=(0, 0))
    assert [e["location"] for e in result] == ["near", "middle", "far"]
    assert [e["visit_order"] for e in result] == [1, 2, 3]
    assert [e["distance_from_prev"] for e in result] == [88, 88, 88]
    assert routes.get_total_distance(result) == 264  # No return trip.
    assert events == original


@pytest.mark.parametrize("count", [8, 9])
def test_exact_search_and_heuristic_boundary(monkeypatch, count):
    monkeypatch.setattr(routes, "LOCATION_COORDS", {str(i): (0, .001 * i) for i in range(count)})
    events = [event(str(i)) for i in reversed(range(count))]
    heuristic_calls = []
    original = routes.find_nearest_order

    def tracked(items, start):
        heuristic_calls.append(len(items))
        return original(items, start)

    monkeypatch.setattr(routes, "find_nearest_order", tracked)
    result = routes.optimize_route(events, start=(0, 0))
    assert [e["location"] for e in result] == [str(i) for i in range(count)]
    assert heuristic_calls == ([] if count == 8 else [9])
    assert routes.get_total_distance(result) == 88 * (count - 1)


@pytest.mark.parametrize("start", [(float("nan"), 0), (0, float("inf")), (91, 0), (0, 181), (0,), "bad"])
def test_invalid_start_fails_with_clear_error(start):
    with pytest.raises(ValueError, match="latitude and longitude"):
        routes.optimize_route([event()], start=start)


def test_empty_route_and_zero_distance():
    assert routes.optimize_route([]) == []
    assert routes.get_total_distance([]) == 0
    result = routes.optimize_route([event()])
    assert result[0]["distance_from_prev"] == 0
    assert routes.get_total_distance(result) == 0
