import pandas as pd
import numpy as np
import pytest

pytest.importorskip("sklearn")

from sprint3.world_model_lstm_dataset import (
    fit_window_scalers,
    make_policy_windows,
    split_training_and_stream_by_time,
    split_windows_chronologically,
    transform_windows,
    weekly_retraining_cutoffs,
)


def test_make_policy_windows_does_not_cross_policy_boundaries():
    df = pd.DataFrame({
        "policy_id": ["a", "a", "a", "b", "b", "b"],
        "x": [1, 2, 3, 10, 11, 12],
        "target": [2, 3, 4, 11, 12, 13],
    })

    x, y = make_policy_windows(df, feature_cols=["x"], target_cols=["target"], window_size=2)

    assert x.shape == (2, 2, 1)
    assert y.shape == (2, 1)
    assert x[0, :, 0].tolist() == [1, 2]
    assert x[1, :, 0].tolist() == [10, 11]


def test_split_windows_chronologically_preserves_order():
    x = np.arange(10 * 2 * 1, dtype="float32").reshape(10, 2, 1)
    y = np.arange(10, dtype="float32").reshape(10, 1)

    split = split_windows_chronologically(x, y, train_frac=0.6, val_frac=0.2)

    assert split.x_train.shape[0] == 6
    assert split.x_val.shape[0] == 2
    assert split.x_test.shape[0] == 2
    assert split.y_train[-1, 0] == 5
    assert split.y_val[0, 0] == 6
    assert split.y_test[0, 0] == 8


def test_fit_window_scalers_round_trips_shapes():
    x = np.arange(6 * 2 * 2, dtype="float32").reshape(6, 2, 2)
    y = np.arange(6 * 3, dtype="float32").reshape(6, 3)

    scaled = fit_window_scalers(x, y)

    assert scaled.x_scaled.shape == x.shape
    assert scaled.y_scaled.shape == y.shape
    assert scaled.x_scaler is not None
    assert scaled.y_scaler is not None


def test_split_training_and_stream_by_time_uses_same_cutoff_for_all_policies():
    times = pd.date_range("2026-01-01", periods=10, freq="10min")
    df = pd.concat(
        [
            pd.DataFrame({"Time": times, "policy_id": "a", "value": range(10)}),
            pd.DataFrame({"Time": times, "policy_id": "b", "value": range(10, 20)}),
        ],
        ignore_index=True,
    )

    split = split_training_and_stream_by_time(df, stream_frac=0.2)

    assert split.train["Time"].max() < split.stream["Time"].min()
    assert split.stream["Time"].nunique() == 2
    assert set(split.stream["policy_id"]) == {"a", "b"}
    assert split.metadata["train_end"] == times[7].isoformat()
    assert split.metadata["stream_start"] == times[8].isoformat()


def test_transform_windows_uses_existing_scalers_without_refitting():
    x_train = np.array([[[1.0], [3.0]], [[5.0], [7.0]]], dtype="float32")
    y_train = np.array([[10.0], [20.0]], dtype="float32")
    fitted = fit_window_scalers(x_train, y_train)
    original_x_mean = fitted.x_scaler.mean_.copy()
    original_y_mean = fitted.y_scaler.mean_.copy()

    x_stream = np.array([[[100.0], [120.0]]], dtype="float32")
    y_stream = np.array([[300.0]], dtype="float32")
    transformed = transform_windows(x_stream, y_stream, fitted.x_scaler, fitted.y_scaler)

    assert transformed.x_scaled.shape == x_stream.shape
    assert transformed.y_scaled.shape == y_stream.shape
    assert np.array_equal(fitted.x_scaler.mean_, original_x_mean)
    assert np.array_equal(fitted.y_scaler.mean_, original_y_mean)


def test_weekly_retraining_cutoffs_are_based_on_stream_timestamps():
    stream = pd.DataFrame({
        "Time": pd.date_range("2026-01-01", periods=15, freq="D"),
        "policy_id": "a",
    })

    cutoffs = weekly_retraining_cutoffs(stream, frequency_days=7)

    assert cutoffs == [
        pd.Timestamp("2026-01-08"),
        pd.Timestamp("2026-01-15"),
    ]
