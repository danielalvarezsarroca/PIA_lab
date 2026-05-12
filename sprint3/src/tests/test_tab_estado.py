import pandas as pd
import pytest

from tabs.tab_estado import _crop_health_pct, _energy_efficiency_pct, _get_hour_record, _raw_metric_value


def test_get_hour_record_uses_representative_score_instead_of_latest_tail() -> None:
    df = pd.DataFrame(
        {
            "Time": pd.to_datetime(
                [
                    "2026-02-10 12:10:00",
                    "2026-02-11 12:20:00",
                    "2026-02-12 12:50:00",
                ]
            ),
            "hour_of_day": [12, 12, 12],
            "track_mean": [8.0, 8.3, 8.1],
            "IEC": [0.52, 0.55, 0.10],
        }
    )

    row = _get_hour_record(df, 12)

    assert row["IEC"] == pytest.approx(0.52)
    assert row["Time"] == pd.Timestamp("2026-02-10 12:10:00")


def test_crop_health_pct_scales_against_dataset_min_and_max() -> None:
    df = pd.DataFrame({"crop_score": [0.25, 0.55, 0.85]})
    row = pd.Series({"crop_score": 0.55})

    assert _crop_health_pct(row, df) == pytest.approx(50.0)


def test_energy_efficiency_pct_scales_against_dataset_min_and_max() -> None:
    df = pd.DataFrame(
        {
            "hour_of_day": [10, 13, 21],
            "GPOA_mean": [40.0, 250.0, 500.0],
        }
    )

    min_energy_row = pd.Series({"hour_of_day": 10, "GPOA_mean": 40.0})
    mid_energy_row = pd.Series({"hour_of_day": 13, "GPOA_mean": 250.0})
    max_energy_row = pd.Series({"hour_of_day": 21, "GPOA_mean": 500.0})

    assert _energy_efficiency_pct(min_energy_row, df) == pytest.approx(0.0)
    assert _energy_efficiency_pct(mid_energy_row, df) == pytest.approx(45.6521739)
    assert _energy_efficiency_pct(max_energy_row, df) == pytest.approx(100.0)


def test_raw_metric_value_uses_direct_sensor_fallbacks() -> None:
    row = pd.Series({"PAR_S1": 312.5})

    value_col, value = _raw_metric_value(row, "ePAR_S1_mean", "PAR_S1")

    assert value_col == "PAR_S1"
    assert value == pytest.approx(312.5)
