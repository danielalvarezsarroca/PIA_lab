import pytest
from solar_logic import (
    calculate_sun_position,
    estimate_solar_elevation,
    get_recommended_angle,
)
import pandas as pd


def test_sun_position_at_sunrise():
    x, y = calculate_sun_position(6.0)
    assert abs(x - 30) < 2
    assert abs(y - 158) < 2


def test_sun_position_at_sunset():
    x, y = calculate_sun_position(21.0)
    assert abs(x - 430) < 2
    assert abs(y - 158) < 2


def test_sun_position_at_solar_noon():
    x, y = calculate_sun_position(13.5)
    assert abs(x - 230) < 2


def test_solar_elevation_at_noon():
    elev = estimate_solar_elevation(12.5)
    assert elev == pytest.approx(90.0)


def test_solar_elevation_at_sunrise():
    elev = estimate_solar_elevation(6.0)
    assert elev == pytest.approx(38.0)


def test_solar_elevation_is_non_negative():
    for h in [4.0, 5.0, 22.0, 23.0]:
        assert estimate_solar_elevation(h) >= 0.0


def test_get_recommended_angle_returns_float():
    df = pd.DataFrame({
        "hour_of_day": [12, 12, 14],
        "IEC": [0.9, 0.4, 0.7],
        "track_mean": [35.0, 20.0, 40.0],
    })
    angle = get_recommended_angle(12, df)
    assert angle == pytest.approx(35.0)


def test_get_recommended_angle_missing_hour_snaps_to_nearest_available_hour():
    df = pd.DataFrame({
        "hour_of_day": [8],
        "IEC": [0.5],
        "track_mean": [30.0],
    })
    angle = get_recommended_angle(15, df)
    assert angle == pytest.approx(30.0)
