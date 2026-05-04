import pandas as pd
import pytest

from weather_data import (
    WEATHER_COLUMNS,
    build_open_meteo_url,
    build_weather_pending_metadata,
    fetch_open_meteo_weather,
)


def test_fetch_open_meteo_weather_maps_hourly_response_to_prefixed_columns():
    payload = {
        "latitude": 41.5,
        "longitude": 1.8,
        "timezone": "Europe/Madrid",
        "hourly": {
            "time": ["2026-05-03T00:00", "2026-05-03T06:00"],
            "temperature_2m": [12.4, 17.8],
            "relative_humidity_2m": [81, 64],
            "precipitation": [0.0, 0.2],
            "cloud_cover": [42, 55],
            "shortwave_radiation": [0.0, 180.0],
            "wind_speed_10m": [4.3, 8.1],
        },
    }

    rows, metadata = fetch_open_meteo_weather(
        target_date="2026-05-03",
        latitude=41.5,
        longitude=1.8,
        request_json=lambda _url: payload,
    )

    assert list(rows.columns) == ["Time", *WEATHER_COLUMNS, "weather_source"]
    assert rows["Time"].tolist() == pd.to_datetime(["2026-05-03 00:00", "2026-05-03 06:00"]).tolist()
    assert rows.loc[1, "weather_temperature_2m"] == pytest.approx(17.8)
    assert rows.loc[1, "weather_wind_speed_10m"] == pytest.approx(8.1)
    assert set(rows["weather_source"]) == {"open-meteo"}
    assert metadata["source"] == "open-meteo"
    assert metadata["coordinates_status"] == "user_provided"


def test_build_weather_pending_metadata_marks_missing_coordinates():
    metadata = build_weather_pending_metadata()

    assert metadata["source"] == "none"
    assert metadata["coordinates_status"] == "missing"
    assert "coordenadas reales" in metadata["notice"]


def test_build_open_meteo_url_accepts_default_target_date():
    url = build_open_meteo_url(target_date=None, latitude=41.5, longitude=1.8)

    assert "latitude=41.5" in url
    assert "longitude=1.8" in url
    assert "start_date=" in url
    assert "end_date=" in url
