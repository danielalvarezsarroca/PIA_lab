import streamlit as st

CSS_STYLES = """
<style>
/* Apple typography */
html, body, [class*="css"], .stApp, button, input, select, textarea {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
                 "Helvetica Neue", Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* App background */
.stApp { background-color: #f9fafb !important; }
section[data-testid="stSidebar"] { background: #fff !important; }

/* Main content area */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff !important;
    border-bottom: 1px solid #e5e7eb !important;
    padding: 0 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #16a34a !important;
    border-bottom: 2px solid #16a34a !important;
    font-weight: 600 !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 14px 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #111827 !important;
}
[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* Dataframe / tables */
.stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #e5e7eb; }

/* Buttons */
.stButton button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* Selectbox / slider labels */
.stSelectbox label, .stSlider label, .stMultiSelect label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #374151 !important;
}

/* Dividers */
hr { border-color: #e5e7eb !important; margin: 1rem 0 !important; }
</style>
"""

# Colour palette (use in f-strings for inline styles)
COLOR = {
    "green":  "#16a34a",
    "blue":   "#1d4ed8",
    "amber":  "#d97706",
    "red":    "#dc2626",
    "orange": "#c2410c",
    "purple": "#7c3aed",
    "bg":     "#f9fafb",
    "card":   "#ffffff",
    "border": "#e5e7eb",
    "text":   "#111827",
    "muted":  "#6b7280",
}


def inject_styles() -> None:
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


def card_html(title: str, value: str, subtitle: str = "", color: str = "#16a34a") -> str:
    """Return HTML for a KPI-style card using inline styles."""
    return f"""
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;
                padding:14px 16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);
                border-top:3px solid {color};">
      <div style="font-size:10px;font-weight:600;color:#6b7280;
                  text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">
        {title}
      </div>
      <div style="font-size:24px;font-weight:700;letter-spacing:-0.02em;color:#111827;">
        {value}
      </div>
      <div style="font-size:10px;color:#9ca3af;margin-top:3px;">{subtitle}</div>
    </div>"""


def iec_gauge_html(iec_value: float) -> str:
    """Return HTML for the IEC gradient gauge."""
    pct = max(0.0, min(1.0, iec_value)) * 100
    if iec_value >= 0.6:
        status, status_color = "Zona óptima", "#16a34a"
    elif iec_value >= 0.35:
        status, status_color = "Zona media", "#d97706"
    else:
        status, status_color = "Zona crítica", "#dc2626"

    return f"""
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;
                padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);text-align:center;">
      <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;
                  letter-spacing:0.06em;margin-bottom:6px;">Índice IEC</div>
      <div style="font-size:36px;font-weight:700;letter-spacing:-0.04em;color:{status_color};">
        {iec_value:.2f}
      </div>
      <div style="font-size:10px;color:#6b7280;margin-bottom:8px;">Equilibrio Energía–Cultivo</div>
      <div style="background:#f3f4f6;border-radius:6px;height:8px;overflow:visible;position:relative;margin:4px 0;">
        <div style="height:100%;border-radius:6px;width:{pct:.0f}%;
                    background:linear-gradient(90deg,#dc2626 0%,#f59e0b 40%,#22c55e 80%);"></div>
        <div style="position:absolute;top:-4px;left:calc({pct:.0f}% - 6px);width:12px;height:12px;
                    background:#fff;border:2px solid {status_color};border-radius:50%;
                    box-shadow:0 1px 4px rgba(0,0,0,0.2);"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:8px;color:#9ca3af;margin-top:6px;">
        <span>0 Crítico</span><span>0.5</span><span>1.0 Óptimo</span>
      </div>
      <div style="font-size:11px;font-weight:600;color:{status_color};margin-top:8px;">
        ● {status}
      </div>
    </div>"""
