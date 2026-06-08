import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def get_score(event):
    try:
        return float(event.get("risk_score", event.get("violation_score", 0)) or 0)
    except (TypeError, ValueError):
        return 0.0


def make_empty_figure(title):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": "표시할 데이터가 없습니다",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16}
            }
        ],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def plot_detection_ratio(events: list):
    if not events:
        return make_empty_figure("정상/불법 주정차 의심 비율")

    counts = {
        "정상": 0,
        "불법 주정차 의심": 0,
        "감지 실패": 0
    }

    for event in events:
        prediction = event.get("prediction", "none")

        if prediction == "normal":
            counts["정상"] += 1
        elif prediction == "abnormal":
            counts["불법 주정차 의심"] += 1
        else:
            counts["감지 실패"] += 1

    data = [
        {"분석 결과": key, "건수": value}
        for key, value in counts.items()
        if value > 0
    ]

    if not data:
        return make_empty_figure("정상/불법 주정차 의심 비율")

    df = pd.DataFrame(data)

    fig = px.pie(
        df,
        names="분석 결과",
        values="건수",
        title="정상/불법 주정차 의심 비율"
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        legend_title_text="분석 결과",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def plot_events_by_time(events: list):
    if not events:
        return make_empty_figure("시간대별 신고 수")

    timestamps = []

    for event in events:
        timestamp = event.get("timestamp")
        parsed = pd.to_datetime(timestamp, errors="coerce")

        if pd.notna(parsed):
            timestamps.append(parsed)

    if not timestamps:
        return make_empty_figure("시간대별 신고 수")

    df = pd.DataFrame({"timestamp": timestamps})
    df["시간대"] = df["timestamp"].dt.hour

    counts = (
        df["시간대"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    counts.columns = ["시간대", "신고 수"]

    fig = px.bar(
        counts,
        x="시간대",
        y="신고 수",
        title="시간대별 신고 수",
        labels={
            "시간대": "시간대",
            "신고 수": "신고 수"
        }
    )

    fig.update_layout(
        xaxis=dict(dtick=1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def plot_violation_distribution(events: list):
    scores = [
        get_score(event)
        for event in events
        if get_score(event) > 0
    ]

    if not scores:
        return make_empty_figure("위험도 점수 분포")

    fig = px.histogram(
        x=scores,
        title="위험도 점수 분포",
        labels={
            "x": "위험도 점수",
            "y": "건수"
        }
    )

    fig.update_traces(
        xbins=dict(start=0, end=100, size=10)
    )

    thresholds = [
        (30, "낮음 30점"),
        (50, "높음 50점"),
        (80, "매우 높음 80점")
    ]

    for value, label in thresholds:
        fig.add_vline(
            x=value,
            line_dash="dash",
            annotation_text=label,
            annotation_position="top"
        )

    fig.update_layout(
        xaxis_range=[0, 100],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def plot_incidents_by_location(events: list):
    abnormal_events = [
        event for event in events
        if event.get("prediction") == "abnormal"
    ]

    locations = [
        event.get("location", "알 수 없음")
        for event in abnormal_events
    ]

    if not locations:
        return make_empty_figure("위치별 불법 주정차 의심 신고 수")

    df = pd.DataFrame({"위치": locations})

    counts = (
        df["위치"]
        .value_counts()
        .reset_index()
    )

    counts.columns = ["위치", "불법 주정차 의심 신고 수"]

    fig = px.bar(
        counts,
        x="위치",
        y="불법 주정차 의심 신고 수",
        title="위치별 불법 주정차 의심 신고 수",
        labels={
            "위치": "위치",
            "불법 주정차 의심 신고 수": "불법 주정차 의심 신고 수"
        }
    )

    fig.update_layout(
        xaxis_tickangle=-30,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig


plot_abnormal_ratio = plot_detection_ratio
plot_risk_distribution = plot_violation_distribution