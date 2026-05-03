import math

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from alert_logic import build_alert_list, get_anomalous_trackers
from rule_engine import format_regime_label, get_active_rule_index
from solar_logic import estimate_solar_elevation, get_recommended_angle
from svg_generator import generate_solar_svg
from styles import COLOR, card_html, iec_gauge_html

_ALL_TRACKERS = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10"]
_ANOMALY_THRESHOLD = 450.0


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
        icon  = "☀️"
        title = "Tracking de tarde — máximo rendimiento agrovoltaico"
        body  = (
            f"A las {hour:02d}:00h el sol está en su punto más alto (elevación {solar_elev:.0f}°). "
            f"Los paneles se inclinan <b>{angle_abs:.0f}° hacia el {direction}</b> siguiendo la regla de "
            f"Tracking PM, el régimen con mayor IEC registrado históricamente. "
            f"El ángulo {'coincide con' if in_range else 'se desvía del'} óptimo recomendado ({rec_angle:.0f}°). "
            f"IEC actual: <b>{iec_safe:.2f}</b> — zona {'óptima' if iec_safe >= 0.6 else 'media' if iec_safe >= 0.35 else 'crítica'}."
        )
    elif regime == "TRACKING_AM":
        icon  = "🌅"
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
        icon  = "🌙"
        title = "Posición horizontal — régimen de reposo"
        body  = (
            f"A las {hour:02d}:00h {reason}. "
            f"Ángulo ≈ {track_angle:.1f}° (prácticamente plano). "
            f"En este régimen el IEC es bajo ({iec_safe:.2f}) al no haber seguimiento activo del sol."
        )
    else:
        icon  = "🔧"
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
    return "⚠ Bajo umbral crítico (200 µmol/m²/s)", COLOR["red"]


def _vwc_label(v: float) -> tuple[str, str]:
    """Return (label, color) for a VWC value."""
    if math.isnan(v):
        return "Sin datos", COLOR["muted"]
    if v >= 30.0:
        return "Suelo bien hidratado", COLOR["green"]
    if v >= 20.0:
        return "Humedad adecuada", COLOR["amber"]
    return "⚠ Humedad crítica — riego necesario", COLOR["red"]


def _tracker_label(variance: float) -> tuple[str, str, str]:
    """Return (status_text, bg_color, border_color) for a tracker variance."""
    if math.isnan(variance):
        return "Sin datos", "#f9fafb", "#e5e7eb"
    if variance > _ANOMALY_THRESHOLD:
        return "⚠ Alta varianza", "#fef2f2", "#fca5a5"
    return "✓ Normal", "#f0fdf4", "#bbf7d0"


@st.fragment
def _render_interactive_section(df_modelo: pd.DataFrame, df_rules: pd.DataFrame) -> None:
    # ── Slider ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:15px;font-weight:700;color:#111827;margin-bottom:8px;">'
        '⏱ Hora del día — mueve para explorar el estado del sistema</div>',
        unsafe_allow_html=True,
    )
    hour = st.slider(
        "hora",
        min_value=6, max_value=21, value=13, step=1,
        format="%d:00", label_visibility="collapsed",
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

    # ── Natural language justification ────────────────────────────────────────
    icon, just_title, just_body = _angle_justification(
        hour, track_angle, rec_angle, regime, iec_safe, in_range, solar_elev
    )
    box_bg  = "#f0fdf4" if regime == "TRACKING_PM" else "#eff6ff" if regime == "TRACKING_AM" else "#f9fafb"
    box_bdr = "#bbf7d0" if regime == "TRACKING_PM" else "#bfdbfe" if regime == "TRACKING_AM" else "#e5e7eb"
    box_clr = "#15803d" if regime == "TRACKING_PM" else "#1d4ed8" if regime == "TRACKING_AM" else "#6b7280"
    st.markdown(
        f'<div style="background:{box_bg};border:1px solid {box_bdr};border-radius:12px;'
        f'padding:14px 18px;margin-bottom:16px;">'
        f'<div style="font-size:15px;font-weight:700;color:{box_clr};margin-bottom:6px;">'
        f'{icon} {just_title}</div>'
        f'<div style="font-size:13px;color:#374151;line-height:1.7;">{just_body}</div>'
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
        )
        # st.markdown strips SVG defs/gradients/filters — use components.html (iframe, no sanitizer)
        components.html(
            f"<html><body style='margin:0;padding:0;background:transparent;'>{svg_html}</body></html>",
            height=252,
            scrolling=False,
        )
        status_txt = "✓ En rango óptimo" if in_range else "⚠ Fuera del rango recomendado"
        status_clr = COLOR["green"] if in_range else COLOR["orange"]
        st.markdown(
            f'<div style="text-align:center;font-size:14px;font-weight:700;'
            f'color:{status_clr};margin-top:8px;">{status_txt}</div>',
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
                f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;'
                f'padding:12px 14px;margin-bottom:8px;">'
                f'<div style="font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;'
                f'letter-spacing:0.05em;">{lbl}</div>'
                f'<div style="font-size:22px;font-weight:700;color:{clr};margin-top:3px;">{val}</div>'
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
        '<div style="font-size:13px;font-weight:700;color:#111827;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:10px;">🔄 Reglas de rotación candidatas</div>',
        unsafe_allow_html=True,
    )
    if df_rules.empty:
        st.info("No se encontraron reglas.")
    else:
        for i, rule_row in df_rules.iterrows():
            is_active = (i == active_idx)
            bg    = "#f0fdf4" if is_active else "#ffffff"
            lbdr  = "4px solid #22c55e" if is_active else "1px solid #e5e7eb"
            bdr   = "#bbf7d0" if is_active else "#e5e7eb"
            tipo_bg  = "#dcfce7" if "alta" in str(rule_row.get("tipo", "")) else "#eff6ff"
            tipo_clr = "#15803d" if "alta" in str(rule_row.get("tipo", "")) else "#1d4ed8"
            active_badge = (
                '<span style="font-size:11px;font-weight:700;color:#16a34a;">● ACTIVA</span>'
                if is_active else ""
            )
            st.markdown(
                f'<div style="background:{bg};border:1px solid {bdr};border-radius:10px;'
                f'border-left:{lbdr};padding:12px 16px;margin-bottom:8px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'margin-bottom:6px;">'
                f'<span style="background:{tipo_bg};color:{tipo_clr};font-size:11px;font-weight:700;'
                f'padding:3px 10px;border-radius:8px;">{rule_row.get("tipo","—")}</span>'
                f'<span style="font-size:12px;color:#6b7280;">IEC mediana: '
                f'<b style="color:#16a34a;">{float(rule_row.get("iec_mediana",0)):.2f}</b>'
                f' · n={int(rule_row.get("soporte_obs",0))}</span>'
                f'{active_badge}'
                f'</div>'
                f'<div style="font-size:12px;color:#374151;line-height:1.6;">{rule_row.get("regla","—")}</div>'
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

    st.markdown("<hr style='border-color:#e5e7eb;margin:24px 0 16px;'>", unsafe_allow_html=True)

    # ── Static section: trackers + alerts (not in fragment) ───────────────────
    anomalous = get_anomalous_trackers(df_diagnostic, threshold=_ANOMALY_THRESHOLD)
    alerts    = build_alert_list(df_diagnostic, df_modelo)

    col_trackers, col_alerts = st.columns([2, 1])

    with col_trackers:
        st.markdown(
            '<div style="font-size:13px;font-weight:700;color:#111827;text-transform:uppercase;'
            'letter-spacing:0.06em;margin-bottom:6px;">🔩 Estado de los 10 trackers</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:11px;color:#6b7280;margin-bottom:10px;">'
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
                    f'<div style="background:{bg};border:1px solid {bdr};border-radius:8px;'
                    f'padding:10px 8px;text-align:center;margin-bottom:6px;">'
                    f'<div style="font-size:13px;font-weight:700;color:{clr};">{tracker_id}</div>'
                    f'<div style="font-size:10px;color:#6b7280;margin-top:2px;">{variance:.0f} deg²</div>'
                    f'<div style="font-size:10px;font-weight:600;color:{clr};margin-top:3px;">'
                    f'{status_txt}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_alerts:
        if alerts:
            st.markdown(
                f'<div style="font-size:13px;font-weight:700;color:#111827;text-transform:uppercase;'
                f'letter-spacing:0.06em;margin-bottom:8px;">🚨 Alertas activas ({len(alerts)})</div>',
                unsafe_allow_html=True,
            )
            for alert in alerts:
                sev_color = COLOR["red"] if alert["severity"] == "CRÍTICO" else COLOR["orange"]
                sev_bg    = "#fef2f2" if alert["severity"] == "CRÍTICO" else "#fff7ed"
                st.markdown(
                    f'<div style="background:{sev_bg};border-radius:8px;padding:12px;margin-bottom:8px;">'
                    f'<div style="font-size:13px;font-weight:700;color:#111827;">{alert["title"]}</div>'
                    f'<div style="font-size:11px;color:#6b7280;margin-top:4px;line-height:1.5;">'
                    f'{alert["description"]}</div>'
                    f'<div style="display:inline-block;background:{sev_color};color:#fff;font-size:10px;'
                    f'font-weight:700;padding:2px 8px;border-radius:6px;margin-top:6px;">'
                    f'{alert["severity"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("Sin alertas activas.")
