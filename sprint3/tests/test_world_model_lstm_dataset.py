import pandas as pd
import numpy as np

from sprint3.world_model_lstm_dataset import (
    fit_window_scalers,
    make_policy_windows,
    split_windows_chronologically,
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
