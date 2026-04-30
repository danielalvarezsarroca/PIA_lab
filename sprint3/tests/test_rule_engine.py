import pandas as pd
import pytest
from rule_engine import get_active_rule_index, format_regime_label

_RULES = pd.DataFrame({
    "tipo": ["prioridad_alta", "prioridad_alta", "prioridad_media"],
    "regla": ["Regla A texto", "Regla B texto", "Regla C texto"],
    "soporte_obs": [33, 20, 50],
    "iec_mediana": [0.86, 0.60, 0.40],
    "comentario": ["com A", "com B", "com C"],
})


def test_active_rule_closest_iec():
    idx = get_active_rule_index(_RULES, current_iec=0.65)
    assert idx == 1


def test_active_rule_high_iec():
    idx = get_active_rule_index(_RULES, current_iec=0.90)
    assert idx == 0


def test_active_rule_nan_returns_none():
    idx = get_active_rule_index(_RULES, current_iec=float("nan"))
    assert idx is None


def test_active_rule_empty_df_returns_none():
    idx = get_active_rule_index(pd.DataFrame(columns=["iec_mediana"]), current_iec=0.5)
    assert idx is None


def test_format_regime_label_known():
    assert format_regime_label("TRACKING_PM") == "Tracking tarde (óptimo)"
    assert format_regime_label("TRACKING_AM") == "Tracking mañana"
    assert format_regime_label("HORIZONTAL") == "Horizontal (mínimo)"


def test_format_regime_label_unknown():
    assert format_regime_label("UNKNOWN") == "UNKNOWN"
