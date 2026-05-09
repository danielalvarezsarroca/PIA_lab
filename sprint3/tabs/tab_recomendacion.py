import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import get_latest_record
from rule_engine import format_regime_label, get_active_rule_index
from styles import COLOR


def _policy_metric(title: str, value: str, detail: str, color: str = "#007aff") -> str:
    return f"""
    <div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));
                border:1px solid rgba(255,255,255,0.72);border-radius:20px;padding:14px 16px;
                box-shadow:0 16px 42px rgba(16,24,40,0.08),inset 0 1px 0 rgba(255,255,255,0.96),
                inset 0 -1px 0 rgba(60,60,67,0.08);position:relative;overflow:hidden;">
      <div style="position:absolute;left:14px;right:14px;top:0;height:3px;border-radius:999px;
                  background:linear-gradient(90deg,rgba(255,255,255,0),{color},rgba(255,255,255,0));opacity:0.78;"></div>
      <div style="font-size:10px;font-weight:780;color:#6e6e73;text-transform:uppercase;
                  letter-spacing:0.06em;margin-bottom:8px;">{title}</div>
      <div style="font-size:26px;font-weight:820;color:{color};line-height:1;">{value}</div>
      <div style="font-size:11px;color:#6e6e73;margin-top:8px;line-height:1.35;">{detail}</div>
    </div>"""


def _style_policy_fig(fig: go.Figure, height: int = 270) -> go.Figure:
    fig.update_layout(
        font_family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial",
        font_color="#1d1d1f",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(248,250,248,0.72)",
        margin=dict(l=8, r=8, t=34, b=8),
        xaxis=dict(showgrid=True, gridcolor="rgba(60,60,67,0.10)", zeroline=False, title=""),
        yaxis=dict(showgrid=False, title=""),
        height=height,
        showlegend=False,
    )
    return fig


def render_tab_recomendacion(
    df_rules: pd.DataFrame,
    df_modelo: pd.DataFrame,
    df_rl_policy: pd.DataFrame | None = None,
) -> None:
    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">Política de rotación</div>',
        unsafe_allow_html=True,
    )

    latest          = get_latest_record(df_modelo)
    current_iec     = float(latest.get("IEC", float("nan")))
    current_regime  = str(latest.get("tracking_regime", "—"))
    active_idx      = get_active_rule_index(df_rules, latest)

    if df_rules.empty:
        st.info("No se encontraron reglas.")
        return

    best_rule = df_rules.loc[df_rules["iec_mediana"].idxmax()]
    active_support = int(df_rules.iloc[active_idx]["soporte_obs"]) if active_idx is not None else 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(_policy_metric("IEC actual", f"{current_iec:.2f}", "estado operativo reciente", COLOR["green"]), unsafe_allow_html=True)
    with m2:
        rl_states = len(df_rl_policy) if df_rl_policy is not None and not df_rl_policy.empty else 0
        st.markdown(_policy_metric("Estados RL", str(rl_states), "política offline del masterdataset", "#1d1d1f"), unsafe_allow_html=True)
    with m3:
        st.markdown(_policy_metric("Mejor IEC", f"{float(best_rule['iec_mediana']):.2f}", str(best_rule["tipo"]), "#007aff"), unsafe_allow_html=True)
    with m4:
        st.markdown(_policy_metric("Soporte activo", str(active_support), "observaciones de la regla activa", "#6d5bd0"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    col_rec, col_table = st.columns([1, 2])

    # ── Active recommendation box ─────────────────────────────────────────────
    with col_rec:
        regime_label = format_regime_label(current_regime)
        active_rule_text = "—"
        active_iec_med   = float("nan")
        if active_idx is not None:
            active_row       = df_rules.iloc[active_idx]
            active_rule_text = active_row["regla"]
            active_iec_med   = float(active_row["iec_mediana"])

        st.markdown(
            f'<div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));'
            f'border:1px solid rgba(255,255,255,0.72);border-radius:22px;'
            f'padding:16px;box-shadow:0 16px 42px rgba(16,24,40,0.08),inset 0 1px 0 rgba(255,255,255,0.96);">'
            f'<div style="font-size:10px;font-weight:760;color:#64706d;text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:6px;">Régimen activo</div>'
            f'<div style="font-size:17px;font-weight:800;color:{COLOR["green"]};margin-bottom:10px;">'
            f'{regime_label}</div>'
            f'<div style="font-size:10px;font-weight:760;color:#64706d;text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:4px;">IEC actual</div>'
            f'<div style="font-size:30px;font-weight:820;color:{COLOR["green"]};margin-bottom:10px;line-height:1;">'
            f'{current_iec:.2f}</div>'
            f'<div style="font-size:10px;font-weight:760;color:#64706d;text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:4px;">Regla recomendada</div>'
            f'<div style="font-size:12px;color:#35413d;line-height:1.55;">{active_rule_text}</div>'
            f'<div style="font-size:11px;color:#64706d;margin-top:8px;">'
            f'IEC mediana regla: {active_iec_med:.2f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        gauge_pct = max(0, min(100, current_iec * 100))
        st.markdown(
            f'<div style="margin-top:12px;background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));'
            f'border:1px solid rgba(255,255,255,0.72);border-radius:22px;padding:14px 16px;'
            f'box-shadow:0 14px 34px rgba(16,24,40,0.07),inset 0 1px 0 rgba(255,255,255,0.96);">'
            f'<div style="display:flex;justify-content:space-between;font-size:11px;color:#6e6e73;font-weight:760;'
            f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:9px;"><span>Confianza IEC</span><span>{gauge_pct:.0f}%</span></div>'
            f'<div style="height:11px;border-radius:999px;background:linear-gradient(180deg,#e5e8ef,#f7f8fb);'
            f'overflow:hidden;box-shadow:inset 0 2px 5px rgba(16,24,40,0.12);">'
            f'<div style="height:100%;width:{gauge_pct:.0f}%;border-radius:999px;'
            f'background:linear-gradient(90deg,#ff3b30,#ffcc00,#2f8f68);"></div></div>'
            f'<div style="font-size:11px;color:#6e6e73;margin-top:9px;">Comparado con el rango IEC [0,1].</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if df_rl_policy is not None and not df_rl_policy.empty:
            best_rl = df_rl_policy.sort_values(["rl_reward", "observations"], ascending=[False, False]).iloc[0]
            crop_action = str(best_rl.get("crop_management_action", "sin_manejo_directo")).replace("_", " ")
            panel_action = str(best_rl.get("panel_action", "mantener_placas")).replace("_", " ")
            st.markdown(
                f'<div style="margin-top:12px;background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(235,244,255,0.90));'
                f'border:1px solid rgba(255,255,255,0.72);border-radius:22px;padding:14px 16px;'
                f'box-shadow:0 14px 34px rgba(10,132,255,0.10),inset 0 1px 0 rgba(255,255,255,0.96);">'
                f'<div style="font-size:10px;font-weight:760;color:#64706d;text-transform:uppercase;'
                f'letter-spacing:0.06em;margin-bottom:7px;">Mejor acción RL observada</div>'
                f'<div style="font-size:20px;font-weight:820;color:#0a84ff;">'
                f'{float(best_rl.get("rl_angle_deg", 0)):.0f}° · {panel_action}</div>'
                f'<div style="font-size:11px;color:#6e6e73;margin-top:7px;">'
                f'Manejo cultivo: {crop_action} · Reward {float(best_rl.get("rl_reward", 0)):.2f} · n={int(best_rl.get("observations", 0))} · '
                f'{best_rl.get("state_key", "")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Rules table ───────────────────────────────────────────────────────────
    with col_table:
        rules_plot = df_rules.copy().sort_values("iec_mediana", ascending=True)
        rules_plot["Regla"] = rules_plot["tipo"].astype(str)
        fig_rules = px.bar(
            rules_plot,
            x="iec_mediana",
            y="Regla",
            orientation="h",
            color="iec_mediana",
            color_continuous_scale=["#ff3b30", "#ffcc00", "#2f8f68"],
            text=rules_plot["iec_mediana"].map(lambda v: f"{v:.2f}"),
            title="Ranking de reglas por IEC mediana",
        )
        fig_rules.update_traces(textposition="outside", marker_line_width=0)
        fig_rules.update_coloraxes(showscale=False)
        st.plotly_chart(_style_policy_fig(fig_rules, height=260), use_container_width=True)

        st.markdown(
            '<div style="font-size:12px;font-weight:760;color:#64706d;margin-bottom:8px;">'
            'Reglas candidatas del Sprint 2</div>',
            unsafe_allow_html=True,
        )

        for i, row in df_rules.iterrows():
            is_active = (i == active_idx)
            bg  = "linear-gradient(180deg,#f3fbf7,#e7f5ee)" if is_active else "linear-gradient(180deg,#ffffff,#f5f7fb)"
            bdr = "#b8dccb" if is_active else COLOR["border"]
            lbdr = f"3px solid {COLOR['green']}" if is_active else f"1px solid {COLOR['border']}"
            tipo_bg  = "#dff1e8" if "alta" in str(row.get("tipo", "")) else "#edf5fb"
            tipo_clr = COLOR["green"] if "alta" in str(row.get("tipo", "")) else COLOR["blue"]
            active_badge = f'<span style="font-size:10px;font-weight:800;color:{COLOR["green"]};">ACTIVA</span>' if is_active else ""

            st.markdown(
                f'<div style="background:{bg};border:1px solid {bdr};border-radius:20px;'
                f'border-left:{lbdr};padding:12px 14px;margin-bottom:8px;'
                f'box-shadow:0 12px 30px rgba(16,24,40,0.06),inset 0 1px 0 rgba(255,255,255,0.92);">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'margin-bottom:6px;">'
                f'<span style="background:{tipo_bg};color:{tipo_clr};font-size:9px;'
                f'font-weight:700;padding:4px 10px;border-radius:999px;">{row.get("tipo","—")}</span>'
                f'<span style="font-size:11px;color:#64706d;">IEC mediana: '
                f'<b style="color:{COLOR["green"]};">{float(row.get("iec_mediana",0)):.2f}</b> · '
                f'n={int(row.get("soporte_obs",0))}</span>'
                f'{active_badge}'
                f'</div>'
                f'<div style="font-size:12px;color:#35413d;line-height:1.5;">{row.get("regla","—")}</div>'
                f'<div style="font-size:11px;color:#64706d;margin-top:5px;">{row.get("comentario","")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
