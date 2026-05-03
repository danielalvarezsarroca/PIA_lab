import math
import pandas as pd

_REGIME_LABELS: dict[str, str] = {
    "TRACKING_PM": "Tracking tarde (óptimo)",
    "TRACKING_AM": "Tracking mañana",
    "HORIZONTAL":  "Horizontal (mínimo)",
}


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def _num(record: pd.Series, key: str) -> float:
    value = record.get(key, float("nan"))
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def evaluate_rule_condition(rule_text: str, record: pd.Series) -> bool:
    """Evaluate known Sprint 2 candidate rules against the current record."""
    rule = _norm(rule_text)
    hour = int(_num(record, "hour_of_day")) if not math.isnan(_num(record, "hour_of_day")) else None
    regime = str(record.get("tracking_regime", ""))
    albedo_s1 = _num(record, "Albedo_S1")
    albedo_s2 = _num(record, "Albedo_S2")
    vwc_s1 = _num(record, "VWC_S1_mean")
    gpoa_s2 = _num(record, "GPOA_S2")
    solar_elev = _num(record, "solar_elevation_deg")

    if "albedo_s1 > 55.7" in rule and "68 grados" in rule:
        return albedo_s1 > 55.7 and solar_elev > 68.0
    if "franja es 12:00" in rule and "tracking_pm" in rule:
        return hour == 12 and regime == "TRACKING_PM"
    if "franja es 06:00" in rule and "tracking_am" in rule:
        return hour == 6 and regime == "TRACKING_AM"
    if "albedo_s1 <= 55.7" in rule and "albedo_s2 > 18.0" in rule and "vwc_s1 > 20.0" in rule:
        return albedo_s1 <= 55.7 and albedo_s2 > 18.0 and vwc_s1 > 20.0
    if "evitar horizontal" in rule:
        productive_hour = hour in {6, 12}
        tracking_conditions = albedo_s1 > 55.7 or albedo_s2 > 18.0
        return regime == "HORIZONTAL" and productive_hour and tracking_conditions
    if "albedo_s1 <= 55.7" in rule and "albedo_s2 <= 18.0" in rule and "vwc_s1 <= 22.2" in rule:
        return albedo_s1 <= 55.7 and albedo_s2 <= 18.0 and vwc_s1 <= 22.2 and gpoa_s2 <= 35.5
    return False


def _closest_iec_rule_index(df_rules: pd.DataFrame, current_iec: float) -> int | None:
    if df_rules.empty or math.isnan(current_iec):
        return None
    diffs = (df_rules["iec_mediana"] - current_iec).abs()
    return int(diffs.argmin())


def get_active_rule_index(df_rules: pd.DataFrame, current_record: pd.Series | float) -> int | None:
    """
    Return the integer index (iloc position) of the first rule whose condition
    matches the current record. Numeric input preserves the legacy IEC fallback.
    """
    if not isinstance(current_record, pd.Series):
        return _closest_iec_rule_index(df_rules, float(current_record))
    if df_rules.empty:
        return None
    for i, row in df_rules.iterrows():
        if evaluate_rule_condition(str(row.get("regla", "")), current_record):
            return int(i)
    return None


def format_regime_label(regime: str) -> str:
    """Return a human-readable label for a tracking regime code."""
    return _REGIME_LABELS.get(regime, regime)
