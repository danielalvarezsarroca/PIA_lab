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
n_alerts      = len(build_alert_list(df_diagnostic, df_modelo))

# ── Header ────────────────────────────────────────────────────────────────────
status_class = "alert" if n_alerts > 0 else "ok"
status_txt = (
    f"{n_alerts} alerta{'s' if n_alerts != 1 else ''} activa{'s' if n_alerts != 1 else ''}"
    if n_alerts > 0 else "Sistema activo"
)
st.markdown(
    f"""
    <header class="app-header">
      <div class="app-brand">
        <div class="app-mark">SAMO</div>
        <div>
          <div class="app-kicker">Agrovoltaica · Sprint 3</div>
          <div class="app-title">Agrovoltaic Decision Dashboard</div>
          <div class="app-subtitle">
            Monitorización operativa de trackers, cultivo y equilibrio energía-cultivo.
          </div>
        </div>
      </div>
      <div class="app-header-meta">
        <span class="status-pill {status_class}">{status_txt}</span>
        <span class="meta-note">Datos integrados · resolución 6h</span>
      </div>
    </header>
    """,
    unsafe_allow_html=True,
)

# ── Tabs (4 tabs) ─────────────────────────────────────────────────────────────
alerts_label = f"Alertas ({n_alerts})" if n_alerts > 0 else "Alertas"

tab1, tab2, tab3, tab4 = st.tabs([
    "Dashboard",
    "Series temporales",
    "Recomendación",
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
