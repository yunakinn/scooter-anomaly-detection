from pathlib import Path
from datetime import datetime
import hashlib

from src.report_state import report_key, is_duplicate_report

import streamlit as st

from src.detector import Detector
from src.risk_scorer import RiskScorer
from src.event_system import LOCATIONS, create_detection_event
from dashboard.ui_components import (
    render_detection_result_card,
    render_empty_state,
    render_image_caption,
    render_section_heading,
    render_detection_header,
)


ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = ROOT / "data/uploaded_images"


def save_uploaded_file(uploaded_file):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix not in [".jpg", ".jpeg", ".png"]:
        suffix = ".jpg"

    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_hash}{suffix}"
    save_path = UPLOAD_DIR / filename

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    return save_path, file_hash


@st.cache_resource
def load_detector():
    return Detector()


def reset_current_report():
    st.session_state["current_event"] = None
    st.session_state["current_detection"] = None
    st.session_state["current_image_path"] = None
    st.session_state["report_submitted"] = False
    st.session_state["uploaded_file_hash"] = None
    st.session_state["uploaded_image_path"] = None
    st.session_state["upload_key"] += 1


def clear_previous_result_for_new_image():
    st.session_state["current_event"] = None
    st.session_state["current_detection"] = None
    st.session_state["current_image_path"] = None
    st.session_state["report_submitted"] = False


def get_result_copy(prediction):
    if prediction == "abnormal":
        return (
            "danger",
            "불법 주정차 의심",
            "현장 확인 대상으로 등록되었습니다.",
        )
    if prediction == "normal":
        return (
            "success",
            "정상 주차 가능성 높음",
            "접수 내역에 기록되었습니다.",
        )
    return (
        "warning",
        "감지 결과 확인 필요",
        "대상이 작거나 흐리면 다른 사진으로 다시 접수해주세요.",
    )


def render(scorer: RiskScorer):
    default_states = {
        "events": [],
        "current_event": None,
        "current_detection": None,
        "current_image_path": None,
        "report_submitted": False,
        "uploaded_file_hash": None,
        "uploaded_image_path": None,
        "upload_key": 0,
        "submitted_report_keys": set(),
    }

    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

    left, right = st.columns([1.05, 1.15], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<p class="slabel">신고 접수</p>', unsafe_allow_html=True)

            st.markdown(
                '<div class="step"><div class="step-num">1</div><div class="step-text">사진 업로드</div></div>',
                unsafe_allow_html=True
            )

            st.caption("전동킥보드와 주변 보행 공간이 함께 보이는 사진을 올려주세요.")

            uploaded_file = st.file_uploader(
                "신고 이미지 업로드",
                type=["jpg", "jpeg", "png"],
                key=f"report_uploader_{st.session_state['upload_key']}",
                label_visibility="collapsed"
            )

            image_path = None

            if uploaded_file:
                file_bytes = uploaded_file.getvalue()
                current_hash = hashlib.sha256(file_bytes).hexdigest()

                if st.session_state["uploaded_file_hash"] != current_hash:
                    saved_path, saved_hash = save_uploaded_file(uploaded_file)

                    st.session_state["uploaded_file_hash"] = saved_hash
                    st.session_state["uploaded_image_path"] = str(saved_path)

                    clear_previous_result_for_new_image()

                image_path = Path(st.session_state["uploaded_image_path"])

                st.image(
                    str(image_path),
                    caption=uploaded_file.name,
                    width="stretch"
                )
            else:
                st.info("사진을 업로드하면 이곳에 미리보기가 표시됩니다.")

            st.markdown(
                '<div class="step"><div class="step-num">2</div><div class="step-text">발견 위치</div></div>',
                unsafe_allow_html=True
            )

            st.caption("신고 위치와 가장 가까운 건물을 선택해주세요.")

            selected_location = st.selectbox(
                "위치",
                LOCATIONS,
                label_visibility="collapsed"
            )

            st.markdown(
                '<div class="step"><div class="step-num">3</div><div class="step-text">분석 및 제출</div></div>',
                unsafe_allow_html=True
            )

            submission_key = report_key(st.session_state.get("uploaded_file_hash"), selected_location)
            duplicate = is_duplicate_report(submission_key, st.session_state["submitted_report_keys"])
            if duplicate:
                st.info("같은 사진과 위치로 이미 접수한 신고가 있습니다.")

            analyze_clicked = st.button(
                "신고 접수하기",
                width="stretch",
                disabled=image_path is None or duplicate,
                type="primary",
            )

            if analyze_clicked and image_path and not duplicate:
                with st.spinner("YOLO 모델이 전동킥보드 영역을 탐지하고 있습니다..."):
                    try:
                        detector = load_detector()
                        detection_result = detector.predict(image_path)

                        score_result = scorer.score(
                            abnormal_confidence=detection_result.get("abnormal_confidence", 0.0),
                            detections=detection_result.get("detections", []),
                            prediction=detection_result.get("prediction", "none")
                        )

                        event = create_detection_event(
                            image_path=image_path,
                            location=selected_location,
                            source="사진 업로드",
                            detection_result=detection_result,
                            score_result=score_result,
                            existing_events=st.session_state["events"]
                        )

                        st.session_state["events"].append(event)
                        st.session_state["submitted_report_keys"].add(submission_key)
                        st.session_state["current_event"] = event
                        st.session_state["current_detection"] = detection_result
                        st.session_state["current_image_path"] = str(image_path)
                        st.session_state["report_submitted"] = True

                        st.rerun()

                    except Exception as e:
                        st.error("신고 처리 중 오류가 발생했습니다. 모델 경로 또는 이미지 파일을 확인해주세요.")
                        with st.expander("개발자 오류 상세"):
                            st.exception(e)

            if st.session_state.get("current_detection"):
                if st.button("다시 접수하기", width="stretch", type="secondary"):
                    reset_current_report()
                    st.rerun()

    with right:
        render_section_heading(
            "AI 탐지 결과",
            "분석된 이미지와 최종 판정을 확인합니다.",
        )

        current_detection = st.session_state.get("current_detection")
        current_event = st.session_state.get("current_event")
        current_image_path = st.session_state.get("current_image_path")

        if current_detection:
            annotated_image = current_detection.get("annotated_image")
            confidence = float(current_detection.get("confidence", 0.0) or 0.0)

            render_detection_header(confidence)

            if annotated_image is not None:
                st.image(
                    annotated_image,
                    width="stretch",
                    channels="BGR"
                )
                render_image_caption("분석된 전동킥보드 영역")
            elif current_image_path:
                st.image(
                    current_image_path,
                    width="stretch"
                )
                render_image_caption("업로드된 이미지")
                st.warning("AI 탐지 이미지를 불러오지 못했습니다.")

            prediction = current_detection.get("prediction", "-")

            if current_event:
                location = current_event.get("location", "-")
            else:
                location = "-"

            result_status, result_title, result_description = get_result_copy(prediction)
            render_detection_result_card(
                result_status,
                result_title,
                result_description,
                location,
            )

        else:
            render_empty_state(
                "아직 분석 결과가 없습니다.",
                "사진과 위치를 입력한 뒤 신고를 제출하면 탐지 결과와 접수 정보가 표시됩니다.",
            )
