# Dashboard Interactive Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Tab 1 of the Streamlit dashboard fully interactive — a single hour slider drives the solar SVG, IEC gauge, angle metrics, ePAR/VWC cards, and the rules table, all with instant response via `@st.fragment`.

**Architecture:** `@st.fragment` wraps the reactive section of `tab_estado.py` so only that section reruns when the slider changes. Tab 3 "Panel solar" is eliminated — its logic merges into Tab 1. App drops to 4 tabs. Typography sizes increase throughout.

**Tech Stack:** Python 3.10+, Streamlit 1.43 (`@st.fragment` available since 1.37), Plotly 5.24, pandas 2.2

---

## File map

| File | Change |
|------|--------|
| `sprint3/styles.py` | Increase font sizes in `CSS_STYLES`, `card_html`, `iec_gauge_html` |
| `sprint3/tabs/tab_estado.py` | Full rewrite — adds `@st.fragment`, hour-based lookup, SVG, rules table |
| `sprint3/app.py` | 4 tabs, remove `tab_panel_solar` import and tab |
| `sprint3/tabs/tab_panel_solar.py` | Delete (content migrated to tab_estado) |

---

## Task 1: Update styles.py — larger Apple typography

**Files:**
- Modify: `sprint3/styles.py`

No tests (CSS — verified visually when app runs).

- [ ] **Step 1: Replace `CSS_STYLES` and update `card_html` and `iec_gauge_html` in `sprint3/styles.py`**

Replace the entire file with:

```python
import streamlit as st

CSS_STYLES = """
<style>
/* Apple typography — base size increase */
html, body, [class*="css"], .stApp, button, input, select, textarea {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
                 "Helvetica Neue", Arial, sans-serif !important;
    font-size: 15px !important;
    -webkit-font-smoothing: antialiased;
}

/* App background */
.stApp { background-color: #f9fafb !important; }
section[data-testid="stSidebar"] { background: #fff !important; }

/* Main content area */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
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
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
    padding: 12px 20px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #16a34a !important;
    border-bottom: 2px solid #16a34a !important;
    font-weight: 700 !important;
}

/* Slider — bigger label */
.stSlider label, .stSlider [data-testid="stWidgetLabel"] {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #111827 !important;
}
.stSlider [data-testid="stThumbValue"],
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] {
    font-size: 13px !important;
}

/* Metric cards (st.metric) */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 14px 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    font-size: 30px !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #111827 !important;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Dataframe / tables */
.stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #e5e7eb; }

/* Buttons */
.stButton button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

/* Selectbox / multiselect labels */
.stSelectbox label, .stMultiSelect label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #374151 !important;
}

/* Caption text */
.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 12px !important;
    color: #9ca3af !important;
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
                padding:16px 18px;box-shadow:0 1px 3px rgba(0,0,0,0.04);
                border-top:3px solid {color};">
      <div style="font-size:13px;font-weight:600;color:#6b7280;
                  text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">
        {title}
      </div>
      <div style="font-size:30px;font-weight:700;letter-spacing:-0.02em;color:#111827;">
        {value}
      </div>
      <div style="font-size:11px;color:#9ca3af;margin-top:4px;">{subtitle}</div>
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
                padding:18px;box-shadow:0 1px 3px rgba(0,0,0,0.04);text-align:center;">
      <div style="font-size:13px;font-weight:600;color:#6b7280;text-transform:uppercase;
                  letter-spacing:0.06em;margin-bottom:8px;">Índice IEC</div>
      <div style="font-size:42px;font-weight:700;letter-spacing:-0.04em;color:{status_color};">
        {iec_value:.2f}
      </div>
      <div style="font-size:12px;color:#6b7280;margin-bottom:10px;">Equilibrio Energía–Cultivo</div>
      <div style="background:#f3f4f6;border-radius:6px;height:10px;overflow:visible;position:relative;margin:4px 0;">
        <div style="height:100%;border-radius:6px;width:{pct:.0f}%;
                    background:linear-gradient(90deg,#dc2626 0%,#f59e0b 40%,#22c55e 80%);"></div>
        <div style="position:absolute;top:-4px;left:calc({pct:.0f}% - 7px);width:14px;height:14px;
                    background:#fff;border:2px solid {status_color};border-radius:50%;
                    box-shadow:0 1px 4px rgba(0,0,0,0.2);"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:10px;color:#9ca3af;margin-top:8px;">
        <span>0 Crítico</span><span>0.5</span><span>1.0 Óptimo</span>
      </div>
      <div style="font-size:13px;font-weight:700;color:{status_color};margin-top:10px;">
        ● {status}
      </div>
    </div>"""
```

- [ ] **Step 2: Commit**

```bash
git add sprint3/styles.py
git commit -m "feat(sprint3): increase typography sizes for readability"
```

---

## Task 2: Rewrite tab_estado.py — interactive home with @st.fragment

**Files:**
- Modify: `sprint3/tabs/tab_estado.py`

No unit tests (Streamlit UI — verified by running the app).

- [ ] **Step 1: Replace the entire content of `sprint3/tabs/tab_estado.py` with:**

```python
import math

import pandas as pd
import streamlit as st

from alert_logic import build_alert_list, get_anomalous_trackers
from rule_engine import format_regime_label, get_active_rule_index
from solar_logic import estimate_solar_elevation, get_recommended_angle
from svg_generator import generate_solar_svg
from styles import COLOR, card_html, iec_gauge_html

_ALL_TRACKERS = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10"]
_ANOMALY_THRESHOLD = 450.0


def _get_hour_record(df_modelo: pd.DataFrame, hour: int) -> pd.Series:
    """Return the row with the highest IEC for the given hour of day.
    Falls back to nearest available hour if no data for requested hour."""
    rows = df_modelo[df_modelo["hour_of_day"] == hour].dropna(subset=["IEC", "track_mean"])
    if not rows.empty:
        return rows.loc[rows["IEC"].idxmax()]
    valid = df_modelo.dropna(subset=["IEC", "track_mean"])
    if valid.empty:
        return df_modelo.iloc[-1]
    idx = (valid["hour_of_day"] - hour).abs().idxmin()
    return valid.loc[idx]


@st.fragment
def _render_interactive_section(df_modelo: pd.DataFrame, df_rules: pd.DataFrame) -> None:
    # ── Slider ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:15px;font-weight:700;color:#111827;margin-bottom:8px;">'
        '⏱ Hora del día — mueve para explorar el estado del sistema</div>',
        unsafe_allow_html=True,
    )
    hour = st.slider(
        "hora",
        min_value=6, max_value=21, value=13, step=1,
        format="%d:00", label_visibility="collapsed",
    )

    # ── Compute all values for selected hour ──────────────────────────────────
    row         = _get_hour_record(df_modelo, hour)
    track_angle = float(row.get("track_mean", 0.0))
    iec_val     = float(row.get("IEC", float("nan")))
    regime      = str(row.get("tracking_regime", "—"))
    epar_s1     = float(row.get("ePAR_S1_mean", float("nan")))
    epar_s2     = float(row.get("ePAR_S2_mean", float("nan")))
    vwc_s1      = float(row.get("VWC_S1_mean", float("nan")))
    vwc_s2      = float(row.get("VWC_S2_mean", float("nan")))
    solar_elev  = float(row.get("solar_elevation_deg", estimate_solar_elevation(float(hour))))
    rec_angle   = get_recommended_angle(hour, df_modelo)
    regime_label = format_regime_label(regime)
    iec_safe    = iec_val if not math.isnan(iec_val) else 0.0
    active_idx  = get_active_rule_index(df_rules, iec_safe)
    in_range    = abs(track_angle - rec_angle) <= 5

    # ── SVG panel (left) + metric cards (right) ───────────────────────────────
    col_svg, col_info = st.columns([3, 2])

    with col_svg:
        svg_html = generate_solar_svg(
            hour=float(hour),
            track_angle=track_angle,
            rec_angle=rec_angle,
            solar_elevation=solar_elev,
            irradiance=400.0,
        )
        st.markdown(svg_html, unsafe_allow_html=True)
        status_txt = "✓ En rango óptimo" if in_range else "⚠ Fuera del rango recomendado"
        status_clr = COLOR["green"] if in_range else COLOR["orange"]
        st.markdown(
            f'<div style="text-align:center;font-size:14px;font-weight:700;'
            f'color:{status_clr};margin-top:8px;">{status_txt}</div>',
            unsafe_allow_html=True,
        )

    with col_info:
        st.markdown(iec_gauge_html(iec_safe), unsafe_allow_html=True)
        st.markdown("<div style='margin:10px 0;'></div>", unsafe_allow_html=True)
        for lbl, val, clr in [
            ("Ángulo actual",      f"{track_angle:.1f}°", COLOR["blue"]),
            ("Ángulo recomendado", f"{rec_angle:.1f}°",   COLOR["green"]),
            ("Régimen activo",     regime_label,           COLOR["purple"]),
            ("Elevación solar",    f"{solar_elev:.1f}°",  COLOR["orange"]),
        ]:
            st.markdown(
                f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;'
                f'padding:12px 14px;margin-bottom:8px;">'
                f'<div style="font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;'
                f'letter-spacing:0.05em;">{lbl}</div>'
                f'<div style="font-size:22px;font-weight:700;color:{clr};margin-top:3px;">{val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin:14px 0;'></div>", unsafe_allow_html=True)

    # ── ePAR + VWC KPI cards ─────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    def _fmt(v: float, decimals: int) -> str:
        return f"{v:.{decimals}f}" if not math.isnan(v) else "—"
    with k1:
        st.markdown(card_html("ePAR S1", _fmt(epar_s1, 0), "µmol/m²/s", COLOR["green"]), unsafe_allow_html=True)
    with k2:
        st.markdown(card_html("ePAR S2", _fmt(epar_s2, 0), "µmol/m²/s", COLOR["green"]), unsafe_allow_html=True)
    with k3:
        st.markdown(card_html("VWC S1", _fmt(vwc_s1, 2), "m³/m³", COLOR["amber"]), unsafe_allow_html=True)
    with k4:
        st.markdown(card_html("VWC S2", _fmt(vwc_s2, 2), "m³/m³", COLOR["amber"]), unsafe_allow_html=True)

    st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

    # ── Rules table ───────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#111827;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:10px;">🔄 Reglas de rotación candidatas</div>',
        unsafe_allow_html=True,
    )
    if df_rules.empty:
        st.info("No se encontraron reglas.")
    else:
        for i, rule_row in df_rules.iterrows():
            is_active = (i == active_idx)
            bg    = "#f0fdf4" if is_active else "#ffffff"
            lbdr  = "4px solid #22c55e" if is_active else "1px solid #e5e7eb"
            bdr   = "#bbf7d0" if is_active else "#e5e7eb"
            tipo_bg  = "#dcfce7" if "alta" in str(rule_row.get("tipo", "")) else "#eff6ff"
            tipo_clr = "#15803d" if "alta" in str(rule_row.get("tipo", "")) else "#1d4ed8"
            active_badge = (
                '<span style="font-size:11px;font-weight:700;color:#16a34a;">● ACTIVA</span>'
                if is_active else ""
            )
            st.markdown(
                f'<div style="background:{bg};border:1px solid {bdr};border-radius:10px;'
                f'border-left:{lbdr};padding:12px 16px;margin-bottom:8px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'margin-bottom:6px;">'
                f'<span style="background:{tipo_bg};color:{tipo_clr};font-size:11px;font-weight:700;'
                f'padding:3px 10px;border-radius:8px;">{rule_row.get("tipo","—")}</span>'
                f'<span style="font-size:12px;color:#6b7280;">IEC mediana: '
                f'<b style="color:#16a34a;">{float(rule_row.get("iec_mediana",0)):.2f}</b>'
                f' · n={int(rule_row.get("soporte_obs",0))}</span>'
                f'{active_badge}'
                f'</div>'
                f'<div style="font-size:12px;color:#374151;line-height:1.6;">{rule_row.get("regla","—")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.caption(
        "Azul sólido = ángulo actual del registro · verde discontinuo = ángulo óptimo histórico"
    )


def render_tab_estado(
    df_modelo: pd.DataFrame,
    df_diagnostic: pd.DataFrame,
    df_rules: pd.DataFrame,
) -> None:
    _render_interactive_section(df_modelo, df_rules)

    st.markdown("<hr style='border-color:#e5e7eb;margin:24px 0 16px;'>", unsafe_allow_html=True)

    # ── Static section: trackers + alerts (not in fragment) ───────────────────
    anomalous = get_anomalous_trackers(df_diagnostic, threshold=_ANOMALY_THRESHOLD)
    alerts    = build_alert_list(df_diagnostic, df_modelo)

    col_trackers, col_alerts = st.columns([2, 1])

    with col_trackers:
        st.markdown(
            '<div style="font-size:13px;font-weight:700;color:#111827;text-transform:uppercase;'
            'letter-spacing:0.06em;margin-bottom:10px;">🔩 Estado de los 10 trackers</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(5)
        for i, tracker_id in enumerate(_ALL_TRACKERS):
            is_anomaly = tracker_id in anomalous
            diag_rows  = [r for r in df_diagnostic.index if tracker_id in r]
            variance   = float(df_diagnostic.loc[diag_rows[0], "varianza_deg2"]) if diag_rows else float("nan")
            bg   = "#fef2f2" if is_anomaly else "#f0fdf4"
            bdr  = "#fca5a5" if is_anomaly else "#bbf7d0"
            clr  = COLOR["red"] if is_anomaly else COLOR["green"]
            icon = " ⚠" if is_anomaly else ""
            with cols[i % 5]:
                st.markdown(
                    f'<div style="background:{bg};border:1px solid {bdr};border-radius:8px;'
                    f'padding:9px;text-align:center;margin-bottom:6px;">'
                    f'<div style="font-size:13px;font-weight:700;color:{clr};">{tracker_id}{icon}</div>'
                    f'<div style="font-size:11px;color:#6b7280;margin-top:3px;">{variance:.0f} deg²</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_alerts:
        if alerts:
            st.markdown(
                f'<div style="font-size:13px;font-weight:700;color:#111827;text-transform:uppercase;'
                f'letter-spacing:0.06em;margin-bottom:8px;">🚨 Alertas activas ({len(alerts)})</div>',
                unsafe_allow_html=True,
            )
            for alert in alerts:
                sev_color = COLOR["red"] if alert["severity"] == "CRÍTICO" else COLOR["orange"]
                sev_bg    = "#fef2f2" if alert["severity"] == "CRÍTICO" else "#fff7ed"
                st.markdown(
                    f'<div style="background:{sev_bg};border-radius:8px;padding:12px;margin-bottom:8px;">'
                    f'<div style="font-size:13px;font-weight:700;color:#111827;">{alert["title"]}</div>'
                    f'<div style="font-size:11px;color:#6b7280;margin-top:4px;line-height:1.5;">'
                    f'{alert["description"]}</div>'
                    f'<div style="display:inline-block;background:{sev_color};color:#fff;font-size:10px;'
                    f'font-weight:700;padding:2px 8px;border-radius:6px;margin-top:6px;">'
                    f'{alert["severity"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("Sin alertas activas.")
```

- [ ] **Step 2: Commit**

```bash
git add sprint3/tabs/tab_estado.py
git commit -m "feat(sprint3): rewrite tab_estado as interactive home with @st.fragment"
```

---

## Task 3: Update app.py — 4 tabs, remove tab_panel_solar

**Files:**
- Modify: `sprint3/app.py`
- Delete: `sprint3/tabs/tab_panel_solar.py`

- [ ] **Step 1: Replace the entire content of `sprint3/app.py` with:**

```python
import streamlit as st

# Page config MUST be first Streamlit call
st.set_page_config(
    page_title="Agrovoltaic Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from alert_logic import build_alert_list
from data_loader import (
    load_integrado,
    load_modelo,
    load_rules,
    load_tracker_diagnostic,
)
from styles import inject_styles
from tabs.tab_alertas import render_tab_alertas
from tabs.tab_estado import render_tab_estado
from tabs.tab_recomendacion import render_tab_recomendacion
from tabs.tab_series import render_tab_series

# ── Inject CSS ────────────────────────────────────────────────────────────────
inject_styles()

# ── Load data (cached) ────────────────────────────────────────────────────────
df_modelo     = load_modelo()
df_integrado  = load_integrado()
df_rules      = load_rules()
df_diagnostic = load_tracker_diagnostic()

# ── Header ────────────────────────────────────────────────────────────────────
col_logo, col_title, col_badge = st.columns([0.06, 0.8, 0.14])
with col_logo:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#16a34a,#15803d);'
        'border-radius:10px;width:44px;height:44px;display:flex;align-items:center;'
        'justify-content:center;font-size:22px;box-shadow:0 2px 8px rgba(22,163,74,0.3);">'
        '🌿</div>',
        unsafe_allow_html=True,
    )
with col_title:
    st.markdown(
        '<div style="padding-top:2px;">'
        '<span style="font-size:20px;font-weight:700;color:#111827;letter-spacing:-0.02em;">'
        'Agrovoltaic Decision Dashboard</span><br>'
        '<span style="font-size:13px;color:#6b7280;">Sostenibilidad y Ciencia · Análisis Operativo</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with col_badge:
    n_alerts  = len(build_alert_list(df_diagnostic, df_modelo))
    badge_clr = "#dc2626" if n_alerts > 0 else "#16a34a"
    badge_bg  = "#fef2f2" if n_alerts > 0 else "#f0fdf4"
    badge_bdr = "#fca5a5" if n_alerts > 0 else "#bbf7d0"
    badge_txt = (
        f"⚠️ {n_alerts} alerta{'s' if n_alerts != 1 else ''}"
        if n_alerts > 0 else "● Sistema activo"
    )
    st.markdown(
        f'<div style="text-align:right;padding-top:6px;">'
        f'<span style="background:{badge_bg};border:1px solid {badge_bdr};'
        f'color:{badge_clr};font-size:13px;font-weight:600;padding:5px 14px;border-radius:20px;">'
        f'{badge_txt}</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin:4px 0;'></div>", unsafe_allow_html=True)

# ── Tabs (4 tabs) ─────────────────────────────────────────────────────────────
alerts_label = f"🚨 Alertas ({n_alerts})" if n_alerts > 0 else "🚨 Alertas"

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "📈 Series temporales",
    "🔄 Recomendación",
    alerts_label,
])

with tab1:
    render_tab_estado(df_modelo, df_diagnostic, df_rules)
with tab2:
    render_tab_series(df_integrado)
with tab3:
    render_tab_recomendacion(df_rules, df_modelo)
with tab4:
    render_tab_alertas(df_diagnostic, df_modelo)
```

- [ ] **Step 2: Delete `tab_panel_solar.py`**

```bash
git rm sprint3/tabs/tab_panel_solar.py
```

- [ ] **Step 3: Commit**

```bash
git add sprint3/app.py
git commit -m "feat(sprint3): drop to 4 tabs, interactive Dashboard replaces Panel Solar"
```

---

## Self-review

**Spec coverage:**
- ✓ `@st.fragment` for instant slider response → `_render_interactive_section` decorated
- ✓ Hour slider drives SVG, IEC, angles, regime, ePAR, VWC, rules → all inside fragment
- ✓ Solar SVG prominent in Tab 1 → `col_svg` is 3/5 width
- ✓ Rules table below panel in Tab 1 → at bottom of fragment
- ✓ Tracker grid and alerts static (outside fragment) → in `render_tab_estado` after fragment call
- ✓ Typography larger: base 15px, card labels 13px, card values 30px, gauge values 42px
- ✓ Tab 3 eliminated, app drops to 4 tabs
- ✓ `tab_panel_solar.py` deleted via `git rm`

**Type consistency:**
- `_get_hour_record(df_modelo, hour: int) → pd.Series` — used in `_render_interactive_section` ✓
- `get_recommended_angle(hour, df_modelo)` — signature matches `solar_logic.py` ✓
- `get_active_rule_index(df_rules, iec_safe)` — returns `int | None`, used in loop as `i == active_idx` ✓
- `generate_solar_svg(hour, track_angle, rec_angle, solar_elevation, irradiance)` — all floats ✓
- `card_html(title, value, subtitle, color)` — all strings ✓
- `iec_gauge_html(iec_safe)` — receives `float` (never NaN) ✓

**Placeholder scan:** No TBDs, no TODOs, no incomplete steps found.
