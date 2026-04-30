import pandas as pd
import streamlit as st

from solar_logic import estimate_solar_elevation, get_recommended_angle
from svg_generator import generate_solar_svg
from styles import COLOR


def render_tab_panel_solar(df_modelo: pd.DataFrame) -> None:
    st.markdown(
        '<div style="font-size:11px;font-weight:700;color:#111827;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">☀️ Posición del panel solar</div>',
        unsafe_allow_html=True,
    )

    # ── Hour slider ───────────────────────────────────────────────────────────
    hour = st.slider(
        "Hora del día — desplaza para simular la posición del sol y el ángulo óptimo",
        min_value=6,
        max_value=21,
        value=13,
        step=1,
        format="%d:00",
    )

    # ── Compute values for this hour ──────────────────────────────────────────
    solar_elev  = estimate_solar_elevation(float(hour))
    rec_angle   = get_recommended_angle(hour, df_modelo)

    hour_data = df_modelo[df_modelo["hour_of_day"] == hour].dropna(subset=["track_mean"])
    if hour_data.empty:
        track_angle = rec_angle
        iec_val     = float("nan")
        regime      = "—"
        irradiance  = 400.0
    else:
        row = hour_data.iloc[-1]
        track_angle = float(row["track_mean"])
        iec_val     = float(row.get("IEC", float("nan")))
        regime      = str(row.get("tracking_regime", "—"))
        irradiance  = float(row.get("Albedo_S1", 400.0)) * 10  # rough proxy

    in_range    = abs(track_angle - rec_angle) <= 5
    status_txt  = "✓ En rango óptimo" if in_range else "⚠ Fuera del rango recomendado"
    status_clr  = COLOR["green"] if in_range else COLOR["orange"]

    # ── SVG diagram ───────────────────────────────────────────────────────────
    svg_html = generate_solar_svg(
        hour=float(hour),
        track_angle=track_angle,
        rec_angle=rec_angle,
        solar_elevation=solar_elev,
        irradiance=irradiance,
    )

    col_svg, col_info = st.columns([3, 1])

    with col_svg:
        st.markdown(svg_html, unsafe_allow_html=True)

    with col_info:
        for lbl, val, clr in [
            ("Ángulo actual",        f"{track_angle:.1f}°",  COLOR["blue"]),
            ("Ángulo recomendado",   f"{rec_angle:.1f}°",    COLOR["green"]),
            ("Elevación solar",      f"{solar_elev:.1f}°",   COLOR["orange"]),
            ("IEC en esta hora",     f"{iec_val:.2f}" if not pd.isna(iec_val) else "—", COLOR["purple"]),
            ("Régimen",              regime,                  COLOR["muted"]),
        ]:
            st.markdown(
                f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;'
                f'padding:10px 12px;margin-bottom:8px;">'
                f'<div style="font-size:9px;font-weight:600;color:#6b7280;text-transform:uppercase;'
                f'letter-spacing:0.05em;">{lbl}</div>'
                f'<div style="font-size:18px;font-weight:700;color:{clr};margin-top:2px;">{val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;'
            f'padding:10px 12px;">'
            f'<div style="font-size:11px;font-weight:700;color:{status_clr};">{status_txt}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.caption(
        "Línea azul sólida = ángulo actual del dataset · línea verde discontinua = ángulo óptimo histórico para esa hora"
    )
