from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import torch

try:
    from .world_model_lstm import WorldModelLSTM
except ImportError:  # pragma: no cover - supports direct script-style imports from sprint3/
    from world_model_lstm import WorldModelLSTM


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"
DEFAULT_MODEL_PATH = DEFAULT_OUTPUT_DIR / "world_model_lstm.pt"
DEFAULT_SCALERS_PATH = DEFAULT_OUTPUT_DIR / "world_model_lstm_scalers.joblib"
NON_NEGATIVE_OUTPUTS = {"GPOA_mean", "ALBEDO_mean"}
FRACTION_OUTPUTS = {"VWC_R1_sim"}


def recompute_minutes_since_last_irr(
    previous_minutes: float,
    irrigation_on: bool,
    step_minutes: int = 10,
) -> int:
    if irrigation_on:
        return 0
    previous = 0 if pd.isna(previous_minutes) else int(previous_minutes)
    return previous + int(step_minutes)


def load_lstm_world_model(
    model_path: str | Path = DEFAULT_MODEL_PATH,
    scalers_path: str | Path = DEFAULT_SCALERS_PATH,
    hidden_size: int | None = None,
    num_layers: int | None = None,
    device: str | None = None,
) -> tuple[WorldModelLSTM, dict[str, Any]]:
    scalers = joblib.load(scalers_path)
    input_size = len(scalers["feature_cols"])
    output_size = len(scalers["target_cols"])
    model = WorldModelLSTM(
        input_size=input_size,
        hidden_size=int(hidden_size or scalers.get("hidden_size", 64)),
        output_size=output_size,
        num_layers=int(num_layers or scalers.get("num_layers", 2)),
    )
    actual_device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    state = torch.load(model_path, map_location=actual_device)
    model.load_state_dict(state)
    model.to(actual_device)
    model.eval()
    return model, scalers


def _transform_x(x: np.ndarray, scaler: Any | None) -> np.ndarray:
    if scaler is None:
        return x.astype("float32")
    samples, timesteps, features = x.shape
    x_2d = x.reshape(samples * timesteps, features)
    return scaler.transform(x_2d).reshape(samples, timesteps, features).astype("float32")


def _inverse_y(y: np.ndarray, scaler: Any | None) -> np.ndarray:
    if scaler is None:
        return y.astype("float32")
    return scaler.inverse_transform(y).astype("float32")


def _clip_output(name: str, value: float) -> float:
    if name in NON_NEGATIVE_OUTPUTS:
        return max(0.0, value)
    if name in FRACTION_OUTPUTS:
        return min(1.0, max(0.0, value))
    return value


def _coerce_action_value(series: pd.Series, value: float | bool) -> float | bool:
    if isinstance(value, bool) and pd.api.types.is_bool_dtype(series.dtype):
        return value
    if isinstance(value, bool) and pd.api.types.is_numeric_dtype(series.dtype):
        return int(value)
    return value


def predict_next_state(
    model: WorldModelLSTM,
    scalers: dict[str, Any],
    recent_window: pd.DataFrame,
    action: dict[str, float | bool],
    step_minutes: int = 10,
    device: str | None = None,
) -> dict[str, float | int]:
    feature_cols = list(scalers["feature_cols"])
    target_cols = list(scalers["target_cols"])
    window_size = int(scalers.get("window_size", len(recent_window)))
    if len(recent_window) < window_size:
        raise ValueError(f"recent_window must have at least {window_size} rows")
    missing = [column for column in feature_cols if column not in recent_window.columns]
    if missing:
        raise ValueError(f"recent_window missing feature columns: {missing}")

    window = recent_window.tail(window_size).copy()
    for column, value in action.items():
        if column in window.columns:
            window.loc[window.index[-1], column] = _coerce_action_value(window[column], value)

    x_raw = window[feature_cols].to_numpy(dtype="float32")[None, :, :]
    x_scaled = _transform_x(x_raw, scalers.get("x_scaler"))
    actual_device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    with torch.no_grad():
        y_scaled = model(torch.from_numpy(x_scaled).float().to(actual_device)).detach().cpu().numpy()
    y = _inverse_y(y_scaled, scalers.get("y_scaler"))[0]

    result: dict[str, float | int] = {}
    for target, value in zip(target_cols, y, strict=False):
        name = target.removeprefix("next_")
        result[name] = _clip_output(name, float(value))

    previous_minutes = float(window.iloc[-1]["minutes_since_last_irr"])
    irrigation_on = bool(action.get("irrigation_on", window.iloc[-1].get("irrigation_on", False)))
    result["minutes_since_last_irr"] = recompute_minutes_since_last_irr(previous_minutes, irrigation_on, step_minutes)
    return result
