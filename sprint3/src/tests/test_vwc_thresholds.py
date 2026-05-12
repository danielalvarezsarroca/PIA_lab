from tabs.tab_estado import _vwc_label
from tabs.tab_series import _THRESHOLDS


def test_vwc_label_uses_percent_scale():
    hydrated_label, _ = _vwc_label(31.0)
    adequate_label, _ = _vwc_label(24.0)
    low_label, _ = _vwc_label(18.0)

    assert "bien hidratado" in hydrated_label
    assert "adecuada" in adequate_label
    assert "baja" in low_label


def test_vwc_series_thresholds_use_percent_scale():
    assert _THRESHOLDS["VWC_S1d13"][1] == 20.0
    assert _THRESHOLDS["VWC_S2d32"][1] == 20.0
