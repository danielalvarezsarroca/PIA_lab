from __future__ import annotations

from collections.abc import Callable, Iterable

import pandas as pd


Predictor = Callable[[pd.DataFrame, dict[str, float | bool]], dict[str, float | int]]


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
        history = pd.concat([history, pd.DataFrame([next_row])], ignore_index=True)
    return history
