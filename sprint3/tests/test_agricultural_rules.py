from pathlib import Path

import pandas as pd

from agricultural_rules import (
    CROP_PROFILES,
    build_crop_risk_dataset,
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
    assert "regar" in set(risk["recommended_action"])
    assert "pausar_riego" in set(risk["recommended_action"])
    assert "aumentar_sombreado" in set(risk["recommended_action"])
    assert "posicion_segura" in set(risk["recommended_action"])


def test_generate_agricultural_rules_10min_summarizes_actions_with_support():
    model = build_modeling_dataset_10min(_stress_sample())
    risk = build_crop_risk_dataset(model, crop_type="brocoli")

    rules = generate_agricultural_rules_10min(risk, crop_type="brocoli")

    assert not rules.empty
    assert {"tipo", "cultivo", "accion", "regla", "soporte_obs", "riesgo_mediano", "comentario"}.issubset(rules.columns)
    assert {"regar", "pausar_riego", "aumentar_sombreado", "posicion_segura"}.issubset(set(rules["accion"]))
    assert rules["regla"].str.contains("brocoli").any()


def test_write_agricultural_outputs_creates_crop_files(tmp_path: Path):
    model = build_modeling_dataset_10min(_stress_sample())
    risk = build_crop_risk_dataset(model, crop_type="lechuga")
    rules = generate_agricultural_rules_10min(risk, crop_type="lechuga")

    paths = write_agricultural_outputs(tmp_path, risk, rules, CROP_PROFILES)

    assert paths["crop_risk"].exists()
    assert paths["agricultural_rules"].exists()
    assert paths["crop_profiles"].exists()
    assert pd.read_csv(paths["agricultural_rules"])["accion"].str.len().gt(0).all()
