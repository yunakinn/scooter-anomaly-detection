import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from PIL import Image

# ── Real imports from teammates ──────────────────────────────────────────────
from src.event_system import generate_mock_event, get_events
from src.risk_scorer import RiskScorer
from src.route_optimizer import get_priority_list, optimize_route, get_total_distance
from src.visualization import (
    plot_abnormal_ratio,
    plot_events_by_time,
    plot_risk_distribution,
    plot_incidents_by_location,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scooter Anomaly Detection",
    page_icon="🛴",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stMetric"] {
        background: var(--background-color);
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    .section-header {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: grey;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "scored_events" not in st.session_state:
    st.session_state["scored_events"] = []
if "current_event" not in st.session_state:
    st.session_state["current_event"] = None
if "current_risk" not in st.session_state:
    st.session_state["current_risk"] = None

scorer = RiskScorer()

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([5, 1])
with col_title:
    st.markdown("## 🛴 Scooter Anomaly Detection")
    st.caption("Operations Dashboard — Hanyang University ERICA Campus")
with col_badge:
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("● Live")

st.divider()

# ── Metrics row ───────────────────────────────────────────────────────────────
all_events = st.session_state["scored_events"]
total      = len(all_events)
abnormal   = sum(1 for e in all_events if e.get("status") == "abnormal")
danger     = sum(1 for e in all_events if "위험" in e.get("level", ""))
resolved   = max(0, total - danger)

m1, m2, m3, m4 = st.columns(4)
m1.metric("🛴 Total events",   total)
m2.metric("⚠️ Abnormal",       abnormal)
m3.metric("🔴 Danger",         danger)
m4.metric("✅ Resolved",        resolved)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1 — IMU Event + Image Upload ─────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<p class="section-header">📡 IMU Event</p>', unsafe_allow_html=True)

    if st.button("⟳ Simulate IMU Event", use_container_width=True):
        event = generate_mock_event()
        st.session_state["current_event"] = event

        risk = scorer.score(
            detections=[],
            tilt_angle=event["tilt"],
            shock_detected=event["shock"]
        )

        merged = {**event, **risk}
        st.session_state["current_risk"] = risk
        st.session_state["scored_events"].append(merged)

    if st.session_state["current_event"]:
        e = st.session_state["current_event"]
        c1, c2 = st.columns(2)
        c1.markdown(f"**Event ID**  \n`{e['event_id']}`")
        c2.markdown(f"**Location**  \n{e['location']}")
        c1.markdown(f"**Tilt**  \n{e['tilt']}°")
        c2.markdown(f"**Shock**  \n{'⚡ Detected' if e['shock'] else '— None'}")
        c1.markdown(f"**Status**  \n{'🔴 Abnormal' if e['status'] == 'abnormal' else '🟢 Normal'}")
        c2.markdown(f"**Time**  \n{e['timestamp'][:19]}")
    else:
        st.info("Click simulate to generate a mock IMU event.")

with col_right:
    st.markdown('<p class="section-header">🖼️ Image Upload</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload scooter image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="Uploaded image", use_container_width=True)
        st.info("💡 YOLO detector will be connected here once model weights are available.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 2 — Risk Assessment + Collection Priority ─────────────────────────────
col_risk, col_priority = st.columns(2)

with col_risk:
    st.markdown('<p class="section-header">⚠️ Risk Assessment</p>', unsafe_allow_html=True)

    risk = st.session_state["current_risk"]
    if risk:
        score_col, grade_col = st.columns(2)
        score_col.metric("Risk Score", risk["risk_score"])
        grade_col.metric("Grade", risk["level"])

        st.progress(int(risk["risk_score"]) / 100)
        st.markdown(f"**Recommended action:** {risk['action']}")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Score breakdown"):
            b1, b2, b3 = st.columns(3)
            b1.metric("YOLO confidence", f"{risk['abnormal_conf']:.2f}")
            b2.metric("Tilt score",      f"{risk['tilt_score']:.2f}")
            b3.metric("Shock score",     f"{risk['shock_score']:.2f}")
    else:
        st.info("Simulate an event first to see the risk assessment.")

with col_priority:
    st.markdown('<p class="section-header">📋 Collection Priority</p>', unsafe_allow_html=True)

    all_scored = st.session_state["scored_events"]
    if all_scored:
        priority   = get_priority_list(all_scored)
        route      = optimize_route(priority)
        total_dist = get_total_distance(route)

        st.caption(f"Total route distance: **{total_dist} m**")

        for item in route[:6]:
            rc1, rc2, rc3 = st.columns([0.5, 3, 1.5])
            rc1.markdown(f"**#{item['visit_order']}**")
            rc2.markdown(f"**{item['location']}**  \n{item['action']}")
            rc3.markdown(f"{item['level']}  \n`{item['risk_score']}`")
            st.divider()
    else:
        st.info("No events yet. Simulate events to see the priority list.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 3 — Charts ────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Analytics</p>', unsafe_allow_html=True)

all_scored = st.session_state["scored_events"]

if len(all_scored) >= 1:
    ch1, ch2 = st.columns(2)
    with ch1:
        events_with_pred = [
            {**e, "prediction": e.get("status", "normal")}
            for e in all_scored
        ]
        st.plotly_chart(plot_abnormal_ratio(events_with_pred), use_container_width=True)
    with ch2:
        st.plotly_chart(plot_events_by_time(all_scored), use_container_width=True)

    ch3, ch4 = st.columns(2)
    with ch3:
        st.plotly_chart(plot_risk_distribution(all_scored), use_container_width=True)
    with ch4:
        st.plotly_chart(plot_incidents_by_location(all_scored), use_container_width=True)
else:
    st.info("Simulate at least 1 event to see analytics charts.")

# ── Event log ─────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="section-header">🗂️ Event Log</p>', unsafe_allow_html=True)

if all_scored:
    import pandas as pd
    df = pd.DataFrame(all_scored)[
        ["event_id", "timestamp", "location", "tilt", "shock", "status", "risk_score", "level", "action"]
    ]
    df["timestamp"] = df["timestamp"].str[:19]
    st.dataframe(df, use_container_width=True)
else:
    st.info("No events logged yet.")
