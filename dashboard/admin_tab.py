import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from branca.element import Element
from folium.plugins import AntPath

from src.route_optimizer import (
    get_priority_list,
    optimize_route,
    get_total_distance,
    LOCATION_COORDS,
)

from src.visualization import (
    plot_detection_ratio,
    plot_events_by_time,
    plot_violation_distribution,
    plot_incidents_by_location,
)


STATUS_OPTIONS = ["확인 대기", "현장 확인 중", "처리 완료"]


def get_score(event):
    try:
        return float(event.get("risk_score", event.get("violation_score", 0)) or 0)
    except (TypeError, ValueError):
        return 0.0


def normalize_status(status):
    if status in ["처리 대기", "대기 중", None, ""]:
        return "확인 대기"
    if status in STATUS_OPTIONS:
        return status
    return "확인 대기"


def get_status(event):
    return normalize_status(event.get("status", "확인 대기"))


def normalize_events(events):
    normalized = []

    for event in events:
        item = dict(event)
        score = get_score(item)

        item["risk_score"] = score
        item["violation_score"] = score
        item["status"] = get_status(item)

        normalized.append(item)

    return normalized


def sync_normalized_events_to_session(events):
    event_map = {
        event.get("event_id"): event
        for event in events
    }

    for event in st.session_state["events"]:
        event_id = event.get("event_id")
        normalized = event_map.get(event_id)

        if normalized:
            event["risk_score"] = normalized.get("risk_score", 0.0)
            event["violation_score"] = normalized.get("violation_score", 0.0)
            event["status"] = normalized.get("status", "확인 대기")


def get_level_filter_value(event):
    level = event.get("level", "")

    if "매우 높음" in level:
        return "매우 높음"
    if "높음" in level:
        return "높음"
    if "낮음" in level:
        return "낮음"
    if "정상" in level:
        return "정상"

    return "기타"


def get_prediction_label(prediction):
    if prediction == "abnormal":
        return "불법 주정차 의심"
    if prediction == "normal":
        return "정상"
    return "감지 실패"


def get_action_text(score):
    if score >= 80:
        return "즉시 확인 및 수거 필요"
    if score >= 50:
        return "현장 확인 및 수거 필요"
    if score >= 30:
        return "모니터링 대상"
    return "정상 가능성 높음"


def get_marker_color(score):
    if score >= 80:
        return "#c0392b"
    if score >= 50:
        return "#d4a017"
    if score >= 30:
        return "#2a7a4a"
    return "#8d97a8"


def apply_filters(events, level_filter, status_filter, location_filter):
    filtered = []

    for event in events:
        if level_filter != "전체" and get_level_filter_value(event) != level_filter:
            continue

        if status_filter != "전체" and get_status(event) != status_filter:
            continue

        if location_filter != "전체" and event.get("location", "-") != location_filter:
            continue

        filtered.append(event)

    return filtered


def update_event_status(event_id, new_status):
    for event in st.session_state["events"]:
        if event.get("event_id") == event_id:
            event["status"] = new_status
            break


def render_score_status(score):
    if score >= 80:
        st.error(f"{score:.1f}점")
    elif score >= 50:
        st.warning(f"{score:.1f}점")
    elif score >= 30:
        st.success(f"{score:.1f}점")
    else:
        st.info(f"{score:.1f}점")


def render_prediction_status(prediction):
    label = get_prediction_label(prediction)

    if prediction == "abnormal":
        st.error(label)
    elif prediction == "normal":
        st.success(label)
    else:
        st.warning(label)


def render_kpi(events):
    total_events = len(events)

    suspicious_events = sum(
        1 for event in events
        if event.get("prediction") == "abnormal"
    )

    pickup_events = sum(
        1 for event in events
        if event.get("prediction") == "abnormal"
        and get_score(event) >= 50
        and get_status(event) != "처리 완료"
    )

    completed_events = sum(
        1 for event in events
        if get_status(event) == "처리 완료"
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("총 신고", total_events)

    with k2:
        st.metric("불법 주정차 의심", suspicious_events)

    with k3:
        st.metric("수거 대상", pickup_events)

    with k4:
        st.metric("처리 완료", completed_events)


def render_filters(events):
    level_options = ["전체", "매우 높음", "높음", "낮음", "정상", "기타"]
    status_options = ["전체"] + STATUS_OPTIONS

    locations = sorted(
        {
            event.get("location", "-")
            for event in events
            if event.get("location")
        }
    )

    location_options = ["전체"] + locations

    f1, f2, f3 = st.columns(3)

    with f1:
        level_filter = st.selectbox("위험 단계", level_options)

    with f2:
        status_filter = st.selectbox("처리 상태", status_options)

    with f3:
        location_filter = st.selectbox("위치", location_options)

    return level_filter, status_filter, location_filter


def render_pickup_list(route):
    st.markdown("### 📋 수거 대상 목록")
    st.caption("위험도 50점 이상 신고를 수거 대상으로 묶고, 현재 위치에서 가까운 순서로 이동 동선을 추천합니다.")

    if not route:
        with st.container(border=True):
            st.info("현재 수거 대상 신고가 없습니다.")
        return

    for item in route[:6]:
        order = item.get("visit_order", "-")
        score = get_score(item)
        location = item.get("location", "-")
        timestamp = str(item.get("timestamp", ""))[11:16]
        status = get_status(item)
        action_text = get_action_text(score)
        distance = item.get("distance_from_prev", 0)

        with st.container(border=True):
            top_col, score_col = st.columns([1.6, 0.5])

            with top_col:
                st.write(f"**#{order} {location}**")
                st.caption(f"{action_text} · 접수 {timestamp} · 이전 지점에서 약 {distance}m")

            with score_col:
                if score >= 80:
                    st.error(f"{score:.1f}점")
                elif score >= 50:
                    st.warning(f"{score:.1f}점")
                else:
                    st.info(f"{score:.1f}점")

            status_col, info_col = st.columns([0.65, 1.35])

            with status_col:
                if status == "처리 완료":
                    st.success("처리 완료")
                elif status == "현장 확인 중":
                    st.warning("확인 중")
                else:
                    st.info("확인 대기")

            with info_col:
                st.caption("상세 화면에서 처리 상태를 변경할 수 있습니다.")


def add_map_legend(map_object):
    legend_html = """
    <div style="
        position: fixed;
        bottom: 26px;
        left: 26px;
        z-index: 9999;
        background: white;
        padding: 12px 14px;
        border-radius: 14px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.18);
        font-size: 12px;
        color: #24324a;
        line-height: 1.7;
    ">
        <div style="font-weight: 800; margin-bottom: 4px;">동선 표시 기준</div>
        <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#c0392b;margin-right:6px;"></span>매우 높음</div>
        <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#d4a017;margin-right:6px;"></span>높음</div>
        <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#4f67d8;margin-right:6px;"></span>시작 지점</div>
    </div>
    """
    map_object.get_root().html.add_child(Element(legend_html))


def render_route_summary(route):
    st.markdown("#### 최적 동선 요약")

    if not route:
        st.info("추천할 수거 위치가 없습니다.")
        return

    for item in route[:5]:
        order = item.get("visit_order", "-")
        location = item.get("location", "-")
        score = get_score(item)
        distance = item.get("distance_from_prev", 0)
        status = get_status(item)
        action_text = get_action_text(score)

        with st.container(border=True):
            c1, c2, c3 = st.columns([0.18, 1.25, 0.45])

            with c1:
                marker_color = get_marker_color(score)
                st.markdown(
                    f"""
                    <div style="
                        width:32px;
                        height:32px;
                        border-radius:50%;
                        background:{marker_color};
                        color:white;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-weight:800;
                        font-size:13px;
                    ">{order}</div>
                    """,
                    unsafe_allow_html=True
                )

            with c2:
                st.write(f"**{location}**")
                st.caption(f"{action_text} · 이전 지점에서 약 {distance}m")

            with c3:
                if status == "처리 완료":
                    st.success("완료")
                elif status == "현장 확인 중":
                    st.warning("확인 중")
                else:
                    st.info("대기")


def render_route_map(route):
    st.markdown("### 🗺️ 최적 동선 추천")
    st.caption("수거 대상 신고를 하나의 그룹으로 묶고, 현재 위치에서 가장 짧게 이동할 수 있는 순서를 추천합니다.")

    if not route:
        with st.container(border=True):
            st.info("지도에 표시할 수거 대상이 없습니다.")
        return

    start_location = "정문 앞"
    start_coords = LOCATION_COORDS.get(start_location, (37.3010, 126.8317))
    total_distance = get_total_distance(route)

    st.caption(f"추천 동선 기준 이동 거리: 약 **{total_distance}m**")
    st.caption("번호가 낮을수록 먼저 수거할 위치입니다.")

    m = folium.Map(
        location=start_coords,
        zoom_start=17,
        tiles="CartoDB positron"
    )

    folium.Marker(
        location=start_coords,
        tooltip="관리 시작 지점",
        popup="관리 시작 지점",
        icon=folium.DivIcon(html="""
            <div style="
                background:#4f67d8;
                color:white;
                width:34px;
                height:34px;
                border-radius:50%;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:16px;
                font-weight:800;
                border:3px solid white;
                box-shadow:0 2px 8px rgba(0,0,0,0.28);
            ">S</div>
        """)
    ).add_to(m)

    for loc, coords in LOCATION_COORDS.items():
        folium.CircleMarker(
            location=coords,
            radius=3,
            color="#b8c0d9",
            fill=True,
            fill_color="#b8c0d9",
            fill_opacity=0.25,
            tooltip=loc
        ).add_to(m)

    route_coords = [start_coords]

    for item in route:
        location = item.get("location")

        if location not in LOCATION_COORDS:
            continue

        coords = LOCATION_COORDS[location]
        score = get_score(item)
        status = get_status(item)
        action_text = get_action_text(score)
        visit_order = item.get("visit_order", len(route_coords))
        marker_color = get_marker_color(score)

        route_coords.append(coords)

        popup_html = f"""
        <div style="font-size:13px;line-height:1.6;">
            <b>#{visit_order} {location}</b><br>
            위험도: <b>{score:.1f}점</b><br>
            조치: {action_text}<br>
            상태: {status}
        </div>
        """

        folium.Marker(
            location=coords,
            tooltip=f"#{visit_order} {location} · 위험도 {score:.1f}점",
            popup=folium.Popup(popup_html, max_width=260),
            icon=folium.DivIcon(html=f"""
                <div style="
                    background:{marker_color};
                    color:white;
                    width:32px;
                    height:32px;
                    border-radius:50%;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:13px;
                    font-weight:800;
                    border:3px solid white;
                    box-shadow:0 2px 8px rgba(0,0,0,0.28);
                ">{visit_order}</div>
            """)
        ).add_to(m)

    if len(route_coords) > 1:
        AntPath(
            locations=route_coords,
            color="#4f67d8",
            weight=4,
            opacity=0.75,
            delay=900,
            dash_array=[12, 18],
            pulse_color="#24324a"
        ).add_to(m)

        folium.PolyLine(
            locations=route_coords,
            color="#24324a",
            weight=2,
            opacity=0.35
        ).add_to(m)

    add_map_legend(m)

    if len(route_coords) > 1:
        m.fit_bounds(route_coords)

    st_folium(
        m,
        width=None,
        height=430,
        returned_objects=[]
    )

    render_route_summary(route)


def get_event_label(event):
    event_id = event.get("event_id", "-")
    location = event.get("location", "-")
    score = get_score(event)
    timestamp = str(event.get("timestamp", ""))[:16]

    return f"#{event_id} · {location} · {score:.1f}점 · {timestamp}"


def render_selected_event_detail(events):
    st.markdown("### 🔎 선택 신고 상세")

    if not events:
        with st.container(border=True):
            st.info("상세 확인할 신고가 없습니다.")
        return

    sorted_events = sorted(
        events,
        key=lambda x: x.get("event_id", 0),
        reverse=True
    )

    labels = [get_event_label(event) for event in sorted_events]
    selected_label = st.selectbox("상세 확인할 신고 선택", labels)

    selected_event = sorted_events[labels.index(selected_label)]
    event_id = selected_event.get("event_id")
    score = get_score(selected_event)
    prediction = selected_event.get("prediction", "-")
    location = selected_event.get("location", "-")
    timestamp = str(selected_event.get("timestamp", ""))[:19]
    action = selected_event.get("action", "-")
    level = selected_event.get("level", "-")
    image_path = selected_event.get("image_path")

    current_event = st.session_state.get("current_event")
    current_detection = st.session_state.get("current_detection")

    with st.container(border=True):
        img_col, info_col = st.columns([1.05, 1], gap="large")

        with img_col:
            displayed = False

            if current_event and current_event.get("event_id") == event_id and current_detection:
                annotated_image = current_detection.get("annotated_image")

                if annotated_image is not None:
                    st.image(
                        annotated_image,
                        caption="AI 탐지 결과",
                        use_container_width=True,
                        channels="BGR"
                    )
                    displayed = True

            if not displayed and image_path:
                try:
                    st.image(
                        image_path,
                        caption="신고 이미지",
                        use_container_width=True
                    )
                    displayed = True
                except Exception:
                    pass

            if not displayed:
                st.info("표시할 이미지가 없습니다.")

        with info_col:
            st.write(f"**신고 ID**: #{event_id}")
            st.write(f"**신고 시간**: {timestamp}")
            st.write(f"**신고 위치**: {location}")
            st.write(f"**위험 단계**: {level}")

            st.write("**분석 결과**")
            render_prediction_status(prediction)

            st.write("**위험도 점수**")
            render_score_status(score)

            st.write("**권장 조치**")
            if score >= 80:
                st.error(action)
            elif score >= 50:
                st.warning(action)
            elif score >= 30:
                st.success(action)
            else:
                st.info(action)

            current_status = get_status(selected_event)
            current_index = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0

            new_status = st.selectbox(
                "처리 상태 변경",
                STATUS_OPTIONS,
                index=current_index,
                key=f"status_select_{event_id}"
            )

            if st.button("처리 상태 저장", use_container_width=True, key=f"save_status_{event_id}"):
                update_event_status(event_id, new_status)
                st.success(f"#{event_id} 신고의 처리 상태가 `{new_status}`로 변경되었습니다.")
                st.rerun()


def render_statistics(events):
    st.markdown("### 📊 상세 통계")

    if not events:
        with st.container(border=True):
            st.info("통계로 표시할 신고 데이터가 없습니다.")
        return

    with st.expander("상세 통계 보기", expanded=False):
        ch1, ch2 = st.columns(2, gap="medium")

        with ch1:
            fig = plot_incidents_by_location(events)
            fig.update_traces(width=0.35)
            fig.update_layout(
                height=300,
                bargap=0.55,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        with ch2:
            fig = plot_events_by_time(events)
            fig.update_traces(width=0.35)
            fig.update_layout(
                height=300,
                bargap=0.55,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        ch3, ch4 = st.columns(2, gap="medium")

        with ch3:
            fig = plot_violation_distribution(events)
            fig.update_layout(
                height=300,
                bargap=0.55,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        with ch4:
            fig = plot_detection_ratio(events)
            fig.update_layout(
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)


def render_event_log(events):
    st.markdown("### 🗂️ 전체 신고 내역")

    if not events:
        with st.container(border=True):
            st.info("전체 신고 내역이 없습니다.")
        return

    rows = []

    for event in events:
        rows.append({
            "ID": event.get("event_id", "-"),
            "신고 시간": str(event.get("timestamp", ""))[:19],
            "위치": event.get("location", "-"),
            "분석 결과": get_prediction_label(event.get("prediction", "-")),
            "위험도": get_score(event),
            "위험 단계": event.get("level", "-"),
            "권장 조치": event.get("action", "-"),
            "처리 상태": get_status(event),
        })

    df = pd.DataFrame(rows)

    if not df.empty and "ID" in df.columns:
        df = df.sort_values(by="ID", ascending=False)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


def render():
    st.markdown("<br>", unsafe_allow_html=True)

    if "events" not in st.session_state:
        st.session_state["events"] = []

    events = normalize_events(st.session_state["events"])
    sync_normalized_events_to_session(events)

    st.markdown("### 🖥️ 신고 관리")

    render_kpi(events)

    st.markdown("---")

    st.markdown("### 🔍 신고 필터")

    level_filter, status_filter, location_filter = render_filters(events)
    filtered_events = apply_filters(events, level_filter, status_filter, location_filter)

    active_events = [
        event for event in filtered_events
        if get_status(event) != "처리 완료"
    ]

    pickup_targets = get_priority_list(active_events)
    route = optimize_route(pickup_targets)

    st.markdown("---")

    list_col, map_col = st.columns([0.9, 1.35], gap="large")

    with list_col:
        render_pickup_list(route)

    with map_col:
        render_route_map(route)

    st.markdown("---")

    render_selected_event_detail(filtered_events)

    st.markdown("---")

    render_statistics(filtered_events)

    st.markdown("---")

    render_event_log(filtered_events)