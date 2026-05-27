import streamlit as st
from PIL import Image
import random

st.set_page_config(
    page_title="Scooter Anomaly Detection",
    page_icon="🛴",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .metric-card {
        background: #1e1e2e;
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 1.2rem;
    }
    div[data-testid="stMetric"] {
        background: #1a1a2e;
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    div[data-testid="stMetricValue"] { font-size: 2rem !important; }
    .section-header {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #888;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .event-box {
        background: #1a1a2e;
        border: 1px solid #2a2a3e;
        border-radius: 10px;
        padding: 1rem 1.2rem;
    }
    .priority-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 0;
        border-bottom: 1px solid #2a2a3e;
    }
</style>
""", unsafe_allow_html=True)


LOCATIONS = ["정문 앞", "도서관 앞", "기숙사 앞", "편의점 앞", "체육관 앞"]


def mock_event():
    return {
        "event_id": random.randint(1000, 9999),
        "location": random.choice(LOCATIONS),
        "tilt": round(random.uniform(0, 45), 1),
        "shock": random.choice([True, False])
    }


def mock_risk_score(tilt, shock):
    tilt_score = min((tilt / 45) * 20, 20)
    shock_score = 10 if shock else 0
    confidence = random.uniform(0.5, 1.0)
    return round(confidence * 70 + tilt_score + shock_score, 1)


def get_grade(score):
    if score >= 80:
        return "🔴 위험", "Immediate collection required"
    elif score >= 50:
        return "🟡 주의", "Reposition needed"
    elif score >= 30:
        return "🟢 낮음", "Check on site"
    else:
        return "⚪ 정상", "Normal — no action needed"


# ─── Header ───────────────────────────────────────────────────────────────────

col_title, col_badge = st.columns([5, 1])
with col_title:
    st.markdown("## 🛴 Scooter Anomaly Detection")
    st.caption("Operations Dashboard")
with col_badge:
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("● Live")

st.divider()

# ─── Metrics row ──────────────────────────────────────────────────────────────

m1, m2, m3, m4 = st.columns(4)
m1.metric("🛴 Total scooters", "48", "On campus")
m2.metric("⚠️ Abnormal", "7", "-2 from yesterday")
m3.metric("📋 Events today", "23", "+5 since morning")
m4.metric("✅ Resolved", "16", "Collected today")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main row — IMU Event + Image Upload ──────────────────────────────────────

col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<p class="section-header">📡 IMU Event</p>', unsafe_allow_html=True)

    if st.button("⟳ Simulate Event", use_container_width=True):
        st.session_state["event"] = mock_event()

    if "event" in st.session_state:
        e = st.session_state["event"]
        c1, c2 = st.columns(2)
        c1.markdown(f"**Event ID**  \n`{e['event_id']}`")
        c2.markdown(f"**Location**  \n{e['location']}")
        c1.markdown(f"**Tilt angle**  \n{e['tilt']}°")
        c2.markdown(f"**Shock**  \n{'⚡ Detected' if e['shock'] else '— None'}")
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

st.markdown("<br>", unsafe_allow_html=True)

# ─── Second row — Risk Assessment + Priority List ─────────────────────────────

col_risk, col_priority = st.columns(2)

with col_risk:
    st.markdown('<p class="section-header">⚠️ Risk Assessment</p>', unsafe_allow_html=True)

    if "event" in st.session_state:
        e = st.session_state["event"]
        score = mock_risk_score(e["tilt"], e["shock"])
        grade, action = get_grade(score)

        score_col, grade_col = st.columns([1, 1])
        score_col.metric("Risk score", score)
        grade_col.metric("Grade", grade)

        st.progress(int(score) / 100)
        st.markdown(f"**Recommended action:** {action}")
    else:
        st.info("Simulate an event first to see the risk assessment.")

with col_priority:
    st.markdown('<p class="section-header">📋 Collection Priority</p>', unsafe_allow_html=True)

    mock_priority = [
        {"rank": 1, "location": "정문 앞",  "score": 91.2, "grade": "🔴 위험", "detail": "Tilt 43° · Shock detected"},
        {"rank": 2, "location": "도서관 앞", "score": 64.8, "grade": "🟡 주의", "detail": "Tilt 38° · No shock"},
        {"rank": 3, "location": "기숙사 앞", "score": 38.4, "grade": "🟢 낮음", "detail": "Tilt 22° · No shock"},
        {"rank": 4, "location": "편의점 앞", "score": 12.1, "grade": "⚪ 정상", "detail": "Tilt 5° · No shock"},
    ]

    for item in mock_priority:
        col_rank, col_info, col_score = st.columns([0.5, 3, 1])
        col_rank.markdown(f"**#{item['rank']}**")
        col_info.markdown(f"**{item['location']}**  \n{item['detail']}")
        col_score.markdown(f"{item['grade']}  \n`{item['score']}`")
        st.divider()