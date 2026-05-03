import pytest
from solar_logic import (
    calculate_sun_position,
    estimate_solar_elevation,
    get_iec_angle_scenario,
    get_iec_bounds,
    get_recommended_angle,
    get_scenario_confidence,
    get_weight_preset,
    weighted_iec,
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


def test_get_recommended_angle_missing_hour_uses_nearest_available():
    df = pd.DataFrame({
        "hour_of_day": [8],
        "IEC": [0.5],
        "track_mean": [30.0],
    })
    angle = get_recommended_angle(15, df)
    assert angle == pytest.approx(30.0)


def test_get_iec_angle_scenario_prioritizes_target_iec():
    df = pd.DataFrame({
        "hour_of_day": [6, 12, 18],
        "IEC": [0.6, 0.9, 0.2],
        "track_mean": [-32.0, 33.0, 2.0],
    })
    row = get_iec_angle_scenario(13, 0.88, df)
    assert row["track_mean"] == pytest.approx(33.0)


def test_get_iec_bounds_returns_dataset_range():
    df = pd.DataFrame({"IEC": [0.12, 0.75, None]})
    assert get_iec_bounds(df) == pytest.approx((0.12, 0.75))


def test_weighted_iec_uses_custom_weights():
    df = pd.DataFrame({"energy_score": [1.0], "crop_score": [0.0], "IEC": [0.5]})
    assert weighted_iec(df, 0.7, 0.3).iloc[0] == pytest.approx(0.7)


def test_weight_preset_defaults_to_balanced():
    assert get_weight_preset("unknown") == pytest.approx((0.5, 0.5))


def test_scenario_confidence_counts_nearby_records():
    df = pd.DataFrame({
        "hour_of_day": [12, 12, 18],
        "IEC": [0.5, 0.52, 0.9],
        "energy_score": [0.5, 0.52, 0.9],
        "crop_score": [0.5, 0.52, 0.9],
        "track_mean": [30.0, 32.0, 2.0],
    })
    label, n = get_scenario_confidence(df, 12, 0.51)
    assert label == "Baja"
    assert n == 2
