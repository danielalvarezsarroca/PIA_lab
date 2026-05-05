from __future__ import annotations

import html
from base64 import b64encode

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from agricultural_rules import ACTION_LABELS, CROP_PROFILES
from styles import COLOR, card_html


def _fig_style(fig: go.Figure, height: int = 270) -> go.Figure:
    fig.update_layout(
        font_family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(248,250,248,0.72)",
        font_color="#1d1d1f",
        margin=dict(l=10, r=10, t=34, b=8),
        xaxis=dict(showgrid=True, gridcolor="rgba(60,60,67,0.10)", title="", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(60,60,67,0.10)", title="", zeroline=False),
        height=height,
    )
    return fig


def select_action_record(crop_risk: pd.DataFrame, action: str | None = None) -> pd.Series:
    if crop_risk.empty:
        raise ValueError("crop_risk dataset is empty")
    df = crop_risk.copy()
    if action:
        filtered = df[df["recommended_action"] == action]
        if not filtered.empty:
            return filtered.sort_values("crop_risk_score", ascending=False).iloc[0]
    actionable = df[df["recommended_action"] != "mantener"]
    if actionable.empty:
        return df.sort_values("Time").iloc[-1]
    return actionable.sort_values(["crop_risk_score", "IEC"], ascending=[False, False]).iloc[0]


def action_visual_state(action: str) -> dict[str, float | str]:
    states = {
        "regar": {"accent": "#0a84ff", "water_opacity": 0.95, "shade_opacity": 0.18, "blade_angle": -8.0},
        "riego_preventivo": {"accent": "#0a84ff", "water_opacity": 0.70, "shade_opacity": 0.46, "blade_angle": 18.0},
        "pausar_riego": {"accent": "#6e6e73", "water_opacity": 0.05, "shade_opacity": 0.18, "blade_angle": 0.0},
        "aumentar_sombreado": {"accent": "#0a84ff", "water_opacity": 0.08, "shade_opacity": 0.68, "blade_angle": 28.0},
        "reducir_sombreado": {"accent": "#ff9f0a", "water_opacity": 0.06, "shade_opacity": 0.08, "blade_angle": -22.0},
        "posicion_segura": {"accent": "#ff3b30", "water_opacity": 0.04, "shade_opacity": 0.32, "blade_angle": 0.0},
        "alerta_frio": {"accent": "#64d2ff", "water_opacity": 0.02, "shade_opacity": 0.12, "blade_angle": 4.0},
        "mantener": {"accent": "#2f8f68", "water_opacity": 0.10, "shade_opacity": 0.24, "blade_angle": 12.0},
    }
    return states.get(action, states["mantener"])


def crop_scene_svg(row: pd.Series, crop_label: str) -> str:
    action = str(row.get("recommended_action", "mantener"))
    label = str(row.get("action_label", ACTION_LABELS.get(action, action)))
    stress = str(row.get("stress_type", "estable")).replace("_", " ")
    state = action_visual_state(action)
    accent = str(state["accent"])
    water_opacity = float(state["water_opacity"])
    shade_opacity = float(state["shade_opacity"])
    blade_angle = float(state["blade_angle"])
    health = max(0.0, min(1.0, float(row.get("crop_health_score", 0.0))))
    health_width = health * 270

    plants = []
    for idx, x in enumerate(range(74, 520, 42)):
        y = 250 + (idx % 3) * 2
        scale = 0.92 + (health * 0.25)
        plants.append(
            f"""<g transform="translate({x},{y}) scale({scale:.2f})">
              <path d="M0 28 C0 14 4 6 10 0 C16 8 17 18 10 31 Z" fill="#60bf84"/>
              <path d="M10 31 C7 16 16 8 28 6 C28 20 20 29 10 31 Z" fill="#4da873"/>
              <path d="M10 31 C9 17 0 9 -12 8 C-11 22 0 31 10 31 Z" fill="#75cf96"/>
              <line x1="10" y1="34" x2="10" y2="14" stroke="#2f8f68" stroke-width="2" stroke-linecap="round"/>
            </g>"""
        )

    svg = f"""<svg viewBox="0 0 640 360" xmlns="http://www.w3.org/2000/svg" role="img"
    aria-label="Escena agronomica para {html.escape(crop_label)}" style="width:100%;height:100%;display:block;border-radius:24px;">
  <defs>
    <linearGradient id="agroSky" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f9fbff"/>
      <stop offset="48%" stop-color="#eaf3ff"/>
      <stop offset="100%" stop-color="#f5fbf6"/>
    </linearGradient>
    <linearGradient id="soil" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#d7b98f"/>
      <stop offset="100%" stop-color="#a8794f"/>
    </linearGradient>
    <linearGradient id="blade" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#6ea8ff"/>
      <stop offset="50%" stop-color="#1d1d1f"/>
      <stop offset="100%" stop-color="#48484a"/>
    </linearGradient>
    <filter id="softShadow"><feDropShadow dx="0" dy="14" stdDeviation="12" flood-color="#102030" flood-opacity="0.16"/></filter>
  </defs>
  <rect width="640" height="360" rx="24" fill="url(#agroSky)"/>
  <circle cx="545" cy="64" r="38" fill="#ffe58a" opacity="0.92">
    <animate attributeName="r" values="36;40;36" dur="3s" repeatCount="indefinite"/>
  </circle>
  <path d="M0 254 C120 232 220 244 336 236 C466 228 552 236 640 218 L640 360 L0 360 Z" fill="url(#soil)" opacity="0.92"/>
  <ellipse cx="324" cy="244" rx="268" ry="64" fill="#6ed18b" opacity="0.24"/>
  <g opacity="{shade_opacity:.2f}">
    <path d="M52 112 C190 72 392 76 588 116 L588 242 C386 206 194 206 52 242 Z" fill="#0a84ff" opacity="0.22">
      <animate attributeName="opacity" values="0.12;0.28;0.12" dur="3s" repeatCount="indefinite"/>
    </path>
  </g>
  <g transform="translate(322,126) rotate({blade_angle:.1f})" filter="url(#softShadow)">
    <rect x="-128" y="-12" width="256" height="24" rx="9" fill="url(#blade)"/>
    <line x1="-106" y1="-4" x2="106" y2="-4" stroke="#9ec5ff" stroke-width="2" opacity="0.64"/>
    <animateTransform attributeName="transform" type="rotate"
      from="{blade_angle - 4:.1f} 322 126" to="{blade_angle:.1f} 322 126" dur="1.6s" fill="freeze"/>
  </g>
  <g id="waterDrops" opacity="{water_opacity:.2f}">
    <path d="M144 126 C132 148 132 166 144 174 C156 166 156 148 144 126Z" fill="#0a84ff"/>
    <path d="M320 118 C307 144 308 163 320 172 C333 163 333 144 320 118Z" fill="#0a84ff"/>
    <path d="M492 132 C481 152 482 168 492 176 C504 168 504 152 492 132Z" fill="#0a84ff"/>
    <animateTransform attributeName="transform" type="translate" values="0 -8;0 14;0 -8" dur="2.4s" repeatCount="indefinite"/>
  </g>
  {''.join(plants)}
  <rect x="34" y="28" width="292" height="82" rx="22" fill="rgba(255,255,255,0.74)" stroke="rgba(255,255,255,0.88)"/>
  <text x="56" y="58" font-family="-apple-system, BlinkMacSystemFont, Helvetica Neue, Arial" font-size="14" font-weight="800" fill="#6e6e73">{html.escape(crop_label)}</text>
  <text x="56" y="84" font-family="-apple-system, BlinkMacSystemFont, Helvetica Neue, Arial" font-size="24" font-weight="820" fill="{accent}">{html.escape(label)}</text>
  <text x="56" y="102" font-family="-apple-system, BlinkMacSystemFont, Helvetica Neue, Arial" font-size="12" fill="#6e6e73">estres: {html.escape(stress)}</text>
  <rect x="332" y="314" width="270" height="10" rx="5" fill="#dfe5ec"/>
  <rect x="332" y="314" width="{health_width:.0f}" height="10" rx="5" fill="#2f8f68">
    <animate attributeName="width" from="24" to="{health_width:.0f}" dur="1.4s" fill="freeze"/>
  </rect>
  <text x="332" y="304" font-family="-apple-system, BlinkMacSystemFont, Helvetica Neue, Arial" font-size="12" font-weight="760" fill="#6e6e73">salud estimada del cultivo</text>
</svg>"""
    return svg


def _render_scene(svg: str) -> None:
    encoded = b64encode(svg.encode("utf-8")).decode("ascii")
    st.html(
        "<div style='background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));"
        "border:1px solid rgba(255,255,255,0.72);border-radius:26px;padding:10px;"
        "box-shadow:0 20px 58px rgba(16,24,40,0.11),inset 0 1px 0 rgba(255,255,255,0.96);'>"
        f"<img src='data:image/svg+xml;base64,{encoded}' style='width:100%;display:block;border-radius:24px;' "
        "alt='Representación de acciones agronómicas'>"
        "</div>"
    )


def render_tab_agronomia(crop_risk: pd.DataFrame, agricultural_rules: pd.DataFrame) -> None:
    if crop_risk.empty:
        st.info("No hay datos agronómicos disponibles. Ejecuta el pipeline de 10 minutos para generarlos.")
        return

    crop_types = list(CROP_PROFILES.keys())
    detected_crop = str(crop_risk.get("crop_type", pd.Series(["lechuga"])).dropna().iloc[0])
    selected_crop = st.selectbox(
        "Cultivo",
        options=crop_types,
        index=crop_types.index(detected_crop) if detected_crop in crop_types else 0,
    )
    df = crop_risk[crop_risk["crop_type"] == selected_crop].copy()
    if df.empty:
        df = crop_risk.copy()
    profile = CROP_PROFILES.get(selected_crop, CROP_PROFILES["generico_horticola"])
    crop_label = str(profile["display_name"])

    actions = [a for a in df["recommended_action"].dropna().unique().tolist() if a != "mantener"]
    labels = {a: ACTION_LABELS.get(a, a) for a in actions}
    selected_label = st.selectbox(
        "Acción agrícola",
        options=[labels[a] for a in actions] or ["Mantener manejo actual"],
    )
    reverse_labels = {v: k for k, v in labels.items()}
    action = reverse_labels.get(selected_label)
    row = select_action_record(df, action)

    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">Agronomía operativa</div>',
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(card_html("Riesgo cultivo", f"{float(row.get('crop_risk_score', 0)):.2f}", str(row.get("stress_type", "estable")), COLOR["red"] if float(row.get("crop_risk_score", 0)) > 0.45 else COLOR["amber"]), unsafe_allow_html=True)
    with k2:
        st.markdown(card_html("Salud estimada", f"{float(row.get('crop_health_score', 0)):.2f}", "proxy agronómico [0,1]", COLOR["green"]), unsafe_allow_html=True)
    with k3:
        st.markdown(card_html("IEC asociado", f"{float(row.get('IEC', 0)):.2f}", "mantiene objetivo energía-cultivo", COLOR["blue"]), unsafe_allow_html=True)
    with k4:
        vwc = float(row.get("VWC_S1_fraction", 0))
        st.markdown(card_html("VWC S1", f"{vwc:.2f}", "humedad volumétrica normalizada", COLOR["cyan"]), unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    col_scene, col_rules = st.columns([1.35, 1])
    with col_scene:
        _render_scene(crop_scene_svg(row, crop_label=crop_label))
    with col_rules:
        action_rules = agricultural_rules[
            (agricultural_rules["cultivo"] == selected_crop)
            & (agricultural_rules["accion"] == str(row.get("recommended_action", "")))
        ]
        title = html.escape(str(row.get("action_label", "Manejo agronómico")))
        st.markdown(
            f'<div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));'
            f'border:1px solid rgba(255,255,255,0.72);border-radius:24px;padding:18px;'
            f'box-shadow:0 18px 48px rgba(16,24,40,0.09),inset 0 1px 0 rgba(255,255,255,0.96);">'
            f'<div style="font-size:12px;font-weight:780;color:#6e6e73;text-transform:uppercase;letter-spacing:0.06em;">Acción recomendada</div>'
            f'<div style="font-size:28px;font-weight:820;color:{action_visual_state(str(row.get("recommended_action","mantener")))["accent"]};margin:8px 0 10px;">{title}</div>'
            f'<div style="font-size:13px;line-height:1.65;color:#424245;">'
            f'La recomendación cruza condiciones de cultivo con el IEC para cuidar el estado agronómico sin abandonar el objetivo energético.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        if action_rules.empty:
            st.caption("No hay regla agregada para esta acción en el periodo seleccionado.")
        else:
            for _, rule in action_rules.iterrows():
                st.markdown(
                    f'<div style="background:linear-gradient(180deg,#ffffff,#f5f7fb);border:1px solid rgba(60,60,67,0.14);'
                    f'border-radius:20px;padding:13px 15px;margin-bottom:8px;box-shadow:0 12px 30px rgba(16,24,40,0.06);">'
                    f'<div style="display:flex;justify-content:space-between;gap:10px;margin-bottom:6px;">'
                    f'<span style="font-size:11px;font-weight:800;color:{COLOR["blue"]};">{rule.get("accion","—")}</span>'
                    f'<span style="font-size:11px;color:#6e6e73;">riesgo {float(rule.get("riesgo_mediano", 0)):.2f} · n={int(rule.get("soporte_obs",0))}</span>'
                    f'</div>'
                    f'<div style="font-size:12px;color:#35413d;line-height:1.55;">{html.escape(str(rule.get("regla","—")))}</div>'
                    f'<div style="font-size:11px;color:#6e6e73;margin-top:6px;">{html.escape(str(rule.get("comentario","")))}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.2, 1])
    with c1:
        timeline = df.sort_values("Time").copy()
        fig = px.line(
            timeline,
            x="Time",
            y=["crop_risk_score", "IEC"],
            title="Riesgo agrícola vs IEC",
            color_discrete_map={"crop_risk_score": "#ff3b30", "IEC": "#0a84ff"},
        )
        st.plotly_chart(_fig_style(fig, height=290), use_container_width=True)
    with c2:
        counts = df[df["recommended_action"] != "mantener"]["recommended_action"].value_counts().reset_index()
        counts.columns = ["accion", "observaciones"]
        if counts.empty:
            st.info("Sin acciones agrícolas críticas en la ventana actual.")
        else:
            fig_counts = px.bar(
                counts,
                x="observaciones",
                y="accion",
                orientation="h",
                title="Frecuencia de acciones modelables",
                color="accion",
                color_discrete_sequence=["#0a84ff", "#2f8f68", "#ff9f0a", "#ff3b30", "#64d2ff"],
            )
            fig_counts.update_layout(showlegend=False)
            st.plotly_chart(_fig_style(fig_counts, height=290), use_container_width=True)

    st.caption(
        "Reglas demo: regar, pausar riego, riego preventivo, sombreado, reducción de sombreado, posición segura y alerta de frío. "
        "Los umbrales deben validarse con agronomía antes de automatizar."
    )
