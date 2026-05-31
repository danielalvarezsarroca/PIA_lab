from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from licitacion_system import build_tender_demo_system


ACTION_LABELS = {
    "automatico_con_guardarrailes": "Automático supervisado",
    "automatico_supervisado": "Automático supervisado",
    "aumentar_sombreado": "Aumentar sombra",
    "dqn_no_aplicable": "DQN no aplicable",
    "implementado_demo": "Cubierto en demo",
    "mantener_placas": "Mantener placas",
    "modelo_biologico_simple": "Regla biológica",
    "offline_dqn_double_dqn": "DQN offline",
    "posicion_segura": "Posición segura",
    "reducir_sombreado": "Reducir sombra",
    "riego_pausado": "Riego pausado",
    "sin_datos": "Sin datos",
    "sin_manejo_directo": "Sin manejo directo",
    "sin_politica_dqn": "Sin DQN",
    "supervisado": "Supervisado",
    "activar_riego": "Activar riego",
    "vigilar_crecimiento": "Vigilar crecimiento",
    "proteccion_calor": "Proteger del calor",
}


def _plain_action(value: object) -> str:
    key = str(value or "sin_datos").strip()
    if key in ACTION_LABELS:
        return ACTION_LABELS[key]
    text = key.replace("_", " ").strip()
    return text[:1].upper() + text[1:] if text else "Sin datos"


def _metric_card(title: str, value: object, caption: str = "", color: str = "#2f80ed") -> None:
    title_html = escape(str(title))
    value_html = escape(str(value))
    caption_html = escape(str(caption))
    color_html = escape(str(color))
    st.markdown(
        f"""
        <div class="metric-card tender-metric-card">
          <div class="metric-title">{title_html}</div>
          <div class="metric-value" style="color:{color_html};">{value_html}</div>
          <div class="metric-caption">{caption_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_tender_styles() -> None:
    st.markdown(
        """
        <style>
        .tender-hero {
            margin: 0 0 1.3rem;
            padding: 1.2rem 0 0.35rem;
            border-bottom: 1px solid rgba(41, 52, 65, 0.12);
        }
        .tender-eyebrow {
            color: #4f8f68;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0;
            text-transform: uppercase;
        }
        .tender-hero h2 {
            margin: 0.22rem 0 0.35rem;
            color: #1d232b;
            font-size: 2rem;
            line-height: 1.16;
        }
        .tender-subtitle {
            max-width: 920px;
            color: #65707c;
            font-size: 1rem;
            line-height: 1.55;
        }
        .tender-proof-row,
        .tender-readiness-grid {
            display: grid;
            gap: 0.75rem;
            margin: 1rem 0 1.4rem;
        }
        .tender-proof-row {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
        .tender-readiness-grid {
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }
        .tender-proof,
        .tender-panel {
            border: 1px solid rgba(41, 52, 65, 0.1);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.72);
            padding: 0.95rem 1rem;
            box-shadow: 0 10px 28px rgba(31, 44, 60, 0.06);
        }
        .tender-proof-value {
            color: #1d232b;
            font-size: 1.25rem;
            font-weight: 800;
            line-height: 1.2;
        }
        .tender-proof-label,
        .tender-panel p,
        .tender-callout {
            color: #596574;
            line-height: 1.45;
        }
        .tender-proof-label {
            margin-top: 0.25rem;
            font-size: 0.9rem;
        }
        .tender-panel h5 {
            margin: 0 0 0.4rem;
            color: #242a33;
            font-size: 1rem;
        }
        .tender-panel p {
            margin: 0;
            font-size: 0.94rem;
        }
        .tender-status {
            display: inline-block;
            margin-bottom: 0.45rem;
            color: #4f8f68;
            font-weight: 800;
        }
        .tender-callout {
            margin: 1rem 0 1.3rem;
            padding: 0.9rem 1rem;
            border-left: 4px solid #4f8f68;
            border-radius: 6px;
            background: rgba(79, 143, 104, 0.09);
        }
        .tender-small {
            color: #7b8490;
            font-size: 0.86rem;
            line-height: 1.4;
        }
        .tender-metric-card {
            min-height: 118px;
        }
        .tender-metric-card .metric-value {
            line-height: 1.15;
            overflow-wrap: anywhere;
        }
        .tender-metric-card .metric-caption {
            min-height: 1.1rem;
        }
        @media (max-width: 900px) {
            .tender-proof-row,
            .tender-readiness-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    st.markdown(
        """
        <section class="tender-hero">
          <div class="tender-eyebrow">Licitación · Decision Support System</div>
          <h2>Sistema DSS para licitación agrivoltaica</h2>
          <div class="tender-subtitle">
            Versión demostrable para explicar qué puede hacer hoy el proyecto, qué falta para
            llevarlo a piloto real y cómo se podría planificar una entrega completa.
          </div>
          <div class="tender-proof-row">
            <div class="tender-proof">
              <div class="tender-proof-value">5/5 bloques</div>
              <div class="tender-proof-label">Cubiertos como primera demo funcional.</div>
            </div>
            <div class="tender-proof">
              <div class="tender-proof-value">DQN + regla biológica</div>
              <div class="tender-proof-label">Comparación entre modelo aprendido y criterio interpretable.</div>
            </div>
            <div class="tender-proof">
              <div class="tender-proof-value">Control supervisado</div>
              <div class="tender-proof-label">Recomendación lista para validar antes de actuar en planta.</div>
            </div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_bid_answer() -> None:
    st.markdown("#### Respuesta ejecutiva")
    st.markdown(
        """
        <div class="tender-readiness-grid">
          <div class="tender-panel">
            <h5>Qué podemos responder ya</h5>
            <p>Variables, restricciones, gemelo digital, DSS comparativo, escenarios sintéticos y propuesta de control.</p>
          </div>
          <div class="tender-panel">
            <h5>Qué falta para producción</h5>
            <p>Conectar datos en vivo, validar en campo, calibrar más cultivos y cerrar integración con el controlador real.</p>
          </div>
          <div class="tender-panel">
            <h5>Capacidad de cierre</h5>
            <p>Ya hay pipeline de 10 minutos, política DQN, reglas biológicas y métricas offline para medir mejora.</p>
          </div>
          <div class="tender-panel">
            <h5>Mensaje para la empresa</h5>
            <p>La demo reduce riesgo: enseña la arquitectura completa antes de invertir en despliegue de planta.</p>
          </div>
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


def _format_angle(value: object) -> str:
    if value is None or pd.isna(value):
        return "Sin datos"
    return f"{float(value):.1f}°"


def _render_decision_card(title: str, decision: dict[str, object]) -> None:
    st.markdown(f"#### {title}")
    cols = st.columns(3)
    with cols[0]:
        angle = decision.get("target_angle_deg")
        _metric_card("Ángulo objetivo", _format_angle(angle), _plain_action(decision.get("source", "")))
    with cols[1]:
        _metric_card("Placas", _plain_action(decision.get("panel_action")), "Acción propuesta", "#705bd6")
    with cols[2]:
        _metric_card("Cultivo", _plain_action(decision.get("crop_management_action")), str(decision.get("confidence_label", "")), "#4f8f68")
    st.caption(str(decision.get("explanation", "")))


def _comparison_text(comparison: dict[str, object]) -> str:
    panel_text = "sí" if comparison.get("panel_match") else "no"
    crop_text = "sí" if comparison.get("crop_match") else "no"
    return (
        f"{comparison['conclusion']} "
        f"Diferencia de ángulo: {comparison['angle_delta_deg']}°. "
        f"Placas coinciden: {panel_text}. Cultivo coincide: {crop_text}."
    )


def _friendly_synthetic_scenarios(frame: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "escenario": "Escenario",
        "humedad_suelo": "Humedad suelo (%)",
        "temp_suelo_c": "Temp. suelo (°C)",
        "luz_cultivo": "Luz cultivo",
        "luz_placas_wm2": "Luz placas (W/m²)",
        "angulo_solar": "Altura sol (°)",
        "salud_cultivo_pct": "Salud cultivo (%)",
        "eficiencia_energetica_pct": "Eficiencia energética (%)",
        "uso_demo": "Para qué sirve",
    }
    return frame.rename(columns=rename)


def _friendly_variables(frame: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "variable": "Variable técnica",
        "nombre_simple": "Nombre simple",
        "uso_en_sistema": "Uso en el sistema",
        "restriccion_biologica": "Restricción biológica",
    }
    return frame.rename(columns=rename)


def _render_plan_budget() -> None:
    st.markdown("#### Plan temporal y presupuesto")
    cols = st.columns(4)
    phases = [
        ("Fase 1", "2 semanas", "Datos, acceso y validación de sensores."),
        ("Fase 2", "4 semanas", "Gemelo digital y reglas biológicas calibradas."),
        ("Fase 3", "4 semanas", "Datos sintéticos, entrenamiento y evaluación DSS."),
        ("Fase 4", "4-6 semanas", "Integración con control y prueba piloto supervisada."),
    ]
    for col, (title, value, caption) in zip(cols, phases):
        with col:
            _metric_card(title, value, caption, "#1d232b")

    st.markdown(
        """
        <div class="tender-callout">
          <strong>Presupuesto orientativo:</strong> 70k-110k EUR para una primera versión de producción
          con conexión a datos reales, validación agronómica, módulo de datos sintéticos y prueba piloto.
          La demo actual sirve para defender alcance, arquitectura y viabilidad técnica.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tab_licitacion(
    df_modelo: pd.DataFrame,
    df_crop_risk: pd.DataFrame | None,
    df_decision_policy: pd.DataFrame | None,
) -> None:
    _render_tender_styles()
    _render_hero()

    if df_modelo is None or df_modelo.empty:
        st.warning("No hay datos históricos cargados para construir la demo.")
        return

    demo = build_tender_demo_system(df_modelo, df_crop_risk, df_decision_policy)

    _render_bid_answer()

    st.markdown("#### Cobertura de la licitación")
    _render_coverage(demo["coverage"])

    twin = demo["digital_twin"]
    st.markdown("#### Gemelo digital del piloto")
    st.caption(str(twin.get("snapshot_note", "")))
    twin_cols = st.columns(6)
    with twin_cols[0]:
        _metric_card("Zona", twin["crop_zone"], str(twin["crop_type"]))
    with twin_cols[1]:
        _metric_card("Instante usado", str(twin["time"]), "Registro histórico")
    with twin_cols[2]:
        _metric_card("Ángulo actual", f"{twin['current_angle_deg']:.1f}°", "track_mean")
    with twin_cols[3]:
        _metric_card("Humedad suelo", f"{twin['soil_moisture']:.2f}%", "VWC_S1_mean")
    with twin_cols[4]:
        _metric_card("Temp. suelo", f"{twin['soil_temperature_c']:.2f} °C", "Tsoil_S1_mean")
    with twin_cols[5]:
        _metric_card("Sol en placas", f"{twin['panel_light_wm2']:.1f}", "GPOA_mean", "#b35b24")

    st.markdown("#### Comparación DSS")
    dss = demo["dss_comparison"]
    left, right = st.columns(2)
    with left:
        _render_decision_card("Modelo aprendido DQN", dss["dqn"])
    with right:
        _render_decision_card("Modelo biológico simple", dss["biological"])

    comparison = dss["comparison"]
    st.info(_comparison_text(comparison))

    control = demo["control_law"]
    st.markdown("#### Propuesta de control")
    control_cols = st.columns(4)
    with control_cols[0]:
        _metric_card("Modo", _plain_action(control["operational_mode"]), str(control["decision_source"]))
    with control_cols[1]:
        _metric_card("Siguiente ángulo", f"{control['target_angle_deg']:.1f}°", "Orden candidata")
    with control_cols[2]:
        _metric_card("Placas", _plain_action(control["panel_action"]), "Con límites de seguridad", "#705bd6")
    with control_cols[3]:
        _metric_card("Cultivo", _plain_action(control["crop_management_action"]), "Acción sobre riego/cultivo", "#4f8f68")
    st.caption(control["safety_limits"])

    st.markdown("#### Escenarios sintéticos")
    st.caption("Cambios controlados alrededor del estado actual para comprobar cómo responde el DSS.")
    st.dataframe(_friendly_synthetic_scenarios(demo["synthetic_scenarios"]), use_container_width=True, hide_index=True)

    st.markdown("#### Variables y restricciones")
    st.caption("Catálogo de entradas que conectan sensores, cultivo, energía y restricciones biológicas.")
    st.dataframe(_friendly_variables(demo["variables"]), use_container_width=True, hide_index=True)

    _render_plan_budget()
