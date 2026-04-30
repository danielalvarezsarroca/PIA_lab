import pandas as pd
import streamlit as st

from data_loader import get_latest_record
from rule_engine import format_regime_label, get_active_rule_index
from styles import COLOR


def render_tab_recomendacion(df_rules: pd.DataFrame, df_modelo: pd.DataFrame) -> None:
    st.markdown(
        '<div style="font-size:11px;font-weight:700;color:#111827;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">🔄 Política de rotación</div>',
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
            f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;'
            f'padding:16px;">'
            f'<div style="font-size:9px;font-weight:600;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:6px;">Régimen activo</div>'
            f'<div style="font-size:16px;font-weight:700;color:#15803d;margin-bottom:8px;">'
            f'{regime_label}</div>'
            f'<div style="font-size:9px;font-weight:600;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:4px;">IEC actual</div>'
            f'<div style="font-size:22px;font-weight:700;color:#16a34a;margin-bottom:8px;">'
            f'{current_iec:.2f}</div>'
            f'<div style="font-size:9px;font-weight:600;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:4px;">Regla recomendada</div>'
            f'<div style="font-size:10px;color:#374151;line-height:1.5;">{active_rule_text}</div>'
            f'<div style="font-size:9px;color:#6b7280;margin-top:6px;">'
            f'IEC mediana regla: {active_iec_med:.2f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Rules table ───────────────────────────────────────────────────────────
    with col_table:
        st.markdown(
            '<div style="font-size:10px;font-weight:600;color:#6b7280;margin-bottom:8px;">'
            'Reglas candidatas del Sprint 2</div>',
            unsafe_allow_html=True,
        )
        if df_rules.empty:
            st.info("No se encontraron reglas.")
            return

        for i, row in df_rules.iterrows():
            is_active = (i == active_idx)
            bg  = "#f0fdf4" if is_active else "#ffffff"
            bdr = "#16a34a" if is_active else "#e5e7eb"
            lbdr = "3px solid #22c55e" if is_active else "1px solid #e5e7eb"
            tipo_bg  = "#dcfce7" if "alta" in str(row.get("tipo", "")) else "#eff6ff"
            tipo_clr = "#15803d" if "alta" in str(row.get("tipo", "")) else "#1d4ed8"
            active_badge = '<span style="font-size:9px;font-weight:700;color:#16a34a;">● ACTIVA</span>' if is_active else ""

            st.markdown(
                f'<div style="background:{bg};border:{bdr};border-radius:10px;'
                f'border-left:{lbdr};padding:12px 14px;margin-bottom:8px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'margin-bottom:6px;">'
                f'<span style="background:{tipo_bg};color:{tipo_clr};font-size:9px;'
                f'font-weight:700;padding:2px 8px;border-radius:8px;">{row.get("tipo","—")}</span>'
                f'<span style="font-size:10px;color:#6b7280;">IEC mediana: '
                f'<b style="color:#16a34a;">{float(row.get("iec_mediana",0)):.2f}</b> · '
                f'n={int(row.get("soporte_obs",0))}</span>'
                f'{active_badge}'
                f'</div>'
                f'<div style="font-size:10px;color:#374151;line-height:1.5;">{row.get("regla","—")}</div>'
                f'<div style="font-size:9px;color:#6b7280;margin-top:4px;">{row.get("comentario","")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
