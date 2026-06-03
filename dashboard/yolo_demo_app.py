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
.slabel {
    font-size: 11px;
    font-weight: 600;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.8rem;
}
.card {
    background: #fdfaf5;
    border: 0.5px solid rgba(0,0,0,0.08);
    border-radius: 18px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
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
.score-big {
    font-family: 'Instrument Serif', serif;
    font-size: 64px;
    color: #1a1a1a;
    line-height: 1;
    letter-spacing: -2px;
}
.pill { display: inline-block; padding: 4px 16px; border-radius: 99px; font-size: 13px; font-weight: 500; margin-top: 8px; }
.pill-danger { background: #fde8e8; color: #a03030; }
.pill-warn   { background: #fdf0dc; color: #8a5e00; }
.pill-ok     { background: #e4f0e8; color: #2a6840; }
.pill-normal { background: #ece8e0; color: #777; }
.pill-none   { background: #ece8e0; color: #777; }
.bar-bg { background: #e8e2d9; border-radius: 99px; height: 7px; margin: 14px 0 8px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 99px; }
.pred-abnormal { background: #fde8e8; color: #a03030; padding: 6px 18px; border-radius: 99px; font-size: 14px; font-weight: 600; display: inline-block; }
.pred-normal   { background: #e4f0e8; color: #2a6840; padding: 6px 18px; border-radius: 99px; font-size: 14px; font-weight: 600; display: inline-block; }
.pred-none     { background: #ece8e0; color: #777;    padding: 6px 18px; border-radius: 99px; font-size: 14px; font-weight: 600; display: inline-block; }
.prow { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 0.5px solid rgba(0,0,0,0.07); }
.prow:last-child { border-bottom: none; }
.pnum { width: 28px; height: 28px; border-radius: 8px; background: #efe9dc; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: #888; flex-shrink: 0; }
.pnum-hot { background: #fde8e8; color: #a03030; }
.stButton > button {
    background: #1a1a1a !important;
    color: #f5f0e8 !important;
    border: none !important;
    border-radius: 99px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 0.55rem 1.6rem !important;
}
.stButton > button:hover { background: #333 !important; }
.stButton > button:disabled { background: #ccc !important; color: #888 !important; }
.clear-btn > button {
    background: transparent !important;
    color: #999 !important;
    border: 0.5px solid rgba(0,0,0,0.15) !important;
    border-radius: 99px !important;
}
.clear-btn > button:hover { background: #efe9dc !important; color: #555 !important; }
.step { display: flex; align-items: center; gap: 10px; margin-bottom: 1rem; }
.step-num { width: 24px; height: 24px; border-radius: 50%; background: #1a1a1a; color: #f5f0e8; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; flex-shrink: 0; }
.step-text { font-size: 13px; color: #555; }
.success-banner { background: #e4f0e8; border-radius: 12px; padding: 12px 16px; font-size: 13px; color: #2a6840; margin-bottom: 12px; }
.empty { text-align: center; padding: 2rem 1rem; color: #bbb; font-size: 13px; line-height: 2; }
hr { border: none; border-top: 0.5px solid rgba(0,0,0,0.08); margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ── 헬퍼 함수 ─────────────────────────────────────────────────────────────────
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


# ── 탭 구성 ───────────────────────────────────────────────────────────────────
tab_user, tab_admin = st.tabs(["📱 사용자 — 신고하기", "🖥️ 관리자 — 운영 현황"])


# ════════════════════════════════════════════════════════════════════════════════
# 탭 1: 사용자
# ════════════════════════════════════════════════════════════════════════════════
with tab_user:
    st.markdown("<br>", unsafe_allow_html=True)

    col_input, col_result = st.columns([1, 2], gap="medium")

    with col_input:
        st.markdown('<p class="slabel">📥 킥보드 신고</p>', unsafe_allow_html=True)

        st.markdown('<div class="step"><div class="step-num">1</div><div class="step-text">이미지 소스 선택</div></div>', unsafe_allow_html=True)
        input_mode = st.radio("Image source", ["Demo image", "Upload image"], horizontal=True, label_visibility="collapsed")

        st.markdown('<div class="step"><div class="step-num">2</div><div class="step-text">발견 위치 선택</div></div>', unsafe_allow_html=True)
        selected_location = st.selectbox("Location", LOCATIONS, label_visibility="collapsed")

        st.markdown('<div class="step"><div class="step-num">3</div><div class="step-text">이미지 선택 또는 업로드</div></div>', unsafe_allow_html=True)

        image_path = None

        if input_mode == "Demo image":
            demo_images = get_demo_images()
            if demo_images:
                demo_labels = [p.name for p in demo_images]
                selected_label = st.selectbox("Sample image", demo_labels, label_visibility="collapsed")
                image_path = DEMO_DIR / selected_label
                st.image(str(image_path), caption=selected_label, use_container_width=True)
            else:
                st.warning("data/demo_images 폴더에 이미지를 추가해주세요.")
        else:
            uploaded = st.file_uploader("Upload image", type=["jpg","jpeg","png"], label_visibility="collapsed")
            if uploaded:
                image_path = save_uploaded_file(uploaded)
                st.image(Image.open(image_path), caption=uploaded.name, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="step"><div class="step-num">4</div><div class="step-text">신고 제출</div></div>', unsafe_allow_html=True)

        analyze_clicked = st.button("🚨 신고 제출하기", use_container_width=True, disabled=image_path is None)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
            if st.button("↺ 초기화", use_container_width=True):
                st.session_state["events"] = []
                st.session_state["current_event"] = None
                st.session_state["current_detection"] = None
                st.session_state["current_image_path"] = None
                clear_events()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col_result:
        st.markdown('<p class="slabel">🎯 탐지 결과</p>', unsafe_allow_html=True)

        if analyze_clicked and image_path:
            with st.spinner("YOLO 분석 중..."):
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
                    st.error("YOLO 분석 실패")
                    st.exception(e)

        current_event = st.session_state["current_event"]
        current_detection = st.session_state["current_detection"]

        if current_event and current_detection:
            score = current_event.get("violation_score", 0)
            level = current_event.get("level", "-")
            pred = current_event.get("prediction", "none")

            st.markdown(f'<div class="success-banner">✅ 신고 완료 — 이벤트 #{current_event.get("event_id")} 저장됨</div>', unsafe_allow_html=True)

            left, right = st.columns([1, 2])
            with left:
                st.markdown(f"""
                    <div class="score-big">{score}</div>
                    {get_pill(level)}
                    <div style="font-size:12px;color:#aaa;margin-top:6px;">불법 주정차 의심 점수</div>
                    <br>
                    <div class="fbox"><div class="flabel">판정 결과</div><div class="fval">{get_pred_badge(pred)}</div></div>
                    <div class="fbox"><div class="flabel">Confidence</div><div class="fval">{current_event.get('confidence', 0.0):.2f}</div></div>
                    <div class="fbox"><div class="flabel">위치</div><div class="fval">{current_event.get('location', '-')}</div></div>
                    <div class="fbox"><div class="flabel">조치 사항</div><div class="fval">{current_event.get('action', '-')}</div></div>
                """, unsafe_allow_html=True)

            with right:
                bar_col = get_bar_color(score)
                st.markdown(f"""
                    <div class="bar-bg">
                        <div class="bar-fill" style="width:{min(int(score),100)}%;background:{bar_col};"></div>
                    </div>
                """, unsafe_allow_html=True)

                img1, img2 = st.columns(2)
                with img1:
                    st.image(st.session_state["current_image_path"], caption="📷 원본", use_container_width=True)
                with img2:
                    st.image(current_detection["annotated_image"], caption="🎯 YOLO 결과", channels="BGR", use_container_width=True)

                with st.expander("🔬 탐지 상세"):
                    detections = current_detection.get("detections", [])
                    if detections:
                        st.dataframe(pd.DataFrame(detections), use_container_width=True)
                    else:
                        st.info("탐지된 킥보드가 없습니다.")
        else:
            st.markdown("""
                <div class="empty">
                    👈 왼쪽에서 이미지를 선택하고<br>
                    위치를 선택한 후<br>
                    <strong>신고 제출하기</strong>를 눌러주세요
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

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🔍 총 신고 수", total_events)
    m2.metric("⚠️ 불법 주정차 감지", abnormal_events)
    m3.metric("📊 평균 의심 점수", avg_score)
    m4.metric("🔴 고위험", high_priority_count)

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
                            <div style="font-size:13px;font-weight:500;color:#1a1a1a;">{item.get('location','-')}</div>
                            <div style="font-size:11px;color:#aaa;">{item.get('action','-')}</div>
                        </div>
                        {pill}
                        <div style="font-size:14px;font-weight:600;color:#1a1a1a;min-width:36px;text-align:right;">{item.get('violation_score',0)}</div>
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
                    color="#1a1a1a",
                    weight=2,
                    opacity=0.6,
                    dash_array="6"
                ).add_to(m)

            st_folium(m, width=None, height=350, returned_objects=[])

        else:
            st.markdown('<div class="empty">신고 데이터가 없습니다<br>사용자 탭에서 신고를 제출해주세요</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # 통계 차트
    st.markdown('<p class="slabel">📊 통계</p>', unsafe_allow_html=True)
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
        st.markdown('<div class="empty" style="padding:3rem;">신고 데이터가 없습니다</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 이벤트 로그
    st.markdown('<p class="slabel">🗂️ 이벤트 로그</p>', unsafe_allow_html=True)
    if events:
        log_df = pd.DataFrame(events)
        display_columns = ["event_id","timestamp","location","source","prediction","confidence","abnormal_confidence","violation_score","level","action"]
        existing_columns = [col for col in display_columns if col in log_df.columns]
        log_df = log_df[existing_columns]
        log_df["timestamp"] = log_df["timestamp"].str[:19]
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="empty">이벤트 없음</div>', unsafe_allow_html=True)