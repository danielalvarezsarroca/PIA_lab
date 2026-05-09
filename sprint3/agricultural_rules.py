from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DATASET_VARIABLES_USED = [
    "VWC_S1_mean",
    "Tsoil_S1_mean",
    "Tair_WS",
    "ePAR_S1_mean",
    "ePAR_R1_mean",
    "wind_speed_kmh",
    "precip_intensity_mm10min",
]

REFERENCE_SOURCES = {
    "FAO-56": {
        "name": "FAO-56 crop evapotranspiration",
        "url": "https://www.fao.org/3/X0490E/x0490e00.htm",
        "use": "Marco tecnico para necesidades hidricas de cultivo mediante ETo, Kc y ETc.",
    },
    "RuralCat": {
        "name": "RuralCat recomanacions de reg",
        "url": "https://ruralcat.gencat.cat/web/guest/eines/recomanacions-de-reg",
        "use": "Referencia local catalana para recomendaciones de riego basadas en estaciones agroclimaticas.",
    },
    "Illinois Extension lettuce": {
        "name": "University of Illinois Extension - Lettuce",
        "url": "https://extension.illinois.edu/gardening/lettuce",
        "use": "Rangos termicos de cultivo fresco para lechuga y sensibilidad a calor.",
    },
    "Oregon State Extension broccoli": {
        "name": "Oregon State University Extension - Broccoli",
        "url": "https://extension.oregonstate.edu/imported-publication/broccoli",
        "use": "Rangos termicos de cultivo fresco para brocoli y riesgo con temperaturas altas.",
    },
    "UMN irrigation sensors": {
        "name": "University of Minnesota Extension - Irrigation strategies for vegetables",
        "url": "https://extension.umn.edu/vegetables/irrigation-strategies-vegetables",
        "use": "Uso de sensores de humedad del suelo para decisiones de riego en hortalizas.",
    },
}

CROP_PROFILES: dict[str, dict[str, Any]] = {
    "lechuga": {
        "display_name": "Lechuga",
        "crop_history": {
            "planted_at": "2025-08-20",
            "harvest_days": 55,
            "history_note": "Trasplante de verano con riego de establecimiento y seguimiento de humedad cada 10 min.",
        },
        "growth_stages": [
            {"name": "Implantacion", "start_day": 0, "end_day": 10},
            {"name": "Crecimiento vegetativo", "start_day": 11, "end_day": 32},
            {"name": "Formacion de cogollo", "start_day": 33, "end_day": 48},
            {"name": "Ventana de cosecha", "start_day": 49, "end_day": 55},
        ],
        "visual_traits": {"shape": "leafy_rosette", "plant_color": "#30a46c", "accent_color": "#8fd694"},
        "method_note": (
            "Perfil experto referenciado, no aprendida por RL: se aplica sobre variables proxy "
            "del dataset hasta disponer de biomasa, salud visual o rendimiento de cosecha."
        ),
        "dataset_variables": DATASET_VARIABLES_USED,
        "sources": [
            REFERENCE_SOURCES["FAO-56"],
            REFERENCE_SOURCES["RuralCat"],
            REFERENCE_SOURCES["Illinois Extension lettuce"],
            REFERENCE_SOURCES["UMN irrigation sensors"],
        ],
        "air_temp_warn_high_c": 24.0,
        "air_temp_critical_high_c": 28.0,
        "soil_temp_warn_high_c": 22.0,
        "soil_temp_critical_high_c": 25.0,
        "soil_temp_warn_low_c": 6.0,
        "vwc_warn_low": 0.22,
        "vwc_critical_low": 0.18,
        "vwc_warn_high": 0.36,
        "vwc_critical_high": 0.42,
        "par_fraction_min": 0.32,
        "par_fraction_high": 0.78,
        "wind_safe_kmh": 38.0,
        "rain_pause_mm10min": 2.0,
    },
    "brocoli": {
        "display_name": "Brocoli",
        "crop_history": {
            "planted_at": "2025-07-25",
            "harvest_days": 82,
            "history_note": "Plantacion de ciclo medio con fase de desarrollo foliar antes de la pella.",
        },
        "growth_stages": [
            {"name": "Implantacion", "start_day": 0, "end_day": 14},
            {"name": "Desarrollo foliar", "start_day": 15, "end_day": 45},
            {"name": "Inicio de pella", "start_day": 46, "end_day": 68},
            {"name": "Maduracion y cosecha", "start_day": 69, "end_day": 82},
        ],
        "visual_traits": {"shape": "broccoli_head", "plant_color": "#2f8f68", "accent_color": "#4b7f52"},
        "method_note": (
            "Perfil experto referenciado, no aprendida por RL: se aplica sobre variables proxy "
            "del dataset hasta disponer de biomasa, salud visual o rendimiento de cosecha."
        ),
        "dataset_variables": DATASET_VARIABLES_USED,
        "sources": [
            REFERENCE_SOURCES["FAO-56"],
            REFERENCE_SOURCES["RuralCat"],
            REFERENCE_SOURCES["Oregon State Extension broccoli"],
            REFERENCE_SOURCES["UMN irrigation sensors"],
        ],
        "air_temp_warn_high_c": 26.0,
        "air_temp_critical_high_c": 31.0,
        "soil_temp_warn_high_c": 24.0,
        "soil_temp_critical_high_c": 27.0,
        "soil_temp_warn_low_c": 5.0,
        "vwc_warn_low": 0.21,
        "vwc_critical_low": 0.17,
        "vwc_warn_high": 0.37,
        "vwc_critical_high": 0.43,
        "par_fraction_min": 0.30,
        "par_fraction_high": 0.82,
        "wind_safe_kmh": 40.0,
        "rain_pause_mm10min": 2.0,
    },
    "generico_horticola": {
        "display_name": "Horticola generico",
        "crop_history": {
            "planted_at": "2025-08-01",
            "harvest_days": 70,
            "history_note": "Lote generico usado como referencia cuando no se ha fijado una especie concreta.",
        },
        "growth_stages": [
            {"name": "Implantacion", "start_day": 0, "end_day": 12},
            {"name": "Crecimiento", "start_day": 13, "end_day": 40},
            {"name": "Engorde", "start_day": 41, "end_day": 62},
            {"name": "Cosecha", "start_day": 63, "end_day": 70},
        ],
        "visual_traits": {"shape": "leafy_rosette", "plant_color": "#3f9f72", "accent_color": "#83c987"},
        "method_note": (
            "Perfil experto referenciado, no aprendida por RL: se aplica sobre variables proxy "
            "del dataset hasta disponer de biomasa, salud visual o rendimiento de cosecha."
        ),
        "dataset_variables": DATASET_VARIABLES_USED,
        "sources": [
            REFERENCE_SOURCES["FAO-56"],
            REFERENCE_SOURCES["RuralCat"],
            REFERENCE_SOURCES["UMN irrigation sensors"],
        ],
        "air_temp_warn_high_c": 27.0,
        "air_temp_critical_high_c": 32.0,
        "soil_temp_warn_high_c": 25.0,
        "soil_temp_critical_high_c": 29.0,
        "soil_temp_warn_low_c": 5.0,
        "vwc_warn_low": 0.20,
        "vwc_critical_low": 0.16,
        "vwc_warn_high": 0.38,
        "vwc_critical_high": 0.45,
        "par_fraction_min": 0.28,
        "par_fraction_high": 0.84,
        "wind_safe_kmh": 40.0,
        "rain_pause_mm10min": 2.0,
    },
    "tomate": {
        "display_name": "Tomate",
        "crop_history": {
            "planted_at": "2025-06-10",
            "harvest_days": 95,
            "history_note": "Trasplante temprano con entutorado; el control prioriza deficit hidrico y golpe de calor.",
        },
        "growth_stages": [
            {"name": "Implantacion", "start_day": 0, "end_day": 18},
            {"name": "Crecimiento vegetativo", "start_day": 19, "end_day": 42},
            {"name": "Floracion y cuajado", "start_day": 43, "end_day": 68},
            {"name": "Engorde y cosecha", "start_day": 69, "end_day": 95},
        ],
        "visual_traits": {"shape": "vine_fruit", "plant_color": "#2f8f68", "accent_color": "#d92d20"},
        "method_note": (
            "Perfil experto referenciado, no aprendida por RL: se aplica sobre variables proxy "
            "del dataset hasta disponer de biomasa, salud visual o rendimiento de cosecha."
        ),
        "dataset_variables": DATASET_VARIABLES_USED,
        "sources": [
            REFERENCE_SOURCES["FAO-56"],
            REFERENCE_SOURCES["RuralCat"],
            REFERENCE_SOURCES["UMN irrigation sensors"],
        ],
        "air_temp_warn_high_c": 30.0,
        "air_temp_critical_high_c": 35.0,
        "soil_temp_warn_high_c": 28.0,
        "soil_temp_critical_high_c": 32.0,
        "soil_temp_warn_low_c": 10.0,
        "vwc_warn_low": 0.18,
        "vwc_critical_low": 0.14,
        "vwc_warn_high": 0.35,
        "vwc_critical_high": 0.42,
        "par_fraction_min": 0.35,
        "par_fraction_high": 0.88,
        "wind_safe_kmh": 42.0,
        "rain_pause_mm10min": 2.0,
    },
    "pimiento": {
        "display_name": "Pimiento",
        "crop_history": {
            "planted_at": "2025-06-20",
            "harvest_days": 100,
            "history_note": "Cultivo de ciclo largo; se penalizan tanto el estres termico como el exceso de humedad.",
        },
        "growth_stages": [
            {"name": "Implantacion", "start_day": 0, "end_day": 18},
            {"name": "Crecimiento vegetativo", "start_day": 19, "end_day": 46},
            {"name": "Floracion y fruto", "start_day": 47, "end_day": 78},
            {"name": "Recoleccion escalonada", "start_day": 79, "end_day": 100},
        ],
        "visual_traits": {"shape": "pepper_bush", "plant_color": "#2f8f68", "accent_color": "#e11d48"},
        "method_note": (
            "Perfil experto referenciado, no aprendida por RL: se aplica sobre variables proxy "
            "del dataset hasta disponer de biomasa, salud visual o rendimiento de cosecha."
        ),
        "dataset_variables": DATASET_VARIABLES_USED,
        "sources": [
            REFERENCE_SOURCES["FAO-56"],
            REFERENCE_SOURCES["RuralCat"],
            REFERENCE_SOURCES["UMN irrigation sensors"],
        ],
        "air_temp_warn_high_c": 29.0,
        "air_temp_critical_high_c": 34.0,
        "soil_temp_warn_high_c": 27.0,
        "soil_temp_critical_high_c": 31.0,
        "soil_temp_warn_low_c": 12.0,
        "vwc_warn_low": 0.19,
        "vwc_critical_low": 0.15,
        "vwc_warn_high": 0.36,
        "vwc_critical_high": 0.43,
        "par_fraction_min": 0.34,
        "par_fraction_high": 0.86,
        "wind_safe_kmh": 42.0,
        "rain_pause_mm10min": 2.0,
    },
    "fresa": {
        "display_name": "Fresa",
        "crop_history": {
            "planted_at": "2025-07-15",
            "harvest_days": 90,
            "history_note": "Lote sensible a calor y exceso de agua; se prioriza mantener humedad estable.",
        },
        "growth_stages": [
            {"name": "Implantacion", "start_day": 0, "end_day": 16},
            {"name": "Crecimiento vegetativo", "start_day": 17, "end_day": 42},
            {"name": "Floracion", "start_day": 43, "end_day": 62},
            {"name": "Fructificacion y cosecha", "start_day": 63, "end_day": 90},
        ],
        "visual_traits": {"shape": "low_fruit", "plant_color": "#2f8f68", "accent_color": "#e11d48"},
        "method_note": (
            "Perfil experto referenciado, no aprendida por RL: se aplica sobre variables proxy "
            "del dataset hasta disponer de biomasa, salud visual o rendimiento de cosecha."
        ),
        "dataset_variables": DATASET_VARIABLES_USED,
        "sources": [
            REFERENCE_SOURCES["FAO-56"],
            REFERENCE_SOURCES["RuralCat"],
            REFERENCE_SOURCES["UMN irrigation sensors"],
        ],
        "air_temp_warn_high_c": 26.0,
        "air_temp_critical_high_c": 31.0,
        "soil_temp_warn_high_c": 24.0,
        "soil_temp_critical_high_c": 28.0,
        "soil_temp_warn_low_c": 4.0,
        "vwc_warn_low": 0.23,
        "vwc_critical_low": 0.18,
        "vwc_warn_high": 0.38,
        "vwc_critical_high": 0.45,
        "par_fraction_min": 0.30,
        "par_fraction_high": 0.80,
        "wind_safe_kmh": 36.0,
        "rain_pause_mm10min": 2.0,
    },
    "espinaca": {
        "display_name": "Espinaca",
        "crop_history": {
            "planted_at": "2025-08-25",
            "harvest_days": 45,
            "history_note": "Ciclo corto de hoja; el sombreado debe evitar el espigado por calor.",
        },
        "growth_stages": [
            {"name": "Implantacion", "start_day": 0, "end_day": 8},
            {"name": "Hoja joven", "start_day": 9, "end_day": 22},
            {"name": "Crecimiento de hoja", "start_day": 23, "end_day": 38},
            {"name": "Corte", "start_day": 39, "end_day": 45},
        ],
        "visual_traits": {"shape": "leafy_rosette", "plant_color": "#26734d", "accent_color": "#5fb980"},
        "method_note": (
            "Perfil experto referenciado, no aprendida por RL: se aplica sobre variables proxy "
            "del dataset hasta disponer de biomasa, salud visual o rendimiento de cosecha."
        ),
        "dataset_variables": DATASET_VARIABLES_USED,
        "sources": [
            REFERENCE_SOURCES["FAO-56"],
            REFERENCE_SOURCES["RuralCat"],
            REFERENCE_SOURCES["Illinois Extension lettuce"],
            REFERENCE_SOURCES["UMN irrigation sensors"],
        ],
        "air_temp_warn_high_c": 24.0,
        "air_temp_critical_high_c": 29.0,
        "soil_temp_warn_high_c": 22.0,
        "soil_temp_critical_high_c": 26.0,
        "soil_temp_warn_low_c": 4.0,
        "vwc_warn_low": 0.22,
        "vwc_critical_low": 0.17,
        "vwc_warn_high": 0.37,
        "vwc_critical_high": 0.43,
        "par_fraction_min": 0.28,
        "par_fraction_high": 0.78,
        "wind_safe_kmh": 38.0,
        "rain_pause_mm10min": 2.0,
    },
    "cebolla": {
        "display_name": "Cebolla",
        "crop_history": {
            "planted_at": "2025-07-05",
            "harvest_days": 110,
            "history_note": "Plantacion de verano con fase larga de bulbificacion y riegos moderados sin encharcar.",
        },
        "growth_stages": [
            {"name": "Implantacion", "start_day": 0, "end_day": 18},
            {"name": "Desarrollo de hoja", "start_day": 19, "end_day": 55},
            {"name": "Bulbificacion", "start_day": 56, "end_day": 92},
            {"name": "Maduracion y curado", "start_day": 93, "end_day": 110},
        ],
        "visual_traits": {"shape": "allium", "plant_color": "#2f8f68", "accent_color": "#f3d9a4"},
        "method_note": (
            "Perfil experto referenciado, no aprendida por RL: se aplica sobre variables proxy "
            "del dataset hasta disponer de biomasa, salud visual o rendimiento de cosecha."
        ),
        "dataset_variables": DATASET_VARIABLES_USED,
        "sources": [
            REFERENCE_SOURCES["FAO-56"],
            REFERENCE_SOURCES["RuralCat"],
            REFERENCE_SOURCES["UMN irrigation sensors"],
        ],
        "air_temp_warn_high_c": 29.0,
        "air_temp_critical_high_c": 34.0,
        "soil_temp_warn_high_c": 27.0,
        "soil_temp_critical_high_c": 31.0,
        "soil_temp_warn_low_c": 5.0,
        "vwc_warn_low": 0.18,
        "vwc_critical_low": 0.14,
        "vwc_warn_high": 0.34,
        "vwc_critical_high": 0.40,
        "par_fraction_min": 0.33,
        "par_fraction_high": 0.86,
        "wind_safe_kmh": 40.0,
        "rain_pause_mm10min": 1.8,
    },
    "patata": {
        "display_name": "Patata",
        "crop_history": {
            "planted_at": "2025-06-25",
            "harvest_days": 105,
            "history_note": "Lote de tuberculo con riego estable durante tuberizacion y reduccion progresiva antes de cosecha.",
        },
        "growth_stages": [
            {"name": "Brotacion", "start_day": 0, "end_day": 20},
            {"name": "Crecimiento vegetativo", "start_day": 21, "end_day": 45},
            {"name": "Tuberizacion", "start_day": 46, "end_day": 82},
            {"name": "Senescencia y cosecha", "start_day": 83, "end_day": 105},
        ],
        "visual_traits": {"shape": "tuber", "plant_color": "#2f8f68", "accent_color": "#b7791f"},
        "method_note": (
            "Perfil experto referenciado, no aprendida por RL: se aplica sobre variables proxy "
            "del dataset hasta disponer de biomasa, salud visual o rendimiento de cosecha."
        ),
        "dataset_variables": DATASET_VARIABLES_USED,
        "sources": [
            REFERENCE_SOURCES["FAO-56"],
            REFERENCE_SOURCES["RuralCat"],
            REFERENCE_SOURCES["UMN irrigation sensors"],
        ],
        "air_temp_warn_high_c": 28.0,
        "air_temp_critical_high_c": 33.0,
        "soil_temp_warn_high_c": 25.0,
        "soil_temp_critical_high_c": 30.0,
        "soil_temp_warn_low_c": 6.0,
        "vwc_warn_low": 0.20,
        "vwc_critical_low": 0.16,
        "vwc_warn_high": 0.38,
        "vwc_critical_high": 0.45,
        "par_fraction_min": 0.31,
        "par_fraction_high": 0.84,
        "wind_safe_kmh": 40.0,
        "rain_pause_mm10min": 2.0,
    },
}

DEFAULT_WATER_REQUIREMENTS = {
    "weekly_mm_range": [20, 35],
    "root_depth_cm": 25,
    "irrigation_sensitivity": "Mantener humedad estable y evitar tanto deficit prolongado como encharcamiento.",
}

DEFAULT_FERTILIZER_REQUIREMENTS = {
    "nitrogen_kg_ha": [70, 110],
    "phosphorus_kg_ha": [35, 70],
    "potassium_kg_ha": [80, 140],
    "note": "Ajustar abonado con analitica de suelo; valores orientativos para el dashboard operativo.",
}

DEFAULT_LIGHT_REQUIREMENTS = {
    "par_fraction_target_range": [0.34, 0.82],
    "shade_strategy": "Usar la placa para corregir exceso de radiacion o deficit de luz sin forzar movimientos cuando el riesgo es bajo.",
}

CROP_REQUIREMENT_OVERRIDES = {
    "lechuga": {
        "water_requirements": {
            "weekly_mm_range": [25, 38],
            "root_depth_cm": 20,
            "irrigation_sensitivity": "Alta sensibilidad a deficit hidrico en hoja; riegos cortos y frecuentes.",
        },
        "fertilizer_requirements": {"nitrogen_kg_ha": [80, 120], "phosphorus_kg_ha": [35, 65], "potassium_kg_ha": [90, 140]},
        "light_requirements": {"par_fraction_target_range": [0.36, 0.76], "shade_strategy": "Priorizar sombreado en horas calidas para evitar espigado."},
    },
    "brocoli": {
        "water_requirements": {
            "weekly_mm_range": [25, 40],
            "root_depth_cm": 35,
            "irrigation_sensitivity": "Humedad regular durante desarrollo foliar e inicio de pella.",
        },
        "fertilizer_requirements": {"nitrogen_kg_ha": [120, 180], "phosphorus_kg_ha": [45, 85], "potassium_kg_ha": [120, 200]},
        "light_requirements": {"par_fraction_target_range": [0.34, 0.80], "shade_strategy": "Sombrear si coincide radiacion alta con estres termico."},
    },
    "tomate": {
        "water_requirements": {
            "weekly_mm_range": [28, 45],
            "root_depth_cm": 45,
            "irrigation_sensitivity": "Evitar oscilaciones fuertes durante floracion, cuajado y engorde.",
        },
        "fertilizer_requirements": {"nitrogen_kg_ha": [110, 170], "phosphorus_kg_ha": [45, 85], "potassium_kg_ha": [160, 260]},
        "light_requirements": {"par_fraction_target_range": [0.42, 0.88], "shade_strategy": "Reducir sombra cuando el PAR cae, salvo golpe de calor."},
    },
    "pimiento": {
        "water_requirements": {
            "weekly_mm_range": [25, 42],
            "root_depth_cm": 40,
            "irrigation_sensitivity": "Mantener humedad estable en floracion y fruto para evitar caida floral.",
        },
        "fertilizer_requirements": {"nitrogen_kg_ha": [100, 160], "phosphorus_kg_ha": [45, 80], "potassium_kg_ha": [140, 230]},
        "light_requirements": {"par_fraction_target_range": [0.40, 0.86], "shade_strategy": "Sombreado moderado en calor; abrir luz si baja el PAR util."},
    },
    "fresa": {
        "water_requirements": {
            "weekly_mm_range": [18, 30],
            "root_depth_cm": 20,
            "irrigation_sensitivity": "Muy sensible a exceso de agua; preferir pulsos de goteo controlados.",
        },
        "fertilizer_requirements": {"nitrogen_kg_ha": [60, 100], "phosphorus_kg_ha": [35, 65], "potassium_kg_ha": [100, 180]},
        "light_requirements": {"par_fraction_target_range": [0.36, 0.78], "shade_strategy": "Proteger de calor y radiacion excesiva en fructificacion."},
    },
    "espinaca": {
        "water_requirements": {
            "weekly_mm_range": [22, 34],
            "root_depth_cm": 20,
            "irrigation_sensitivity": "Hoja de ciclo corto con alta sensibilidad a sequedad superficial.",
        },
        "fertilizer_requirements": {"nitrogen_kg_ha": [70, 115], "phosphorus_kg_ha": [30, 60], "potassium_kg_ha": [80, 130]},
        "light_requirements": {"par_fraction_target_range": [0.32, 0.76], "shade_strategy": "Sombrear en calor para retrasar espigado."},
    },
    "cebolla": {
        "water_requirements": {
            "weekly_mm_range": [18, 32],
            "root_depth_cm": 30,
            "irrigation_sensitivity": "Humedad constante en bulbificacion y reduccion de riego antes del curado.",
        },
        "fertilizer_requirements": {"nitrogen_kg_ha": [80, 130], "phosphorus_kg_ha": [40, 75], "potassium_kg_ha": [100, 170]},
        "light_requirements": {"par_fraction_target_range": [0.40, 0.86], "shade_strategy": "Mantener buena luz en bulbificacion; sombrear solo con estres termico."},
    },
    "patata": {
        "water_requirements": {
            "weekly_mm_range": [25, 42],
            "root_depth_cm": 45,
            "irrigation_sensitivity": "La tuberizacion penaliza deficit y encharcamiento; estabilizar VWC en rango medio.",
        },
        "fertilizer_requirements": {"nitrogen_kg_ha": [110, 180], "phosphorus_kg_ha": [50, 90], "potassium_kg_ha": [180, 300]},
        "light_requirements": {"par_fraction_target_range": [0.36, 0.84], "shade_strategy": "Sombrear si el suelo supera umbral termico durante tuberizacion."},
    },
}


def _target_range(low: float, high: float, margin: float) -> list[float]:
    target_low = round(low + margin, 3)
    target_high = round(max(target_low + 0.02, high - margin), 3)
    return [target_low, target_high]


def _stage_requirements_from_profile(profile: dict[str, Any]) -> list[dict[str, Any]]:
    vwc_target = _target_range(float(profile["vwc_warn_low"]), float(profile["vwc_warn_high"]), 0.025)
    par_target = _target_range(float(profile["par_fraction_min"]), float(profile["par_fraction_high"]), 0.05)
    requirements = []
    for stage in profile.get("growth_stages", []):
        requirements.append({
            "stage": stage["name"],
            "day_range": [int(stage["start_day"]), int(stage["end_day"])],
            "vwc_target_range": vwc_target,
            "par_fraction_target_range": par_target,
            "management_note": "Mantener VWC y PAR dentro del rango favorable de la fase.",
        })
    return requirements


def _apply_crop_requirements() -> None:
    for crop_type, profile in CROP_PROFILES.items():
        overrides = CROP_REQUIREMENT_OVERRIDES.get(crop_type, {})
        profile["water_requirements"] = {
            **DEFAULT_WATER_REQUIREMENTS,
            **overrides.get("water_requirements", {}),
        }
        profile["fertilizer_requirements"] = {
            **DEFAULT_FERTILIZER_REQUIREMENTS,
            **overrides.get("fertilizer_requirements", {}),
        }
        profile["light_requirements"] = {
            **DEFAULT_LIGHT_REQUIREMENTS,
            **overrides.get("light_requirements", {}),
        }
        profile["stage_requirements"] = overrides.get("stage_requirements", _stage_requirements_from_profile(profile))


_apply_crop_requirements()

VALID_CROP_ZONES = ("S1", "S2")

RISK_COLUMNS = [
    "Time",
    "crop_type",
    "crop_zone",
    "time_block_10min",
    "hour_of_day",
    "solar_elevation_deg",
    "tracking_regime",
    "track_mean",
    "IEC",
    "energy_score",
    "crop_score",
    "Tair_WS",
    "Tsoil_crop_zone_mean",
    "Tsoil_crop_zone_source",
    "VWC_crop_zone_fraction",
    "VWC_crop_zone_source",
    "ePAR_crop_zone_mean",
    "ePAR_crop_zone_source",
    "Tsoil_S1_mean",
    "VWC_S1_fraction",
    "ePAR_S1_mean",
    "ePAR_R1_mean",
    "par_fraction_s1",
    "wind_speed_kmh",
    "precip_intensity_mm10min",
    "heat_stress",
    "cold_stress",
    "water_deficit",
    "water_excess",
    "light_deficit",
    "excess_radiation",
    "weather_risk",
    "crop_risk_score",
    "crop_health_score",
    "stress_type",
    "crop_management_action",
    "irrigation_mode",
    "irrigation_active",
    "irrigation_mm_10min",
    "irrigation_duration_min",
    "irrigation_vwc_delta_est",
    "irrigation_tsoil_delta_est_c",
    "panel_action",
    "recommended_action",
    "action_label",
    "panel_action_label",
]

ACTION_LABELS = {
    "activar_riego": "Activar riego",
    "pausar_riego": "Pausar riego",
    "riego_preventivo": "Riego preventivo",
    "poda_sanitaria": "Inspeccion y poda sanitaria",
    "proteccion_frio": "Proteccion por frio",
    "sin_manejo_directo": "Sin manejo directo",
    "aumentar_sombreado": "Aumentar sombreado",
    "reducir_sombreado": "Reducir sombreado",
    "posicion_segura": "Posicion segura",
    "mantener_placas": "Mantener placas",
    "mantener": "Mantener manejo actual",
}

DEFAULT_IRRIGATION_ACTUATOR = {
    "mode": "off",
    "active": False,
    "mm_10min": 0.0,
    "duration_min": 0.0,
    "vwc_delta_est": 0.0,
    "tsoil_delta_est_c": 0.0,
}

IRRIGATION_ACTUATOR_PROFILES = {
    "activar_riego": {
        "mode": "drip",
        "active": True,
        "mm_10min": 2.0,
        "duration_min": 10.0,
        "vwc_delta_est": 0.010,
        "tsoil_delta_est_c": -0.15,
    },
    "riego_preventivo": {
        "mode": "preventive",
        "active": True,
        "mm_10min": 1.2,
        "duration_min": 6.0,
        "vwc_delta_est": 0.006,
        "tsoil_delta_est_c": -0.08,
    },
    "pausar_riego": {
        "mode": "paused",
        "active": False,
        "mm_10min": 0.0,
        "duration_min": 0.0,
        "vwc_delta_est": 0.0,
        "tsoil_delta_est_c": 0.0,
    },
}


def _irrigation_actuator_for_action(action: Any) -> dict[str, Any]:
    profile = IRRIGATION_ACTUATOR_PROFILES.get(str(action), DEFAULT_IRRIGATION_ACTUATOR)
    return dict(profile)


def _crop_management_action(row: pd.Series) -> str:
    if bool(row.get("water_excess", False)) and bool(row.get("light_deficit", False)):
        return "poda_sanitaria"
    if bool(row.get("water_excess", False)):
        return "pausar_riego"
    if bool(row.get("water_deficit", False)) and bool(row.get("heat_stress", False)):
        return "riego_preventivo"
    if bool(row.get("water_deficit", False)):
        return "activar_riego"
    if bool(row.get("cold_stress", False)):
        return "proteccion_frio"
    return "sin_manejo_directo"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(numeric):
        return default
    return numeric


def _panel_action(row: pd.Series) -> str:
    if bool(row.get("weather_risk", False)):
        return "posicion_segura"
    if bool(row.get("heat_stress", False)) or bool(row.get("excess_radiation", False)):
        return "aumentar_sombreado"

    solar_elevation = _safe_float(row.get("solar_elevation_deg"), 0.0)
    par_fraction = _safe_float(row.get("par_fraction_s1"), 1.0)
    crop_risk = _safe_float(row.get("crop_risk_score"), 0.0)
    actionable_light_deficit = (
        bool(row.get("light_deficit", False))
        and solar_elevation >= 18.0
        and par_fraction >= 0.06
        and crop_risk >= 0.18
    )
    if actionable_light_deficit:
        return "reducir_sombreado"
    return "mantener_placas"


def _profile(crop_type: str) -> dict[str, Any]:
    if crop_type not in CROP_PROFILES:
        raise ValueError(f"unknown crop_type '{crop_type}'. Expected one of {sorted(CROP_PROFILES)}")
    return CROP_PROFILES[crop_type]


def _normalise_crop_zone(crop_zone: str) -> str:
    zone = str(crop_zone).upper()
    if zone not in VALID_CROP_ZONES:
        raise ValueError(f"unknown crop_zone '{crop_zone}'. Expected one of {list(VALID_CROP_ZONES)}")
    return zone


def crop_calendar_for_date(crop_type: str, current_time: Any) -> dict[str, Any]:
    """Return crop-cycle state for the selected crop and dashboard timestamp."""
    profile = _profile(crop_type)
    history = profile.get("crop_history", {})
    planted_at = pd.Timestamp(history.get("planted_at", current_time)).normalize()
    current_at = pd.Timestamp(current_time).normalize()
    harvest_days = int(history.get("harvest_days", 60))
    days_after_planting = max(0, int((current_at - planted_at).days))
    harvest_at = planted_at + pd.Timedelta(days=harvest_days)
    days_to_harvest = max(0, int((harvest_at - current_at).days))
    progress = 1.0 if harvest_days <= 0 else min(1.0, days_after_planting / harvest_days)

    stages = profile.get("growth_stages", [])
    current_stage = stages[-1] if stages else {"name": "Ciclo activo", "start_day": 0, "end_day": harvest_days}
    for stage in stages:
        if int(stage.get("start_day", 0)) <= days_after_planting <= int(stage.get("end_day", harvest_days)):
            current_stage = stage
            break
    if days_after_planting > harvest_days:
        current_stage = {"name": "Listo para recoger", "start_day": harvest_days, "end_day": days_after_planting}

    return {
        "crop_type": crop_type,
        "display_name": profile.get("display_name", crop_type),
        "planted_at": planted_at.date().isoformat(),
        "harvest_at": harvest_at.date().isoformat(),
        "harvest_days": harvest_days,
        "days_after_planting": days_after_planting,
        "days_to_harvest": days_to_harvest,
        "progress": progress,
        "current_stage": current_stage,
        "growth_stages": stages,
        "history_note": history.get("history_note", ""),
        "ready_to_harvest": days_after_planting >= harvest_days,
    }


def _series(df: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(default, index=df.index, dtype="float64")


def _normalise_vwc(vwc: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(vwc, errors="coerce")
    return numeric.where(numeric <= 1.5, numeric / 100.0)


def _sensor_source(values: pd.Series, source: str) -> pd.Series:
    return pd.Series(np.where(values.notna(), source, ""), index=values.index, dtype="object")


def _fill_missing_with_source(
    values: pd.Series,
    sources: pd.Series,
    fallback: pd.Series,
    fallback_source: str,
) -> tuple[pd.Series, pd.Series]:
    mask = values.isna() & fallback.notna()
    return values.mask(mask, fallback), sources.mask(mask, fallback_source)


def _fill_default_with_source(
    values: pd.Series,
    sources: pd.Series,
    default: pd.Series | float,
    default_source: str,
) -> tuple[pd.Series, pd.Series]:
    if not isinstance(default, pd.Series):
        default = pd.Series(default, index=values.index, dtype="float64")
    mask = values.isna()
    return values.mask(mask, default), sources.mask(mask, default_source)


def _main_stress_type(row: pd.Series) -> str:
    checks = [
        ("weather_risk", "riesgo_meteorologico"),
        ("water_deficit", "deficit_hidrico"),
        ("water_excess", "exceso_hidrico"),
        ("heat_stress", "estres_termico"),
        ("cold_stress", "frio"),
        ("light_deficit", "deficit_luz"),
        ("excess_radiation", "radiacion_excesiva"),
    ]
    for key, label in checks:
        if bool(row.get(key, False)):
            return label
    return "estable"


def _recommended_action(row: pd.Series) -> str:
    crop_action = str(row.get("crop_management_action", "sin_manejo_directo"))
    panel_action = str(row.get("panel_action", "mantener_placas"))
    if crop_action != "sin_manejo_directo":
        return crop_action
    if panel_action != "mantener_placas":
        return panel_action
    return "mantener"


def build_crop_risk_dataset(model_df: pd.DataFrame, crop_type: str = "lechuga", crop_zone: str = "S1") -> pd.DataFrame:
    profile = _profile(crop_type)
    zone = _normalise_crop_zone(crop_zone)
    df = model_df.copy()

    tsoil_col = f"Tsoil_{zone}_mean"
    vwc_col = f"VWC_{zone}_mean"
    epar_col = f"ePAR_{zone}_mean"

    solar_elevation = _series(df, "solar_elevation_deg", 0).fillna(0)
    tair = _series(df, "Tair_WS")
    epar_r1_raw = _series(df, "ePAR_R1_mean")
    epar_r1 = epar_r1_raw.replace(0, np.nan)

    tsoil_s1 = _series(df, "Tsoil_S1_mean")
    vwc_s1 = _normalise_vwc(_series(df, "VWC_S1_mean"))
    epar_s1 = _series(df, "ePAR_S1_mean")

    vwc_fraction = _normalise_vwc(_series(df, vwc_col))
    vwc_source = _sensor_source(vwc_fraction, f"{vwc_col}_sensor")
    if zone != "S1":
        vwc_fraction, vwc_source = _fill_missing_with_source(
            vwc_fraction,
            vwc_source,
            vwc_s1,
            "VWC_S1_mean_proxy_under_panel",
        )
    vwc_r1_under_panel = (_normalise_vwc(_series(df, "VWC_R1_mean")) + 0.015).clip(0, 1)
    vwc_fraction, vwc_source = _fill_missing_with_source(
        vwc_fraction,
        vwc_source,
        vwc_r1_under_panel,
        "VWC_R1_mean_imputed_under_panel",
    )
    vwc_fraction, vwc_source = _fill_default_with_source(
        vwc_fraction,
        vwc_source,
        float(profile["vwc_warn_low"]) + 0.04,
        "crop_profile_default",
    )

    day_adjustment = pd.Series(np.where(solar_elevation > 5, -0.6, 0.2), index=df.index, dtype="float64")
    tsoil = _series(df, tsoil_col)
    tsoil_source = _sensor_source(tsoil, f"{tsoil_col}_sensor")
    if zone != "S1":
        tsoil, tsoil_source = _fill_missing_with_source(
            tsoil,
            tsoil_source,
            tsoil_s1,
            "Tsoil_S1_mean_proxy_under_panel",
        )
    tsoil_r1_under_panel = _series(df, "Tsoil_R1_mean") + day_adjustment
    tsoil, tsoil_source = _fill_missing_with_source(
        tsoil,
        tsoil_source,
        tsoil_r1_under_panel,
        "Tsoil_R1_mean_imputed_under_panel",
    )
    tsoil, tsoil_source = _fill_default_with_source(
        tsoil,
        tsoil_source,
        tair.fillna(18.0),
        "Tair_WS_profile_proxy",
    )

    epar_crop_zone = _series(df, epar_col)
    epar_source = _sensor_source(epar_crop_zone, f"{epar_col}_sensor")
    if zone != "S1":
        epar_crop_zone, epar_source = _fill_missing_with_source(
            epar_crop_zone,
            epar_source,
            epar_s1,
            "ePAR_S1_mean_proxy_under_panel",
        )
    epar_r1_under_panel = (epar_r1_raw * 0.78).clip(lower=0)
    epar_crop_zone, epar_source = _fill_missing_with_source(
        epar_crop_zone,
        epar_source,
        epar_r1_under_panel,
        "ePAR_R1_mean_imputed_under_panel",
    )
    epar_crop_zone, epar_source = _fill_default_with_source(
        epar_crop_zone,
        epar_source,
        0.0,
        "night_or_crop_profile_default",
    )

    par_fraction = (epar_crop_zone / epar_r1).clip(0, 2).fillna(0)
    wind = _series(df, "wind_speed_kmh", 0).fillna(0)
    rain = _series(df, "precip_intensity_mm10min", 0).fillna(0)

    heat_stress = (
        (tair >= profile["air_temp_critical_high_c"])
        | (tsoil >= profile["soil_temp_critical_high_c"])
        | ((tair >= profile["air_temp_warn_high_c"]) & (tsoil >= profile["soil_temp_warn_high_c"]))
    )
    cold_stress = tsoil <= profile["soil_temp_warn_low_c"]
    water_deficit = vwc_fraction <= profile["vwc_warn_low"]
    water_excess = (vwc_fraction >= profile["vwc_warn_high"]) | (rain >= profile["rain_pause_mm10min"])
    light_deficit = (par_fraction <= profile["par_fraction_min"]) & (rain < profile["rain_pause_mm10min"])
    excess_radiation = (par_fraction >= profile["par_fraction_high"]) & (heat_stress | water_deficit)
    weather_risk = wind >= profile["wind_safe_kmh"]

    risk_score = (
        0.24 * heat_stress.astype(float)
        + 0.22 * water_deficit.astype(float)
        + 0.16 * water_excess.astype(float)
        + 0.13 * light_deficit.astype(float)
        + 0.10 * excess_radiation.astype(float)
        + 0.10 * weather_risk.astype(float)
        + 0.05 * cold_stress.astype(float)
    ).clip(0, 1)

    risk = pd.DataFrame({
        "Time": pd.to_datetime(df["Time"]),
        "crop_type": crop_type,
        "crop_zone": zone,
        "time_block_10min": df.get("time_block_10min", pd.Series("", index=df.index)),
        "hour_of_day": df.get("hour_of_day", pd.Series(pd.NA, index=df.index)),
        "solar_elevation_deg": _series(df, "solar_elevation_deg"),
        "tracking_regime": df.get("tracking_regime", pd.Series("", index=df.index)),
        "track_mean": _series(df, "track_mean"),
        "IEC": _series(df, "IEC"),
        "energy_score": _series(df, "energy_score"),
        "crop_score": _series(df, "crop_score"),
        "Tair_WS": tair,
        "Tsoil_crop_zone_mean": tsoil,
        "Tsoil_crop_zone_source": tsoil_source,
        "VWC_crop_zone_fraction": vwc_fraction,
        "VWC_crop_zone_source": vwc_source,
        "ePAR_crop_zone_mean": epar_crop_zone,
        "ePAR_crop_zone_source": epar_source,
        "Tsoil_S1_mean": tsoil_s1,
        "VWC_S1_fraction": vwc_s1,
        "ePAR_S1_mean": epar_s1,
        "ePAR_R1_mean": epar_r1,
        "par_fraction_s1": par_fraction,
        "wind_speed_kmh": wind,
        "precip_intensity_mm10min": rain,
        "heat_stress": heat_stress,
        "cold_stress": cold_stress,
        "water_deficit": water_deficit,
        "water_excess": water_excess,
        "light_deficit": light_deficit,
        "excess_radiation": excess_radiation,
        "weather_risk": weather_risk,
        "crop_risk_score": risk_score,
        "crop_health_score": (1.0 - risk_score).clip(0, 1),
    })
    risk = risk.assign(
        stress_type=risk.apply(_main_stress_type, axis=1),
        crop_management_action=risk.apply(_crop_management_action, axis=1),
        panel_action=risk.apply(_panel_action, axis=1),
    )
    irrigation_actuator = risk["crop_management_action"].map(_irrigation_actuator_for_action)
    risk = risk.assign(
        irrigation_mode=irrigation_actuator.map(lambda actuator: actuator["mode"]),
        irrigation_active=irrigation_actuator.map(lambda actuator: actuator["active"]),
        irrigation_mm_10min=irrigation_actuator.map(lambda actuator: actuator["mm_10min"]),
        irrigation_duration_min=irrigation_actuator.map(lambda actuator: actuator["duration_min"]),
        irrigation_vwc_delta_est=irrigation_actuator.map(lambda actuator: actuator["vwc_delta_est"]),
        irrigation_tsoil_delta_est_c=irrigation_actuator.map(lambda actuator: actuator["tsoil_delta_est_c"]),
    )
    risk = risk.assign(recommended_action=risk.apply(_recommended_action, axis=1))
    risk = risk.assign(
        action_label=risk["recommended_action"].map(ACTION_LABELS).fillna(risk["recommended_action"]),
        panel_action_label=risk["panel_action"].map(ACTION_LABELS).fillna(risk["panel_action"]),
    )
    return risk[RISK_COLUMNS].round(4)


def generate_agricultural_rules_10min(risk_df: pd.DataFrame, crop_type: str = "lechuga") -> pd.DataFrame:
    profile = _profile(crop_type)
    source_names = ", ".join(source["name"] for source in profile["sources"])
    df = risk_df[risk_df["recommended_action"] != "mantener"].copy()
    rules = []
    action_templates = {
        "regar": (
            "Si el VWC de {cultivo} cae por debajo del umbral de confort, activar riego localizado manteniendo la politica energetica si no hay estres termico.",
            "Regla experta referenciada: usa humedad del suelo normalizada del dataset y criterios de riego FAO/RuralCat.",
        ),
        "activar_riego": (
            "Si el VWC de {cultivo} cae por debajo del umbral de confort, activar riego localizado manteniendo la politica energetica si no hay estres termico.",
            "Regla experta referenciada: usa humedad del suelo normalizada del dataset y criterios de riego FAO/RuralCat.",
        ),
        "riego_preventivo": (
            "Si {cultivo} combina deficit hidrico con calor, aplicar riego preventivo y aumentar sombra para evitar perdida de vigor.",
            "Regla experta referenciada: combina VWC bajo y temperatura alta como proxy de estres hidrico-termico.",
        ),
        "pausar_riego": (
            "Si {cultivo} presenta VWC alto o lluvia reciente, pausar riego para reducir riesgo de encharcamiento.",
            "Regla experta referenciada: usa VWC y precipitacion a 10 minutos para evitar exceso hidrico.",
        ),
        "poda_sanitaria": (
            "Si {cultivo} combina humedad elevada con baja PAR bajo panel, planificar inspeccion y poda sanitaria de hojas danadas o focos de enfermedad.",
            "Regla experta referenciada: usa VWC/lluvia y fraccion PAR como proxy de riesgo sanitario; no automatiza poda sin inspeccion humana.",
        ),
        "proteccion_frio": (
            "Si {cultivo} entra en umbral frio, activar protocolo de proteccion termica y evitar riegos innecesarios.",
            "Regla experta referenciada: usa temperatura del suelo como proxy de frio para hortalizas.",
        ),
        "aumentar_sombreado": (
            "Si {cultivo} entra en estres termico o radiacion excesiva, aumentar sombreado mediante la posicion de placas compatible con buen IEC.",
            "Regla experta referenciada: convierte la rotacion en una accion de microclima cuando temperatura/PAR superan umbrales.",
        ),
        "reducir_sombreado": (
            "Si {cultivo} recibe poca PAR sin estres termico ni lluvia, reducir sombreado para recuperar actividad fotosintetica.",
            "Regla experta referenciada: usa fraccion PAR bajo panel frente a referencia como proxy de deficit luminico.",
        ),
        "posicion_segura": (
            "Si hay viento fuerte, usar posicion segura de placas y suspender cambios agresivos sobre {cultivo}.",
            "Regla experta referenciada: accion de proteccion por meteorologia usando viento del dataset.",
        ),
    }

    for action, (template, comment) in action_templates.items():
        subset = df[df["recommended_action"] == action]
        if subset.empty:
            continue
        rules.append({
            "tipo": "10min_agronomia_modelable",
            "cultivo": crop_type,
            "accion": action,
            "regla": template.format(cultivo=crop_type),
            "soporte_obs": int(len(subset)),
            "riesgo_mediano": round(float(subset["crop_risk_score"].median()), 3),
            "iec_mediana": round(float(subset["IEC"].median()), 3),
            "franja_dominante": str(subset["time_block_10min"].mode().iloc[0]) if not subset.empty else "",
            "variables_dataset": ", ".join(DATASET_VARIABLES_USED),
            "fuentes": source_names,
            "comentario": comment,
        })

    return pd.DataFrame(
        rules,
        columns=[
            "tipo",
            "cultivo",
            "accion",
            "regla",
            "soporte_obs",
            "riesgo_mediano",
            "iec_mediana",
            "franja_dominante",
            "variables_dataset",
            "fuentes",
            "comentario",
        ],
    )


def write_agricultural_outputs(
    output_dir: str | Path,
    crop_risk: pd.DataFrame,
    agricultural_rules: pd.DataFrame,
    crop_profiles: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    crop_risk_path = output_path / "crop_risk_10min.csv"
    agricultural_rules_path = output_path / "agricultural_rules_10min.csv"
    crop_profiles_path = output_path / "crop_profiles.json"

    crop_risk.to_csv(crop_risk_path, index=False)
    agricultural_rules.to_csv(agricultural_rules_path, index=False)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "method": "reglas expertas referenciadas sobre variables proxy del dataset",
        "scope": (
            "Estas reglas no son una recompensa RL aprendida ni un modelo agronomico supervisado; "
            "documentan umbrales aplicables a VWC, temperatura, PAR, lluvia y viento hasta disponer "
            "de etiquetas reales de salud, biomasa o rendimiento."
        ),
        "reference_sources": REFERENCE_SOURCES,
        "profiles": crop_profiles or CROP_PROFILES,
        "note": (
            "Perfiles demo con umbrales agronomicos referenciados. Validar con especialista "
            "antes de automatizar riego, sombreado o manejo del cultivo; no son una recompensa RL aprendida."
        ),
    }
    crop_profiles_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "crop_risk": crop_risk_path,
        "agricultural_rules": agricultural_rules_path,
        "crop_profiles": crop_profiles_path,
    }
