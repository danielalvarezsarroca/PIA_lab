from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from agricultural_rules import (
    CROP_PROFILES,
    build_crop_risk_dataset,
    crop_calendar_for_date,
    generate_agricultural_rules_10min,
    write_agricultural_outputs,
)
from ten_min_pipeline import build_modeling_dataset_10min
from tests.test_ten_min_pipeline import _master_sample


def _stress_sample() -> pd.DataFrame:
    master = _master_sample()
    stress = pd.DataFrame({
        "Time": pd.to_datetime([
            "2026-05-03 13:00",
            "2026-05-03 13:10",
            "2026-05-03 13:20",
            "2026-05-03 14:00",
            "2026-05-03 14:10",
            "2026-05-03 18:00",
            "2026-05-03 18:10",
            "2026-05-03 18:20",
            "2026-05-03 19:00",
            "2026-05-03 19:10",
        ]),
        "tracker_angle_deg": [28.0, 29.0, 30.0, 22.0, 21.0, 5.0, 4.0, 3.0, 0.0, 0.0],
        "solar_elevation_deg": [72.0, 73.0, 72.0, 70.0, 69.0, 20.0, 18.0, 17.0, 8.0, 7.0],
        "solar_azimuth_deg": [180.0, 184.0, 188.0, 195.0, 198.0, 245.0, 248.0, 251.0, 260.0, 264.0],
        "clearsky_ghi_wm2": [900.0, 920.0, 910.0, 820.0, 810.0, 260.0, 240.0, 220.0, 120.0, 110.0],
        "air_temp_ext_avg_degc": [20.0, 20.5, 20.0, 31.0, 32.0, 16.0, 16.0, 15.5, 15.0, 15.0],
        "wind_speed_kmh": [8.0, 9.0, 8.5, 7.0, 7.0, 6.0, 5.0, 5.0, 42.0, 44.0],
        "precip_intensity_mm10min": [0.0, 0.0, 0.0, 0.0, 0.0, 2.4, 2.8, 2.2, 0.0, 0.0],
        "PAR_R1": [900.0, 930.0, 920.0, 860.0, 850.0, 500.0, 480.0, 470.0, 210.0, 205.0],
        "PAR_S1": [760.0, 780.0, 770.0, 740.0, 735.0, 90.0, 80.0, 85.0, 160.0, 155.0],
        "PAR_S2": [740.0, 760.0, 755.0, 725.0, 720.0, 95.0, 85.0, 90.0, 150.0, 148.0],
        "Tsoil_R1_mean": [18.0, 18.4, 18.1, 24.0, 24.4, 15.0, 15.0, 14.8, 14.0, 14.0],
        "Tsoil_S1_mean": [18.0, 18.5, 18.2, 25.0, 25.5, 14.0, 14.0, 13.8, 13.5, 13.5],
        "Tsoil_S2_mean": [18.1, 18.4, 18.3, 24.8, 25.0, 14.2, 14.2, 14.0, 13.6, 13.6],
        "VWC_R1_mean": [0.18, 0.17, 0.16, 0.27, 0.27, 0.38, 0.40, 0.39, 0.24, 0.24],
        "VWC_S1_mean": [0.17, 0.16, 0.15, 0.27, 0.27, 0.42, 0.43, 0.41, 0.25, 0.25],
        "VWC_S2_mean": [0.18, 0.17, 0.16, 0.26, 0.26, 0.40, 0.42, 0.41, 0.24, 0.24],
        "GPOA_mean": [850.0, 870.0, 860.0, 780.0, 770.0, 210.0, 200.0, 190.0, 80.0, 75.0],
        "ALBEDO_mean": [60.0, 62.0, 61.0, 58.0, 57.0, 25.0, 24.0, 23.0, 20.0, 19.0],
        "Delta_PAR_S1": [-140.0, -150.0, -150.0, -120.0, -115.0, -410.0, -400.0, -385.0, -50.0, -50.0],
        "Delta_Tsoil_S1": [0.0, 0.1, 0.0, 1.0, 1.1, -1.0, -1.0, -1.0, -0.5, -0.5],
        "Delta_VWC_S1": [-0.02, -0.03, -0.03, 0.0, 0.0, 0.04, 0.05, 0.04, 0.0, 0.0],
    })
    return pd.concat([master, stress], ignore_index=True)


def test_build_crop_risk_dataset_generates_modelable_agronomic_actions():
    model = build_modeling_dataset_10min(_stress_sample())

    risk = build_crop_risk_dataset(model, crop_type="lechuga")

    assert {"crop_type", "crop_risk_score", "crop_health_score", "stress_type", "recommended_action"}.issubset(risk.columns)
    assert risk["crop_risk_score"].between(0, 1).all()
    assert risk["crop_health_score"].between(0, 1).all()
    assert "activar_riego" in set(risk["recommended_action"])
    assert "pausar_riego" in set(risk["recommended_action"])
    assert "aumentar_sombreado" in set(risk["recommended_action"])
    assert "posicion_segura" in set(risk["recommended_action"])


def test_crop_risk_dataset_adds_irrigation_actuator_outputs():
    model = build_modeling_dataset_10min(_stress_sample())

    risk = build_crop_risk_dataset(model, crop_type="lechuga")

    expected_columns = {
        "irrigation_mode",
        "irrigation_active",
        "irrigation_mm_10min",
        "irrigation_duration_min",
        "irrigation_vwc_delta_est",
        "irrigation_tsoil_delta_est_c",
    }
    assert expected_columns.issubset(risk.columns)

    active_irrigation = risk[risk["crop_management_action"].eq("activar_riego")]
    assert not active_irrigation.empty
    assert active_irrigation["irrigation_mode"].eq("drip").all()
    assert active_irrigation["irrigation_active"].all()
    assert active_irrigation["irrigation_mm_10min"].gt(0).all()
    assert active_irrigation["irrigation_duration_min"].gt(0).all()
    assert active_irrigation["irrigation_vwc_delta_est"].gt(0).all()
    assert active_irrigation["irrigation_tsoil_delta_est_c"].lt(0).all()

    paused_irrigation = risk[risk["crop_management_action"].eq("pausar_riego")]
    assert not paused_irrigation.empty
    assert paused_irrigation["irrigation_mode"].eq("paused").all()
    assert not paused_irrigation["irrigation_active"].any()
    assert paused_irrigation["irrigation_mm_10min"].eq(0).all()
    assert paused_irrigation["irrigation_duration_min"].eq(0).all()

    joint_actions = risk[risk["irrigation_active"] & risk["panel_action"].ne("mantener_placas")]
    assert not joint_actions.empty


def test_crop_risk_dataset_can_score_independent_crop_zones():
    model = build_modeling_dataset_10min(_stress_sample())

    risk_s1 = build_crop_risk_dataset(model, crop_type="lechuga", crop_zone="S1")
    risk_s2 = build_crop_risk_dataset(model, crop_type="patata", crop_zone="S2")

    assert risk_s1["crop_zone"].eq("S1").all()
    assert risk_s2["crop_zone"].eq("S2").all()
    assert risk_s1["crop_type"].eq("lechuga").all()
    assert risk_s2["crop_type"].eq("patata").all()

    expected_s2_vwc = model["VWC_S2_mean"].astype(float)
    expected_s2_vwc = expected_s2_vwc.where(expected_s2_vwc <= 1.5, expected_s2_vwc / 100).clip(0, 1)

    assert np.allclose(risk_s2["VWC_crop_zone_fraction"], expected_s2_vwc.round(4))
    assert np.allclose(risk_s2["Tsoil_crop_zone_mean"], model["Tsoil_S2_mean"].round(4))
    assert np.allclose(risk_s2["ePAR_crop_zone_mean"], model["ePAR_S2_mean"].round(4))
    assert not risk_s1["VWC_crop_zone_fraction"].equals(risk_s2["VWC_crop_zone_fraction"])


def test_crop_risk_dataset_imputes_missing_crop_zone_sensors_with_traceable_sources():
    model = build_modeling_dataset_10min(_stress_sample())
    model = model.drop(columns=["VWC_S2_mean", "Tsoil_S2_mean", "ePAR_S2_mean"])

    risk = build_crop_risk_dataset(model, crop_type="patata", crop_zone="S2")

    assert {
        "VWC_crop_zone_source",
        "Tsoil_crop_zone_source",
        "ePAR_crop_zone_source",
    }.issubset(risk.columns)
    assert risk["VWC_crop_zone_fraction"].notna().all()
    assert risk["Tsoil_crop_zone_mean"].notna().all()
    assert risk["ePAR_crop_zone_mean"].notna().all()
    assert risk["VWC_crop_zone_source"].eq("VWC_S1_mean_proxy_under_panel").all()
    assert risk["Tsoil_crop_zone_source"].eq("Tsoil_S1_mean_proxy_under_panel").all()
    assert risk["ePAR_crop_zone_source"].eq("ePAR_S1_mean_proxy_under_panel").all()


def test_crop_risk_dataset_rejects_unknown_crop_zone():
    model = build_modeling_dataset_10min(_stress_sample())

    with pytest.raises(ValueError, match="unknown crop_zone"):
        build_crop_risk_dataset(model, crop_type="lechuga", crop_zone="S3")


def test_generate_agricultural_rules_10min_summarizes_actions_with_support():
    model = build_modeling_dataset_10min(_stress_sample())
    risk = build_crop_risk_dataset(model, crop_type="brocoli")

    rules = generate_agricultural_rules_10min(risk, crop_type="brocoli")

    assert not rules.empty
    assert {"tipo", "cultivo", "accion", "regla", "soporte_obs", "riesgo_mediano", "comentario"}.issubset(rules.columns)
    assert {"activar_riego", "pausar_riego", "aumentar_sombreado", "posicion_segura"}.issubset(set(rules["accion"]))
    assert rules["regla"].str.contains("brocoli").any()
    assert "fuentes" in rules.columns
    assert rules["fuentes"].str.contains("FAO-56|RuralCat|Extension", regex=True).any()
    assert rules["comentario"].str.contains("regla experta", case=False).all()


def test_crop_profiles_document_sources_and_dataset_variables():
    lechuga = CROP_PROFILES["lechuga"]

    assert {"sources", "dataset_variables", "method_note"}.issubset(lechuga)
    assert {"VWC_S1_mean", "Tsoil_S1_mean", "Tair_WS", "ePAR_S1_mean"}.issubset(lechuga["dataset_variables"])
    assert any("FAO" in source["name"] for source in lechuga["sources"])
    assert any(source["url"].startswith("https://") for source in lechuga["sources"])
    assert "no aprendida por RL" in lechuga["method_note"]


def test_crop_profiles_include_calendar_and_visual_traits():
    for crop_type in ["lechuga", "brocoli", "tomate", "pimiento", "fresa", "espinaca", "cebolla", "patata"]:
        profile = CROP_PROFILES[crop_type]

        assert {"crop_history", "growth_stages", "visual_traits"}.issubset(profile)
        assert profile["crop_history"]["harvest_days"] > 0
        assert profile["growth_stages"]
        assert profile["visual_traits"]["shape"]
        assert "air_temp_warn_high_c" in profile


def test_crop_profiles_include_requirements_for_decision_dashboard():
    for crop_type in ["lechuga", "brocoli", "cebolla", "patata", "tomate"]:
        profile = CROP_PROFILES[crop_type]

        assert {"water_requirements", "fertilizer_requirements", "light_requirements", "stage_requirements"}.issubset(profile)

        water = profile["water_requirements"]
        assert len(water["weekly_mm_range"]) == 2
        assert water["weekly_mm_range"][0] < water["weekly_mm_range"][1]
        assert water["root_depth_cm"] > 0
        assert water["irrigation_sensitivity"]

        fertilizer = profile["fertilizer_requirements"]
        assert {"nitrogen_kg_ha", "phosphorus_kg_ha", "potassium_kg_ha", "note"}.issubset(fertilizer)
        assert len(fertilizer["nitrogen_kg_ha"]) == 2

        light = profile["light_requirements"]
        assert len(light["par_fraction_target_range"]) == 2
        assert light["shade_strategy"]

        assert len(profile["stage_requirements"]) == len(profile["growth_stages"])
        for requirement in profile["stage_requirements"]:
            assert {"stage", "vwc_target_range", "par_fraction_target_range", "management_note"}.issubset(requirement)


def test_crop_calendar_uses_history_and_flags_harvest():
    tomato = crop_calendar_for_date("tomate", "2025-07-20")

    assert tomato["display_name"] == "Tomate"
    assert tomato["current_stage"]["name"] == "Crecimiento vegetativo"
    assert not tomato["ready_to_harvest"]
    assert tomato["days_to_harvest"] > 0

    ready = crop_calendar_for_date("tomate", "2025-09-20")

    assert ready["ready_to_harvest"]
    assert ready["days_to_harvest"] == 0
    assert ready["current_stage"]["name"] == "Listo para recoger"


def test_write_agricultural_outputs_creates_crop_files(tmp_path: Path):
    model = build_modeling_dataset_10min(_stress_sample())
    risk = build_crop_risk_dataset(model, crop_type="lechuga")
    rules = generate_agricultural_rules_10min(risk, crop_type="lechuga")

    paths = write_agricultural_outputs(tmp_path, risk, rules, CROP_PROFILES)

    assert paths["crop_risk"].exists()
    assert paths["agricultural_rules"].exists()
    assert paths["crop_profiles"].exists()
    assert pd.read_csv(paths["agricultural_rules"])["accion"].str.len().gt(0).all()
    profile_text = paths["crop_profiles"].read_text(encoding="utf-8")
    assert "reglas expertas referenciadas" in profile_text
    assert "no son una recompensa RL aprendida" in profile_text
