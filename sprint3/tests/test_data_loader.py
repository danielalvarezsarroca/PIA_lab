import pandas as pd
import pytest
from data_loader import get_latest_record, load_crop_risk_for_crop, parse_tracker_name


def test_get_latest_record_returns_last_non_null_iec_row():
    df = pd.DataFrame({
        "Time": pd.to_datetime(["2025-06-01", "2025-06-02", "2025-06-03"]),
        "IEC": [0.3, 0.6, float("nan")],
        "track_mean": [20.0, 35.0, 40.0],
        "hour_of_day": [12, 12, 12],
    })
    result = get_latest_record(df)
    assert result["IEC"] == pytest.approx(0.6)
    assert result["track_mean"] == pytest.approx(35.0)


def test_get_latest_record_empty_raises():
    df = pd.DataFrame({"IEC": pd.Series([], dtype=float)})
    with pytest.raises(ValueError, match="No valid records"):
        get_latest_record(df)


def test_parse_tracker_name_extracts_id():
    assert parse_tracker_name("tracker_M04 (actual)") == "M04"
    assert parse_tracker_name("tracker_M10 (actual)") == "M10"


def test_parse_tracker_name_unknown_format_returns_raw():
    assert parse_tracker_name("something_weird") == "something_weird"


def test_load_crop_risk_for_cultivo_changes_actions():
    risk_lechuga = load_crop_risk_for_crop("lechuga")
    risk_brocoli = load_crop_risk_for_crop("brocoli")

    assert not risk_lechuga.empty
    assert not risk_brocoli.empty
    assert risk_lechuga["crop_type"].iloc[0] == "lechuga"
    assert risk_brocoli["crop_type"].iloc[0] == "brocoli"


def test_load_crop_risk_for_crop_accepts_independent_zone():
    risk_s2 = load_crop_risk_for_crop("patata", crop_zone="S2")

    assert not risk_s2.empty
    assert risk_s2["crop_type"].eq("patata").all()
    assert risk_s2["crop_zone"].eq("S2").all()
    assert "VWC_crop_zone_fraction" in risk_s2.columns
