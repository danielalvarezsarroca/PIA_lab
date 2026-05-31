import pandas as pd

from tabs.tab_lstm_simulation import (
    artifacts_available,
    build_metric_comparison_frame,
    build_prediction_frame_if_available,
    build_retraining_timeline_frame,
    build_stream_chart_frame,
    build_stream_empty_state,
    build_week_windows,
    build_world_model_training_command,
    lstm_retraining_command,
    try_predict_dashboard_next_state,
    resolve_stream_slider_bounds,
    select_week_stream_state,
    select_stream_cursor_state,
)


def _stream(rows: int = 14, policy_id: str = "p1") -> pd.DataFrame:
    return pd.DataFrame({
        "Time": pd.date_range("2026-01-01 00:00:00", periods=rows, freq="10min"),
        "policy_id": [policy_id] * rows,
        "VWC_R1_sim": [0.18 + i * 0.001 for i in range(rows)],
        "Tsoil_R1_sim": [20.0 + i * 0.1 for i in range(rows)],
        "PAR_R1": [500.0] * rows,
        "GPOA_mean": [700.0] * rows,
    })


def test_valid_stream_cursor_selects_policy_local_window_with_enough_rows():
    stream = pd.concat([_stream(4, "other"), _stream(14, "p1")], ignore_index=True)

    state = select_stream_cursor_state(stream, policy_id="p1", cursor=13, window_size=12)

    assert state["ready"] is True
    assert len(state["recent_window"]) == 12
    assert state["current_row"]["policy_id"] == "p1"
    assert state["observed_rows"] == 14


def test_week_windows_split_policy_stream_into_seven_day_blocks():
    stream = _stream(10 * 24 * 6, "p1")

    weeks = build_week_windows(stream)

    assert list(weeks["week_index"]) == [1, 2]
    assert weeks.loc[0, "start_cursor"] == 0
    assert weeks.loc[0, "end_cursor"] == (7 * 24 * 6) - 1
    assert weeks.loc[1, "row_count"] == 3 * 24 * 6


def test_select_week_stream_state_clamps_cursor_inside_week():
    stream = _stream(10 * 24 * 6, "p1")
    weeks = build_week_windows(stream)

    state = select_week_stream_state(stream, weeks, week_index=2, cursor=9999, window_size=12)

    assert state["week_index"] == 2
    assert state["cursor"] == len(stream) - 1
    assert state["ready"] is True


def test_build_stream_chart_frame_limits_to_current_week_progress():
    stream = _stream(30, "p1")
    weeks = build_week_windows(stream)
    state = select_week_stream_state(stream, weeks, week_index=1, cursor=20, window_size=12)

    chart = build_stream_chart_frame(state)

    assert set(chart["variable"]) == {"VWC", "Tsoil", "GPOA"}
    assert chart["Time"].max() == stream.loc[20, "Time"]


def test_stream_cursor_reports_insufficient_context_safely():
    state = select_stream_cursor_state(_stream(6), policy_id="p1", cursor=5, window_size=12)

    assert state["ready"] is False
    assert state["recent_window"].empty
    assert "pasos anteriores" in state["message"].lower()


def test_empty_stream_has_no_slider_bounds():
    bounds = resolve_stream_slider_bounds(pd.DataFrame(), "default")

    assert bounds["can_render_slider"] is False
    assert bounds["max_cursor"] == 0


def test_empty_stream_state_explains_prerequisite_commands():
    state = build_stream_empty_state(training_dataset_exists=False)

    assert state["can_render_controls"] is False
    assert "datos suficientes" in state["body"]
    assert "simulación semanal" in state["body"]
    assert "build_world_model_training_dataset.py" in state["training_command"]
    assert "train_world_model_lstm.py --mode simulate-retraining" in state["command"]


def test_build_world_model_training_command_uses_world_model_dataset():
    command = build_world_model_training_command()

    assert "build_world_model_training_dataset.py" in command
    assert "master_dataset_world_model.csv" in command
    assert "master_dataset.csv" not in command


def test_lstm_retraining_command_matches_actual_cli():
    command = lstm_retraining_command()

    assert "--mode simulate-retraining" in command
    assert "--simulate-weekly-retraining" not in command


def test_retraining_timeline_handles_present_runs():
    metrics = {
        "weekly_retraining_runs": [
            {
                "cutoff_time": "2026-01-08 00:00:00",
                "observed_rows": 120,
                "target_metrics": {
                    "next_VWC_R1_sim": {"mae": 0.01},
                    "next_Tsoil_R1_sim": {"mae": 0.12},
                    "next_GPOA_mean": {"mae": 15.5},
                },
            }
        ]
    }

    timeline = build_retraining_timeline_frame(metrics)

    assert list(timeline.columns) == ["cutoff_time", "observed_rows", "Error humedad", "Error suelo", "Error luz"]
    assert timeline.loc[0, "Error humedad"] == 0.01


def test_retraining_timeline_handles_generated_metrics_keys():
    metrics = {
        "weekly_retraining_runs": [
            {
                "cutoff": "2026-01-08 00:00:00",
                "observed_stream_rows": 120,
                "target_metrics": {"next_VWC_R1_sim": {"mae": 0.01}},
            }
        ]
    }

    timeline = build_retraining_timeline_frame(metrics)

    assert timeline.loc[0, "cutoff_time"] == pd.Timestamp("2026-01-08 00:00:00")
    assert timeline.loc[0, "observed_rows"] == 120


def test_retraining_timeline_absent_returns_empty_frame():
    assert build_retraining_timeline_frame({}).empty


def test_prediction_comparison_frame_requires_artifacts():
    current = _stream(1).iloc[0]
    predicted = {"VWC_R1_sim": 0.2, "Tsoil_R1_sim": 20.5, "Delta_PAR_S1": -50, "GPOA_mean": 650}

    assert build_prediction_frame_if_available(current, predicted, False).empty
    assert not build_prediction_frame_if_available(current, predicted, True).empty


def test_lstm_prediction_missing_optional_dependency_does_not_crash(monkeypatch):
    def _missing_joblib(**_kwargs):
        exc = ModuleNotFoundError("No module named 'joblib'")
        exc.name = "joblib"
        raise exc

    monkeypatch.setattr("tabs.tab_lstm_simulation.predict_dashboard_next_state", _missing_joblib)

    result = try_predict_dashboard_next_state(
        recent_window=_stream(12),
        tracker_angle_deg=0.0,
        irrigation_on=False,
        irrigation_dose_mm=0.0,
        model_path="missing.pt",
        scalers_path="missing.joblib",
    )

    assert result["prediction"] is None
    assert "joblib" in result["message"]
    assert "Simulación" in result["message"]


def test_artifacts_available_requires_model_scalers_and_metrics():
    assert artifacts_available({"model": True, "scalers": True, "metrics": True}) is True
    assert artifacts_available({"model": True, "scalers": False, "metrics": True}) is False


def test_metric_comparison_frame_uses_initial_and_stream_metrics():
    metrics = {
        "target_metrics": {"next_VWC_R1_sim": {"mae": 0.01}},
        "stream_holdout_metrics": {"target_metrics": {"next_VWC_R1_sim": {"mae": 0.02}}},
    }

    frame = build_metric_comparison_frame(metrics)

    assert list(frame["serie"]) == ["Prueba inicial", "Datos de prueba"]
    assert list(frame["Error humedad"]) == [0.01, 0.02]


def test_metric_comparison_frame_uses_generated_stream_target_metrics():
    metrics = {
        "target_metrics": {"next_VWC_R1_sim": {"mae": 0.01}},
        "stream_target_metrics": {"next_VWC_R1_sim": {"mae": 0.02}},
    }

    frame = build_metric_comparison_frame(metrics)

    assert list(frame["serie"]) == ["Prueba inicial", "Datos de prueba"]
    assert list(frame["Error humedad"]) == [0.01, 0.02]
