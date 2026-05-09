import math

from agricultural_rules import CROP_PROFILES
from solar_logic import calculate_sun_position

_W, _H = 640, 430
_GROUND_Y = 252
_PIVOTS = [(190, 244), (320, 236), (450, 244)]
_PANEL_W, _PANEL_H = 118, 14
_ANIM_DUR = "3s"


def _direction_label(angle: float) -> str:
    if abs(angle) < 4:
        return "Plano"
    return "Oeste" if angle > 0 else "Este"


def _ambient_palette(hour: float) -> dict[str, str]:
    """Return scene colors for a day/night ambiance."""
    if hour < 7 or hour >= 20:
        return {
            "sky_top": "#172554",
            "sky_mid": "#35548f",
            "sky_bot": "#9dc2e6",
            "sun": "#ffe58a",
            "sun_glow": "#fbbf24",
            "arc": "#f7c873",
            "ground_top": "#5fb980",
            "ground_bot": "#2f8f68",
            "label": "#f8fafc",
        }
    if hour < 10:
        return {
            "sky_top": "#ffd7a8",
            "sky_mid": "#f7e7c8",
            "sky_bot": "#e6f5ff",
            "sun": "#fff1a8",
            "sun_glow": "#ffbf5f",
            "arc": "#ffc27a",
            "ground_top": "#b8edc9",
            "ground_bot": "#77cf9b",
            "label": "#5f4a2f",
        }
    if hour < 17:
        return {
            "sky_top": "#d9ecff",
            "sky_mid": "#edf7ff",
            "sky_bot": "#f8fbff",
            "sun": "#ffe58a",
            "sun_glow": "#ffd45f",
            "arc": "#ffd69a",
            "ground_top": "#c7f0d5",
            "ground_bot": "#8fd9a9",
            "label": "#6e6e73",
        }
    return {
        "sky_top": "#f9b58e",
        "sky_mid": "#d9c6ef",
        "sky_bot": "#d8ecff",
        "sun": "#ffd37a",
        "sun_glow": "#ff9f5a",
        "arc": "#ffbd7a",
        "ground_top": "#aadfbd",
        "ground_bot": "#63bb85",
        "label": "#5f4a55",
    }


def _animate_color(name: str, start: str, end: str) -> str:
    if start == end:
        return ""
    return f'<animate attributeName="{name}" from="{start}" to="{end}" dur="{_ANIM_DUR}" fill="freeze"/>'


def _sun_rays(r: float) -> str:
    import math

    lines = []
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        x1 = r * math.cos(rad)
        y1 = r * math.sin(rad)
        x2 = (r + 13) * math.cos(rad)
        y2 = (r + 13) * math.sin(rad)
        lines.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#ffcc4d" stroke-width="2" stroke-linecap="round" opacity="0.78"/>'
        )
    return "\n".join(lines)


def _scaled_sun_position(hour: float) -> tuple[float, float]:
    """Scale the existing sun path into the larger illustration canvas."""
    old_x, old_y = calculate_sun_position(hour)
    x = 54 + ((old_x - 30) / 400) * (_W - 108)
    y = 42 + ((old_y - 15) / 143) * 172
    return x, y


def _label_for_action(action: str) -> str:
    labels = {
        "activar_riego": "Riego activo",
        "riego_preventivo": "Riego preventivo",
        "pausar_riego": "Riego pausado",
        "poda_sanitaria": "Poda sanitaria",
        "proteccion_frio": "Proteccion frio",
        "sin_manejo_directo": "Sin manejo",
        "aumentar_sombreado": "Aumentar sombra",
        "reducir_sombreado": "Reducir sombra",
        "posicion_segura": "Posicion segura",
        "mantener_placas": "Mantener placas",
        "mantener": "Mantener",
    }
    return labels.get(action, action.replace("_", " ").title())


def _short_label(text: str, max_chars: int = 19) -> str:
    return text if len(text) <= max_chars else f"{text[: max_chars - 1]}..."


def _crop_traits(crop_type: str) -> dict[str, str]:
    traits = CROP_PROFILES.get(crop_type, {}).get("visual_traits", {})
    return {
        "shape": str(traits.get("shape", "leafy_rosette")),
        "plant_color": str(traits.get("plant_color", "#2f8f68")),
        "accent_color": str(traits.get("accent_color", "#83c987")),
    }


def _plant_svg(x: float, base_y: float, i: int, traits: dict[str, str]) -> str:
    shape = traits["shape"]
    plant_color = traits["plant_color"]
    accent_color = traits["accent_color"]
    h = 21 + (i % 4) * 3
    if shape == "broccoli_head":
        return (
            f'<g opacity="0.96" data-crop-shape="broccoli_head">'
            f'<path d="M{x} {base_y} C{x + 1} {base_y - 12}, {x + 5} {base_y - 26}, {x + 10} {base_y - 40}" '
            f'stroke="{plant_color}" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
            f'<ellipse cx="{x - 4}" cy="{base_y - 10}" rx="10" ry="5" fill="{plant_color}" opacity="0.42"/>'
            f'<ellipse cx="{x + 18}" cy="{base_y - 12}" rx="11" ry="5" fill="{plant_color}" opacity="0.42"/>'
            f'<circle cx="{x}" cy="{base_y - h - 12}" r="8" fill="{accent_color}"/>'
            f'<circle cx="{x + 10}" cy="{base_y - h - 19}" r="10" fill="{accent_color}"/>'
            f'<circle cx="{x + 21}" cy="{base_y - h - 12}" r="8" fill="{accent_color}"/>'
            f'<circle cx="{x + 10}" cy="{base_y - h - 9}" r="8" fill="{plant_color}" opacity="0.86"/>'
            f'</g>'
        )
    if shape == "vine_fruit":
        return (
            f'<g opacity="0.96" data-crop-shape="vine_fruit">'
            f'<path d="M{x} {base_y} C{x + 5} {base_y - 17}, {x - 2} {base_y - 31}, {x + 8} {base_y - 48}" '
            f'stroke="{plant_color}" stroke-width="3.1" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x + 5} {base_y - 26} C{x - 9} {base_y - 35},{x - 18} {base_y - 21},{x - 22} {base_y - 13}" '
            f'stroke="{plant_color}" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x + 7} {base_y - 33} C{x + 23} {base_y - 42},{x + 30} {base_y - 27},{x + 31} {base_y - 17}" '
            f'stroke="{plant_color}" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            f'<circle cx="{x + 18}" cy="{base_y - 26}" r="6.5" fill="{accent_color}"/>'
            f'<circle cx="{x - 8}" cy="{base_y - 18}" r="5.8" fill="{accent_color}"/>'
            f'<circle cx="{x + 18}" cy="{base_y - 29}" r="1.9" fill="#ffffff" opacity="0.64"/>'
            f'</g>'
        )
    if shape == "low_fruit":
        return (
            f'<g opacity="0.95" data-crop-shape="low_fruit">'
            f'<path d="M{x} {base_y} C{x - 8} {base_y - 20},{x - 23} {base_y - 23},{x - 30} {base_y - 9}" '
            f'stroke="{plant_color}" stroke-width="2.9" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x} {base_y} C{x + 8} {base_y - 20},{x + 23} {base_y - 23},{x + 30} {base_y - 9}" '
            f'stroke="{plant_color}" stroke-width="2.9" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x} {base_y - 3} C{x - 11} {base_y - 17},{x - 5} {base_y - 32},{x + 4} {base_y - 21}" '
            f'stroke="{plant_color}" stroke-width="2.8" fill="none" stroke-linecap="round"/>'
            f'<circle cx="{x - 16}" cy="{base_y - 11}" r="5.8" fill="{accent_color}"/>'
            f'<circle cx="{x + 16}" cy="{base_y - 12}" r="5.8" fill="{accent_color}"/>'
            f'</g>'
        )
    if shape == "allium":
        return (
            f'<g opacity="0.95" data-crop-shape="allium">'
            f'<ellipse cx="{x + 4}" cy="{base_y - 2}" rx="10" ry="7" fill="{accent_color}" opacity="0.74"/>'
            f'<path d="M{x + 1} {base_y} C{x - 2} {base_y - 18},{x - 2} {base_y - 34},{x + 2} {base_y - 48}" '
            f'stroke="{plant_color}" stroke-width="3" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x + 6} {base_y} C{x + 13} {base_y - 19},{x + 9} {base_y - 35},{x + 15} {base_y - 47}" '
            f'stroke="{plant_color}" stroke-width="3" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x + 3} {base_y - 11} C{x - 16} {base_y - 28},{x - 12} {base_y - 43},{x - 3} {base_y - 50}" '
            f'stroke="{plant_color}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.76"/>'
            f'<path d="M{x + 8} {base_y - 12} C{x + 27} {base_y - 29},{x + 23} {base_y - 44},{x + 14} {base_y - 51}" '
            f'stroke="{plant_color}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.72"/>'
            f'</g>'
        )
    if shape == "tuber":
        return (
            f'<g opacity="0.95" data-crop-shape="tuber">'
            f'<ellipse cx="{x - 5}" cy="{base_y - 2}" rx="9" ry="6" fill="{accent_color}" opacity="0.72"/>'
            f'<ellipse cx="{x + 11}" cy="{base_y - 5}" rx="11" ry="7" fill="{accent_color}" opacity="0.66"/>'
            f'<path d="M{x + 3} {base_y} C{x + 2} {base_y - 16},{x + 5} {base_y - 30},{x + 10} {base_y - 45}" '
            f'stroke="{plant_color}" stroke-width="3.1" fill="none" stroke-linecap="round"/>'
            f'<ellipse cx="{x - 6}" cy="{base_y - 24}" rx="15" ry="6" fill="{plant_color}" opacity="0.40" '
            f'transform="rotate(-18 {x - 6} {base_y - 24})"/>'
            f'<ellipse cx="{x + 17}" cy="{base_y - 28}" rx="16" ry="6" fill="{plant_color}" opacity="0.38" '
            f'transform="rotate(20 {x + 17} {base_y - 28})"/>'
            f'</g>'
        )
    return (
        f'<g opacity="0.93" data-crop-shape="leafy_rosette">'
        f'<path d="M{x} {base_y} C{x + 1} {base_y - 14}, {x + 3} {base_y - 24}, {x + 7} {base_y - 36}" '
        f'stroke="{plant_color}" stroke-width="2.8" fill="none" stroke-linecap="round"/>'
        f'<path d="M{x + 6} {base_y - 23} C{x - 8} {base_y - h - 7}, {x - 22} {base_y - h + 5}, {x - 22} {base_y - 2}" '
        f'stroke="{accent_color}" stroke-width="3" fill="none" stroke-linecap="round"/>'
        f'<path d="M{x + 7} {base_y - 24} C{x + 22} {base_y - h - 7}, {x + 29} {base_y - h + 8}, {x + 26} {base_y - 1}" '
        f'stroke="{accent_color}" stroke-width="3" fill="none" stroke-linecap="round"/>'
        f'<ellipse cx="{x - 10}" cy="{base_y - 13}" rx="10" ry="5" fill="{accent_color}" opacity="0.34"/>'
        f'<ellipse cx="{x + 17}" cy="{base_y - 13}" rx="10" ry="5" fill="{accent_color}" opacity="0.34"/>'
        f"</g>"
    )


def _crop_row(
    crop_type: str,
    *,
    row_id: str = "selected-crop-row",
    base_y: float | None = None,
    start_x: float = 48,
    spacing: float = 39,
    count: int = 15,
) -> str:
    traits = _crop_traits(crop_type)
    row_base_y = _GROUND_Y + 45 if base_y is None else base_y
    plants = []
    for i in range(count):
        x = start_x + i * spacing
        plants.append(_plant_svg(x, row_base_y + (i % 2) * 2, i, traits))
    return f'<g id="{row_id}">{"".join(plants)}</g>'


def _shadow_geometry(angle: float, solar_elevation: float, panel_action: str) -> tuple[float, float, float]:
    sun_factor = max(0.0, min(1.0, solar_elevation / 75.0))
    length = 94 - 42 * sun_factor + abs(angle) * 0.42
    opacity = 0.16 + 0.24 * sun_factor
    if panel_action == "aumentar_sombreado":
        length *= 1.26
        opacity += 0.12
    elif panel_action == "reducir_sombreado":
        length *= 0.74
        opacity -= 0.08
    elif panel_action == "posicion_segura":
        length *= 0.92
        opacity += 0.02
    shift = -angle * 0.85
    return length, shift, max(0.06, min(0.54, opacity))


def _water_drops(action: str, fill: str = "#0a84ff", base_opacity: float = 0.56) -> str:
    if action not in {"activar_riego", "riego_preventivo", "pausar_riego"}:
        return ""
    drops = []
    for i, x in enumerate(range(72, 572, 62)):
        y = _GROUND_Y + 9 + (i % 2) * 10
        drops.append(
            f'<path d="M{x} {y} C{x-5} {y+8},{x-4} {y+16},{x} {y+19} '
            f'C{x+4} {y+16},{x+5} {y+8},{x} {y}Z" fill="{fill}" opacity="{base_opacity:.2f}">'
            f'<animate attributeName="opacity" values="0.22;0.78;0.22" dur="1.6s" repeatCount="indefinite"/></path>'
        )
    return "".join(drops)


def _pause_icon(cx: float, cy: float) -> str:
    return (
        f'<g transform="translate({cx} {cy})" opacity="0.9">'
        f'<rect x="-12" y="-14" width="26" height="28" rx="8" fill="rgba(255,255,255,0.7)"/>'
        f'<rect x="-5" y="-8" width="4" height="16" rx="2" fill="#6b7280"/>'
        f'<rect x="4" y="-8" width="4" height="16" rx="2" fill="#6b7280"/>'
        f'</g>'
    )


def _scissors_icon(cx: float, cy: float) -> str:
    return (
        f'<g transform="translate({cx} {cy})" stroke="#b7791f" stroke-width="2" '
        f'stroke-linecap="round" fill="none" opacity="0.95">'
        f'<circle cx="-6" cy="6" r="4"/>'
        f'<circle cx="6" cy="6" r="4"/>'
        f'<line x1="-4" y1="2" x2="12" y2="-12"/>'
        f'<line x1="4" y1="2" x2="-12" y2="-12"/>'
        f'</g>'
    )


def _snowflake_icon(cx: float, cy: float) -> str:
    return (
        f'<g transform="translate({cx} {cy})" stroke="#60a5fa" stroke-width="2" '
        f'stroke-linecap="round" opacity="0.9">'
        f'<line x1="0" y1="-10" x2="0" y2="10"/>'
        f'<line x1="-10" y1="0" x2="10" y2="0"/>'
        f'<line x1="-7" y1="-7" x2="7" y2="7"/>'
        f'<line x1="7" y1="-7" x2="-7" y2="7"/>'
        f'</g>'
    )


def _cold_tint() -> str:
    return (
        f'<rect x="14" y="{_GROUND_Y - 18}" width="{_W - 28}" height="70" '
        f'rx="18" fill="#93c5fd" opacity="0.12">'
        f'<animate attributeName="opacity" values="0.08;0.18;0.08" dur="2.8s" repeatCount="indefinite"/>'
        f'</rect>'
    )


def _management_overlay(action: str) -> str:
    if action == "sin_manejo_directo":
        return ""
    elements = []
    if action in {"activar_riego", "riego_preventivo"}:
        elements.append(_water_drops(action))
    elif action == "pausar_riego":
        elements.append(_water_drops(action, fill="#9aa3ad", base_opacity=0.38))
        elements.append(_pause_icon(522, _GROUND_Y - 48))
    elif action == "poda_sanitaria":
        elements.append(_scissors_icon(522, _GROUND_Y - 48))
    elif action == "proteccion_frio":
        elements.append(_cold_tint())
        elements.append(_snowflake_icon(520, _GROUND_Y - 48))
    else:
        return ""
    return (
        f'<g id="management-overlay" data-management-action="{action}" opacity="0.92">'
        f'<animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" repeatCount="indefinite"/>'
        f'{"".join(elements)}'
        f'</g>'
    )


def _crop_display_name(crop_type: str) -> str:
    profile = CROP_PROFILES.get(crop_type, {})
    return str(profile.get("display_name", crop_type.replace("_", " ").title()))


def _crop_zone_card(crop_zone: str, crop_type: str, x: int) -> str:
    crop_name = _short_label(_crop_display_name(crop_type), 21)
    return f"""
    <g transform="translate({x} 18)" data-crop-zone="{crop_zone}" data-crop-type="{crop_type}">
      <rect x="0" y="0" width="288" height="82" rx="14" fill="rgba(255,255,255,0.78)" stroke="rgba(60,60,67,0.12)"/>
      <rect x="0" y="51" width="288" height="31" rx="12" fill="rgba(143,217,169,0.52)"/>
      <text x="14" y="24" font-size="12" fill="#6e6e73" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-weight="850">{crop_zone}</text>
      <text x="46" y="24" font-size="11" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-weight="800">{crop_name}</text>
      <g transform="translate(0 0)">{_crop_row(crop_type, row_id=f"crop-row-{crop_zone.lower()}", base_y=82, start_x=36, spacing=43, count=6)}</g>
    </g>"""


def _crop_zone_panel(crop_type_s1: str, crop_type_s2: str) -> str:
    return f"""
  <g id="crop-zone-panel" transform="translate(24 320)">
    <text x="0" y="11" font-size="10" fill="#6e6e73" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-weight="850" letter-spacing="0.08em">ZONAS DE CULTIVO</text>
    {_crop_zone_card("S1", crop_type_s1, 0)}
    {_crop_zone_card("S2", crop_type_s2, 304)}
  </g>"""


def generate_solar_svg(
    hour: float,
    track_angle: float,
    rec_angle: float,
    solar_elevation: float,
    irradiance: float,
    next_hour: float | None = None,
    next_track_angle: float | None = None,
    next_rec_angle: float | None = None,
    management_action: str = "sin_manejo_directo",
    panel_action: str = "mantener_placas",
    crop_risk: float | None = None,
    crop_type: str = "lechuga",
    crop_type_s1: str | None = None,
    crop_type_s2: str | None = None,
    zone_label: str | None = None,
    show_zone_panel: bool = True,
) -> str:
    """
    Return a high-resolution inline SVG that animates toward the next hour.

    The app reruns every 3 seconds. This SVG uses the same duration so the scene
    feels continuous: by the time Streamlit refreshes, the animation has reached
    the next state.
    """
    next_hour = hour if next_hour is None else next_hour
    next_track_angle = track_angle if next_track_angle is None else next_track_angle
    next_rec_angle = rec_angle if next_rec_angle is None else next_rec_angle
    crop_type_s1 = crop_type if crop_type_s1 is None else crop_type_s1
    crop_type_s2 = crop_type_s1 if crop_type_s2 is None else crop_type_s2
    svg_height = _H if show_zone_panel else 320

    sun_x, sun_y = _scaled_sun_position(hour)
    next_sun_x, next_sun_y = _scaled_sun_position(next_hour)
    sun_r = 23
    palette = _ambient_palette(hour)
    next_palette = _ambient_palette(next_hour)
    # SVG rotations are clockwise in screen coordinates. Invert the data angle
    # so east/west tracker signs keep the same physical reading in the scene.
    visual_track_angle = -track_angle
    visual_rec_angle = -rec_angle
    next_visual_track_angle = -next_track_angle
    next_visual_rec_angle = -next_rec_angle
    shadow_length, shadow_shift, shadow_opacity = _shadow_geometry(track_angle, solar_elevation, panel_action)
    next_shadow_length, next_shadow_shift, next_shadow_opacity = _shadow_geometry(next_track_angle, solar_elevation, panel_action)

    panels_solid = []
    panels_ghost = []
    panel_shadows = []
    for px, py in _PIVOTS:
        tx = px - _PANEL_W // 2
        ty = py - _PANEL_H // 2
        panels_solid.append(
            f'<g transform="rotate({int(visual_track_angle)},{px},{py})">'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'from="{visual_track_angle:.1f} {px} {py}" to="{next_visual_track_angle:.1f} {px} {py}" '
            f'dur="{_ANIM_DUR}" fill="freeze"/>'
            f'<rect x="{tx}" y="{ty}" width="{_PANEL_W}" height="{_PANEL_H}" rx="5" '
            f'fill="url(#panel)" filter="url(#panelShadow)"/>'
            f'<line x1="{tx + 10}" y1="{ty + 4}" x2="{tx + _PANEL_W - 10}" y2="{ty + 4}" '
            f'stroke="#8fb7ff" stroke-width="1" opacity="0.65"/>'
            f"</g>"
        )
        panels_ghost.append(
            f'<rect x="{tx}" y="{ty}" width="{_PANEL_W}" height="{_PANEL_H}" rx="5" '
            f'fill="none" stroke="#007aff" stroke-width="2" stroke-dasharray="7,5" '
            f'opacity="0.62" transform="rotate({int(visual_rec_angle)},{px},{py})">'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'from="{visual_rec_angle:.1f} {px} {py}" to="{next_visual_rec_angle:.1f} {px} {py}" '
            f'dur="{_ANIM_DUR}" fill="freeze"/>'
            f"</rect>"
        )
        sx = px + shadow_shift - shadow_length / 2
        next_sx = px + next_shadow_shift - next_shadow_length / 2
        panel_shadows.append(
            f'<ellipse cx="{px + shadow_shift:.1f}" cy="{_GROUND_Y + 24}" '
            f'rx="{shadow_length / 2:.1f}" ry="13" fill="#1d1d1f" opacity="{shadow_opacity:.2f}">'
            f'<animate attributeName="cx" from="{px + shadow_shift:.1f}" to="{px + next_shadow_shift:.1f}" dur="{_ANIM_DUR}" fill="freeze"/>'
            f'<animate attributeName="rx" from="{shadow_length / 2:.1f}" to="{next_shadow_length / 2:.1f}" dur="{_ANIM_DUR}" fill="freeze"/>'
            f'<animate attributeName="opacity" from="{shadow_opacity:.2f}" to="{next_shadow_opacity:.2f}" dur="{_ANIM_DUR}" fill="freeze"/>'
            f'</ellipse>'
        )

    cx, cy = _PIVOTS[1]
    arrow_x2, arrow_y2 = cx - 14, cy - 26
    arrow_y1 = sun_y + sun_r + 7
    next_arrow_y1 = next_sun_y + sun_r + 7
    direction = _direction_label(track_angle)
    agri_badge = _short_label(_label_for_action(management_action))
    energy_badge = _short_label(_label_for_action(panel_action))
    crop_label = _short_label(_crop_display_name(crop_type), 16)
    zone_s1_label = _short_label(_crop_display_name(crop_type_s1), 18)
    zone_s2_label = _short_label(_crop_display_name(crop_type_s2), 18)
    zone_heading = f"ZONA {zone_label}" if zone_label else "CULTIVO"
    zone_crop_x = 68 if zone_label else 72
    aria_zone = f" zona {zone_label}" if zone_label else ""
    management_overlay = _management_overlay(management_action)
    crop_zone_panel = _crop_zone_panel(crop_type_s1, crop_type_s2) if show_zone_panel else ""

    svg = f"""<svg viewBox="0 0 {_W} {svg_height}" xmlns="http://www.w3.org/2000/svg"
   role="img" aria-label="Visualización solar de trackers agrovoltaicos{aria_zone} para {crop_label}; S1 {zone_s1_label}; S2 {zone_s2_label}"
   style="width:100%;height:100%;display:block;border-radius:22px;">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{palette["sky_top"]}">{_animate_color("stop-color", palette["sky_top"], next_palette["sky_top"])}</stop>
      <stop offset="55%" stop-color="{palette["sky_mid"]}">{_animate_color("stop-color", palette["sky_mid"], next_palette["sky_mid"])}</stop>
      <stop offset="100%" stop-color="{palette["sky_bot"]}">{_animate_color("stop-color", palette["sky_bot"], next_palette["sky_bot"])}</stop>
    </linearGradient>
    <linearGradient id="gnd" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{palette["ground_top"]}">{_animate_color("stop-color", palette["ground_top"], next_palette["ground_top"])}</stop>
      <stop offset="100%" stop-color="{palette["ground_bot"]}">{_animate_color("stop-color", palette["ground_bot"], next_palette["ground_bot"])}</stop>
    </linearGradient>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0a84ff"/>
      <stop offset="52%" stop-color="#1d1d1f"/>
      <stop offset="100%" stop-color="#3a3a3c"/>
    </linearGradient>
    <marker id="arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#f5a623"/>
    </marker>
    <filter id="glow">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="panelShadow" x="-20%" y="-250%" width="140%" height="600%">
      <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#0b1b33" flood-opacity="0.22"/>
    </filter>
  </defs>

  <rect x="0" y="0" width="{_W}" height="{svg_height}" rx="22" fill="#ffffff"/>
  <rect x="10" y="10" width="{_W - 20}" height="{svg_height - 20}" rx="20" fill="url(#sky)"/>

  <path d="M 54 {_GROUND_Y} Q 320 34 586 {_GROUND_Y}"
        stroke="{palette["arc"]}" stroke-width="2" fill="none" stroke-dasharray="8,8" opacity="0.78">
    {_animate_color("stroke", palette["arc"], next_palette["arc"])}
  </path>

  <g transform="translate({sun_x:.1f} {sun_y:.1f})">
    <animateTransform attributeName="transform" type="translate"
      from="{sun_x:.1f} {sun_y:.1f}" to="{next_sun_x:.1f} {next_sun_y:.1f}"
      dur="{_ANIM_DUR}" fill="freeze"/>
    <circle cx="0" cy="0" r="{sun_r + 9}" fill="{palette["sun_glow"]}"
            filter="url(#glow)" opacity="0.48">{_animate_color("fill", palette["sun_glow"], next_palette["sun_glow"])}</circle>
    <circle cx="0" cy="0" r="{sun_r}" fill="{palette["sun"]}">{_animate_color("fill", palette["sun"], next_palette["sun"])}</circle>
    <circle cx="-6" cy="-7" r="{sun_r * 0.32:.1f}" fill="#fff4bd" opacity="0.9"/>
    {_sun_rays(sun_r)}
  </g>

  <text x="42"  y="288" font-size="13" fill="{palette["label"]}" font-family="-apple-system,BlinkMacSystemFont,sans-serif">06h{_animate_color("fill", palette["label"], next_palette["label"])}</text>
  <text x="304" y="288" font-size="13" fill="{palette["label"]}" font-family="-apple-system,BlinkMacSystemFont,sans-serif">13h{_animate_color("fill", palette["label"], next_palette["label"])}</text>
  <text x="562" y="288" font-size="13" fill="{palette["label"]}" font-family="-apple-system,BlinkMacSystemFont,sans-serif">21h{_animate_color("fill", palette["label"], next_palette["label"])}</text>

  <rect x="10" y="{_GROUND_Y}" width="{_W - 20}" height="58" fill="url(#gnd)"/>
  <g opacity="0.92">{''.join(panel_shadows)}</g>
  <path d="M10 {_GROUND_Y} C120 {_GROUND_Y - 12}, 230 {_GROUND_Y + 7}, 330 {_GROUND_Y - 2} S530 {_GROUND_Y - 10}, 630 {_GROUND_Y + 3}"
        stroke="#ffffff" stroke-width="2" fill="none" opacity="0.45"/>
  <g data-crop-type="{crop_type}">{_crop_row(crop_type)}</g>
  {management_overlay}

  {''.join(f'<line x1="{px}" y1="{_GROUND_Y}" x2="{px}" y2="{py+5}" stroke="#9aa3ad" stroke-width="4" stroke-linecap="round"/>' for px, py in _PIVOTS)}

  {''.join(panels_ghost)}
  {''.join(panels_solid)}

  <line x1="{sun_x:.1f}" y1="{arrow_y1:.1f}"
        x2="{arrow_x2}" y2="{arrow_y2}"
        stroke="#f5a623" stroke-width="2" stroke-dasharray="5,4"
        marker-end="url(#arr)" opacity="0.86">
    <animate attributeName="x1" from="{sun_x:.1f}" to="{next_sun_x:.1f}" dur="{_ANIM_DUR}" fill="freeze"/>
    <animate attributeName="y1" from="{arrow_y1:.1f}" to="{next_arrow_y1:.1f}" dur="{_ANIM_DUR}" fill="freeze"/>
  </line>

  <text x="{max(22.0, sun_x - 18):.0f}" y="{min(sun_y + sun_r + 26, 238):.0f}"
        font-size="13" fill="#a45f00" font-family="-apple-system,BlinkMacSystemFont,sans-serif"
        font-weight="700">{int(hour):02d}:00</text>

  <g transform="translate(28 28)">
    <rect x="0" y="0" width="284" height="98" rx="16" fill="rgba(255,255,255,0.78)" stroke="rgba(60,60,67,0.12)"/>
    <rect x="15" y="15" width="18" height="8" rx="3" fill="#1a7cff"/>
    <text x="42" y="22" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif">Ángulo actual ({int(track_angle)}°)</text>
    <rect x="15" y="32" width="18" height="8" rx="3" fill="none" stroke="#2f8f68"
          stroke-width="2" stroke-dasharray="5,3"/>
    <text x="42" y="40" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif">Ángulo recomendado ({int(rec_angle)}°)</text>
    <circle cx="24" cy="58" r="5" fill="#0a84ff" opacity="0.9"/>
    <text x="42" y="62" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif">Orientación visual: {direction}</text>
    <rect x="15" y="74" width="18" height="8" rx="4" fill="#1d1d1f" opacity="{shadow_opacity:.2f}"/>
    <text x="42" y="82" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif">Sombra proyectada</text>
  </g>

  <g transform="translate(350 26)">
    <rect x="0" y="0" width="252" height="96" rx="17" fill="rgba(255,255,255,0.82)" stroke="rgba(60,60,67,0.12)"/>
    <text x="14" y="17" font-size="10" fill="#6e6e73" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-weight="800">{zone_heading}</text>
    <text x="{zone_crop_x}" y="17" font-size="11" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-weight="800">{crop_label}</text>
    <g transform="translate(14 28)">
      <rect x="0" y="0" width="106" height="52" rx="14" fill="rgba(10,132,255,0.12)" stroke="rgba(10,132,255,0.22)"/>
      <text x="10" y="16" font-size="9" fill="#0a84ff" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-weight="800">AGRONOMICA</text>
      <text x="10" y="35" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-weight="850">{agri_badge}</text>
    </g>
    <g transform="translate(132 28)">
      <rect x="0" y="0" width="106" height="52" rx="14" fill="rgba(109,91,208,0.12)" stroke="rgba(109,91,208,0.22)"/>
      <text x="10" y="16" font-size="9" fill="#6d5bd0" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-weight="800">ENERGETICA</text>
      <text x="10" y="35" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-weight="850">{energy_badge}</text>
    </g>
  </g>
  {crop_zone_panel}
</svg>"""

    return svg
