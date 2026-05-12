# Integrate Agronomy Reward World Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the useful agronomy, crop-zone, irrigation-rule, and reward pieces from `sprint3-10min-pipeline` with the calibrated `master_dataset_world_model.csv`, producing a clean training dataset for the future LSTM/World Model and preserving dashboard compatibility.

**Architecture:** Keep the calibrated notebook/output as the source of environment dynamics, then add a separate agronomy/reward layer that computes crop risk and reward from the simulated state. Do not merge Joel's old `Master_dataset_reg.ipynb`; cherry-pick focused modules and adapt them to the new world-model schema. The final pipeline should produce both dashboard-facing outputs and RL/LSTM-ready `(state_t, action_t, state_t+1, reward_t)` rows.

**Tech Stack:** Python, pandas, pytest, Streamlit dashboard modules, CSV/JSON outputs.

---

## File Structure

- `sprint3/Master_dataset_reg.ipynb`: keep current calibrated irrigation simulation and `episode_id` fix. Do not replace from `sprint3-10min-pipeline`.
- `sprint3/agricultural_rules.py`: import from `sprint3-10min-pipeline`, then adapt column names for the calibrated world model.
- `sprint3/rl_policy.py`: import from `sprint3-10min-pipeline`, then keep only reward/policy utilities that fit the new model outputs.
- `sprint3/world_model_dataset.py`: create a focused adapter from `master_dataset_world_model.csv` to agronomy/reward/training rows.
- `sprint3/build_world_model_training_dataset.py`: create a CLI entrypoint that generates the reward-enriched training dataset.
- `sprint3/tabs/tab_agronomia.py`: import later from Joel's branch after backend outputs exist; dashboard integration is a final task, not the first step.
- `sprint3/data_loader.py`: update only after output filenames are stable.
- `sprint3/tests/test_world_model_dataset.py`: add tests for schema conversion, next-state alignment, and reward columns.
- `sprint3/tests/test_agricultural_rules.py`: import/adapt Joel's tests.
- `sprint3/tests/test_rl_policy.py`: import/adapt Joel's tests.

---

### Task 1: Import Agronomy And Reward Modules Safely

**Files:**
- Create: `sprint3/agricultural_rules.py`
- Create: `sprint3/rl_policy.py`
- Test: `sprint3/tests/test_agricultural_rules.py`
- Test: `sprint3/tests/test_rl_policy.py`

- [ ] **Step 1: Restore files from Joel's branch without switching branches**

Run:

```powershell
git show sprint3-10min-pipeline:sprint3/agricultural_rules.py > sprint3/agricultural_rules.py
git show sprint3-10min-pipeline:sprint3/rl_policy.py > sprint3/rl_policy.py
git show sprint3-10min-pipeline:sprint3/tests/test_agricultural_rules.py > sprint3/tests/test_agricultural_rules.py
git show sprint3-10min-pipeline:sprint3/tests/test_rl_policy.py > sprint3/tests/test_rl_policy.py
```

Expected: the four files exist locally. Do not restore Joel's notebook.

- [ ] **Step 2: Run imported tests**

Run:

```powershell
python -m pytest sprint3/tests/test_agricultural_rules.py sprint3/tests/test_rl_policy.py -q
```

Expected: tests may fail because the current branch does not yet expose Joel's expected 10-minute modeling schema. Record exact failures before changing code.

- [ ] **Step 3: Keep only source-compatible imports**

If tests fail due to missing module imports, update import paths only. Do not change behavior yet.

Expected: failures, if any, should be schema/column mismatches, not import errors.

---

### Task 2: Create World Model Schema Adapter

**Files:**
- Create: `sprint3/world_model_dataset.py`
- Create: `sprint3/tests/test_world_model_dataset.py`

- [ ] **Step 1: Write failing tests for world-model schema conversion**

Create `sprint3/tests/test_world_model_dataset.py`:

```python
import pandas as pd
import pytest

from sprint3.world_model_dataset import (
    ACTION_COLUMNS,
    ENDO_COLUMNS,
    EXO_COLUMNS,
    build_dashboard_model_frame,
    build_transition_dataset,
)


def _sample_world_model_df():
    return pd.DataFrame({
        "Time": pd.date_range("2025-06-17 14:00:00", periods=4, freq="10min"),
        "policy_id": ["fixed_6h_2.0mm"] * 4,
        "episode_id": [f"fixed_6h_2.0mm_{i}" for i in range(4)],
        "hour_sin": [0.0, 0.1, 0.2, 0.3],
        "hour_cos": [1.0, 0.9, 0.8, 0.7],
        "day_sin": [0.2] * 4,
        "day_cos": [0.9] * 4,
        "solar_elevation_deg": [60.0, 58.0, 55.0, 50.0],
        "solar_azimuth_deg": [180.0, 185.0, 190.0, 195.0],
        "clearsky_ghi_wm2": [900.0, 880.0, 850.0, 810.0],
        "air_temp_ext_avg_degc": [26.0, 26.5, 27.0, 27.5],
        "wind_speed_kmh": [8.0, 8.5, 9.0, 9.5],
        "precip_intensity_mm10min": [0.0, 0.0, 0.0, 0.0],
        "PAR_R1": [1500.0, 1450.0, 1400.0, 1300.0],
        "tracker_angle_deg": [20.0, 22.0, 24.0, 26.0],
        "irrigation_on": [0, 1, 0, 0],
        "irrigation_dose_mm": [2.0, 2.0, 2.0, 2.0],
        "GPOA_mean": [700.0, 710.0, 690.0, 660.0],
        "ALBEDO_mean": [40.0, 41.0, 42.0, 43.0],
        "Delta_PAR_S1": [-200.0, -210.0, -220.0, -230.0],
        "VWC_R1_sim": [0.18, 0.19, 0.20, 0.205],
        "minutes_since_last_irr": [120.0, 0.0, 10.0, 20.0],
        "Delta_VWC_S1_sim": [0.01, 0.012, 0.014, 0.015],
        "Tsoil_R1_sim": [22.0, 21.8, 21.7, 21.6],
        "Delta_Tsoil_S1_sim": [-0.5, -0.6, -0.7, -0.8],
        "irrigation_mm_10min": [0.0, 2.1, 0.0, 0.0],
        "irrigation_duration_min": [0.0, 10.5, 0.0, 0.0],
        "irrigation_cumulative_day_mm": [0.0, 2.1, 2.1, 2.1],
        "water_input_mm": [0.0, 2.1, 0.0, 0.0],
    })


def test_dashboard_model_frame_maps_world_model_columns():
    frame = build_dashboard_model_frame(_sample_world_model_df(), crop_zone="S1")

    assert list(frame["Time"]) == list(_sample_world_model_df()["Time"])
    assert frame["track_mean"].tolist() == [20.0, 22.0, 24.0, 26.0]
    assert frame["VWC_S1_mean"].iloc[0] == pytest.approx(0.19)
    assert frame["Tsoil_S1_mean"].iloc[0] == pytest.approx(21.5)
    assert "energy_score" in frame.columns
    assert "crop_score" in frame.columns
    assert "IEC" in frame.columns


def test_transition_dataset_aligns_next_state_within_policy():
    transitions = build_transition_dataset(_sample_world_model_df())

    assert len(transitions) == 3
    assert transitions["policy_id"].nunique() == 1
    assert transitions["next_VWC_R1_sim"].iloc[0] == pytest.approx(0.19)
    assert transitions["next_Tsoil_R1_sim"].iloc[1] == pytest.approx(21.7)
    assert set(EXO_COLUMNS).issubset(transitions.columns)
    assert set(ACTION_COLUMNS).issubset(transitions.columns)
    assert set(ENDO_COLUMNS).issubset(transitions.columns)
```

- [ ] **Step 2: Verify tests fail**

Run:

```powershell
python -m pytest sprint3/tests/test_world_model_dataset.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'sprint3.world_model_dataset'`.

- [ ] **Step 3: Implement minimal adapter**

Create `sprint3/world_model_dataset.py`:

```python
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


EXO_COLUMNS = [
    "hour_sin",
    "hour_cos",
    "day_sin",
    "day_cos",
    "solar_elevation_deg",
    "solar_azimuth_deg",
    "clearsky_ghi_wm2",
    "air_temp_ext_avg_degc",
    "wind_speed_kmh",
    "precip_intensity_mm10min",
    "PAR_R1",
]

ACTION_COLUMNS = [
    "tracker_angle_deg",
    "irrigation_on",
    "irrigation_dose_mm",
]

ENDO_COLUMNS = [
    "GPOA_mean",
    "ALBEDO_mean",
    "Delta_PAR_S1",
    "VWC_R1_sim",
    "minutes_since_last_irr",
    "Delta_VWC_S1_sim",
    "Tsoil_R1_sim",
    "Delta_Tsoil_S1_sim",
]

META_COLUMNS = [
    "Time",
    "policy_id",
    "episode_id",
    "irrigation_mm_10min",
    "irrigation_duration_min",
    "irrigation_cumulative_day_mm",
    "water_input_mm",
]


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"world model dataset missing required columns: {missing}")


def load_world_model_dataset(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Time"])
    _require_columns(df, META_COLUMNS + EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS)
    return df.sort_values(["policy_id", "Time"]).reset_index(drop=True)


def _bounded_score(series: pd.Series, denominator: float) -> pd.Series:
    if denominator <= 0 or pd.isna(denominator):
        return pd.Series(0.0, index=series.index)
    return (pd.to_numeric(series, errors="coerce").fillna(0).clip(lower=0) / denominator).clip(0, 1)


def build_dashboard_model_frame(world_df: pd.DataFrame, crop_zone: str = "S1") -> pd.DataFrame:
    _require_columns(world_df, ["Time", "tracker_angle_deg", "VWC_R1_sim", "Delta_VWC_S1_sim", "Tsoil_R1_sim", "Delta_Tsoil_S1_sim"])
    df = world_df.copy()
    df["Time"] = pd.to_datetime(df["Time"])
    gpoa_p95 = float(pd.to_numeric(df["GPOA_mean"], errors="coerce").quantile(0.95))
    vwc_s1 = (pd.to_numeric(df["VWC_R1_sim"], errors="coerce") + pd.to_numeric(df["Delta_VWC_S1_sim"], errors="coerce")).clip(0, 1)
    tsoil_s1 = pd.to_numeric(df["Tsoil_R1_sim"], errors="coerce") + pd.to_numeric(df["Delta_Tsoil_S1_sim"], errors="coerce")
    energy_score = _bounded_score(df["GPOA_mean"], gpoa_p95)
    vwc_score = (1.0 - (vwc_s1 - 0.24).abs().div(0.14)).clip(0, 1)
    temp_score = (1.0 - (tsoil_s1 - 20.0).abs().div(18.0)).clip(0, 1)
    crop_score = (0.65 * vwc_score + 0.35 * temp_score).clip(0, 1)
    frame = pd.DataFrame({
        "Time": df["Time"],
        "source_resolution": "10min_world_model",
        "minute_of_day": df["Time"].dt.hour * 60 + df["Time"].dt.minute,
        "time_block_10min": df["Time"].dt.strftime("%H:%M"),
        "hour_of_day": df["Time"].dt.hour,
        "day_of_year": df["Time"].dt.dayofyear,
        "solar_elevation_deg": df["solar_elevation_deg"],
        "solar_azimuth_deg": df["solar_azimuth_deg"],
        "clearsky_ghi_wm2": df["clearsky_ghi_wm2"],
        "track_mean": df["tracker_angle_deg"],
        "tracking_regime": np.select(
            [df["solar_elevation_deg"].fillna(-1) <= 0, df["tracker_angle_deg"].abs() < 5, df["tracker_angle_deg"] < 0],
            ["NIGHT_STOW", "HORIZONTAL", "TRACKING_AM"],
            default="TRACKING_PM",
        ),
        "Tair_WS": df["air_temp_ext_avg_degc"],
        "wind_speed_kmh": df["wind_speed_kmh"],
        "precip_intensity_mm10min": df["precip_intensity_mm10min"],
        "Tsoil_R1_mean": df["Tsoil_R1_sim"],
        "Tsoil_S1_mean": tsoil_s1,
        "Tsoil_S2_mean": tsoil_s1,
        "VWC_R1_mean": df["VWC_R1_sim"],
        "VWC_S1_mean": vwc_s1,
        "VWC_S2_mean": vwc_s1,
        "ePAR_R1_mean": df["PAR_R1"],
        "ePAR_S1_mean": (df["PAR_R1"] + df["Delta_PAR_S1"]).clip(lower=0),
        "ePAR_S2_mean": (df["PAR_R1"] + df["Delta_PAR_S1"]).clip(lower=0),
        "GPOA_mean": df["GPOA_mean"],
        "Delta_PAR_S1": df["Delta_PAR_S1"],
        "Delta_Tsoil_S1": df["Delta_Tsoil_S1_sim"],
        "Delta_VWC_S1": df["Delta_VWC_S1_sim"],
        "energy_score": energy_score,
        "crop_score": crop_score,
        "IEC": (0.55 * energy_score + 0.45 * crop_score).clip(0, 1),
        "crop_zone": crop_zone,
        "policy_id": df["policy_id"],
        "episode_id": df["episode_id"],
        "irrigation_on": df["irrigation_on"].astype(bool),
        "irrigation_mm_10min": df["irrigation_mm_10min"],
        "irrigation_duration_min": df["irrigation_duration_min"],
    })
    return frame.round(4)


def build_transition_dataset(world_df: pd.DataFrame) -> pd.DataFrame:
    df = world_df.copy()
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.sort_values(["policy_id", "Time"]).reset_index(drop=True)
    _require_columns(df, ["policy_id", "Time"] + EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS)
    grouped = df.groupby("policy_id", sort=False)
    for column in ENDO_COLUMNS:
        df[f"next_{column}"] = grouped[column].shift(-1)
    df["next_Time"] = grouped["Time"].shift(-1)
    next_cols = [f"next_{column}" for column in ENDO_COLUMNS]
    return df.dropna(subset=next_cols).reset_index(drop=True)
```

- [ ] **Step 4: Verify adapter tests pass**

Run:

```powershell
python -m pytest sprint3/tests/test_world_model_dataset.py -q
```

Expected: PASS.

---

### Task 3: Generate Reward-Enriched Training Dataset

**Files:**
- Create: `sprint3/build_world_model_training_dataset.py`
- Modify: `sprint3/world_model_dataset.py`
- Test: `sprint3/tests/test_world_model_dataset.py`

- [ ] **Step 1: Add failing test for reward-enriched transitions**

Append to `sprint3/tests/test_world_model_dataset.py`:

```python
from sprint3.world_model_dataset import build_reward_training_dataset


def test_reward_training_dataset_contains_total_reward_and_next_state():
    dataset = build_reward_training_dataset(_sample_world_model_df(), crop_type="lechuga", crop_zone="S1")

    assert len(dataset) == 3
    assert "agronomic_component" in dataset.columns
    assert "energy_component" in dataset.columns
    assert "rl_reward" in dataset.columns
    assert dataset["rl_reward"].between(0, 1).all()
    assert "next_VWC_R1_sim" in dataset.columns
```

- [ ] **Step 2: Verify test fails**

Run:

```powershell
python -m pytest sprint3/tests/test_world_model_dataset.py::test_reward_training_dataset_contains_total_reward_and_next_state -q
```

Expected: FAIL with `ImportError` or missing function.

- [ ] **Step 3: Implement reward-enriched builder**

Append to `sprint3/world_model_dataset.py`:

```python
def build_reward_training_dataset(
    world_df: pd.DataFrame,
    crop_type: str = "lechuga",
    crop_zone: str = "S1",
    alpha_agronomic: float = 0.45,
    beta_energy: float = 0.55,
) -> pd.DataFrame:
    transitions = build_transition_dataset(world_df)
    dashboard = build_dashboard_model_frame(world_df, crop_zone=crop_zone)
    reward_cols = dashboard[["episode_id", "energy_score", "crop_score"]].rename(
        columns={"energy_score": "energy_component", "crop_score": "agronomic_component"}
    )
    dataset = transitions.merge(reward_cols, on="episode_id", how="left")
    dataset["crop_type"] = crop_type
    dataset["crop_zone"] = crop_zone
    dataset["reward_alpha_agronomic"] = float(alpha_agronomic)
    dataset["reward_beta_energy"] = float(beta_energy)
    dataset["rl_reward"] = (
        dataset["reward_alpha_agronomic"] * dataset["agronomic_component"].fillna(0)
        + dataset["reward_beta_energy"] * dataset["energy_component"].fillna(0)
    ).clip(0, 1)
    return dataset.round(4)
```

- [ ] **Step 4: Create CLI script**

Create `sprint3/build_world_model_training_dataset.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from world_model_dataset import build_reward_training_dataset, load_world_model_dataset


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_WORLD_MODEL_PATH = BASE_DIR / "outputs" / "master_dataset_world_model.csv"
DEFAULT_OUTPUT_PATH = BASE_DIR / "outputs" / "world_model_training_dataset.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reward-enriched transition dataset for LSTM/RL training.")
    parser.add_argument("--world-model-path", type=Path, default=DEFAULT_WORLD_MODEL_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--crop-type", default="lechuga")
    parser.add_argument("--crop-zone", default="S1")
    args = parser.parse_args()

    world_df = load_world_model_dataset(args.world_model_path)
    dataset = build_reward_training_dataset(world_df, crop_type=args.crop_type, crop_zone=args.crop_zone)
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(args.output_path, index=False)
    print(f"training dataset: {args.output_path}")
    print(f"rows: {len(dataset):,}")
    print(f"policies: {dataset['policy_id'].nunique():,}")
    print(f"reward mean: {dataset['rl_reward'].mean():.4f}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Verify tests and CLI**

Run:

```powershell
python -m pytest sprint3/tests/test_world_model_dataset.py -q
python sprint3/build_world_model_training_dataset.py
```

Expected: tests pass and `sprint3/outputs/world_model_training_dataset.csv` is created with `414744` rows: `12 * (34563 - 1)`.

---

### Task 4: Decide IEC Role And Dashboard Outputs

**Files:**
- Modify: `sprint3/data_loader.py`
- Create or import: `sprint3/tabs/tab_agronomia.py`
- Modify: `sprint3/app.py`
- Test: `sprint3/tests/test_data_loader.py`

- [ ] **Step 1: Keep IEC as diagnostic, reward as primary**

Dashboard wording should use:

```text
Primary: Reward agroenergético
Secondary: componente agrícola, componente energético
Diagnostic: IEC histórico
```

- [ ] **Step 2: Add loader tests for world-model training dataset**

Add to `sprint3/tests/test_data_loader.py`:

```python
def test_load_world_model_training_dataset_reads_reward_columns(tmp_path, monkeypatch):
    path = tmp_path / "world_model_training_dataset.csv"
    path.write_text(
        "Time,policy_id,episode_id,rl_reward,energy_component,agronomic_component\n"
        "2025-01-01 00:00:00,p,e,0.7,0.8,0.6\n",
        encoding="utf-8",
    )
    import sprint3.data_loader as data_loader
    monkeypatch.setattr(data_loader, "WORLD_MODEL_TRAINING_PATH", path)

    df = data_loader.load_world_model_training_dataset()

    assert df["rl_reward"].iloc[0] == 0.7
```

- [ ] **Step 3: Implement loader**

Add to `sprint3/data_loader.py`:

```python
WORLD_MODEL_TRAINING_PATH = _BASE_DIR / "outputs" / "world_model_training_dataset.csv"


def load_world_model_training_dataset() -> pd.DataFrame:
    if not WORLD_MODEL_TRAINING_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(WORLD_MODEL_TRAINING_PATH, parse_dates=["Time"])
```

- [ ] **Step 4: Import dashboard tab from Joel's branch only after backend works**

Run:

```powershell
git show sprint3-10min-pipeline:sprint3/tabs/tab_agronomia.py > sprint3/tabs/tab_agronomia.py
```

Then update imports/data loaders to point to the new reward/world-model outputs. Do not make this step until Tasks 1-3 pass.

---

### Task 5: Prepare LSTM Training Script Skeleton

**Files:**
- Create: `sprint3/world_model_lstm_dataset.py`
- Create: `sprint3/train_world_model_lstm.py`
- Create: `sprint3/tests/test_world_model_lstm_dataset.py`

- [ ] **Step 1: Write failing tests for temporal windows**

Create `sprint3/tests/test_world_model_lstm_dataset.py`:

```python
import pandas as pd

from sprint3.world_model_lstm_dataset import make_policy_windows


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
```

- [ ] **Step 2: Implement window utility**

Create `sprint3/world_model_lstm_dataset.py`:

```python
from __future__ import annotations

import numpy as np
import pandas as pd


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
        return np.empty((0, window_size, len(feature_cols)), dtype="float32"), np.empty((0, len(target_cols)), dtype="float32")
    return np.stack(xs), np.stack(ys)
```

- [ ] **Step 3: Verify window tests**

Run:

```powershell
python -m pytest sprint3/tests/test_world_model_lstm_dataset.py -q
```

Expected: PASS.

- [ ] **Step 4: Create placeholder train script that validates dataset and window shapes**

Create `sprint3/train_world_model_lstm.py`:

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd

from world_model_dataset import ACTION_COLUMNS, ENDO_COLUMNS, EXO_COLUMNS
from world_model_lstm_dataset import make_policy_windows


BASE_DIR = Path(__file__).resolve().parent
TRAINING_DATASET = BASE_DIR / "outputs" / "world_model_training_dataset.csv"


def main() -> None:
    df = pd.read_csv(TRAINING_DATASET, parse_dates=["Time"])
    feature_cols = EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS
    target_cols = [f"next_{column}" for column in ENDO_COLUMNS]
    x, y = make_policy_windows(df.dropna(subset=feature_cols + target_cols), feature_cols, target_cols, window_size=12)
    print(f"X shape: {x.shape}")
    print(f"y shape: {y.shape}")
    print("Next step: plug these arrays into torch/keras LSTM after baseline metrics.")


if __name__ == "__main__":
    main()
```

---

## Verification Checklist

- [ ] `python -m pytest sprint3/tests -q` passes.
- [ ] `sprint3/outputs/master_dataset_world_model.csv` still has `414756` rows and unique `episode_id`.
- [ ] `sprint3/outputs/world_model_training_dataset.csv` has `414744` rows.
- [ ] `rl_reward`, `energy_component`, and `agronomic_component` are present and in `[0, 1]`.
- [ ] No code imports Joel's old notebook or overwrites the calibrated notebook.
- [ ] Dashboard still starts after backend integration.

---

## Self-Review

Spec coverage:
- Uses Joel's branch for crop thresholds, zones, reward, and irrigation-rule ideas.
- Preserves calibrated world-model output and does not merge the old notebook.
- Creates the missing bridge toward LSTM: transition rows and temporal windows.
- Keeps IEC as diagnostic while reward becomes primary.

Placeholder scan:
- No task uses "TBD" or "implement later".
- Each code task contains concrete file paths, snippets, and commands.

Type consistency:
- `EXO_COLUMNS`, `ACTION_COLUMNS`, and `ENDO_COLUMNS` are defined in `world_model_dataset.py` and reused by the LSTM skeleton.
- `policy_id` is the grouping key for both transitions and windows.
