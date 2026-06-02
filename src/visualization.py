import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plot_detection_ratio(events: list):
    counts = {
        "normal": 0,
        "abnormal": 0,
        "none": 0
    }

    for e in events:
        label = e.get("prediction", "none")
        counts[label] = counts.get(label, 0) + 1

    fig = px.pie(
        names=list(counts.keys()),
        values=list(counts.values()),
        title="Normal vs Abnormal Detection Ratio"
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(legend_title_text="Prediction")

    return fig


def plot_events_by_time(events: list):
    hours = []

    for e in events:
        ts = e.get("timestamp", "")
        if ts:
            try:
                hour = int(ts.split(" ")[1].split(":")[0])
                hours.append(hour)
            except Exception:
                pass

    if not hours:
        fig = go.Figure()
        fig.update_layout(title="Detection Events by Hour (No Data)")
        return fig

    df = pd.DataFrame({"hour": hours})
    counts = df["hour"].value_counts().sort_index().reset_index()
    counts.columns = ["hour", "count"]

    fig = px.bar(
        counts,
        x="hour",
        y="count",
        title="Detection Events by Hour",
        labels={"hour": "Hour", "count": "Number of Events"}
    )

    fig.update_layout(xaxis=dict(dtick=1))
    return fig


def plot_violation_distribution(events: list):
    scores = [
        e["violation_score"]
        for e in events
        if "violation_score" in e
    ]

    if not scores:
        fig = go.Figure()
        fig.update_layout(title="Illegal Parking Suspicion Score Distribution (No Data)")
        return fig

    fig = px.histogram(
        x=scores,
        title="Illegal Parking Suspicion Score Distribution",
        labels={"x": "Violation Score", "y": "Count"}
    )

    fig.update_traces(xbins=dict(start=0, end=100, size=10))

    thresholds = [
        (30, "Low (30)"),
        (50, "High (50)"),
        (80, "Very High (80)")
    ]

    for value, label in thresholds:
        fig.add_vline(
            x=value,
            line_dash="dash",
            annotation_text=label,
            annotation_position="top"
        )

    fig.update_layout(xaxis_range=[0, 100])
    return fig


def plot_incidents_by_location(events: list):
    abnormal_events = [
        e for e in events
        if e.get("prediction") == "abnormal"
    ]

    locations = [
        e.get("location", "Unknown")
        for e in abnormal_events
    ]

    if not locations:
        fig = go.Figure()
        fig.update_layout(title="Abnormal Detections by Location (No Data)")
        return fig

    df = pd.DataFrame({"location": locations})
    counts = df["location"].value_counts().reset_index()
    counts.columns = ["location", "count"]

    fig = px.bar(
        counts,
        x="location",
        y="count",
        title="Abnormal Detections by Location",
        labels={"location": "Location", "count": "Abnormal Detection Count"}
    )

    return fig


plot_abnormal_ratio = plot_detection_ratio
plot_risk_distribution = plot_violation_distribution
