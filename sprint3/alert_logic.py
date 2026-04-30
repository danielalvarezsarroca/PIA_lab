import numpy as np
import pandas as pd

from data_loader import parse_tracker_name

ANOMALY_THRESHOLD = 450.0   # deg² variance — trackers above this are flagged
VWC_ALERT_THRESHOLD = -0.005  # m³/m³ per hour — declining trend triggers AVISO


def get_anomalous_trackers(df_diagnostic: pd.DataFrame, threshold: float = ANOMALY_THRESHOLD) -> list[str]:
    """Return list of tracker IDs (e.g. 'M05') with varianza_deg2 > threshold."""
    anomalous = df_diagnostic[df_diagnostic["varianza_deg2"] > threshold]
    return [parse_tracker_name(idx) for idx in anomalous.index]


def get_vwc_trend(df_modelo: pd.DataFrame) -> float:
    """
    Return linear slope of VWC_S1_mean over time (m³/m³ per hour).
    Negative → declining soil moisture.
    """
    valid = df_modelo[["Time", "VWC_S1_mean"]].dropna()
    if len(valid) < 2:
        return 0.0
    hours = (valid["Time"] - valid["Time"].iloc[0]).dt.total_seconds() / 3600
    slope = float(np.polyfit(hours, valid["VWC_S1_mean"], 1)[0])
    return slope


def build_alert_list(df_diagnostic: pd.DataFrame, df_modelo: pd.DataFrame) -> list[dict]:
    """
    Return a list of alert dicts with keys: title, description, severity.
    CRÍTICO: trackers with varianza > ANOMALY_THRESHOLD.
    AVISO: VWC declining faster than VWC_ALERT_THRESHOLD.
    """
    alerts: list[dict] = []

    anomalous = get_anomalous_trackers(df_diagnostic)
    if anomalous:
        alerts.append({
            "title": f"Trackers anómalos: {', '.join(anomalous)}",
            "description": f"Varianza angular > {ANOMALY_THRESHOLD} deg² — comportamiento irregular detectado",
            "severity": "CRÍTICO",
        })

    trend = get_vwc_trend(df_modelo)
    if trend < VWC_ALERT_THRESHOLD:
        latest_vwc = df_modelo["VWC_S1_mean"].dropna().iloc[-1] if not df_modelo["VWC_S1_mean"].dropna().empty else float("nan")
        alerts.append({
            "title": "VWC descendente",
            "description": f"Tendencia: {trend:.4f} m³/m³·h. Último valor: {latest_vwc:.2f} (umbral crítico: 0.20)",
            "severity": "AVISO",
        })

    return alerts
