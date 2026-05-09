# Mini-spec: Irrigation Bias Tests and RL Metadata

## Goal
Add regression tests that prove irrigation decisions are driven by soil moisture risk rather than time-of-day bias, and document factorized joint actions in RL policy metadata.

## Scope
- Tests in `sprint3/tests/test_agricultural_rules.py` for day/night irrigation behavior and blocking rules.
- Tests in `sprint3/tests/test_rl_policy.py` for factorized actions, coexistence of irrigation with panel action, trajectories including night/day irrigation states, and metadata validation.
- Update `write_rl_policy_outputs` to emit an explicit `action_factorization` field in metadata.

## Non-goals
- New agronomic features or changes unrelated to irrigation bias.
- Refactors not required by the tests.

## Test Scenarios (Synthetic)
- Day + VWC critical -> `irrigation_active=True`.
- Night + VWC critical -> `irrigation_active=True`.
- Day + VWC low (non-critical) -> can prefer preventive/night bias but not solely time-dependent.
- Day + VWC normal + high temperature -> no irrigation solely for heat.
- Rain or VWC high -> irrigation paused/blocked.
- Day + irrigation active + panel action active -> coexists.

## RL Metadata
Emit `action_factorization` with:
- `type == "factorized_joint_action"`
- `dimensions` includes `panel_action` and `irrigation_action`
- Description/rationale/reward_scope clarify a single joint decision per timestep

## Acceptance Criteria
- New tests pass without brittle value assertions.
- RL metadata includes `action_factorization` as explicit source of truth.
- If tests reveal a day/night irrigation bias, adjust irrigation logic to prioritize moisture risk.
