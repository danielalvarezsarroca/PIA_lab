import sys
from pathlib import Path

import streamlit as st

SPRINT3_DIR = Path(__file__).resolve().parents[1]
if str(SPRINT3_DIR) not in sys.path:
    sys.path.insert(0, str(SPRINT3_DIR))

# Page config MUST be first Streamlit call
st.set_page_config(
    page_title="Agrovoltaic Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from alert_logic import build_alert_list
from agricultural_rules import CROP_PROFILES
from data_loader import (
    load_crop_risk,
    load_agricultural_rules_for_crop,
    load_crop_risk_for_crop,
    load_integrado,
    load_modelo,
    load_rl_policy_for_crop,
    load_rules,
    load_tracker_diagnostic,
)
from styles import inject_styles
from tabs.tab_alertas import render_tab_alertas
from tabs.tab_agronomia import render_tab_agronomia
from tabs.tab_estado import render_tab_estado
from tabs.tab_recomendacion import render_tab_recomendacion
from tabs.tab_series import render_tab_series

_CROP_ZONES = ("S1", "S2")

# ── Inject CSS ────────────────────────────────────────────────────────────────
inject_styles()

# ── Load data (cached) ────────────────────────────────────────────────────────
df_modelo     = load_modelo()
df_integrado  = load_integrado()
df_rules      = load_rules()
crop_options = list(CROP_PROFILES.keys()) or ["lechuga"]
selected_crop_zone = str(st.session_state.get("selected_crop_zone", _CROP_ZONES[0]))
if selected_crop_zone not in _CROP_ZONES:
    selected_crop_zone = _CROP_ZONES[0]
st.session_state["selected_crop_zone"] = selected_crop_zone

for crop_zone in _CROP_ZONES:
    zone_key = f"selected_crop_type_{crop_zone.lower()}"
    zone_crop_type = st.session_state.get(
        zone_key,
        st.session_state.get("selected_crop_type", crop_options[0]),
    )
    if isinstance(zone_crop_type, (list, tuple)):
        zone_crop_type = zone_crop_type[0] if zone_crop_type else crop_options[0]
    zone_crop_type = str(zone_crop_type)
    if zone_crop_type not in crop_options:
        zone_crop_type = crop_options[0]
    st.session_state[zone_key] = zone_crop_type

selected_crop_type = st.session_state[f"selected_crop_type_{selected_crop_zone.lower()}"]
st.session_state["selected_crop_type"] = selected_crop_type
df_crop_risk  = load_crop_risk_for_crop(selected_crop_type, crop_zone=selected_crop_zone)
if df_crop_risk.empty:
    df_crop_risk = load_crop_risk(selected_crop_type, crop_zone=selected_crop_zone)
df_agri_rules = load_agricultural_rules_for_crop(selected_crop_type, crop_zone=selected_crop_zone)
df_rl_policy  = load_rl_policy_for_crop(selected_crop_type, crop_zone=selected_crop_zone)
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
        <span class="meta-note">Masterdataset 10 min · política RL offline</span>
      </div>
    </header>
    """,
    unsafe_allow_html=True,
)

# ── Tabs ─────────────────────────────────────────────────────────────────────
alerts_label = f"Alertas ({n_alerts})" if n_alerts > 0 else "Alertas"

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard",
    "Series temporales",
    "Recomendación",
    "Agronomía",
    alerts_label,
])

with tab1:
    render_tab_estado(df_modelo, df_diagnostic, df_rules, df_rl_policy, df_crop_risk)
with tab2:
    render_tab_series(df_integrado)
with tab3:
    render_tab_recomendacion(df_rules, df_modelo, df_rl_policy)
with tab4:
    render_tab_agronomia(df_crop_risk, df_agri_rules, df_rl_policy, df_modelo)
with tab5:
    render_tab_alertas(df_diagnostic, df_modelo)
