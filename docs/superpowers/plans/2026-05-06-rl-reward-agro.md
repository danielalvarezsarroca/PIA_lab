# RL Reward IEC + Penalización Agronómica Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ajustar el reward RL para usar IEC como base y aplicar una penalización fuerte cuando haya daño agronómico crítico según cultivo.

**Architecture:** Mantener el pipeline RL offline actual, pero calcular `rl_reward` como IEC menos una penalización por daño. El daño se determina con umbrales críticos por cultivo ya definidos en `CROP_PROFILES` (sin nuevas fuentes). La penalización se registra en metadatos.

**Tech Stack:** Python, pandas, pytest, Streamlit (solo para visualización).

---

## File Structure

**Modify**
- `sprint3/rl_policy.py`: aplicar penalización de daño al reward y exportar metadatos.
- `sprint3/tests/test_rl_policy.py`: añadir tests para penalización de daño.

## Task 1: Añadir penalización por daño en el reward RL

**Files:**
- Modify: `sprint3/rl_policy.py`
- Test: `sprint3/tests/test_rl_policy.py`

- [ ] **Step 1: Write the failing test**

```python
def test_rl_reward_penalizes_critical_crop_damage():
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    # Force a critical damage row
    crop_risk = crop_risk.copy()
    crop_risk.loc[crop_risk.index[0], "water_deficit"] = True
    crop_risk.loc[crop_risk.index[0], "heat_stress"] = True
    crop_risk.loc[crop_risk.index[0], "crop_risk_score"] = 0.95

    policy = build_offline_rl_policy(model, crop_risk)

    assert (policy["rl_reward"] < 0.8).any()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest sprint3/tests/test_rl_policy.py::test_rl_reward_penalizes_critical_crop_damage -v`

Expected: FAIL (no penalización aplicada, reward sigue sin castigo).

- [ ] **Step 3: Write minimal implementation**

In `sprint3/rl_policy.py`, add helpers and update reward calculation:

```python
def _is_critical_damage(row: pd.Series) -> bool:
    return bool(
        row.get("water_deficit", False)
        or row.get("water_excess", False)
        or row.get("heat_stress", False)
        or row.get("cold_stress", False)
        or row.get("excess_radiation", False)
    )


def _apply_damage_penalty(reward: pd.Series, damage: pd.Series) -> pd.Series:
    penalty = 0.35
    return (reward - penalty * damage.astype(float)).clip(0, 1)
```

Then in `_merged_reward_frame` replace reward assignment:

```python
reward_base = (
    0.55 * df["energy_component"]
    + 0.35 * df["agronomic_component"]
    + 0.10 * pd.to_numeric(df["IEC"], errors="coerce").fillna(0).clip(0, 1)
).clip(0, 1)
damage_flag = df.apply(_is_critical_damage, axis=1)
reward = _apply_damage_penalty(reward_base, damage_flag)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest sprint3/tests/test_rl_policy.py::test_rl_reward_penalizes_critical_crop_damage -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sprint3/rl_policy.py sprint3/tests/test_rl_policy.py
git commit -m "feat: penalize rl reward on agronomic damage"
```

## Task 2: Documentar penalización en metadatos de policy

**Files:**
- Modify: `sprint3/rl_policy.py`
- Test: `sprint3/tests/test_rl_policy.py`

- [ ] **Step 1: Write the failing test**

```python
def test_rl_policy_metadata_includes_damage_penalty(tmp_path):
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga")
    policy = build_offline_rl_policy(model, crop_risk)

    paths = write_rl_policy_outputs(tmp_path, policy)
    metadata = (tmp_path / "rl_policy_metadata.json").read_text(encoding="utf-8")

    assert "penalty_damage" in metadata
    assert "IEC" in metadata
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest sprint3/tests/test_rl_policy.py::test_rl_policy_metadata_includes_damage_penalty -v`

Expected: FAIL (no metadata sobre penalización).

- [ ] **Step 3: Write minimal implementation**

In `write_rl_policy_outputs`, update metadata:

```python
metadata = {
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "source": "offline_rl_tabular_masterdataset",
    "reward_base": "IEC",
    "penalty_damage": "fixed_0.35_on_critical_agronomic_damage",
    "note": (
        "Politica RL tabular offline para demo, derivada del masterdataset. "
        "Reward = IEC - penalizacion por dano agronomico critico."
    ),
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest sprint3/tests/test_rl_policy.py::test_rl_policy_metadata_includes_damage_penalty -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sprint3/rl_policy.py sprint3/tests/test_rl_policy.py
git commit -m "docs: add rl damage penalty metadata"
```

---

## Self-Review Checklist

- Spec coverage: reward IEC base + penalización fuerte por daño → Task 1
- Metadatos y trazabilidad → Task 2
- No placeholders → OK
- Consistencia de nombres → `penalty_damage`, `reward_base`, `IEC`

---

Plan complete and saved to `docs/superpowers/plans/2026-05-06-rl-reward-agro.md`. Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration
2. Inline Execution - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
