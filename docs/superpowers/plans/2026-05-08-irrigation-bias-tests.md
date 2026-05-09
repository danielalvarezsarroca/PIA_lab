# Irrigation Bias Tests and RL Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add regression tests for irrigation bias and update RL policy metadata to document factorized joint actions without expanding scope.

**Architecture:** Add synthetic scenario tests in agricultural rules and integration-focused tests in RL policy. Extend RL policy metadata with an explicit `action_factorization` block that documents joint action semantics.

**Tech Stack:** Python, pytest, pandas

---

### Task 1: Add irrigation bias tests in agricultural rules

**Files:**
- Modify: `sprint3/tests/test_agricultural_rules.py`

- [ ] **Step 1: Write the failing test cases**

```python
def _irrigation_bias_sample() -> pd.DataFrame:
    return pd.DataFrame({
        "Time": pd.to_datetime([
            "2026-05-03 14:00",  # day, critical VWC
            "2026-05-03 23:10",  # night, critical VWC
            "2026-05-03 13:20",  # day, low but not critical
            "2026-05-03 15:00",  # day, normal VWC + high temp
            "2026-05-03 16:00",  # day, rain/high VWC
            "2026-05-03 12:30",  # day, low VWC + active panel action
        ]),
        "hour_of_day": [14, 23, 13, 15, 16, 12],
        "solar_elevation_deg": [60.0, -12.0, 55.0, 65.0, 50.0, 58.0],
        "track_mean": [25.0, 0.0, 30.0, 28.0, 26.0, 10.0],
        "tracking_regime": ["tracking"] * 6,
        "energy_score": [0.7, 0.3, 0.68, 0.72, 0.5, 0.6],
        "crop_score": [0.4, 0.4, 0.6, 0.8, 0.6, 0.55],
        "Tair_WS": [28.0, 16.0, 26.0, 34.0, 24.0, 29.0],
        "Tsoil_S1_mean": [22.0, 14.0, 21.0, 28.0, 22.0, 22.0],
        "VWC_S1_mean": [0.17, 0.17, 0.20, 0.26, 0.42, 0.19],
        "ePAR_S1_mean": [700.0, 0.0, 640.0, 680.0, 520.0, 690.0],
        "ePAR_R1_mean": [900.0, 0.0, 820.0, 860.0, 700.0, 880.0],
        "wind_speed_kmh": [5.0, 4.0, 6.0, 5.0, 5.0, 5.0],
        "precip_intensity_mm10min": [0.0, 0.0, 0.0, 0.0, 2.4, 0.0],
    })


def test_irrigation_bias_scenarios_do_not_depend_only_on_hour():
    model = build_modeling_dataset_10min(_irrigation_bias_sample())
    risk = build_crop_risk_dataset(model, crop_type="lechuga")

    day_critical = risk.iloc[0]
    night_critical = risk.iloc[1]
    day_low = risk.iloc[2]
    day_hot_normal = risk.iloc[3]
    day_rain_or_high = risk.iloc[4]
    day_joint = risk.iloc[5]

    assert day_critical["irrigation_active"] is True
    assert night_critical["irrigation_active"] is True

    assert day_low["crop_management_action"] in {"activar_riego", "riego_preventivo", "sin_manejo_directo"}
    assert day_low["water_deficit"] is True

    assert day_hot_normal["water_deficit"] is False
    assert day_hot_normal["irrigation_active"] is False

    assert day_rain_or_high["water_excess"] is True
    assert day_rain_or_high["irrigation_active"] is False

    assert day_joint["irrigation_active"] is True
    assert day_joint["panel_action"] != "mantener_placas"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.venv/bin/python -m pytest sprint3/tests/test_agricultural_rules.py::test_irrigation_bias_scenarios_do_not_depend_only_on_hour -q`
Expected: FAIL (logic may be too time-dependent or missing panel action coexistence)

- [ ] **Step 3: Implement minimal logic adjustments if needed**

If failures show bias, adjust irrigation logic in `sprint3/agricultural_rules.py`:

```python
def _crop_management_action(row: pd.Series) -> str:
    if bool(row.get("water_excess", False)):
        return "pausar_riego"
    if bool(row.get("water_deficit", False)) and bool(row.get("heat_stress", False)):
        return "riego_preventivo"
    if bool(row.get("water_deficit", False)):
        return "activar_riego"
    if bool(row.get("cold_stress", False)):
        return "proteccion_frio"
    return "sin_manejo_directo"
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `.venv/bin/python -m pytest sprint3/tests/test_agricultural_rules.py::test_irrigation_bias_scenarios_do_not_depend_only_on_hour -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sprint3/tests/test_agricultural_rules.py sprint3/agricultural_rules.py
git commit -m "test: add irrigation bias scenarios"
```

### Task 2: Add RL integration tests for factorized joint action

**Files:**
- Modify: `sprint3/tests/test_rl_policy.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_rl_policy_metadata_exposes_factorized_joint_action(tmp_path):
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    policy = build_offline_rl_policy(model, crop_risk)

    paths = write_rl_policy_outputs(tmp_path, policy)
    metadata = json.loads(paths["rl_policy_metadata"].read_text(encoding="utf-8"))

    factorization = metadata["action_factorization"]
    assert factorization["type"] == "factorized_joint_action"
    assert "panel_action" in factorization["dimensions"]
    assert "irrigation_action" in factorization["dimensions"]
    assert "one joint decision" in factorization["description"].lower()
    assert "timestep" in factorization["reward_scope"].lower()


def test_rl_policy_joint_action_keeps_irrigation_and_panel_dimensions():
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    policy = build_offline_rl_policy(model, crop_risk)

    assert "panel_action" in policy.columns
    assert "irrigation_active" in policy.columns
    assert (policy["irrigation_active"] & policy["panel_action"].ne("mantener_placas")).any()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest sprint3/tests/test_rl_policy.py::test_rl_policy_metadata_exposes_factorized_joint_action -q`
Expected: FAIL (missing metadata block)

- [ ] **Step 3: Update RL policy metadata**

Modify `write_rl_policy_outputs` in `sprint3/rl_policy.py`:

```python
        "action_factorization": {
            "type": "factorized_joint_action",
            "description": (
                "Each timestep selects one joint decision composed of independent actuator dimensions: "
                "panel_action and irrigation_action."
            ),
            "dimensions": ["panel_action", "irrigation_action"],
            "rationale": (
                "Panel movement and irrigation affect different actuators, so they can be active in the same "
                "timestep while still being evaluated by a single shared reward."
            ),
            "reward_scope": (
                "The reward evaluates the combined agronomic and energy effect of the full joint action "
                "at each timestep."
            ),
        },
```

- [ ] **Step 4: Run the RL tests to verify they pass**

Run: `.venv/bin/python -m pytest sprint3/tests/test_rl_policy.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sprint3/tests/test_rl_policy.py sprint3/rl_policy.py
git commit -m "test: validate factorized joint action metadata"
```

### Task 3: Full test suite verification

**Files:**
- Test: `sprint3/tests`

- [ ] **Step 1: Run targeted tests**

Run: `.venv/bin/python -m pytest sprint3/tests/test_agricultural_rules.py -q`
Expected: PASS

- [ ] **Step 2: Run RL policy tests**

Run: `.venv/bin/python -m pytest sprint3/tests/test_rl_policy.py -q`
Expected: PASS

- [ ] **Step 3: Run full sprint3 test suite**

Run: `.venv/bin/python -m pytest sprint3/tests -q`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add sprint3/tests/test_agricultural_rules.py sprint3/tests/test_rl_policy.py sprint3/rl_policy.py
git commit -m "test: cover irrigation bias and RL metadata"
```
