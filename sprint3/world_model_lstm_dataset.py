from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class WindowSplit:
    x_train: np.ndarray
    y_train: np.ndarray
    x_val: np.ndarray
    y_val: np.ndarray
    x_test: np.ndarray
    y_test: np.ndarray


@dataclass(frozen=True)
class ScaledWindows:
    x_scaled: np.ndarray
    y_scaled: np.ndarray
    x_scaler: StandardScaler
    y_scaler: StandardScaler


@dataclass(frozen=True)
class TimeStreamSplit:
    train: pd.DataFrame
    stream: pd.DataFrame
    metadata: dict[str, object]


def make_policy_windows(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_cols: list[str],
    window_size: int = 12,
) -> tuple[np.ndarray, np.ndarray]:
    if window_size < 1:
        raise ValueError("window_size must be >= 1")

    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    for _, group in df.groupby("policy_id", sort=False):
        group = group.reset_index(drop=True)
        if len(group) <= window_size:
            continue
        features = group[feature_cols].to_numpy(dtype="float32")
        targets = group[target_cols].to_numpy(dtype="float32")
        for end in range(window_size, len(group)):
            xs.append(features[end - window_size:end])
            ys.append(targets[end])

    if not xs:
        return (
            np.empty((0, window_size, len(feature_cols)), dtype="float32"),
            np.empty((0, len(target_cols)), dtype="float32"),
        )
    return np.stack(xs), np.stack(ys)


def split_windows_chronologically(
    x: np.ndarray,
    y: np.ndarray,
    train_frac: float = 0.70,
    val_frac: float = 0.15,
) -> WindowSplit:
    if len(x) != len(y):
        raise ValueError("x and y must have the same number of samples")
    if not 0 < train_frac < 1:
        raise ValueError("train_frac must be between 0 and 1")
    if not 0 <= val_frac < 1:
        raise ValueError("val_frac must be between 0 and 1")
    train_end = int(len(x) * train_frac)
    val_end = int(len(x) * (train_frac + val_frac))
    return WindowSplit(
        x_train=x[:train_end],
        y_train=y[:train_end],
        x_val=x[train_end:val_end],
        y_val=y[train_end:val_end],
        x_test=x[val_end:],
        y_test=y[val_end:],
    )


def fit_window_scalers(x: np.ndarray, y: np.ndarray) -> ScaledWindows:
    if x.ndim != 3:
        raise ValueError("x must have shape (samples, timesteps, features)")
    if y.ndim != 2:
        raise ValueError("y must have shape (samples, targets)")
    samples, timesteps, features = x.shape
    x_scaler = StandardScaler()
    y_scaler = StandardScaler()
    x_2d = x.reshape(samples * timesteps, features)
    x_scaled = x_scaler.fit_transform(x_2d).reshape(samples, timesteps, features).astype("float32")
    y_scaled = y_scaler.fit_transform(y).astype("float32")
    return ScaledWindows(x_scaled=x_scaled, y_scaled=y_scaled, x_scaler=x_scaler, y_scaler=y_scaler)


def transform_windows(
    x: np.ndarray,
    y: np.ndarray,
    x_scaler: StandardScaler,
    y_scaler: StandardScaler,
) -> ScaledWindows:
    if x.ndim != 3:
        raise ValueError("x must have shape (samples, timesteps, features)")
    if y.ndim != 2:
        raise ValueError("y must have shape (samples, targets)")
    samples, timesteps, features = x.shape
    x_2d = x.reshape(samples * timesteps, features)
    x_scaled = x_scaler.transform(x_2d).reshape(samples, timesteps, features).astype("float32")
    y_scaled = y_scaler.transform(y).astype("float32")
    return ScaledWindows(x_scaled=x_scaled, y_scaled=y_scaled, x_scaler=x_scaler, y_scaler=y_scaler)


def split_training_and_stream_by_time(
    df: pd.DataFrame,
    stream_frac: float = 0.20,
    time_col: str = "Time",
) -> TimeStreamSplit:
    if not 0 < stream_frac < 1:
        raise ValueError("stream_frac must be between 0 and 1")
    if time_col not in df.columns:
        raise ValueError(f"missing time column: {time_col}")

    normalized = df.copy()
    normalized[time_col] = pd.to_datetime(normalized[time_col])
    unique_times = pd.Index(normalized[time_col].dropna().sort_values().unique())
    if len(unique_times) < 2:
        raise ValueError("at least two unique timestamps are required")

    stream_count = max(1, int(np.ceil(len(unique_times) * stream_frac)))
    train_count = len(unique_times) - stream_count
    if train_count < 1:
        raise ValueError("stream_frac leaves no training timestamps")

    stream_start = pd.Timestamp(unique_times[train_count])
    train_mask = normalized[time_col] < stream_start
    train = normalized.loc[train_mask].sort_values(["policy_id", time_col]).reset_index(drop=True)
    stream = normalized.loc[~train_mask].sort_values(["policy_id", time_col]).reset_index(drop=True)

    metadata = {
        "stream_frac": float(stream_frac),
        "time_col": time_col,
        "unique_timestamps": int(len(unique_times)),
        "train_timestamps": int(train[time_col].nunique()),
        "stream_timestamps": int(stream[time_col].nunique()),
        "train_start": pd.Timestamp(train[time_col].min()).isoformat(),
        "train_end": pd.Timestamp(train[time_col].max()).isoformat(),
        "stream_start": pd.Timestamp(stream[time_col].min()).isoformat(),
        "stream_end": pd.Timestamp(stream[time_col].max()).isoformat(),
    }
    return TimeStreamSplit(train=train, stream=stream, metadata=metadata)


def weekly_retraining_cutoffs(
    stream_df: pd.DataFrame,
    frequency_days: int = 7,
    time_col: str = "Time",
) -> list[pd.Timestamp]:
    if frequency_days < 1:
        raise ValueError("frequency_days must be >= 1")
    if time_col not in stream_df.columns:
        raise ValueError(f"missing time column: {time_col}")

    times = pd.to_datetime(stream_df[time_col]).dropna()
    if times.empty:
        return []
    first = times.min().normalize()
    last = times.max()
    step = pd.Timedelta(days=int(frequency_days))
    cutoff = first + step
    cutoffs: list[pd.Timestamp] = []
    while cutoff <= last:
        cutoffs.append(pd.Timestamp(cutoff))
        cutoff += step
    return cutoffs
