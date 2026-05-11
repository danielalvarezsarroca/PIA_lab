from __future__ import annotations

from collections.abc import Callable, Iterable

import pandas as pd


Predictor = Callable[[pd.DataFrame, dict[str, float | bool]], dict[str, float | int]]


def _as_float(value: object, default: float = 0.0) -> float:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return default
    return float(numeric)


def _bounded(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(max(value, lower), upper)


def _apply_irrigation_water_balance(
    next_row: pd.Series,
    last: pd.Series,
    action: dict[str, float | bool],
    step_minutes: int,
) -> pd.Series:
    if "VWC_R1_sim" not in next_row:
        return next_row

    previous_vwc = _as_float(last.get("VWC_R1_sim"), _as_float(next_row.get("VWC_R1_sim")))
    predicted_vwc = _as_float(next_row.get("VWC_R1_sim"), previous_vwc)
    irrigation_dose = max(_as_float(action.get("irrigation_dose_mm"), 0.0), 0.0)
    irrigation_on = bool(action.get("irrigation_on", False)) and irrigation_dose > 0

    if irrigation_on:
        delta = min(0.018, 0.004 + 0.006 * irrigation_dose)
        minutes_since_last_irr = 0.0
    else:
        gpoa = _as_float(next_row.get("GPOA_mean"), _as_float(last.get("GPOA_mean"), 0.0))
        tsoil = _as_float(
            next_row.get("Tsoil_R1_sim"),
            _as_float(next_row.get("Tsoil_R1_mean"), _as_float(last.get("Tsoil_R1_sim"), 20.0)),
        )
        solar_factor = _bounded(gpoa / 900.0, 0.0, 1.2)
        heat_factor = _bounded((tsoil - 22.0) / 10.0, 0.0, 1.0)
        delta = -(0.0015 + 0.0025 * solar_factor + 0.0015 * heat_factor) * (step_minutes / 10.0)
        minutes_since_last_irr = _as_float(last.get("minutes_since_last_irr"), 0.0) + step_minutes

    next_row["VWC_R1_sim"] = _bounded(predicted_vwc + delta)
    next_row["minutes_since_last_irr"] = minutes_since_last_irr
    if "Delta_VWC_S1_sim" in next_row:
        next_row["Delta_VWC_S1_sim"] = _as_float(next_row.get("Delta_VWC_S1_sim"), 0.0) + delta
    return next_row


def rollout_with_policy(
    initial_history: pd.DataFrame,
    actions: Iterable[dict[str, float | bool]],
    predictor: Predictor,
    step_minutes: int = 10,
) -> pd.DataFrame:
    if initial_history.empty:
        raise ValueError("initial_history cannot be empty")

    history = initial_history.copy().reset_index(drop=True)
    for action in actions:
        predicted = predictor(history, action)
        last = history.iloc[-1].copy()
        next_row = last.copy()
        if "Time" in next_row:
            next_row["Time"] = pd.to_datetime(last["Time"]) + pd.Timedelta(minutes=step_minutes)
        for column, value in action.items():
            next_row[column] = value
        for column, value in predicted.items():
            next_row[column] = value
        next_row = _apply_irrigation_water_balance(next_row, last, action, step_minutes)
        history = pd.concat([history, pd.DataFrame([next_row])], ignore_index=True)
    return history
