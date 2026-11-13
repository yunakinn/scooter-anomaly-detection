from contextlib import nullcontext

from dashboard import admin_tab
from src.route_optimizer import get_priority_list, optimize_route


def test_rendered_pickup_count_matches_route_eligibility(monkeypatch):
    def report(event_id, **values):
        return {"event_id": event_id, "prediction": "abnormal", "risk_score": 80,
                "location": "본관 앞", "status": "확인 대기", **values}

    events = [
        report(1, location="본관 앞", risk_score=50),
        report(2, location="정문 앞"),
        report(3, location="unknown"),
        report(4, location="본관 앞", status="처리 완료"),
        report(5, location="본관 앞", prediction="normal"),
        report(6, location="본관 앞", risk_score=49.9),
        report(7, location="본관 앞", risk_score=float("inf")),
        report(8, location="본관 앞", risk_score=float("nan")),
    ]
    cards = {}
    monkeypatch.setattr(admin_tab.st, "columns", lambda count: [nullcontext() for _ in range(count)])
    monkeypatch.setattr(admin_tab, "render_kpi_card", lambda label, value, caption: cards.update({label: value}))
    admin_tab.render_kpi(events)
    assert cards["수거 대상"] == len(get_priority_list(events)) == len(optimize_route(events)) == 2
    assert cards["전체 신고"] == 8
    assert cards["처리 완료"] == 1
