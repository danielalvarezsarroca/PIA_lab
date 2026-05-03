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
col_logo, col_title, col_badge = st.columns([0.07, 0.68, 0.25])
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
        '<div style="padding-top:1px;min-width:0;line-height:1.25;">'
        '<div style="font-size:22px;font-weight:700;color:#111827;letter-spacing:0;'
        'white-space:normal;overflow:visible;">Agrovoltaic Decision Dashboard</div>'
        '<div style="font-size:13px;color:#6b7280;white-space:normal;overflow:visible;">'
        'Sostenibilidad y Ciencia · Análisis Operativo</div>'
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
