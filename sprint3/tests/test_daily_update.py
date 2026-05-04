from pathlib import Path

import pandas as pd
import pytest

from daily_update import (
    build_daily_update,
    regenerate_candidate_rules,
    write_daily_update_outputs,
)


def _historical_model() -> pd.DataFrame:
    return pd.DataFrame({
        "Time": pd.to_datetime([
            "2026-01-01 00:00", "2026-01-01 06:00",
            "2026-01-01 12:00", "2026-01-01 18:00",
            "2026-01-02 00:00", "2026-01-02 06:00",
            "2026-01-02 12:00", "2026-01-02 18:00",
        ]),
        "hour_of_day": [0, 6, 12, 18, 0, 6, 12, 18],
        "day_of_year": [1, 1, 1, 1, 2, 2, 2, 2],
        "solar_elevation_deg": [0, 38, 86, 46, 0, 37, 85, 45],
        "track_mean": [0, -32, 32, 1, 0, -31, 33, 1],
        "tracking_regime": ["HORIZONTAL", "TRACKING_AM", "TRACKING_PM", "HORIZONTAL"] * 2,
        "Tair_WS": [8, 10, 18, 12, 9, 11, 19, 13],
        "Tair_S1_center": [8, 10, 18, 12, 9, 11, 19, 13],
        "wind_speed_kmh": [3, 4, 6, 5, 3, 4, 6, 5],
        "Albedo_S1": [15, 25, 60, 20, 16, 26, 62, 21],
        "Albedo_S2": [12, 18, 24, 16, 13, 19, 25, 17],
        "Tsoil_S1_mean": [9, 10, 13, 12, 9, 10, 14, 12],
        "Tsoil_S2_mean": [9, 10, 13, 12, 9, 10, 14, 12],
        "Tsoil_S1_mean_lag_6h": [9, 9, 10, 13, 12, 9, 10, 14],
        "Tsoil_S1_mean_lag_12h": [9, 9, 9, 10, 13, 12, 9, 10],
        "VWC_S1_mean": [24, 23, 22, 23, 25, 24, 23, 24],
        "VWC_S2_mean": [20, 20, 19, 20, 21, 21, 20, 21],
        "VWC_diff_S1_minus_S2": [4, 3, 3, 3, 4, 3, 3, 3],
        "ePAR_S1_mean": [0, 80, 500, 140, 0, 90, 520, 150],
        "ePAR_S2_mean": [0, 70, 460, 130, 0, 80, 480, 140],
        "IEC": [0.12, 0.61, 0.86, 0.20, 0.13, 0.62, 0.88, 0.21],
        "energy_score": [0.1, 0.6, 0.9, 0.2, 0.1, 0.6, 0.9, 0.2],
        "crop_score": [0.8, 0.7, 0.8, 0.6, 0.8, 0.7, 0.8, 0.6],
    })


def test_build_daily_update_demo_imputes_four_6h_rows():
    rows, metadata = build_daily_update(_historical_model(), target_date="2026-05-03")

    assert list(rows["hour_of_day"]) == [0, 6, 12, 18]
    assert rows["Time"].dt.date.astype(str).tolist() == ["2026-05-03"] * 4
    assert set(rows["data_source"]) == {"demo_imputed"}
    assert set(rows["sensor_status"]) == {"pending_sensor_integration"}
    assert rows["IEC"].between(0, 1).all()
    assert metadata["mode"] == "demo_imputed"


def test_build_daily_update_uses_sensor_values_and_marks_partial_imputation():
    sensors = pd.DataFrame({
        "Time": pd.to_datetime(["2026-05-03 06:00", "2026-05-03 12:00"]),
        "track_mean": [-29.5, 34.0],
        "VWC_S1_mean": [26.0, 24.0],
        "IEC": [0.64, 0.90],
    })

    rows, metadata = build_daily_update(_historical_model(), target_date="2026-05-03", sensor_rows=sensors)

    six = rows.loc[rows["hour_of_day"] == 6].iloc[0]
    noon = rows.loc[rows["hour_of_day"] == 12].iloc[0]
    assert six["track_mean"] == pytest.approx(-29.5)
    assert noon["IEC"] == pytest.approx(0.90)
    assert set(rows["data_source"]) == {"sensor_with_imputation", "demo_imputed"}
    assert metadata["mode"] == "sensor_with_demo_fill"


def test_regenerate_candidate_rules_returns_demo_metadata():
    updated = pd.concat([
        _historical_model(),
        build_daily_update(_historical_model(), target_date="2026-05-03")[0],
    ], ignore_index=True)

    rules = regenerate_candidate_rules(updated)

    assert {"tipo", "regla", "soporte_obs", "iec_mediana", "comentario"}.issubset(rules.columns)
    assert not rules.empty
    assert rules["comentario"].str.contains("demo", case=False).any()


def test_write_daily_update_outputs_creates_dataset_rules_and_metadata(tmp_path: Path):
    rows, metadata = build_daily_update(_historical_model(), target_date="2026-05-03")
    updated = pd.concat([_historical_model(), rows], ignore_index=True)
    rules = regenerate_candidate_rules(updated)

    paths = write_daily_update_outputs(tmp_path, updated, rules, metadata)

    assert paths["dataset"].exists()
    assert paths["rules"].exists()
    assert paths["metadata"].exists()
