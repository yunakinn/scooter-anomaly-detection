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


ROOT = Path("/data1/workspaces/tp2026/scooter-anomaly-detection")
DEMO_DIR = ROOT / "data/demo_images"


st.set_page_config(
    page_title="Scooter Violation Detection",
    page_icon="🛴",
    layout="wide"
)


st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
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


@st.cache_resource
def load_detector():
    return Detector()


def get_demo_images():
    if not DEMO_DIR.exists():
        return []

    exts = {".jpg", ".jpeg", ".png"}
    return sorted([
        p for p in DEMO_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in exts
    ])


def save_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    temp.write(uploaded_file.getbuffer())
    temp.close()

    return Path(temp.name)


if "events" not in st.session_state:
    st.session_state["events"] = []

if "current_event" not in st.session_state:
    st.session_state["current_event"] = None

if "current_detection" not in st.session_state:
    st.session_state["current_detection"] = None

if "current_image_path" not in st.session_state:
    st.session_state["current_image_path"] = None


scorer = RiskScorer()


col_title, col_badge = st.columns([5, 1])

with col_title:
    st.markdown("## 🛴 YOLO-based Scooter Illegal Parking Detection")
    st.caption("Object Detection Dashboard — Hanyang University ERICA Campus")

with col_badge:
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("● Demo")

st.divider()


events = st.session_state["events"]

total_events = len(events)
abnormal_events = sum(1 for e in events if e.get("prediction") == "abnormal")
high_priority_events = sum(1 for e in events if e.get("violation_score", 0) >= 80)
avg_score = round(
    sum(e.get("violation_score", 0) for e in events) / total_events,
    1
) if total_events else 0.0

m1, m2, m3, m4 = st.columns(4)

m1.metric("Total analyzed", total_events)
m2.metric("Abnormal detected", abnormal_events)
m3.metric("Avg suspicion score", avg_score)
m4.metric("High priority", high_priority_events)

st.markdown("<br>", unsafe_allow_html=True)


col_input, col_result = st.columns([1, 2])

with col_input:
    st.markdown('<p class="section-header">Input</p>', unsafe_allow_html=True)

    input_mode = st.radio(
        "Image source",
        ["Demo image", "Upload image"],
        horizontal=True
    )

    selected_location = st.selectbox(
        "Detection location",
        LOCATIONS
    )

    image_path = None

    if input_mode == "Demo image":
        demo_images = get_demo_images()

        if demo_images:
            demo_labels = [str(p.relative_to(ROOT)) for p in demo_images]
            selected_label = st.selectbox("Select sample image", demo_labels)
            image_path = ROOT / selected_label

            st.image(str(image_path), caption="Selected demo image", use_container_width=True)
        else:
            st.warning("No demo images found in data/demo_images.")

    else:
        uploaded = st.file_uploader(
            "Upload scooter image",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded:
            image_path = save_uploaded_file(uploaded)
            st.image(Image.open(image_path), caption="Uploaded image", use_container_width=True)

    analyze_clicked = st.button(
        "Run YOLO Detection",
        use_container_width=True,
        disabled=image_path is None
    )

    if st.button("Clear dashboard events", use_container_width=True):
        st.session_state["events"] = []
        st.session_state["current_event"] = None
        st.session_state["current_detection"] = None
        st.session_state["current_image_path"] = None
        clear_events()
        st.rerun()


with col_result:
    st.markdown('<p class="section-header">YOLO Detection Result</p>', unsafe_allow_html=True)

    if analyze_clicked and image_path:
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

    current_event = st.session_state["current_event"]
    current_detection = st.session_state["current_detection"]

    if current_event and current_detection:
        r1, r2, r3, r4 = st.columns(4)

        r1.metric("Prediction", current_event.get("prediction", "none"))
        r2.metric("Confidence", f"{current_event.get('confidence', 0.0):.2f}")
        r3.metric("Suspicion score", current_event.get("violation_score", 0.0))
        r4.metric("Level", current_event.get("level", "-"))

        st.progress(min(int(current_event.get("violation_score", 0)), 100) / 100)
        st.markdown(f"**Recommended action:** {current_event.get('action', '-')}")

        img_col1, img_col2 = st.columns(2)

        with img_col1:
            st.image(
                st.session_state["current_image_path"],
                caption="Input image",
                use_container_width=True
            )

        with img_col2:
            st.image(
                current_detection["annotated_image"],
                caption="YOLO bounding box result",
                channels="BGR",
                use_container_width=True
            )

        with st.expander("Detection details"):
            detections = current_detection.get("detections", [])
            if detections:
                st.dataframe(pd.DataFrame(detections), use_container_width=True)
            else:
                st.info("No scooter was detected.")

    else:
        st.info("Select or upload an image, then run YOLO detection.")


st.markdown("<br>", unsafe_allow_html=True)


col_priority, col_route = st.columns(2)

with col_priority:
    st.markdown('<p class="section-header">Collection Priority</p>', unsafe_allow_html=True)

    priority = get_priority_list(events)

    if priority:
        priority_df = pd.DataFrame(priority)[
            ["event_id", "timestamp", "location", "prediction", "confidence", "violation_score", "level", "action"]
        ]
        priority_df["timestamp"] = priority_df["timestamp"].str[:19]
        st.dataframe(priority_df, use_container_width=True)
    else:
        st.info("No abnormal detection events yet.")

with col_route:
    st.markdown('<p class="section-header">Route Optimization</p>', unsafe_allow_html=True)

    route = optimize_route(priority)
    total_distance = get_total_distance(route)

    if route:
        st.caption(f"Total route distance: **{total_distance} m**")

        route_df = pd.DataFrame(route)[
            ["visit_order", "location", "violation_score", "level", "distance_from_prev", "action"]
        ]
        st.dataframe(route_df, use_container_width=True)

        for item in route:
            st.markdown(
                f"**#{item['visit_order']} {item['location']}**  \n"
                f"Suspicion score: `{item['violation_score']}` / "
                f"Move: `{item['distance_from_prev']} m` / "
                f"{item['action']}"
            )
            st.divider()
    else:
        st.info("No route recommendation available yet.")


st.markdown("<br>", unsafe_allow_html=True)


st.markdown('<p class="section-header">Analytics</p>', unsafe_allow_html=True)

if events:
    ch1, ch2 = st.columns(2)

    with ch1:
        st.plotly_chart(plot_detection_ratio(events), use_container_width=True)

    with ch2:
        st.plotly_chart(plot_events_by_time(events), use_container_width=True)

    ch3, ch4 = st.columns(2)

    with ch3:
        st.plotly_chart(plot_violation_distribution(events), use_container_width=True)

    with ch4:
        st.plotly_chart(plot_incidents_by_location(events), use_container_width=True)
else:
    st.info("Run at least one detection to see analytics charts.")


st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="section-header">Event Log</p>', unsafe_allow_html=True)

if events:
    log_df = pd.DataFrame(events)

    display_columns = [
        "event_id",
        "timestamp",
        "location",
        "source",
        "prediction",
        "confidence",
        "abnormal_confidence",
        "violation_score",
        "level",
        "action",
        "image_path"
    ]

    existing_columns = [
        col for col in display_columns
        if col in log_df.columns
    ]

    log_df = log_df[existing_columns]
    log_df["timestamp"] = log_df["timestamp"].str[:19]

    st.dataframe(log_df, use_container_width=True)
else:
    st.info("No events logged yet.")
