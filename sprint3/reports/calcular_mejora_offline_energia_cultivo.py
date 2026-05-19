from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


REPORT_DIR = Path(__file__).resolve().parent
SPRINT_DIR = REPORT_DIR.parent
SRC_DIR = SPRINT_DIR / "src"
DATASET_PATH = SPRINT_DIR / "outputs_10min" / "dataset_modelizacion_10min.csv"
OUTPUT_JSON = REPORT_DIR / "validacion_offline_mejora_energia_cultivo.json"

sys.path.insert(0, str(SRC_DIR))

from core.agricultural_rules import build_crop_risk_dataset  # noqa: E402
from core.rl_policy import _merged_reward_frame, build_offline_dqn_policy  # noqa: E402


ACTION_COLUMNS = [
    "rl_angle_deg",
    "tracking_regime",
    "crop_management_action",
    "panel_action",
    "irrigation_mode",
    "irrigation_active",
    "irrigation_mm_10min",
    "irrigation_duration_min",
]


def _normalise_action_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=True).reset_index(drop=True)
    for column in ACTION_COLUMNS:
        if column not in result.columns:
            result.loc[:, column] = pd.NA
    result.loc[:, "rl_angle_deg"] = pd.to_numeric(result["rl_angle_deg"], errors="coerce").round(4)
    result.loc[:, "irrigation_mm_10min"] = (
        pd.to_numeric(result["irrigation_mm_10min"], errors="coerce").fillna(0).round(4)
    )
    result.loc[:, "irrigation_duration_min"] = (
        pd.to_numeric(result["irrigation_duration_min"], errors="coerce").fillna(0).round(4)
    )
    result.loc[:, "irrigation_active"] = result["irrigation_active"].fillna(False).astype(bool)
    for column in ["tracking_regime", "crop_management_action", "panel_action", "irrigation_mode"]:
        result.loc[:, column] = result[column].astype(str).fillna("")
    return result


def _build_comparable_frame(model_df: pd.DataFrame, crop_type: str, crop_zone: str) -> pd.DataFrame:
    crop_risk = build_crop_risk_dataset(model_df, crop_type=crop_type, crop_zone=crop_zone)
    reward_df = _merged_reward_frame(model_df, crop_risk).copy(deep=True)
    reward_df.loc[:, "Time"] = pd.to_datetime(reward_df["Time"])
    reward_df.loc[:, "date"] = reward_df["Time"].dt.date.astype(str)

    comparable = reward_df[
        reward_df["hour_of_day"].between(6, 21)
        & reward_df["IEC"].notna()
        & reward_df["rl_reward"].notna()
    ].copy()
    records_by_day = comparable.groupby("date")["Time"].transform("size")
    comparable = comparable[records_by_day >= 24].copy()
    return _normalise_action_columns(comparable)


def calculate_improvement(crop_type: str = "lechuga", crop_zone: str = "S1") -> dict:
    model_df = pd.read_csv(DATASET_PATH)
    crop_risk = build_crop_risk_dataset(model_df, crop_type=crop_type, crop_zone=crop_zone)
    policy = build_offline_dqn_policy(model_df, crop_risk)

    comparable = _build_comparable_frame(model_df, crop_type, crop_zone)
    baseline_iec = float(comparable["IEC"].mean())
    baseline_reward = float(comparable["rl_reward"].mean())

    policy_actions = policy.rename(columns={"rl_tracking_regime": "tracking_regime"}).copy()
    policy_actions = _normalise_action_columns(policy_actions)
    policy_actions = policy_actions[
        ["state_key", "crop_type", "crop_zone", *ACTION_COLUMNS, "rl_confidence", "source"]
    ].copy()

    same_state_action = (
        comparable.groupby(["state_key", "crop_type", "crop_zone", *ACTION_COLUMNS], dropna=False)
        .agg(
            estimated_iec_same_state=("IEC", "mean"),
            estimated_reward_same_state=("rl_reward", "mean"),
            same_state_observations=("IEC", "size"),
        )
        .reset_index()
    )
    global_action = (
        comparable.groupby(ACTION_COLUMNS, dropna=False)
        .agg(
            estimated_iec_global=("IEC", "mean"),
            estimated_reward_global=("rl_reward", "mean"),
            global_observations=("IEC", "size"),
        )
        .reset_index()
    )

    estimated = (
        comparable[["Time", "date", "state_key", "crop_type", "crop_zone", "IEC", "rl_reward"]]
        .merge(
            policy_actions,
            on=["state_key", "crop_type", "crop_zone"],
            how="left",
            suffixes=("", "_policy"),
        )
        .copy(deep=True)
    )
    estimated = estimated.merge(
        same_state_action,
        on=["state_key", "crop_type", "crop_zone", *ACTION_COLUMNS],
        how="left",
    ).copy(deep=True)
    estimated = estimated.merge(global_action, on=ACTION_COLUMNS, how="left").copy(deep=True)

    estimated.loc[:, "estimated_iec"] = estimated["estimated_iec_same_state"].fillna(
        estimated["estimated_iec_global"]
    )
    estimated.loc[:, "estimated_reward"] = estimated["estimated_reward_same_state"].fillna(
        estimated["estimated_reward_global"]
    )
    estimated.loc[:, "estimate_source"] = "same_state_action"
    estimated.loc[estimated["estimated_iec_same_state"].isna(), "estimate_source"] = "global_action"
    estimated.loc[estimated["estimated_iec"].isna(), "estimate_source"] = "baseline_fallback"
    estimated.loc[:, "estimated_iec"] = estimated["estimated_iec"].fillna(baseline_iec)
    estimated.loc[:, "estimated_reward"] = estimated["estimated_reward"].fillna(baseline_reward)

    system_iec = float(estimated["estimated_iec"].mean())
    system_reward = float(estimated["estimated_reward"].mean())
    iec_improvement_pct = float(((system_iec - baseline_iec) / baseline_iec) * 100)
    reward_improvement_pct = float(((system_reward - baseline_reward) / baseline_reward) * 100)

    daily = (
        estimated.groupby("date")
        .agg(
            historical_iec=("IEC", "mean"),
            system_iec=("estimated_iec", "mean"),
            historical_reward=("rl_reward", "mean"),
            system_reward=("estimated_reward", "mean"),
        )
        .reset_index()
    )
    daily = daily.copy(deep=True)
    daily.loc[:, "iec_improvement_pct"] = (
        (daily["system_iec"] - daily["historical_iec"]) / daily["historical_iec"] * 100
    )
    daily.loc[:, "reward_improvement_pct"] = (
        (daily["system_reward"] - daily["historical_reward"]) / daily["historical_reward"] * 100
    )

    result = {
        "dataset": str(DATASET_PATH.relative_to(SPRINT_DIR)),
        "crop_type": crop_type,
        "crop_zone": crop_zone,
        "records": int(len(comparable)),
        "comparable_days": int(comparable["date"].nunique()),
        "date_min": str(comparable["Time"].min()),
        "date_max": str(comparable["Time"].max()),
        "hour_filter": "06:00-21:59",
        "policy_source": str(policy["source"].iloc[0]) if not policy.empty and "source" in policy else "unknown",
        "policy_states": int(len(policy)),
        "historical_iec_mean": round(baseline_iec, 4),
        "system_dqn_iec_mean": round(system_iec, 4),
        "iec_improvement_pct": round(iec_improvement_pct, 2),
        "historical_reward_mean": round(baseline_reward, 4),
        "system_dqn_reward_mean": round(system_reward, 4),
        "reward_improvement_pct": round(reward_improvement_pct, 2),
        "estimate_source_share": {
            key: round(float(value), 4)
            for key, value in estimated["estimate_source"].value_counts(normalize=True).sort_index().items()
        },
        "daily_iec_improvement_pct": {
            "mean": round(float(daily["iec_improvement_pct"].mean()), 2),
            "median": round(float(daily["iec_improvement_pct"].median()), 2),
            "p25": round(float(daily["iec_improvement_pct"].quantile(0.25)), 2),
            "p75": round(float(daily["iec_improvement_pct"].quantile(0.75)), 2),
        },
        "daily_reward_improvement_pct": {
            "mean": round(float(daily["reward_improvement_pct"].mean()), 2),
            "median": round(float(daily["reward_improvement_pct"].median()), 2),
            "p25": round(float(daily["reward_improvement_pct"].quantile(0.25)), 2),
            "p75": round(float(daily["reward_improvement_pct"].quantile(0.75)), 2),
        },
        "formula": "((indice_sistema_DQN - indice_historico) / indice_historico) * 100",
        "interpretation_note": (
            "Estimacion offline basada en datos historicos; no equivale a una prueba experimental en campo."
        ),
    }
    return result


def main() -> None:
    result = calculate_improvement()
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
