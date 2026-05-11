import numpy as np
import pytest

torch = pytest.importorskip("torch")

from sprint3.world_model_lstm import WorldModelLSTM
from sprint3.world_model_lstm_training import regression_metrics


def test_world_model_lstm_forward_shape():
    model = WorldModelLSTM(input_size=22, hidden_size=16, output_size=7, num_layers=1)
    x = torch.randn(5, 12, 22)

    y = model(x)

    assert y.shape == (5, 7)


def test_regression_metrics_returns_mae_rmse_per_target():
    y_true = np.array([[1.0, 2.0], [3.0, 4.0]], dtype="float32")
    y_pred = np.array([[1.5, 1.0], [2.5, 5.0]], dtype="float32")

    metrics = regression_metrics(y_true, y_pred, target_cols=["a", "b"])

    assert metrics["a"]["mae"] == 0.5
    assert metrics["b"]["mae"] == 1.0
    assert "rmse" in metrics["a"]
