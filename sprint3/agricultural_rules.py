from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

CROP_PROFILES: dict[str, dict[str, Any]] = {
    "lechuga": {
        "display_name": "Lechuga",
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
}

RISK_COLUMNS = [
    "Time",
    "crop_type",
    "time_block_10min",
    "hour_of_day",
    "tracking_regime",
    "track_mean",
    "IEC",
    "energy_score",
    "crop_score",
    "Tair_WS",
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
    "recommended_action",
    "action_label",
]

ACTION_LABELS = {
    "regar": "Activar riego",
    "pausar_riego": "Pausar riego",
    "riego_preventivo": "Riego preventivo",
    "aumentar_sombreado": "Aumentar sombreado",
    "reducir_sombreado": "Reducir sombreado",
    "posicion_segura": "Posicion segura",
    "alerta_frio": "Alerta por frio",
    "mantener": "Mantener manejo actual",
}


def _profile(crop_type: str) -> dict[str, Any]:
    if crop_type not in CROP_PROFILES:
        raise ValueError(f"unknown crop_type '{crop_type}'. Expected one of {sorted(CROP_PROFILES)}")
    return CROP_PROFILES[crop_type]


def _series(df: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(default, index=df.index, dtype="float64")


def _normalise_vwc(vwc: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(vwc, errors="coerce")
    median = numeric.dropna().median()
    if pd.isna(median):
        return numeric
    if median > 1.5:
        return numeric / 100.0
    return numeric


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
    if bool(row.get("weather_risk", False)):
        return "posicion_segura"
    if bool(row.get("water_excess", False)):
        return "pausar_riego"
    if bool(row.get("water_deficit", False)) and bool(row.get("heat_stress", False)):
        return "riego_preventivo"
    if bool(row.get("water_deficit", False)):
        return "regar"
    if bool(row.get("heat_stress", False)) or bool(row.get("excess_radiation", False)):
        return "aumentar_sombreado"
    if bool(row.get("cold_stress", False)):
        return "alerta_frio"
    if bool(row.get("light_deficit", False)):
        return "reducir_sombreado"
    return "mantener"


def build_crop_risk_dataset(model_df: pd.DataFrame, crop_type: str = "lechuga") -> pd.DataFrame:
    profile = _profile(crop_type)
    df = model_df.copy()

    vwc_fraction = _normalise_vwc(_series(df, "VWC_S1_mean"))
    epar_s1 = _series(df, "ePAR_S1_mean")
    epar_r1 = _series(df, "ePAR_R1_mean").replace(0, np.nan)
    par_fraction = (epar_s1 / epar_r1).clip(0, 2).fillna(0)
    tair = _series(df, "Tair_WS")
    tsoil = _series(df, "Tsoil_S1_mean")
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
        "time_block_10min": df.get("time_block_10min", pd.Series("", index=df.index)),
        "hour_of_day": df.get("hour_of_day", pd.Series(pd.NA, index=df.index)),
        "tracking_regime": df.get("tracking_regime", pd.Series("", index=df.index)),
        "track_mean": _series(df, "track_mean"),
        "IEC": _series(df, "IEC"),
        "energy_score": _series(df, "energy_score"),
        "crop_score": _series(df, "crop_score"),
        "Tair_WS": tair,
        "Tsoil_S1_mean": tsoil,
        "VWC_S1_fraction": vwc_fraction,
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
        recommended_action=risk.apply(_recommended_action, axis=1),
    )
    risk = risk.assign(
        action_label=risk["recommended_action"].map(ACTION_LABELS).fillna(risk["recommended_action"])
    )
    return risk[RISK_COLUMNS].round(4)


def generate_agricultural_rules_10min(risk_df: pd.DataFrame, crop_type: str = "lechuga") -> pd.DataFrame:
    _profile(crop_type)
    df = risk_df[risk_df["recommended_action"] != "mantener"].copy()
    rules = []
    action_templates = {
        "regar": (
            "Si el VWC de {cultivo} cae por debajo del umbral de confort, activar riego localizado manteniendo la politica energetica si no hay estres termico.",
            "Accion modelable con humedad del suelo normalizada; no requiere sensores extra.",
        ),
        "riego_preventivo": (
            "Si {cultivo} combina deficit hidrico con calor, aplicar riego preventivo y aumentar sombra para evitar perdida de vigor.",
            "Accion combinada por VWC bajo y temperatura alta.",
        ),
        "pausar_riego": (
            "Si {cultivo} presenta VWC alto o lluvia reciente, pausar riego para reducir riesgo de encharcamiento.",
            "Accion modelable con VWC y precipitacion a 10 minutos.",
        ),
        "aumentar_sombreado": (
            "Si {cultivo} entra en estres termico o radiacion excesiva, aumentar sombreado mediante la posicion de placas compatible con buen IEC.",
            "Convierte la rotacion en una accion agronomica de microclima.",
        ),
        "reducir_sombreado": (
            "Si {cultivo} recibe poca PAR sin estres termico ni lluvia, reducir sombreado para recuperar actividad fotosintetica.",
            "Accion modelable por fraccion PAR bajo panel frente a referencia.",
        ),
        "posicion_segura": (
            "Si hay viento fuerte, usar posicion segura de placas y suspender cambios agresivos sobre {cultivo}.",
            "Accion de proteccion por meteorologia.",
        ),
        "alerta_frio": (
            "Si {cultivo} entra en umbral frio, generar alerta de proteccion termica y evitar riegos innecesarios.",
            "Accion modelable con temperatura del suelo.",
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
        "profiles": crop_profiles or CROP_PROFILES,
        "note": (
            "Perfiles demo con umbrales agronomicos aproximados. Validar con especialista "
            "antes de automatizar riego, sombreado o manejo del cultivo."
        ),
    }
    crop_profiles_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "crop_risk": crop_risk_path,
        "agricultural_rules": agricultural_rules_path,
        "crop_profiles": crop_profiles_path,
    }
