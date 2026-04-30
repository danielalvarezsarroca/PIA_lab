import pandas as pd
import streamlit as st

from alert_logic import build_alert_list, get_anomalous_trackers
from data_loader import get_latest_record
from rule_engine import format_regime_label, get_active_rule_index
from styles import COLOR, card_html, iec_gauge_html

_ALL_TRACKERS = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10"]
_ANOMALY_THRESHOLD = 450.0


def render_tab_estado(
    df_modelo: pd.DataFrame,
    df_diagnostic: pd.DataFrame,
    df_rules: pd.DataFrame,
) -> None:
    latest = get_latest_record(df_modelo)
    anomalous = get_anomalous_trackers(df_diagnostic, threshold=_ANOMALY_THRESHOLD)
    alerts = build_alert_list(df_diagnostic, df_modelo)
    active_rule_idx = get_active_rule_index(df_rules, float(latest.get("IEC", float("nan"))))

    # ── Header timestamp ──────────────────────────────────────────────────────
    ts = pd.to_datetime(latest["Time"]).strftime("%d %b %Y · %H:%M") if "Time" in latest.index else "—"
    col_ts, col_badge = st.columns([3, 1])
    with col_ts:
        st.caption(f"Último registro disponible · {ts}")
    with col_badge:
        st.markdown(
            f'<div style="text-align:right;"><span style="background:#f0fdf4;border:1px solid #bbf7d0;'
            f'color:#15803d;font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;">'
            f'● Sistema activo</span></div>',
            unsafe_allow_html=True,
        )

    # ── KPI row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    track = latest.get("track_mean", float("nan"))
    epar  = (latest.get("ePAR_S1_mean", 0) + latest.get("ePAR_S2_mean", 0)) / 2
    vwc   = (latest.get("VWC_S1_mean", 0) + latest.get("VWC_S2_mean", 0)) / 2
    iec   = latest.get("IEC", float("nan"))

    with c1:
        st.markdown(card_html("Ángulo tracking", f"{track:.1f}°", "track_mean · media trackers", COLOR["blue"]), unsafe_allow_html=True)
    with c2:
        st.markdown(card_html("ePAR media", f"{epar:.0f}", "µmol/m²/s · S1+S2", COLOR["green"]), unsafe_allow_html=True)
    with c3:
        st.markdown(card_html("VWC suelo", f"{vwc:.2f}", "m³/m³ · S1+S2", COLOR["amber"]), unsafe_allow_html=True)
    with c4:
        st.markdown(card_html("Índice IEC", f"{iec:.2f}" if not pd.isna(iec) else "—", "Energía–Cultivo", COLOR["purple"]), unsafe_allow_html=True)
    with c5:
        n_anom = len(anomalous)
        color_anom = COLOR["red"] if n_anom > 0 else COLOR["green"]
        st.markdown(card_html("Trackers anómalos", f"{n_anom}/10", ", ".join(anomalous) or "Ninguno", color_anom), unsafe_allow_html=True)

    st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)

    # ── Tracker grid + IEC + Recomendación ───────────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;color:{COLOR["text"]};'
            f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">'
            f'🔩 Estado de los 10 trackers</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(5)
        for i, tracker_id in enumerate(_ALL_TRACKERS):
            is_anomaly = tracker_id in anomalous
            diag_rows = [r for r in df_diagnostic.index if tracker_id in r]
            variance = float(df_diagnostic.loc[diag_rows[0], "varianza_deg2"]) if diag_rows else float("nan")
            bg   = "#fef2f2" if is_anomaly else "#f0fdf4"
            bdr  = "#fca5a5" if is_anomaly else "#bbf7d0"
            clr  = COLOR["red"] if is_anomaly else COLOR["green"]
            icon = " ⚠" if is_anomaly else ""
            with cols[i % 5]:
                st.markdown(
                    f'<div style="background:{bg};border:1px solid {bdr};border-radius:8px;'
                    f'padding:7px;text-align:center;margin-bottom:6px;">'
                    f'<div style="font-size:10px;font-weight:700;color:{clr};">{tracker_id}{icon}</div>'
                    f'<div style="font-size:8px;color:#6b7280;margin-top:2px;">{variance:.0f} deg²</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_right:
        st.markdown(iec_gauge_html(float(iec) if not pd.isna(iec) else 0.0), unsafe_allow_html=True)
        st.markdown("<div style='margin:8px 0;'></div>", unsafe_allow_html=True)

        regime = latest.get("tracking_regime", "—")
        regime_label = format_regime_label(str(regime))
        rule_text = "—"
        if active_rule_idx is not None and not df_rules.empty:
            rule_text = df_rules.iloc[active_rule_idx]["regla"][:80] + "…"

        st.markdown(
            f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;'
            f'padding:12px 14px;">'
            f'<div style="font-size:9px;font-weight:600;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:4px;">Régimen activo</div>'
            f'<div style="font-size:14px;font-weight:700;color:#15803d;">{regime_label}</div>'
            f'<div style="font-size:9px;color:#6b7280;margin-top:6px;line-height:1.4;">{rule_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Alert summary ─────────────────────────────────────────────────────────
    if alerts:
        st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;color:{COLOR["text"]};'
            f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">'
            f'🚨 Alertas activas ({len(alerts)})</div>',
            unsafe_allow_html=True,
        )
        for alert in alerts:
            sev_color = COLOR["red"] if alert["severity"] == "CRÍTICO" else COLOR["orange"]
            sev_bg    = "#fef2f2" if alert["severity"] == "CRÍTICO" else "#fff7ed"
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:10px;'
                f'padding:10px 0;border-bottom:1px solid #f3f4f6;">'
                f'<div style="width:8px;height:8px;border-radius:50%;background:{sev_color};'
                f'margin-top:4px;flex-shrink:0;"></div>'
                f'<div style="flex:1;">'
                f'<div style="font-size:11px;font-weight:600;color:#111827;">{alert["title"]}</div>'
                f'<div style="font-size:10px;color:#6b7280;margin-top:2px;">{alert["description"]}</div>'
                f'</div>'
                f'<div style="background:{sev_bg};color:{sev_color};font-size:8px;font-weight:700;'
                f'padding:2px 7px;border-radius:8px;flex-shrink:0;">{alert["severity"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
