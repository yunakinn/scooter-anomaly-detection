import html

import streamlit as st


def escape(value):
    return html.escape(str(value), quote=True)


def score_badge(score):
    if score >= 80:
        return f'<span class="badge badge-red">{score:.1f}점</span>'
    if score >= 50:
        return f'<span class="badge badge-yellow">{score:.1f}점</span>'
    if score >= 30:
        return f'<span class="badge badge-green">{score:.1f}점</span>'
    return f'<span class="badge badge-gray">{score:.1f}점</span>'


def status_badge(status):
    status_text = escape(status)

    if status == "처리 완료":
        return f'<span class="badge badge-green">{status_text}</span>'
    if status == "현장 확인 중":
        return f'<span class="badge badge-yellow">{status_text}</span>'
    return f'<span class="badge badge-gray">{status_text}</span>'


def render_section_heading(title, description=None):
    description_html = ""

    if description:
        description_html = f'<p class="section-desc">{escape(description)}</p>'

    st.markdown(
        f"""
        <div class="section-heading">
            <div>
                <p class="section-title">{escape(title)}</p>
                {description_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_admin_heading(title, description=None):
    st.markdown(
        f'<div class="admin-section-title">{escape(title)}</div>',
        unsafe_allow_html=True,
    )

    if description:
        st.markdown(
            f'<div class="admin-section-desc">{escape(description)}</div>',
            unsafe_allow_html=True,
        )


def render_subsection_title(title):
    st.markdown(
        f'<div class="subsection-title">{escape(title)}</div>',
        unsafe_allow_html=True,
    )


def render_kpi_card(label, value, caption):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{escape(label)}</div>
            <div class="kpi-value">{escape(value)}</div>
            <div class="kpi-caption">{escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_filter_panel(title, description):
    st.markdown(
        f"""
        <div class="filter-panel">
            <div class="result-card-title">{escape(title)}</div>
            <p class="result-card-text">{escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title, description):
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-state-title">{escape(title)}</div>
            {escape(description)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_detection_header(confidence):
    confidence_text = f"{confidence * 100:.1f}%" if isinstance(confidence, (int, float)) else "-"

    st.markdown(
        f"""
        <div class="yolo-result-header">
            <div>
                <div class="yolo-eyebrow">Image Analysis</div>
                <div class="yolo-title">이미지 분석 결과</div>
            </div>
            <div class="yolo-confidence">
                <span>판정 확률</span>
                <strong>{escape(confidence_text)}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_image_caption(text):
    st.markdown(
        f'<div class="image-caption">{escape(text)}</div>',
        unsafe_allow_html=True,
    )


def render_detection_result_card(status, title, description, location):
    st.markdown(
        f"""
        <div class="detection-card detection-card-{escape(status)}">
            <div class="detection-topline">
                <span class="detection-label">판정 결과</span>
                <span class="detection-chip">{escape(title)}</span>
            </div>
            <p class="detection-copy">{escape(description)}</p>
            <div class="detection-location-text">신고 위치: {escape(location)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_route_summary(route_count, route_text):
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-title">수거 동선 요약</div>
            <div class="summary-desc">
                수거 대상 {route_count}건을 현재 위치 기준 최단 동선으로 정렬했습니다.
            </div>
            <div class="route-text-box">
                {escape(route_text)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pickup_card(order, location, score_html, action_text, timestamp, distance, status_html):
    st.markdown(
        f"""
        <div class="pickup-card">
            <div class="pickup-header">
                <div class="pickup-title">#{escape(order)} {escape(location)}</div>
                {score_html}
            </div>
            <div class="pickup-meta">
                조치: {escape(action_text)}<br>
                접수: {escape(timestamp)} · 이전 지점에서 약 {escape(distance)}m<br>
                상태: {status_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_event_detail_card(location, event_id, timestamp, rows):
    row_html = "\n".join(
        f"""
        <div class="detail-row">
            <div class="detail-label">{escape(label)}</div>
            <div class="detail-value">{value}</div>
        </div>
        """
        for label, value in rows
    )

    st.markdown(
        f"""
        <div class="detail-card">
            <div class="detail-title">{escape(location)}</div>
            <div class="detail-subtitle">신고 ID #{escape(event_id)} · {escape(timestamp)}</div>
            {row_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
