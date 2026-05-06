import pandas as pd
import pytest
from data_loader import get_latest_record, parse_tracker_name


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
