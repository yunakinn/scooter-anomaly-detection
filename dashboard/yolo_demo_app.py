import sys
import os
import tempfile
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import st_folium

from src.detector import Detector
from src.risk_scorer import RiskScorer
from src.event_system import LOCATIONS, create_detection_event, clear_events
from src.route_optimizer import get_priority_list, optimize_route, get_total_distance, LOCATION_COORDS
from src.visualization import (
    plot_detection_ratio,
    plot_events_by_time,
    plot_violation_distribution,
    plot_incidents_by_location,
)

ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = ROOT / "data/demo_images"

@st.cache_resource
def load_detector():
    return Detector()


st.set_page_config(
    page_title="ScooterOps — YOLO Detection",
    page_icon="🛴",
    layout="wide"
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
    background-color: #ffffff !important;
}

html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid rgba(79,103,216,0.08) !important;
    border-radius: 28px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow:
        0 36px 90px rgba(79,103,216,0.30),
        0 14px 38px rgba(79,103,216,0.16) !important;
}

div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 0.5px solid rgba(79,103,216,0.10) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.4rem !important;
    box-shadow: 0 4px 12px rgba(79,103,216,0.08);
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #ffffff !important;
}

[data-testid="stVerticalBlockBorderWrapper"] * {
    background-color: transparent;
}            
            
div[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    font-family: 'Manrope', sans-serif !important;
    color: #24324a !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #8d97a8 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

.slabel {
    font-size: 12px;
    font-weight: 800;
    color: #8d97a8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.8rem;
}

.card {
    background: #ffffff;
    border: 0.5px solid rgba(79,103,216,0.10);
    border-radius: 18px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(79,103,216,0.08);
}

.fbox {
    background: #f4f7ff;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
}

.flabel {
    font-size: 10px;
    color: #8d97a8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 3px;
}

.fval {
    font-size: 15px;
    font-weight: 600;
    color: #24324a;
}

.score-big {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 64px;
    color: #24324a;
    line-height: 1;
    letter-spacing: -2px;
}

.pill {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 99px;
    font-size: 13px;
    font-weight: 600;
    margin-top: 8px;
}
.pill-danger { background: #fde8e8; color: #a03030; }
.pill-warn   { background: #fff4de; color: #8a5e00; }
.pill-ok     { background: #e4f0e8; color: #2a6840; }
.pill-normal { background: #f4f7ff; color: #8d97a8; }
.pill-none   { background: #f4f7ff; color: #8d97a8; }

.bar-bg {
    background: #e5ebff;
    border-radius: 99px;
    height: 7px;
    margin: 14px 0 8px;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 99px;
}

.pred-abnormal {
    background: #fde8e8;
    color: #a03030;
    padding: 6px 18px;
    border-radius: 99px;
    font-size: 14px;
    font-weight: 700;
    display: inline-block;
}
.pred-normal {
    background: #e4f0e8;
    color: #2a6840;
    padding: 6px 18px;
    border-radius: 99px;
    font-size: 14px;
    font-weight: 700;
    display: inline-block;
}
.pred-none {
    background: #f4f7ff;
    color: #8d97a8;
    padding: 6px 18px;
    border-radius: 99px;
    font-size: 14px;
    font-weight: 700;
    display: inline-block;
}

.prow {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 0.5px solid rgba(79,103,216,0.10);
}
.prow:last-child {
    border-bottom: none;
}

.pnum {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: #f4f7ff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    color: #8d97a8;
    flex-shrink: 0;
}
.pnum-hot {
    background: #fde8e8;
    color: #a03030;
}

.stButton > button {
    background: #4f67d8 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 99px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 0.55rem 1.6rem !important;
    box-shadow: 0 6px 14px rgba(79,103,216,0.20);
}
.stButton > button:hover {
    background: #3954cc !important;
}
.stButton > button:disabled {
    background: #cfd6f5 !important;
    color: #ffffff !important;
    box-shadow: none !important;
}

.clear-btn > button {
    background: #ffffff !important;
    color: #8d97a8 !important;
    border: 0.5px solid rgba(79,103,216,0.18) !important;
    border-radius: 99px !important;
}
.clear-btn > button:hover {
    background: #f4f7ff !important;
    color: #4f67d8 !important;
}

.step {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
}
.step-num {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #4f67d8;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 800;
    flex-shrink: 0;
}
.step-text {
    font-size: 13px;
    color: #24324a;
    font-weight: 600;
}

.success-banner {
    background: #e4f0e8;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 13px;
    color: #2a6840;
    margin-bottom: 12px;
    font-weight: 600;
}

.empty {
    text-align: center;
    padding: 2rem 1rem;
    color: #b0b8c8;
    font-size: 13px;
    line-height: 2;
}

hr {
    border: none;
    border-top: 0.5px solid rgba(79,103,216,0.16);
    margin: 0.5rem 0;
}

.user-hero {
    background: #ffffff;
    border: 0.5px solid rgba(79,103,216,0.10);
    border-radius: 28px;
    padding: 2rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 18px rgba(79,103,216,0.08);
}

.user-title {
    font-family: 'Manrope', sans-serif;
    font-size: 34px;
    font-weight: 800;
    color: #24324a;
    line-height: 1.1;
}

.user-sub {
    font-size: 13px;
    color: #8d97a8;
    margin-top: 8px;
    line-height: 1.6;
}

.mini-card {
    background: #ffffff;
    border: 0.5px solid rgba(79,103,216,0.10);
    border-radius: 20px;
    padding: 1.2rem;
    box-shadow: 0 4px 14px rgba(79,103,216,0.08);
    margin-bottom: 1rem;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}

.status-box {
    background: #f4f7ff;
    border-radius: 16px;
    padding: 14px;
    text-align: center;
}

.status-num {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 30px;
    color: #24324a;
}

.status-label {
    font-size: 11px;
    color: #8d97a8;
    font-weight: 600;
}

.process-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 0.5px solid rgba(79,103,216,0.10);
}
.process-step:last-child {
    border-bottom: none;
}

.process-icon {
    width: 34px;
    height: 34px;
    border-radius: 12px;
    background: #f4f7ff;
    display: flex;
    align-items: center;
    justify-content: center;
}

.alert-item {
    background: #f4f7ff;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #24324a;
    font-weight: 500;
}

.page-header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
    margin-bottom: 1.5rem;
}
.page-header .page-title {
    font-family: 'Manrope', sans-serif;
    font-size: 34px;
    font-weight: 800;
    color: #24324a;
    margin: 0;
}
.page-header .page-subtitle {
    color: #6b7280;
    font-size: 0.95rem;
    margin-top: 0.6rem;
    line-height: 1.6;
}
.page-header .status-pill {
    background: #ffffff;
    color: #4f67d8;
    border-radius: 999px;
    padding: 12px 20px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    white-space: nowrap;
    box-shadow: 0 18px 40px rgba(79,103,216,0.1);
}
.hero-card {
    background: #ffffff;
    border-radius: 28px;
    padding: 1.5rem 1.75rem;
    box-shadow: 0 22px 50px rgba(79,103,216,0.08);
    border: 1px solid rgba(79,103,216,0.08);
    margin-bottom: 1.8rem;
}
.card-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
}
.stat-card {
    background: #f8faff;
    border-radius: 22px;
    padding: 1.2rem 1.35rem;
    border: 1px solid rgba(79,103,216,0.08);
    box-shadow: 0 12px 24px rgba(79,103,216,0.06);
}
.stat-card .title {
    font-size: 0.78rem;
    color: #677294;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.65rem;
}
.stat-card .value {
    font-size: 2rem;
    font-weight: 800;
    color: #24324a;
}
.stat-card .note {
    margin-top: 0.45rem;
    font-size: 0.88rem;
    color: #6b7280;
}
.dashboard-panel {
    background: #ffffff;
    border-radius: 28px;
    border: 1px solid rgba(79,103,216,0.08);
    box-shadow: 0 20px 35px rgba(79,103,216,0.07);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
.chart-card {
    background: #ffffff;
    border-radius: 24px;
    border: 1px solid rgba(79,103,216,0.08);
    padding: 1rem;
    box-shadow: 0 18px 32px rgba(79,103,216,0.06);
    margin-bottom: 1rem;
}
.location-card {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 0.5rem;
}
.location-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 1rem 1.1rem;
    background: #f4f7ff;
    border-radius: 16px;
    border: 1px solid rgba(79,103,216,0.08);
}
.location-name {
    font-size: 14px;
    font-weight: 700;
    color: #24324a;
}
.location-count {
    font-size: 13px;
    font-weight: 800;
    color: #4f67d8;
}
.location-card-empty {
    padding: 1.8rem 1rem;
    text-align: center;
    color: #8d97a8;
    font-size: 13px;
    background: #f9fbff;
    border-radius: 16px;
    border: 1px solid rgba(79,103,216,0.08);
}
/* selectbox 높이 깨짐 방지 */
div[data-baseweb="select"] {
    height: auto !important;
}

div[data-baseweb="select"] > div {
    min-height: 48px !important;
    height: 48px !important;
    border-radius: 14px !important;
    background-color: #ffffff !important;
}

div[data-baseweb="popover"] {
    z-index: 999999 !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid rgba(79,103,216,0.08) !important;
    border-radius: 28px !important;
    padding: 1.5rem !important;
    box-shadow:
        0 32px 80px rgba(79,103,216,0.28),
        0 14px 36px rgba(79,103,216,0.14) !important;

[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #ffffff !important;
    border-radius: 28px !important;
}                             
</style>
""", unsafe_allow_html=True)

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
    if "매우 높음" in level: return f'<span class="pill pill-danger">{level}</span>'
    elif "높음" in level: return f'<span class="pill pill-warn">{level}</span>'
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
for key in ["events", "current_event", "current_detection", "current_image_path"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "events" else None

scorer = RiskScorer()


# ── 헤더 ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div>
        <p class="page-title">🛴 Smart Scooter Safety Platform</p>
        <p class="page-subtitle">
            YOLO Illegal Parking Detection — Hanyang ERICA Campus
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── 탭 구성 ───────────────────────────────────────────────────────────────────
tab_user, tab_admin = st.tabs(["📱 사용자 — 신고하기", "🖥️ 관리자 — 운영 현황"])

# ════════════════════════════════════════════════════════════════════════════════
# 탭 1: 사용자
# ════════════════════════════════════════════════════════════════════════════════
with tab_user:
    st.markdown("<br>", unsafe_allow_html=True)

    events = st.session_state["events"]
    total_reports = len(events)
    pending_reports = total_reports
    completed_reports = 0

    left, right = st.columns([1.15, 1], gap="large")

with left:
    with st.container(border=True):

        st.markdown('<p class="slabel">📥 킥보드 신고</p>', unsafe_allow_html=True)

        st.markdown(
            '<div class="step"><div class="step-num">1</div><div class="step-text">신고 이미지 선택</div></div>',
            unsafe_allow_html=True
        )

        image_path = None
        demo_images = get_demo_images()

        if demo_images:
            demo_labels = [p.name for p in demo_images]

            selected_label = st.selectbox(
                "신고 이미지",
                demo_labels,
                label_visibility="collapsed"
            )

            image_path = DEMO_DIR / selected_label

            st.image(
                str(image_path),
                caption=selected_label,
                use_container_width=True
            )
        else:
            st.warning("data/demo_images 폴더에 이미지를 추가해주세요.")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="step"><div class="step-num">2</div><div class="step-text">신고 제출</div></div>',
            unsafe_allow_html=True
        )

        analyze_clicked = st.button(
            "🚨 신고 제출하기",
            use_container_width=True,
            disabled=image_path is None
        )

        if analyze_clicked and image_path:
            with st.spinner("신고 접수 중..."):
                try:
                    detector = load_detector()
                    detection_result = detector.predict(image_path)

                    score_result = scorer.score(
                        abnormal_confidence=detection_result.get("abnormal_confidence", 0.0),
                        detections=detection_result.get("detections", [])
                    )

                    event = create_detection_event(
                        image_path=image_path,
                        location=LOCATIONS[len(st.session_state["events"]) % len(LOCATIONS)],
                        source="Demo",
                        detection_result=detection_result,
                        score_result=score_result
                    )

                    st.session_state["events"].append(event)
                    st.session_state["current_event"] = event
                    st.session_state["current_detection"] = detection_result
                    st.session_state["current_image_path"] = str(image_path)

                    st.success("✅ 신고가 완료되었습니다. 관리자 확인 후 처리됩니다.")

                except Exception:
                    st.error("신고 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("↺ 초기화", use_container_width=True):
            st.session_state["events"] = []
            st.session_state["current_event"] = None
            st.session_state["current_detection"] = None
            st.session_state["current_image_path"] = None
            clear_events()
            st.rerun()

    with right:
        st.markdown('<p class="slabel">📊 신고 현황</p>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="dashboard-panel">
                <div class="status-grid">
                    <div class="status-box">
                        <div class="status-num">{total_reports}</div>
                        <div class="status-label">총 신고</div>
                    </div>
                    <div class="status-box">
                        <div class="status-num">{pending_reports}</div>
                        <div class="status-label">처리 대기</div>
                    </div>
                    <div class="status-box">
                        <div class="status-num">{completed_reports}</div>
                        <div class="status-label">처리 완료</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="slabel">📢 캠퍼스 안전 알림</p>', unsafe_allow_html=True)

        st.markdown("""
            <div class="dashboard-panel">
                <div class="alert-item">⚠️ 보행로 위 전동킥보드는 통행 방해 위험이 있습니다.</div>
                <div class="alert-item">🛴 쓰러진 킥보드는 사진 촬영 후 신고해주세요.</div>
                <div class="alert-item">📍 신고 위치는 관리자 시스템에서 자동 기록됩니다.</div>
            </div>
        """, unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════════════════════════
# 탭 2: 관리자
# ════════════════════════════════════════════════════════════════════════════════
with tab_admin:
    st.markdown("<br>", unsafe_allow_html=True)

    events = st.session_state["events"]

    # 지표
    total_events = len(events)
    abnormal_events = sum(1 for e in events if e.get("prediction") == "abnormal")
    high_priority_count = sum(1 for e in events if e.get("violation_score", 0) >= 80)
    avg_score = round(sum(e.get("violation_score", 0) for e in events) / total_events, 1) if total_events else 0.0

    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🔍 총 신고 수", total_events)
    m2.metric("⚠️ 불법 주정차 감지", abnormal_events)
    m3.metric("📊 평균 의심 점수", avg_score)
    m4.metric("🔴 고위험", high_priority_count)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 수거 우선순위 + 지도
    col_priority, col_map = st.columns(2, gap="medium")

    priority = get_priority_list(events)
    route = optimize_route(priority)
    total_distance = get_total_distance(route)

    with col_priority:
        st.markdown('<p class="slabel">📋 수거 우선순위</p>', unsafe_allow_html=True)
        if priority:
            for i, item in enumerate(priority[:6]):
                hot = "pnum-hot" if item.get("violation_score", 0) >= 80 else ""
                pill = get_pill(item.get("level", ""))
                st.markdown(f"""
                    <div class="prow">
                        <div class="pnum {hot}">#{i+1}</div>
                        <div style="flex:1;">
                            <div style="font-size:13px;font-weight:500;color:#1f2a44;">{item.get('location','-')}</div>
                            <div style="font-size:11px;color:#aaa;">{item.get('action','-')}</div>
                        </div>
                        {pill}
                        <div style="font-size:14px;font-weight:600;color:#1f2a44;min-width:36px;text-align:right;">{item.get('violation_score',0)}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty">신고된 불법 주정차가 없습니다</div>', unsafe_allow_html=True)

    with col_map:
        st.markdown('<p class="slabel">🗺️ 동선 최적화</p>', unsafe_allow_html=True)

        if route:
            st.caption(f"최적 동선 — 총 **{total_distance} m**")

            m = folium.Map(
                location=[37.2997, 126.8410],
                zoom_start=17,
                tiles="CartoDB positron"
            )

            # 전체 위치 회색 마커
            for loc, coords in LOCATION_COORDS.items():
                folium.CircleMarker(
                    location=coords,
                    radius=5,
                    color="#aaaaaa",
                    fill=True,
                    fill_color="#aaaaaa",
                    fill_opacity=0.5,
                    tooltip=loc
                ).add_to(m)

            # 동선 마커
            route_coords = []
            for item in route:
                coords = LOCATION_COORDS[item["location"]]
                route_coords.append(coords)
                color = "#c0392b" if item.get("violation_score", 0) >= 80 else "#d4a017"
                folium.Marker(
                    location=coords,
                    tooltip=f"#{item['visit_order']} {item['location']} (score: {item['violation_score']})",
                    icon=folium.DivIcon(html=f"""
                        <div style="
                            background:{color};color:white;
                            width:24px;height:24px;border-radius:50%;
                            display:flex;align-items:center;justify-content:center;
                            font-size:11px;font-weight:700;
                            border:2px solid white;
                            box-shadow:0 1px 4px rgba(0,0,0,0.3);
                        ">{item['visit_order']}</div>
                    """)
                ).add_to(m)

            # 동선 연결
            if len(route_coords) > 1:
                folium.PolyLine(
                    locations=route_coords,
                    color="#1f2a44",
                    weight=2,
                    opacity=0.6,
                    dash_array="6"
                ).add_to(m)

            st_folium(m, width=None, height=350, returned_objects=[])

        else:
            st.markdown('<div class="empty">신고 데이터가 없습니다<br>사용자 탭에서 신고를 제출해주세요</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    st.markdown('<p class="slabel">📊 통계</p>', unsafe_allow_html=True)

    if events:
        ch1, ch2 = st.columns(2, gap="medium")

        with ch1:
            fig = plot_detection_ratio(events)
            fig.update_layout(
                height=360,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        with ch2:
            fig = plot_events_by_time(events)
            fig.update_traces(width=0.3)
            fig.update_layout(
                height=260,
                bargap=0.6,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        ch3, ch4 = st.columns(2, gap="medium")

        with ch3:
            fig = plot_violation_distribution(events)
            fig.update_layout(
                height=260,
                bargap=0.6,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        with ch4:
            fig = plot_incidents_by_location(events)
            fig.update_traces(width=0.3)
            fig.update_layout(
                height=260,
                bargap=0.6,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.markdown(
            '<div class="empty" style="padding:3rem;">신고 데이터가 없습니다</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="slabel">🗂️ 이벤트 로그</p>', unsafe_allow_html=True)

    if events:
        df = pd.DataFrame(events)
        columns = [
            "event_id",
            "timestamp",
            "location",
            "source",
            "prediction",
            "confidence",
            "abnormal_confidence",
            "violation_score",
            "level",
            "action"
        ]
        existing_columns = [c for c in columns if c in df.columns]
        df = df[existing_columns]
        if "timestamp" in df.columns:
            df["timestamp"] = df["timestamp"].astype(str).str[:19]
        st.dataframe(df, use_container_width=True)
    else:
        st.markdown(
            '<div class="empty" style="padding:3rem;">이벤트 로그가 없습니다</div>',
            unsafe_allow_html=True
        )
