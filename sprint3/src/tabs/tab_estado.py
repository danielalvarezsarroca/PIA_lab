import math
import time
from base64 import b64encode

import pandas as pd
import streamlit as st

from agricultural_rules import CROP_PROFILES
from alert_logic import build_alert_list, get_anomalous_trackers
from data_loader import load_crop_risk_for_crop, load_dqn_policy_for_crop
from rl_policy import recommend_action_for_record
from solar_logic import estimate_solar_elevation, get_recommended_angle
from svg_generator import generate_solar_svg
from styles import COLOR, card_html

_ALL_TRACKERS = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10"]
_ANOMALY_THRESHOLD = 450.0
_HOUR_MIN = 6
_HOUR_MAX = 21
_DEFAULT_HOUR = 13
_CROP_ZONES = ("S1", "S2")


def _selected_crop_zone() -> str:
    selected = st.session_state.get("selected_crop_zone", _CROP_ZONES[0])
    selected = str(selected)
    return selected if selected in _CROP_ZONES else _CROP_ZONES[0]


def _selected_crop_type(crop_zone: str | None = None) -> str:
    crop_options = list(CROP_PROFILES.keys()) or ["lechuga"]
    zone = crop_zone or _selected_crop_zone()
    selected = st.session_state.get(f"selected_crop_type_{zone.lower()}", st.session_state.get("selected_crop_type", crop_options[0]))
    if isinstance(selected, (list, tuple)):
        selected = selected[0] if selected else crop_options[0]
    selected = str(selected)
    return selected if selected in crop_options else crop_options[0]


def _selected_crop_risk(fallback: pd.DataFrame | None) -> pd.DataFrame:
    crop_zone = _selected_crop_zone()
    selected = load_crop_risk_for_crop(_selected_crop_type(crop_zone), crop_zone=crop_zone)
    if not selected.empty:
        return selected
    return fallback if fallback is not None else pd.DataFrame()


def _get_hour_record(df_modelo: pd.DataFrame, hour: int) -> pd.Series:
    """Return a representative row for the given hour of day.
    Falls back to nearest available hour if no data for requested hour."""
    rows = df_modelo[df_modelo["hour_of_day"] == hour].dropna(subset=["track_mean"])
    if not rows.empty:
        return _representative_hour_row(rows)
    valid = df_modelo.dropna(subset=["track_mean"])
    if valid.empty:
        return df_modelo.iloc[-1]
    idx = (valid["hour_of_day"] - hour).abs().idxmin()
    nearest_hour = valid.loc[idx, "hour_of_day"]
    nearest_rows = valid[valid["hour_of_day"] == nearest_hour]
    return _representative_hour_row(nearest_rows)


def _representative_hour_row(rows: pd.DataFrame) -> pd.Series:
    """Pick the row closest to the average score for this hour."""
    for score_col in ("crop_score", "energy_score", "IEC"):
        if score_col in rows.columns:
            values = pd.to_numeric(rows[score_col], errors="coerce")
            if values.notna().any():
                target_value = values.mean()
                distance = (values - target_value).abs()
                return rows.loc[distance.idxmin()]

    for time_col in ("Time", "timestamp", "datetime", "date_time", "fecha_hora"):
        if time_col in rows.columns:
            parsed_time = pd.to_datetime(rows[time_col], errors="coerce")
            if parsed_time.notna().any():
                return rows.loc[parsed_time.idxmax()]
    return rows.iloc[-1]


def _finite_float(value: object, fallback: float = float("nan")) -> float:
    try:
        if pd.isna(value):
            return fallback
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if math.isfinite(parsed) else fallback


def _clamp_pct(value: float, *, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _dataset_scaled_pct(row: pd.Series, df_modelo: pd.DataFrame, value_col: str) -> float:
    """Scale a value against the full dataset: dataset min = 0%, max = 100%."""
    current_value = _finite_float(row.get(value_col), float("nan"))
    if math.isnan(current_value) or value_col not in df_modelo.columns:
        return 0.0

    values = pd.to_numeric(df_modelo[value_col], errors="coerce").dropna()
    if values.empty:
        return 0.0

    min_value = float(values.min())
    max_value = float(values.max())
    if math.isclose(min_value, max_value):
        return 100.0

    return _clamp_pct(((current_value - min_value) / (max_value - min_value)) * 100.0)


def _crop_health_pct(row: pd.Series, df_modelo: pd.DataFrame) -> float:
    return _dataset_scaled_pct(row, df_modelo, "crop_score")


def _energy_efficiency_pct(row: pd.Series, df_modelo: pd.DataFrame) -> float:
    if "GPOA_mean" in df_modelo.columns:
        return _dataset_scaled_pct(row, df_modelo, "GPOA_mean")
    return _dataset_scaled_pct(row, df_modelo, "energy_score")


def _raw_metric_value(
    row: pd.Series,
    primary_col: str,
    fallback_col: str | list[str] | tuple[str, ...] | None = None,
) -> tuple[str, float]:
    fallback_cols: list[str] = []
    if isinstance(fallback_col, str):
        fallback_cols = [fallback_col]
    elif fallback_col is not None:
        fallback_cols = list(fallback_col)

    for value_col in [primary_col, *fallback_cols]:
        if value_col in row.index:
            value = _finite_float(row.get(value_col), float("nan"))
            if not math.isnan(value):
                return value_col, value

    return primary_col, float("nan")


def _format_raw_value(value: float, suffix: str = "") -> str:
    if math.isnan(value):
        return "Sin datos"
    return f"{value:.2f}{suffix}"


def _score_button_html(label: str, value_pct: float, color: str, hint: str) -> str:
    value_pct = _clamp_pct(value_pct)
    return (
        f'<div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.90));'
        f'border:1px solid rgba(255,255,255,0.74);border-radius:18px;padding:12px 13px;'
        f'box-shadow:0 14px 30px rgba(16,24,40,0.08),inset 0 1px 0 rgba(255,255,255,0.96);">'
        f'<div style="font-size:10px;font-weight:800;color:#64706d;text-transform:uppercase;'
        f'letter-spacing:0.04em;line-height:1.25;">{label}</div>'
        f'<div style="font-size:25px;font-weight:850;color:{color};margin-top:5px;line-height:1;">'
        f'{value_pct:.0f}%</div>'
        f'<div style="font-size:11px;color:#6e6e73;margin-top:7px;line-height:1.3;">{hint}</div>'
        f'</div>'
    )


def _raw_metric_button_html(label: str, value_text: str, color: str, source: str) -> str:
    return (
        f'<div style="background:linear-gradient(180deg,rgba(255,255,255,0.96),rgba(248,250,252,0.88));'
        f'border:1px solid rgba(255,255,255,0.72);border-radius:16px;padding:10px 12px;'
        f'box-shadow:0 10px 24px rgba(16,24,40,0.06),inset 0 1px 0 rgba(255,255,255,0.94);">'
        f'<div style="font-size:10px;font-weight:800;color:#64706d;text-transform:uppercase;'
        f'letter-spacing:0.04em;line-height:1.25;">{label}</div>'
        f'<div style="font-size:19px;font-weight:820;color:{color};margin-top:5px;line-height:1.05;">'
        f'{value_text}</div>'
        f'<div style="font-size:10px;color:#8e8e93;margin-top:6px;line-height:1.25;">{source}</div>'
        f'</div>'
    )


def _get_query_hour() -> int:
    """Read hour from URL query params and clamp it to the dashboard range."""
    raw_hour = st.query_params.get("hour", str(_DEFAULT_HOUR))
    try:
        hour = int(raw_hour)
    except (TypeError, ValueError):
        hour = _DEFAULT_HOUR
    return max(_HOUR_MIN, min(_HOUR_MAX, hour))


def _matching_crop_record(df_crop_risk: pd.DataFrame | None, row: pd.Series) -> pd.Series:
    if df_crop_risk is None or df_crop_risk.empty or "Time" not in df_crop_risk.columns:
        return pd.Series(dtype="object")
    matches = df_crop_risk[pd.to_datetime(df_crop_risk["Time"]) == pd.to_datetime(row.get("Time"))]
    if matches.empty:
        hour = int(row.get("hour_of_day", _DEFAULT_HOUR))
        same_hour = df_crop_risk[df_crop_risk["hour_of_day"] == hour]
        return same_hour.iloc[-1] if not same_hour.empty else pd.Series(dtype="object")
    return matches.iloc[0]


def _rl_recommendation(
    df_rl_policy: pd.DataFrame | None,
    row: pd.Series,
    crop_record: pd.Series,
) -> pd.Series:
    if df_rl_policy is None or df_rl_policy.empty:
        return pd.Series(dtype="object")
    record = row.copy()
    if not crop_record.empty:
        record["stress_type"] = crop_record.get("stress_type", "estable")
    try:
        return recommend_action_for_record(df_rl_policy, record)
    except (ValueError, KeyError, TypeError):
        return pd.Series(dtype="object")


def _action_label(value: object, fallback: str = "—") -> str:
    if value is None or pd.isna(value):
        return fallback
    label = str(value).replace("_", " ").strip()
    return label[:1].upper() + label[1:] if label else fallback


def _zone_visual_state(
    crop_zone: str,
    row: pd.Series,
    next_row: pd.Series,
    fallback_rl_policy: pd.DataFrame | None,
    fallback_crop_risk: pd.DataFrame | None,
) -> dict[str, object]:
    """Resolve crop-specific agronomic state for one physical cultivation zone."""
    crop_type = _selected_crop_type(crop_zone)
    crop_risk_df = load_crop_risk_for_crop(crop_type, crop_zone=crop_zone)
    if crop_risk_df.empty and crop_zone == _selected_crop_zone() and fallback_crop_risk is not None:
        crop_risk_df = fallback_crop_risk

    crop_record = _matching_crop_record(crop_risk_df, row)
    next_crop_record = _matching_crop_record(crop_risk_df, next_row)

    rl_policy = load_dqn_policy_for_crop(crop_type, crop_zone=crop_zone)
    if rl_policy.empty and crop_zone == _selected_crop_zone() and fallback_rl_policy is not None:
        rl_policy = fallback_rl_policy

    rl_rec = _rl_recommendation(rl_policy, row, crop_record)
    next_rl_rec = _rl_recommendation(rl_policy, next_row, next_crop_record)
    management_action = str(
        rl_rec.get(
            "crop_management_action",
            crop_record.get("crop_management_action", "sin_manejo_directo"),
        )
    )
    crop_risk = crop_record.get("crop_risk_score", None) if not crop_record.empty else None

    return {
        "crop_type": crop_type,
        "crop_record": crop_record,
        "rl_rec": rl_rec,
        "next_rl_rec": next_rl_rec,
        "management_action": management_action,
        "crop_risk": crop_risk,
    }


def _next_hour(hour: int) -> int:
    """Return the next hour in the dashboard day cycle."""
    return _HOUR_MIN if hour >= _HOUR_MAX else hour + 1


def _render_svg_image(
    svg_html: str,
    *,
    min_height: int = 498,
    image_min_height: int = 478,
    alt: str = "Vista de placas y cultivo",
) -> None:
    """Render the SVG as a data image so Streamlit does not sanitize SVG tags."""
    encoded = b64encode(svg_html.encode("utf-8")).decode("ascii")
    st.html(
        "<div style='background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(241,246,252,0.86));"
        "border:1px solid rgba(255,255,255,0.72);border-radius:24px;padding:10px;"
        "box-shadow:0 20px 58px rgba(16,24,40,0.11),inset 0 1px 0 rgba(255,255,255,0.96);"
        f"min-height:{min_height}px;"
        "display:flex;align-items:stretch;'>"
        f"<img src='data:image/svg+xml;base64,{encoded}' "
        f"style='width:100%;height:100%;min-height:{image_min_height}px;display:block;border-radius:22px;' "
        f"alt='{alt}'>"
        "</div>"
    )


def _angle_justification(
    hour: int,
    track_angle: float,
    rec_angle: float,
    panel_action: str,
    crop_action: str,
    confidence: float | None,
    crop_health_pct: float,
    energy_efficiency_pct: float,
    in_range: bool,
    solar_elev: float,
) -> tuple[str, str, str]:
    """Return (icon, title, body) for the natural-language explanation box."""
    direction = "oeste" if track_angle > 0 else "este"
    angle_abs = abs(track_angle)

    panel_label = _action_label(panel_action)
    crop_label = _action_label(crop_action)
    confidence_text = (
        f"Confianza <b>{confidence * 100:.0f}%</b>. "
        if confidence is not None and not math.isnan(confidence)
        else ""
    )
    status = "coincide con" if in_range else "se desvía del"

    if panel_action == "aumentar_sombreado":
        icon = "◐"
        title = "Aumentar sombra"
    elif panel_action == "reducir_sombreado":
        icon = "☀"
        title = "Reducir sombra"
    elif panel_action == "posicion_segura":
        icon = "−"
        title = "Posición segura"
    else:
        icon = "◇"
        title = "Mantener placas"

    body = (
        f"A las {hour:02d}:00h se sugiere <b>{panel_label}</b> "
        f"con objetivo <b>{rec_angle:.0f}°</b>. El registro actual muestra "
        f"<b>{angle_abs:.0f}° hacia el {direction}</b> y {status} objetivo. "
        f"{confidence_text}Acción sobre el cultivo: <b>{crop_label}</b>. Elevación solar {solar_elev:.0f}°. "
        f"Salud del cultivo <b>{crop_health_pct:.0f}%</b> y eficiencia energética "
        f"<b>{energy_efficiency_pct:.0f}%</b>."
    )

    return icon, title, body


def _epar_label(v: float) -> tuple[str, str]:
    """Return (label, color) for an ePAR value."""
    if math.isnan(v):
        return "Sin datos", COLOR["muted"]
    if v >= 500:
        return "Mucha luz para el cultivo", COLOR["green"]
    if v >= 200:
        return "Luz suficiente para el cultivo", COLOR["green"]
    return "Poca luz: vigilar crecimiento", COLOR["red"]


def _vwc_label(v: float) -> tuple[str, str]:
    """Return (label, color) for a VWC value."""
    if math.isnan(v):
        return "Sin datos", COLOR["muted"]
    if v >= 30.0:
        return "Suelo bien hidratado", COLOR["green"]
    if v >= 20.0:
        return "Humedad adecuada", COLOR["amber"]
    return "Humedad baja: conviene regar", COLOR["red"]


def _tracker_label(variance: float) -> tuple[str, str, str]:
    """Return (status_text, bg_color, border_color) for panel movement spread."""
    if math.isnan(variance):
        return "Sin datos", "#f9fafb", "#e5e7eb"
    if variance > _ANOMALY_THRESHOLD:
        return "Revisar", "#fff0ef", "#ffd1cf"
    return "Normal", "#eaf6ef", "#c9ead8"


@st.fragment(run_every="3s")
def _render_interactive_section(
    df_modelo: pd.DataFrame,
    df_rules: pd.DataFrame,
    df_rl_policy: pd.DataFrame | None = None,
    df_crop_risk: pd.DataFrame | None = None,
) -> None:
    del df_rules

    # ── Hour controls ─────────────────────────────────────────────────────────
    query_hour = _get_query_hour()
    query_autoplay = st.query_params.get("autoplay", "1") != "0"

    if "hour_slider" not in st.session_state:
        st.session_state["hour_slider"] = query_hour
    if "hour_autoplay" not in st.session_state:
        st.session_state["hour_autoplay"] = query_autoplay
    if "_last_auto_tick" not in st.session_state:
        st.session_state["_last_auto_tick"] = time.monotonic()

    # Streamlit widget state must be changed before the slider is instantiated.
    now = time.monotonic()
    if st.session_state["hour_autoplay"] and now - st.session_state["_last_auto_tick"] >= 2.8:
        st.session_state["hour_slider"] = _next_hour(int(st.session_state["hour_slider"]))
        st.session_state["_last_auto_tick"] = now
    elif not st.session_state["hour_autoplay"]:
        st.session_state["_last_auto_tick"] = now

    col_title, col_toggle = st.columns([0.62, 0.38])
    with col_title:
        st.markdown(
            '<div style="font-size:15px;font-weight:800;color:#1d1d1f;margin-bottom:4px;">'
            'Hora del día</div>'
            '<div style="font-size:12px;color:#6e6e73;margin-bottom:8px;">'
            'Avance automático cada 3 segundos, con selección manual disponible.</div>',
            unsafe_allow_html=True,
        )
    with col_toggle:
        st.markdown(
            """
            <style>
            .hour-autoplay-label {
                color: #1d1d1f !important;
                font-size: 0.9rem !important;
                font-weight: 700;
                line-height: 1;
                padding-top: 22px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        toggle_col, label_col = st.columns([0.52, 0.48], gap="small")
        with toggle_col:
            autoplay = st.toggle(
                "Auto",
                key="hour_autoplay",
                label_visibility="collapsed",
            )
        with label_col:
            st.markdown('<div class="hour-autoplay-label">Auto</div>', unsafe_allow_html=True)

    hour = st.slider(
        "Seleccionar hora",
        min_value=_HOUR_MIN,
        max_value=_HOUR_MAX,
        step=1,
        format="%d:00",
        key="hour_slider",
        label_visibility="collapsed",
    )

    st.markdown(
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'margin:-4px 0 18px;color:#8e8e93;font-size:12px;">'
        f'<span>{_HOUR_MIN}:00</span><span style="color:#007aff;font-weight:760;">{hour}:00</span>'
        f'<span>{_HOUR_MAX}:00</span></div>',
        unsafe_allow_html=True,
    )

    # ── Compute all values for selected hour ──────────────────────────────────
    row          = _get_hour_record(df_modelo, hour)
    track_angle  = float(row.get("track_mean", 0.0))
    epar_s1      = float(row.get("ePAR_S1_mean", float("nan")))
    epar_s2      = float(row.get("ePAR_S2_mean", float("nan")))
    vwc_s1       = float(row.get("VWC_S1_mean", float("nan")))
    vwc_s2       = float(row.get("VWC_S2_mean", float("nan")))
    solar_elev   = float(row.get("solar_elevation_deg", estimate_solar_elevation(float(hour))))
    rec_angle    = get_recommended_angle(hour, df_modelo)
    crop_record  = _matching_crop_record(df_crop_risk, row)
    rl_rec       = _rl_recommendation(df_rl_policy, row, crop_record)
    if not rl_rec.empty and pd.notna(rl_rec.get("rl_angle_deg")):
        rec_angle = float(rl_rec.get("rl_angle_deg"))
    panel_action = str(rl_rec.get("panel_action", crop_record.get("panel_action", "mantener_placas")))
    crop_action = str(
        rl_rec.get(
            "crop_management_action",
            crop_record.get("crop_management_action", "sin_manejo_directo"),
        )
    )
    rl_reward_raw = rl_rec.get("rl_reward", float("nan")) if not rl_rec.empty else float("nan")
    rl_confidence_raw = rl_rec.get("rl_confidence", rl_reward_raw) if not rl_rec.empty else float("nan")
    rl_confidence = float(rl_confidence_raw) if pd.notna(rl_confidence_raw) else float("nan")
    crop_health = _crop_health_pct(row, df_modelo)
    energy_efficiency = _energy_efficiency_pct(row, df_modelo)
    vwc_value_col, vwc_value = _raw_metric_value(row, "VWC_S1_mean")
    soil_temp_value_col, soil_temp_value = _raw_metric_value(row, "Tsoil_S1_mean")
    crop_light_value_col, crop_light_value = _raw_metric_value(row, "ePAR_S1_mean", "PAR_S1")
    ref_light_value_col, ref_light_value = _raw_metric_value(row, "ePAR_R1_mean", "PAR_R1")
    energy_value_col, energy_value = _raw_metric_value(row, "GPOA_mean")
    in_range     = abs(track_angle - rec_angle) <= 5

    next_visual_hour = _next_hour(hour) if autoplay else hour
    next_row         = _get_hour_record(df_modelo, next_visual_hour)
    next_track_angle = float(next_row.get("track_mean", track_angle))
    next_crop_record = _matching_crop_record(df_crop_risk, next_row)
    next_rl_rec      = _rl_recommendation(df_rl_policy, next_row, next_crop_record)
    next_rec_angle   = float(next_rl_rec.get("rl_angle_deg")) if not next_rl_rec.empty else get_recommended_angle(next_visual_hour, df_modelo)
    zone_visual_states = {
        zone: _zone_visual_state(zone, row, next_row, df_rl_policy, df_crop_risk)
        for zone in _CROP_ZONES
    }

    # ── Natural language justification ────────────────────────────────────────
    icon, just_title, just_body = _angle_justification(
        hour,
        track_angle,
        rec_angle,
        panel_action,
        crop_action,
        rl_confidence,
        crop_health,
        energy_efficiency,
        in_range,
        solar_elev,
    )
    box_bg  = "linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86))"
    box_bdr = "rgba(255,255,255,0.72)"
    box_clr = (
        COLOR["green"]
        if panel_action == "reducir_sombreado"
        else COLOR["blue"]
        if panel_action == "mantener_placas"
        else COLOR["purple"]
    )
    icon_class = "green" if panel_action == "reducir_sombreado" else "" if panel_action == "mantener_placas" else "amber"
    st.markdown(
        f'<div style="background:{box_bg};border:1px solid {box_bdr};border-radius:22px;'
        f'padding:16px 18px;margin-bottom:16px;box-shadow:0 16px 42px rgba(16,24,40,0.08),'
        f'inset 0 1px 0 rgba(255,255,255,0.96);'
        f'backdrop-filter:blur(20px) saturate(1.35);-webkit-backdrop-filter:blur(20px) saturate(1.35);">'
        f'<div style="font-size:15px;font-weight:760;color:{box_clr};margin-bottom:7px;">'
        f'<span class="apple-icon {icon_class}">{icon}</span>{just_title}</div>'
        f'<div style="font-size:13px;color:#424245;line-height:1.7;">{just_body}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── SVG panel (left) + metric cards (right) ───────────────────────────────
    col_svg, col_info = st.columns([3, 2])

    with col_svg:
        for index, zone in enumerate(_CROP_ZONES):
            state = zone_visual_states[zone]
            crop_risk_value = state["crop_risk"]
            svg_html = generate_solar_svg(
                hour=float(hour),
                track_angle=track_angle,
                rec_angle=rec_angle,
                solar_elevation=solar_elev,
                irradiance=400.0,
                next_hour=float(next_visual_hour),
                next_track_angle=next_track_angle,
                next_rec_angle=next_rec_angle,
                management_action=str(state["management_action"]),
                panel_action=panel_action,
                crop_risk=float(crop_risk_value) if crop_risk_value is not None and pd.notna(crop_risk_value) else None,
                crop_type=str(state["crop_type"]),
                crop_type_s1=_selected_crop_type("S1"),
                crop_type_s2=_selected_crop_type("S2"),
                zone_label=zone,
                show_zone_panel=False,
            )
            _render_svg_image(
                svg_html,
                min_height=382,
                image_min_height=362,
                alt=f"Vista solar zona {zone}",
            )
            if index < len(_CROP_ZONES) - 1:
                st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        status_txt = "Alineado con objetivo" if in_range else "Diferente al objetivo"
        status_clr = COLOR["green"] if in_range else COLOR["orange"]
        st.markdown(
            f'<div style="text-align:center;margin-top:10px;">'
            f'<span class="apple-status" style="font-size:14px;font-weight:760;color:{status_clr};">'
            f'<span class="apple-status-dot" style="background:{status_clr};"></span>{status_txt}</span></div>',
            unsafe_allow_html=True,
        )

    with col_info:
        st.markdown(
            "<div style='display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-bottom:10px;'>"
            + _score_button_html("Salud cultivo", crop_health, COLOR["green"], "Estado general")
            + _score_button_html("Eficiencia energética", energy_efficiency, COLOR["orange"], "Luz aprovechada")
            + _raw_metric_button_html("Humedad suelo", _format_raw_value(vwc_value, "%"), COLOR["green"], vwc_value_col)
            + _raw_metric_button_html("Temp. suelo", _format_raw_value(soil_temp_value, " °C"), COLOR["green"], soil_temp_value_col)
            + _raw_metric_button_html("Luz cultivo", _format_raw_value(crop_light_value), COLOR["blue"], crop_light_value_col)
            + _raw_metric_button_html("Luz referencia", _format_raw_value(ref_light_value), COLOR["blue"], ref_light_value_col)
            + _raw_metric_button_html(
                "Sol en placas",
                _format_raw_value(energy_value, " W/m²"),
                COLOR["orange"],
                energy_value_col,
            )
            + "</div>",
            unsafe_allow_html=True,
        )
        if not rl_rec.empty:
            confidence_label = f"{rl_confidence * 100:.0f}%" if not math.isnan(rl_confidence) else "Sin datos"
            st.markdown(
                f'<div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(235,244,255,0.90));'
                f'border:1px solid rgba(255,255,255,0.72);border-radius:20px;'
                f'padding:13px 15px;margin-bottom:9px;box-shadow:0 14px 34px rgba(10,132,255,0.10),'
                f'inset 0 1px 0 rgba(255,255,255,0.96);">'
                f'<div style="font-size:11px;font-weight:760;color:#64706d;text-transform:uppercase;'
                f'letter-spacing:0.05em;">Recomendación actual</div>'
                f'<div style="font-size:19px;font-weight:800;color:#0a84ff;margin-top:5px;">'
                f'Confianza {confidence_label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        for lbl, val, clr in [
            ("Ángulo actual",      f"{track_angle:.1f}°", COLOR["blue"]),
            ("Ángulo sugerido",    f"{rec_angle:.1f}°",   COLOR["green"]),
            ("Placas",            _action_label(panel_action), COLOR["purple"]),
            ("Elevación solar",    f"{solar_elev:.1f}°",  COLOR["orange"]),
        ]:
            st.markdown(
                f'<div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));'
                f'border:1px solid rgba(255,255,255,0.72);border-radius:20px;'
                f'padding:13px 15px;margin-bottom:9px;box-shadow:0 14px 34px rgba(16,24,40,0.07),'
                f'inset 0 1px 0 rgba(255,255,255,0.96);">'
                f'<div style="font-size:11px;font-weight:760;color:#64706d;text-transform:uppercase;'
                f'letter-spacing:0.05em;">{lbl}</div>'
                f'<div style="font-size:22px;font-weight:780;color:{clr};margin-top:3px;">{val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.caption(
        "Azul = posición actual · verde = posición sugerida"
    )


def render_tab_estado(
    df_modelo: pd.DataFrame,
    df_diagnostic: pd.DataFrame,
    df_rules: pd.DataFrame,
    df_rl_policy: pd.DataFrame | None = None,
    df_crop_risk: pd.DataFrame | None = None,
) -> None:
    df_crop_risk = _selected_crop_risk(df_crop_risk)
    _render_interactive_section(df_modelo, df_rules, df_rl_policy, df_crop_risk)

    st.markdown("<hr style='border-color:#dfe7e2;margin:24px 0 16px;'>", unsafe_allow_html=True)

    # ── Static section: panel movement + alerts (not in fragment) ─────────────
    anomalous = get_anomalous_trackers(df_diagnostic, threshold=_ANOMALY_THRESHOLD)
    alerts    = build_alert_list(df_diagnostic, df_modelo)

    col_trackers, col_alerts = st.columns([2, 1])

    with col_trackers:
        st.markdown(
            '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
            'letter-spacing:0.06em;margin-bottom:6px;">Estado de las placas</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:11px;color:#64706d;margin-bottom:10px;line-height:1.55;">'
            'Compara si cada placa se mueve de forma estable. '
            'Si el desvío es alto, conviene revisar el motor, el sensor o la comunicación.</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(5)
        for i, tracker_id in enumerate(_ALL_TRACKERS):
            is_anomaly = tracker_id in anomalous
            diag_rows  = [r for r in df_diagnostic.index if tracker_id in r]
            variance   = float(df_diagnostic.loc[diag_rows[0], "varianza_deg2"]) if diag_rows else float("nan")
            status_txt, bg, bdr = _tracker_label(variance)
            clr  = COLOR["red"] if is_anomaly else COLOR["green"]
            with cols[i % 5]:
                st.markdown(
                    f'<div style="background:linear-gradient(180deg,{bg},#ffffff);border:1px solid {bdr};border-radius:18px;'
                    f'padding:11px 8px;text-align:center;margin-bottom:7px;'
                    f'box-shadow:0 10px 22px rgba(16,24,40,0.07),inset 0 1px 0 rgba(255,255,255,0.92);">'
                    f'<div style="font-size:13px;font-weight:700;color:{clr};">{tracker_id}</div>'
                    f'<div style="font-size:10px;color:#64706d;margin-top:2px;">desvío {variance:.0f}</div>'
                    f'<div style="font-size:10px;font-weight:700;color:{clr};margin-top:3px;">'
                    f'{status_txt}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_alerts:
        if alerts:
            st.markdown(
                f'<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
                f'letter-spacing:0.06em;margin-bottom:8px;">Alertas activas ({len(alerts)})</div>',
                unsafe_allow_html=True,
            )
            for alert in alerts:
                sev_color = COLOR["red"] if alert["severity"] == "CRÍTICO" else COLOR["orange"]
                sev_bg    = "#fef2f2" if alert["severity"] == "CRÍTICO" else "#fff7ed"
                st.markdown(
                    f'<div style="background:linear-gradient(180deg,#ffffff,{sev_bg});border:1px solid rgba(255,255,255,0.72);'
                    f'border-radius:20px;padding:12px;margin-bottom:8px;'
                    f'box-shadow:0 12px 30px rgba(16,24,40,0.07),inset 0 1px 0 rgba(255,255,255,0.92);">'
                    f'<div style="font-size:13px;font-weight:760;color:#101820;">{alert["title"]}</div>'
                    f'<div style="font-size:11px;color:#64706d;margin-top:4px;line-height:1.5;">'
                    f'{alert["description"]}</div>'
                    f'<div style="display:inline-block;background:{sev_color};color:#fff;font-size:10px;'
                    f'font-weight:700;padding:2px 8px;border-radius:6px;margin-top:6px;">'
                    f'{alert["severity"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("Sin alertas activas.")
