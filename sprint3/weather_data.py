from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_HOURLY = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "cloud_cover",
    "shortwave_radiation",
    "wind_speed_10m",
]
WEATHER_COLUMN_MAP = {
    "temperature_2m": "weather_temperature_2m",
    "relative_humidity_2m": "weather_relative_humidity_2m",
    "precipitation": "weather_precipitation",
    "cloud_cover": "weather_cloud_cover",
    "shortwave_radiation": "weather_shortwave_radiation",
    "wind_speed_10m": "weather_wind_speed_10m",
}
WEATHER_COLUMNS = list(WEATHER_COLUMN_MAP.values())


def _coerce_target_date(target_date: str | date | None) -> date:
    if target_date is None:
        return date.today() - timedelta(days=1)
    if isinstance(target_date, datetime):
        return target_date.date()
    if isinstance(target_date, date):
        return target_date
    return datetime.strptime(target_date, "%Y-%m-%d").date()


def _request_json(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def build_weather_pending_metadata() -> dict[str, Any]:
    return {
        "source": "none",
        "coordinates_status": "missing",
        "notice": (
            "Meteorologia externa pendiente: pasar coordenadas reales de la planta "
            "con --latitude y --longitude para consultar Open-Meteo."
        ),
    }


def build_open_meteo_url(target_date: str | date | None, latitude: float, longitude: float) -> str:
    target = _coerce_target_date(target_date)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": target.isoformat(),
        "end_date": target.isoformat(),
        "hourly": ",".join(OPEN_METEO_HOURLY),
        "timezone": "auto",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }
    return f"{OPEN_METEO_ARCHIVE_URL}?{urlencode(params)}"


def fetch_open_meteo_weather(
    target_date: str | date | None,
    latitude: float,
    longitude: float,
    request_json: Callable[[str], dict[str, Any]] = _request_json,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    url = build_open_meteo_url(target_date, latitude, longitude)
    payload = request_json(url)
    hourly = payload.get("hourly", {})
    if "time" not in hourly:
        raise ValueError("Open-Meteo response does not include hourly time values")

    rows = pd.DataFrame({"Time": pd.to_datetime(hourly["time"])})
    for api_name, column_name in WEATHER_COLUMN_MAP.items():
        rows[column_name] = hourly.get(api_name, [pd.NA] * len(rows))
    rows["weather_source"] = "open-meteo"

    metadata = {
        "source": "open-meteo",
        "coordinates_status": "user_provided",
        "latitude": latitude,
        "longitude": longitude,
        "timezone": payload.get("timezone"),
        "api_url": url,
        "notice": (
            "Datos meteorologicos externos de Open-Meteo. Complementan el dataset, "
            "pero no sustituyen sensores internos de planta."
        ),
    }
    return rows[["Time", *WEATHER_COLUMNS, "weather_source"]], metadata
