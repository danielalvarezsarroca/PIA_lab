import pandas as pd
import pytest

from world_model_dataset import (
    ACTION_COLUMNS,
    ENDO_COLUMNS,
    EXO_COLUMNS,
    build_dashboard_model_frame,
    build_reward_training_dataset,
    build_transition_dataset,
)


def _sample_world_model_df():
    return pd.DataFrame({
        "Time": pd.date_range("2025-06-17 14:00:00", periods=4, freq="10min"),
        "policy_id": ["fixed_6h_2.0mm"] * 4,
        "episode_id": [f"fixed_6h_2.0mm_{i}" for i in range(4)],
        "hour_sin": [0.0, 0.1, 0.2, 0.3],
        "hour_cos": [1.0, 0.9, 0.8, 0.7],
        "day_sin": [0.2] * 4,
        "day_cos": [0.9] * 4,
        "solar_elevation_deg": [60.0, 58.0, 55.0, 50.0],
        "solar_azimuth_deg": [180.0, 185.0, 190.0, 195.0],
        "clearsky_ghi_wm2": [900.0, 880.0, 850.0, 810.0],
        "air_temp_ext_avg_degc": [26.0, 26.5, 27.0, 27.5],
        "wind_speed_kmh": [8.0, 8.5, 9.0, 9.5],
        "precip_intensity_mm10min": [0.0, 0.0, 0.0, 0.0],
        "PAR_R1": [1500.0, 1450.0, 1400.0, 1300.0],
        "tracker_angle_deg": [20.0, 22.0, 24.0, 26.0],
        "irrigation_on": [0, 1, 0, 0],
        "irrigation_dose_mm": [2.0, 2.0, 2.0, 2.0],
        "GPOA_mean": [700.0, 710.0, 690.0, 660.0],
        "ALBEDO_mean": [40.0, 41.0, 42.0, 43.0],
        "Delta_PAR_S1": [-200.0, -210.0, -220.0, -230.0],
        "VWC_R1_sim": [0.18, 0.19, 0.20, 0.205],
        "minutes_since_last_irr": [120.0, 0.0, 10.0, 20.0],
        "Delta_VWC_S1_sim": [0.01, 0.012, 0.014, 0.015],
        "Tsoil_R1_sim": [22.0, 21.8, 21.7, 21.6],
        "Delta_Tsoil_S1_sim": [-0.5, -0.6, -0.7, -0.8],
        "irrigation_mm_10min": [0.0, 2.1, 0.0, 0.0],
        "irrigation_duration_min": [0.0, 10.5, 0.0, 0.0],
        "irrigation_cumulative_day_mm": [0.0, 2.1, 2.1, 2.1],
        "water_input_mm": [0.0, 2.1, 0.0, 0.0],
    })


def test_dashboard_model_frame_maps_world_model_columns():
    frame = build_dashboard_model_frame(_sample_world_model_df(), crop_zone="S1")

    assert list(frame["Time"]) == list(_sample_world_model_df()["Time"])
    assert frame["track_mean"].tolist() == [20.0, 22.0, 24.0, 26.0]
    assert frame["VWC_S1_mean"].iloc[0] == pytest.approx(0.19)
    assert frame["Tsoil_S1_mean"].iloc[0] == pytest.approx(21.5)
    assert "energy_score" in frame.columns
    assert "crop_score" in frame.columns
    assert "IEC" in frame.columns


def test_transition_dataset_aligns_next_state_within_policy():
    transitions = build_transition_dataset(_sample_world_model_df())

    assert len(transitions) == 3
    assert transitions["policy_id"].nunique() == 1
    assert transitions["next_VWC_R1_sim"].iloc[0] == pytest.approx(0.19)
    assert transitions["next_Tsoil_R1_sim"].iloc[1] == pytest.approx(21.7)
    assert set(EXO_COLUMNS).issubset(transitions.columns)
    assert set(ACTION_COLUMNS).issubset(transitions.columns)
    assert set(ENDO_COLUMNS).issubset(transitions.columns)


def test_reward_training_dataset_contains_total_reward_and_next_state():
    dataset = build_reward_training_dataset(_sample_world_model_df(), crop_type="lechuga", crop_zone="S1")

    assert len(dataset) == 3
    assert "agronomic_component" in dataset.columns
    assert "energy_component" in dataset.columns
    assert "rl_reward" in dataset.columns
    assert dataset["rl_reward"].between(0, 1).all()
    assert "next_VWC_R1_sim" in dataset.columns
