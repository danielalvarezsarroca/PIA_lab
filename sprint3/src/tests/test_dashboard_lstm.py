import pandas as pd

from dashboard_lstm import build_prediction_delta_frame, format_model_status


def test_format_model_status_extracts_key_metrics():
    metrics = {
        "window_size": 12,
        "target_metrics": {
            "next_VWC_R1_sim": {"mae": 0.003852, "rmse": 0.005831},
            "next_Tsoil_R1_sim": {"mae": 0.111123, "rmse": 0.192392},
            "next_GPOA_mean": {"mae": 12.740058, "rmse": 26.970427},
        },
    }

    status = format_model_status(metrics, model_exists=True, scalers_exist=True)

    assert status["state"] == "Entrenado"
    assert status["window"] == "12 pasos x 10 min"
    assert status["vwc_mae"] == "0.0039"
    assert status["tsoil_mae"] == "0.111 degC"
    assert status["gpoa_mae"] == "12.74 W/m2"


def test_format_model_status_reports_missing_artifacts():
    status = format_model_status({}, model_exists=False, scalers_exist=False)

    assert status["state"] == "No disponible"
    assert status["window"] == "Sin artefactos"


def test_build_prediction_delta_frame_returns_before_after_rows():
    current = pd.Series({
        "VWC_R1_sim": 0.18,
        "Tsoil_R1_sim": 24.0,
        "PAR_R1": 520.0,
        "GPOA_mean": 760.0,
    })
    predicted = {
        "VWC_R1_sim": 0.20,
        "Tsoil_R1_sim": 23.5,
        "Delta_PAR_S1": -120.0,
        "GPOA_mean": 710.0,
        "minutes_since_last_irr": 0,
    }

    frame = build_prediction_delta_frame(current, predicted)

    assert list(frame["momento"]) == ["Ahora", "+10 min"]
    assert frame.loc[1, "VWC"] == 0.20
    assert frame.loc[1, "Tsoil"] == 23.5
    assert frame.loc[1, "PAR"] == 400.0
