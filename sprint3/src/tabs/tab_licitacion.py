from __future__ import annotations

import pandas as pd
import streamlit as st

from licitacion_system import build_tender_demo_system


def _plain_action(value: object) -> str:
    text = str(value or "sin datos").replace("_", " ").strip()
    return text[:1].upper() + text[1:] if text else "Sin datos"


def _metric_card(title: str, value: object, caption: str = "", color: str = "#2f80ed") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-title">{title}</div>
          <div class="metric-value" style="color:{color};">{value}</div>
          <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_coverage(coverage: list[dict[str, object]]) -> None:
    cols = st.columns(len(coverage))
    for col, item in zip(cols, coverage):
        with col:
            _metric_card(
                str(item["apartado"]),
                _plain_action(item["status"]),
                str(item["entregable"]),
                "#4f8f68",
            )


def _render_decision_card(title: str, decision: dict[str, object]) -> None:
    st.markdown(f"#### {title}")
    cols = st.columns(3)
    with cols[0]:
        angle = decision.get("target_angle_deg")
        _metric_card("Angulo objetivo", "Sin datos" if angle is None else f"{angle:.1f}°", str(decision.get("source", "")))
    with cols[1]:
        _metric_card("Placas", _plain_action(decision.get("panel_action")), "Accion propuesta", "#705bd6")
    with cols[2]:
        _metric_card("Cultivo", _plain_action(decision.get("crop_management_action")), str(decision.get("confidence_label", "")), "#4f8f68")
    st.caption(str(decision.get("explanation", "")))


def render_tab_licitacion(
    df_modelo: pd.DataFrame,
    df_crop_risk: pd.DataFrame | None,
    df_decision_policy: pd.DataFrame | None,
) -> None:
    st.markdown("### Sistema DSS para licitacion")
    st.caption(
        "Primera version demostrable: variables biologicas, gemelo digital, comparacion de modelos, "
        "escenarios sinteticos y propuesta de control."
    )

    if df_modelo is None or df_modelo.empty:
        st.warning("No hay datos historicos cargados para construir la demo.")
        return

    demo = build_tender_demo_system(df_modelo, df_crop_risk, df_decision_policy)

    st.markdown("#### Cobertura de la licitacion")
    _render_coverage(demo["coverage"])

    twin = demo["digital_twin"]
    st.markdown("#### Gemelo digital actual")
    twin_cols = st.columns(5)
    with twin_cols[0]:
        _metric_card("Zona", twin["crop_zone"], str(twin["crop_type"]))
    with twin_cols[1]:
        _metric_card("Angulo actual", f"{twin['current_angle_deg']:.1f}°", str(twin["time"]))
    with twin_cols[2]:
        _metric_card("Humedad suelo", f"{twin['soil_moisture']:.2f}%", "Variable directa")
    with twin_cols[3]:
        _metric_card("Temp. suelo", f"{twin['soil_temperature_c']:.2f} °C", "Variable directa")
    with twin_cols[4]:
        _metric_card("Sol en placas", f"{twin['panel_light_wm2']:.1f}", "GPOA_mean", "#b35b24")

    st.markdown("#### Comparacion DSS")
    dss = demo["dss_comparison"]
    left, right = st.columns(2)
    with left:
        _render_decision_card("Modelo aprendido DQN", dss["dqn"])
    with right:
        _render_decision_card("Modelo biologico simple", dss["biological"])

    comparison = dss["comparison"]
    st.info(
        f"{comparison['conclusion']} "
        f"Diferencia de angulo: {comparison['angle_delta_deg']}°. "
        f"Placas coinciden: {'si' if comparison['panel_match'] else 'no'}."
    )

    control = demo["control_law"]
    st.markdown("#### Propuesta de control")
    control_cols = st.columns(4)
    with control_cols[0]:
        _metric_card("Modo", _plain_action(control["operational_mode"]), str(control["decision_source"]))
    with control_cols[1]:
        _metric_card("Siguiente angulo", f"{control['target_angle_deg']:.1f}°", "Orden candidata")
    with control_cols[2]:
        _metric_card("Placas", _plain_action(control["panel_action"]), "Con limites de seguridad", "#705bd6")
    with control_cols[3]:
        _metric_card("Cultivo", _plain_action(control["crop_management_action"]), "Accion sobre riego/cultivo", "#4f8f68")
    st.caption(control["safety_limits"])

    st.markdown("#### Escenarios sinteticos")
    st.dataframe(demo["synthetic_scenarios"], use_container_width=True, hide_index=True)

    st.markdown("#### Variables y restricciones")
    st.dataframe(demo["variables"], use_container_width=True, hide_index=True)
