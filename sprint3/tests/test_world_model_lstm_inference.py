import warnings

import pandas as pd

from sprint3.world_model_dataset import ACTION_COLUMNS, ENDO_COLUMNS, EXO_COLUMNS, LEARNED_ENDO_COLUMNS
from sprint3.world_model_lstm import WorldModelLSTM
from sprint3.world_model_lstm_inference import recompute_minutes_since_last_irr, predict_next_state


def _window(window_size=12):
    rows = []
    for i in range(window_size):
        row = {column: 0.1 for column in EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS}
        row["Time"] = pd.Timestamp("2026-01-01") + pd.Timedelta(minutes=10 * i)
        row["policy_id"] = "test_policy"
        row["minutes_since_last_irr"] = 60 + 10 * i
        row["irrigation_on"] = False
        row["irrigation_dose_mm"] = 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def test_recompute_minutes_since_last_irr_resets_when_irrigating():
    assert recompute_minutes_since_last_irr(previous_minutes=180, irrigation_on=True) == 0


def test_recompute_minutes_since_last_irr_advances_by_step_when_not_irrigating():
    assert recompute_minutes_since_last_irr(previous_minutes=180, irrigation_on=False, step_minutes=10) == 190


def test_predict_next_state_returns_learned_targets_and_deterministic_counter():
    model = WorldModelLSTM(input_size=22, hidden_size=8, output_size=len(LEARNED_ENDO_COLUMNS), num_layers=1)
    scalers = {
        "x_scaler": None,
        "y_scaler": None,
        "feature_cols": EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS,
        "target_cols": [f"next_{column}" for column in LEARNED_ENDO_COLUMNS],
        "window_size": 12,
    }

    result = predict_next_state(
        model=model,
        scalers=scalers,
        recent_window=_window(),
        action={"irrigation_on": True, "irrigation_dose_mm": 1.2, "tracker_angle_deg": 15.0},
        device="cpu",
    )

    assert set(LEARNED_ENDO_COLUMNS).issubset(result)
    assert result["minutes_since_last_irr"] == 0


def test_predict_next_state_accepts_boolean_action_for_integer_irrigation_column():
    window = _window()
    window["irrigation_on"] = window["irrigation_on"].astype("int64")
    model = WorldModelLSTM(input_size=22, hidden_size=8, output_size=len(LEARNED_ENDO_COLUMNS), num_layers=1)
    scalers = {
        "x_scaler": None,
        "y_scaler": None,
        "feature_cols": EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS,
        "target_cols": [f"next_{column}" for column in LEARNED_ENDO_COLUMNS],
        "window_size": 12,
    }

    with warnings.catch_warnings():
        warnings.simplefilter("error", FutureWarning)
        result = predict_next_state(
            model=model,
            scalers=scalers,
            recent_window=window,
            action={"irrigation_on": True, "irrigation_dose_mm": 1.2, "tracker_angle_deg": 15.0},
            device="cpu",
        )

    assert result["minutes_since_last_irr"] == 0
