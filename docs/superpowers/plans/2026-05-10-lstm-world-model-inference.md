# LSTM World Model Inference Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the trained LSTM from an offline experiment into a reusable world-model inference layer for RL simulation and dashboard consumption.

**Architecture:** Keep the LSTM as a supervised next-state predictor for continuous physical variables, while deterministic counter variables such as `minutes_since_last_irr` are recalculated by rules. Add a small inference API that loads the saved model/scalers, validates feature windows, predicts the next state, and exposes simulation helpers that the RL/dashboard code can call without knowing PyTorch details.

**Tech Stack:** Python, pandas, numpy, scikit-learn `StandardScaler`, PyTorch, joblib, pytest, Streamlit cache wrappers already present in `sprint3/data_loader.py`.

---

## File Structure

- Modify `sprint3/world_model_dataset.py`
  - Split learned targets from deterministic state variables.
  - Keep `minutes_since_last_irr` as an input feature/context column but stop training the LSTM to predict it directly.

- Modify `sprint3/train_world_model_lstm.py`
  - Train only on continuous next-state targets.
  - Save metadata with `feature_cols`, `target_cols`, `window_size`, `hidden_size`, `num_layers`, and the deterministic columns excluded from targets.

- Modify `sprint3/world_model_lstm_training.py`
  - Save richer artifact metadata into the scaler/joblib payload.
  - Keep current metrics and prediction sample output.

- Create `sprint3/world_model_lstm_inference.py`
  - Load model/scalers/artifact metadata.
  - Build one input window from the last `window_size` rows.
  - Predict next continuous state.
  - Recompute `minutes_since_last_irr` from previous value and irrigation action.
  - Return a plain `dict`/`Series` suitable for RL rollout code.

- Create `sprint3/world_model_rollout.py`
  - Simulate multi-step trajectories by repeatedly applying actions and calling `predict_next_state`.
  - Keep a simple interface for future RL policy evaluation.

- Modify `sprint3/data_loader.py`
  - Add cached loader for LSTM artifacts.
  - Add a cached prediction/sample helper for dashboard tabs.

- Add tests:
  - `sprint3/tests/test_world_model_lstm_targets.py`
  - `sprint3/tests/test_world_model_lstm_inference.py`
  - `sprint3/tests/test_world_model_rollout.py`
  - Update existing LSTM tests where target count changes from 8 to 7.

---

### Task 0: Review Current CSV Outputs Before Changing Training

**Files:**
- Read: `sprint3/outputs/world_model_training_dataset.csv`
- Read: `sprint3/outputs/master_dataset_world_model.csv`
- Read: `sprint3/outputs/world_model_lstm_predictions_sample.csv`
- Read: `sprint3/outputs/world_model_lstm_metrics.json`

- [ ] **Step 1: Inspect file sizes, row counts, and model metrics**

Run:

```powershell
@'
import json
from pathlib import Path
import pandas as pd

base = Path("sprint3/outputs")
files = {
    "training": base / "world_model_training_dataset.csv",
    "pred_sample": base / "world_model_lstm_predictions_sample.csv",
    "metrics": base / "world_model_lstm_metrics.json",
    "world": base / "master_dataset_world_model.csv",
}

for name, path in files.items():
    print(name, path.exists(), round(path.stat().st_size / 1024 / 1024, 2))

metrics = json.loads(files["metrics"].read_text(encoding="utf-8"))
for target, values in metrics["target_metrics"].items():
    print(target, values)
'@ | & 'C:\Users\dania\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -
```

Expected:

```text
world_model_training_dataset.csv exists and is roughly 118 MB
master_dataset_world_model.csv exists and is roughly 99 MB
world_model_lstm_predictions_sample.csv exists
world_model_lstm_metrics.json exists
```

- [ ] **Step 2: Compare actual vs predicted ranges**

Run:

```powershell
@'
from pathlib import Path
import pandas as pd

pred = pd.read_csv(Path("sprint3/outputs/world_model_lstm_predictions_sample.csv"))
rows = []
for col in pred.columns:
    if not col.startswith("actual_"):
        continue
    target = col.removeprefix("actual_")
    pcol = "pred_" + target
    actual = pd.to_numeric(pred[col], errors="coerce")
    predicted = pd.to_numeric(pred[pcol], errors="coerce")
    err = predicted - actual
    rows.append({
        "target": target,
        "actual_min": actual.min(),
        "actual_max": actual.max(),
        "pred_min": predicted.min(),
        "pred_max": predicted.max(),
        "mae_sample": err.abs().mean(),
        "bias_sample": err.mean(),
        "nan_pred": int(predicted.isna().sum()),
    })
print(pd.DataFrame(rows).round(5).to_string(index=False))
'@ | & 'C:\Users\dania\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -
```

Expected findings to document before implementation:

```text
Continuous soil targets should have small MAE.
minutes_since_last_irr should show high MAE and should be removed from learned targets.
Some radiation predictions may be slightly negative near night; inference should clip physically bounded outputs.
No NaN predictions should appear.
```

- [ ] **Step 3: Check physical ranges in the generated world model**

Run:

```powershell
@'
import pandas as pd

cols = [
    "policy_id",
    "episode_id",
    "irrigation_on",
    "irrigation_dose_mm",
    "VWC_R1_sim",
    "Delta_VWC_S1_sim",
    "Tsoil_R1_sim",
    "Delta_Tsoil_S1_sim",
    "minutes_since_last_irr",
]
df = pd.read_csv("sprint3/outputs/master_dataset_world_model.csv", usecols=cols)
print("rows", len(df))
print("policies", df["policy_id"].nunique())
print("episode_unique", df["episode_id"].nunique())
print("episode_duplicates", df["episode_id"].duplicated().sum())
print(df.drop(columns=["policy_id", "episode_id"]).describe(include="all").round(5).to_string())
print("irrigation_on_rate", float(pd.to_numeric(df["irrigation_on"], errors="coerce").mean()))
'@ | & 'C:\Users\dania\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -
```

Expected:

```text
414756 rows
12 policies
414756 unique episode_id values
0 duplicated episode_id values
VWC_R1_sim roughly within 0.12-0.42
Tsoil_R1_sim roughly within 2.5-36.5
irrigation_on_rate around 0.026
```

---

### Task 1: Separate Learned Targets From Deterministic Counters

**Files:**
- Modify: `sprint3/world_model_dataset.py`
- Modify: `sprint3/train_world_model_lstm.py`
- Test: `sprint3/tests/test_world_model_lstm_targets.py`

- [ ] **Step 1: Add a failing target-definition test**

Create `sprint3/tests/test_world_model_lstm_targets.py`:

```python
from sprint3.world_model_dataset import DETERMINISTIC_STATE_COLUMNS, LEARNED_ENDO_COLUMNS


def test_lstm_does_not_learn_minutes_since_last_irrigation():
    assert "minutes_since_last_irr" in DETERMINISTIC_STATE_COLUMNS
    assert "minutes_since_last_irr" not in LEARNED_ENDO_COLUMNS


def test_lstm_still_learns_continuous_soil_and_radiation_targets():
    assert "VWC_R1_sim" in LEARNED_ENDO_COLUMNS
    assert "Delta_VWC_S1_sim" in LEARNED_ENDO_COLUMNS
    assert "Tsoil_R1_sim" in LEARNED_ENDO_COLUMNS
    assert "Delta_Tsoil_S1_sim" in LEARNED_ENDO_COLUMNS
    assert "GPOA_mean" in LEARNED_ENDO_COLUMNS
    assert "Delta_PAR_S1" in LEARNED_ENDO_COLUMNS
```

- [ ] **Step 2: Run the target test and verify it fails**

Run:

```powershell
python -m pytest sprint3\tests\test_world_model_lstm_targets.py -q
```

Expected: FAIL because `LEARNED_ENDO_COLUMNS` and `DETERMINISTIC_STATE_COLUMNS` do not exist yet.

- [ ] **Step 3: Add explicit learned/deterministic target lists**

In `sprint3/world_model_dataset.py`, keep `ENDO_COLUMNS` unchanged for backward compatibility and add:

```python
DETERMINISTIC_STATE_COLUMNS = [
    "minutes_since_last_irr",
]

LEARNED_ENDO_COLUMNS = [
    column for column in ENDO_COLUMNS if column not in DETERMINISTIC_STATE_COLUMNS
]
```

- [ ] **Step 4: Change training targets to learned-only targets**

In `sprint3/train_world_model_lstm.py`, change:

```python
from world_model_dataset import ACTION_COLUMNS, ENDO_COLUMNS, EXO_COLUMNS
```

to:

```python
from world_model_dataset import ACTION_COLUMNS, DETERMINISTIC_STATE_COLUMNS, ENDO_COLUMNS, EXO_COLUMNS, LEARNED_ENDO_COLUMNS
```

and change:

```python
target_cols = [f"next_{column}" for column in ENDO_COLUMNS]
```

to:

```python
target_cols = [f"next_{column}" for column in LEARNED_ENDO_COLUMNS]
```

Add deterministic metadata to the scaler payload:

```python
"deterministic_state_cols": DETERMINISTIC_STATE_COLUMNS,
"learned_endo_cols": LEARNED_ENDO_COLUMNS,
```

- [ ] **Step 5: Run the target test and existing LSTM dataset tests**

Run:

```powershell
python -m pytest sprint3\tests\test_world_model_lstm_targets.py sprint3\tests\test_world_model_lstm_dataset.py -q
```

Expected: PASS.

---

### Task 2: Retrain LSTM With 7 Learned Targets

**Files:**
- Modify: `sprint3/tests/test_world_model_lstm_training.py`
- Generated: `sprint3/outputs/world_model_lstm.pt`
- Generated: `sprint3/outputs/world_model_lstm_scalers.joblib`
- Generated: `sprint3/outputs/world_model_lstm_metrics.json`
- Generated: `sprint3/outputs/world_model_lstm_predictions_sample.csv`

- [ ] **Step 1: Update forward-shape test to 7 outputs**

In `sprint3/tests/test_world_model_lstm_training.py`, change:

```python
model = WorldModelLSTM(input_size=22, hidden_size=16, output_size=8, num_layers=1)
```

to:

```python
model = WorldModelLSTM(input_size=22, hidden_size=16, output_size=7, num_layers=1)
```

and change:

```python
assert y.shape == (5, 8)
```

to:

```python
assert y.shape == (5, 7)
```

- [ ] **Step 2: Run the focused LSTM tests**

Run:

```powershell
python -m pytest sprint3\tests\test_world_model_lstm_training.py sprint3\tests\test_world_model_lstm_targets.py -q
```

Expected: PASS.

- [ ] **Step 3: Run a 1-epoch smoke training**

Run:

```powershell
& 'C:\Users\dania\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' sprint3\train_world_model_lstm.py --epochs 1 --batch-size 512
```

Expected output includes:

```text
X shape: (76620, 12, 22)
y shape: (76620, 7)
metrics: ...\sprint3\outputs\world_model_lstm_metrics.json
model: ...\sprint3\outputs\world_model_lstm.pt
```

- [ ] **Step 4: Run the final 30-epoch training**

Run:

```powershell
& 'C:\Users\dania\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' sprint3\train_world_model_lstm.py --epochs 30 --batch-size 512
```

Expected: training completes and `world_model_lstm_metrics.json` no longer contains `next_minutes_since_last_irr` under `target_metrics`.

- [ ] **Step 5: Inspect metrics**

Run:

```powershell
Get-Content -Path sprint3\outputs\world_model_lstm_metrics.json
```

Expected: the best metrics remain for continuous targets; no direct metric for `minutes_since_last_irr`.

---

### Task 3: Add Single-Step Inference API

**Files:**
- Create: `sprint3/world_model_lstm_inference.py`
- Test: `sprint3/tests/test_world_model_lstm_inference.py`

- [ ] **Step 1: Add failing inference tests**

Create `sprint3/tests/test_world_model_lstm_inference.py`:

```python
import numpy as np
import pandas as pd
import pytest
import torch

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
```

- [ ] **Step 2: Run inference test and verify it fails**

Run:

```powershell
python -m pytest sprint3\tests\test_world_model_lstm_inference.py -q
```

Expected: FAIL because `world_model_lstm_inference.py` does not exist.

- [ ] **Step 3: Implement inference helpers**

Create `sprint3/world_model_lstm_inference.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import torch

from world_model_lstm import WorldModelLSTM


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
DEFAULT_MODEL_PATH = DEFAULT_OUTPUT_DIR / "world_model_lstm.pt"
DEFAULT_SCALERS_PATH = DEFAULT_OUTPUT_DIR / "world_model_lstm_scalers.joblib"


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
    hidden_size: int = 64,
    num_layers: int = 2,
    device: str | None = None,
) -> tuple[WorldModelLSTM, dict[str, Any]]:
    scalers = joblib.load(scalers_path)
    input_size = len(scalers["feature_cols"])
    output_size = len(scalers["target_cols"])
    model = WorldModelLSTM(input_size=input_size, hidden_size=hidden_size, output_size=output_size, num_layers=num_layers)
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
    return scaler.transform(x.reshape(samples * timesteps, features)).reshape(samples, timesteps, features).astype("float32")


def _inverse_y(y: np.ndarray, scaler: Any | None) -> np.ndarray:
    if scaler is None:
        return y.astype("float32")
    return scaler.inverse_transform(y).astype("float32")


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
            window.loc[window.index[-1], column] = value

    x_raw = window[feature_cols].to_numpy(dtype="float32")[None, :, :]
    x_scaled = _transform_x(x_raw, scalers.get("x_scaler"))
    actual_device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    with torch.no_grad():
        y_scaled = model(torch.from_numpy(x_scaled).float().to(actual_device)).detach().cpu().numpy()
    y = _inverse_y(y_scaled, scalers.get("y_scaler"))[0]

    result: dict[str, float | int] = {}
    for target, value in zip(target_cols, y, strict=False):
        name = target.removeprefix("next_")
        result[name] = float(value)

    previous_minutes = float(window.iloc[-1]["minutes_since_last_irr"])
    irrigation_on = bool(action.get("irrigation_on", window.iloc[-1].get("irrigation_on", False)))
    result["minutes_since_last_irr"] = recompute_minutes_since_last_irr(previous_minutes, irrigation_on, step_minutes)
    return result
```

- [ ] **Step 4: Run inference tests**

Run:

```powershell
python -m pytest sprint3\tests\test_world_model_lstm_inference.py -q
```

Expected: PASS.

---

### Task 4: Add Multi-Step Rollout Helper for RL Simulation

**Files:**
- Create: `sprint3/world_model_rollout.py`
- Test: `sprint3/tests/test_world_model_rollout.py`

- [ ] **Step 1: Add failing rollout test**

Create `sprint3/tests/test_world_model_rollout.py`:

```python
import pandas as pd

from sprint3.world_model_dataset import ACTION_COLUMNS, ENDO_COLUMNS, EXO_COLUMNS
from sprint3.world_model_rollout import rollout_with_policy


def _history(rows=12):
    data = []
    for i in range(rows):
        row = {column: 0.1 for column in EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS}
        row["Time"] = pd.Timestamp("2026-01-01") + pd.Timedelta(minutes=10 * i)
        row["policy_id"] = "test_policy"
        row["minutes_since_last_irr"] = 30 + 10 * i
        row["irrigation_on"] = False
        row["irrigation_dose_mm"] = 0.0
        data.append(row)
    return pd.DataFrame(data)


def test_rollout_with_policy_appends_one_row_per_action():
    def fake_predictor(recent_window, action):
        return {
            "GPOA_mean": 0.2,
            "ALBEDO_mean": 0.2,
            "Delta_PAR_S1": 0.2,
            "VWC_R1_sim": 0.3,
            "minutes_since_last_irr": 0 if action["irrigation_on"] else 120,
            "Delta_VWC_S1_sim": 0.01,
            "Tsoil_R1_sim": 19.0,
            "Delta_Tsoil_S1_sim": -0.2,
        }

    actions = [
        {"tracker_angle_deg": 10.0, "irrigation_on": True, "irrigation_dose_mm": 1.0},
        {"tracker_angle_deg": 15.0, "irrigation_on": False, "irrigation_dose_mm": 0.0},
    ]

    result = rollout_with_policy(_history(), actions, predictor=fake_predictor)

    assert len(result) == 14
    assert result.iloc[-2]["irrigation_on"] is True
    assert result.iloc[-1]["tracker_angle_deg"] == 15.0
```

- [ ] **Step 2: Run rollout test and verify it fails**

Run:

```powershell
python -m pytest sprint3\tests\test_world_model_rollout.py -q
```

Expected: FAIL because `world_model_rollout.py` does not exist.

- [ ] **Step 3: Implement rollout helper**

Create `sprint3/world_model_rollout.py`:

```python
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
```

- [ ] **Step 4: Run rollout tests**

Run:

```powershell
python -m pytest sprint3\tests\test_world_model_rollout.py -q
```

Expected: PASS.

---

### Task 5: Expose LSTM World Model to Dashboard/Data Loader

**Files:**
- Modify: `sprint3/data_loader.py`
- Test: `sprint3/tests/test_data_loader.py`

- [ ] **Step 1: Add data-loader tests for artifact availability**

Append to `sprint3/tests/test_data_loader.py`:

```python
from sprint3 import data_loader


def test_lstm_artifact_paths_are_defined_under_sprint3_outputs():
    assert data_loader.WORLD_MODEL_LSTM_PATH.name == "world_model_lstm.pt"
    assert data_loader.WORLD_MODEL_LSTM_SCALERS_PATH.name == "world_model_lstm_scalers.joblib"
    assert "sprint3" in str(data_loader.WORLD_MODEL_LSTM_PATH)
```

- [ ] **Step 2: Run data-loader test and verify it fails**

Run:

```powershell
python -m pytest sprint3\tests\test_data_loader.py::test_lstm_artifact_paths_are_defined_under_sprint3_outputs -q
```

Expected: FAIL because these constants do not exist.

- [ ] **Step 3: Add artifact paths and a safe cached status loader**

In `sprint3/data_loader.py`, add:

```python
WORLD_MODEL_LSTM_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm.pt"
WORLD_MODEL_LSTM_SCALERS_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm_scalers.joblib"
WORLD_MODEL_LSTM_METRICS_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm_metrics.json"
```

and add:

```python
@st.cache_data
def load_world_model_lstm_metrics() -> dict:
    if not WORLD_MODEL_LSTM_METRICS_PATH.exists():
        return {}
    import json

    return json.loads(WORLD_MODEL_LSTM_METRICS_PATH.read_text(encoding="utf-8"))
```

- [ ] **Step 4: Run data-loader tests**

Run:

```powershell
python -m pytest sprint3\tests\test_data_loader.py -q
```

Expected: PASS.

---

### Task 6: Final Verification and Dashboard-Ready Check

**Files:**
- All modified files above
- Existing generated outputs in `sprint3/outputs/`

- [ ] **Step 1: Run full sprint3 test suite**

Run:

```powershell
python -m pytest sprint3\tests -q
```

Expected: all tests pass.

- [ ] **Step 2: Run a small inference smoke script**

Run:

```powershell
& 'C:\Users\dania\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "import pandas as pd; from sprint3.world_model_dataset import EXO_COLUMNS,ACTION_COLUMNS,ENDO_COLUMNS; from sprint3.world_model_lstm_inference import load_lstm_world_model,predict_next_state; df=pd.read_csv('sprint3/outputs/world_model_training_dataset.csv', parse_dates=['Time']).dropna(subset=EXO_COLUMNS+ACTION_COLUMNS+ENDO_COLUMNS).sort_values(['policy_id','Time']); model,scalers=load_lstm_world_model(); row=predict_next_state(model,scalers,df.head(12),{'tracker_angle_deg':15.0,'irrigation_on':True,'irrigation_dose_mm':1.0},device='cpu'); print(row)"
```

Expected: prints a dictionary containing `VWC_R1_sim`, `Tsoil_R1_sim`, `Delta_VWC_S1_sim`, `Delta_Tsoil_S1_sim`, and `minutes_since_last_irr: 0`.

- [ ] **Step 3: Inspect git status**

Run:

```powershell
git status --short
```

Expected: only intentional source/tests/outputs changes are listed; no `__pycache__` additions.

- [ ] **Step 4: Decide artifact policy before commit**

Recommended commit set:

```text
Include:
- sprint3/*.py source files
- sprint3/tests/*.py tests
- docs/superpowers/plans/*.md
- sprint3/outputs/world_model_lstm_metrics.json
- sprint3/outputs/world_model_lstm_predictions_sample.csv

Discuss before including:
- sprint3/outputs/world_model_lstm.pt
- sprint3/outputs/world_model_lstm_scalers.joblib
- large generated CSVs
```

Rationale: source code and metrics are reviewable; model binaries and large generated datasets may be better regenerated locally unless the team wants reproducible demo artifacts in git.

---

## Self-Review

Spec coverage:
- Adds a CSV sanity review before code changes so model outputs are checked against physical ranges and dataset shape.
- Removes the weak direct LSTM target `minutes_since_last_irr`.
- Keeps irrigation context available as model input.
- Adds a concrete `predict_next_state` inference layer.
- Adds deterministic irrigation-counter behavior.
- Adds multi-step rollout for future RL policy simulation.
- Exposes LSTM artifact status for dashboard usage.

Placeholder scan:
- No `TBD`, `TODO`, or vague "add tests" steps remain.

Type consistency:
- `LEARNED_ENDO_COLUMNS` feeds `target_cols`.
- `predict_next_state` returns endogeneous state names without `next_`.
- `rollout_with_policy` accepts a predictor that receives `(recent_window, action)` and returns predicted state fields.
