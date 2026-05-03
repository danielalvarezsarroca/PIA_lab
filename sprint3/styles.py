import streamlit as st

CSS_STYLES = """
<style>
:root {
    --bg: #f5f5f7;
    --surface: rgba(255,255,255,0.86);
    --surface-solid: #ffffff;
    --surface-soft: #fbfbfd;
    --surface-tint: #f2f7f4;
    --ink: #1d1d1f;
    --muted: #6e6e73;
    --faint: #8e8e93;
    --border: rgba(60,60,67,0.14);
    --border-strong: rgba(60,60,67,0.22);
    --green: #2f8f68;
    --green-soft: #eaf6ef;
    --blue: #007aff;
    --cyan: #0e7490;
    --amber: #a45f00;
    --red: #ff3b30;
    --shadow: 0 18px 52px rgba(0, 0, 0, 0.08);
    --shadow-soft: 0 8px 28px rgba(0, 0, 0, 0.06);
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
        radial-gradient(circle at 12% 0%, rgba(0,122,255,0.08), transparent 30%),
        radial-gradient(circle at 84% 4%, rgba(47,143,104,0.10), transparent 28%),
        linear-gradient(180deg, #fbfbfd 0%, #f5f5f7 58%, #f2f4f5 100%) !important;
    color: var(--ink) !important;
}
section[data-testid="stSidebar"] { background: var(--surface) !important; }

.block-container {
    padding-top: 1.1rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1320px !important;
}

.app-header {
    backdrop-filter: blur(28px) saturate(1.6);
    -webkit-backdrop-filter: blur(28px) saturate(1.6);
    background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(246,248,247,0.82));
    border: 1px solid rgba(255,255,255,0.68);
    border-radius: 18px;
    box-shadow: var(--shadow);
    color: var(--ink);
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
    background: linear-gradient(145deg, #ffffff, #dfeee7);
    border: 1px solid rgba(60,60,67,0.12);
    border-radius: 15px;
    color: #25664d;
    display: flex;
    font-size: 13px;
    font-weight: 800;
    height: 48px;
    justify-content: center;
    width: 48px;
}
.app-kicker {
    color: var(--green);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.08em !important;
    margin-bottom: 4px;
    text-transform: uppercase;
}
.app-title {
    color: var(--ink);
    font-size: 24px;
    font-weight: 780;
    letter-spacing: 0 !important;
    line-height: 1.15;
}
.app-subtitle {
    color: var(--muted);
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
    border: 1px solid rgba(255,255,255,0.72);
    border-radius: 999px;
    display: inline-flex;
    font-size: 12px;
    font-weight: 760;
    padding: 6px 12px;
    white-space: nowrap;
}
.status-pill.ok {
    background: #eaf6ef;
    color: #25664d;
}
.status-pill.alert {
    background: #fff0ef;
    color: #d92d20;
}
.meta-note {
    color: var(--muted);
    font-size: 11px;
}

.stTabs [data-baseweb="tab-list"] {
    backdrop-filter: blur(24px) saturate(1.55);
    -webkit-backdrop-filter: blur(24px) saturate(1.55);
    background: rgba(255,255,255,0.78) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    box-shadow: var(--shadow-soft);
    gap: 6px !important;
    padding: 6px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important;
    color: var(--muted) !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif !important;
    font-size: 14px !important;
    font-weight: 650 !important;
    min-height: 42px !important;
    padding: 10px 16px !important;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #f2f7f4 !important;
    color: var(--ink) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(29,29,31,0.92) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 18px rgba(29,29,31,0.16);
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
    background: rgba(255,255,255,0.94);
    border: 1px solid var(--border);
    border-radius: 16px;
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
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: var(--shadow-soft);
    overflow: hidden;
}

/* Buttons */
.stButton button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    min-height: 42px !important;
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
    background: rgba(255,255,255,0.74);
    border: 1px solid rgba(60,60,67,0.12);
    border-radius: 999px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.9), 0 6px 16px rgba(0,0,0,0.06);
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
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(60,60,67,0.12);
    border-radius: 999px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.045);
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
    "blue":   "#007aff",
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
    <div style="background:rgba(255,255,255,0.88);border:1px solid rgba(60,60,67,0.14);border-radius:16px;
                padding:16px 18px;box-shadow:0 10px 28px rgba(0,0,0,0.055);
                border-top:3px solid {color};min-height:122px;">
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
    <div style="background:rgba(255,255,255,0.88);border:1px solid rgba(60,60,67,0.14);border-radius:16px;
                padding:18px;box-shadow:0 10px 28px rgba(0,0,0,0.055);text-align:center;">
      <div style="font-size:12px;font-weight:780;color:#6e6e73;text-transform:uppercase;
                  letter-spacing:0.06em;margin-bottom:8px;">Índice IEC</div>
      <div style="font-size:44px;font-weight:820;letter-spacing:0;color:{status_color};line-height:1;">
        {iec_value:.2f}
      </div>
      <div style="font-size:12px;color:#6e6e73;margin:9px 0 12px;">Equilibrio Energía-Cultivo</div>
      <div style="background:#ececf0;border-radius:999px;height:10px;overflow:visible;position:relative;margin:4px 0;">
        <div style="height:100%;border-radius:6px;width:{pct:.0f}%;
                    background:linear-gradient(90deg,#c83737 0%,#d88a16 42%,#12805c 86%);"></div>
        <div style="position:absolute;top:-4px;left:calc({pct:.0f}% - 7px);width:14px;height:14px;
                    background:#fff;border:2px solid {status_color};border-radius:50%;
                    box-shadow:0 1px 4px rgba(0,0,0,0.2);"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:10px;color:#8e8e93;margin-top:8px;">
        <span>0 Crítico</span><span>0.5</span><span>1.0 Óptimo</span>
      </div>
      <div style="font-size:13px;font-weight:760;color:{status_color};margin-top:11px;">
        {status}
      </div>
    </div>"""
