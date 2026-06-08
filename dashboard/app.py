import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.risk_scorer import RiskScorer
from dashboard.styles import get_styles
from dashboard import user_tab, admin_tab


st.set_page_config(
    page_title="전동킥보드 불법 주정차 탐지 시스템",
    page_icon="🛴",
    layout="wide"
)

st.markdown(get_styles(), unsafe_allow_html=True)


def get_demo_events():
    return [
        {
            "event_id": 1,
            "timestamp": "2026-06-08 08:12:34",
            "location": "경상관 앞",
            "source": "데모",
            "prediction": "abnormal",
            "confidence": 0.94,
            "abnormal_confidence": 0.94,
            "risk_score": 94.0,
            "violation_score": 94.0,
            "level": "매우 높음 🔴",
            "action": "즉시 확인 및 수거 필요",
            "status": "확인 대기",
            "detections": []
        },
        {
            "event_id": 2,
            "timestamp": "2026-06-08 09:05:21",
            "location": "제4공학관 앞",
            "source": "데모",
            "prediction": "abnormal",
            "confidence": 0.88,
            "abnormal_confidence": 0.88,
            "risk_score": 88.0,
            "violation_score": 88.0,
            "level": "매우 높음 🔴",
            "action": "즉시 확인 및 수거 필요",
            "status": "확인 대기",
            "detections": []
        },
        {
            "event_id": 3,
            "timestamp": "2026-06-08 09:45:10",
            "location": "셔틀콕 앞",
            "source": "데모",
            "prediction": "abnormal",
            "confidence": 0.76,
            "abnormal_confidence": 0.76,
            "risk_score": 76.0,
            "violation_score": 76.0,
            "level": "높음 🟡",
            "action": "현장 확인 필요",
            "status": "현장 확인 중",
            "detections": []
        },
        {
            "event_id": 4,
            "timestamp": "2026-06-08 10:22:48",
            "location": "제2과학기술관 앞",
            "source": "데모",
            "prediction": "abnormal",
            "confidence": 0.82,
            "abnormal_confidence": 0.82,
            "risk_score": 82.0,
            "violation_score": 82.0,
            "level": "매우 높음 🔴",
            "action": "즉시 확인 및 수거 필요",
            "status": "확인 대기",
            "detections": []
        },
        {
            "event_id": 5,
            "timestamp": "2026-06-08 11:10:05",
            "location": "본관 앞",
            "source": "데모",
            "prediction": "normal",
            "confidence": 0.91,
            "abnormal_confidence": 0.0,
            "risk_score": 0.0,
            "violation_score": 0.0,
            "level": "정상 ⚪",
            "action": "정상 주차 가능성 높음",
            "status": "처리 완료",
            "detections": []
        },
        {
            "event_id": 6,
            "timestamp": "2026-06-08 12:33:17",
            "location": "제1공학관 앞",
            "source": "데모",
            "prediction": "abnormal",
            "confidence": 0.65,
            "abnormal_confidence": 0.65,
            "risk_score": 65.0,
            "violation_score": 65.0,
            "level": "높음 🟡",
            "action": "현장 확인 필요",
            "status": "확인 대기",
            "detections": []
        },
        {
            "event_id": 7,
            "timestamp": "2026-06-08 13:55:42",
            "location": "언론정보관 앞",
            "source": "데모",
            "prediction": "normal",
            "confidence": 0.89,
            "abnormal_confidence": 0.0,
            "risk_score": 0.0,
            "violation_score": 0.0,
            "level": "정상 ⚪",
            "action": "정상 주차 가능성 높음",
            "status": "처리 완료",
            "detections": []
        },
        {
            "event_id": 8,
            "timestamp": "2026-06-08 14:20:09",
            "location": "제5공학관 앞",
            "source": "데모",
            "prediction": "abnormal",
            "confidence": 0.71,
            "abnormal_confidence": 0.71,
            "risk_score": 71.0,
            "violation_score": 71.0,
            "level": "높음 🟡",
            "action": "현장 확인 필요",
            "status": "현장 확인 중",
            "detections": []
        },
    ]


@st.cache_resource
def load_scorer():
    return RiskScorer()


if "events" not in st.session_state:
    st.session_state["events"] = get_demo_events()

for key in ["current_event", "current_detection", "current_image_path"]:
    if key not in st.session_state:
        st.session_state[key] = None

scorer = load_scorer()

st.markdown("""
<div class="page-header">
    <div>
        <p class="page-title">🛴 전동킥보드 불법 주정차 탐지 시스템</p>
        <p class="page-subtitle">AI 기반 신고 분석 및 동선 최적화 서비스</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

tab_user, tab_admin = st.tabs(["📱 신고하기", "🖥️ 신고 관리"])

with tab_user:
    user_tab.render(scorer)

with tab_admin:
    admin_tab.render()