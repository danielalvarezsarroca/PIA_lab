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
    assert bool(result.iloc[-2]["irrigation_on"]) is True
    assert result.iloc[-1]["tracker_angle_deg"] == 15.0


def test_rollout_without_irrigation_applies_drydown_to_vwc():
    def flat_predictor(recent_window, action):
        previous = recent_window.iloc[-1]
        return {
            "GPOA_mean": 850.0,
            "ALBEDO_mean": 0.2,
            "Delta_PAR_S1": 0.2,
            "VWC_R1_sim": float(previous["VWC_R1_sim"]),
            "minutes_since_last_irr": float(previous["minutes_since_last_irr"]),
            "Delta_VWC_S1_sim": float(previous["Delta_VWC_S1_sim"]),
            "Tsoil_R1_sim": 27.0,
            "Delta_Tsoil_S1_sim": 0.3,
        }

    history = _history()
    history.loc[:, "VWC_R1_sim"] = 0.25
    history.loc[:, "Delta_VWC_S1_sim"] = 0.0
    actions = [
        {"tracker_angle_deg": 10.0, "irrigation_on": False, "irrigation_dose_mm": 0.0},
        {"tracker_angle_deg": 10.0, "irrigation_on": True, "irrigation_dose_mm": 1.5},
    ]

    result = rollout_with_policy(history, actions, predictor=flat_predictor)

    no_irrigation_vwc = result.iloc[-2]["VWC_R1_sim"]
    irrigated_vwc = result.iloc[-1]["VWC_R1_sim"]
    assert no_irrigation_vwc < 0.25
    assert irrigated_vwc > no_irrigation_vwc
    assert result.iloc[-2]["minutes_since_last_irr"] > history.iloc[-1]["minutes_since_last_irr"]
    assert result.iloc[-1]["minutes_since_last_irr"] == 0
