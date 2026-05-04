import math
import time
from base64 import b64encode

import pandas as pd
import streamlit as st

from alert_logic import build_alert_list, get_anomalous_trackers
from rule_engine import format_regime_label, get_active_rule_index
from solar_logic import estimate_solar_elevation, get_recommended_angle
from svg_generator import generate_solar_svg
from styles import COLOR, card_html, iec_gauge_html

_ALL_TRACKERS = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10"]
_ANOMALY_THRESHOLD = 450.0
_HOUR_MIN = 6
_HOUR_MAX = 21
_DEFAULT_HOUR = 13


def _get_hour_record(df_modelo: pd.DataFrame, hour: int) -> pd.Series:
    """Return the row with the highest IEC for the given hour of day.
    Falls back to nearest available hour if no data for requested hour."""
    rows = df_modelo[df_modelo["hour_of_day"] == hour].dropna(subset=["IEC", "track_mean"])
    if not rows.empty:
        return rows.loc[rows["IEC"].idxmax()]
    valid = df_modelo.dropna(subset=["IEC", "track_mean"])
    if valid.empty:
        return df_modelo.iloc[-1]
    idx = (valid["hour_of_day"] - hour).abs().idxmin()
    return valid.loc[idx]


def _get_query_hour() -> int:
    """Read hour from URL query params and clamp it to the dashboard range."""
    raw_hour = st.query_params.get("hour", str(_DEFAULT_HOUR))
    try:
        hour = int(raw_hour)
    except (TypeError, ValueError):
        hour = _DEFAULT_HOUR
    return max(_HOUR_MIN, min(_HOUR_MAX, hour))


def _next_hour(hour: int) -> int:
    """Return the next hour in the dashboard day cycle."""
    return _HOUR_MIN if hour >= _HOUR_MAX else hour + 1


def _render_svg_image(svg_html: str) -> None:
    """Render the SVG as a data image so Streamlit does not sanitize SVG tags."""
    encoded = b64encode(svg_html.encode("utf-8")).decode("ascii")
    st.html(
        "<div style='background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(241,246,252,0.86));"
        "border:1px solid rgba(255,255,255,0.72);border-radius:24px;padding:10px;"
        "box-shadow:0 20px 58px rgba(16,24,40,0.11),inset 0 1px 0 rgba(255,255,255,0.96);"
        "min-height:388px;"
        "display:flex;align-items:stretch;'>"
        f"<img src='data:image/svg+xml;base64,{encoded}' "
        "style='width:100%;height:100%;min-height:368px;display:block;border-radius:22px;' "
        "alt='Visualización solar de trackers agrovoltaicos'>"
        "</div>"
    )


def _angle_justification(
    hour: int,
    track_angle: float,
    rec_angle: float,
    regime: str,
    iec_safe: float,
    in_range: bool,
    solar_elev: float,
) -> tuple[str, str, str]:
    """Return (icon, title, body) for the natural-language explanation box."""
    direction = "oeste" if track_angle > 0 else "este"
    angle_abs = abs(track_angle)

    if regime == "TRACKING_PM":
        icon  = "☀"
        title = "Tracking de tarde — máximo rendimiento agrovoltaico"
        body  = (
            f"A las {hour:02d}:00h el sol está en su punto más alto (elevación {solar_elev:.0f}°). "
            f"Los paneles se inclinan <b>{angle_abs:.0f}° hacia el {direction}</b> siguiendo la regla de "
            f"Tracking PM, el régimen con mayor IEC registrado históricamente. "
            f"El ángulo {'coincide con' if in_range else 'se desvía del'} óptimo recomendado ({rec_angle:.0f}°). "
            f"IEC actual: <b>{iec_safe:.2f}</b> — zona {'óptima' if iec_safe >= 0.6 else 'media' if iec_safe >= 0.35 else 'crítica'}."
        )
    elif regime == "TRACKING_AM":
        icon  = "↗"
        title = "Tracking de mañana — seguimiento del sol naciente"
        body  = (
            f"A las {hour:02d}:00h el sol sale por el este (elevación {solar_elev:.0f}°). "
            f"Los paneles apuntan <b>{angle_abs:.0f}° hacia el {direction}</b> para aprovechar "
            f"la irradiancia matinal. La regla de Tracking AM maximiza la producción en las primeras "
            f"horas del día, aunque el IEC ({iec_safe:.2f}) es menor que en la tarde."
        )
    elif regime == "HORIZONTAL":
        if hour <= 8 or hour >= 17:
            reason = (
                "el sol está bajo en el horizonte o ausente — "
                "los trackers se colocan en posición de reposo horizontal para protegerse del viento"
            )
        else:
            reason = "el sistema mantiene posición horizontal según la política activa"
        icon  = "−"
        title = "Posición horizontal — régimen de reposo"
        body  = (
            f"A las {hour:02d}:00h {reason}. "
            f"Ángulo ≈ {track_angle:.1f}° (prácticamente plano). "
            f"En este régimen el IEC es bajo ({iec_safe:.2f}) al no haber seguimiento activo del sol."
        )
    else:
        icon  = "◇"
        title = f"Régimen: {format_regime_label(regime)}"
        body  = f"Ángulo actual {track_angle:.1f}° · elevación solar {solar_elev:.0f}° · IEC {iec_safe:.2f}."

    return icon, title, body


def _epar_label(v: float) -> tuple[str, str]:
    """Return (label, color) for an ePAR value."""
    if math.isnan(v):
        return "Sin datos", COLOR["muted"]
    if v >= 500:
        return "Alta irradiancia PAR — condiciones óptimas", COLOR["green"]
    if v >= 200:
        return "Irradiancia PAR normal — cultivo activo", COLOR["green"]
    return "Bajo umbral crítico (200 µmol/m²/s)", COLOR["red"]


def _vwc_label(v: float) -> tuple[str, str]:
    """Return (label, color) for a VWC value."""
    if math.isnan(v):
        return "Sin datos", COLOR["muted"]
    if v >= 30.0:
        return "Suelo bien hidratado", COLOR["green"]
    if v >= 20.0:
        return "Humedad adecuada", COLOR["amber"]
    return "Humedad crítica — riego necesario", COLOR["red"]


def _tracker_label(variance: float) -> tuple[str, str, str]:
    """Return (status_text, bg_color, border_color) for a tracker variance."""
    if math.isnan(variance):
        return "Sin datos", "#f9fafb", "#e5e7eb"
    if variance > _ANOMALY_THRESHOLD:
        return "Alta varianza", "#fff0ef", "#ffd1cf"
    return "Normal", "#eaf6ef", "#c9ead8"


@st.fragment(run_every="3s")
def _render_interactive_section(df_modelo: pd.DataFrame, df_rules: pd.DataFrame) -> None:
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

    col_title, col_toggle = st.columns([0.72, 0.28])
    with col_title:
        st.markdown(
            '<div style="font-size:15px;font-weight:800;color:#1d1d1f;margin-bottom:4px;">'
            'Hora del día</div>'
            '<div style="font-size:12px;color:#6e6e73;margin-bottom:8px;">'
            'Avance automático cada 3 segundos, con selección manual disponible.</div>',
            unsafe_allow_html=True,
        )
    with col_toggle:
        autoplay = st.toggle(
            "Reproducción automática",
            key="hour_autoplay",
        )

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
    iec_val      = float(row.get("IEC", float("nan")))
    regime       = str(row.get("tracking_regime", "—"))
    epar_s1      = float(row.get("ePAR_S1_mean", float("nan")))
    epar_s2      = float(row.get("ePAR_S2_mean", float("nan")))
    vwc_s1       = float(row.get("VWC_S1_mean", float("nan")))
    vwc_s2       = float(row.get("VWC_S2_mean", float("nan")))
    solar_elev   = float(row.get("solar_elevation_deg", estimate_solar_elevation(float(hour))))
    rec_angle    = get_recommended_angle(hour, df_modelo)
    regime_label = format_regime_label(regime)
    iec_safe     = iec_val if not math.isnan(iec_val) else 0.0
    active_idx   = get_active_rule_index(df_rules, row)
    in_range     = abs(track_angle - rec_angle) <= 5

    next_visual_hour = _next_hour(hour) if autoplay else hour
    next_row         = _get_hour_record(df_modelo, next_visual_hour)
    next_track_angle = float(next_row.get("track_mean", track_angle))
    next_rec_angle   = get_recommended_angle(next_visual_hour, df_modelo)

    # ── Natural language justification ────────────────────────────────────────
    icon, just_title, just_body = _angle_justification(
        hour, track_angle, rec_angle, regime, iec_safe, in_range, solar_elev
    )
    box_bg  = "linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86))"
    box_bdr = "rgba(255,255,255,0.72)"
    box_clr = COLOR["green"] if regime == "TRACKING_PM" else COLOR["blue"] if regime == "TRACKING_AM" else COLOR["muted"]
    icon_class = "green" if regime == "TRACKING_PM" else "" if regime == "TRACKING_AM" else "amber"
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
        svg_html = generate_solar_svg(
            hour=float(hour),
            track_angle=track_angle,
            rec_angle=rec_angle,
            solar_elevation=solar_elev,
            irradiance=400.0,
            next_hour=float(next_visual_hour),
            next_track_angle=next_track_angle,
            next_rec_angle=next_rec_angle,
        )
        _render_svg_image(svg_html)
        status_txt = "En rango óptimo" if in_range else "Fuera del rango recomendado"
        status_clr = COLOR["green"] if in_range else COLOR["orange"]
        st.markdown(
            f'<div style="text-align:center;margin-top:10px;">'
            f'<span class="apple-status" style="font-size:14px;font-weight:760;color:{status_clr};">'
            f'<span class="apple-status-dot" style="background:{status_clr};"></span>{status_txt}</span></div>',
            unsafe_allow_html=True,
        )

    with col_info:
        st.markdown(iec_gauge_html(iec_safe), unsafe_allow_html=True)
        st.markdown("<div style='margin:10px 0;'></div>", unsafe_allow_html=True)
        for lbl, val, clr in [
            ("Ángulo actual",      f"{track_angle:.1f}°", COLOR["blue"]),
            ("Ángulo recomendado", f"{rec_angle:.1f}°",   COLOR["green"]),
            ("Régimen activo",     regime_label,           COLOR["purple"]),
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

    st.markdown("<div style='margin:14px 0;'></div>", unsafe_allow_html=True)

    # ── ePAR + VWC KPI cards with contextual status ───────────────────────────
    def _fmt(v: float, decimals: int) -> str:
        return f"{v:.{decimals}f}" if not math.isnan(v) else "—"

    k1, k2, k3, k4 = st.columns(4)
    epar_s1_lbl, epar_s1_clr = _epar_label(epar_s1)
    epar_s2_lbl, epar_s2_clr = _epar_label(epar_s2)
    vwc_s1_lbl,  vwc_s1_clr  = _vwc_label(vwc_s1)
    vwc_s2_lbl,  vwc_s2_clr  = _vwc_label(vwc_s2)

    with k1:
        st.markdown(card_html("ePAR S1", _fmt(epar_s1, 0), epar_s1_lbl, epar_s1_clr), unsafe_allow_html=True)
    with k2:
        st.markdown(card_html("ePAR S2", _fmt(epar_s2, 0), epar_s2_lbl, epar_s2_clr), unsafe_allow_html=True)
    with k3:
        st.markdown(card_html("VWC S1", _fmt(vwc_s1, 2), vwc_s1_lbl, vwc_s1_clr), unsafe_allow_html=True)
    with k4:
        st.markdown(card_html("VWC S2", _fmt(vwc_s2, 2), vwc_s2_lbl, vwc_s2_clr), unsafe_allow_html=True)

    st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

    # ── Rules table ───────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:10px;">Reglas de rotación candidatas</div>',
        unsafe_allow_html=True,
    )
    if df_rules.empty:
        st.info("No se encontraron reglas.")
    else:
        for i, rule_row in df_rules.iterrows():
            is_active = (i == active_idx)
            bg    = "linear-gradient(180deg,#f3fbf7,#e7f5ee)" if is_active else "linear-gradient(180deg,#ffffff,#f5f7fb)"
            lbdr  = f"4px solid {COLOR['green']}" if is_active else f"1px solid {COLOR['border']}"
            bdr   = "#b8dccb" if is_active else COLOR["border"]
            tipo_bg  = "#dff1e8" if "alta" in str(rule_row.get("tipo", "")) else "#edf5fb"
            tipo_clr = COLOR["green"] if "alta" in str(rule_row.get("tipo", "")) else COLOR["blue"]
            active_badge = (
                f'<span style="font-size:11px;font-weight:800;color:{COLOR["green"]};">ACTIVA</span>'
                if is_active else ""
            )
            st.markdown(
                f'<div style="background:{bg};border:1px solid {bdr};border-radius:20px;'
                f'border-left:{lbdr};padding:12px 16px;margin-bottom:8px;'
                f'box-shadow:0 12px 30px rgba(16,24,40,0.06),inset 0 1px 0 rgba(255,255,255,0.92);">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'margin-bottom:6px;">'
                f'<span style="background:{tipo_bg};color:{tipo_clr};font-size:11px;font-weight:700;'
                f'padding:4px 10px;border-radius:999px;">{rule_row.get("tipo","—")}</span>'
                f'<span style="font-size:12px;color:#64706d;">IEC mediana: '
                f'<b style="color:{COLOR["green"]};">{float(rule_row.get("iec_mediana",0)):.2f}</b>'
                f' · n={int(rule_row.get("soporte_obs",0))}</span>'
                f'{active_badge}'
                f'</div>'
                f'<div style="font-size:12px;color:#35413d;line-height:1.6;">{rule_row.get("regla","—")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.caption(
        "Azul sólido = ángulo actual del registro · verde discontinuo = ángulo óptimo histórico"
    )


def render_tab_estado(
    df_modelo: pd.DataFrame,
    df_diagnostic: pd.DataFrame,
    df_rules: pd.DataFrame,
) -> None:
    _render_interactive_section(df_modelo, df_rules)

    st.markdown("<hr style='border-color:#dfe7e2;margin:24px 0 16px;'>", unsafe_allow_html=True)

    # ── Static section: trackers + alerts (not in fragment) ───────────────────
    anomalous = get_anomalous_trackers(df_diagnostic, threshold=_ANOMALY_THRESHOLD)
    alerts    = build_alert_list(df_diagnostic, df_modelo)

    col_trackers, col_alerts = st.columns([2, 1])

    with col_trackers:
        st.markdown(
            '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
            'letter-spacing:0.06em;margin-bottom:6px;">Estado de los 10 trackers</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:11px;color:#64706d;margin-bottom:10px;line-height:1.55;">'
            'La varianza angular mide la estabilidad del seguimiento. '
            'Una varianza alta (&gt;450 deg²) indica que el tracker no sigue con precisión '
            'las consignas — posible fallo mecánico o de comunicación.</div>',
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
                    f'<div style="font-size:10px;color:#64706d;margin-top:2px;">{variance:.0f} deg²</div>'
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
