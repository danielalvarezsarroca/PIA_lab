from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from daily_update import build_daily_update, regenerate_candidate_rules, write_daily_update_outputs
from weather_data import build_weather_pending_metadata, fetch_open_meteo_weather

BASE_DIR = Path(__file__).resolve().parent
MODELO_PATH = BASE_DIR.parent / "sprint2" / "outputs_sprint2" / "dataset_modelizacion_6h.csv"


def _load_optional_sensor_csv(path: str | None) -> pd.DataFrame | None:
    if not path:
        return None
    return pd.read_csv(path, parse_dates=["Time"])


def _load_optional_weather(
    target_date: str | None,
    latitude: float | None,
    longitude: float | None,
    weather_source: str,
) -> tuple[pd.DataFrame | None, dict]:
    if weather_source == "none":
        return None, build_weather_pending_metadata()
    if latitude is None or longitude is None:
        return None, build_weather_pending_metadata()
    try:
        return fetch_open_meteo_weather(target_date=target_date, latitude=latitude, longitude=longitude)
    except Exception as exc:
        metadata = build_weather_pending_metadata()
        metadata.update({
            "source": weather_source,
            "coordinates_status": "user_provided",
            "status": "fetch_failed",
            "error": str(exc),
        })
        return None, metadata


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
    parser.add_argument("--latitude", type=float, help="Plant latitude for optional Open-Meteo enrichment.")
    parser.add_argument("--longitude", type=float, help="Plant longitude for optional Open-Meteo enrichment.")
    parser.add_argument(
        "--weather-source",
        choices=["none", "open-meteo"],
        default="none",
        help="Optional external weather enrichment source. Requires --latitude and --longitude.",
    )
    args = parser.parse_args()

    historical = pd.read_csv(MODELO_PATH, parse_dates=["Time"])
    sensors = _load_optional_sensor_csv(args.sensor_csv)
    weather_rows, weather_metadata = _load_optional_weather(
        args.target_date,
        args.latitude,
        args.longitude,
        args.weather_source,
    )
    daily_rows, metadata = build_daily_update(
        historical,
        target_date=args.target_date,
        sensor_rows=sensors,
        weather_rows=weather_rows,
        weather_metadata=weather_metadata,
    )
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
    print("weather:", metadata["weather"]["notice"])


if __name__ == "__main__":
    main()
