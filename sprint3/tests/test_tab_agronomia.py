import sys
import types

import pandas as pd

sys.modules.setdefault(
    "data_loader",
    types.SimpleNamespace(
        load_agricultural_rules_for_crop=lambda *args, **kwargs: pd.DataFrame(),
        load_crop_risk_for_crop=lambda *args, **kwargs: pd.DataFrame(),
        load_rl_policy_for_crop=lambda *args, **kwargs: pd.DataFrame(),
        parse_tracker_name=lambda name: name,
    ),
)

from tabs.tab_agronomia import (
    _external_action_card_view_model,
    _panel_action_card_view_model,
    _timeline_view_model,
)


def test_timeline_view_model_keeps_10_minute_records_and_defaults_to_latest():
    frame = pd.DataFrame(
        {
            "Time": pd.to_datetime(
                [
                    "2026-05-01 08:20:00",
                    "2026-05-01 08:00:00",
                    "2026-05-01 08:10:00",
                ]
            ),
            "crop_health_score": [0.82, 0.78, 0.80],
            "crop_risk_score": [0.12, 0.18, 0.15],
        }
    )

    timeline, labels, selected_idx = _timeline_view_model(frame)

    assert labels == ["2026-05-01 08:00", "2026-05-01 08:10", "2026-05-01 08:20"]
    assert selected_idx == 2
    assert timeline["crop_health_score"].tolist() == [0.78, 0.80, 0.82]


def test_external_action_card_view_model_describes_preventive_10_minute_dose():
    row = pd.Series(
        {
            "crop_management_action": "riego_preventivo",
            "irrigation_active": True,
            "irrigation_mm_10min": 1.2,
            "irrigation_duration_min": 6,
        }
    )

    card = _external_action_card_view_model(row)

    assert card["title"] == "Acción externa"
    assert card["value"] == "Riego preventivo"
    assert "1.2 mm/10min" in card["detail"]
    assert "6 min" in card["detail"]
    assert card["color"]


def test_external_action_card_view_model_reports_paused_irrigation():
    row = pd.Series(
        {
            "crop_management_action": "pausar_riego",
            "irrigation_active": False,
            "irrigation_mode": "paused",
            "irrigation_mm_10min": 0,
            "irrigation_duration_min": 0,
        }
    )

    card = _external_action_card_view_model(row)

    assert card["title"] == "Acción externa"
    assert card["value"] == "Pausar riego"
    assert card["detail"] == "riego pausado · sin aporte de agua"
    assert card["color"] == "#6e6e73"


def test_panel_action_card_view_model_describes_panel_action_separately():
    row = pd.Series(
        {
            "panel_action": "aumentar_sombreado",
            "rl_angle_deg": 35,
            "tracking_regime": "anti-estres",
        }
    )

    card = _panel_action_card_view_model(row)

    assert card["title"] == "Acción placas"
    assert card["value"] == "Aumentar sombreado"
    assert "35°" in card["detail"]
    assert "anti-estres" in card["detail"]
