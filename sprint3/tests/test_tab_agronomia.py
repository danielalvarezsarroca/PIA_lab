import pandas as pd

from tabs.tab_agronomia import (
    action_visual_state,
    crop_scene_svg,
    select_action_record,
)


def _risk_rows() -> pd.DataFrame:
    return pd.DataFrame({
        "Time": pd.to_datetime(["2026-05-03 10:00", "2026-05-03 12:00", "2026-05-03 18:00"]),
        "recommended_action": ["mantener", "regar", "aumentar_sombreado"],
        "action_label": ["Mantener manejo actual", "Activar riego", "Aumentar sombreado"],
        "stress_type": ["estable", "deficit_hidrico", "estres_termico"],
        "crop_risk_score": [0.0, 0.46, 0.34],
        "crop_health_score": [1.0, 0.54, 0.66],
        "IEC": [0.7, 0.62, 0.58],
        "VWC_S1_fraction": [0.28, 0.16, 0.27],
        "par_fraction_s1": [0.55, 0.64, 0.86],
        "Tair_WS": [20.0, 22.0, 31.0],
        "Tsoil_S1_mean": [18.0, 18.0, 25.0],
    })


def test_select_action_record_prefers_requested_action():
    row = select_action_record(_risk_rows(), "regar")

    assert row["recommended_action"] == "regar"
    assert row["stress_type"] == "deficit_hidrico"


def test_action_visual_state_maps_actions_to_scene_controls():
    state = action_visual_state("aumentar_sombreado")

    assert state["shade_opacity"] > 0.45
    assert state["water_opacity"] < 0.2
    assert state["accent"] == "#0a84ff"


def test_crop_scene_svg_represents_action_and_crop_label():
    row = select_action_record(_risk_rows(), "regar")

    svg = crop_scene_svg(row, crop_label="Lechuga")

    assert "Lechuga" in svg
    assert "Activar riego" in svg
    assert "animate" in svg
    assert "waterDrops" in svg
