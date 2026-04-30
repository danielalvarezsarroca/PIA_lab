import pandas as pd
import pytest
from alert_logic import get_anomalous_trackers, get_vwc_trend, build_alert_list

_DIAG_DF = pd.DataFrame(
    {"varianza_deg2": [366.0, 534.9, 508.5, 366.1], "posible_stow_fijo": [False, False, False, False]},
    index=["tracker_M01 (actual)", "tracker_M05 (actual)", "tracker_M02 (actual)", "tracker_M03 (actual)"],
)


def test_get_anomalous_trackers_above_threshold():
    result = get_anomalous_trackers(_DIAG_DF, threshold=450.0)
    assert "M05" in result
    assert "M02" in result


def test_get_anomalous_trackers_normal_excluded():
    result = get_anomalous_trackers(_DIAG_DF, threshold=450.0)
    assert "M01" not in result
    assert "M03" not in result


def test_get_vwc_trend_declining():
    df = pd.DataFrame({
        "Time": pd.date_range("2025-06-01", periods=5, freq="6h"),
        "VWC_S1_mean": [0.30, 0.28, 0.26, 0.24, 0.22],
    })
    trend = get_vwc_trend(df)
    assert trend < 0


def test_get_vwc_trend_stable_near_zero():
    df = pd.DataFrame({
        "Time": pd.date_range("2025-06-01", periods=4, freq="6h"),
        "VWC_S1_mean": [0.28, 0.28, 0.29, 0.28],
    })
    trend = get_vwc_trend(df)
    assert abs(trend) < 0.005


def test_build_alert_list_includes_tracker_critical():
    df_modelo = pd.DataFrame({
        "Time": pd.date_range("2025-06-01", periods=4, freq="6h"),
        "VWC_S1_mean": [0.30, 0.29, 0.28, 0.27],
    })
    alerts = build_alert_list(_DIAG_DF, df_modelo)
    severities = [a["severity"] for a in alerts]
    assert "CRÍTICO" in severities


def test_build_alert_list_empty_when_no_issues():
    diag_ok = pd.DataFrame(
        {"varianza_deg2": [366.0, 366.1], "posible_stow_fijo": [False, False]},
        index=["tracker_M01 (actual)", "tracker_M03 (actual)"],
    )
    df_modelo = pd.DataFrame({
        "Time": pd.date_range("2025-06-01", periods=4, freq="6h"),
        "VWC_S1_mean": [0.30, 0.31, 0.30, 0.31],
    })
    alerts = build_alert_list(diag_ok, df_modelo)
    assert alerts == []
