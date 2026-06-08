def get_styles():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

:root {
    --primary: #4f67d8;
    --primary-dark: #3954cc;
    --text-main: #24324a;
    --text-sub: #6b7280;
    --text-muted: #8d97a8;
    --bg-main: #ffffff;
    --bg-soft: #f4f7ff;
    --border-soft: rgba(79,103,216,0.12);
    --danger-bg: #fde8e8;
    --danger-text: #a03030;
    --warn-bg: #fff4de;
    --warn-text: #8a5e00;
    --ok-bg: #e4f0e8;
    --ok-text: #2a6840;
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
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1320px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 20px !important;
    padding: 1.1rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 10px 26px rgba(79,103,216,0.08) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #ffffff !important;
    border-radius: 20px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] * {
    background-color: transparent;
}

div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 14px !important;
    padding: 0.95rem 1.05rem !important;
    box-shadow: 0 6px 14px rgba(79,103,216,0.06);
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
    letter-spacing: -0.01em;
}

h1, h2, h3, h4 {
    color: var(--text-main) !important;
    font-family: 'Manrope', 'Noto Sans KR', sans-serif !important;
    letter-spacing: -0.03em;
}

p, span, div, label {
    font-family: 'Manrope', 'Noto Sans KR', sans-serif;
}

.slabel {
    font-size: 12px;
    font-weight: 800;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.75rem;
}

.fbox {
    background: var(--bg-soft);
    border-radius: 12px;
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
    letter-spacing: -2px;
}

.pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 99px;
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
    background: var(--primary) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 99px !important;
    font-weight: 800 !important;
    font-size: 14px !important;
    padding: 0.58rem 1.55rem !important;
    box-shadow: 0 8px 18px rgba(79,103,216,0.18);
    transition: all 0.15s ease-in-out;
}

.stButton > button:hover {
    background: var(--primary-dark) !important;
    transform: translateY(-1px);
}

.stButton > button:disabled {
    background: #cfd6f5 !important;
    color: #ffffff !important;
    box-shadow: none !important;
    transform: none;
}

.step {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.75rem;
}

.step-num {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--primary);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 800;
    flex-shrink: 0;
}

.step-text {
    font-size: 14px;
    color: var(--text-main);
    font-weight: 700;
}

.success-banner {
    background: var(--ok-bg);
    border-radius: 12px;
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
    border-top: 1px solid rgba(79,103,216,0.14);
    margin: 0.6rem 0 1.1rem;
}

.alert-item {
    background: var(--bg-soft);
    border-radius: 14px;
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
    border-radius: 14px;
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
    background: #ffffff;
    border-radius: 20px;
    border: 1px solid var(--border-soft);
    box-shadow: 0 10px 26px rgba(79,103,216,0.07);
    padding: 1.15rem;
    margin-bottom: 1rem;
}

.page-header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
    margin-bottom: 1.25rem;
}

.page-header .page-title {
    font-family: 'Manrope', 'Noto Sans KR', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: var(--text-main);
    margin: 0;
    letter-spacing: -0.04em;
}

.page-header .page-subtitle {
    color: var(--text-sub);
    font-size: 0.95rem;
    margin-top: 0.5rem;
    line-height: 1.55;
}

div[data-baseweb="select"] {
    height: auto !important;
}

div[data-baseweb="select"] > div {
    min-height: 46px !important;
    height: 46px !important;
    border-radius: 13px !important;
    background-color: #ffffff !important;
    border-color: rgba(79,103,216,0.16) !important;
}

div[data-baseweb="popover"] {
    z-index: 999999 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid rgba(79,103,216,0.12);
}

.stTabs [data-baseweb="tab"] {
    height: 44px;
    padding: 0 18px;
    border-radius: 12px 12px 0 0;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
}

.stDataFrame {
    border-radius: 16px !important;
    overflow: hidden !important;
}

[data-testid="stFileUploader"] section {
    border-radius: 16px !important;
    border: 1px dashed rgba(79,103,216,0.28) !important;
    background: #f8faff !important;
}

[data-testid="stFileUploader"] section:hover {
    border-color: rgba(79,103,216,0.55) !important;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border-soft) !important;
    border-radius: 16px !important;
    box-shadow: 0 6px 14px rgba(79,103,216,0.04);
}

[data-testid="stAlert"] {
    border-radius: 14px !important;
}

img {
    border-radius: 16px;
}

@media (max-width: 900px) {
    .page-header .page-title {
        font-size: 26px;
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
}
</style>
"""