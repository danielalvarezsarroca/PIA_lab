from pathlib import Path

import pandas as pd

from sprint2.retrain_from_updated_dataset import retrain_from_updated_dataset


def test_retrain_from_updated_dataset_writes_rules_and_metadata(tmp_path: Path):
    dataset = pd.DataFrame({
        "Time": pd.to_datetime(["2026-05-03 06:00", "2026-05-03 12:00"]),
        "hour_of_day": [6, 12],
        "tracking_regime": ["TRACKING_AM", "TRACKING_PM"],
        "track_mean": [-31.0, 33.0],
        "Albedo_S1": [30.0, 62.0],
        "solar_elevation_deg": [38.0, 86.0],
        "IEC": [0.62, 0.88],
    })
    input_path = tmp_path / "dataset_modelizacion_6h_updated.csv"
    output_dir = tmp_path / "retrain"
    dataset.to_csv(input_path, index=False)

    paths = retrain_from_updated_dataset(input_path, output_dir)

    assert paths["rules"].exists()
    assert paths["metadata"].exists()
    rules = pd.read_csv(paths["rules"])
    assert not rules.empty
    assert rules["comentario"].str.contains("dataset actualizado", case=False).any()
