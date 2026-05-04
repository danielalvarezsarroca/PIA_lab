from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from daily_update import build_daily_update, regenerate_candidate_rules, write_daily_update_outputs

BASE_DIR = Path(__file__).resolve().parent
MODELO_PATH = BASE_DIR.parent / "sprint2" / "outputs_sprint2" / "dataset_modelizacion_6h.csv"


def _load_optional_sensor_csv(path: str | None) -> pd.DataFrame | None:
    if not path:
        return None
    return pd.read_csv(path, parse_dates=["Time"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a daily 6h dataset update. Without --sensor-csv, internal "
            "plant variables are demo-imputed from historical profiles and clearly "
            "marked as pending sensor/SCADA integration."
        )
    )
    parser.add_argument("--target-date", help="Date to update in YYYY-MM-DD format. Defaults to yesterday.")
    parser.add_argument(
        "--sensor-csv",
        help=(
            "Optional CSV exported from plant sensors/SCADA. It must include Time and can "
            "include any model columns such as track_mean, VWC_S1_mean, ePAR_S1_mean or IEC."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="outputs_daily",
        help="Directory where updated dataset, rules and metadata will be written.",
    )
    args = parser.parse_args()

    historical = pd.read_csv(MODELO_PATH, parse_dates=["Time"])
    sensors = _load_optional_sensor_csv(args.sensor_csv)
    daily_rows, metadata = build_daily_update(historical, target_date=args.target_date, sensor_rows=sensors)
    updated_dataset = (
        pd.concat([historical, daily_rows], ignore_index=True)
        .sort_values("Time")
        .reset_index(drop=True)
    )
    rules = regenerate_candidate_rules(updated_dataset)
    paths = write_daily_update_outputs(Path(args.output_dir), updated_dataset, rules, metadata)

    print("Daily update generated")
    print(f"mode: {metadata['mode']}")
    print(f"dataset: {paths['dataset']}")
    print(f"rules: {paths['rules']}")
    print(f"metadata: {paths['metadata']}")
    print("note:", metadata["notice"])


if __name__ == "__main__":
    main()
