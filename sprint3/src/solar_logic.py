import math
import pandas as pd

# Quadratic Bezier control points for the sun arc SVG (px coordinates)
_P0 = (30.0, 158.0)    # sunrise (06:00)
_P1 = (230.0, 15.0)    # zenith control point
_P2 = (430.0, 158.0)   # sunset (21:00)
_DAY_HOURS = 15.0       # 06:00 → 21:00


def calculate_sun_position(hour: float) -> tuple[float, float]:
    """Return (x, y) SVG coords of the sun at the given hour using a quadratic Bezier."""
    t = max(0.0, min(1.0, (hour - 6.0) / _DAY_HOURS))
    x = (1 - t) ** 2 * _P0[0] + 2 * t * (1 - t) * _P1[0] + t ** 2 * _P2[0]
    y = (1 - t) ** 2 * _P0[1] + 2 * t * (1 - t) * _P1[1] + t ** 2 * _P2[1]
    return x, y


def estimate_solar_elevation(hour: float) -> float:
    """Approximate solar elevation in degrees. Max 90° at 12:30, 0° at sunrise/sunset."""
    return max(0.0, 90.0 - abs(hour - 12.5) * 8.0)


def get_recommended_angle(hour: int, df_modelo: pd.DataFrame) -> float:
    """
    Return the track_mean of the best-IEC record at the nearest available hour.
    Dataset has 6h resolution (hours 0, 6, 12, 18), so snaps to nearest instead
    of returning 0 for hours without data.
    """
    valid = df_modelo.dropna(subset=["IEC", "track_mean"])
    if valid.empty:
        return 0.0
    available = valid["hour_of_day"].unique()
    nearest = available[(available - hour).__abs__().argmin()]
    hour_data = valid[valid["hour_of_day"] == nearest]
    best_idx = hour_data["IEC"].idxmax()
    return float(hour_data.loc[best_idx, "track_mean"])
