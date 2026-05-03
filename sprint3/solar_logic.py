import math
import pandas as pd

# Quadratic Bezier control points for the sun arc SVG (px coordinates)
_P0 = (30.0, 158.0)    # sunrise (06:00)
_P1 = (230.0, 15.0)    # zenith control point
_P2 = (430.0, 158.0)   # sunset (21:00)
_DAY_HOURS = 15.0       # 06:00 → 21:00

WEIGHT_PRESETS: dict[str, tuple[float, float]] = {
    "Equilibrado": (0.5, 0.5),
    "Priorizar energia": (0.7, 0.3),
    "Priorizar cultivo": (0.3, 0.7),
}


def calculate_sun_position(hour: float) -> tuple[float, float]:
    """Return (x, y) SVG coords of the sun at the given hour using a quadratic Bezier."""
    t = max(0.0, min(1.0, (hour - 6.0) / _DAY_HOURS))
    x = (1 - t) ** 2 * _P0[0] + 2 * t * (1 - t) * _P1[0] + t ** 2 * _P2[0]
    y = (1 - t) ** 2 * _P0[1] + 2 * t * (1 - t) * _P1[1] + t ** 2 * _P2[1]
    return x, y


def estimate_solar_elevation(hour: float) -> float:
    """Approximate solar elevation in degrees. Max 90° at 12:30, 0° at sunrise/sunset."""
    return max(0.0, 90.0 - abs(hour - 12.5) * 8.0)


def weighted_iec(
    df_modelo: pd.DataFrame,
    energy_weight: float = 0.5,
    crop_weight: float = 0.5,
) -> pd.Series:
    """Return IEC recalculated from energy_score and crop_score with custom weights."""
    total = energy_weight + crop_weight
    if total <= 0:
        raise ValueError("IEC weights must add up to a positive value")
    ew = energy_weight / total
    cw = crop_weight / total
    if {"energy_score", "crop_score"}.issubset(df_modelo.columns):
        return ew * df_modelo["energy_score"] + cw * df_modelo["crop_score"]
    return df_modelo["IEC"]


def get_weight_preset(name: str) -> tuple[float, float]:
    """Return energy/crop weights for a dashboard priority mode."""
    return WEIGHT_PRESETS.get(name, WEIGHT_PRESETS["Equilibrado"])


def get_recommended_angle(
    hour: int,
    df_modelo: pd.DataFrame,
    energy_weight: float = 0.5,
    crop_weight: float = 0.5,
) -> float:
    """
    Return the track_mean of the best-IEC record at the nearest available hour.
    Dataset has 6h resolution (hours 0, 6, 12, 18), so snaps to nearest instead
    of returning 0 for hours without data.
    """
    valid = df_modelo.dropna(subset=["IEC", "track_mean"]).copy()
    if valid.empty:
        return 0.0
    valid["IEC_weighted"] = weighted_iec(valid, energy_weight, crop_weight)
    available = valid["hour_of_day"].unique()
    nearest = available[(available - hour).__abs__().argmin()]
    hour_data = valid[valid["hour_of_day"] == nearest]
    best_idx = hour_data["IEC_weighted"].idxmax()
    return float(hour_data.loc[best_idx, "track_mean"])


def get_iec_angle_scenario(
    hour: float,
    target_iec: float,
    df_modelo: pd.DataFrame,
    energy_weight: float = 0.5,
    crop_weight: float = 0.5,
) -> pd.Series:
    """
    Return the historical record that best represents a user-selected IEC.

    The dashboard uses this as an operational scenario: IEC is the primary
    control, while hour keeps the result anchored to the current part of day.
    """
    valid = df_modelo.dropna(subset=["IEC", "track_mean", "hour_of_day"]).copy()
    if valid.empty:
        raise ValueError("No valid records with IEC and track_mean in dataset")
    valid["IEC_weighted"] = weighted_iec(valid, energy_weight, crop_weight)

    iec_min = float(valid["IEC_weighted"].min())
    iec_max = float(valid["IEC_weighted"].max())
    iec_range = max(iec_max - iec_min, 1e-9)
    hour_range = 24.0
    clipped_iec = max(iec_min, min(iec_max, float(target_iec)))

    score = (
        ((valid["IEC_weighted"] - clipped_iec).abs() / iec_range)
        + 0.18 * ((valid["hour_of_day"] - hour).abs() / hour_range)
    )
    return valid.loc[score.idxmin()]


def get_iec_bounds(
    df_modelo: pd.DataFrame,
    energy_weight: float = 0.5,
    crop_weight: float = 0.5,
) -> tuple[float, float]:
    """Return min and max IEC values available for slider configuration."""
    valid = df_modelo.dropna(subset=["IEC"]).copy()
    if valid.empty:
        return 0.0, 1.0
    scores = weighted_iec(valid, energy_weight, crop_weight).dropna()
    if scores.empty:
        return 0.0, 1.0
    return float(scores.min()), float(scores.max())


def get_scenario_confidence(
    df_modelo: pd.DataFrame,
    hour: float,
    target_iec: float,
    energy_weight: float = 0.5,
    crop_weight: float = 0.5,
) -> tuple[str, int]:
    """Estimate recommendation confidence from nearby historical observations."""
    valid = df_modelo.dropna(subset=["IEC", "track_mean", "hour_of_day"]).copy()
    if valid.empty:
        return "Sin datos", 0
    valid["IEC_weighted"] = weighted_iec(valid, energy_weight, crop_weight)
    nearby = valid[
        ((valid["IEC_weighted"] - target_iec).abs() <= 0.05)
        & ((valid["hour_of_day"] - hour).abs() <= 6)
    ]
    n = int(len(nearby))
    if n >= 25:
        return "Alta", n
    if n >= 10:
        return "Media", n
    if n > 0:
        return "Baja", n
    return "Sin soporte", n
