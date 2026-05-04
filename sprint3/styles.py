import streamlit as st

CSS_STYLES = """
<style>
:root {
    --bg: #f5f5f7;
    --surface: rgba(255,255,255,0.82);
    --surface-solid: #ffffff;
    --surface-soft: #fbfbfd;
    --surface-tint: #eef4ff;
    --ink: #1d1d1f;
    --muted: #6e6e73;
    --faint: #8e8e93;
    --border: rgba(60,60,67,0.14);
    --border-strong: rgba(60,60,67,0.22);
    --green: #2f8f68;
    --green-soft: #eaf6ef;
    --blue: #0a84ff;
    --cyan: #64d2ff;
    --amber: #a45f00;
    --red: #ff3b30;
    --shadow: 0 26px 70px rgba(16, 24, 40, 0.12), 0 2px 8px rgba(16, 24, 40, 0.05);
    --shadow-soft: 0 16px 42px rgba(16, 24, 40, 0.08), 0 1px 2px rgba(255,255,255,0.9) inset;
    --physical-shadow: 0 14px 28px rgba(16,24,40,0.14), inset 0 1px 0 rgba(255,255,255,0.82), inset 0 -1px 0 rgba(0,0,0,0.10);
    --physical-shadow-active: 0 7px 16px rgba(10,132,255,0.22), inset 0 1px 0 rgba(255,255,255,0.36), inset 0 -2px 6px rgba(0,0,0,0.18);
    --radius-xl: 22px;
    --radius-lg: 18px;
    --radius-md: 14px;
}

html, body, [class*="css"], .stApp, button, input, select, textarea {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
                 "Helvetica Neue", Arial, sans-serif !important;
    font-size: 15px !important;
    letter-spacing: 0 !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background:
        radial-gradient(circle at 18% -8%, rgba(10,132,255,0.22), transparent 30%),
        radial-gradient(circle at 82% 4%, rgba(100,210,255,0.17), transparent 28%),
        radial-gradient(circle at 50% 100%, rgba(229,241,255,0.78), transparent 36%),
        linear-gradient(180deg, #fbfbfd 0%, #f5f5f7 48%, #eef3fb 100%) !important;
    color: var(--ink) !important;
}
section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.86), rgba(245,247,251,0.82)) !important;
}

.block-container {
    padding-top: 1.1rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1320px !important;
}

.app-header {
    backdrop-filter: blur(28px) saturate(1.6);
    -webkit-backdrop-filter: blur(28px) saturate(1.6);
    background:
        radial-gradient(circle at 14% -24%, rgba(100,210,255,0.34), transparent 34%),
        radial-gradient(circle at 96% 0%, rgba(255,255,255,0.14), transparent 28%),
        linear-gradient(135deg, #171a20 0%, #303238 48%, #4a4a4d 100%);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 28px;
    box-shadow: 0 30px 82px rgba(12,18,28,0.26), inset 0 1px 0 rgba(255,255,255,0.18);
    color: #f5f5f7;
    display: flex;
    justify-content: space-between;
    gap: 18px;
    padding: 18px 20px;
    margin-bottom: 14px;
}
.app-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}
.app-mark {
    align-items: center;
    background: linear-gradient(180deg, rgba(255,255,255,0.20), rgba(255,255,255,0.08));
    border: 1px solid rgba(255,255,255,0.24);
    border-radius: 20px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.25), 0 14px 28px rgba(0,0,0,0.18);
    color: #ffffff;
    display: flex;
    font-size: 13px;
    font-weight: 800;
    height: 48px;
    justify-content: center;
    width: 48px;
}
.app-kicker {
    color: #64d2ff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.08em !important;
    margin-bottom: 4px;
    text-transform: uppercase;
}
.app-title {
    color: #f5f5f7;
    font-size: 26px;
    font-weight: 820;
    letter-spacing: 0 !important;
    line-height: 1.15;
}
.app-subtitle {
    color: rgba(245,245,247,0.72);
    font-size: 13px;
    line-height: 1.45;
    margin-top: 4px;
}
.app-header-meta {
    align-items: flex-end;
    display: flex;
    flex-direction: column;
    gap: 8px;
    justify-content: center;
    text-align: right;
}
.status-pill {
    border: 1px solid rgba(255,255,255,0.62);
    border-radius: 999px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.30), 0 10px 24px rgba(0,0,0,0.16);
    display: inline-flex;
    font-size: 12px;
    font-weight: 760;
    padding: 6px 12px;
    white-space: nowrap;
}
.status-pill.ok {
    background: rgba(48,209,88,0.14);
    color: #d8ffe4;
}
.status-pill.alert {
    background: linear-gradient(180deg, rgba(255,255,255,0.24), rgba(255,69,58,0.18));
    color: #ffd7d4;
}
.meta-note {
    color: rgba(245,245,247,0.58);
    font-size: 11px;
}

.stTabs [data-baseweb="tab-list"] {
    backdrop-filter: blur(24px) saturate(1.55);
    -webkit-backdrop-filter: blur(24px) saturate(1.55);
    background:
        linear-gradient(180deg, rgba(255,255,255,0.92), rgba(246,247,250,0.78)) !important;
    border: 1px solid rgba(255,255,255,0.72) !important;
    border-radius: 20px !important;
    box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,0.95);
    gap: 6px !important;
    padding: 6px !important;
}
.stTabs [data-baseweb="tab"] {
    border: 1px solid transparent !important;
    border-radius: 15px !important;
    color: var(--muted) !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif !important;
    font-size: 14px !important;
    font-weight: 650 !important;
    min-height: 42px !important;
    padding: 10px 16px !important;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease, transform 180ms ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: linear-gradient(180deg, #ffffff, #eef5ff) !important;
    color: var(--ink) !important;
    border-color: rgba(10,132,255,0.18) !important;
    box-shadow: 0 9px 20px rgba(16,24,40,0.08), inset 0 1px 0 rgba(255,255,255,0.96);
    transform: translateY(-1px);
}
.stTabs [aria-selected="true"] {
    background:
        linear-gradient(180deg, #3b3b40 0%, #1d1d1f 100%) !important;
    border-color: rgba(255,255,255,0.16) !important;
    color: #ffffff !important;
    box-shadow: var(--physical-shadow-active);
    font-weight: 780 !important;
}

/* Slider — bigger label */
.stSlider label, .stSlider [data-testid="stWidgetLabel"] {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
}
.stSlider [data-testid="stThumbValue"],
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] {
    font-size: 13px !important;
}

/* Metric cards (st.metric) */
[data-testid="stMetric"] {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.98), rgba(246,248,252,0.88));
    border: 1px solid rgba(255,255,255,0.72);
    border-radius: 20px;
    padding: 15px 16px !important;
    box-shadow: var(--shadow-soft);
}
[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    font-size: 30px !important;
    font-weight: 700 !important;
    letter-spacing: 0 !important;
    color: var(--ink) !important;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Dataframe / tables */
.stDataFrame {
    border: 1px solid rgba(255,255,255,0.72);
    border-radius: 20px;
    box-shadow: var(--shadow);
    overflow: hidden;
}

/* Buttons */
.stButton button {
    background: linear-gradient(180deg, #ffffff 0%, #f2f5fb 100%) !important;
    border: 1px solid rgba(60,60,67,0.16) !important;
    border-radius: 999px !important;
    box-shadow: var(--physical-shadow) !important;
    color: var(--ink) !important;
    font-weight: 680 !important;
    font-size: 14px !important;
    min-height: 42px !important;
    padding-left: 18px !important;
    padding-right: 18px !important;
    transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease !important;
}
.stButton button:hover {
    background: linear-gradient(180deg, #ffffff 0%, #eaf3ff 100%) !important;
    border-color: rgba(10,132,255,0.34) !important;
    transform: translateY(-1px);
}
.stButton button:active {
    box-shadow: inset 0 2px 8px rgba(16,24,40,0.16), 0 5px 14px rgba(16,24,40,0.10) !important;
    transform: translateY(1px);
}

/* iOS-like toggle */
[data-testid="stToggle"] [role="switch"] {
    border-radius: 999px !important;
    box-shadow: inset 0 2px 6px rgba(0,0,0,0.16), inset 0 1px 0 rgba(255,255,255,0.55), 0 8px 18px rgba(16,24,40,0.10) !important;
}
[data-testid="stToggle"] [aria-checked="true"] {
    background: linear-gradient(180deg, #4f9cff, #0a84ff) !important;
}

/* Selectbox / multiselect labels */
.stSelectbox label, .stMultiSelect label {
    font-size: 13px !important;
    font-weight: 720 !important;
    color: var(--ink) !important;
}

/* Caption text */
.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 12px !important;
    color: var(--faint) !important;
}

/* Dividers */
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

div[data-testid="stAlert"] {
    border-radius: 16px !important;
    border: 1px solid var(--border) !important;
}

.apple-icon {
    align-items: center;
    backdrop-filter: blur(18px) saturate(1.35);
    -webkit-backdrop-filter: blur(18px) saturate(1.35);
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(238,244,255,0.78));
    border: 1px solid rgba(255,255,255,0.78);
    border-radius: 999px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,1), inset 0 -1px 0 rgba(60,60,67,0.08), 0 9px 18px rgba(16,24,40,0.10);
    color: var(--blue);
    display: inline-flex;
    font-size: 13px;
    font-weight: 800;
    height: 28px;
    justify-content: center;
    line-height: 1;
    margin-right: 8px;
    vertical-align: middle;
    width: 28px;
}
.apple-icon.green { color: var(--green); }
.apple-icon.amber { color: var(--amber); }
.apple-icon.red { color: var(--red); }

.apple-status {
    align-items: center;
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(245,248,252,0.86));
    border: 1px solid rgba(255,255,255,0.72);
    border-radius: 999px;
    box-shadow: var(--physical-shadow);
    display: inline-flex;
    gap: 8px;
    padding: 8px 14px;
}
.apple-status-dot {
    border-radius: 999px;
    display: inline-block;
    height: 8px;
    width: 8px;
}

@media (max-width: 760px) {
    .app-header {
        flex-direction: column;
        padding: 16px;
    }
    .app-header-meta {
        align-items: flex-start;
        text-align: left;
    }
    .app-title {
        font-size: 21px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 9px 10px !important;
    }
}
</style>
"""

# Colour palette (use in f-strings for inline styles)
COLOR = {
    "green":  "#2f8f68",
    "blue":   "#0a84ff",
    "amber":  "#a45f00",
    "red":    "#ff3b30",
    "orange": "#b45309",
    "purple": "#6d5bd0",
    "cyan":   "#0e7490",
    "bg":     "#f5f5f7",
    "card":   "#ffffff",
    "soft":   "#f8faf8",
    "border": "rgba(60,60,67,0.14)",
    "text":   "#1d1d1f",
    "muted":  "#6e6e73",
    "faint":  "#8e8e93",
}

def inject_styles() -> None:
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


def card_html(title: str, value: str, subtitle: str = "", color: str = "#16a34a") -> str:
    """Return HTML for a KPI-style card using inline styles."""
    return f"""
    <div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));
                border:1px solid rgba(255,255,255,0.72);border-radius:20px;
                padding:16px 18px;box-shadow:0 16px 42px rgba(16,24,40,0.08),
                inset 0 1px 0 rgba(255,255,255,0.96), inset 0 -1px 0 rgba(60,60,67,0.08);
                min-height:122px;position:relative;overflow:hidden;">
      <div style="position:absolute;left:14px;right:14px;top:0;height:3px;border-radius:999px;
                  background:linear-gradient(90deg,rgba(255,255,255,0),{color},rgba(255,255,255,0));opacity:0.85;"></div>
      <div style="font-size:12px;font-weight:780;color:#6e6e73;
                  text-transform:uppercase;letter-spacing:0.06em;margin-bottom:7px;">
        {title}
      </div>
      <div style="font-size:31px;font-weight:780;letter-spacing:0;color:#1d1d1f;line-height:1.05;">
        {value}
      </div>
      <div style="font-size:11px;color:#6e6e73;margin-top:7px;line-height:1.35;">{subtitle}</div>
    </div>"""


def iec_gauge_html(iec_value: float) -> str:
    """Return HTML for the IEC gradient gauge."""
    pct = max(0.0, min(1.0, iec_value)) * 100
    if iec_value >= 0.6:
        status, status_color = "Zona óptima", COLOR["green"]
    elif iec_value >= 0.35:
        status, status_color = "Zona media", COLOR["amber"]
    else:
        status, status_color = "Zona crítica", COLOR["red"]

    return f"""
    <div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));
                border:1px solid rgba(255,255,255,0.72);border-radius:22px;
                padding:18px;box-shadow:0 18px 48px rgba(16,24,40,0.09),
                inset 0 1px 0 rgba(255,255,255,0.96);text-align:center;">
      <div style="font-size:12px;font-weight:780;color:#6e6e73;text-transform:uppercase;
                  letter-spacing:0.06em;margin-bottom:8px;">Índice IEC</div>
      <div style="font-size:44px;font-weight:820;letter-spacing:0;color:{status_color};line-height:1;">
        {iec_value:.2f}
      </div>
      <div style="font-size:12px;color:#6e6e73;margin:9px 0 12px;">Equilibrio Energía-Cultivo</div>
      <div style="background:linear-gradient(180deg,#e5e8ef,#f7f8fb);border-radius:999px;height:11px;
                  overflow:visible;position:relative;margin:4px 0;box-shadow:inset 0 2px 5px rgba(16,24,40,0.12);">
        <div style="height:100%;border-radius:6px;width:{pct:.0f}%;
                    background:linear-gradient(90deg,#ff453a 0%,#ff9f0a 42%,#30d158 86%);
                    box-shadow:0 2px 8px rgba(48,209,88,0.18);"></div>
        <div style="position:absolute;top:-4px;left:calc({pct:.0f}% - 7px);width:14px;height:14px;
                    background:#fff;border:2px solid {status_color};border-radius:50%;
                    box-shadow:0 5px 12px rgba(16,24,40,0.18), inset 0 1px 0 rgba(255,255,255,1);"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:10px;color:#8e8e93;margin-top:8px;">
        <span>0 Crítico</span><span>0.5</span><span>1.0 Óptimo</span>
      </div>
      <div style="font-size:13px;font-weight:760;color:{status_color};margin-top:11px;">
        {status}
      </div>
    </div>"""
