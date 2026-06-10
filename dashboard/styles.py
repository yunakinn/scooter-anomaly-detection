def get_styles():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

:root {
    --primary: #335c81;
    --primary-dark: #254966;
    --primary-soft: #edf4f8;
    --accent: #2f7d68;
    --accent-soft: #edf8f4;
    --surface: #ffffff;
    --surface-soft: #f7f9fc;
    --text-main: #1f2937;
    --text-sub: #667085;
    --text-muted: #98a2b3;
    --bg-main: #f8fafc;
    --bg-soft: #f2f5fb;
    --border-soft: rgba(31,41,55,0.10);
    --danger-bg: #fff5f3;
    --danger-text: #b23b2e;
    --warn-bg: #fff8ec;
    --warn-text: #8a5b13;
    --ok-bg: #f0f8f4;
    --ok-text: #2f7d68;
    --shadow-sm: 0 4px 12px rgba(31,41,55,0.05);
    --shadow-md: 0 12px 26px rgba(31,41,55,0.08);
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
    background-color: var(--bg-main) !important;
}

html, body, [class*="css"] {
    font-family: 'Manrope', 'Noto Sans KR', sans-serif;
}

.block-container {
    padding-top: 3.4rem !important;
    padding-bottom: 3rem !important;
    max-width: 1320px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 8px !important;
    padding: 1.35rem !important;
    margin-bottom: 0.9rem !important;
    box-shadow: var(--shadow-sm) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: var(--surface) !important;
    border-radius: 8px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] * {
    background-color: transparent;
}

div[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 8px !important;
    padding: 0.95rem 1.05rem !important;
    box-shadow: var(--shadow-sm);
}

div[data-testid="stMetricValue"] {
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    font-family: 'Manrope', 'Noto Sans KR', sans-serif !important;
    color: var(--text-main) !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: var(--text-muted) !important;
    font-weight: 700 !important;
    letter-spacing: 0;
}

h1, h2, h3, h4 {
    color: var(--text-main) !important;
    font-family: 'Manrope', 'Noto Sans KR', sans-serif !important;
    letter-spacing: 0;
    line-height: 1.35;
}

p, span, div, label {
    font-family: 'Manrope', 'Noto Sans KR', sans-serif;
}

.slabel {
    font-size: 20px;
    font-weight: 900;
    color: var(--text-main);
    margin: 0 0 1.1rem;
    line-height: 1.4;
}

.fbox {
    background: var(--bg-soft);
    border-radius: 8px;
    padding: 11px 13px;
    margin-bottom: 8px;
}

.flabel {
    font-size: 10px;
    color: var(--text-muted);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 3px;
}

.fval {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-main);
}

.score-big {
    font-family: 'Manrope', 'Noto Sans KR', sans-serif;
    font-weight: 800;
    font-size: 56px;
    color: var(--text-main);
    line-height: 1;
    letter-spacing: 0;
}

.pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 6px;
}

.pill-danger {
    background: var(--danger-bg);
    color: var(--danger-text);
}

.pill-warn {
    background: var(--warn-bg);
    color: var(--warn-text);
}

.pill-ok {
    background: var(--ok-bg);
    color: var(--ok-text);
}

.pill-normal {
    background: var(--bg-soft);
    color: var(--text-muted);
}

.pill-none {
    background: var(--bg-soft);
    color: var(--text-muted);
}

.bar-bg {
    background: #e5ebff;
    border-radius: 99px;
    height: 8px;
    margin: 14px 0 8px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 99px;
}

.bar-fill-danger {
    background: #ef4444;
}

.bar-fill-warn {
    background: #f59e0b;
}

.bar-fill-ok {
    background: #22c55e;
}

.pred-abnormal,
.pred-normal,
.pred-none {
    padding: 6px 16px;
    border-radius: 99px;
    font-size: 13px;
    font-weight: 800;
    display: inline-block;
}

.pred-abnormal {
    background: var(--danger-bg);
    color: var(--danger-text);
}

.pred-normal {
    background: var(--ok-bg);
    color: var(--ok-text);
}

.pred-none {
    background: var(--bg-soft);
    color: var(--text-muted);
}

.prow {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid var(--border-soft);
}

.prow:last-child {
    border-bottom: none;
}

.pnum {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: var(--bg-soft);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    color: var(--text-muted);
    flex-shrink: 0;
}

.pnum-hot {
    background: var(--danger-bg);
    color: var(--danger-text);
}

.stButton > button {
    border-radius: 8px !important;
    font-weight: 800 !important;
    font-size: 14px !important;
    padding: 0.64rem 1.4rem !important;
    transition: all 0.15s ease-in-out;
}

.stButton [data-testid="stBaseButton-primary"] {
    background: var(--primary) !important;
    color: #ffffff !important;
    border: 1px solid var(--primary) !important;
    box-shadow: 0 8px 18px rgba(51,92,129,0.18);
}

.stButton [data-testid="stBaseButton-primary"]:hover {
    background: var(--primary-dark) !important;
    border-color: var(--primary-dark) !important;
    transform: translateY(-1px);
}

.stButton [data-testid="stBaseButton-secondary"] {
    background: var(--surface) !important;
    color: var(--text-main) !important;
    border: 1px solid rgba(31,41,55,0.16) !important;
    box-shadow: none;
}

.stButton [data-testid="stBaseButton-secondary"]:hover {
    background: var(--surface-soft) !important;
    border-color: rgba(31,41,55,0.24) !important;
    color: var(--text-main) !important;
}

.stButton > button:disabled {
    background: #e5e7eb !important;
    color: #98a2b3 !important;
    border-color: #e5e7eb !important;
    box-shadow: none !important;
    transform: none;
}

.step {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1.25rem 0 0.45rem;
}

.step-num {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: var(--primary-soft);
    color: var(--primary-dark);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 800;
    flex-shrink: 0;
}

.step-text {
    font-size: 16px;
    color: var(--text-main);
    font-weight: 850;
    line-height: 1.35;
}

[data-testid="stCaptionContainer"] {
    color: var(--text-sub) !important;
    font-size: 13px !important;
    line-height: 1.55 !important;
}

.success-banner {
    background: var(--ok-bg);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    color: var(--ok-text);
    margin-bottom: 12px;
    font-weight: 700;
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
    border-top: 1px solid var(--border-soft);
    margin: 0.35rem 0 1rem;
}

.alert-item {
    background: var(--bg-soft);
    border-radius: 8px;
    padding: 11px 13px;
    margin-bottom: 8px;
    font-size: 13px;
    color: var(--text-main);
    font-weight: 600;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}

.status-box {
    background: var(--bg-soft);
    border-radius: 8px;
    padding: 13px;
    text-align: center;
}

.status-num {
    font-family: 'Manrope', 'Noto Sans KR', sans-serif;
    font-weight: 800;
    font-size: 28px;
    color: var(--text-main);
}

.status-label {
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 700;
}

.dashboard-panel {
    background: var(--surface);
    border-radius: 8px;
    border: 1px solid var(--border-soft);
    box-shadow: var(--shadow-sm);
    padding: 1.15rem;
    margin-bottom: 1rem;
}

.page-header {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 1rem;
    align-items: flex-start;
    margin: 0 0 0.8rem;
    padding: 0.35rem 0 0.1rem;
    width: 100%;
    min-width: 0;
    overflow: visible;
}

.page-header > div {
    width: 100%;
    min-width: 0;
    overflow: visible;
}

.page-title-row {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
}

.page-icon {
    width: clamp(40px, 4.4vw, 54px);
    height: clamp(40px, 4.4vw, 54px);
    border-radius: 8px;
    background: var(--primary-soft);
    color: var(--primary);
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    font-size: clamp(23px, 2.8vw, 32px);
    line-height: 1;
    box-shadow: inset 0 0 0 1px rgba(79,103,216,0.10);
}

.page-subtitle-wrap {
    padding-left: calc(clamp(40px, 4.4vw, 54px) + 0.8rem);
}

.page-header .page-title {
    font-family: 'Manrope', 'Noto Sans KR', sans-serif;
    font-size: clamp(30px, 3.7vw, 44px);
    font-weight: 900;
    color: var(--text-main);
    margin: 0;
    letter-spacing: 0;
    line-height: 1.28;
    white-space: normal;
    word-break: keep-all;
    overflow-wrap: break-word;
    overflow: visible;
    max-width: 100%;
}

.page-header .page-subtitle {
    color: var(--text-sub);
    font-size: clamp(15px, 1.55vw, 20px);
    font-weight: 600;
    margin: 0.45rem 0 0;
    line-height: 1.55;
    word-break: keep-all;
    overflow-wrap: break-word;
}

div[data-baseweb="select"] {
    height: auto !important;
}

div[data-baseweb="select"] > div {
    min-height: 46px !important;
    height: 46px !important;
    border-radius: 8px !important;
    background-color: var(--surface) !important;
    border-color: rgba(79,103,216,0.16) !important;
}

div[data-baseweb="popover"] {
    z-index: 999999 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 1px solid rgba(79,103,216,0.12);
    padding-top: 0.15rem;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    padding: 0 16px;
    border-radius: 8px 8px 0 0;
    font-weight: 800;
    color: var(--text-sub);
}

.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    background: var(--primary-soft);
}

.stDataFrame {
    border-radius: 8px !important;
    overflow: hidden !important;
}

[data-testid="stFileUploader"] section {
    border-radius: 8px !important;
    border: 1px dashed rgba(79,103,216,0.28) !important;
    background: var(--surface-soft) !important;
}

[data-testid="stFileUploader"] section:hover {
    border-color: rgba(79,103,216,0.55) !important;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border-soft) !important;
    border-radius: 8px !important;
    box-shadow: var(--shadow-sm);
}

[data-testid="stAlert"] {
    border-radius: 8px !important;
}

img {
    border-radius: 8px;
}

.admin-section-title {
    font-size: 21px;
    font-weight: 800;
    color: var(--text-main);
    margin: 18px 0 6px 0;
    letter-spacing: 0;
    line-height: 1.35;
    word-break: keep-all;
}

.admin-section-desc {
    font-size: 14px;
    color: var(--text-sub);
    margin-bottom: 14px;
    line-height: 1.65;
    word-break: keep-all;
}

.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border-soft);
    border-radius: 8px;
    padding: 18px 20px;
    box-shadow: var(--shadow-sm);
    min-height: 108px;
}

.kpi-label {
    font-size: 14px;
    color: var(--text-sub);
    font-weight: 800;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 30px;
    line-height: 1.1;
    color: var(--text-main);
    font-weight: 900;
    letter-spacing: 0;
}

.kpi-caption {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 8px;
    line-height: 1.5;
}

.summary-card {
    background: var(--surface);
    border: 1px solid var(--border-soft);
    border-radius: 8px;
    padding: 18px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 18px;
}

.summary-title {
    font-size: 18px;
    font-weight: 850;
    color: var(--text-main);
    margin-bottom: 8px;
    letter-spacing: 0;
    line-height: 1.4;
}

.summary-desc {
    font-size: 14px;
    color: var(--text-sub);
    line-height: 1.65;
    margin-bottom: 16px;
    word-break: keep-all;
}

.route-text-box {
    background: var(--surface-soft);
    border: 1px solid var(--border-soft);
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 14px;
    color: var(--text-main);
    line-height: 1.75;
    font-weight: 700;
    word-break: keep-all;
}

.pickup-card {
    background: var(--surface);
    border: 1px solid var(--border-soft);
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: var(--shadow-sm);
}

.pickup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}

.pickup-title {
    font-size: 16px;
    font-weight: 850;
    color: var(--text-main);
    letter-spacing: 0;
    line-height: 1.4;
}

.pickup-meta {
    font-size: 13px;
    color: var(--text-sub);
    line-height: 1.75;
    word-break: keep-all;
}

.badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    white-space: nowrap;
}

.badge-red {
    background: var(--danger-bg);
    color: var(--danger-text);
}

.badge-yellow {
    background: var(--warn-bg);
    color: var(--warn-text);
}

.badge-green {
    background: var(--ok-bg);
    color: var(--ok-text);
}

.badge-gray {
    background: var(--bg-soft);
    color: var(--text-muted);
}

.detail-card {
    background: var(--surface);
    border: 1px solid var(--border-soft);
    border-radius: 8px;
    padding: 20px;
    box-shadow: var(--shadow-sm);
}

.detail-title {
    font-size: 18px;
    font-weight: 850;
    color: var(--text-main);
    margin-bottom: 6px;
    letter-spacing: 0;
    line-height: 1.4;
}

.detail-subtitle {
    font-size: 13px;
    color: var(--text-sub);
    margin-bottom: 16px;
    line-height: 1.5;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    border-bottom: 1px solid rgba(79,103,216,0.10);
    padding: 9px 0;
    font-size: 14px;
}

.section-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin: 0 0 0.85rem;
}

.section-title {
    color: var(--text-main);
    font-size: 20px;
    font-weight: 850;
    line-height: 1.35;
    margin: 0;
}

.section-desc {
    color: var(--text-sub);
    font-size: 14px;
    line-height: 1.6;
    margin: 0.25rem 0 0;
    word-break: keep-all;
}

.empty-state,
.result-card,
.filter-panel {
    background: var(--surface);
    border: 1px solid var(--border-soft);
    border-radius: 8px;
    box-shadow: var(--shadow-sm);
}

.empty-state {
    padding: 1.15rem;
    color: var(--text-sub);
    font-size: 14px;
    line-height: 1.7;
}

.empty-state-title {
    color: var(--text-main);
    font-weight: 800;
    margin-bottom: 0.35rem;
}

.result-card {
    padding: 1.05rem;
    margin-top: 0.85rem;
}

.yolo-result-header {
    align-items: center;
    background: #ffffff;
    border: 1px solid rgba(31,41,55,0.10);
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    gap: 16px;
    margin: 0.65rem 0 0.85rem;
    padding: 0.9rem 1rem;
}

.yolo-eyebrow {
    color: var(--primary);
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.08em;
    line-height: 1.2;
    text-transform: uppercase;
}

.yolo-title {
    color: var(--text-main);
    font-size: 18px;
    font-weight: 900;
    line-height: 1.35;
    margin-top: 0.2rem;
    word-break: keep-all;
}

.yolo-confidence {
    align-items: flex-end;
    background: var(--primary-soft);
    border: 1px solid rgba(51,92,129,0.16);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    min-width: 96px;
    padding: 0.65rem 0.75rem;
}

.yolo-confidence span {
    color: var(--text-sub);
    font-size: 12px;
    font-weight: 800;
    line-height: 1.2;
}

.yolo-confidence strong {
    color: var(--primary-dark);
    font-size: 20px;
    font-weight: 900;
    line-height: 1.25;
    margin-top: 0.2rem;
}

.image-caption {
    color: var(--text-muted);
    font-size: 13px;
    font-weight: 800;
    line-height: 1.5;
    margin: 0.55rem 0 1.1rem;
    text-align: center;
}

.detection-card {
    background: #ffffff;
    border: 1px solid rgba(31,41,55,0.12);
    border-radius: 8px;
    box-shadow: none;
    margin-top: 0.8rem;
    padding: 1rem 1.05rem;
}

.detection-card-warning {
    background: #fffdf8;
    border-color: rgba(183,121,31,0.22);
}

.detection-card-success {
    background: #fbfefc;
    border-color: rgba(47,125,104,0.18);
}

.detection-card-danger {
    background: #fbfdff;
    border-color: rgba(51,92,129,0.18);
}

.detection-topline {
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: flex-start;
    flex-wrap: wrap;
}

.detection-label {
    color: var(--text-sub);
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.04em;
    line-height: 1.2;
}

.detection-chip {
    display: inline-flex;
    align-items: center;
    min-height: 28px;
    padding: 4px 10px;
    border-radius: 999px;
    background: var(--text-main);
    color: #ffffff;
    font-size: 12px;
    font-weight: 900;
    line-height: 1.2;
    word-break: keep-all;
}

.detection-card-danger .detection-chip {
    background: var(--danger-text);
}

.detection-card-success .detection-chip {
    background: var(--accent);
}

.detection-card-warning .detection-chip {
    background: #b7791f;
}

.detection-location-text {
    border-top: 1px solid rgba(31,41,55,0.08);
    color: var(--text-sub);
    font-size: 13px;
    font-weight: 800;
    line-height: 1.45;
    margin-top: 0.85rem;
    padding-top: 0.7rem;
    word-break: keep-all;
}

.detection-copy {
    color: var(--text-main);
    font-size: 18px;
    font-weight: 900;
    line-height: 1.5;
    margin: 0.7rem 0 0;
    word-break: keep-all;
}

.result-card-title {
    color: var(--text-main);
    font-size: 15px;
    font-weight: 850;
    margin-bottom: 0.35rem;
}

.result-card-text {
    color: var(--text-sub);
    font-size: 14px;
    line-height: 1.65;
    margin: 0;
    word-break: keep-all;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    margin-top: 0.9rem;
}

.mini-field {
    background: #fbfcfe;
    border: 1px solid rgba(31,41,55,0.08);
    border-radius: 8px;
    padding: 12px 14px;
}

.mini-label {
    color: #7a8699;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 5px;
}

.mini-value {
    color: var(--text-main);
    font-size: 15px;
    font-weight: 850;
    line-height: 1.45;
    word-break: keep-all;
}

.filter-panel {
    padding: 1rem;
    margin: 1rem 0 0.85rem;
}

.subsection-title {
    color: var(--text-main);
    font-size: 16px;
    font-weight: 850;
    margin: 1.15rem 0 0.65rem;
    line-height: 1.4;
}

.event-board {
    display: grid;
    gap: 12px;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    margin-bottom: 1.1rem;
}

.event-group {
    background: var(--surface);
    border: 1px solid rgba(31,41,55,0.10);
    border-radius: 8px;
    box-shadow: var(--shadow-sm);
    min-height: 180px;
    padding: 14px;
}

.event-group-waiting {
    border-top: 4px solid var(--danger-text);
}

.event-group-progress {
    border-top: 4px solid #b7791f;
}

.event-group-done {
    border-top: 4px solid var(--accent);
}

.event-group-header {
    align-items: center;
    border-bottom: 1px solid rgba(31,41,55,0.08);
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    padding-bottom: 10px;
}

.event-group-kicker {
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.08em;
    line-height: 1.2;
}

.event-group-title {
    color: var(--text-main);
    font-size: 17px;
    font-weight: 900;
    line-height: 1.35;
    margin-top: 3px;
}

.event-group-count {
    align-items: center;
    background: var(--bg-soft);
    border-radius: 999px;
    color: var(--text-main);
    display: inline-flex;
    font-size: 13px;
    font-weight: 900;
    height: 28px;
    justify-content: center;
    min-width: 28px;
    padding: 0 9px;
}

.event-group-empty {
    color: var(--text-muted);
    font-size: 13px;
    font-weight: 700;
    line-height: 1.6;
    padding: 8px 2px;
}

.event-log-card {
    background: #fbfcfe;
    border: 1px solid rgba(31,41,55,0.08);
    border-radius: 8px;
    display: flex;
    gap: 10px;
    justify-content: space-between;
    margin-bottom: 8px;
    padding: 11px 12px;
}

.event-log-card:last-child {
    margin-bottom: 0;
}

.event-log-main {
    min-width: 0;
}

.event-log-title {
    color: var(--text-main);
    font-size: 14px;
    font-weight: 900;
    line-height: 1.35;
    word-break: keep-all;
}

.event-log-meta {
    color: var(--text-sub);
    font-size: 12px;
    font-weight: 750;
    line-height: 1.45;
    margin-top: 4px;
}

.event-log-side {
    align-items: flex-end;
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-width: 130px;
    text-align: right;
}

.event-log-action {
    color: var(--text-sub);
    font-size: 12px;
    font-weight: 750;
    line-height: 1.35;
    word-break: keep-all;
}

.map-note {
    color: var(--text-sub);
    font-size: 13px;
    line-height: 1.55;
    margin: -0.25rem 0 0.75rem;
}

.detail-row:last-child {
    border-bottom: none;
}

.detail-label {
    color: var(--text-sub);
    font-weight: 700;
    flex-shrink: 0;
}

.detail-value {
    color: var(--text-main);
    font-weight: 750;
    text-align: right;
    line-height: 1.5;
    word-break: keep-all;
}

@media (max-width: 900px) {
    .block-container {
        padding-top: 3.25rem !important;
    }

    .page-header .page-title {
        font-size: 28px;
        line-height: 1.32;
        letter-spacing: 0;
    }

    .page-header .page-subtitle {
        font-size: 17px;
    }

    .page-title-row {
        gap: 0.65rem;
    }

    .page-subtitle-wrap {
        padding-left: 0;
    }

    .score-big {
        font-size: 44px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0.95rem !important;
    }

    .dashboard-panel {
        padding: 1rem;
    }

    .status-grid {
        grid-template-columns: 1fr;
    }

    .kpi-card {
        min-height: auto;
    }

    .pickup-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .detail-row {
        flex-direction: column;
        gap: 4px;
    }

    .detail-value {
        text-align: left;
    }

    .detail-grid {
        grid-template-columns: 1fr;
    }

    .event-board {
        grid-template-columns: 1fr;
    }

    .event-log-card {
        flex-direction: column;
    }

    .event-log-side {
        align-items: flex-start;
        max-width: none;
        text-align: left;
    }

    .detection-topline {
        align-items: flex-start;
        flex-direction: column;
        gap: 8px;
    }

    .detection-location-text {
        text-align: left;
    }

    .yolo-result-header {
        align-items: stretch;
        flex-direction: column;
    }

    .yolo-confidence {
        align-items: flex-start;
        min-width: 0;
    }
}
</style>
"""
