from __future__ import annotations

import math
from typing import Any

import pandas as pd

from rl_policy import recommend_action_for_record


VARIABLE_CATALOG_ROWS = [
    {
        "variable": "GPOA_mean",
        "nombre_simple": "Luz que llega a las placas",
        "uso_en_sistema": "Mide cuanta energia puede aprovechar el panel.",
        "restriccion_biologica": "No debe maximizarse si deja el cultivo sin luz o con exceso de calor.",
    },
    {
        "variable": "ePAR_S1_mean",
        "nombre_simple": "Luz util para el cultivo",
        "uso_en_sistema": "Aproxima la luz que puede usar la planta para crecer.",
        "restriccion_biologica": "Valores bajos durante muchas horas pueden limitar crecimiento.",
    },
    {
        "variable": "VWC_S1_mean",
        "nombre_simple": "Humedad del suelo",
        "uso_en_sistema": "Indica si el cultivo tiene agua suficiente.",
        "restriccion_biologica": "Por debajo de 20 se considera riesgo de falta de agua.",
    },
    {
        "variable": "Tsoil_S1_mean",
        "nombre_simple": "Temperatura del suelo",
        "uso_en_sistema": "Ayuda a detectar estres por calor o frio en raiz.",
        "restriccion_biologica": "Por encima de 30 C se prioriza proteger el cultivo.",
    },
    {
        "variable": "solar_elevation_deg",
        "nombre_simple": "Altura del sol",
        "uso_en_sistema": "Situa el momento del dia y la utilidad de mover placas.",
        "restriccion_biologica": "De noche no se recomienda optimizar energia solar.",
    },
    {
        "variable": "track_mean",
        "nombre_simple": "Angulo actual de placas",
        "uso_en_sistema": "Permite comparar la posicion real con el objetivo recomendado.",
        "restriccion_biologica": "El cambio debe respetar limites fisicos y evitar oscilaciones.",
    },
]


TENDER_COVERAGE_ROWS = [
    {
        "id": "i",
        "apartado": "Variables y restricciones",
        "status": "implementado_demo",
        "entregable": "Catalogo operativo de variables, limites biologicos y uso en decisiones.",
    },
    {
        "id": "ii",
        "apartado": "Gemelo digital del piloto",
        "status": "implementado_demo",
        "entregable": "Foto viva del estado actual con sensor, cultivo y recomendacion.",
    },
    {
        "id": "iii",
        "apartado": "DSS comparativo",
        "status": "implementado_demo",
        "entregable": "Comparacion entre recomendacion DQN y regla biologica interpretable.",
    },
    {
        "id": "iv",
        "apartado": "Datos sinteticos",
        "status": "implementado_demo",
        "entregable": "Escenarios que modifican clima, suelo y radiacion alrededor del estado actual.",
    },
    {
        "id": "v",
        "apartado": "Conexion con control agri-PV",
        "status": "implementado_demo",
        "entregable": "Ley de control candidata con angulo objetivo, accion de placas y fallback.",
    },
]


def _finite_float(value: Any, fallback: float = float("nan")) -> float:
    try:
        if pd.isna(value):
            return fallback
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if math.isfinite(parsed) else fallback


def _string_value(value: Any, fallback: str = "Sin datos") -> str:
    if value is None or pd.isna(value):
        return fallback
    text = str(value).replace("_", " ").strip()
    return text[:1].upper() + text[1:] if text else fallback


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pct_from_range(value: float, low: float, high: float) -> float:
    if math.isnan(value):
        return 0.0
    if math.isclose(low, high):
        return 100.0
    return _clip(((value - low) / (high - low)) * 100.0, 0.0, 100.0)


def _latest_representative_record(model_df: pd.DataFrame) -> pd.Series:
    if model_df.empty:
        raise ValueError("No hay datos para construir la demo de licitacion")
    valid = model_df.copy()
    if "Time" in valid.columns:
        valid = valid.sort_values("Time")
    for column in ("GPOA_mean", "track_mean", "solar_elevation_deg"):
        if column in valid.columns:
            rows = valid[pd.to_numeric(valid[column], errors="coerce").notna()]
            if not rows.empty:
                return rows.iloc[-1]
    return valid.iloc[-1]


def _matching_crop_record(crop_risk_df: pd.DataFrame | None, record: pd.Series) -> pd.Series:
    if crop_risk_df is None or crop_risk_df.empty:
        return pd.Series(dtype="object")
    if "Time" in crop_risk_df.columns and "Time" in record.index:
        times = pd.to_datetime(crop_risk_df["Time"], errors="coerce")
        record_time = pd.to_datetime(record.get("Time"), errors="coerce")
        matches = crop_risk_df[times.eq(record_time)]
        if not matches.empty:
            return matches.iloc[-1]
    hour = record.get("hour_of_day")
    if hour is not None and "hour_of_day" in crop_risk_df.columns:
        same_hour = crop_risk_df[pd.to_numeric(crop_risk_df["hour_of_day"], errors="coerce").eq(int(hour))]
        if not same_hour.empty:
            return same_hour.iloc[-1]
    return crop_risk_df.iloc[-1]


def build_variable_catalog() -> pd.DataFrame:
    return pd.DataFrame(VARIABLE_CATALOG_ROWS)


def build_tender_coverage() -> list[dict[str, str]]:
    return [row.copy() for row in TENDER_COVERAGE_ROWS]


def build_digital_twin_snapshot(record: pd.Series, crop_record: pd.Series | None = None) -> dict[str, Any]:
    crop_record = crop_record if crop_record is not None else pd.Series(dtype="object")
    return {
        "time": str(record.get("Time", "Sin datos")),
        "crop_type": str(crop_record.get("crop_type", record.get("crop_type", "lechuga"))),
        "crop_zone": str(crop_record.get("crop_zone", record.get("crop_zone", "S1"))),
        "current_angle_deg": round(_finite_float(record.get("track_mean"), 0.0), 2),
        "solar_elevation_deg": round(_finite_float(record.get("solar_elevation_deg"), 0.0), 2),
        "soil_moisture": round(_finite_float(record.get("VWC_S1_mean"), 0.0), 2),
        "soil_temperature_c": round(_finite_float(record.get("Tsoil_S1_mean"), 0.0), 2),
        "crop_light": round(_finite_float(record.get("ePAR_S1_mean", record.get("PAR_S1")), 0.0), 2),
        "panel_light_wm2": round(_finite_float(record.get("GPOA_mean"), 0.0), 2),
        "stress_type": str(crop_record.get("stress_type", "estable")),
    }


def build_biological_baseline(record: pd.Series, crop_record: pd.Series | None = None) -> dict[str, Any]:
    crop_record = crop_record if crop_record is not None else pd.Series(dtype="object")
    solar_elevation = _finite_float(record.get("solar_elevation_deg"), 0.0)
    current_angle = _finite_float(record.get("track_mean"), 0.0)
    gpoa = _finite_float(record.get("GPOA_mean"), 0.0)
    epar = _finite_float(record.get("ePAR_S1_mean", record.get("PAR_S1")), 0.0)
    vwc = _finite_float(record.get("VWC_S1_mean"), 0.0)
    tsoil = _finite_float(record.get("Tsoil_S1_mean"), 0.0)

    if solar_elevation <= 0:
        panel_action = "posicion_segura"
        crop_action = "sin_manejo_directo"
        target_angle = 0.0
        reason = "Sin sol util, la prioridad es dejar las placas en posicion segura."
    elif vwc < 20 or tsoil > 30:
        panel_action = "aumentar_sombreado"
        crop_action = "activar_riego" if vwc < 20 else "proteccion_calor"
        target_angle = -25.0
        reason = "El cultivo muestra riesgo por agua o temperatura; se prioriza proteccion."
    elif epar < 200 and gpoa > 300:
        panel_action = "reducir_sombreado"
        crop_action = "vigilar_crecimiento"
        target_angle = _clip(current_angle * 0.5, -25.0, 25.0)
        reason = "Hay energia en placas pero poca luz para el cultivo; se abre algo mas la sombra."
    elif gpoa > 700:
        panel_action = "mantener_placas"
        crop_action = "sin_manejo_directo"
        target_angle = _clip(current_angle, -25.0, 25.0)
        reason = "La energia disponible es alta y el cultivo no muestra alerta fuerte."
    else:
        panel_action = "mantener_placas"
        crop_action = str(crop_record.get("crop_management_action", "sin_manejo_directo"))
        target_angle = _clip(current_angle, -25.0, 25.0)
        reason = "Estado estable: se evita mover placas sin una ganancia clara."

    return {
        "source": "modelo_biologico_simple",
        "target_angle_deg": round(target_angle, 2),
        "panel_action": panel_action,
        "crop_management_action": crop_action,
        "confidence_label": "Media",
        "explanation": reason,
    }


def build_dqn_recommendation(
    policy_df: pd.DataFrame | None,
    record: pd.Series,
    crop_record: pd.Series | None = None,
) -> dict[str, Any]:
    if policy_df is None or policy_df.empty:
        return {
            "source": "sin_politica_dqn",
            "target_angle_deg": None,
            "panel_action": "sin_recomendacion",
            "crop_management_action": "sin_recomendacion",
            "confidence_label": "Sin datos",
            "explanation": "No hay politica DQN disponible para este cultivo.",
        }
    record_for_policy = pd.Series(record).copy()
    if crop_record is not None and "stress_type" in crop_record.index:
        record_for_policy["stress_type"] = crop_record.get("stress_type")

    try:
        recommendation = recommend_action_for_record(policy_df, record_for_policy)
    except (ValueError, KeyError, TypeError):
        return {
            "source": "dqn_no_aplicable",
            "target_angle_deg": None,
            "panel_action": "sin_recomendacion",
            "crop_management_action": "sin_recomendacion",
            "confidence_label": "Sin datos",
            "explanation": "La politica DQN no encontro un estado comparable.",
        }

    confidence = _finite_float(recommendation.get("rl_confidence"), float("nan"))
    if math.isnan(confidence):
        confidence_label = "Sin datos"
    elif confidence >= 0.85:
        confidence_label = "Muy alta"
    elif confidence >= 0.65:
        confidence_label = "Alta"
    else:
        confidence_label = "Media"

    return {
        "source": str(recommendation.get("source", "offline_dqn_double_dqn")),
        "target_angle_deg": round(_finite_float(recommendation.get("rl_angle_deg"), 0.0), 2),
        "panel_action": str(recommendation.get("panel_action", "mantener_placas")),
        "crop_management_action": str(recommendation.get("crop_management_action", "sin_manejo_directo")),
        "confidence_label": confidence_label,
        "reward": round(_finite_float(recommendation.get("rl_reward"), 0.0), 4),
        "explanation": "Recomendacion aprendida comparando estados historicos similares.",
    }


def compare_dss_decisions(dqn: dict[str, Any], biological: dict[str, Any]) -> dict[str, Any]:
    dqn_angle = dqn.get("target_angle_deg")
    bio_angle = biological.get("target_angle_deg")
    if dqn_angle is None or bio_angle is None:
        angle_delta = None
    else:
        angle_delta = round(float(dqn_angle) - float(bio_angle), 2)
    panel_match = dqn.get("panel_action") == biological.get("panel_action")
    crop_match = dqn.get("crop_management_action") == biological.get("crop_management_action")
    if panel_match and crop_match:
        conclusion = "Los modelos coinciden: decision de bajo riesgo operativo."
    elif panel_match:
        conclusion = "Coinciden en placas, pero difieren en manejo del cultivo."
    else:
        conclusion = "Hay desacuerdo: conviene revisar variables clave antes de actuar."
    return {
        "angle_delta_deg": angle_delta,
        "panel_match": panel_match,
        "crop_match": crop_match,
        "conclusion": conclusion,
    }


def _scenario_score(vwc: float, tsoil: float, epar: float, gpoa: float, solar_elevation: float) -> tuple[float, float]:
    moisture_score = 100.0 - min(abs(vwc - 28.0) * 4.0, 100.0)
    temp_score = 100.0 - min(abs(tsoil - 24.0) * 7.0, 100.0)
    light_score = _pct_from_range(epar, 120.0, 900.0)
    crop_health = _clip(0.45 * moisture_score + 0.35 * temp_score + 0.20 * light_score, 0.0, 100.0)
    energy = _pct_from_range(gpoa, 0.0, max(900.0, gpoa))
    if solar_elevation < 8:
        energy = min(energy, 10.0)
    return round(crop_health, 1), round(energy, 1)


def build_synthetic_scenarios(record: pd.Series) -> pd.DataFrame:
    base = {
        "VWC_S1_mean": _finite_float(record.get("VWC_S1_mean"), 25.0),
        "Tsoil_S1_mean": _finite_float(record.get("Tsoil_S1_mean"), 24.0),
        "ePAR_S1_mean": _finite_float(record.get("ePAR_S1_mean", record.get("PAR_S1")), 450.0),
        "GPOA_mean": _finite_float(record.get("GPOA_mean"), 600.0),
        "solar_elevation_deg": _finite_float(record.get("solar_elevation_deg"), 35.0),
    }
    scenario_defs = [
        ("Estado actual", 1.0, 0.0, 1.0, 1.0, 0.0, "Referencia para comparar decisiones."),
        ("Dia mas seco", 0.75, 1.5, 0.95, 1.05, 2.0, "Comprueba respuesta ante falta de agua."),
        ("Dia mas calido", 0.95, 4.0, 0.90, 1.05, 4.0, "Comprueba proteccion ante calor."),
        ("Menos radiacion", 1.05, -1.0, 0.65, 0.60, -8.0, "Comprueba si merece mover placas con poca energia."),
        ("Final del dia", 1.0, -2.0, 0.25, 0.20, -30.0, "Comprueba que la energia cae hacia cierre de dia."),
    ]
    rows = []
    for name, vwc_factor, tsoil_delta, epar_factor, gpoa_factor, solar_delta, usage in scenario_defs:
        vwc = _clip(base["VWC_S1_mean"] * vwc_factor, 0.0, 60.0)
        tsoil = _clip(base["Tsoil_S1_mean"] + tsoil_delta, -5.0, 50.0)
        epar = _clip(base["ePAR_S1_mean"] * epar_factor, 0.0, 2000.0)
        gpoa = _clip(base["GPOA_mean"] * gpoa_factor, 0.0, 1400.0)
        solar = _clip(base["solar_elevation_deg"] + solar_delta, -20.0, 90.0)
        crop_health, energy = _scenario_score(vwc, tsoil, epar, gpoa, solar)
        rows.append(
            {
                "escenario": name,
                "humedad_suelo": round(vwc, 2),
                "temp_suelo_c": round(tsoil, 2),
                "luz_cultivo": round(epar, 2),
                "luz_placas_wm2": round(gpoa, 2),
                "angulo_solar": round(solar, 2),
                "salud_cultivo_pct": crop_health,
                "eficiencia_energetica_pct": energy,
                "uso_demo": usage,
            }
        )
    return pd.DataFrame(rows)


def build_control_law_proposal(dqn: dict[str, Any], biological: dict[str, Any], comparison: dict[str, Any]) -> dict[str, Any]:
    has_dqn_angle = dqn.get("target_angle_deg") is not None
    target_angle = dqn.get("target_angle_deg")
    if target_angle is None:
        target_angle = biological.get("target_angle_deg")
        source = "modelo_biologico_simple"
    else:
        source = dqn.get("source", "offline_dqn_double_dqn")
    needs_review = not comparison.get("panel_match", False)
    return {
        "target_angle_deg": target_angle,
        "panel_action": dqn.get("panel_action") if has_dqn_angle else biological.get("panel_action"),
        "crop_management_action": dqn.get("crop_management_action") if has_dqn_angle else biological.get("crop_management_action"),
        "decision_source": source,
        "operational_mode": "supervisado" if needs_review else "automatico_con_guardarrailes",
        "safety_limits": "Mantener angulo entre -25 y 25 grados y revisar si DQN y regla biologica discrepan.",
        "fallback": "Si faltan datos o hay desacuerdo fuerte, aplicar regla biologica simple.",
    }


def build_tender_demo_system(
    model_df: pd.DataFrame,
    crop_risk_df: pd.DataFrame | None = None,
    policy_df: pd.DataFrame | None = None,
) -> dict[str, Any]:
    record = _latest_representative_record(model_df)
    crop_record = _matching_crop_record(crop_risk_df, record)
    biological = build_biological_baseline(record, crop_record)
    dqn = build_dqn_recommendation(policy_df, record, crop_record)
    comparison = compare_dss_decisions(dqn, biological)
    return {
        "coverage": build_tender_coverage(),
        "variables": build_variable_catalog(),
        "digital_twin": build_digital_twin_snapshot(record, crop_record),
        "dss_comparison": {
            "dqn": dqn,
            "biological": biological,
            "comparison": comparison,
        },
        "synthetic_scenarios": build_synthetic_scenarios(record),
        "control_law": build_control_law_proposal(dqn, biological, comparison),
    }
