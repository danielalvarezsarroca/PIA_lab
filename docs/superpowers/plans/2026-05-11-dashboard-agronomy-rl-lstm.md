# Dashboard Agronomy RL LSTM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the sprint 3 agronomy/RL/LSTM work to the main Streamlit dashboard as a realistic decision workspace for crop-zone management, irrigation, panel movement, and short-horizon world-model simulation.

**Architecture:** Connect the existing `tab_agronomia.py` into `app.py`, then add a small dashboard-facing prediction layer that wraps `predict_next_state(...)` without leaking PyTorch details into UI code. The UI should keep the current glassy/card aesthetic, but make `Reward RL` and crop/energy trade-off more prominent than the old `IEC`; LSTM metrics should appear as model confidence/status, not as a separate technical page.

**Tech Stack:** Streamlit, pandas, Plotly, existing sprint3 CSS helpers, PyTorch artifacts loaded through `world_model_lstm_inference.py`, pytest.

---

## Visual Thesis

Operational, calm, and decision-first: the new tab should feel like a control desk for an agronomist/operator, with the model quietly supporting decisions rather than shouting “machine learning demo”.

## Product Shape

The new tab is named `Agronomía / RL`. Its main user story is:

> “For zone S1/S2 and crop X, compare the recommended action with a manual what-if action, then see the predicted next soil/crop/energy state.”

The page should have four layers:

1. Crop and zone selectors.
2. Current decision cards: `Reward RL`, crop health, energy component, irrigation action.
3. Visual decision surface: crop scene + policy recommendation + “Qué pasa si...” controls.
4. Model status strip: LSTM trained/not found, target MAEs, window length, artifact freshness.

---

## File Structure

- Modify `sprint3/app.py`
  - Import `render_tab_agronomia`.
  - Load default world-model dashboard frame/crop-risk/RL-policy data.
  - Add a fifth tab named `Agronomía / RL`.
  - Update header metadata from `resolución 6h` to `6h + simulación 10min` if world-model outputs exist.

- Modify `sprint3/data_loader.py`
  - Add cached `load_world_model_lstm_prediction_sample()`.
  - Add lightweight artifact status helper `get_world_model_lstm_status()`.
  - Add `load_world_model_recent_window(crop_zone="S1", policy_id=None, rows=12)` for dashboard what-if inference.

- Modify `sprint3/tabs/tab_agronomia.py`
  - Keep existing crop scene, calendar, rules, and crop selector.
  - Add model-status strip.
  - Add “Qué pasa si...” controls.
  - Add predicted next-state cards and a compact before/after chart.
  - Keep the current rounded/glassy style and Plotly styling.

- Create `sprint3/dashboard_lstm.py`
  - Dashboard-specific wrapper around LSTM artifacts.
  - Builds safe prediction previews without importing Streamlit.
  - Converts model output into UI fields: VWC, Tsoil, PAR, GPOA, irrigation counter.

- Add tests:
  - `sprint3/tests/test_dashboard_lstm.py`
  - Update `sprint3/tests/test_data_loader.py`
  - Add `sprint3/tests/test_app_tabs.py`

---

### Task 1: Add Dashboard LSTM Wrapper

**Files:**
- Create: `sprint3/dashboard_lstm.py`
- Test: `sprint3/tests/test_dashboard_lstm.py`

- [ ] **Step 1: Write failing tests for dashboard prediction formatting**

Create `sprint3/tests/test_dashboard_lstm.py`:

```python
import pandas as pd

from sprint3.dashboard_lstm import build_prediction_delta_frame, format_model_status


def test_format_model_status_extracts_key_metrics():
    metrics = {
        "window_size": 12,
        "target_metrics": {
            "next_VWC_R1_sim": {"mae": 0.003852, "rmse": 0.005831},
            "next_Tsoil_R1_sim": {"mae": 0.111123, "rmse": 0.192392},
            "next_GPOA_mean": {"mae": 12.740058, "rmse": 26.970427},
        },
    }

    status = format_model_status(metrics, model_exists=True, scalers_exist=True)

    assert status["state"] == "Entrenado"
    assert status["window"] == "12 pasos x 10 min"
    assert status["vwc_mae"] == "0.0039"
    assert status["tsoil_mae"] == "0.111 °C"
    assert status["gpoa_mae"] == "12.74 W/m²"


def test_format_model_status_reports_missing_artifacts():
    status = format_model_status({}, model_exists=False, scalers_exist=False)

    assert status["state"] == "No disponible"
    assert status["window"] == "Sin artefactos"


def test_build_prediction_delta_frame_returns_before_after_rows():
    current = pd.Series({
        "VWC_R1_sim": 0.18,
        "Tsoil_R1_sim": 24.0,
        "PAR_R1": 520.0,
        "GPOA_mean": 760.0,
    })
    predicted = {
        "VWC_R1_sim": 0.20,
        "Tsoil_R1_sim": 23.5,
        "Delta_PAR_S1": -120.0,
        "GPOA_mean": 710.0,
        "minutes_since_last_irr": 0,
    }

    frame = build_prediction_delta_frame(current, predicted)

    assert list(frame["momento"]) == ["Ahora", "+10 min"]
    assert frame.loc[1, "VWC"] == 0.20
    assert frame.loc[1, "Tsoil"] == 23.5
    assert frame.loc[1, "PAR"] == 400.0
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
python -m pytest sprint3\tests\test_dashboard_lstm.py -q
```

Expected: FAIL because `sprint3.dashboard_lstm` does not exist.

- [ ] **Step 3: Implement dashboard wrapper**

Create `sprint3/dashboard_lstm.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from world_model_lstm_inference import load_lstm_world_model, predict_next_state


def _metric_value(metrics: dict, target: str, key: str = "mae") -> float | None:
    value = metrics.get("target_metrics", {}).get(target, {}).get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_model_status(metrics: dict, model_exists: bool, scalers_exist: bool) -> dict[str, str]:
    if not model_exists or not scalers_exist or not metrics:
        return {
            "state": "No disponible",
            "window": "Sin artefactos",
            "vwc_mae": "—",
            "tsoil_mae": "—",
            "gpoa_mae": "—",
        }

    window_size = int(metrics.get("window_size", 12))
    vwc_mae = _metric_value(metrics, "next_VWC_R1_sim")
    tsoil_mae = _metric_value(metrics, "next_Tsoil_R1_sim")
    gpoa_mae = _metric_value(metrics, "next_GPOA_mean")
    return {
        "state": "Entrenado",
        "window": f"{window_size} pasos x 10 min",
        "vwc_mae": f"{vwc_mae:.4f}" if vwc_mae is not None else "—",
        "tsoil_mae": f"{tsoil_mae:.3f} °C" if tsoil_mae is not None else "—",
        "gpoa_mae": f"{gpoa_mae:.2f} W/m²" if gpoa_mae is not None else "—",
    }


def build_prediction_delta_frame(current: pd.Series, predicted: dict[str, float | int]) -> pd.DataFrame:
    current_par = float(current.get("PAR_R1", 0.0))
    predicted_par = max(0.0, current_par + float(predicted.get("Delta_PAR_S1", 0.0)))
    return pd.DataFrame([
        {
            "momento": "Ahora",
            "VWC": float(current.get("VWC_R1_sim", current.get("VWC_R1_mean", 0.0))),
            "Tsoil": float(current.get("Tsoil_R1_sim", current.get("Tsoil_R1_mean", 0.0))),
            "PAR": current_par,
            "GPOA": float(current.get("GPOA_mean", 0.0)),
        },
        {
            "momento": "+10 min",
            "VWC": float(predicted.get("VWC_R1_sim", 0.0)),
            "Tsoil": float(predicted.get("Tsoil_R1_sim", 0.0)),
            "PAR": predicted_par,
            "GPOA": float(predicted.get("GPOA_mean", 0.0)),
        },
    ])


def predict_dashboard_next_state(
    recent_window: pd.DataFrame,
    tracker_angle_deg: float,
    irrigation_on: bool,
    irrigation_dose_mm: float,
    model_path: str | Path,
    scalers_path: str | Path,
    device: str = "cpu",
) -> dict[str, float | int]:
    model, scalers = load_lstm_world_model(
        model_path=model_path,
        scalers_path=scalers_path,
        device=device,
    )
    return predict_next_state(
        model=model,
        scalers=scalers,
        recent_window=recent_window,
        action={
            "tracker_angle_deg": float(tracker_angle_deg),
            "irrigation_on": bool(irrigation_on),
            "irrigation_dose_mm": float(irrigation_dose_mm),
        },
        device=device,
    )
```

- [ ] **Step 4: Run dashboard LSTM tests**

Run:

```powershell
python -m pytest sprint3\tests\test_dashboard_lstm.py -q
```

Expected: PASS.

---

### Task 2: Add Data Loader Hooks for Dashboard

**Files:**
- Modify: `sprint3/data_loader.py`
- Test: `sprint3/tests/test_data_loader.py`

- [ ] **Step 1: Add tests for status and recent-window loaders**

Append to `sprint3/tests/test_data_loader.py`:

```python
def test_get_world_model_lstm_status_uses_metrics_and_artifact_paths(monkeypatch):
    import data_loader

    monkeypatch.setattr(data_loader.WORLD_MODEL_LSTM_PATH, "exists", lambda: True)
    monkeypatch.setattr(data_loader.WORLD_MODEL_LSTM_SCALERS_PATH, "exists", lambda: True)
    monkeypatch.setattr(
        data_loader,
        "load_world_model_lstm_metrics",
        lambda: {
            "window_size": 12,
            "target_metrics": {
                "next_VWC_R1_sim": {"mae": 0.003852},
                "next_Tsoil_R1_sim": {"mae": 0.111123},
                "next_GPOA_mean": {"mae": 12.740058},
            },
        },
    )

    status = data_loader.get_world_model_lstm_status()

    assert status["state"] == "Entrenado"
    assert status["window"] == "12 pasos x 10 min"


def test_load_world_model_recent_window_returns_sorted_tail(tmp_path, monkeypatch):
    path = tmp_path / "master_dataset_world_model.csv"
    path.write_text(
        "Time,policy_id,episode_id,irrigation_mm_10min,irrigation_duration_min,irrigation_cumulative_day_mm,water_input_mm,"
        "hour_sin,hour_cos,day_sin,day_cos,solar_elevation_deg,solar_azimuth_deg,clearsky_ghi_wm2,air_temp_ext_avg_degc,"
        "wind_speed_kmh,precip_intensity_mm10min,PAR_R1,tracker_angle_deg,irrigation_on,irrigation_dose_mm,"
        "GPOA_mean,ALBEDO_mean,Delta_PAR_S1,VWC_R1_sim,minutes_since_last_irr,Delta_VWC_S1_sim,Tsoil_R1_sim,Delta_Tsoil_S1_sim\n"
        "2026-01-01 00:00:00,p,e1,0,0,0,0,0,1,0,1,0,0,0,20,1,0,100,0,0,0,0,0,0,0.18,10,0.01,20,-1\n"
        "2026-01-01 00:10:00,p,e2,0,0,0,0,0,1,0,1,0,0,0,20,1,0,100,0,0,0,0,0,0,0.19,20,0.01,21,-1\n",
        encoding="utf-8",
    )
    import data_loader

    monkeypatch.setattr(data_loader, "WORLD_MODEL_PATH", path)

    recent = data_loader.load_world_model_recent_window(rows=1)

    assert len(recent) == 1
    assert recent.iloc[0]["episode_id"] == "e2"
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
python -m pytest sprint3\tests\test_data_loader.py::test_get_world_model_lstm_status_uses_metrics_and_artifact_paths sprint3\tests\test_data_loader.py::test_load_world_model_recent_window_returns_sorted_tail -q
```

Expected: FAIL because the new functions do not exist.

- [ ] **Step 3: Implement hooks in `data_loader.py`**

Add imports:

```python
from dashboard_lstm import format_model_status
```

Add functions:

```python
@st.cache_data
def load_world_model_lstm_prediction_sample() -> pd.DataFrame:
    path = _SPRINT3_DIR / "outputs" / "world_model_lstm_predictions_sample.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_world_model_recent_window(crop_zone: str = "S1", policy_id: str | None = None, rows: int = 12) -> pd.DataFrame:
    if not WORLD_MODEL_PATH.exists():
        return pd.DataFrame()
    world_df = load_world_model_dataset(WORLD_MODEL_PATH)
    if policy_id is not None and "policy_id" in world_df.columns:
        scoped = world_df[world_df["policy_id"].astype(str).eq(str(policy_id))]
        if not scoped.empty:
            world_df = scoped
    return world_df.sort_values(["policy_id", "Time"]).tail(rows).reset_index(drop=True)


def get_world_model_lstm_status() -> dict[str, str]:
    return format_model_status(
        load_world_model_lstm_metrics(),
        model_exists=WORLD_MODEL_LSTM_PATH.exists(),
        scalers_exist=WORLD_MODEL_LSTM_SCALERS_PATH.exists(),
    )
```

- [ ] **Step 4: Run data loader tests**

Run:

```powershell
python -m pytest sprint3\tests\test_data_loader.py -q
```

Expected: PASS.

---

### Task 3: Connect Agronomy Tab in Main App

**Files:**
- Modify: `sprint3/app.py`
- Test: `sprint3/tests/test_app_tabs.py`

- [ ] **Step 1: Add app source test for fifth tab**

Create `sprint3/tests/test_app_tabs.py`:

```python
from pathlib import Path


APP_SOURCE = Path("sprint3/app.py").read_text(encoding="utf-8")


def test_app_imports_agronomy_tab():
    assert "from tabs.tab_agronomia import render_tab_agronomia" in APP_SOURCE


def test_app_declares_agronomy_rl_tab():
    assert "Agronomía / RL" in APP_SOURCE or "Agronomia / RL" in APP_SOURCE
    assert "tab1, tab2, tab3, tab4, tab5 = st.tabs" in APP_SOURCE


def test_app_renders_agronomy_tab():
    assert "render_tab_agronomia(" in APP_SOURCE
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
python -m pytest sprint3\tests\test_app_tabs.py -q
```

Expected: FAIL because `app.py` still has only four tabs.

- [ ] **Step 3: Modify `app.py` imports and data loading**

Add to imports from `data_loader`:

```python
load_crop_risk_for_crop,
load_agricultural_rules_for_crop,
load_rl_policy_for_crop,
load_world_model_dashboard_frame,
```

Add tab import:

```python
from tabs.tab_agronomia import render_tab_agronomia
```

After current data loading, add:

```python
df_world_dashboard = load_world_model_dashboard_frame()
df_crop_risk = load_crop_risk_for_crop("lechuga", crop_zone="S1")
df_agri_rules = load_agricultural_rules_for_crop("lechuga", crop_zone="S1")
df_rl_policy = load_rl_policy_for_crop("lechuga", crop_zone="S1")
```

Change header metadata:

```python
resolution_note = "Datos integrados · 6h + simulación 10min" if not df_world_dashboard.empty else "Datos integrados · resolución 6h"
```

Use `{resolution_note}` inside the `meta-note` span.

- [ ] **Step 4: Modify tab list and render call**

Change:

```python
tab1, tab2, tab3, tab4 = st.tabs([
    "Dashboard",
    "Series temporales",
    "Recomendación",
    alerts_label,
])
```

to:

```python
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard",
    "Series temporales",
    "Recomendación",
    "Agronomía / RL",
    alerts_label,
])
```

Add:

```python
with tab4:
    render_tab_agronomia(df_crop_risk, df_agri_rules, df_rl_policy, df_world_dashboard if not df_world_dashboard.empty else df_modelo)
with tab5:
    render_tab_alertas(df_diagnostic, df_modelo)
```

and move the old alert rendering from `tab4` to `tab5`.

- [ ] **Step 5: Run app-tab tests**

Run:

```powershell
python -m pytest sprint3\tests\test_app_tabs.py -q
```

Expected: PASS.

---

### Task 4: Add Model Status Strip to Agronomy Tab

**Files:**
- Modify: `sprint3/tabs/tab_agronomia.py`
- Test: `sprint3/tests/test_tab_agronomia_source.py`

- [ ] **Step 1: Add source test for model status UI**

Create `sprint3/tests/test_tab_agronomia_source.py`:

```python
from pathlib import Path


SOURCE = Path("sprint3/tabs/tab_agronomia.py").read_text(encoding="utf-8")


def test_agronomy_tab_imports_lstm_status_loader():
    assert "get_world_model_lstm_status" in SOURCE


def test_agronomy_tab_has_model_status_renderer():
    assert "def _render_lstm_model_status" in SOURCE
    assert "Modelo predictivo" in SOURCE
    assert "Error humedad" in SOURCE
```

- [ ] **Step 2: Run source test and verify failure**

Run:

```powershell
python -m pytest sprint3\tests\test_tab_agronomia_source.py -q
```

Expected: FAIL because the model status strip does not exist.

- [ ] **Step 3: Add imports**

In `sprint3/tabs/tab_agronomia.py`, extend `data_loader` imports:

```python
    get_world_model_lstm_status,
```

- [ ] **Step 4: Add `_render_lstm_model_status`**

Add this helper near other render helpers:

```python
def _render_lstm_model_status() -> None:
    status = get_world_model_lstm_status()
    cards = [
        ("Modelo predictivo", status["state"], status["window"], COLOR["blue"]),
        ("Error humedad", status["vwc_mae"], "MAE VWC R1 sim", COLOR["green"]),
        ("Error temperatura", status["tsoil_mae"], "MAE Tsoil R1 sim", COLOR["amber"]),
        ("Error energía", status["gpoa_mae"], "MAE GPOA", "#6d5bd0"),
    ]
    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin:22px 0 10px;">Modelo predictivo</div>',
        unsafe_allow_html=True,
    )
    for col, (title, value, detail, color) in zip(st.columns(4), cards):
        col.markdown(_metric_card(title, value, detail, color), unsafe_allow_html=True)
```

- [ ] **Step 5: Render status strip after current KPI cards**

After the first four KPI cards in `render_tab_agronomia`, add:

```python
    _render_lstm_model_status()
```

- [ ] **Step 6: Run source test**

Run:

```powershell
python -m pytest sprint3\tests\test_tab_agronomia_source.py -q
```

Expected: PASS.

---

### Task 5: Add “Qué Pasa Si...” LSTM Simulator

**Files:**
- Modify: `sprint3/tabs/tab_agronomia.py`
- Test: update `sprint3/tests/test_tab_agronomia_source.py`

- [ ] **Step 1: Add source tests for what-if simulator**

Append to `sprint3/tests/test_tab_agronomia_source.py`:

```python
def test_agronomy_tab_has_what_if_simulator():
    assert "def _render_lstm_what_if" in SOURCE
    assert "Qué pasa si" in SOURCE
    assert "Simular siguiente estado" in SOURCE
    assert "predict_dashboard_next_state" in SOURCE
```

- [ ] **Step 2: Run source test and verify failure**

Run:

```powershell
python -m pytest sprint3\tests\test_tab_agronomia_source.py::test_agronomy_tab_has_what_if_simulator -q
```

Expected: FAIL because simulator does not exist.

- [ ] **Step 3: Add imports**

Add:

```python
from dashboard_lstm import build_prediction_delta_frame, predict_dashboard_next_state
```

and extend `data_loader` imports:

```python
    WORLD_MODEL_LSTM_PATH,
    WORLD_MODEL_LSTM_SCALERS_PATH,
    load_world_model_recent_window,
```

- [ ] **Step 4: Add simulator helper**

Add:

```python
def _render_lstm_what_if(selected_zone: str) -> None:
    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin:22px 0 10px;">Qué pasa si...</div>',
        unsafe_allow_html=True,
    )
    recent_window = load_world_model_recent_window(crop_zone=selected_zone, rows=12)
    if recent_window.empty or not WORLD_MODEL_LSTM_PATH.exists() or not WORLD_MODEL_LSTM_SCALERS_PATH.exists():
        st.info("El simulador predictivo necesita el world model entrenado y una ventana reciente de 12 pasos.")
        return

    latest = recent_window.iloc[-1]
    col_controls, col_result = st.columns([0.95, 1.35])
    with col_controls:
        angle = st.slider(
            "Ángulo placa",
            min_value=-60.0,
            max_value=60.0,
            value=float(latest.get("tracker_angle_deg", latest.get("track_mean", 0.0))),
            step=5.0,
            key=f"what_if_angle_{selected_zone}",
        )
        irrigation_on = st.toggle(
            "Riego activo",
            value=bool(latest.get("irrigation_on", False)),
            key=f"what_if_irrigation_{selected_zone}",
        )
        dose = st.slider(
            "Dosis riego mm/10min",
            min_value=0.0,
            max_value=3.5,
            value=1.0 if irrigation_on else 0.0,
            step=0.1,
            key=f"what_if_dose_{selected_zone}",
        )
        simulate = st.button("Simular siguiente estado", key=f"what_if_button_{selected_zone}")

    if not simulate:
        with col_result:
            st.caption("Ajusta una acción de placa/riego y simula el siguiente estado a +10 min.")
        return

    predicted = predict_dashboard_next_state(
        recent_window=recent_window,
        tracker_angle_deg=angle,
        irrigation_on=irrigation_on,
        irrigation_dose_mm=dose,
        model_path=WORLD_MODEL_LSTM_PATH,
        scalers_path=WORLD_MODEL_LSTM_SCALERS_PATH,
        device="cpu",
    )
    delta = build_prediction_delta_frame(latest, predicted)
    with col_result:
        fig = go.Figure()
        for metric, color in [("VWC", COLOR["green"]), ("Tsoil", COLOR["amber"]), ("PAR", COLOR["blue"]), ("GPOA", "#6d5bd0")]:
            fig.add_trace(go.Scatter(
                x=delta["momento"],
                y=delta[metric],
                mode="lines+markers",
                name=metric,
                line=dict(width=3, color=color),
            ))
        fig.update_layout(title="Predicción world model (+10 min)", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(_style_fig(fig, height=260), use_container_width=True)
        cards = [
            ("VWC pred.", f"{predicted.get('VWC_R1_sim', 0):.3f}", "fracción volumétrica", COLOR["green"]),
            ("Tsoil pred.", f"{predicted.get('Tsoil_R1_sim', 0):.1f} °C", "temperatura suelo R1", COLOR["amber"]),
            ("GPOA pred.", f"{predicted.get('GPOA_mean', 0):.0f}", "W/m² sobre panel", "#6d5bd0"),
            ("Último riego", f"{int(predicted.get('minutes_since_last_irr', 0))} min", "contador por regla", COLOR["blue"]),
        ]
        for col, (title, value, detail, color) in zip(st.columns(4), cards):
            col.markdown(_metric_card(title, value, detail, color), unsafe_allow_html=True)
```

- [ ] **Step 5: Render simulator in agronomy tab**

After `_render_lstm_model_status()`, add:

```python
    _render_lstm_what_if(selected_zone)
```

- [ ] **Step 6: Run source tests**

Run:

```powershell
python -m pytest sprint3\tests\test_tab_agronomia_source.py -q
```

Expected: PASS.

---

### Task 6: Keep Reward RL as Main Decision Signal

**Files:**
- Modify: `sprint3/tabs/tab_agronomia.py`
- Test: update `sprint3/tests/test_tab_agronomia_source.py`

- [ ] **Step 1: Add source test for Reward RL prominence**

Append:

```python
def test_agronomy_tab_promotes_reward_rl():
    assert "Reward RL" in SOURCE
    assert "componente energía" in SOURCE or "componente energia" in SOURCE
    assert "componente agronómica" in SOURCE or "componente agronomica" in SOURCE
```

- [ ] **Step 2: Update KPI cards**

In the first KPI card group, change card titles/details so they read:

```python
st.markdown(_metric_card("Reward RL", f"{rl_reward:.2f}", "alpha agronomía + beta energía", "#6d5bd0"), unsafe_allow_html=True)
st.markdown(_metric_card("Salud cultivo", f"{health:.2f}", "componente agronómica", COLOR["green"]), unsafe_allow_html=True)
st.markdown(_metric_card("Riesgo", f"{risk:.2f}", str(latest.get("stress_type", "estable")).replace("_", " "), COLOR["red"] if risk > 0.45 else COLOR["amber"]), unsafe_allow_html=True)
st.markdown(_metric_card("Riego/placa", f"{rl_angle:.0f}°", f"{action_label} · {panel_action_label}", COLOR["blue"]), unsafe_allow_html=True)
```

This replaces the current layout where crop health appears before reward.

- [ ] **Step 3: Run source test**

Run:

```powershell
python -m pytest sprint3\tests\test_tab_agronomia_source.py -q
```

Expected: PASS.

---

### Task 7: Full Verification and Visual QA

**Files:**
- All modified files above

- [ ] **Step 1: Run focused dashboard tests**

Run:

```powershell
python -m pytest sprint3\tests\test_dashboard_lstm.py sprint3\tests\test_data_loader.py sprint3\tests\test_app_tabs.py sprint3\tests\test_tab_agronomia_source.py -q
```

Expected: PASS.

- [ ] **Step 2: Run full sprint3 tests**

Run:

```powershell
python -m pytest sprint3\tests -q
```

Expected: PASS.

- [ ] **Step 3: Start dashboard locally**

Run:

```powershell
& 'C:\Users\dania\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m streamlit run sprint3\app.py --server.port 8501
```

Expected: dashboard starts at `http://localhost:8501`.

- [ ] **Step 4: Visual QA checklist**

Open `http://localhost:8501` and verify:

```text
Header still fits and says 6h + simulación 10min when world-model outputs exist.
There are five tabs.
Agronomía / RL loads without Streamlit exception.
Crop selector and zone selector appear.
Reward RL is the first KPI.
Model status strip appears with trained status and MAE values.
What-if controls appear without crowding.
Clicking Simular siguiente estado displays chart and predicted cards.
No text overlaps on desktop width.
The page still matches the current glass/card dashboard aesthetic.
```

- [ ] **Step 5: Inspect git status**

Run:

```powershell
git status --short
```

Expected: no `__pycache__` files; only source/tests/plan changes plus existing output artifacts.

---

## Self-Review

Spec coverage:
- Connects the existing agronomy tab into the main dashboard.
- Adds LSTM model status without exposing technical clutter.
- Adds a realistic what-if simulator for panel angle and irrigation.
- Keeps `Reward RL` as the principal decision metric.
- Preserves the current UI style and does not create a separate “LSTM” tab.

Placeholder scan:
- No `TBD`, `TODO`, or vague implementation-only steps remain.

Type consistency:
- Dashboard wrapper returns plain dictionaries/DataFrames.
- `data_loader` owns paths and cached data access.
- `tab_agronomia.py` owns Streamlit rendering only.
- `app.py` only wires tabs and initial data.
