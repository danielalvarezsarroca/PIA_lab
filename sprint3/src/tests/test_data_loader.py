import pandas as pd
import pytest
from data_loader import get_latest_record, parse_tracker_name


def test_get_latest_record_returns_last_non_null_iec_row():
    df = pd.DataFrame({
        "Time": pd.to_datetime(["2025-06-01", "2025-06-02", "2025-06-03"]),
        "IEC": [0.3, 0.6, float("nan")],
        "track_mean": [20.0, 35.0, 40.0],
        "hour_of_day": [12, 12, 12],
    })
    result = get_latest_record(df)
    assert result["IEC"] == pytest.approx(0.6)
    assert result["track_mean"] == pytest.approx(35.0)


def test_get_latest_record_empty_raises():
    df = pd.DataFrame({"IEC": pd.Series([], dtype=float)})
    with pytest.raises(ValueError, match="No valid records"):
        get_latest_record(df)


def test_parse_tracker_name_extracts_id():
    assert parse_tracker_name("tracker_M04 (actual)") == "M04"
    assert parse_tracker_name("tracker_M10 (actual)") == "M10"


def test_parse_tracker_name_unknown_format_returns_raw():
    assert parse_tracker_name("something_weird") == "something_weird"


def test_load_world_model_training_dataset_reads_reward_columns(tmp_path, monkeypatch):
    path = tmp_path / "world_model_training_dataset.csv"
    path.write_text(
        "Time,policy_id,episode_id,rl_reward,energy_component,agronomic_component\n"
        "2025-01-01 00:00:00,p,e,0.7,0.8,0.6\n",
        encoding="utf-8",
    )
    import data_loader

    monkeypatch.setattr(data_loader, "WORLD_MODEL_TRAINING_PATH", path)

    df = data_loader.load_world_model_training_dataset()

    assert df["rl_reward"].iloc[0] == 0.7


def test_lstm_artifact_paths_are_defined_under_sprint3_outputs():
    import data_loader

    assert data_loader.WORLD_MODEL_LSTM_PATH.name == "world_model_lstm.pt"
    assert data_loader.WORLD_MODEL_LSTM_SCALERS_PATH.name == "world_model_lstm_scalers.joblib"
    assert "sprint3" in str(data_loader.WORLD_MODEL_LSTM_PATH)


def test_get_world_model_lstm_status_uses_metrics_and_artifact_paths(monkeypatch):
    import data_loader

    class FakePath:
        def exists(self):
            return True

    monkeypatch.setattr(data_loader, "WORLD_MODEL_LSTM_PATH", FakePath())
    monkeypatch.setattr(data_loader, "WORLD_MODEL_LSTM_SCALERS_PATH", FakePath())
    monkeypatch.setattr(
        data_loader,
        "load_world_model_lstm_metrics",
        lambda: {
            "window_size": 12,
            "target_metrics": {
                "next_VWC_R1_sim": {"mae": 0.003852},
                "next_Tsoil_R1_sim": {"mae": 0.111123},
                "next_GPOA_mean": {"mae": 12.740058},
            },
        },
    )

    status = data_loader.get_world_model_lstm_status()

    assert status["state"] == "Entrenado"
    assert status["window"] == "12 pasos x 10 min"


def test_load_world_model_recent_window_returns_sorted_tail(tmp_path, monkeypatch):
    path = tmp_path / "master_dataset_world_model.csv"
    header = (
        "Time,policy_id,episode_id,irrigation_mm_10min,irrigation_duration_min,"
        "irrigation_cumulative_day_mm,water_input_mm,hour_sin,hour_cos,day_sin,day_cos,"
        "solar_elevation_deg,solar_azimuth_deg,clearsky_ghi_wm2,air_temp_ext_avg_degc,"
        "wind_speed_kmh,precip_intensity_mm10min,PAR_R1,tracker_angle_deg,irrigation_on,"
        "irrigation_dose_mm,GPOA_mean,ALBEDO_mean,Delta_PAR_S1,VWC_R1_sim,"
        "minutes_since_last_irr,Delta_VWC_S1_sim,Tsoil_R1_sim,Delta_Tsoil_S1_sim\n"
    )
    path.write_text(
        header
        + "2026-01-01 00:00:00,p,e1,0,0,0,0,0,1,0,1,0,0,0,20,1,0,100,0,0,0,0,0,0,0.18,10,0.01,20,-1\n"
        + "2026-01-01 00:10:00,p,e2,0,0,0,0,0,1,0,1,0,0,0,20,1,0,100,0,0,0,0,0,0,0.19,20,0.01,21,-1\n",
        encoding="utf-8",
    )
    import data_loader

    monkeypatch.setattr(data_loader, "WORLD_MODEL_PATH", path)

    recent = data_loader.load_world_model_recent_window(rows=1)

    assert len(recent) == 1
    assert recent.iloc[0]["episode_id"] == "e2"
