import pandas as pd
import streamlit as st

from data_loader import get_latest_record
from rule_engine import format_regime_label, get_active_rule_index
from styles import COLOR


def render_tab_recomendacion(df_rules: pd.DataFrame, df_modelo: pd.DataFrame) -> None:
    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">Política de rotación</div>',
        unsafe_allow_html=True,
    )

    latest          = get_latest_record(df_modelo)
    current_iec     = float(latest.get("IEC", float("nan")))
    current_regime  = str(latest.get("tracking_regime", "—"))
    active_idx      = get_active_rule_index(df_rules, current_iec)

    col_rec, col_table = st.columns([1, 2])

    # ── Active recommendation box ─────────────────────────────────────────────
    with col_rec:
        regime_label = format_regime_label(current_regime)
        active_rule_text = "—"
        active_iec_med   = float("nan")
        if active_idx is not None and not df_rules.empty:
            active_row       = df_rules.iloc[active_idx]
            active_rule_text = active_row["regla"]
            active_iec_med   = float(active_row["iec_mediana"])

        st.markdown(
            f'<div style="background:rgba(255,255,255,0.78);border:1px solid rgba(60,60,67,0.12);border-radius:18px;'
            f'padding:16px;box-shadow:0 12px 30px rgba(0,0,0,0.055);">'
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

    # ── Rules table ───────────────────────────────────────────────────────────
    with col_table:
        st.markdown(
            '<div style="font-size:12px;font-weight:760;color:#64706d;margin-bottom:8px;">'
            'Reglas candidatas del Sprint 2</div>',
            unsafe_allow_html=True,
        )
        if df_rules.empty:
            st.info("No se encontraron reglas.")
            return

        for i, row in df_rules.iterrows():
            is_active = (i == active_idx)
            bg  = "#e7f5ee" if is_active else "#ffffff"
            bdr = "#b8dccb" if is_active else COLOR["border"]
            lbdr = f"3px solid {COLOR['green']}" if is_active else f"1px solid {COLOR['border']}"
            tipo_bg  = "#dff1e8" if "alta" in str(row.get("tipo", "")) else "#edf5fb"
            tipo_clr = COLOR["green"] if "alta" in str(row.get("tipo", "")) else COLOR["blue"]
            active_badge = f'<span style="font-size:10px;font-weight:800;color:{COLOR["green"]};">ACTIVA</span>' if is_active else ""

            st.markdown(
                f'<div style="background:{bg};border:1px solid {bdr};border-radius:16px;'
                f'border-left:{lbdr};padding:12px 14px;margin-bottom:8px;">'
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
