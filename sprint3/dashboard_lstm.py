from __future__ import annotations

from pathlib import Path

import pandas as pd

from world_model_lstm_inference import load_lstm_world_model, predict_next_state


def _metric_value(metrics: dict, target: str, key: str = "mae") -> float | None:
    value = metrics.get("target_metrics", {}).get(target, {}).get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_model_status(metrics: dict, model_exists: bool, scalers_exist: bool) -> dict[str, str]:
    if not model_exists or not scalers_exist or not metrics:
        return {
            "state": "No disponible",
            "window": "Sin artefactos",
            "vwc_mae": "-",
            "tsoil_mae": "-",
            "gpoa_mae": "-",
        }

    window_size = int(metrics.get("window_size", 12))
    vwc_mae = _metric_value(metrics, "next_VWC_R1_sim")
    tsoil_mae = _metric_value(metrics, "next_Tsoil_R1_sim")
    gpoa_mae = _metric_value(metrics, "next_GPOA_mean")
    return {
        "state": "Entrenado",
        "window": f"{window_size} pasos x 10 min",
        "vwc_mae": f"{vwc_mae:.4f}" if vwc_mae is not None else "-",
        "tsoil_mae": f"{tsoil_mae:.3f} degC" if tsoil_mae is not None else "-",
        "gpoa_mae": f"{gpoa_mae:.2f} W/m2" if gpoa_mae is not None else "-",
    }


def build_prediction_delta_frame(current: pd.Series, predicted: dict[str, float | int]) -> pd.DataFrame:
    current_par = float(current.get("PAR_R1", 0.0))
    predicted_par = max(0.0, current_par + float(predicted.get("Delta_PAR_S1", 0.0)))
    return pd.DataFrame([
        {
            "momento": "Ahora",
            "VWC": float(current.get("VWC_R1_sim", current.get("VWC_R1_mean", 0.0))),
            "Tsoil": float(current.get("Tsoil_R1_sim", current.get("Tsoil_R1_mean", 0.0))),
            "PAR": current_par,
            "GPOA": float(current.get("GPOA_mean", 0.0)),
        },
        {
            "momento": "+10 min",
            "VWC": float(predicted.get("VWC_R1_sim", 0.0)),
            "Tsoil": float(predicted.get("Tsoil_R1_sim", 0.0)),
            "PAR": predicted_par,
            "GPOA": float(predicted.get("GPOA_mean", 0.0)),
        },
    ])


def predict_dashboard_next_state(
    recent_window: pd.DataFrame,
    tracker_angle_deg: float,
    irrigation_on: bool,
    irrigation_dose_mm: float,
    model_path: str | Path,
    scalers_path: str | Path,
    device: str = "cpu",
) -> dict[str, float | int]:
    model, scalers = load_lstm_world_model(
        model_path=model_path,
        scalers_path=scalers_path,
        device=device,
    )
    return predict_next_state(
        model=model,
        scalers=scalers,
        recent_window=recent_window,
        action={
            "tracker_angle_deg": float(tracker_angle_deg),
            "irrigation_on": bool(irrigation_on),
            "irrigation_dose_mm": float(irrigation_dose_mm),
        },
        device=device,
    )
