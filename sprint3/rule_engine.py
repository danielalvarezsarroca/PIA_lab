import math
import pandas as pd

_REGIME_LABELS: dict[str, str] = {
    "TRACKING_PM": "Tracking tarde (óptimo)",
    "TRACKING_AM": "Tracking mañana",
    "HORIZONTAL":  "Horizontal (mínimo)",
}


def get_active_rule_index(df_rules: pd.DataFrame, current_iec: float) -> int | None:
    """
    Return the integer index (iloc position) of the rule whose iec_mediana is
    closest to current_iec. Returns None if df_rules is empty or current_iec is NaN.
    """
    if df_rules.empty or math.isnan(current_iec):
        return None
    diffs = (df_rules["iec_mediana"] - current_iec).abs()
    return int(diffs.argmin())


def format_regime_label(regime: str) -> str:
    """Return a human-readable label for a tracking regime code."""
    return _REGIME_LABELS.get(regime, regime)
