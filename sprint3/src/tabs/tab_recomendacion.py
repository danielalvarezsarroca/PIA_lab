from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import get_latest_record
from rl_policy import recommend_action_for_record
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
                  letter-spacing:0.06em;margin-bottom:8px;">{escape(title)}</div>
      <div style="font-size:26px;font-weight:820;color:{color};line-height:1;">{escape(value)}</div>
      <div style="font-size:11px;color:#6e6e73;margin-top:8px;line-height:1.35;">{escape(detail)}</div>
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


def _action_label(value: object, fallback: str = "—") -> str:
    if value is None or pd.isna(value):
        return fallback
    label = str(value).replace("_", " ").strip()
    return label[:1].upper() + label[1:] if label else fallback


def _safe_float(value: object, fallback: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return fallback
    return fallback if pd.isna(numeric) else numeric


def _safe_int(value: object, fallback: int = 0) -> int:
    try:
        numeric = int(float(value))
    except (TypeError, ValueError):
        return fallback
    return fallback if pd.isna(numeric) else numeric


def _policy_series(policy_view: pd.DataFrame, column: str, fallback: object) -> pd.Series:
    if column in policy_view.columns:
        return policy_view[column]
    return pd.Series([fallback] * len(policy_view), index=policy_view.index)


_SUN_LABELS = {
    "night": "noche",
    "low": "sol bajo",
    "medium": "sol medio",
    "high": "sol alto",
}


def _state_label(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "situación parecida"

    hour_label = ""
    parts: dict[str, str] = {}
    for chunk in raw.split("|"):
        if chunk.startswith("h") and chunk[1:].isdigit():
            hour_label = f"{int(chunk[1:]):02d}:00"
        elif ":" in chunk:
            key, item = chunk.split(":", 1)
            parts[key] = item

    sun = _SUN_LABELS.get(parts.get("sun", ""), parts.get("sun", "").replace("_", " "))
    stress = parts.get("stress", "").replace("_", " ")
    labels = [item for item in (hour_label, sun, stress) if item]
    return " · ".join(labels) if labels else raw.replace("|", " · ")


def _current_rl_recommendation(df_rl_policy: pd.DataFrame | None, record: pd.Series) -> pd.Series:
    if df_rl_policy is None or df_rl_policy.empty:
        return pd.Series(dtype="object")
    try:
        return recommend_action_for_record(df_rl_policy, record)
    except (ValueError, KeyError, TypeError):
        return pd.Series(dtype="object")


def _recommendation_card(
    recommendation: pd.Series,
    current_iec: float,
    title: str = "Qué hacer ahora",
    accent: str = "#0a84ff",
) -> str:
    if recommendation.empty:
        return f"""
        <div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));
                    border:1px solid rgba(255,255,255,0.72);border-radius:22px;padding:16px;
                    box-shadow:0 16px 42px rgba(16,24,40,0.08),inset 0 1px 0 rgba(255,255,255,0.96);">
          <div style="font-size:10px;font-weight:760;color:#64706d;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">
            {escape(title)}
          </div>
          <div style="font-size:19px;font-weight:820;color:{COLOR["muted"]};line-height:1.2;">
            Sin recomendación disponible
          </div>
          <div style="font-size:12px;color:#6e6e73;margin-top:9px;line-height:1.45;">
            Equilibrio actual: {current_iec:.2f}. No hay una acción cargada para esta situación.
          </div>
        </div>"""

    panel_action = _action_label(recommendation.get("panel_action", "mantener_placas"))
    crop_action = _action_label(recommendation.get("crop_management_action", "sin_manejo_directo"))
    angle = _safe_float(recommendation.get("rl_angle_deg"), 0.0)
    confidence = _safe_float(recommendation.get("rl_confidence", recommendation.get("rl_reward")), 0.0)
    observations = _safe_int(recommendation.get("observations"), 0)
    irrigation_active = _safe_int(recommendation.get("irrigation_active"), 0) == 1
    irrigation_mm = _safe_float(recommendation.get("irrigation_mm_10min"), 0.0)
    irrigation_mode = _action_label(recommendation.get("irrigation_mode", "sin_riego"))
    state_key = escape(_state_label(recommendation.get("state_key", "estado actual")))

    irrigation_text = (
        f"Riego activo · {irrigation_mm:.1f} mm/10 min · {irrigation_mode}"
        if irrigation_active
        else "Sin riego en este intervalo"
    )

    return f"""
    <div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(235,244,255,0.90));
                border:1px solid rgba(255,255,255,0.72);border-radius:22px;padding:16px;
                box-shadow:0 16px 42px rgba(10,132,255,0.10),inset 0 1px 0 rgba(255,255,255,0.96);">
      <div style="font-size:10px;font-weight:760;color:#64706d;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">
        {escape(title)}
      </div>
      <div style="font-size:27px;font-weight:850;color:{accent};line-height:1;">{angle:.0f}°</div>
      <div style="font-size:12px;color:#6e6e73;margin-top:6px;">Posición sugerida para las placas ahora.</div>
      <div style="display:grid;grid-template-columns:1fr;gap:8px;margin-top:14px;">
        <div style="background:rgba(255,255,255,0.70);border:1px solid rgba(60,60,67,0.10);border-radius:15px;padding:10px 12px;">
          <div style="font-size:9px;font-weight:800;color:#6d5bd0;text-transform:uppercase;letter-spacing:0.06em;">Placas</div>
          <div style="font-size:15px;font-weight:820;color:#1d1d1f;margin-top:4px;">{escape(panel_action)}</div>
        </div>
        <div style="background:rgba(255,255,255,0.70);border:1px solid rgba(60,60,67,0.10);border-radius:15px;padding:10px 12px;">
          <div style="font-size:9px;font-weight:800;color:#0a84ff;text-transform:uppercase;letter-spacing:0.06em;">Cultivo</div>
          <div style="font-size:15px;font-weight:820;color:#1d1d1f;margin-top:4px;">{escape(crop_action)}</div>
        </div>
      </div>
      <div style="font-size:12px;color:#424245;margin-top:12px;line-height:1.55;">
        {escape(irrigation_text)}<br>
        Confianza: <b>{confidence * 100:.0f}%</b> · Casos parecidos: <b>{observations}</b><br>
        Situación: {state_key}
      </div>
    </div>"""


def render_tab_recomendacion(
    df_rules: pd.DataFrame,
    df_modelo: pd.DataFrame,
    df_rl_policy: pd.DataFrame | None = None,
) -> None:
    del df_rules

    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">Recomendación actual</div>',
        unsafe_allow_html=True,
    )

    latest = get_latest_record(df_modelo)
    current_iec = _safe_float(latest.get("IEC"), 0.0)
    current_recommendation = _current_rl_recommendation(df_rl_policy, latest)
    policy_available = df_rl_policy is not None and not df_rl_policy.empty

    reward = _safe_float(current_recommendation.get("rl_reward"), 0.0) if not current_recommendation.empty else 0.0
    confidence = (
        _safe_float(current_recommendation.get("rl_confidence", current_recommendation.get("rl_reward")), 0.0)
        if not current_recommendation.empty
        else 0.0
    )
    observations = _safe_int(current_recommendation.get("observations"), 0) if not current_recommendation.empty else 0
    rl_states = len(df_rl_policy) if policy_available else 0
    panel_action = (
        _action_label(current_recommendation.get("panel_action", "mantener_placas"))
        if not current_recommendation.empty
        else "Sin accion"
    )
    crop_action = (
        _action_label(current_recommendation.get("crop_management_action", "sin_manejo_directo"))
        if not current_recommendation.empty
        else "Sin accion"
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(_policy_metric("Confianza", f"{confidence * 100:.0f}%", "diferencia con la segunda opción", "#0a84ff"), unsafe_allow_html=True)
    with m2:
        st.markdown(_policy_metric("Placas", panel_action, "posición sugerida", COLOR["purple"]), unsafe_allow_html=True)
    with m3:
        st.markdown(_policy_metric("Cultivo", crop_action, "acción sugerida", COLOR["green"]), unsafe_allow_html=True)
    with m4:
        st.markdown(
            _policy_metric(
                "Equilibrio",
                f"{current_iec:.2f}",
                f"indicador de apoyo · {observations} casos parecidos · {rl_states} patrones",
                "#8e8e93",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    col_rec, col_policy = st.columns([1, 2])

    with col_rec:
        st.markdown(_recommendation_card(current_recommendation, current_iec), unsafe_allow_html=True)

        gauge_pct = max(0, min(100, confidence * 100))
        st.markdown(
            f'<div style="margin-top:12px;background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));'
            f'border:1px solid rgba(255,255,255,0.72);border-radius:22px;padding:14px 16px;'
            f'box-shadow:0 14px 34px rgba(16,24,40,0.07),inset 0 1px 0 rgba(255,255,255,0.96);">'
            f'<div style="display:flex;justify-content:space-between;font-size:11px;color:#6e6e73;font-weight:760;'
            f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:9px;"><span>Confianza de la recomendación</span><span>{gauge_pct:.0f}%</span></div>'
            f'<div style="height:11px;border-radius:999px;background:linear-gradient(180deg,#e5e8ef,#f7f8fb);'
            f'overflow:hidden;box-shadow:inset 0 2px 5px rgba(16,24,40,0.12);">'
            f'<div style="height:100%;width:{gauge_pct:.0f}%;border-radius:999px;'
            f'background:linear-gradient(90deg,#ff3b30,#ffcc00,#2f8f68);"></div></div>'
            f'<div style="font-size:11px;color:#6e6e73;margin-top:9px;">Cuanto más alto, más clara es la recomendación para una situación parecida.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_policy:
        if not policy_available:
            st.info("No hay recomendaciones cargadas para este cultivo.")
            return

        policy_view = df_rl_policy.copy().assign(
            situacion=_policy_series(df_rl_policy, "state_key", "situación parecida").map(_state_label),
            accion_placas=_policy_series(df_rl_policy, "panel_action", "mantener_placas").map(_action_label),
            accion_externa=_policy_series(
                df_rl_policy,
                "crop_management_action",
                "sin_manejo_directo",
            ).map(_action_label),
            angle_label=_policy_series(df_rl_policy, "rl_angle_deg", 0).map(lambda value: f"{_safe_float(value):.0f}°"),
            claridad=_policy_series(df_rl_policy, "rl_confidence", 0.0),
        )
        policy_view = policy_view.sort_values(["claridad", "rl_reward", "observations"], ascending=[False, False, False]).head(12)

        fig_policy = px.bar(
            policy_view.sort_values("claridad", ascending=True),
            x="claridad",
            y="situacion",
            orientation="h",
            color="claridad",
            color_continuous_scale=["#ff3b30", "#ffcc00", "#2f8f68"],
            text="angle_label",
            title="Recomendaciones más claras",
            labels={"claridad": "confianza", "situacion": "situación"},
            hover_data=["accion_placas", "accion_externa", "rl_reward", "observations"],
        )
        fig_policy.update_traces(textposition="outside", marker_line_width=0)
        fig_policy.update_coloraxes(showscale=False)
        st.plotly_chart(_style_policy_fig(fig_policy, height=280), use_container_width=True)

        st.markdown(
            '<div style="font-size:12px;font-weight:760;color:#64706d;margin-bottom:8px;">'
            'Situaciones parecidas</div>',
            unsafe_allow_html=True,
        )

        display_cols = [
            "situacion",
            "hour_of_day",
            "solar_band",
            "accion_placas",
            "accion_externa",
            "irrigation_active",
            "rl_angle_deg",
            "claridad",
            "rl_reward",
            "observations",
        ]
        display_cols = [col for col in display_cols if col in policy_view.columns]
        table = policy_view[display_cols].rename(
            columns={
                "situacion": "situación",
                "hour_of_day": "hora",
                "solar_band": "luz",
                "accion_placas": "placas",
                "accion_externa": "cultivo",
                "irrigation_active": "riego",
                "rl_angle_deg": "ángulo sugerido",
                "claridad": "confianza",
                "rl_reward": "valor esperado",
                "observations": "casos",
            }
        )
        st.dataframe(table, use_container_width=True, hide_index=True)
