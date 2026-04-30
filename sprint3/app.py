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
    load_high_iec,
    load_integrado,
    load_modelo,
    load_rules,
    load_tracker_diagnostic,
)
from styles import inject_styles
from tabs.tab_alertas import render_tab_alertas
from tabs.tab_estado import render_tab_estado
from tabs.tab_panel_solar import render_tab_panel_solar
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
        'border-radius:10px;width:40px;height:40px;display:flex;align-items:center;'
        'justify-content:center;font-size:20px;box-shadow:0 2px 8px rgba(22,163,74,0.3);">'
        '🌿</div>',
        unsafe_allow_html=True,
    )
with col_title:
    st.markdown(
        '<div style="padding-top:2px;">'
        '<span style="font-size:18px;font-weight:700;color:#111827;letter-spacing:-0.02em;">'
        'Agrovoltaic Decision Dashboard</span><br>'
        '<span style="font-size:11px;color:#6b7280;">Sostenibilidad y Ciencia · Análisis Operativo</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with col_badge:
    n_alerts = len(build_alert_list(df_diagnostic, df_modelo))
    badge_clr = "#dc2626" if n_alerts > 0 else "#16a34a"
    badge_bg  = "#fef2f2" if n_alerts > 0 else "#f0fdf4"
    badge_bdr = "#fca5a5" if n_alerts > 0 else "#bbf7d0"
    st.markdown(
        f'<div style="text-align:right;padding-top:4px;">'
        f'<span style="background:{badge_bg};border:1px solid {badge_bdr};'
        f'color:{badge_clr};font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;">'
        f'{"⚠️ " + str(n_alerts) + " alerta" + ("s" if n_alerts!=1 else "") if n_alerts > 0 else "● Sistema activo"}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin:4px 0;'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
alerts_label = f"🚨 Alertas ({n_alerts})" if n_alerts > 0 else "🚨 Alertas"

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Estado actual",
    "📈 Series temporales",
    "☀️ Panel solar",
    "🔄 Recomendación",
    alerts_label,
])

with tab1:
    render_tab_estado(df_modelo, df_diagnostic, df_rules)
with tab2:
    render_tab_series(df_integrado)
with tab3:
    render_tab_panel_solar(df_modelo)
with tab4:
    render_tab_recomendacion(df_rules, df_modelo)
with tab5:
    render_tab_alertas(df_diagnostic, df_modelo)
