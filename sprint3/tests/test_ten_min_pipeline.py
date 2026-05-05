from pathlib import Path

import pandas as pd

from ten_min_pipeline import (
    build_modeling_dataset_10min,
    regenerate_candidate_rules_10min,
    write_10min_outputs,
)


def _master_sample() -> pd.DataFrame:
    return pd.DataFrame({
        "Time": pd.to_datetime([
            "2026-05-03 06:00",
            "2026-05-03 06:10",
            "2026-05-03 06:20",
            "2026-05-03 06:30",
            "2026-05-03 06:40",
            "2026-05-03 06:50",
        ]),
        "tracker_angle_deg": [-32.0, -30.0, -28.0, 31.0, 33.0, 34.0],
        "solar_elevation_deg": [15.0, 18.0, 21.0, 70.0, 72.0, 71.0],
        "solar_azimuth_deg": [92.0, 96.0, 100.0, 180.0, 184.0, 188.0],
        "clearsky_ghi_wm2": [120.0, 180.0, 240.0, 880.0, 900.0, 870.0],
        "air_temp_ext_avg_degc": [14.0, 14.5, 15.0, 25.0, 25.5, 25.0],
        "wind_speed_kmh": [3.0, 4.0, 4.5, 8.0, 8.5, 8.0],
        "precip_intensity_mm10min": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "PAR_R1": [110.0, 170.0, 220.0, 900.0, 920.0, 890.0],
        "PAR_S1": [65.0, 90.0, 120.0, 520.0, 540.0, 530.0],
        "PAR_S2": [70.0, 95.0, 130.0, 500.0, 530.0, 520.0],
        "Tsoil_R1_mean": [13.0, 13.0, 13.5, 19.0, 19.5, 19.0],
        "Tsoil_S1_mean": [12.5, 12.5, 13.0, 18.0, 18.5, 18.0],
        "Tsoil_S2_mean": [12.7, 12.8, 13.0, 18.2, 18.3, 18.1],
        "VWC_R1_mean": [23.0, 23.0, 23.0, 22.0, 22.0, 22.0],
        "VWC_S1_mean": [25.0, 25.0, 25.0, 23.0, 23.0, 23.0],
        "VWC_S2_mean": [21.0, 21.0, 21.0, 20.0, 20.0, 20.0],
        "GPOA_mean": [90.0, 140.0, 190.0, 760.0, 790.0, 780.0],
        "ALBEDO_mean": [18.0, 18.5, 19.0, 35.0, 36.0, 35.0],
        "Delta_PAR_S1": [-45.0, -80.0, -100.0, -380.0, -380.0, -360.0],
        "Delta_Tsoil_S1": [-0.5, -0.5, -0.5, -1.0, -1.0, -1.0],
        "Delta_VWC_S1": [2.0, 2.0, 2.0, 1.0, 1.0, 1.0],
    })


def test_build_modeling_dataset_10min_preserves_resolution_and_maps_columns():
    model = build_modeling_dataset_10min(_master_sample())

    assert model["Time"].diff().dropna().dt.total_seconds().eq(600).all()
    assert set(model["source_resolution"]) == {"10min"}
    assert model.loc[0, "track_mean"] == -32.0
    assert model.loc[0, "tracking_regime"] == "TRACKING_AM"
    assert model.loc[3, "tracking_regime"] == "TRACKING_PM"
    assert model["IEC"].between(0, 1).all()
    assert {"minute_of_day", "time_block_10min", "GPOA_mean"}.issubset(model.columns)


def test_regenerate_candidate_rules_10min_uses_finer_time_blocks():
    model = build_modeling_dataset_10min(_master_sample())

    rules = regenerate_candidate_rules_10min(model)

    assert not rules.empty
    assert {"tipo", "regla", "soporte_obs", "iec_mediana", "comentario"}.issubset(rules.columns)
    assert rules["comentario"].str.contains("10 min").any()


def test_write_10min_outputs_creates_dataset_rules_metadata_and_6h_backup(tmp_path: Path):
    model = build_modeling_dataset_10min(_master_sample())
    rules = regenerate_candidate_rules_10min(model)
    backup_source = tmp_path / "dataset_modelizacion_6h.csv"
    backup_source.write_text("Time,IEC\n2026-05-03 00:00,0.5\n", encoding="utf-8")

    paths = write_10min_outputs(
        output_dir=tmp_path / "outputs_10min",
        model_dataset=model,
        rules=rules,
        metadata={"mode": "10min"},
        backup_6h_paths=[backup_source],
    )

    assert paths["dataset"].exists()
    assert paths["rules"].exists()
    assert paths["metadata"].exists()
    assert paths["backup_dir"].joinpath("dataset_modelizacion_6h.csv").exists()
