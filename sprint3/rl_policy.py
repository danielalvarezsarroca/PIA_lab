from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_REWARD_ALPHA_AGRONOMIC = 0.45
DEFAULT_REWARD_BETA_ENERGY = 0.55
DEFAULT_DAMAGE_PENALTY = 0.35

POLICY_COLUMNS = [
    "state_key",
    "hour_of_day",
    "solar_band",
    "stress_type",
    "crop_type",
    "crop_zone",
    "rl_angle_deg",
    "rl_tracking_regime",
    "agronomic_action",
    "crop_management_action",
    "panel_action",
    "irrigation_mode",
    "irrigation_active",
    "irrigation_mm_10min",
    "irrigation_duration_min",
    "rl_reward",
    "rl_confidence",
    "energy_component",
    "agronomic_component",
    "water_stress_score",
    "future_water_stress_score",
    "irrigation_need_score",
    "reward_alpha_agronomic",
    "reward_beta_energy",
    "observations",
    "source",
]

TRAJECTORY_COLUMNS = [
    "Time",
    "episode_id",
    "step_in_episode",
    "is_night",
    "state_key",
    "hour_of_day",
    "solar_band",
    "stress_type",
    "crop_type",
    "crop_zone",
    "VWC_S1_mean",
    "Tsoil_S1_mean",
    "ePAR_S1_mean",
    "VWC_crop_zone_fraction",
    "Tsoil_crop_zone_mean",
    "ePAR_crop_zone_mean",
    "VWC_crop_zone_source",
    "Tsoil_crop_zone_source",
    "ePAR_crop_zone_source",
    "energy_component",
    "agronomic_component",
    "water_stress_score",
    "future_water_stress_score",
    "irrigation_need_score",
    "projected_vwc_no_irrigation_1h",
    "rl_reward",
    "rl_angle_deg",
    "tracking_regime",
    "panel_action",
    "crop_management_action",
    "irrigation_mode",
    "irrigation_active",
    "irrigation_mm_10min",
    "irrigation_duration_min",
    "prev_vwc_s1_mean",
    "prev_tsoil_s1_mean",
    "prev_vwc_crop_zone_fraction",
    "prev_tsoil_crop_zone_mean",
    "prev_irrigation_active",
    "vwc_s1_context_mean",
    "tsoil_s1_context_mean",
    "vwc_crop_zone_context_mean",
    "tsoil_crop_zone_context_mean",
    "irrigation_context_mm",
]

CRITICAL_DAMAGE_COLUMNS = [
    "water_deficit",
    "water_excess",
    "heat_stress",
    "cold_stress",
    "excess_radiation",
]

DQN_ACTION_COLUMNS = [
    "rl_angle_deg",
    "tracking_regime",
    "recommended_action",
    "crop_management_action",
    "panel_action",
    "irrigation_mode",
    "irrigation_active",
    "irrigation_mm_10min",
    "irrigation_duration_min",
]

DQN_NUMERIC_STATE_COLUMNS = [
    "hour_of_day",
    "solar_elevation_deg",
    "track_mean",
    "energy_component",
    "agronomic_component",
    "water_stress_score",
    "future_water_stress_score",
    "irrigation_need_score",
    "projected_vwc_no_irrigation_1h",
    "VWC_crop_zone_fraction",
    "Tsoil_crop_zone_mean",
    "ePAR_crop_zone_mean",
]

DQN_CATEGORICAL_STATE_COLUMNS = ["state_key", "solar_band", "stress_type", "crop_type", "crop_zone"]


def _solar_band(elevation: float) -> str:
    if pd.isna(elevation) or elevation <= 0:
        return "night"
    if elevation < 25:
        return "low"
    if elevation < 55:
        return "medium"
    return "high"


def _angle_bucket(angle: float, step: int = 5) -> float:
    if pd.isna(angle):
        return 0.0
    return float(round(float(angle) / step) * step)


def _state_key(hour: int, solar_band: str, stress_type: str) -> str:
    return f"h{int(hour):02d}|sun:{solar_band}|stress:{stress_type}"


def _is_critical_damage(row: pd.Series) -> bool:
    return bool(any(row.get(column, False) for column in CRITICAL_DAMAGE_COLUMNS))


def _apply_damage_penalty(reward: pd.Series, damage: pd.Series) -> pd.Series:
    return (reward - DEFAULT_DAMAGE_PENALTY * damage.astype(float)).clip(0, 1)


def _merged_reward_frame(
    model_df: pd.DataFrame,
    crop_risk: pd.DataFrame,
    *,
    alpha_agronomic: float = DEFAULT_REWARD_ALPHA_AGRONOMIC,
    beta_energy: float = DEFAULT_REWARD_BETA_ENERGY,
) -> pd.DataFrame:
    model = model_df.copy()
    risk = crop_risk.copy()
    model = model.assign(Time=pd.to_datetime(model["Time"]))
    risk = risk.assign(Time=pd.to_datetime(risk["Time"]))
    risk_columns = [
        "Time",
        "crop_type",
        "crop_zone",
        "crop_health_score",
        "Tsoil_crop_zone_mean",
        "VWC_crop_zone_fraction",
        "ePAR_crop_zone_mean",
        "Tsoil_crop_zone_source",
        "VWC_crop_zone_source",
        "ePAR_crop_zone_source",
        "recommended_action",
        "crop_management_action",
        "panel_action",
        "irrigation_mode",
        "irrigation_active",
        "irrigation_mm_10min",
        "irrigation_duration_min",
        "water_stress_score",
        "future_water_stress_score",
        "irrigation_need_score",
        "projected_vwc_no_irrigation_1h",
        "stress_type",
        *CRITICAL_DAMAGE_COLUMNS,
    ]
    available_risk_columns = [column for column in risk_columns if column in risk.columns]
    df = model.merge(
        risk[available_risk_columns],
        on="Time",
        how="left",
    )
    df = df.assign(
        crop_type=df.get("crop_type", pd.Series(index=df.index, dtype="object")).fillna("unknown"),
        crop_zone=df.get("crop_zone", pd.Series(index=df.index, dtype="object")).fillna("S1"),
        Tsoil_crop_zone_mean=pd.to_numeric(
            df.get("Tsoil_crop_zone_mean", pd.Series(index=df.index, dtype="float64")),
            errors="coerce",
        ).fillna(pd.to_numeric(df.get("Tsoil_S1_mean", pd.Series(index=df.index, dtype="float64")), errors="coerce")),
        VWC_crop_zone_fraction=pd.to_numeric(
            df.get("VWC_crop_zone_fraction", pd.Series(index=df.index, dtype="float64")),
            errors="coerce",
        ).fillna(pd.to_numeric(df.get("VWC_S1_mean", pd.Series(index=df.index, dtype="float64")), errors="coerce")),
        ePAR_crop_zone_mean=pd.to_numeric(
            df.get("ePAR_crop_zone_mean", pd.Series(index=df.index, dtype="float64")),
            errors="coerce",
        ).fillna(pd.to_numeric(df.get("ePAR_S1_mean", pd.Series(index=df.index, dtype="float64")), errors="coerce")),
        Tsoil_crop_zone_source=df.get(
            "Tsoil_crop_zone_source", pd.Series(index=df.index, dtype="object")
        ).fillna("Tsoil_S1_mean_fallback"),
        VWC_crop_zone_source=df.get(
            "VWC_crop_zone_source", pd.Series(index=df.index, dtype="object")
        ).fillna("VWC_S1_mean_fallback"),
        ePAR_crop_zone_source=df.get(
            "ePAR_crop_zone_source", pd.Series(index=df.index, dtype="object")
        ).fillna("ePAR_S1_mean_fallback"),
        crop_health_score=pd.to_numeric(df["crop_health_score"], errors="coerce").fillna(df["crop_score"]),
        recommended_action=df["recommended_action"].fillna("mantener"),
        crop_management_action=df["crop_management_action"].fillna("sin_manejo_directo"),
        panel_action=df["panel_action"].fillna("mantener_placas"),
        irrigation_mode=df.get("irrigation_mode", pd.Series(index=df.index, dtype="object")).fillna("off"),
        irrigation_active=df.get("irrigation_active", pd.Series(index=df.index, dtype="bool")).fillna(False).astype(bool),
        irrigation_mm_10min=pd.to_numeric(
            df.get("irrigation_mm_10min", pd.Series(index=df.index, dtype="float64")),
            errors="coerce",
        ).fillna(0),
        irrigation_duration_min=pd.to_numeric(
            df.get("irrigation_duration_min", pd.Series(index=df.index, dtype="float64")),
            errors="coerce",
        ).fillna(0),
        stress_type=df["stress_type"].fillna("estable"),
    )
    df = df.assign(
        energy_component=pd.to_numeric(df["energy_score"], errors="coerce").fillna(0).clip(0, 1),
        water_stress_score=pd.to_numeric(
            df.get("water_stress_score", pd.Series(index=df.index, dtype="float64")),
            errors="coerce",
        ).fillna(0).clip(0, 1),
        future_water_stress_score=pd.to_numeric(
            df.get("future_water_stress_score", pd.Series(index=df.index, dtype="float64")),
            errors="coerce",
        ).fillna(0).clip(0, 1),
        irrigation_need_score=pd.to_numeric(
            df.get("irrigation_need_score", pd.Series(index=df.index, dtype="float64")),
            errors="coerce",
        ).fillna(0).clip(0, 1),
        projected_vwc_no_irrigation_1h=pd.to_numeric(
            df.get("projected_vwc_no_irrigation_1h", pd.Series(index=df.index, dtype="float64")),
            errors="coerce",
        ).fillna(df["VWC_crop_zone_fraction"]).clip(0, 1),
        reward_alpha_agronomic=float(alpha_agronomic),
        reward_beta_energy=float(beta_energy),
    )
    projected_water_penalty = (
        0.16 * df["future_water_stress_score"] + 0.06 * df["irrigation_need_score"]
    ).clip(0, 0.22)
    df = df.assign(
        agronomic_component=(
            pd.to_numeric(df["crop_health_score"], errors="coerce").fillna(0).clip(0, 1)
            - projected_water_penalty
        ).clip(0, 1)
    )
    for column in CRITICAL_DAMAGE_COLUMNS:
        if column not in df.columns:
            df[column] = False
        df.loc[:, column] = df[column].fillna(False).astype(bool)
    # Offline tabular reward: explicit crop/energy trade-off plus agronomic damage guardrail.
    reward_base = (
        df["reward_alpha_agronomic"] * df["agronomic_component"]
        + df["reward_beta_energy"] * df["energy_component"]
    ).clip(0, 1)
    damage_flag = df.apply(_is_critical_damage, axis=1)
    reward = _apply_damage_penalty(reward_base, damage_flag)
    solar_band = df["solar_elevation_deg"].map(_solar_band)
    df = df.assign(
        rl_reward=reward,
        solar_band=solar_band,
        rl_angle_deg=df["track_mean"].map(_angle_bucket),
    )
    state_keys = [
        _state_key(hour, band, stress)
        for hour, band, stress in zip(df["hour_of_day"], df["solar_band"], df["stress_type"], strict=False)
    ]
    df = df.assign(state_key=state_keys)
    return df


def build_offline_rl_policy(
    model_df: pd.DataFrame,
    crop_risk: pd.DataFrame,
    *,
    alpha_agronomic: float = DEFAULT_REWARD_ALPHA_AGRONOMIC,
    beta_energy: float = DEFAULT_REWARD_BETA_ENERGY,
) -> pd.DataFrame:
    df = _merged_reward_frame(model_df, crop_risk, alpha_agronomic=alpha_agronomic, beta_energy=beta_energy)
    df = df.dropna(subset=["state_key", "rl_angle_deg", "tracking_regime", "rl_reward"])
    if df.empty:
        raise ValueError("Cannot build RL policy without valid model and crop risk rows")

    action_values = (
        df.groupby(
            [
                "state_key",
                "hour_of_day",
                "solar_band",
                "stress_type",
                "crop_type",
                "crop_zone",
                "rl_angle_deg",
                "tracking_regime",
                "recommended_action",
                "crop_management_action",
                "panel_action",
                "irrigation_mode",
                "irrigation_active",
                "irrigation_mm_10min",
                "irrigation_duration_min",
            ],
            as_index=False,
        )
        .agg(
            rl_reward=("rl_reward", "mean"),
            energy_component=("energy_component", "mean"),
            agronomic_component=("agronomic_component", "mean"),
            water_stress_score=("water_stress_score", "mean"),
            future_water_stress_score=("future_water_stress_score", "mean"),
            irrigation_need_score=("irrigation_need_score", "mean"),
            reward_alpha_agronomic=("reward_alpha_agronomic", "first"),
            reward_beta_energy=("reward_beta_energy", "first"),
            observations=("rl_reward", "size"),
        )
        .sort_values(
            ["crop_zone", "crop_type", "state_key", "rl_reward", "observations"],
            ascending=[True, True, True, False, False],
        )
    )
    confidence_by_state = action_values.groupby(["state_key", "crop_type", "crop_zone"])["rl_reward"].transform(
        _confidence_from_q_values
    )
    action_values = action_values.assign(rl_confidence=confidence_by_state)
    best = action_values.groupby(["state_key", "crop_type", "crop_zone"], as_index=False).head(1).copy()
    best = best.rename(
        columns={
            "tracking_regime": "rl_tracking_regime",
            "recommended_action": "agronomic_action",
        }
    )
    best["source"] = "offline_rl_tabular_masterdataset"
    return best[POLICY_COLUMNS].round(4).reset_index(drop=True)


def _confidence_from_q_values(q_values: list[float] | np.ndarray | pd.Series) -> float:
    values = pd.to_numeric(pd.Series(q_values), errors="coerce").dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return 0.0
    if len(values) == 1:
        return 1.0

    ordered = np.sort(values)[::-1]
    best = float(ordered[0])
    second_best = float(ordered[1])
    if best <= 0:
        return 0.0
    return round(float(np.clip((best - second_best) / best, 0, 1)), 4)


def _action_key_frame(df: pd.DataFrame) -> pd.Series:
    parts = []
    for column in DQN_ACTION_COLUMNS:
        if column not in df.columns:
            parts.append(pd.Series([""] * len(df), index=df.index, dtype="object"))
        else:
            parts.append(df[column].astype(str).fillna(""))
    return pd.concat(parts, axis=1).agg("|".join, axis=1)


def _dqn_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame = frame.assign(action_key=_action_key_frame(frame).reset_index(drop=True))
    numeric = pd.DataFrame(index=frame.index)
    for column in DQN_NUMERIC_STATE_COLUMNS:
        numeric[column] = pd.to_numeric(
            frame.get(column, pd.Series(0.0, index=frame.index)),
            errors="coerce",
        ).fillna(0.0)
    categorical_columns = [
        column for column in [*DQN_CATEGORICAL_STATE_COLUMNS, "action_key"] if column in frame.columns
    ]
    categorical = pd.get_dummies(
        frame[categorical_columns].astype(str),
        prefix=categorical_columns,
        dtype=float,
    )
    return pd.concat([numeric, categorical], axis=1)


def _fit_numpy_q_network(
    x: np.ndarray,
    rewards: np.ndarray,
    next_x: np.ndarray,
    terminal: np.ndarray,
    *,
    epochs: int,
    gamma: float,
    hidden_size: int,
    seed: int,
    learning_rate: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    input_size = x.shape[1]
    hidden = max(4, min(hidden_size, max(4, input_size * 2)))
    w1 = rng.normal(0.0, 0.08, size=(input_size, hidden))
    b1 = np.zeros(hidden)
    w2 = rng.normal(0.0, 0.08, size=(hidden, 1))
    b2 = np.zeros(1)
    target_w1 = w1.copy()
    target_b1 = b1.copy()
    target_w2 = w2.copy()
    target_b2 = b2.copy()

    def forward(values: np.ndarray, params: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]):
        layer_w1, layer_b1, layer_w2, layer_b2 = params
        hidden_raw = values @ layer_w1 + layer_b1
        hidden_act = np.maximum(hidden_raw, 0)
        q_values = hidden_act @ layer_w2 + layer_b2
        return hidden_raw, hidden_act, q_values.reshape(-1)

    for epoch in range(max(1, epochs)):
        _, _, next_q = forward(next_x, (target_w1, target_b1, target_w2, target_b2))
        td_target = rewards + gamma * next_q * (~terminal).astype(float)
        td_target = np.clip(td_target, 0, 1)

        hidden_raw, hidden_act, q_pred = forward(x, (w1, b1, w2, b2))
        error = (q_pred - td_target) / max(1, len(x))
        grad_q = error[:, None]
        grad_w2 = hidden_act.T @ grad_q
        grad_b2 = grad_q.sum(axis=0)
        grad_hidden = (grad_q @ w2.T) * (hidden_raw > 0)
        grad_w1 = x.T @ grad_hidden
        grad_b1 = grad_hidden.sum(axis=0)

        w1 -= learning_rate * grad_w1
        b1 -= learning_rate * grad_b1
        w2 -= learning_rate * grad_w2
        b2 -= learning_rate * grad_b2

        if (epoch + 1) % 5 == 0:
            target_w1, target_b1, target_w2, target_b2 = w1.copy(), b1.copy(), w2.copy(), b2.copy()

    return w1, b1, w2, b2


def _predict_numpy_q_network(
    x: np.ndarray,
    params: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> np.ndarray:
    w1, b1, w2, b2 = params
    hidden = np.maximum(x @ w1 + b1, 0)
    return (hidden @ w2 + b2).reshape(-1)


def build_offline_dqn_policy(
    model_df: pd.DataFrame,
    crop_risk: pd.DataFrame,
    *,
    alpha_agronomic: float = DEFAULT_REWARD_ALPHA_AGRONOMIC,
    beta_energy: float = DEFAULT_REWARD_BETA_ENERGY,
    epochs: int = 60,
    gamma: float = 0.85,
    hidden_size: int = 48,
    learning_rate: float = 0.025,
    seed: int = 42,
    max_candidate_actions: int = 24,
) -> pd.DataFrame:
    df = _merged_reward_frame(model_df, crop_risk, alpha_agronomic=alpha_agronomic, beta_energy=beta_energy)
    df = df.dropna(subset=["state_key", "rl_angle_deg", "tracking_regime", "rl_reward"]).copy()
    if df.empty:
        raise ValueError("Cannot build DQN policy without valid model and crop risk rows")

    df = df.sort_values("Time").reset_index(drop=True)
    features = _dqn_feature_frame(df)
    feature_columns = list(features.columns)
    mean = features.mean(axis=0)
    std = features.std(axis=0).replace(0, 1).fillna(1)
    x = ((features - mean) / std).to_numpy(dtype=float)
    rewards = pd.to_numeric(df["rl_reward"], errors="coerce").fillna(0).to_numpy(dtype=float)

    next_x = np.roll(x, -1, axis=0)
    next_day = df["Time"].dt.date.shift(-1)
    terminal = df["Time"].dt.date.ne(next_day).fillna(True).to_numpy(dtype=bool)
    if len(next_x):
        next_x[-1] = x[-1]
        terminal[-1] = True

    params = _fit_numpy_q_network(
        x,
        rewards,
        next_x,
        terminal,
        epochs=epochs,
        gamma=gamma,
        hidden_size=hidden_size,
        seed=seed,
        learning_rate=learning_rate,
    )

    action_stats = (
        df.groupby(DQN_ACTION_COLUMNS, as_index=False, dropna=False)
        .agg(
            observed_reward=("rl_reward", "mean"),
            observations=("rl_reward", "size"),
        )
        .sort_values(["observed_reward", "observations"], ascending=[False, False])
        .head(max(1, max_candidate_actions))
        .reset_index(drop=True)
    )
    state_rows = (
        df.sort_values("Time")
        .groupby(["state_key", "crop_type", "crop_zone"], as_index=False, dropna=False)
        .tail(1)
        .reset_index(drop=True)
    )

    best_rows = []
    for _, state_row in state_rows.iterrows():
        candidates = pd.concat([state_row.to_frame().T] * len(action_stats), ignore_index=True)
        for column in DQN_ACTION_COLUMNS:
            candidates[column] = action_stats[column].to_numpy()
        candidate_features = _dqn_feature_frame(candidates).reindex(columns=feature_columns, fill_value=0)
        candidate_x = ((candidate_features - mean) / std).to_numpy(dtype=float)
        q_values = np.clip(_predict_numpy_q_network(candidate_x, params), 0, 1)
        selected_idx = int(np.argmax(q_values))
        selected = candidates.iloc[selected_idx].copy()
        selected["rl_reward"] = float(q_values[selected_idx])
        selected["rl_confidence"] = _confidence_from_q_values(q_values)
        selected["observations"] = int(action_stats.iloc[selected_idx]["observations"])
        best_rows.append(selected)

    best = pd.DataFrame(best_rows)
    best = best.rename(
        columns={
            "tracking_regime": "rl_tracking_regime",
            "recommended_action": "agronomic_action",
        }
    )
    best["source"] = "offline_dqn_double_dqn"
    return best[POLICY_COLUMNS].round(4).reset_index(drop=True)


def build_rl_trajectories(
    model_df: pd.DataFrame,
    crop_risk: pd.DataFrame,
    *,
    context_steps: int = 6,
    alpha_agronomic: float = DEFAULT_REWARD_ALPHA_AGRONOMIC,
    beta_energy: float = DEFAULT_REWARD_BETA_ENERGY,
) -> pd.DataFrame:
    if context_steps < 1:
        raise ValueError("context_steps must be >= 1")

    df = _merged_reward_frame(model_df, crop_risk, alpha_agronomic=alpha_agronomic, beta_energy=beta_energy)
    df = df.sort_values("Time").reset_index(drop=True)
    df = df.assign(
        episode_id=df["Time"].dt.strftime("%Y-%m-%d"),
        step_in_episode=df.groupby(df["Time"].dt.date).cumcount(),
        is_night=df["solar_band"].eq("night"),
    )
    for column in [
        "VWC_S1_mean",
        "Tsoil_S1_mean",
        "ePAR_S1_mean",
        "VWC_crop_zone_fraction",
        "Tsoil_crop_zone_mean",
        "ePAR_crop_zone_mean",
        "irrigation_mm_10min",
    ]:
        df.loc[:, column] = pd.to_numeric(df[column], errors="coerce")

    grouped = df.groupby("episode_id", sort=False)
    prev_irrigation_active = grouped["irrigation_active"].shift(1)
    df = df.assign(
        prev_vwc_s1_mean=grouped["VWC_S1_mean"].shift(1),
        prev_tsoil_s1_mean=grouped["Tsoil_S1_mean"].shift(1),
        prev_vwc_crop_zone_fraction=grouped["VWC_crop_zone_fraction"].shift(1),
        prev_tsoil_crop_zone_mean=grouped["Tsoil_crop_zone_mean"].shift(1),
        prev_irrigation_active=prev_irrigation_active.eq(True),
    )
    df["vwc_s1_context_mean"] = grouped["VWC_S1_mean"].transform(
        lambda series: series.rolling(context_steps, min_periods=1).mean()
    )
    df["tsoil_s1_context_mean"] = grouped["Tsoil_S1_mean"].transform(
        lambda series: series.rolling(context_steps, min_periods=1).mean()
    )
    df["vwc_crop_zone_context_mean"] = grouped["VWC_crop_zone_fraction"].transform(
        lambda series: series.rolling(context_steps, min_periods=1).mean()
    )
    df["tsoil_crop_zone_context_mean"] = grouped["Tsoil_crop_zone_mean"].transform(
        lambda series: series.rolling(context_steps, min_periods=1).mean()
    )
    df["irrigation_context_mm"] = grouped["irrigation_mm_10min"].transform(
        lambda series: series.rolling(context_steps, min_periods=1).sum()
    )

    available_columns = [column for column in TRAJECTORY_COLUMNS if column in df.columns]
    return df[available_columns].round(4).reset_index(drop=True)


def _scope_policy_to_record(policy_df: pd.DataFrame, record: pd.Series) -> pd.DataFrame:
    scoped = policy_df
    for column in ["crop_type", "crop_zone"]:
        if column not in scoped.columns:
            continue
        value = record.get(column)
        if pd.isna(value):
            continue
        candidate = scoped[scoped[column].astype(str).eq(str(value))]
        if not candidate.empty:
            scoped = candidate
    return scoped


def recommend_action_for_record(policy_df: pd.DataFrame, record: pd.Series) -> pd.Series:
    if policy_df.empty:
        raise ValueError("RL policy is empty")
    policy_df = _scope_policy_to_record(policy_df, record)
    hour = int(record.get("hour_of_day", 12))
    band = _solar_band(float(record.get("solar_elevation_deg", np.nan)))
    stress = str(record.get("stress_type", "estable"))
    exact_key = _state_key(hour, band, stress)
    exact = policy_df[policy_df["state_key"] == exact_key]
    if not exact.empty:
        return exact.iloc[0]

    same_hour = policy_df[policy_df["hour_of_day"] == hour]
    if not same_hour.empty:
        return same_hour.sort_values(["rl_reward", "observations"], ascending=[False, False]).iloc[0]

    diffs = (policy_df["hour_of_day"] - hour).abs()
    return policy_df.loc[diffs.idxmin()]


def write_rl_policy_outputs(output_dir: str | Path, policy: pd.DataFrame) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    policy_path = output_path / "rl_policy_actions_10min.csv"
    metadata_path = output_path / "rl_policy_metadata.json"
    policy.to_csv(policy_path, index=False)
    metadata = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": "offline_rl_tabular_masterdataset",
        "reward_formula": "alpha * agronomic_component + beta * energy_component",
        "alpha_agronomic": DEFAULT_REWARD_ALPHA_AGRONOMIC,
        "beta_energy": DEFAULT_REWARD_BETA_ENERGY,
        "agronomic_component_note": (
            "crop_health_score adjusted by projected no-irrigation water stress and irrigation_need_score"
        ),
        "penalty_damage": f"fixed_{DEFAULT_DAMAGE_PENALTY}_on_critical_agronomic_damage",
        "action_factorization": {
            "type": "factorized_joint_action",
            "dimensions": ["panel_action", "irrigation_action"],
            "description": "Decision conjunta factorizada entre accion de placas y accion de riego por intervalo.",
            "rationale": "El movimiento de placas y el riego se optimizan en paralelo sin mezclar la interpretacion operativa.",
            "reward_scope": "Un unico reward por timestep que evalua la combinacion de ambas dimensiones.",
        },
        "note": (
            "Politica RL tabular offline para demo, derivada del masterdataset. "
            "Reward = alpha * componente agricola + beta * componente electrico, "
            "con penalizacion por dano agronomico critico."
        ),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"rl_policy": policy_path, "rl_policy_metadata": metadata_path}


def write_rl_trajectory_outputs(output_dir: str | Path, trajectories: pd.DataFrame) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    trajectory_path = output_path / "rl_trajectories_10min.csv"
    metadata_path = output_path / "rl_trajectories_metadata.json"
    trajectories.to_csv(trajectory_path, index=False)
    metadata = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": "rl_trajectories_10min",
        "rows": int(len(trajectories)),
        "night_rows": int(trajectories["is_night"].sum()) if "is_night" in trajectories else 0,
        "reward_formula": "alpha * agronomic_component + beta * energy_component",
        "note": (
            "Trayectorias offline a 10 minutos para modelos con contexto temporal. "
            "Conservan filas nocturnas y acciones independientes de riego y placas."
        ),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"rl_trajectories": trajectory_path, "rl_trajectories_metadata": metadata_path}
