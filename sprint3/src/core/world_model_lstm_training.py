from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray, target_cols: list[str]) -> dict[str, dict[str, float]]:
    metrics: dict[str, dict[str, float]] = {}
    for idx, name in enumerate(target_cols):
        error = y_pred[:, idx] - y_true[:, idx]
        metrics[name] = {
            "mae": round(float(np.mean(np.abs(error))), 6),
            "rmse": round(float(np.sqrt(np.mean(error ** 2))), 6),
        }
    return metrics


def _loader(x: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool) -> DataLoader:
    dataset = TensorDataset(torch.from_numpy(x).float(), torch.from_numpy(y).float())
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def train_model(
    model: nn.Module,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    epochs: int = 30,
    batch_size: int = 256,
    lr: float = 1e-3,
    device: str | None = None,
) -> dict[str, list[float]]:
    actual_device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    model.to(actual_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    history = {"train_loss": [], "val_loss": []}
    train_loader = _loader(x_train, y_train, batch_size=batch_size, shuffle=True)
    val_loader = _loader(x_val, y_val, batch_size=batch_size, shuffle=False)

    for _ in range(epochs):
        model.train()
        train_losses = []
        for xb, yb in train_loader:
            xb = xb.to(actual_device)
            yb = yb.to(actual_device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_fn(model(xb), yb)
            loss.backward()
            optimizer.step()
            train_losses.append(float(loss.detach().cpu()))

        model.eval()
        val_losses = []
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(actual_device)
                yb = yb.to(actual_device)
                val_losses.append(float(loss_fn(model(xb), yb).detach().cpu()))

        history["train_loss"].append(round(float(np.mean(train_losses)), 6))
        history["val_loss"].append(round(float(np.mean(val_losses)), 6))

    return history


def predict(model: nn.Module, x: np.ndarray, batch_size: int = 512, device: str | None = None) -> np.ndarray:
    actual_device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    model.to(actual_device)
    model.eval()
    outputs = []
    loader = DataLoader(torch.from_numpy(x).float(), batch_size=batch_size, shuffle=False)
    with torch.no_grad():
        for xb in loader:
            outputs.append(model(xb.to(actual_device)).detach().cpu().numpy())
    return np.concatenate(outputs, axis=0)


def save_artifacts(
    output_dir: Path,
    model: nn.Module,
    scalers: Any,
    metrics: dict,
    predictions_sample,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_dir / "world_model_lstm.pt")
    joblib.dump(scalers, output_dir / "world_model_lstm_scalers.joblib")
    (output_dir / "world_model_lstm_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    predictions_sample.to_csv(output_dir / "world_model_lstm_predictions_sample.csv", index=False)
