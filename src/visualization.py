import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plot_abnormal_ratio(events: list):
    """
    Chart 1: Pie chart showing normal vs abnormal ratio.
    (abnormal와normal 비율 차트)
    """
    counts = {"normal": 0, "abnormal": 0}
    for e in events:
        label = e.get("prediction", "normal")
        counts[label] = counts.get(label, 0) + 1

    fig = px.pie(
        names=list(counts.keys()),
        values=list(counts.values()),
        title="Normal vs Abnormal Ratio",
        color=list(counts.keys()),
        color_discrete_map={"normal": "#4C78A8", "abnormal": "#F58518"}
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(legend_title_text="Prediction")
    return fig


def plot_events_by_time(events: list):
    """
    Chart 2: Bar chart showing number of events per hour of day.
    (시간대별 이벤트 수 그래프)
    """
    hours = []
    for e in events:
        ts = e.get("timestamp", "")
        if ts:
            try:
                hour = int(ts.split(":")[0])
                hours.append(hour)
            except ValueError:
                pass

    if not hours:
        fig = go.Figure()
        fig.update_layout(title="Events by Hour of Day (No Data)")
        return fig

    df = pd.DataFrame({"hour": hours})
    counts = df["hour"].value_counts().sort_index().reset_index()
    counts.columns = ["hour", "count"]

    fig = px.bar(
        counts, x="hour", y="count",
        title="Events by Hour of Day",
        labels={"hour": "Hour (24h)", "count": "Number of Events"},
        color_discrete_sequence=["#457B9D"]
    )
    fig.update_layout(xaxis=dict(dtick=1))
    return fig


def plot_risk_distribution(events: list):
    """
    Chart 3: Risk distribution chart
    (위험도 분포 차트)
    """
    scores = [e["risk_score"] for e in events if "risk_score" in e]

    if not scores:
        fig = go.Figure()
        fig.update_layout(title="Risk Score Distribution (No Data)")
        return fig

    fig = px.histogram(
        x=scores,
        title="Risk Score Distribution",
        labels={"x": "Risk Score", "y": "Count"},
        color_discrete_sequence=["#4E79A7"]
    )
    fig.update_traces(xbins=dict(start=0, end=100, size=10))

    # Threshold lines
    thresholds = [
        (30, "green",  "Low (30)"),
        (50, "orange", "Caution (50)"),
        (80, "red",    "Danger (80)"),
    ]
    for value, color, label in thresholds:
        fig.add_vline(
            x=value,
            line_dash="dash",
            line_color=color,
            annotation_text=label,
            annotation_position="top"
        )

    fig.update_layout(xaxis_range=[0, 100])
    return fig


def plot_incidents_by_location(events: list):
    """
    Chart 4: Bar chart showing incident count per location.
    (위치별 위험 발생 수 그래프)
    """
    locations = [e.get("location", "Unknown") for e in events]

    if not locations:
        fig = go.Figure()
        fig.update_layout(title="Incidents by Location (No Data)")
        return fig

    df = pd.DataFrame({"location": locations})
    counts = df["location"].value_counts().reset_index()
    counts.columns = ["location", "count"]

    fig = px.bar(
        counts,
        x="location",
        y="count",
        title="Incidents by Location",
        labels={"location": "Location", "count": "Incident Count"},
        color="count",
        color_continuous_scale="Reds"
    )
    return fig