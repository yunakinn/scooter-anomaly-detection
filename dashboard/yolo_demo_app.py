import sys
import os
import tempfile
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import streamlit as st
from PIL import Image

from src.detector import Detector
from src.risk_scorer import RiskScorer
from src.event_system import LOCATIONS, create_detection_event, clear_events
from src.route_optimizer import get_priority_list, optimize_route, get_total_distance
from src.visualization import (
    plot_detection_ratio,
    plot_events_by_time,
    plot_violation_distribution,
    plot_incidents_by_location,
)

ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = ROOT / "data/demo_images"

st.set_page_config(
    page_title="ScooterOps — YOLO Detection",
    page_icon="🛴",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Instrument+Serif:ital@0;1&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #f5f0e8 !important;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1300px;
    background-color: #f5f0e8;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: #fdfaf5 !important;
    border: 0.5px solid rgba(0,0,0,0.08) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.4rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
div[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 600 !important;
    font-family: 'Instrument Serif', serif !important;
    color: #1a1a1a !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #999 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* Section labels */
.slabel {
    font-size: 11px;
    font-weight: 600;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.8rem;
}

/* Cards */
.card {
    background: #fdfaf5;
    border: 0.5px solid rgba(0,0,0,0.08);
    border-radius: 18px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* Field boxes */
.fbox {
    background: #efe9dc;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.flabel {
    font-size: 10px;
    color: #999;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 3px;
}
.fval {
    font-size: 15px;
    font-weight: 500;
    color: #1a1a1a;
}

/* Big score */
.score-big {
    font-family: 'Instrument Serif', serif;
    font-size: 64px;
    color: #1a1a1a;
    line-height: 1;
    letter-spacing: -2px;
}

/* Pills */
.pill { display: inline-block; padding: 4px 16px; border-radius: 99px; font-size: 13px; font-weight: 500; margin-top: 8px; }
.pill-danger { background: #fde8e8; color: #a03030; }
.pill-warn   { background: #fdf0dc; color: #8a5e00; }
.pill-ok     { background: #e4f0e8; color: #2a6840; }
.pill-normal { background: #ece8e0; color: #777; }
.pill-none   { background: #ece8e0; color: #777; }

/* Bar */
.bar-bg { background: #e8e2d9; border-radius: 99px; height: 7px; margin: 14px 0 8px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 99px; }

/* Prediction badge */
.pred-abnormal { background: #fde8e8; color: #a03030; padding: 6px 18px; border-radius: 99px; font-size: 14px; font-weight: 600; display: inline-block; }
.pred-normal   { background: #e4f0e8; color: #2a6840; padding: 6px 18px; border-radius: 99px; font-size: 14px; font-weight: 600; display: inline-block; }
.pred-none     { background: #ece8e0; color: #777;    padding: 6px 18px; border-radius: 99px; font-size: 14px; font-weight: 600; display: inline-block; }

/* Priority rows */
.prow { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 0.5px solid rgba(0,0,0,0.07); }
.prow:last-child { border-bottom: none; }
.pnum { width: 28px; height: 28px; border-radius: 8px; background: #efe9dc; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: #888; flex-shrink: 0; }
.pnum-hot { background: #fde8e8; color: #a03030; }

/* Buttons */
.stButton > button {
    background: #1a1a1a !important;
    color: #f5f0e8 !important;
    border: none !important;
    border-radius: 99px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 0.55rem 1.6rem !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { background: #333 !important; }
.stButton > button:disabled { background: #ccc !important; color: #888 !important; }

/* Clear button override */
.clear-btn > button {
    background: transparent !important;
    color: #999 !important;
    border: 0.5px solid rgba(0,0,0,0.15) !important;
    border-radius: 99px !important;
}
.clear-btn > button:hover { background: #efe9dc !important; color: #555 !important; }

/* Radio */
div[data-testid="stRadio"] label { font-size: 13px; }

/* Selectbox */
div[data-testid="stSelectbox"] > div { border-radius: 10px !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: #fdfaf5 !important;
    border: 1.5px dashed rgba(0,0,0,0.12) !important;
    border-radius: 14px !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #fdfaf5 !important;
    border: 0.5px solid rgba(0,0,0,0.08) !important;
    border-radius: 12px !important;
}

/* Info/warning boxes */
[data-testid="stInfo"] { border-radius: 12px !important; background: #efe9dc !important; }
[data-testid="stWarning"] { border-radius: 12px !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 14px !important; overflow: hidden; }

/* Divider */
hr { border: none; border-top: 0.5px solid rgba(0,0,0,0.08); margin: 0.5rem 0; }

/* Empty state */
.empty { text-align: center; padding: 2rem 1rem; color: #bbb; font-size: 13px; line-height: 2; }

/* Step indicator */
.step { display: flex; align-items: center; gap: 10px; margin-bottom: 1rem; }
.step-num { width: 24px; height: 24px; border-radius: 50%; background: #1a1a1a; color: #f5f0e8; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; flex-shrink: 0; }
.step-text { font-size: 13px; color: #555; }

/* Success flash */
.success-banner { background: #e4f0e8; border-radius: 12px; padding: 12px 16px; font-size: 13px; color: #2a6840; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Cache & helpers ───────────────────────────────────────────────────────────
@st.cache_resource
def load_detector():
    return Detector()

def get_demo_images():
    if not DEMO_DIR.exists():
        return []
    exts = {".jpg", ".jpeg", ".png"}
    return sorted([p for p in DEMO_DIR.rglob("*") if p.is_file() and p.suffix.lower() in exts])

def save_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp.write(uploaded_file.getbuffer())
    temp.close()
    return Path(temp.name)

def get_pill(level):
    if not level or level == "-": return '<span class="pill pill-none">—</span>'
    if "매우 높음" in level or "위험" in level: return f'<span class="pill pill-danger">{level}</span>'
    elif "높음" in level or "주의" in level: return f'<span class="pill pill-warn">{level}</span>'
    elif "낮음" in level: return f'<span class="pill pill-ok">{level}</span>'
    else: return f'<span class="pill pill-normal">{level}</span>'

def get_bar_color(score):
    if score >= 80: return "#c0392b"
    elif score >= 50: return "#d4a017"
    elif score >= 30: return "#2a7a4a"
    return "#bbb"

def get_pred_badge(pred):
    if pred == "abnormal": return '<span class="pred-abnormal">🔴 Abnormal</span>'
    elif pred == "normal": return '<span class="pred-normal">🟢 Normal</span>'
    else: return '<span class="pred-none">— Not detected</span>'

# ── Session state ─────────────────────────────────────────────────────────────
if "events" not in st.session_state:
    st.session_state["events"] = []
if "current_event" not in st.session_state:
    st.session_state["current_event"] = None
if "current_detection" not in st.session_state:
    st.session_state["current_detection"] = None
if "current_image_path" not in st.session_state:
    st.session_state["current_image_path"] = None

scorer = RiskScorer()

# ── Header ────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([5, 1])
with h1:
    st.markdown("""
        <span style="font-family:'Instrument Serif',serif;font-size:34px;color:#1a1a1a;letter-spacing:-1px;">
            🛴 ScooterOps
        </span>
        <span style="font-size:13px;color:#aaa;margin-left:12px;">
            YOLO Illegal Parking Detection — Hanyang ERICA Campus
        </span>
    """, unsafe_allow_html=True)
with h2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("● Live Demo")

st.divider()

# ── Metrics ───────────────────────────────────────────────────────────────────
events = st.session_state["events"]
total_events     = len(events)
abnormal_events  = sum(1 for e in events if e.get("prediction") == "abnormal")
high_priority    = sum(1 for e in events if e.get("violation_score", 0) >= 80)
avg_score        = round(sum(e.get("violation_score", 0) for e in events) / total_events, 1) if total_events else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("🔍 Total analysed", total_events)
m2.metric("⚠️ Abnormal detected", abnormal_events)
m3.metric("📊 Avg suspicion score", avg_score)
m4.metric("🔴 High priority", high_priority)

st.markdown("<br>", unsafe_allow_html=True)

# ── Main — Input + Result ─────────────────────────────────────────────────────
col_input, col_result = st.columns([1, 2], gap="medium")

with col_input:
    st.markdown('<p class="slabel">📥 Input</p>', unsafe_allow_html=True)

    st.markdown("""
        <div class="step"><div class="step-num">1</div><div class="step-text">Choose image source</div></div>
    """, unsafe_allow_html=True)

    input_mode = st.radio("Image source", ["Demo image", "Upload image"], horizontal=True, label_visibility="collapsed")

    st.markdown("""
        <div class="step"><div class="step-num">2</div><div class="step-text">Select detection location</div></div>
    """, unsafe_allow_html=True)

    selected_location = st.selectbox("Location", LOCATIONS, label_visibility="collapsed")

    st.markdown("""
        <div class="step"><div class="step-num">3</div><div class="step-text">Select or upload image</div></div>
    """, unsafe_allow_html=True)

    image_path = None

    if input_mode == "Demo image":
        demo_images = get_demo_images()
        if demo_images:
            demo_labels = [p.name for p in demo_images]
            selected_label = st.selectbox("Sample image", demo_labels, label_visibility="collapsed")
            image_path = DEMO_DIR / selected_label
            st.image(str(image_path), caption=selected_label, use_container_width=True)
        else:
            st.warning("No demo images found in data/demo_images. Add some JPG/PNG files there!")
    else:
        uploaded = st.file_uploader("Upload image", type=["jpg","jpeg","png"], label_visibility="collapsed")
        if uploaded:
            image_path = save_uploaded_file(uploaded)
            st.image(Image.open(image_path), caption=uploaded.name, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
        <div class="step"><div class="step-num">4</div><div class="step-text">Run detection</div></div>
    """, unsafe_allow_html=True)

    analyze_clicked = st.button("🔍 Run YOLO Detection", use_container_width=True, disabled=image_path is None)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("↺ Clear all events", use_container_width=True):
            st.session_state["events"] = []
            st.session_state["current_event"] = None
            st.session_state["current_detection"] = None
            st.session_state["current_image_path"] = None
            clear_events()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── Result panel ──────────────────────────────────────────────────────────────
with col_result:
    st.markdown('<p class="slabel">🎯 YOLO Detection Result</p>', unsafe_allow_html=True)

    if analyze_clicked and image_path:
        with st.spinner("Running YOLO detection..."):
            try:
                detector = load_detector()
                detection_result = detector.predict(image_path)
                score_result = scorer.score(
                    abnormal_confidence=detection_result.get("abnormal_confidence", 0.0),
                    detections=detection_result.get("detections", [])
                )
                event = create_detection_event(
                    image_path=image_path,
                    location=selected_location,
                    source=input_mode,
                    detection_result=detection_result,
                    score_result=score_result
                )
                st.session_state["events"].append(event)
                st.session_state["current_event"] = event
                st.session_state["current_detection"] = detection_result
                st.session_state["current_image_path"] = str(image_path)
                st.rerun()
            except Exception as e:
                st.error("YOLO analysis failed.")
                st.exception(e)

    current_event     = st.session_state["current_event"]
    current_detection = st.session_state["current_detection"]

    if current_event and current_detection:
        score = current_event.get("violation_score", 0)
        level = current_event.get("level", "-")
        pred  = current_event.get("prediction", "none")

        st.markdown(f'<div class="success-banner">✅ Detection complete — Event #{current_event.get("event_id")} saved</div>', unsafe_allow_html=True)

        # Score + grade
        left, right = st.columns([1, 2])
        with left:
            st.markdown(f"""
                <div class="score-big">{score}</div>
                {get_pill(level)}
                <div style="font-size:12px;color:#aaa;margin-top:6px;">Suspicion score</div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="fbox">
                    <div class="flabel">Prediction</div>
                    <div class="fval">{get_pred_badge(pred)}</div>
                </div>
                <div class="fbox">
                    <div class="flabel">Confidence</div>
                    <div class="fval">{current_event.get('confidence', 0.0):.2f}</div>
                </div>
                <div class="fbox">
                    <div class="flabel">Location</div>
                    <div class="fval">{current_event.get('location', '-')}</div>
                </div>
                <div class="fbox">
                    <div class="flabel">Recommended action</div>
                    <div class="fval">{current_event.get('action', '-')}</div>
                </div>
            """, unsafe_allow_html=True)

        with right:
            # Progress bar
            bar_col = get_bar_color(score)
            st.markdown(f"""
                <div class="bar-bg">
                    <div class="bar-fill" style="width:{min(int(score),100)}%;background:{bar_col};"></div>
                </div>
            """, unsafe_allow_html=True)

            # Images side by side
            img1, img2 = st.columns(2)
            with img1:
                st.image(st.session_state["current_image_path"], caption="📷 Original", use_container_width=True)
            with img2:
                st.image(current_detection["annotated_image"], caption="🎯 YOLO result", channels="BGR", use_container_width=True)

            with st.expander("🔬 Detection details"):
                detections = current_detection.get("detections", [])
                if detections:
                    st.dataframe(pd.DataFrame(detections), use_container_width=True)
                else:
                    st.info("No objects detected in this image.")

    else:
        st.markdown("""
            <div class="empty">
                👈 Follow the steps on the left<br>
                Upload or select an image<br>
                then click <strong>Run YOLO Detection</strong>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Priority + Route ──────────────────────────────────────────────────────────
col_priority, col_route = st.columns(2, gap="medium")

with col_priority:
    st.markdown('<p class="slabel">📋 Collection Priority</p>', unsafe_allow_html=True)
    priority = get_priority_list(events)
    if priority:
        for i, item in enumerate(priority[:6]):
            hot  = "pnum-hot" if item.get("violation_score", 0) >= 80 else ""
            pill = get_pill(item.get("level", ""))
            st.markdown(f"""
                <div class="prow">
                    <div class="pnum {hot}">#{i+1}</div>
                    <div style="flex:1;">
                        <div style="font-size:13px;font-weight:500;color:#1a1a1a;">{item.get('location','-')}</div>
                        <div style="font-size:11px;color:#aaa;">{item.get('action','-')}</div>
                    </div>
                    {pill}
                    <div style="font-size:14px;font-weight:600;color:#1a1a1a;min-width:36px;text-align:right;">{item.get('violation_score',0)}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty">No abnormal events yet<br>Run a detection to see priority list</div>', unsafe_allow_html=True)

with col_route:
    st.markdown('<p class="slabel">🗺️ Route Optimisation</p>', unsafe_allow_html=True)
    route          = optimize_route(priority)
    total_distance = get_total_distance(route)
    if route:
        st.caption(f"Optimised route — **{total_distance} m** total distance")
        for item in route:
            hot  = "pnum-hot" if item.get("violation_score", 0) >= 80 else ""
            pill = get_pill(item.get("level", ""))
            st.markdown(f"""
                <div class="prow">
                    <div class="pnum {hot}">#{item['visit_order']}</div>
                    <div style="flex:1;">
                        <div style="font-size:13px;font-weight:500;color:#1a1a1a;">{item.get('location','-')}</div>
                        <div style="font-size:11px;color:#aaa;">Move: {item.get('distance_from_prev',0)} m</div>
                    </div>
                    {pill}
                    <div style="font-size:14px;font-weight:600;color:#1a1a1a;min-width:36px;text-align:right;">{item.get('violation_score',0)}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty">No route available yet<br>Run detections to generate route</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
st.markdown('<p class="slabel">📊 Analytics</p>', unsafe_allow_html=True)
if events:
    ch1, ch2 = st.columns(2, gap="medium")
    with ch1:
        fig = plot_detection_ratio(events)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with ch2:
        fig = plot_events_by_time(events)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    ch3, ch4 = st.columns(2, gap="medium")
    with ch3:
        fig = plot_violation_distribution(events)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with ch4:
        fig = plot_incidents_by_location(events)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown('<div class="empty" style="padding:3rem;">Run at least one detection to see analytics</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Event Log ─────────────────────────────────────────────────────────────────
st.markdown('<p class="slabel">🗂️ Event Log</p>', unsafe_allow_html=True)
if events:
    log_df = pd.DataFrame(events)
    display_columns = ["event_id","timestamp","location","source","prediction","confidence","abnormal_confidence","violation_score","level","action"]
    existing_columns = [col for col in display_columns if col in log_df.columns]
    log_df = log_df[existing_columns]
    log_df["timestamp"] = log_df["timestamp"].str[:19]
    st.dataframe(log_df, use_container_width=True, hide_index=True)
else:
    st.markdown('<div class="empty">No events logged yet</div>', unsafe_allow_html=True)