import streamlit as st
import folium
from streamlit_folium import st_folium
from branca.element import Element
from folium.plugins import AntPath

from dashboard.map_tiles import add_base_tiles
from dashboard.ui_components import (
    escape,
    render_admin_heading,
    render_event_detail_card,
    render_filter_panel,
    render_kpi_card,
    render_pickup_card,
    render_route_summary,
    render_subsection_title,
    score_badge,
    status_badge,
)
from src.route_optimizer import (
    get_priority_list,
    optimize_route,
    get_total_distance,
    LOCATION_COORDS,
    START_LOCATION,
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

    cards = [
        ("전체 신고", total_events, "누적 접수 건수"),
        ("의심 신고", suspicious_events, "AI가 이상 상태로 판단"),
        ("수거 대상", pickup_events, "현장 조치가 필요한 건"),
        ("처리 완료", completed_events, "조치가 완료된 신고"),
    ]

    for col, (label, value, caption) in zip([k1, k2, k3, k4], cards):
        with col:
            render_kpi_card(label, value, caption)


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

    render_filter_panel(
        "신고 필터",
        "위험 단계, 처리 상태, 위치를 기준으로 목록과 지도 표시 대상을 좁힙니다.",
    )

    f1, f2, f3 = st.columns(3, gap="medium")

    with f1:
        level_filter = st.selectbox("위험 단계", level_options)

    with f2:
        status_filter = st.selectbox("처리 상태", status_options)

    with f3:
        location_filter = st.selectbox("위치", location_options)

    return level_filter, status_filter, location_filter


def render_pickup_list(route):
    render_admin_heading(
        "📋 수거 대상 목록 및 동선 요약",
        "위험도 50점 이상 신고를 기준으로 추천 수거 순서와 이동 정보를 정리합니다.",
    )

    if not route:
        with st.container(border=True):
            st.info("현재 수거 대상 신고가 없습니다.")
        return

    total_distance = get_total_distance(route)

    route_text = " → ".join(
        [
            f"{item.get('visit_order', '-')}. {item.get('location', '-')}"
            for item in route
        ]
    )

    render_route_summary(len(route), route_text)

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric("수거 대상", f"{len(route)}건")

    with s2:
        st.metric("예상 이동 거리", f"{total_distance}m")

    with s3:
        first_location = route[0].get("location", "-") if route else "-"
        st.metric("첫 수거 위치", first_location)

    render_subsection_title("수거 대상 상세")

    for item in route[:6]:
        order = item.get("visit_order", "-")
        score = get_score(item)
        location = item.get("location", "-")
        timestamp = str(item.get("timestamp", ""))[11:16]
        status = get_status(item)
        action_text = get_action_text(score)
        distance = item.get("distance_from_prev", 0)

        render_pickup_card(
            order,
            location,
            score_badge(score),
            action_text,
            timestamp,
            distance,
            status_badge(status),
        )


def add_map_legend(map_object):
    legend_html = """
    <div style="
        position: fixed;
        bottom: 26px;
        left: 26px;
        z-index: 9999;
        background: white;
        padding: 12px 14px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.16);
        font-size: 12px;
        color: #24324a;
        line-height: 1.7;
    ">
        <div style="font-weight: 800; margin-bottom: 4px;">마커 기준</div>
        <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#c0392b;margin-right:6px;"></span>매우 높음</div>
        <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#d4a017;margin-right:6px;"></span>높음</div>
        <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#4f67d8;margin-right:6px;"></span>시작 지점</div>
    </div>
    """
    map_object.get_root().html.add_child(Element(legend_html))


def render_route_map(route):
    render_admin_heading(
        "🗺️ 최적 동선 추천",
        "수거 대상 신고를 지도에 표시하고, 이동 거리가 짧은 순서로 연결합니다.",
    )

    if not route:
        with st.container(border=True):
            st.info("지도에 표시할 수거 대상이 없습니다.")
        return

    start_coords = LOCATION_COORDS.get(START_LOCATION, (37.2995, 126.8334))
    total_distance = get_total_distance(route)

    st.markdown(
        f'<div class="map-note">추천 이동 거리 약 <strong>{total_distance}m</strong> · 번호가 낮을수록 먼저 방문할 위치입니다.</div>',
        unsafe_allow_html=True
    )

    m = folium.Map(
        location=start_coords,
        zoom_start=17,
        tiles=None
    )
    add_base_tiles(m)

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
                box-sizing:border-box;
                border-radius:50%;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:16px;
                font-weight:800;
                border:3px solid white;
                box-shadow:0 2px 8px rgba(0,0,0,0.28);
            ">S</div>
        """, icon_size=(34, 34), icon_anchor=(17, 17), class_name="route-div-icon")
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
            <b>#{escape(visit_order)} {escape(location)}</b><br>
            위험도: <b>{score:.1f}점</b><br>
            조치: {escape(action_text)}<br>
            상태: {escape(status)}
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
                    box-sizing:border-box;
                    border-radius:50%;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:13px;
                    font-weight:800;
                    border:3px solid white;
                    box-shadow:0 2px 8px rgba(0,0,0,0.28);
                ">{visit_order}</div>
            """, icon_size=(32, 32), icon_anchor=(16, 16), class_name="route-div-icon")
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


def get_event_label(event):
    event_id = event.get("event_id", "-")
    location = event.get("location", "-")
    score = get_score(event)
    timestamp = str(event.get("timestamp", ""))[:16]

    return f"#{event_id} · {location} · {score:.1f}점 · {timestamp}"


def render_selected_event_detail(events):
    render_admin_heading(
        "🔎 선택 신고 상세",
        "개별 신고의 이미지, 분석 결과, 처리 상태를 확인합니다.",
    )

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
    status = get_status(selected_event)

    if image_path:
        try:
            st.image(
                image_path,
                caption="신고 이미지",
                width="stretch"
            )
        except Exception:
            st.info("표시할 이미지가 없습니다.")
    else:
        st.info("표시할 이미지가 없습니다.")

    prediction_label = get_prediction_label(prediction)
    render_event_detail_card(
        location,
        event_id,
        timestamp,
        [
            ("분석 결과", escape(prediction_label)),
            ("위험 단계", escape(level)),
            ("위험도 점수", score_badge(score)),
            ("권장 조치", escape(action)),
            ("처리 상태", status_badge(status)),
        ],
    )

    current_index = STATUS_OPTIONS.index(status) if status in STATUS_OPTIONS else 0

    new_status = st.selectbox(
        "처리 상태 변경",
        STATUS_OPTIONS,
        index=current_index,
        key=f"status_select_{event_id}"
    )

    if st.button("처리 상태 저장", width="stretch", key=f"save_status_{event_id}"):
        update_event_status(event_id, new_status)
        st.success(f"#{event_id} 신고의 처리 상태가 `{new_status}`로 변경되었습니다.")
        st.rerun()


def render_statistics(events):
    render_admin_heading(
        "📊 상세 통계",
        "위치, 시간대, 위험도 분포를 기준으로 운영 현황을 확인합니다.",
    )

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
            st.plotly_chart(fig)

        with ch2:
            fig = plot_events_by_time(events)
            fig.update_traces(width=0.35)
            fig.update_layout(
                height=300,
                bargap=0.55,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig)

        ch3, ch4 = st.columns(2, gap="medium")

        with ch3:
            fig = plot_violation_distribution(events)
            fig.update_layout(
                height=300,
                bargap=0.55,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig)

        with ch4:
            fig = plot_detection_ratio(events)
            fig.update_layout(
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig)


def render_event_log(events):
    render_subsection_title("전체 신고 내역")

    if not events:
        with st.container(border=True):
            st.info("전체 신고 내역이 없습니다.")
        return

    status_groups = [
        ("확인 대기", "대기"),
        ("현장 확인 중", "진행"),
        ("처리 완료", "완료"),
    ]

    grouped_events = {
        status: sorted(
            [event for event in events if get_status(event) == status],
            key=lambda event: (
                get_score(event),
                str(event.get("timestamp", "")),
                int(event.get("event_id", 0) or 0),
            ),
            reverse=True,
        )
        for status, _ in status_groups
    }

    board_html = ['<div class="event-board">']

    for status, short_label in status_groups:
        group = grouped_events[status]
        status_class = {
            "확인 대기": "waiting",
            "현장 확인 중": "progress",
            "처리 완료": "done",
        }[status]

        group_html = [
            f'<div class="event-group event-group-{status_class}">',
            '<div class="event-group-header">',
            "<div>",
            f'<div class="event-group-kicker">{short_label}</div>',
            f'<div class="event-group-title">{escape(status)}</div>',
            "</div>",
            f'<div class="event-group-count">{len(group)}</div>',
            "</div>",
        ]

        if not group:
            group_html.append('<div class="event-group-empty">해당 상태의 신고가 없습니다.</div>')
        else:
            for event in group:
                event_id = event.get("event_id", "-")
                timestamp = str(event.get("timestamp", ""))[:16]
                location = event.get("location", "-")
                score = get_score(event)
                prediction = get_prediction_label(event.get("prediction", "-"))
                action = event.get("action", "-")

                group_html.extend([
                    '<div class="event-log-card">',
                    '<div class="event-log-main">',
                    f'<div class="event-log-title">#{escape(event_id)} {escape(location)}</div>',
                    f'<div class="event-log-meta">{escape(timestamp)} · {escape(prediction)}</div>',
                    "</div>",
                    '<div class="event-log-side">',
                    score_badge(score),
                    f'<div class="event-log-action">{escape(action)}</div>',
                    "</div>",
                    "</div>",
                ])

        group_html.append("</div>")
        board_html.extend(group_html)

    board_html.append("</div>")
    st.markdown("\n".join(board_html), unsafe_allow_html=True)


def render():
    if "events" not in st.session_state:
        st.session_state["events"] = []

    events = normalize_events(st.session_state["events"])
    sync_normalized_events_to_session(events)

    render_admin_heading(
        "🖥️ 신고 관리",
        "접수된 신고의 위험도, 처리 상태, 수거 동선을 한 화면에서 관리합니다.",
    )

    render_kpi(events)

    level_filter, status_filter, location_filter = render_filters(events)
    filtered_events = apply_filters(events, level_filter, status_filter, location_filter)

    render_event_log(filtered_events)

    active_events = [
        event for event in filtered_events
        if get_status(event) != "처리 완료"
    ]

    pickup_targets = get_priority_list(active_events)
    route = optimize_route(pickup_targets)

    st.markdown("---")

    route_col, detail_col = st.columns([1.35, 1], gap="large")

    with route_col:
        render_route_map(route)

    with detail_col:
        render_selected_event_detail(filtered_events)

    st.markdown("---")

    render_pickup_list(route)

    st.markdown("---")

    render_statistics(filtered_events)
