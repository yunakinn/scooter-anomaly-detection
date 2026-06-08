from pathlib import Path
from datetime import datetime
import hashlib

import streamlit as st

from src.detector import Detector
from src.risk_scorer import RiskScorer
from src.event_system import LOCATIONS, create_detection_event


ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = ROOT / "data/uploaded_images"


def save_uploaded_file(uploaded_file):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.md5(file_bytes).hexdigest()[:10]
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


def render_result_summary(prediction):
    if prediction == "abnormal":
        st.warning("불법 주정차 의심 상태로 접수되었습니다.")
        st.write("관리자가 신고 위치와 이미지를 확인한 뒤 필요한 조치를 진행합니다.")
    elif prediction == "normal":
        st.success("정상 주차 가능성이 높은 상태로 분석되었습니다.")
        st.write("신고 내용은 기록되며, 필요 시 관리자가 확인할 수 있습니다.")
    else:
        st.warning("전동킥보드를 명확하게 감지하지 못했습니다.")
        st.write("사진이 흐리거나 대상이 작게 보이면 다른 사진으로 다시 신고해주세요.")


def render(scorer: RiskScorer):
    st.markdown("<br>", unsafe_allow_html=True)

    default_states = {
        "events": [],
        "current_event": None,
        "current_detection": None,
        "current_image_path": None,
        "report_submitted": False,
        "uploaded_file_hash": None,
        "uploaded_image_path": None,
        "upload_key": 0,
    }

    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

    left, right = st.columns([1.05, 1.15], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<p class="slabel">📥 킥보드 신고</p>', unsafe_allow_html=True)

            if st.session_state.get("report_submitted"):
                st.success("신고가 접수되었습니다. 오른쪽에서 AI 탐지 결과를 확인할 수 있습니다.")
                st.session_state["report_submitted"] = False

            st.markdown(
                '<div class="step"><div class="step-num">1</div><div class="step-text">사진 등록</div></div>',
                unsafe_allow_html=True
            )

            st.caption("신고할 전동킥보드 사진을 업로드해주세요.")

            uploaded_file = st.file_uploader(
                "신고 이미지 업로드",
                type=["jpg", "jpeg", "png"],
                key=f"report_uploader_{st.session_state['upload_key']}",
                label_visibility="collapsed"
            )

            image_path = None

            if uploaded_file:
                file_bytes = uploaded_file.getvalue()
                current_hash = hashlib.md5(file_bytes).hexdigest()[:10]

                if st.session_state["uploaded_file_hash"] != current_hash:
                    saved_path, saved_hash = save_uploaded_file(uploaded_file)

                    st.session_state["uploaded_file_hash"] = saved_hash
                    st.session_state["uploaded_image_path"] = str(saved_path)

                    clear_previous_result_for_new_image()

                image_path = Path(st.session_state["uploaded_image_path"])

                st.image(
                    str(image_path),
                    caption=uploaded_file.name,
                    use_container_width=True
                )
            else:
                st.info("신고할 사진을 업로드하면 미리보기가 표시됩니다.")

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                '<div class="step"><div class="step-num">2</div><div class="step-text">위치 선택</div></div>',
                unsafe_allow_html=True
            )

            st.caption("전동킥보드를 발견한 위치를 직접 선택해주세요.")

            selected_location = st.selectbox(
                "위치",
                LOCATIONS,
                label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                '<div class="step"><div class="step-num">3</div><div class="step-text">AI 탐지 및 신고 제출</div></div>',
                unsafe_allow_html=True
            )

            analyze_clicked = st.button(
                "AI 탐지 후 신고 제출",
                use_container_width=True,
                disabled=image_path is None
            )

            if analyze_clicked and image_path:
                with st.spinner("AI가 전동킥보드 주차 상태를 분석하고 있습니다..."):
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
                            source="사진 업로드",
                            detection_result=detection_result,
                            score_result=score_result,
                            existing_events=st.session_state["events"]
                        )

                        st.session_state["events"].append(event)
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
                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("새 신고 작성", use_container_width=True):
                    reset_current_report()
                    st.rerun()

    with right:
        st.markdown("### 🤖 AI 탐지 결과")

        current_detection = st.session_state.get("current_detection")
        current_event = st.session_state.get("current_event")
        current_image_path = st.session_state.get("current_image_path")

        if current_detection:
            annotated_image = current_detection.get("annotated_image")

            if annotated_image is not None:
                st.image(
                    annotated_image,
                    caption="AI가 감지한 전동킥보드 영역",
                    use_container_width=True,
                    channels="BGR"
                )
            elif current_image_path:
                st.image(
                    current_image_path,
                    caption="업로드된 이미지",
                    use_container_width=True
                )
                st.warning("AI 탐지 이미지를 불러오지 못했습니다.")

            prediction = current_detection.get("prediction", "-")

            if current_event:
                location = current_event.get("location", "-")
            else:
                location = "-"

            st.markdown("#### 신고 결과 요약")
            render_result_summary(prediction)

            st.markdown("#### 신고 위치")
            st.info(location)

            st.markdown("#### 접수 안내")
            st.info("신고가 접수되었습니다. 관리자가 이미지와 위치를 확인한 뒤 필요한 조치를 진행합니다.")

        else:
            with st.container(border=True):
                st.info("왼쪽에서 사진을 등록하고 위치를 선택한 뒤 신고를 제출하면 AI 탐지 결과가 여기에 표시됩니다.")
                st.write("업로드된 사진은 AI 모델을 통해 정상 주차 또는 불법 주정차 의심 상태로 분석됩니다.")
                st.write("신고가 접수되면 관리자가 이미지와 위치를 확인합니다.")