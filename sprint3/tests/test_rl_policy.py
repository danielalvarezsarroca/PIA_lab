import json
import pandas as pd

from agricultural_rules import build_crop_risk_dataset
from rl_policy import (
    build_rl_trajectories,
    build_offline_rl_policy,
    _merged_reward_frame,
    recommend_action_for_record,
    write_rl_trajectory_outputs,
    write_rl_policy_outputs,
)
from ten_min_pipeline import build_modeling_dataset_10min
from tests.test_agricultural_rules import _stress_sample


def _stress_sample_with_night_rows() -> pd.DataFrame:
    sample = _stress_sample()
    night_rows = sample.iloc[[0, 1]].copy()
    night_rows.loc[:, "Time"] = pd.to_datetime(["2026-05-03 23:00", "2026-05-03 23:10"])
    night_rows.loc[:, "tracker_angle_deg"] = 0.0
    night_rows.loc[:, "solar_elevation_deg"] = -18.0
    night_rows.loc[:, "solar_azimuth_deg"] = 320.0
    night_rows.loc[:, "clearsky_ghi_wm2"] = 0.0
    night_rows.loc[:, "GPOA_mean"] = 0.0
    night_rows.loc[:, "PAR_R1"] = 0.0
    night_rows.loc[:, "PAR_S1"] = 0.0
    night_rows.loc[:, "PAR_S2"] = 0.0
    night_rows.loc[:, "Tsoil_S1_mean"] = [14.0, 13.8]
    night_rows.loc[:, "Tsoil_S2_mean"] = [13.7, 13.5]
    night_rows.loc[:, "VWC_S1_mean"] = [19.5, 19.3]
    night_rows.loc[:, "VWC_S2_mean"] = [20.2, 20.0]
    return pd.concat([sample, night_rows], ignore_index=True)


def test_build_offline_rl_policy_combines_energy_and_agronomic_reward():
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")

    policy = build_offline_rl_policy(model, crop_risk)

    assert not policy.empty
    assert {
        "state_key",
        "rl_angle_deg",
        "rl_tracking_regime",
        "agronomic_action",
        "rl_reward",
        "energy_component",
        "agronomic_component",
        "source",
    }.issubset(policy.columns)
    assert policy["rl_reward"].between(0, 1).all()
    assert policy["source"].eq("offline_rl_tabular_masterdataset").all()
    assert policy["agronomic_action"].isin({
        "activar_riego",
        "pausar_riego",
        "riego_preventivo",
        "poda_sanitaria",
        "proteccion_frio",
        "aumentar_sombreado",
        "posicion_segura",
        "mantener",
    }).any()


def test_recommend_action_for_record_returns_nearest_policy_state():
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    policy = build_offline_rl_policy(model, crop_risk)
    record = model.iloc[-1].copy()

    recommendation = recommend_action_for_record(policy, record)

    assert recommendation["source"] == "offline_rl_tabular_masterdataset"
    assert pd.notna(recommendation["rl_angle_deg"])
    assert pd.notna(recommendation["agronomic_action"])


def test_write_rl_policy_outputs_creates_policy_file(tmp_path):
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    policy = build_offline_rl_policy(model, crop_risk)

    paths = write_rl_policy_outputs(tmp_path, policy)

    assert paths["rl_policy"].exists()
    assert "offline_rl_tabular_masterdataset" in paths["rl_policy"].read_text(encoding="utf-8")


def test_rl_reward_penalizes_critical_crop_damage():
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    baseline_risk = crop_risk.copy()
    damaged_risk = crop_risk.copy()
    for column in ["water_deficit", "water_excess", "heat_stress", "cold_stress", "excess_radiation"]:
        baseline_risk[column] = False
        damaged_risk[column] = False
    damaged_risk["water_deficit"] = True
    damaged_risk["heat_stress"] = True

    baseline_policy = build_offline_rl_policy(model, baseline_risk)
    damaged_policy = build_offline_rl_policy(model, damaged_risk)
    comparison = baseline_policy[["state_key", "rl_reward"]].merge(
        damaged_policy[["state_key", "rl_reward"]],
        on="state_key",
        suffixes=("_baseline", "_damaged"),
    )
    comparable = comparison[comparison["rl_reward_baseline"] > 0.36]

    assert not comparable.empty
    assert (comparable["rl_reward_damaged"] <= comparable["rl_reward_baseline"] - 0.34).all()


def test_rl_reward_uses_explicit_agricultural_and_energy_weights_before_damage_penalty():
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    clean_risk = crop_risk.copy()
    damaged_risk = crop_risk.copy()
    for column in ["water_deficit", "water_excess", "heat_stress", "cold_stress", "excess_radiation"]:
        clean_risk[column] = False
        damaged_risk[column] = False
    damaged_risk["water_excess"] = True

    clean_frame = _merged_reward_frame(model, clean_risk)
    damaged_frame = _merged_reward_frame(model, damaged_risk)

    clean_expected = (
        clean_frame["reward_alpha_agronomic"] * clean_frame["agronomic_component"]
        + clean_frame["reward_beta_energy"] * clean_frame["energy_component"]
    ).clip(0, 1)
    damaged_expected = (
        damaged_frame["reward_alpha_agronomic"] * damaged_frame["agronomic_component"]
        + damaged_frame["reward_beta_energy"] * damaged_frame["energy_component"]
        - 0.35
    ).clip(0, 1)
    pd.testing.assert_series_equal(
        clean_frame["rl_reward"].round(4).reset_index(drop=True),
        clean_expected.round(4).reset_index(drop=True),
        check_names=False,
    )
    pd.testing.assert_series_equal(
        damaged_frame["rl_reward"].round(4).reset_index(drop=True),
        damaged_expected.round(4).reset_index(drop=True),
        check_names=False,
    )


def test_rl_policy_exposes_irrigation_actuator_as_independent_action():
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")

    policy = build_offline_rl_policy(model, crop_risk)

    assert {
        "irrigation_mode",
        "irrigation_active",
        "irrigation_mm_10min",
        "irrigation_duration_min",
    }.issubset(policy.columns)
    joint_actions = policy[
        policy["irrigation_active"]
        & policy["panel_action"].ne("mantener_placas")
    ]
    assert not joint_actions.empty


def test_rl_policy_metadata_includes_weighted_reward_and_damage_penalty(tmp_path):
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    policy = build_offline_rl_policy(model, crop_risk)

    paths = write_rl_policy_outputs(tmp_path, policy)
    metadata = (tmp_path / "rl_policy_metadata.json").read_text(encoding="utf-8")

    assert "alpha * agronomic_component + beta * energy_component" in metadata
    assert "penalty_damage" in metadata


def test_rl_policy_metadata_describes_factorized_actions(tmp_path):
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    policy = build_offline_rl_policy(model, crop_risk)

    paths = write_rl_policy_outputs(tmp_path, policy)
    metadata = json.loads(paths["rl_policy_metadata"].read_text(encoding="utf-8"))

    action_factorization = metadata.get("action_factorization", {})
    assert action_factorization.get("type") == "factorized_joint_action"
    assert {"panel_action", "irrigation_action"}.issubset(
        set(action_factorization.get("dimensions", []))
    )
    for key in ["description", "rationale", "reward_scope"]:
        assert isinstance(action_factorization.get(key), str)
        assert action_factorization.get(key)
    assert "panel_action" in policy.columns
    assert {
        "irrigation_mode",
        "irrigation_active",
        "irrigation_mm_10min",
        "irrigation_duration_min",
    }.issubset(policy.columns)


def test_rl_trajectories_keep_night_rows_and_temporal_irrigation_context():
    model = build_modeling_dataset_10min(_stress_sample_with_night_rows())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")

    trajectories = build_rl_trajectories(model, crop_risk, context_steps=3)

    assert not trajectories.empty
    assert {
        "episode_id",
        "step_in_episode",
        "is_night",
        "crop_type",
        "crop_zone",
        "VWC_crop_zone_fraction",
        "Tsoil_crop_zone_mean",
        "ePAR_crop_zone_mean",
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
        "irrigation_mode",
        "irrigation_active",
        "irrigation_mm_10min",
        "panel_action",
        "crop_management_action",
        "rl_reward",
    }.issubset(trajectories.columns)
    assert trajectories["is_night"].any()
    assert trajectories.loc[trajectories["is_night"], "solar_band"].eq("night").all()
    assert trajectories["Time"].is_monotonic_increasing
    assert trajectories.groupby("episode_id")["step_in_episode"].min().eq(0).all()
    assert trajectories["irrigation_context_mm"].ge(0).all()


def test_rl_trajectories_use_selected_crop_zone_context():
    model = build_modeling_dataset_10min(_stress_sample_with_night_rows())
    crop_risk = build_crop_risk_dataset(model, crop_type="patata", crop_zone="S2")

    trajectories = build_rl_trajectories(model, crop_risk, context_steps=3)

    assert not trajectories.empty
    assert trajectories["crop_type"].eq("patata").all()
    assert trajectories["crop_zone"].eq("S2").all()
    assert {
        "VWC_crop_zone_source",
        "Tsoil_crop_zone_source",
        "ePAR_crop_zone_source",
    }.issubset(trajectories.columns)
    pd.testing.assert_series_equal(
        trajectories["VWC_crop_zone_fraction"].reset_index(drop=True),
        crop_risk["VWC_crop_zone_fraction"].round(4).reset_index(drop=True),
        check_names=False,
    )
    for column in ["VWC_crop_zone_source", "Tsoil_crop_zone_source", "ePAR_crop_zone_source"]:
        pd.testing.assert_series_equal(
            trajectories[column].reset_index(drop=True),
            crop_risk[column].reset_index(drop=True),
            check_names=False,
        )
    assert not trajectories["VWC_crop_zone_fraction"].equals(trajectories["VWC_S1_mean"])
    first_episode = trajectories[trajectories["episode_id"].eq(trajectories["episode_id"].iloc[0])]
    assert first_episode["vwc_crop_zone_context_mean"].iloc[0] == first_episode["VWC_crop_zone_fraction"].iloc[0]


def test_write_rl_trajectory_outputs_creates_training_artifacts(tmp_path):
    model = build_modeling_dataset_10min(_stress_sample_with_night_rows())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    trajectories = build_rl_trajectories(model, crop_risk, context_steps=3)

    paths = write_rl_trajectory_outputs(tmp_path, trajectories)

    assert paths["rl_trajectories"].exists()
    assert paths["rl_trajectories_metadata"].exists()
    assert "rl_trajectories_10min" in paths["rl_trajectories_metadata"].read_text(encoding="utf-8")
