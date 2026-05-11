from types import SimpleNamespace

import pandas as pd

from agricultural_rules import CROP_PROFILES, crop_calendar_for_date
from tabs import tab_agronomia, tab_estado


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}


def test_selected_crop_type_uses_single_shared_state(monkeypatch):
    fake_st = FakeStreamlit()
    monkeypatch.setattr(tab_estado, "st", fake_st)
    monkeypatch.setattr(tab_estado, "CROP_PROFILES", {"lechuga": {}, "brocoli": {}})

    assert tab_estado._selected_crop_type() == "lechuga"

    fake_st.session_state["selected_crop_type"] = "brocoli"
    assert tab_estado._selected_crop_type() == "brocoli"

    fake_st.session_state["selected_crop_type"] = ["lechuga", "brocoli"]
    assert tab_estado._selected_crop_type() == "lechuga"


def test_selected_crop_type_can_be_scoped_by_zone(monkeypatch):
    fake_st = FakeStreamlit()
    fake_st.session_state["selected_crop_zone"] = "S2"
    fake_st.session_state["selected_crop_type_s1"] = "lechuga"
    fake_st.session_state["selected_crop_type_s2"] = "patata"
    monkeypatch.setattr(tab_estado, "st", fake_st)
    monkeypatch.setattr(tab_estado, "CROP_PROFILES", {"lechuga": {}, "patata": {}})

    assert tab_estado._selected_crop_zone() == "S2"
    assert tab_estado._selected_crop_type() == "patata"


def test_selected_crop_risk_loads_selected_crop_policy_inputs(monkeypatch):
    fake_st = FakeStreamlit()
    fake_st.session_state["selected_crop_zone"] = "S2"
    fake_st.session_state["selected_crop_type_s2"] = "brocoli"
    monkeypatch.setattr(tab_estado, "st", fake_st)
    monkeypatch.setattr(tab_estado, "CROP_PROFILES", {"lechuga": {}, "brocoli": {}})

    def fake_load_crop_risk(crop_type, crop_zone="S1"):
        return pd.DataFrame({"crop_type": [crop_type], "crop_zone": [crop_zone], "risk": [0.7]})

    monkeypatch.setattr(tab_estado, "load_crop_risk_for_crop", fake_load_crop_risk)

    fallback = pd.DataFrame({"crop_type": ["lechuga"], "risk": [0.1]})
    selected = tab_estado._selected_crop_risk(fallback)

    assert selected["crop_type"].tolist() == ["brocoli"]
    assert selected["crop_zone"].tolist() == ["S2"]
    assert selected["risk"].tolist() == [0.7]


def test_agronomia_crop_selector_uses_profile_catalog(monkeypatch):
    monkeypatch.setattr(tab_agronomia, "CROP_PROFILES", {"lechuga": {}, "brocoli": {}})

    df_only_loaded_crop = pd.DataFrame({"crop_type": ["lechuga"]})

    assert tab_agronomia._available_crop_options(df_only_loaded_crop) == ["lechuga", "brocoli"]


def test_agronomia_default_crop_type_uses_zone_specific_state(monkeypatch):
    fake_st = FakeStreamlit()
    fake_st.session_state["selected_crop_type_s1"] = "lechuga"
    fake_st.session_state["selected_crop_type_s2"] = "patata"
    monkeypatch.setattr(tab_agronomia, "st", fake_st)

    assert tab_agronomia._default_crop_type(["lechuga", "patata"], "S2") == "patata"


def test_crop_scene_svg_names_selected_crop(monkeypatch):
    monkeypatch.setattr(tab_agronomia, "CROP_PROFILES", {"brocoli": {"display_name": "Brocoli"}})

    svg = tab_agronomia._crop_scene_svg(
        management_action="activar_riego",
        panel_action="mantener_placas",
        health=0.5,
        risk=0.6,
        crop_type="brocoli",
    )

    assert "Cultivo: Brocoli" in svg
    assert "riesgo" not in svg.lower()


def test_crop_scene_svg_renders_new_crop_shapes():
    onion_svg = tab_agronomia._crop_scene_svg(
        management_action="sin_manejo_directo",
        panel_action="mantener_placas",
        health=0.82,
        risk=0.13,
        crop_type="cebolla",
    )
    potato_svg = tab_agronomia._crop_scene_svg(
        management_action="sin_manejo_directo",
        panel_action="mantener_placas",
        health=0.82,
        risk=0.13,
        crop_type="patata",
    )

    assert "Cultivo: Cebolla" in onion_svg
    assert "data-crop-shape='allium'" in onion_svg
    assert "Cultivo: Patata" in potato_svg
    assert "data-crop-shape='tuber'" in potato_svg


def test_crop_calendar_view_model_keeps_harvest_status_visible():
    calendar = crop_calendar_for_date("tomate", "2025-07-20")

    view = tab_agronomia._crop_calendar_view_model(calendar)

    assert calendar["harvest_at"] == "2025-09-13"
    assert view["harvest_detail"] == "hasta cosecha"
    assert view["harvest_value"] == "55 dias"
    assert view["stage_name"] == "Crecimiento vegetativo"
    assert view["progress_pct"] == 42


def test_crop_requirements_view_model_exposes_crop_needs():
    calendar = crop_calendar_for_date("patata", "2025-08-18")

    cards = tab_agronomia._crop_requirements_view_model(CROP_PROFILES["patata"], calendar)
    cards_by_title = {card["title"]: card for card in cards}

    assert set(cards_by_title) == {"Agua", "Abonado", "Luz", "Fase actual"}
    assert "mm/sem" in cards_by_title["Agua"]["value"]
    assert "raiz 45 cm" in cards_by_title["Agua"]["detail"]
    assert "kg/ha" in cards_by_title["Abonado"]["detail"]
    assert "PAR" in cards_by_title["Luz"]["value"]
    assert cards_by_title["Fase actual"]["value"] == calendar["current_stage"]["name"]
    assert "VWC" in cards_by_title["Fase actual"]["detail"]
