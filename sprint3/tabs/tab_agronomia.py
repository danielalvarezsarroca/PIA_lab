import html
from base64 import b64encode
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from agricultural_rules import ACTION_LABELS, CROP_PROFILES, crop_calendar_for_date
from data_loader import (
    load_agricultural_rules_for_crop,
    load_crop_risk_for_crop,
    load_rl_policy_for_crop,
)
from rl_policy import recommend_action_for_record
from styles import COLOR

_CROP_ZONES = ("S1", "S2")


def _style_fig(fig: go.Figure, height: int = 280) -> go.Figure:
    fig.update_layout(
        font_family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial",
        font_color="#1d1d1f",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(248,250,252,0.78)",
        margin=dict(l=8, r=8, t=38, b=12),
        xaxis=dict(showgrid=True, gridcolor="rgba(60,60,67,0.10)", zeroline=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(60,60,67,0.10)", zeroline=False, title=""),
        height=height,
    )
    return fig


def _metric_card(title: str, value: str, detail: str, color: str) -> str:
    value_size = 25
    if len(value) > 20:
        value_size = 18
    elif len(value) > 14:
        value_size = 19
    return f"""
    <div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.88));
                border:1px solid rgba(255,255,255,0.72);border-radius:22px;padding:15px 16px;
                box-shadow:0 16px 42px rgba(16,24,40,0.08),inset 0 1px 0 rgba(255,255,255,0.96);
                min-height:106px;position:relative;overflow:hidden;box-sizing:border-box;min-width:0;">
      <div style="position:absolute;left:16px;right:16px;top:0;height:3px;border-radius:999px;
                  background:linear-gradient(90deg,rgba(255,255,255,0),{color},rgba(255,255,255,0));opacity:.72;"></div>
      <div style="font-size:10px;font-weight:780;color:#6e6e73;text-transform:uppercase;
                  letter-spacing:.06em;margin-bottom:8px;overflow-wrap:anywhere;">{html.escape(title)}</div>
      <div style="font-size:{value_size}px;font-weight:820;color:{color};line-height:1.08;
                  overflow-wrap:anywhere;">{html.escape(value)}</div>
      <div style="font-size:11px;color:#6e6e73;margin-top:8px;line-height:1.35;
                  overflow-wrap:anywhere;">{html.escape(detail)}</div>
    </div>
    """


def _safe_number(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _timeline_view_model(crop_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], int]:
    timeline = crop_df.assign(Time=pd.to_datetime(crop_df["Time"]))
    timeline = timeline.sort_values("Time").reset_index(drop=True)
    labels = timeline["Time"].dt.strftime("%Y-%m-%d %H:%M").tolist()
    selected_idx = max(len(labels) - 1, 0)
    return timeline, labels, selected_idx


def _external_action_card_view_model(row: pd.Series) -> dict[str, str]:
    action = str(row.get("crop_management_action", "sin_manejo_directo"))
    mode = str(row.get("irrigation_mode", "off"))
    active = bool(row.get("irrigation_active", False))
    mm_10min = _safe_number(row.get("irrigation_mm_10min", 0))
    duration_min = _safe_number(row.get("irrigation_duration_min", 0))
    label = ACTION_LABELS.get(action, action.replace("_", " ").title())

    if active:
        color = COLOR["blue"] if action == "activar_riego" else COLOR["green"]
        return {
            "title": "Acción externa",
            "value": label,
            "detail": f"riego activo · {mm_10min:.1f} mm/10min · {duration_min:g} min",
            "color": color,
        }

    if mode == "paused" or action == "pausar_riego":
        return {
            "title": "Acción externa",
            "value": label,
            "detail": "riego pausado · sin aporte de agua",
            "color": "#6e6e73",
        }

    if action != "sin_manejo_directo":
        return {
            "title": "Acción externa",
            "value": label,
            "detail": "sin aporte de agua en este intervalo",
            "color": COLOR["amber"],
        }

    return {
        "title": "Acción externa",
        "value": "Sin intervención",
        "detail": "sin riego ni actuador externo",
        "color": "#6e6e73",
    }


def _panel_action_card_view_model(row: pd.Series) -> dict[str, str]:
    action = str(row.get("panel_action", "mantener_placas"))
    label = ACTION_LABELS.get(action, action.replace("_", " ").title())
    angle = _safe_number(row.get("rl_angle_deg", row.get("track_mean", 0)))
    regime = str(row.get("tracking_regime", "") or "seguimiento RL")
    color = "#6d5bd0"
    if action == "aumentar_sombreado":
        color = COLOR["blue"]
    elif action == "reducir_sombreado":
        color = COLOR["amber"]
    elif action == "posicion_segura":
        color = COLOR["red"]
    return {
        "title": "Acción placas",
        "value": label,
        "detail": f"{angle:.0f}° · {regime}",
        "color": color,
    }


def _crop_display_name(crop_type: str) -> str:
    profile = CROP_PROFILES.get(crop_type, {})
    return str(profile.get("display_name", crop_type.replace("_", " ").title()))


def _crop_visual_traits(crop_type: str) -> dict[str, str]:
    traits = CROP_PROFILES.get(crop_type, {}).get("visual_traits", {})
    return {
        "shape": str(traits.get("shape", "leafy_rosette")),
        "plant_color": str(traits.get("plant_color", "#30a46c")),
        "accent_color": str(traits.get("accent_color", "#8fd694")),
    }


def _scene_plant_svg(x: int, height: int, plant_color: str, accent_color: str, shape: str) -> str:
    if shape == "broccoli_head":
        return (
            f"<g transform='translate({x},314)' data-crop-shape='broccoli_head'>"
            f"<path d='M0 0 C-5 -18,-6 -28,2 -{height}' stroke='{plant_color}' stroke-width='4' fill='none' stroke-linecap='round'/>"
            f"<path d='M0 -14 C-22 -24,-22 -42,-2 -35' fill='{plant_color}' opacity='.74'/>"
            f"<path d='M4 -16 C26 -26,26 -43,5 -36' fill='{plant_color}' opacity='.68'/>"
            f"<circle cx='-7' cy='-{height + 2}' r='9' fill='{accent_color}'/>"
            f"<circle cx='3' cy='-{height + 9}' r='11' fill='{accent_color}'/>"
            f"<circle cx='15' cy='-{height + 2}' r='8' fill='{accent_color}'/>"
            f"</g>"
        )
    if shape == "vine_fruit":
        return (
            f"<g transform='translate({x},314)' data-crop-shape='vine_fruit'>"
            f"<path d='M0 0 C10 -20,-8 -37,8 -{height}' stroke='{plant_color}' stroke-width='4' fill='none' stroke-linecap='round'/>"
            f"<path d='M4 -24 C-28 -36,-27 -56,-4 -45' fill='{plant_color}' opacity='.72'/>"
            f"<path d='M8 -28 C34 -40,34 -58,8 -47' fill='{plant_color}' opacity='.68'/>"
            f"<circle cx='-12' cy='-24' r='6' fill='{accent_color}'/>"
            f"<circle cx='18' cy='-32' r='6' fill='{accent_color}'/>"
            f"</g>"
        )
    if shape == "low_fruit":
        return (
            f"<g transform='translate({x},314)' data-crop-shape='low_fruit'>"
            f"<path d='M0 0 C-20 -16,-30 -21,-40 -8' stroke='{plant_color}' stroke-width='4' fill='none' stroke-linecap='round'/>"
            f"<path d='M0 0 C18 -16,30 -21,39 -8' stroke='{plant_color}' stroke-width='4' fill='none' stroke-linecap='round'/>"
            f"<path d='M0 -4 C-9 -26,9 -38,18 -20' stroke='{plant_color}' stroke-width='4' fill='none' stroke-linecap='round'/>"
            f"<circle cx='-19' cy='-8' r='6' fill='{accent_color}'/>"
            f"<circle cx='22' cy='-10' r='6' fill='{accent_color}'/>"
            f"</g>"
        )
    if shape == "allium":
        return (
            f"<g transform='translate({x},314)' data-crop-shape='allium'>"
            f"<ellipse cx='0' cy='-4' rx='12' ry='9' fill='{accent_color}' opacity='.86'/>"
            f"<path d='M-3 0 C-7 -20,-7 -36,-3 -{height + 8}' stroke='{plant_color}' stroke-width='4' fill='none' stroke-linecap='round'/>"
            f"<path d='M1 0 C6 -20,4 -36,10 -{height + 5}' stroke='{plant_color}' stroke-width='4' fill='none' stroke-linecap='round'/>"
            f"<path d='M-1 -8 C-22 -28,-20 -45,-9 -54' stroke='{plant_color}' stroke-width='3' fill='none' stroke-linecap='round' opacity='.82'/>"
            f"<path d='M4 -9 C25 -29,23 -46,12 -55' stroke='{plant_color}' stroke-width='3' fill='none' stroke-linecap='round' opacity='.78'/>"
            f"</g>"
        )
    if shape == "tuber":
        return (
            f"<g transform='translate({x},314)' data-crop-shape='tuber'>"
            f"<ellipse cx='-10' cy='-4' rx='11' ry='7' fill='{accent_color}' opacity='.78'/>"
            f"<ellipse cx='9' cy='-7' rx='13' ry='8' fill='{accent_color}' opacity='.70'/>"
            f"<path d='M0 0 C-3 -18,2 -34,7 -{height + 7}' stroke='{plant_color}' stroke-width='4' fill='none' stroke-linecap='round'/>"
            f"<path d='M5 -20 C-24 -32,-26 -51,-4 -42' fill='{plant_color}' opacity='.66'/>"
            f"<path d='M8 -24 C33 -35,34 -54,9 -44' fill='{plant_color}' opacity='.62'/>"
            f"</g>"
        )
    return (
        f"<g transform='translate({x},314)' data-crop-shape='leafy_rosette'>"
        f"<path d='M0 0 C-8 -18,-10 -28,-4 -{height}' stroke='{plant_color}' stroke-width='4' fill='none' stroke-linecap='round'/>"
        f"<path d='M0 -18 C-22 -24,-24 -44,-4 -38' fill='{accent_color}' opacity='.82'/>"
        f"<path d='M2 -20 C24 -27,25 -45,4 -39' fill='{accent_color}' opacity='.70'/>"
        f"</g>"
    )


def _available_crop_options(df_crop_risk: pd.DataFrame) -> list[str]:
    profile_options = list(CROP_PROFILES.keys())
    if profile_options:
        return profile_options
    if "crop_type" not in df_crop_risk.columns:
        return ["lechuga"]
    return sorted(df_crop_risk["crop_type"].dropna().unique().tolist()) or ["lechuga"]


def _default_crop_zone() -> str:
    crop_zone = str(st.session_state.get("selected_crop_zone", _CROP_ZONES[0]))
    return crop_zone if crop_zone in _CROP_ZONES else _CROP_ZONES[0]


def _default_crop_type(crop_options: list[str], crop_zone: str | None = None) -> str:
    zone = crop_zone or _default_crop_zone()
    crop_type = st.session_state.get(
        f"selected_crop_type_{zone.lower()}",
        st.session_state.get("selected_crop_type", crop_options[0]),
    )
    if isinstance(crop_type, (list, tuple)):
        crop_type = crop_type[0] if crop_type else crop_options[0]
    crop_type = str(crop_type)
    return crop_type if crop_type in crop_options else crop_options[0]


def _crop_scene_svg(management_action: str, panel_action: str, health: float, risk: float, crop_type: str) -> str:
    management_action = management_action or "sin_manejo_directo"
    panel_action = panel_action or "mantener_placas"
    crop_label = _crop_display_name(crop_type)
    water_opacity = 0.0
    shade_opacity = 0.10
    safe_tilt = 0
    sun_color = "#ffd66b"
    soil_color = "#8a5a35"
    traits = _crop_visual_traits(crop_type)
    shape = traits["shape"]
    accent_color = traits["accent_color"]
    plant_color = traits["plant_color"] if health >= 0.72 else "#b7791f" if health >= 0.48 else "#d92d20"
    note = ACTION_LABELS.get(management_action, management_action.replace("_", " ").title())
    panel_note = ACTION_LABELS.get(panel_action, panel_action.replace("_", " ").title())

    if management_action in {"activar_riego", "riego_preventivo"}:
        water_opacity = 0.86
    if management_action == "pausar_riego":
        water_opacity = 0.12
    if management_action == "poda_sanitaria":
        plant_color = "#b7791f"
    if panel_action == "aumentar_sombreado":
        shade_opacity = 0.42
        safe_tilt = -12
    if panel_action == "reducir_sombreado":
        shade_opacity = 0.04
        safe_tilt = 12
    if panel_action == "posicion_segura":
        shade_opacity = 0.28
        safe_tilt = 0
        sun_color = "#b8c2d6"

    plants = []
    for i, x in enumerate(range(92, 520, 46)):
        height = 34 + (i % 3) * 8
        plants.append(_scene_plant_svg(x, height, plant_color, accent_color, shape))

    drops = []
    for x in range(120, 488, 58):
        drops.append(
            f"<path d='M{x} 176 C{x-7} 188,{x-8} 198,{x} 204 C{x+8} 198,{x+7} 188,{x} 176Z' "
            f"fill='#0a84ff' opacity='{water_opacity}'/>"
        )

    svg = f"""
    <svg viewBox="0 0 620 390" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Escena agronómica para {html.escape(crop_label)}">
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#f7fbff"/>
          <stop offset="52%" stop-color="#eaf4ff"/>
          <stop offset="100%" stop-color="#f9fbfd"/>
        </linearGradient>
        <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#3b82f6"/>
          <stop offset="100%" stop-color="#1d1d1f"/>
        </linearGradient>
        <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="18" stdDeviation="14" flood-color="#101828" flood-opacity=".16"/>
        </filter>
      </defs>
      <rect width="620" height="390" rx="28" fill="url(#sky)"/>
      <circle cx="504" cy="80" r="38" fill="{sun_color}" opacity=".92"/>
      <circle cx="504" cy="80" r="54" fill="{sun_color}" opacity=".17"/>
      <path d="M0 276 C116 248,218 268,326 248 C428 229,506 245,620 220 L620 390 L0 390Z" fill="#dff7e8"/>
      <path d="M0 326 L620 326 L620 390 L0 390Z" fill="{soil_color}" opacity=".22"/>
      <path d="M72 228 H548 L500 326 H120Z" fill="#1d1d1f" opacity="{shade_opacity}"/>
      <g filter="url(#shadow)" transform="translate(0,0)">
        <g transform="translate(126,164) rotate({safe_tilt})">
          <rect x="0" y="0" width="130" height="24" rx="10" fill="url(#panel)"/>
          <line x1="65" y1="24" x2="65" y2="118" stroke="#8e8e93" stroke-width="5" stroke-linecap="round"/>
        </g>
        <g transform="translate(330,154) rotate({safe_tilt})">
          <rect x="0" y="0" width="144" height="26" rx="11" fill="url(#panel)"/>
          <line x1="72" y1="26" x2="72" y2="128" stroke="#8e8e93" stroke-width="5" stroke-linecap="round"/>
        </g>
      </g>
      {"".join(drops)}
      <g data-crop-type="{html.escape(crop_type)}">{"".join(plants)}</g>
      <rect x="24" y="24" width="308" height="76" rx="18" fill="rgba(255,255,255,.78)" stroke="rgba(255,255,255,.9)"/>
      <text x="44" y="49" font-family="-apple-system, BlinkMacSystemFont, Helvetica Neue" font-size="15" font-weight="800" fill="#1d1d1f">Cultivo: {html.escape(crop_label)}</text>
      <text x="44" y="70" font-family="-apple-system, BlinkMacSystemFont, Helvetica Neue" font-size="12" font-weight="700" fill="#3b82f6">{html.escape(note)}</text>
      <text x="44" y="88" font-family="-apple-system, BlinkMacSystemFont, Helvetica Neue" font-size="11" fill="#6e6e73">{html.escape(panel_note)} · salud {health:.2f}</text>
    </svg>
    """
    return svg


def _render_svg(svg_html: str) -> None:
    encoded = b64encode(svg_html.encode("utf-8")).decode("ascii")
    st.html(
        "<div style='background:linear-gradient(180deg,rgba(255,255,255,.98),rgba(244,247,252,.88));"
        "border:1px solid rgba(255,255,255,.72);border-radius:26px;padding:10px;"
        "box-shadow:0 22px 64px rgba(16,24,40,.11),inset 0 1px 0 rgba(255,255,255,.96);'>"
        f"<img src='data:image/svg+xml;base64,{encoded}' style='width:100%;display:block;border-radius:22px;' "
        "alt='Visualización agronómica'>"
        "</div>"
    )


def _crop_calendar_view_model(calendar: dict[str, Any]) -> dict[str, Any]:
    current_stage = calendar.get("current_stage", {})
    stage_name = str(current_stage.get("name", "Ciclo activo"))
    progress_pct = max(0, min(100, int(round(float(calendar.get("progress", 0)) * 100))))
    ready = bool(calendar.get("ready_to_harvest", False))
    days_to_harvest = int(calendar.get("days_to_harvest", 0))
    return {
        "stage_name": stage_name,
        "progress_pct": progress_pct,
        "harvest_value": "Listo" if ready else f"{days_to_harvest} dias",
        "harvest_detail": "para recoger" if ready else "hasta cosecha",
        "harvest_color": COLOR["green"] if ready else COLOR["amber"],
        "stages": list(calendar.get("growth_stages", [])),
    }


def _render_crop_calendar(calendar: dict[str, Any]) -> None:
    view = _crop_calendar_view_model(calendar)
    stage_name = view["stage_name"]

    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin:22px 0 10px;">Calendario del cultivo</div>',
        unsafe_allow_html=True,
    )
    card_cols = st.columns(4)
    cards = [
        ("Plantado", str(calendar.get("planted_at", "")), str(calendar.get("history_note", "")), COLOR["green"]),
        (
            "Fase actual",
            stage_name,
            f"dia {int(calendar.get('days_after_planting', 0))} de {int(calendar.get('harvest_days', 0))}",
            COLOR["blue"],
        ),
        ("Cosecha prevista", str(calendar.get("harvest_at", "")), view["harvest_detail"], "#6d5bd0"),
        ("Estado cosecha", view["harvest_value"], "segun historial del lote", view["harvest_color"]),
    ]
    for col, (title, value, detail, color) in zip(card_cols, cards):
        col.markdown(_metric_card(title, value, detail, color), unsafe_allow_html=True)

    st.progress(view["progress_pct"] / 100)

    stages = view["stages"]
    if not stages:
        return
    for col, stage in zip(st.columns(len(stages)), stages):
        name = str(stage.get("name", "Fase"))
        active = name == stage_name
        start = int(stage.get("start_day", 0))
        end = int(stage.get("end_day", start))
        bg = "rgba(10,132,255,.14)" if active else "rgba(255,255,255,.70)"
        border = "rgba(10,132,255,.34)" if active else "rgba(60,60,67,.10)"
        color = "#0a84ff" if active else "#424245"
        col.markdown(
            f'<div style="min-width:0;border:1px solid {border};border-radius:16px;'
            f'padding:10px 11px;background:{bg};">'
            f'<div style="font-size:11px;font-weight:820;color:{color};line-height:1.2;">{html.escape(name)}</div>'
            f'<div style="font-size:10px;color:#6e6e73;margin-top:5px;">dia {start}-{end}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _format_range(values: Any, suffix: str = "") -> str:
    if not isinstance(values, (list, tuple)) or len(values) < 2:
        return "Sin dato"

    def fmt(value: Any) -> str:
        try:
            return f"{float(value):g}"
        except (TypeError, ValueError):
            return str(value)

    return f"{fmt(values[0])}-{fmt(values[1])}{suffix}"


def _current_stage_requirements(profile: dict[str, Any], calendar: dict[str, Any]) -> dict[str, Any]:
    current_stage = str(calendar.get("current_stage", {}).get("name", ""))
    for stage in profile.get("stage_requirements", []):
        if str(stage.get("stage", stage.get("name", ""))) == current_stage:
            return stage
    stage_requirements = profile.get("stage_requirements", [])
    return stage_requirements[0] if stage_requirements else {}


def _crop_requirements_view_model(profile: dict[str, Any], calendar: dict[str, Any]) -> list[dict[str, str]]:
    water = profile.get("water_requirements", {})
    fertilizer = profile.get("fertilizer_requirements", {})
    light = profile.get("light_requirements", {})
    stage_req = _current_stage_requirements(profile, calendar)
    stage_name = str(calendar.get("current_stage", {}).get("name", "Ciclo activo"))
    return [
        {
            "title": "Agua",
            "value": _format_range(water.get("weekly_mm_range"), " mm/sem"),
            "detail": f"raiz {water.get('root_depth_cm', 'sin dato')} cm · {water.get('irrigation_sensitivity', '')}",
            "color": COLOR["blue"],
        },
        {
            "title": "Abonado",
            "value": f"N {_format_range(fertilizer.get('nitrogen_kg_ha'), ' kg/ha')}",
            "detail": (
                f"P {_format_range(fertilizer.get('phosphorus_kg_ha'), ' kg/ha')} · "
                f"K {_format_range(fertilizer.get('potassium_kg_ha'), ' kg/ha')}"
            ),
            "color": COLOR["green"],
        },
        {
            "title": "Luz",
            "value": f"PAR {_format_range(light.get('par_fraction_target_range'))}",
            "detail": str(light.get("shade_strategy", "")),
            "color": "#6d5bd0",
        },
        {
            "title": "Fase actual",
            "value": stage_name,
            "detail": (
                f"VWC {_format_range(stage_req.get('vwc_target_range'))} · "
                f"PAR {_format_range(stage_req.get('par_fraction_target_range'))}"
            ),
            "color": COLOR["amber"],
        },
    ]


def _render_crop_requirements(profile: dict[str, Any], calendar: dict[str, Any]) -> None:
    cards = _crop_requirements_view_model(profile, calendar)
    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin:20px 0 10px;">Requerimientos del cultivo</div>',
        unsafe_allow_html=True,
    )
    for col, card in zip(st.columns(len(cards)), cards):
        col.markdown(
            _metric_card(card["title"], card["value"], card["detail"], card["color"]),
            unsafe_allow_html=True,
        )


def render_tab_agronomia(
    df_crop_risk: pd.DataFrame,
    df_agri_rules: pd.DataFrame,
    df_rl_policy: pd.DataFrame,
    df_modelo: pd.DataFrame,
) -> None:
    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">Agronomía y RL agroenergético</div>',
        unsafe_allow_html=True,
    )
    if df_crop_risk.empty:
        st.info("No hay datos agronómicos disponibles. Genera el pipeline de 10 minutos desde el masterdataset.")
        return

    crop_options = _available_crop_options(df_crop_risk)
    default_zone = _default_crop_zone()
    selected_zone = st.selectbox(
        "Zona de cultivo",
        options=list(_CROP_ZONES),
        index=list(_CROP_ZONES).index(default_zone),
        format_func=lambda zone: f"Zona {zone}",
        key="selected_crop_zone",
    )
    default_crop = _default_crop_type(crop_options, selected_zone)
    crop_type = st.selectbox(
        f"Cultivo que se quiere cultivar en {selected_zone}",
        options=crop_options,
        index=crop_options.index(default_crop),
        format_func=_crop_display_name,
        key=f"selected_crop_type_{selected_zone.lower()}",
    )
    st.session_state["selected_crop_type"] = crop_type
    crop_label = _crop_display_name(crop_type)
    st.caption(f"Zona {selected_zone} · cultivo seleccionado: {crop_label}")
    crop_df = load_crop_risk_for_crop(crop_type, crop_zone=selected_zone)
    if crop_df.empty:
        st.info("No hay registros para este cultivo.")
        return

    crop_df, time_labels, default_time_idx = _timeline_view_model(crop_df)
    selected_time_label = time_labels[default_time_idx]
    if len(time_labels) > 1:
        selected_time_label = st.select_slider(
            "Instante de visualización",
            options=time_labels,
            value=selected_time_label,
            key=f"agro_timeline_{selected_zone}_{crop_type}",
        )
    selected_time_idx = time_labels.index(selected_time_label)
    latest = crop_df.iloc[selected_time_idx]
    st.caption(f"Visualización cada 10 minutos · instante seleccionado: {selected_time_label}")

    model_row = df_modelo[pd.to_datetime(df_modelo["Time"]) == pd.to_datetime(latest["Time"])]
    rl_record = latest.copy()
    if not model_row.empty:
        for col in ["solar_elevation_deg", "hour_of_day", "tracking_regime", "track_mean"]:
            rl_record[col] = model_row.iloc[0].get(col, rl_record.get(col))
    rl_policy = load_rl_policy_for_crop(crop_type, crop_zone=selected_zone)
    rl_rec = pd.Series(dtype="object")
    if not rl_policy.empty:
        try:
            rl_rec = recommend_action_for_record(rl_policy, rl_record)
        except (ValueError, KeyError, TypeError):
            rl_rec = pd.Series(dtype="object")

    health = float(latest.get("crop_health_score", 0))
    risk = float(latest.get("crop_risk_score", 0))
    management_action = str(rl_rec.get("crop_management_action", latest.get("crop_management_action", "sin_manejo_directo")))
    panel_action = str(rl_rec.get("panel_action", latest.get("panel_action", "mantener_placas")))
    action = str(rl_rec.get("agronomic_action", latest.get("recommended_action", "mantener")))
    rl_angle = float(rl_rec.get("rl_angle_deg", latest.get("track_mean", 0)))
    rl_reward = float(rl_rec.get("rl_reward", 0))
    latest_with_rl = latest.copy()
    latest_with_rl["crop_management_action"] = management_action
    latest_with_rl["panel_action"] = panel_action
    latest_with_rl["rl_angle_deg"] = rl_angle
    external_card = _external_action_card_view_model(latest_with_rl)
    panel_card = _panel_action_card_view_model(latest_with_rl)

    c1, c2, c3, c4 = st.columns([1, 1, 1.24, 1.24])
    with c1:
        st.markdown(_metric_card("Salud cultivo", f"{health:.2f}", "componente agronómica de la recompensa", COLOR["green"]), unsafe_allow_html=True)
    with c2:
        st.markdown(_metric_card("Riesgo", f"{risk:.2f}", str(latest.get("stress_type", "estable")).replace("_", " "), COLOR["red"] if risk > 0.45 else COLOR["amber"]), unsafe_allow_html=True)
    with c3:
        st.markdown(_metric_card(external_card["title"], external_card["value"], external_card["detail"], external_card["color"]), unsafe_allow_html=True)
    with c4:
        st.markdown(_metric_card(panel_card["title"], panel_card["value"], f"{panel_card['detail']} · reward {rl_reward:.2f}", panel_card["color"]), unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    col_scene, col_charts = st.columns([1.05, 1])
    with col_scene:
        _render_svg(_crop_scene_svg(management_action, panel_action, health, risk, crop_type))
        st.caption("La política RL muestra acciones factorizadas: placa y acción externa pueden coexistir en el mismo intervalo de 10 minutos.")

    with col_charts:
        fig_health = go.Figure()
        fig_health.add_trace(go.Scatter(
            x=crop_df["Time"],
            y=crop_df["crop_health_score"],
            mode="lines",
            name="salud",
            line=dict(color=COLOR["green"], width=3),
            fill="tozeroy",
            fillcolor="rgba(47,143,104,.20)",
        ))
        fig_health.add_trace(go.Scatter(
            x=crop_df["Time"],
            y=crop_df["crop_risk_score"],
            mode="lines",
            name="riesgo",
            line=dict(color=COLOR["red"], width=2),
        ))
        fig_health.add_vline(
            x=latest["Time"],
            line_width=2,
            line_dash="dot",
            line_color="rgba(10,132,255,.72)",
        )
        fig_health.update_layout(title="Riesgo y salud cada 10 minutos", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(_style_fig(fig_health, height=238), use_container_width=True)

        if "irrigation_mm_10min" in crop_df.columns:
            irrigation_mm = pd.to_numeric(crop_df["irrigation_mm_10min"], errors="coerce").fillna(0)
        else:
            irrigation_mm = pd.Series(0.0, index=crop_df.index)
        irrigation_actions = crop_df["crop_management_action"].map(ACTION_LABELS).fillna(crop_df["crop_management_action"])
        irrigation_colors = [
            COLOR["green"] if str(action) == "riego_preventivo" else COLOR["blue"] if mm > 0 else "rgba(110,110,115,.28)"
            for action, mm in zip(crop_df["crop_management_action"], irrigation_mm)
        ]
        fig_irrigation = go.Figure()
        fig_irrigation.add_trace(go.Bar(
            x=crop_df["Time"],
            y=irrigation_mm,
            text=irrigation_actions,
            name="mm/10min",
            marker_color=irrigation_colors,
            hovertemplate="%{x|%d/%m %H:%M}<br>%{text}<br>%{y:.1f} mm/10min<extra></extra>",
        ))
        fig_irrigation.add_vline(
            x=latest["Time"],
            line_width=2,
            line_dash="dot",
            line_color="rgba(10,132,255,.72)",
        )
        fig_irrigation.update_layout(title="Acción externa y riego aplicado cada 10 minutos", showlegend=False)
        st.plotly_chart(_style_fig(fig_irrigation, height=238), use_container_width=True)

    profile = CROP_PROFILES.get(str(crop_type), {})
    calendar = crop_calendar_for_date(crop_type, latest["Time"])
    _render_crop_calendar(calendar)
    _render_crop_requirements(profile, calendar)

    sources = profile.get("sources", [])
    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin:20px 0 10px;">Reglas agronómicas referenciadas</div>',
        unsafe_allow_html=True,
    )
    rules = load_agricultural_rules_for_crop(crop_type, crop_zone=selected_zone)
    if rules.empty:
        st.info("No se han generado reglas agronómicas para este cultivo.")
    else:
        for _, row in rules.iterrows():
            label = ACTION_LABELS.get(str(row.get("accion", "")), str(row.get("accion", "")))
            st.markdown(
                f'<div style="background:linear-gradient(180deg,#ffffff,#f5f8fc);border:1px solid rgba(255,255,255,.72);'
                f'border-radius:20px;padding:13px 15px;margin-bottom:9px;box-shadow:0 12px 30px rgba(16,24,40,.06),'
                f'inset 0 1px 0 rgba(255,255,255,.92);">'
                f'<div style="display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:6px;">'
                f'<span style="font-size:12px;font-weight:800;color:#0a84ff;">{html.escape(label)}</span>'
                f'<span style="font-size:11px;color:#6e6e73;">riesgo mediano {float(row.get("riesgo_mediano", 0)):.2f} · n={int(row.get("soporte_obs", 0))}</span>'
                f'</div>'
                f'<div style="font-size:12px;color:#424245;line-height:1.55;">{html.escape(str(row.get("regla", "—")))}</div>'
                f'<div style="font-size:11px;color:#6e6e73;margin-top:5px;">{html.escape(str(row.get("comentario", "")))}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if sources:
        st.caption("Fuentes de umbrales: " + " · ".join(source["name"] for source in sources))
