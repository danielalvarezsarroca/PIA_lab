import pandas as pd
import pytest
from rule_engine import evaluate_rule_condition, format_regime_label, get_active_rule_index

_RULES = pd.DataFrame({
    "tipo": ["prioridad_alta", "prioridad_alta", "prioridad_media"],
    "regla": ["Regla A texto", "Regla B texto", "Regla C texto"],
    "soporte_obs": [33, 20, 50],
    "iec_mediana": [0.86, 0.60, 0.40],
    "comentario": ["com A", "com B", "com C"],
})


def test_active_rule_closest_iec():
    idx = get_active_rule_index(_RULES, current_record=0.65)
    assert idx == 1


def test_active_rule_high_iec():
    idx = get_active_rule_index(_RULES, current_record=0.90)
    assert idx == 0


def test_active_rule_nan_returns_none():
    idx = get_active_rule_index(_RULES, current_record=float("nan"))
    assert idx is None


def test_active_rule_empty_df_returns_none():
    idx = get_active_rule_index(pd.DataFrame(columns=["iec_mediana"]), current_record=0.5)
    assert idx is None


def test_active_rule_uses_real_conditions_for_tracking_pm_hour():
    rules = pd.DataFrame({
        "tipo": ["prioridad_alta", "operativa", "operativa"],
        "regla": [
            "Si Albedo_S1 > 55.7 y la elevacion solar teorica supera 68 grados, priorizar tracking activo de la tarde y evitar modos conservadores.",
            "Si la franja es 12:00 y el sistema opera en TRACKING_PM, mantener un angulo cercano a 31.8 grados",
            "Si la franja es 06:00 y el sistema opera en TRACKING_AM, mantener un angulo cercano a -32.2 grados",
        ],
        "soporte_obs": [33, 75, 10],
        "iec_mediana": [0.862, 0.769, 0.602],
        "comentario": ["", "", ""],
    })
    record = pd.Series({
        "hour_of_day": 12,
        "tracking_regime": "TRACKING_PM",
        "Albedo_S1": 40.0,
        "solar_elevation_deg": 72.0,
        "IEC": 0.61,
    })
    assert get_active_rule_index(rules, current_record=record) == 1


def test_active_rule_does_not_mark_closest_iec_when_condition_is_false():
    rules = pd.DataFrame({
        "tipo": ["cautela_hidrica"],
        "regla": [
            "Si Albedo_S1 <= 55.7, Albedo_S2 <= 18.0, VWC_S1 <= 22.2 y GPOA_S2 <= 35.5, evitar forzar una politica orientada a produccion: el IEC esperado es muy bajo."
        ],
        "soporte_obs": [43],
        "iec_mediana": [0.093],
        "comentario": [""],
    })
    record = pd.Series({
        "Albedo_S1": 80.0,
        "Albedo_S2": 40.0,
        "VWC_S1_mean": 30.0,
        "GPOA_S2": 100.0,
        "IEC": 0.09,
    })
    assert get_active_rule_index(rules, current_record=record) is None


def test_evaluate_rule_condition_uses_vwc_percent_scale_for_transition_rule():
    rule_text = "Si Albedo_S1 <= 55.7 pero Albedo_S2 > 18.0 y VWC_S1 > 20.0, usar tracking suave o una transicion controlada antes que HORIZONTAL permanente."
    record = pd.Series({"Albedo_S1": 50.0, "Albedo_S2": 20.0, "VWC_S1_mean": 21.0})
    assert evaluate_rule_condition(rule_text, record) is True


def test_format_regime_label_known():
    assert format_regime_label("TRACKING_PM") == "Tracking tarde (óptimo)"
    assert format_regime_label("TRACKING_AM") == "Tracking mañana"
    assert format_regime_label("HORIZONTAL") == "Horizontal (mínimo)"


def test_format_regime_label_unknown():
    assert format_regime_label("UNKNOWN") == "UNKNOWN"
