from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


EXO_COLUMNS = [
    "hour_sin",
    "hour_cos",
    "day_sin",
    "day_cos",
    "solar_elevation_deg",
    "solar_azimuth_deg",
    "clearsky_ghi_wm2",
    "air_temp_ext_avg_degc",
    "wind_speed_kmh",
    "precip_intensity_mm10min",
    "PAR_R1",
]

ACTION_COLUMNS = [
    "tracker_angle_deg",
    "irrigation_on",
    "irrigation_dose_mm",
]

ENDO_COLUMNS = [
    "GPOA_mean",
    "ALBEDO_mean",
    "Delta_PAR_S1",
    "VWC_R1_sim",
    "minutes_since_last_irr",
    "Delta_VWC_S1_sim",
    "Tsoil_R1_sim",
    "Delta_Tsoil_S1_sim",
]

DETERMINISTIC_STATE_COLUMNS = [
    "minutes_since_last_irr",
]

LEARNED_ENDO_COLUMNS = [
    column for column in ENDO_COLUMNS if column not in DETERMINISTIC_STATE_COLUMNS
]

META_COLUMNS = [
    "Time",
    "policy_id",
    "episode_id",
    "irrigation_mm_10min",
    "irrigation_duration_min",
    "irrigation_cumulative_day_mm",
    "water_input_mm",
]


def _round_numeric(df: pd.DataFrame, decimals: int = 4) -> pd.DataFrame:
    rounded = df.copy()
    numeric_cols = rounded.select_dtypes(include="number").columns
    rounded[numeric_cols] = rounded[numeric_cols].round(decimals)
    return rounded


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"world model dataset missing required columns: {missing}")


def load_world_model_dataset(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Time"])
    _require_columns(df, META_COLUMNS + EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS)
    return df.sort_values(["policy_id", "Time"]).reset_index(drop=True)


def _bounded_score(series: pd.Series, denominator: float) -> pd.Series:
    if denominator <= 0 or pd.isna(denominator):
        return pd.Series(0.0, index=series.index)
    numeric = pd.to_numeric(series, errors="coerce").fillna(0)
    return (numeric.clip(lower=0) / denominator).clip(0, 1)


def build_dashboard_model_frame(world_df: pd.DataFrame, crop_zone: str = "S1") -> pd.DataFrame:
    _require_columns(
        world_df,
        [
            "Time",
            "tracker_angle_deg",
            "VWC_R1_sim",
            "Delta_VWC_S1_sim",
            "Tsoil_R1_sim",
            "Delta_Tsoil_S1_sim",
            "GPOA_mean",
            "PAR_R1",
            "Delta_PAR_S1",
        ],
    )
    df = world_df.copy()
    df["Time"] = pd.to_datetime(df["Time"])
    gpoa_p95 = float(pd.to_numeric(df["GPOA_mean"], errors="coerce").quantile(0.95))
    vwc_s1 = (
        pd.to_numeric(df["VWC_R1_sim"], errors="coerce")
        + pd.to_numeric(df["Delta_VWC_S1_sim"], errors="coerce")
    ).clip(0, 1)
    tsoil_s1 = (
        pd.to_numeric(df["Tsoil_R1_sim"], errors="coerce")
        + pd.to_numeric(df["Delta_Tsoil_S1_sim"], errors="coerce")
    )
    energy_score = _bounded_score(df["GPOA_mean"], gpoa_p95)
    vwc_score = (1.0 - (vwc_s1 - 0.24).abs().div(0.14)).clip(0, 1)
    temp_score = (1.0 - (tsoil_s1 - 20.0).abs().div(18.0)).clip(0, 1)
    crop_score = (0.65 * vwc_score + 0.35 * temp_score).clip(0, 1)
    frame = pd.DataFrame({
        "Time": df["Time"],
        "source_resolution": "10min_world_model",
        "minute_of_day": df["Time"].dt.hour * 60 + df["Time"].dt.minute,
        "time_block_10min": df["Time"].dt.strftime("%H:%M"),
        "hour_of_day": df["Time"].dt.hour,
        "day_of_year": df["Time"].dt.dayofyear,
        "solar_elevation_deg": df["solar_elevation_deg"],
        "solar_azimuth_deg": df["solar_azimuth_deg"],
        "clearsky_ghi_wm2": df["clearsky_ghi_wm2"],
        "track_mean": df["tracker_angle_deg"],
        "tracking_regime": np.select(
            [
                df["solar_elevation_deg"].fillna(-1) <= 0,
                df["tracker_angle_deg"].abs() < 5,
                df["tracker_angle_deg"] < 0,
            ],
            ["NIGHT_STOW", "HORIZONTAL", "TRACKING_AM"],
            default="TRACKING_PM",
        ),
        "Tair_WS": df["air_temp_ext_avg_degc"],
        "wind_speed_kmh": df["wind_speed_kmh"],
        "precip_intensity_mm10min": df["precip_intensity_mm10min"],
        "Tsoil_R1_mean": df["Tsoil_R1_sim"],
        "Tsoil_S1_mean": tsoil_s1,
        "Tsoil_S2_mean": tsoil_s1,
        "VWC_R1_mean": df["VWC_R1_sim"],
        "VWC_S1_mean": vwc_s1,
        "VWC_S2_mean": vwc_s1,
        "ePAR_R1_mean": df["PAR_R1"],
        "ePAR_S1_mean": (df["PAR_R1"] + df["Delta_PAR_S1"]).clip(lower=0),
        "ePAR_S2_mean": (df["PAR_R1"] + df["Delta_PAR_S1"]).clip(lower=0),
        "GPOA_mean": df["GPOA_mean"],
        "Delta_PAR_S1": df["Delta_PAR_S1"],
        "Delta_Tsoil_S1": df["Delta_Tsoil_S1_sim"],
        "Delta_VWC_S1": df["Delta_VWC_S1_sim"],
        "energy_score": energy_score,
        "crop_score": crop_score,
        "IEC": (0.55 * energy_score + 0.45 * crop_score).clip(0, 1),
        "crop_zone": crop_zone,
        "policy_id": df["policy_id"],
        "episode_id": df["episode_id"],
        "irrigation_on": df["irrigation_on"].astype(bool),
        "irrigation_mm_10min": df["irrigation_mm_10min"],
        "irrigation_duration_min": df["irrigation_duration_min"],
    })
    return _round_numeric(frame)


def build_transition_dataset(world_df: pd.DataFrame) -> pd.DataFrame:
    df = world_df.copy()
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.sort_values(["policy_id", "Time"]).reset_index(drop=True)
    _require_columns(df, ["policy_id", "Time"] + EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS)
    grouped = df.groupby("policy_id", sort=False)
    for column in ENDO_COLUMNS:
        df[f"next_{column}"] = grouped[column].shift(-1)
    df["next_Time"] = grouped["Time"].shift(-1)
    return df.dropna(subset=["next_Time"]).reset_index(drop=True)


def build_reward_training_dataset(
    world_df: pd.DataFrame,
    crop_type: str = "lechuga",
    crop_zone: str = "S1",
    alpha_agronomic: float = 0.45,
    beta_energy: float = 0.55,
) -> pd.DataFrame:
    transitions = build_transition_dataset(world_df)
    dashboard = build_dashboard_model_frame(world_df, crop_zone=crop_zone)
    reward_cols = dashboard[["episode_id", "energy_score", "crop_score"]].rename(
        columns={
            "energy_score": "energy_component",
            "crop_score": "agronomic_component",
        }
    )
    dataset = transitions.merge(reward_cols, on="episode_id", how="left")
    dataset["crop_type"] = crop_type
    dataset["crop_zone"] = crop_zone
    dataset["reward_alpha_agronomic"] = float(alpha_agronomic)
    dataset["reward_beta_energy"] = float(beta_energy)
    dataset["rl_reward"] = (
        dataset["reward_alpha_agronomic"] * dataset["agronomic_component"].fillna(0)
        + dataset["reward_beta_energy"] * dataset["energy_component"].fillna(0)
    ).clip(0, 1)
    return _round_numeric(dataset)
