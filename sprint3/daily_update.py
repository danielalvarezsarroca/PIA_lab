from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from weather_data import WEATHER_COLUMNS, build_weather_pending_metadata

MODEL_COLUMNS = [
    "Time",
    "hour_of_day",
    "day_of_year",
    "solar_elevation_deg",
    "track_mean",
    "tracking_regime",
    "Tair_WS",
    "Tair_S1_center",
    "wind_speed_kmh",
    "Albedo_S1",
    "Albedo_S2",
    "Tsoil_S1_mean",
    "Tsoil_S2_mean",
    "Tsoil_S1_mean_lag_6h",
    "Tsoil_S1_mean_lag_12h",
    "VWC_S1_mean",
    "VWC_S2_mean",
    "VWC_diff_S1_minus_S2",
    "ePAR_S1_mean",
    "ePAR_S2_mean",
    "IEC",
    "energy_score",
    "crop_score",
]

UPDATE_HOURS = [0, 6, 12, 18]
SENSOR_STATUS = "pending_sensor_integration"
DEMO_NOTICE = (
    "Actualizacion demo: las variables internas de planta se imputan desde el "
    "historico hasta disponer de conexion diaria a sensores/SCADA."
)


def _coerce_target_date(target_date: str | date | None) -> date:
    if target_date is None:
        return date.today() - timedelta(days=1)
    if isinstance(target_date, datetime):
        return target_date.date()
    if isinstance(target_date, date):
        return target_date
    return datetime.strptime(target_date, "%Y-%m-%d").date()


def _prepare_historical(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise ValueError("historical dataset is empty")
    if "Time" not in df.columns:
        raise ValueError("historical dataset must include Time")

    prepared = df.copy()
    prepared.loc[:, "Time"] = pd.to_datetime(prepared["Time"])
    if "hour_of_day" not in prepared.columns:
        prepared.loc[:, "hour_of_day"] = prepared["Time"].dt.hour
    if "day_of_year" not in prepared.columns:
        prepared.loc[:, "day_of_year"] = prepared["Time"].dt.dayofyear
    return prepared.sort_values("Time").reset_index(drop=True)


def _historical_profile(df: pd.DataFrame, hour: int) -> pd.Series:
    numeric_cols = [c for c in MODEL_COLUMNS if c in df.columns and c not in {"Time", "tracking_regime"}]
    hour_rows = df[df["hour_of_day"] == hour]
    if hour_rows.empty:
        hour_rows = df

    profile: dict[str, Any] = {}
    for col in numeric_cols:
        value = hour_rows[col].median(skipna=True)
        if pd.isna(value):
            value = df[col].median(skipna=True)
        profile[col] = value

    if "tracking_regime" in df.columns:
        modes = hour_rows["tracking_regime"].dropna().mode()
        profile["tracking_regime"] = modes.iloc[0] if not modes.empty else "HORIZONTAL"
    else:
        profile["tracking_regime"] = "HORIZONTAL"

    return pd.Series(profile)


def _sensor_rows_by_hour(sensor_rows: pd.DataFrame | None, target: date) -> dict[int, pd.Series]:
    if sensor_rows is None or sensor_rows.empty:
        return {}
    sensors = sensor_rows.copy().assign(Time=pd.to_datetime(sensor_rows["Time"]))
    sensors = sensors[sensors["Time"].dt.date == target]
    if sensors.empty:
        return {}
    sensors = sensors.assign(hour_of_day=sensors["Time"].dt.hour)
    return {int(row["hour_of_day"]): row for _, row in sensors.iterrows()}


def _weather_rows_by_hour(weather_rows: pd.DataFrame | None, target: date) -> dict[int, pd.Series]:
    if weather_rows is None or weather_rows.empty:
        return {}
    weather = weather_rows.copy().assign(Time=pd.to_datetime(weather_rows["Time"]))
    weather = weather[weather["Time"].dt.date == target]
    if weather.empty:
        return {}
    weather = weather.assign(hour_of_day=weather["Time"].dt.hour)
    return {int(row["hour_of_day"]): row for _, row in weather.iterrows()}


def _score_from_row(row: pd.Series) -> tuple[float, float, float]:
    epar = max(float(row.get("ePAR_S1_mean", 0.0) or 0.0), 0.0)
    vwc = float(row.get("VWC_S1_mean", 0.0) or 0.0)
    tsoil = float(row.get("Tsoil_S1_mean", 0.0) or 0.0)

    energy_score = min(1.0, epar / 600.0)
    vwc_score = 1.0 - min(1.0, abs(vwc - 24.0) / 12.0)
    temp_score = 1.0 - min(1.0, abs(tsoil - 18.0) / 18.0)
    crop_score = max(0.0, 0.65 * vwc_score + 0.35 * temp_score)
    iec = max(0.0, min(1.0, 0.55 * energy_score + 0.45 * crop_score))
    return energy_score, crop_score, iec


def build_daily_update(
    historical_df: pd.DataFrame,
    target_date: str | date | None = None,
    sensor_rows: pd.DataFrame | None = None,
    weather_rows: pd.DataFrame | None = None,
    weather_metadata: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Build one 6h-resolution daily update.

    If `sensor_rows` is provided, matching values override the historical profile.
    Missing internal plant variables are still filled from the profile and marked
    as demo imputation. This is intentional until a daily SCADA/sensor feed exists.
    """
    target = _coerce_target_date(target_date)
    historical = _prepare_historical(historical_df)
    sensors_by_hour = _sensor_rows_by_hour(sensor_rows, target)
    weather_by_hour = _weather_rows_by_hour(weather_rows, target)

    rows: list[dict[str, Any]] = []
    used_sensor_hours: list[int] = []
    for hour in UPDATE_HOURS:
        profile = _historical_profile(historical, hour)
        row = {col: profile.get(col, pd.NA) for col in MODEL_COLUMNS if col != "Time"}
        row["Time"] = pd.Timestamp(datetime.combine(target, datetime.min.time())).replace(hour=hour)
        row["hour_of_day"] = hour
        row["day_of_year"] = target.timetuple().tm_yday

        if hour in sensors_by_hour:
            sensor = sensors_by_hour[hour]
            for col in sensor.index:
                if col in MODEL_COLUMNS and col != "Time" and not pd.isna(sensor[col]):
                    row[col] = sensor[col]
            row["data_source"] = "sensor_with_imputation"
            used_sensor_hours.append(hour)
        else:
            row["data_source"] = "demo_imputed"

        weather = weather_by_hour.get(hour)
        for col in WEATHER_COLUMNS:
            row[col] = weather[col] if weather is not None and col in weather.index else pd.NA
        row["weather_source"] = (
            weather["weather_source"]
            if weather is not None and "weather_source" in weather.index
            else weather_metadata.get("source", "none") if weather_metadata else "none"
        )

        row["sensor_status"] = SENSOR_STATUS
        row["update_note"] = DEMO_NOTICE
        row_series = pd.Series(row)
        if pd.isna(row_series.get("energy_score")) or pd.isna(row_series.get("crop_score")) or pd.isna(row_series.get("IEC")):
            energy_score, crop_score, iec = _score_from_row(row_series)
            row["energy_score"] = energy_score
            row["crop_score"] = crop_score
            row["IEC"] = iec
        rows.append(row)

    mode = "sensor_with_demo_fill" if used_sensor_hours else "demo_imputed"
    metadata = {
        "target_date": target.isoformat(),
        "mode": mode,
        "sensor_hours_used": used_sensor_hours,
        "rows_generated": len(rows),
        "sensor_status": SENSOR_STATUS,
        "notice": DEMO_NOTICE,
        "weather": weather_metadata or build_weather_pending_metadata(),
    }
    return pd.DataFrame(rows), metadata


def regenerate_candidate_rules(updated_df: pd.DataFrame) -> pd.DataFrame:
    """Regenerate demo candidate rules from the latest updated dataset."""
    df = _prepare_historical(updated_df).dropna(subset=["IEC"])
    if df.empty:
        raise ValueError("updated dataset has no IEC values")

    rules: list[dict[str, Any]] = []
    high = df[df["IEC"] >= df["IEC"].quantile(0.75)]
    if not high.empty and {"Albedo_S1", "solar_elevation_deg"}.issubset(high.columns):
        rules.append({
            "tipo": "demo_prioridad_alta",
            "regla": "Si Albedo_S1 y elevacion solar son altos, priorizar tracking activo productivo.",
            "soporte_obs": int(len(high)),
            "iec_mediana": round(float(high["IEC"].median()), 3),
            "comentario": f"{DEMO_NOTICE} Regla recalculada desde dataset actualizado.",
        })

    if {"hour_of_day", "tracking_regime", "track_mean"}.issubset(df.columns):
        grouped = (
            df.dropna(subset=["tracking_regime", "track_mean"])
            .groupby(["hour_of_day", "tracking_regime"], as_index=False)
            .agg(
                soporte_obs=("IEC", "size"),
                iec_mediana=("IEC", "median"),
                angle_mediano=("track_mean", "median"),
            )
            .sort_values("iec_mediana", ascending=False)
            .head(4)
        )
        for _, row in grouped.iterrows():
            rules.append({
                "tipo": "demo_operativa",
                "regla": (
                    f"Si la franja es {int(row['hour_of_day']):02d}:00 y el sistema opera en "
                    f"{row['tracking_regime']}, mantener un angulo cercano a {row['angle_mediano']:.1f} grados."
                ),
                "soporte_obs": int(row["soporte_obs"]),
                "iec_mediana": round(float(row["iec_mediana"]), 3),
                "comentario": f"{DEMO_NOTICE} Sustituir por reglas entrenadas con sensores reales cuando esten disponibles.",
            })

    if not rules:
        rules.append({
            "tipo": "demo_fallback",
            "regla": "Mantener politica historica hasta recibir datos operativos reales.",
            "soporte_obs": int(len(df)),
            "iec_mediana": round(float(df["IEC"].median()), 3),
            "comentario": DEMO_NOTICE,
        })

    return pd.DataFrame(rules, columns=["tipo", "regla", "soporte_obs", "iec_mediana", "comentario"])


def write_daily_update_outputs(
    output_dir: str | Path,
    updated_dataset: pd.DataFrame,
    rules: pd.DataFrame,
    metadata: dict[str, Any],
) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    dataset_path = output_path / "dataset_modelizacion_6h_updated.csv"
    rules_path = output_path / "candidate_rotation_rules_updated.csv"
    metadata_path = output_path / "daily_update_metadata.json"

    updated_dataset.to_csv(dataset_path, index=False)
    rules.to_csv(rules_path, index=False)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"dataset": dataset_path, "rules": rules_path, "metadata": metadata_path}
