import math

import pandas as pd
import streamlit as st

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
    row         = _get_hour_record(df_modelo, hour)
    track_angle = float(row.get("track_mean", 0.0))
    iec_val     = float(row.get("IEC", float("nan")))
    regime      = str(row.get("tracking_regime", "—"))
    epar_s1     = float(row.get("ePAR_S1_mean", float("nan")))
    epar_s2     = float(row.get("ePAR_S2_mean", float("nan")))
    vwc_s1      = float(row.get("VWC_S1_mean", float("nan")))
    vwc_s2      = float(row.get("VWC_S2_mean", float("nan")))
    solar_elev  = float(row.get("solar_elevation_deg", estimate_solar_elevation(float(hour))))
    rec_angle   = get_recommended_angle(hour, df_modelo)
    regime_label = format_regime_label(regime)
    iec_safe    = iec_val if not math.isnan(iec_val) else 0.0
    active_idx  = get_active_rule_index(df_rules, iec_safe)
    in_range    = abs(track_angle - rec_angle) <= 5

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
        st.markdown(svg_html, unsafe_allow_html=True)
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

    # ── ePAR + VWC KPI cards ─────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    def _fmt(v: float, decimals: int) -> str:
        return f"{v:.{decimals}f}" if not math.isnan(v) else "—"
    with k1:
        st.markdown(card_html("ePAR S1", _fmt(epar_s1, 0), "µmol/m²/s", COLOR["green"]), unsafe_allow_html=True)
    with k2:
        st.markdown(card_html("ePAR S2", _fmt(epar_s2, 0), "µmol/m²/s", COLOR["green"]), unsafe_allow_html=True)
    with k3:
        st.markdown(card_html("VWC S1", _fmt(vwc_s1, 2), "m³/m³", COLOR["amber"]), unsafe_allow_html=True)
    with k4:
        st.markdown(card_html("VWC S2", _fmt(vwc_s2, 2), "m³/m³", COLOR["amber"]), unsafe_allow_html=True)

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
            'letter-spacing:0.06em;margin-bottom:10px;">🔩 Estado de los 10 trackers</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(5)
        for i, tracker_id in enumerate(_ALL_TRACKERS):
            is_anomaly = tracker_id in anomalous
            diag_rows  = [r for r in df_diagnostic.index if tracker_id in r]
            variance   = float(df_diagnostic.loc[diag_rows[0], "varianza_deg2"]) if diag_rows else float("nan")
            bg   = "#fef2f2" if is_anomaly else "#f0fdf4"
            bdr  = "#fca5a5" if is_anomaly else "#bbf7d0"
            clr  = COLOR["red"] if is_anomaly else COLOR["green"]
            icon = " ⚠" if is_anomaly else ""
            with cols[i % 5]:
                st.markdown(
                    f'<div style="background:{bg};border:1px solid {bdr};border-radius:8px;'
                    f'padding:9px;text-align:center;margin-bottom:6px;">'
                    f'<div style="font-size:13px;font-weight:700;color:{clr};">{tracker_id}{icon}</div>'
                    f'<div style="font-size:11px;color:#6b7280;margin-top:3px;">{variance:.0f} deg²</div>'
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
