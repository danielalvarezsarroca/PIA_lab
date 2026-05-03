import pandas as pd
import streamlit as st

from alert_logic import build_alert_list
from styles import COLOR


def render_tab_alertas(df_diagnostic: pd.DataFrame, df_modelo: pd.DataFrame) -> None:
    alerts = build_alert_list(df_diagnostic, df_modelo)

    # ── Header with count ─────────────────────────────────────────────────────
    n = len(alerts)
    header_clr = COLOR["red"] if n > 0 else COLOR["green"]
    header_txt = f"{n} alerta{'s' if n != 1 else ''} activa{'s' if n != 1 else ''}"
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">'
        f'<span style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        f'letter-spacing:0.06em;">Alertas del sistema</span>'
        f'<span style="background:{"#fee8e8" if n>0 else "#e7f5ee"};'
        f'color:{header_clr};border:1px solid rgba(60,60,67,0.10);border-radius:999px;padding:3px 11px;font-size:10px;font-weight:760;">'
        f'{header_txt}</span></div>',
        unsafe_allow_html=True,
    )

    if not alerts:
        st.success("Sin alertas activas. Todos los parámetros dentro de rangos normales.")
    else:
        for alert in alerts:
            sev_color = COLOR["red"] if alert["severity"] == "CRÍTICO" else COLOR["orange"]
            sev_bg    = "#fee8e8" if alert["severity"] == "CRÍTICO" else "#fff4e5"
            bdr_clr   = "#efb1b1" if alert["severity"] == "CRÍTICO" else "#efc280"
            icon      = "!" if alert["severity"] == "CRÍTICO" else "•"
            icon_class = "red" if alert["severity"] == "CRÍTICO" else "amber"
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:12px;'
                f'background:{sev_bg};border:1px solid {bdr_clr};border-left:4px solid {sev_color};'
                f'border-radius:18px;padding:14px 16px;margin-bottom:10px;box-shadow:0 10px 26px rgba(0,0,0,0.055);">'
                f'<span class="apple-icon {icon_class}" style="flex-shrink:0;margin-right:0;">{icon}</span>'
                f'<div style="flex:1;">'
                f'<div style="font-size:13px;font-weight:760;color:#101820;">{alert["title"]}</div>'
                f'<div style="font-size:11px;color:#64706d;margin-top:4px;line-height:1.5;">{alert["description"]}</div>'
                f'</div>'
                f'<div style="background:{sev_color};color:#fff;font-size:9px;font-weight:700;'
                f'padding:4px 10px;border-radius:999px;flex-shrink:0;margin-top:2px;">{alert["severity"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Tracker diagnostic table ──────────────────────────────────────────────
    st.markdown("<div style='margin:20px 0 8px;'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:12px;font-weight:760;color:#64706d;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:8px;">Diagnóstico de varianza — todos los trackers</div>',
        unsafe_allow_html=True,
    )

    diag_display = df_diagnostic.copy()
    diag_display.index = [idx.replace(" (actual)", "") for idx in diag_display.index]
    diag_display = diag_display.sort_values("varianza_deg2", ascending=False)
    diag_display["Estado"] = diag_display["varianza_deg2"].apply(
        lambda v: "Alta varianza" if v > 450 else "Normal"
    )
    diag_display = diag_display.rename(columns={
        "varianza_deg2":   "Varianza (deg²)",
        "posible_stow_fijo": "Stow fijo",
    })
    st.dataframe(diag_display, use_container_width=True)
    st.caption("Umbral de anomalía: varianza > 450 deg²")

    # ── VWC history ───────────────────────────────────────────────────────────
    if "VWC_S1_mean" in df_modelo.columns:
        st.markdown("<div style='margin:16px 0 8px;'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:12px;font-weight:760;color:#64706d;text-transform:uppercase;'
            'letter-spacing:0.06em;margin-bottom:8px;">Evolución VWC — últimas 48h</div>',
            unsafe_allow_html=True,
        )
        import plotly.express as px
        last_48h = df_modelo[["Time", "VWC_S1_mean", "VWC_S2_mean"]].dropna().tail(8)
        if not last_48h.empty:
            df_long = last_48h.melt("Time", var_name="Sección", value_name="VWC")
            fig = px.line(df_long, x="Time", y="VWC", color="Sección",
                          color_discrete_map={"VWC_S1_mean": "#b66a00", "VWC_S2_mean": "#9a4d00"},
                          template="simple_white", height=200)
            fig.add_hline(y=0.20, line_dash="dash", line_color="#c83737",
                          annotation_text="umbral crítico 0.20", annotation_font_size=9)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=0),
                              font_family="-apple-system, 'Helvetica Neue', Arial",
                              font_color="#101820",
                              paper_bgcolor="#ffffff", plot_bgcolor="#f8faf8",
                              xaxis=dict(gridcolor="#dfe7e2", zeroline=False),
                              yaxis=dict(gridcolor="#dfe7e2", zeroline=False))
            st.plotly_chart(fig, use_container_width=True)
