from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

OUTPUT_COLUMNS = [
    "Time",
    "source_resolution",
    "minute_of_day",
    "time_block_10min",
    "hour_of_day",
    "day_of_year",
    "solar_elevation_deg",
    "solar_azimuth_deg",
    "clearsky_ghi_wm2",
    "track_mean",
    "tracking_regime",
    "Tair_WS",
    "wind_speed_kmh",
    "precip_intensity_mm10min",
    "Albedo_S1",
    "Albedo_S2",
    "Tsoil_R1_mean",
    "Tsoil_S1_mean",
    "Tsoil_S2_mean",
    "VWC_R1_mean",
    "VWC_S1_mean",
    "VWC_S2_mean",
    "VWC_diff_S1_minus_S2",
    "ePAR_R1_mean",
    "ePAR_S1_mean",
    "ePAR_S2_mean",
    "GPOA_mean",
    "Delta_PAR_S1",
    "Delta_Tsoil_S1",
    "Delta_VWC_S1",
    "energy_score",
    "crop_score",
    "IEC",
]


def _require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"master dataset missing required columns: {missing}")


def _classify_tracking_regime(row: pd.Series) -> str:
    elevation = row.get("solar_elevation_deg")
    angle = row.get("tracker_angle_deg")
    if pd.isna(elevation) or float(elevation) <= 0:
        return "NIGHT_STOW"
    if pd.isna(angle) or abs(float(angle)) < 5:
        return "HORIZONTAL"
    return "TRACKING_AM" if float(angle) < 0 else "TRACKING_PM"


def _bounded_score(series: pd.Series, denominator: float) -> pd.Series:
    if denominator <= 0 or pd.isna(denominator):
        return pd.Series(0.0, index=series.index)
    return (series.fillna(0).clip(lower=0) / denominator).clip(0, 1)


def _column(df: pd.DataFrame, name: str) -> pd.Series:
    if name in df.columns:
        return df[name]
    return pd.Series(pd.NA, index=df.index)


def build_modeling_dataset_10min(master_df: pd.DataFrame) -> pd.DataFrame:
    _require_columns(master_df, ["Time", "tracker_angle_deg", "solar_elevation_deg"])
    df = master_df.copy()
    df.loc[:, "Time"] = pd.to_datetime(df["Time"])
    df = df.sort_values("Time").reset_index(drop=True)

    model = pd.DataFrame({
        "Time": df["Time"],
        "source_resolution": "10min",
        "minute_of_day": df["Time"].dt.hour * 60 + df["Time"].dt.minute,
        "time_block_10min": df["Time"].dt.strftime("%H:%M"),
        "hour_of_day": df["Time"].dt.hour,
        "day_of_year": df["Time"].dt.dayofyear,
        "solar_elevation_deg": _column(df, "solar_elevation_deg"),
        "solar_azimuth_deg": _column(df, "solar_azimuth_deg"),
        "clearsky_ghi_wm2": _column(df, "clearsky_ghi_wm2"),
        "track_mean": df["tracker_angle_deg"],
        "tracking_regime": df.apply(_classify_tracking_regime, axis=1),
        "Tair_WS": _column(df, "air_temp_ext_avg_degc"),
        "wind_speed_kmh": _column(df, "wind_speed_kmh"),
        "precip_intensity_mm10min": _column(df, "precip_intensity_mm10min"),
        "Albedo_S1": _column(df, "ALBEDO_mean"),
        "Albedo_S2": _column(df, "ALBEDO_mean"),
        "Tsoil_R1_mean": _column(df, "Tsoil_R1_mean"),
        "Tsoil_S1_mean": _column(df, "Tsoil_S1_mean"),
        "Tsoil_S2_mean": _column(df, "Tsoil_S2_mean"),
        "VWC_R1_mean": _column(df, "VWC_R1_mean"),
        "VWC_S1_mean": _column(df, "VWC_S1_mean"),
        "VWC_S2_mean": _column(df, "VWC_S2_mean"),
        "ePAR_R1_mean": _column(df, "PAR_R1"),
        "ePAR_S1_mean": _column(df, "PAR_S1"),
        "ePAR_S2_mean": _column(df, "PAR_S2"),
        "GPOA_mean": _column(df, "GPOA_mean"),
        "Delta_PAR_S1": _column(df, "Delta_PAR_S1"),
        "Delta_Tsoil_S1": _column(df, "Delta_Tsoil_S1"),
        "Delta_VWC_S1": _column(df, "Delta_VWC_S1"),
    })
    model = model.assign(VWC_diff_S1_minus_S2=model["VWC_S1_mean"] - model["VWC_S2_mean"])

    energy_p95 = float(model["GPOA_mean"].quantile(0.95)) if "GPOA_mean" in model else 0.0
    energy_score = _bounded_score(model["GPOA_mean"], energy_p95)
    vwc_score = 1.0 - (model["VWC_S1_mean"].fillna(model["VWC_S1_mean"].median()) - 24.0).abs().div(12.0).clip(0, 1)
    temp_score = 1.0 - (model["Tsoil_S1_mean"].fillna(model["Tsoil_S1_mean"].median()) - 18.0).abs().div(18.0).clip(0, 1)
    par_stress = (1.0 - model["ePAR_S1_mean"].fillna(model["ePAR_S1_mean"].median()).div(model["ePAR_R1_mean"].replace(0, np.nan)).clip(0, 1)).fillna(0)
    crop_score = (0.55 * vwc_score + 0.30 * temp_score + 0.15 * (1.0 - par_stress)).clip(0, 1)
    iec = (0.55 * energy_score + 0.45 * crop_score).clip(0, 1)
    model = model.assign(energy_score=energy_score, crop_score=crop_score, IEC=iec)

    return model[OUTPUT_COLUMNS].round(4)


def regenerate_candidate_rules_10min(model_df: pd.DataFrame) -> pd.DataFrame:
    df = model_df.dropna(subset=["IEC", "track_mean", "tracking_regime"]).copy()
    if df.empty:
        raise ValueError("10 min model dataset has no valid IEC/tracking rows")
    daylight = df[df["solar_elevation_deg"].fillna(-1) > 0]
    if daylight.empty:
        daylight = df

    rules = []

    high_albedo_elevation = daylight[
        (daylight["Albedo_S1"].fillna(-1) > 55.7)
        & (daylight["solar_elevation_deg"].fillna(-1) > 68)
    ]
    if not high_albedo_elevation.empty:
        best_regime = high_albedo_elevation["tracking_regime"].mode()
        regime = best_regime.iloc[0] if not best_regime.empty else "TRACKING_PM"
        rules.append({
            "tipo": "10min_condicional_albedo_elevacion",
            "regla": (
                "Si Albedo_S1 > 55.7 y la elevacion solar supera 68 grados, "
                f"priorizar {regime} con angulo cercano a "
                f"{high_albedo_elevation['track_mean'].median():.1f} grados."
            ),
            "soporte_obs": int(len(high_albedo_elevation)),
            "iec_mediana": round(float(high_albedo_elevation["IEC"].median()), 3),
            "comentario": (
                "Regla condicional generada desde master_dataset a resolucion 10 min; "
                "replica la lectura fisica de alta radiacion de la version 6h."
            ),
        })

    period_specs = [
        ("manana", 6 * 60, 11 * 60 + 59),
        ("mediodia", 12 * 60, 15 * 60 + 59),
        ("tarde", 16 * 60, 21 * 60 + 59),
        ("noche_stow", 0, 5 * 60 + 59),
    ]
    for label, start, end in period_specs:
        period = df[(df["minute_of_day"] >= start) & (df["minute_of_day"] <= end)]
        if label == "noche_stow":
            period = df[df["solar_elevation_deg"].fillna(1) <= 0]
        if period.empty:
            continue
        best = (
            period.groupby("tracking_regime", as_index=False)
            .agg(
                soporte_obs=("IEC", "size"),
                iec_mediana=("IEC", "median"),
                angle_mediano=("track_mean", "median"),
            )
            .sort_values(["iec_mediana", "soporte_obs"], ascending=[False, False])
            .iloc[0]
        )
        rules.append({
            "tipo": f"10min_franja_{label}",
            "regla": (
                f"En franja {label.replace('_', ' ')}, usar {best['tracking_regime']} "
                f"con angulo cercano a {best['angle_mediano']:.1f} grados."
            ),
            "soporte_obs": int(best["soporte_obs"]),
            "iec_mediana": round(float(best["iec_mediana"]), 3),
            "comentario": (
                "Regla de cobertura por franja generada a 10 min para evitar que "
                "el ranking global solo muestre una ventana horaria."
            ),
        })

    grouped = (
        daylight.groupby(["time_block_10min", "tracking_regime"], as_index=False)
        .agg(
            soporte_obs=("IEC", "size"),
            iec_mediana=("IEC", "median"),
            angle_mediano=("track_mean", "median"),
            elevacion_mediana=("solar_elevation_deg", "median"),
        )
        .sort_values(["iec_mediana", "soporte_obs"], ascending=[False, False])
        .head(12)
    )

    for _, row in grouped.iterrows():
        rules.append({
            "tipo": "10min_microbloque",
            "regla": (
                f"En bloque {row['time_block_10min']}, usar {row['tracking_regime']} "
                f"con angulo cercano a {row['angle_mediano']:.1f} grados."
            ),
            "soporte_obs": int(row["soporte_obs"]),
            "iec_mediana": round(float(row["iec_mediana"]), 3),
            "comentario": (
                "Regla generada desde master_dataset a resolucion 10 min. "
                "La version 6h se conserva como backup operativo."
            ),
        })

    return pd.DataFrame(rules, columns=["tipo", "regla", "soporte_obs", "iec_mediana", "comentario"])


def write_10min_outputs(
    output_dir: str | Path,
    model_dataset: pd.DataFrame,
    rules: pd.DataFrame,
    metadata: dict[str, Any],
    backup_6h_paths: Iterable[str | Path] | None = None,
) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    dataset_path = output_path / "dataset_modelizacion_10min.csv"
    rules_path = output_path / "candidate_rotation_rules_10min.csv"
    metadata_path = output_path / "pipeline_10min_metadata.json"
    backup_dir = output_path / "backup_6h"
    backup_dir.mkdir(parents=True, exist_ok=True)

    model_dataset.to_csv(dataset_path, index=False)
    rules.to_csv(rules_path, index=False)
    full_metadata = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_resolution": "10min",
        "backup_resolution": "6h",
        **metadata,
    }
    metadata_path.write_text(json.dumps(full_metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    for source in backup_6h_paths or []:
        source_path = Path(source)
        if source_path.exists():
            shutil.copy2(source_path, backup_dir / source_path.name)

    return {
        "dataset": dataset_path,
        "rules": rules_path,
        "metadata": metadata_path,
        "backup_dir": backup_dir,
    }
