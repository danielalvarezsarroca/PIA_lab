import pandas as pd
import pytest
from data_loader import get_latest_record, get_modelo_path, get_rules_path, parse_tracker_name


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


def test_get_modelo_path_prefers_daily_updated_dataset(tmp_path, monkeypatch):
    base_modelo = tmp_path / "base_modelo.csv"
    updated_modelo = tmp_path / "outputs_daily" / "dataset_modelizacion_6h_updated.csv"
    updated_modelo.parent.mkdir()
    base_modelo.write_text("base", encoding="utf-8")
    updated_modelo.write_text("updated", encoding="utf-8")

    monkeypatch.setattr("data_loader.MODELO_PATH", base_modelo)
    monkeypatch.setattr("data_loader.UPDATED_MODELO_PATH", updated_modelo)

    assert get_modelo_path() == updated_modelo


def test_get_rules_path_falls_back_to_sprint2_rules_when_no_daily_rules(tmp_path, monkeypatch):
    base_rules = tmp_path / "candidate_rotation_rules.csv"
    updated_rules = tmp_path / "outputs_daily" / "candidate_rotation_rules_updated.csv"
    base_rules.write_text("rules", encoding="utf-8")

    monkeypatch.setattr("data_loader.RULES_PATH", base_rules)
    monkeypatch.setattr("data_loader.UPDATED_RULES_PATH", updated_rules)

    assert get_rules_path() == base_rules
