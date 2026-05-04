from solar_logic import calculate_sun_position

_W, _H = 640, 320
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


def _crop_row() -> str:
    plants = []
    for i in range(26):
        x = 32 + i * 22
        h = 12 + (i % 4) * 2
        plants.append(
            f'<g opacity="0.82">'
            f'<path d="M{x} {_GROUND_Y + 38} C{x + 1} {_GROUND_Y + 28}, {x + 2} {_GROUND_Y + 22}, {x + 5} {_GROUND_Y + 16}" '
            f'stroke="#2f8f68" stroke-width="2" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x + 5} {_GROUND_Y + 20} C{x - 2} {_GROUND_Y + h}, {x - 9} {_GROUND_Y + h + 4}, {x - 12} {_GROUND_Y + h + 10}" '
            f'stroke="#68b684" stroke-width="2" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x + 5} {_GROUND_Y + 20} C{x + 12} {_GROUND_Y + h}, {x + 17} {_GROUND_Y + h + 5}, {x + 19} {_GROUND_Y + h + 11}" '
            f'stroke="#68b684" stroke-width="2" fill="none" stroke-linecap="round"/>'
            f"</g>"
        )
    return "".join(plants)


def generate_solar_svg(
    hour: float,
    track_angle: float,
    rec_angle: float,
    solar_elevation: float,
    irradiance: float,
    next_hour: float | None = None,
    next_track_angle: float | None = None,
    next_rec_angle: float | None = None,
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

    panels_solid = []
    panels_ghost = []
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

    cx, cy = _PIVOTS[1]
    arrow_x2, arrow_y2 = cx - 14, cy - 26
    arrow_y1 = sun_y + sun_r + 7
    next_arrow_y1 = next_sun_y + sun_r + 7
    label_x = (sun_x + arrow_x2) / 2 - 10
    label_y = (sun_y + arrow_y2) / 2
    next_label_x = (next_sun_x + arrow_x2) / 2 - 10
    next_label_y = (next_sun_y + arrow_y2) / 2
    direction = _direction_label(track_angle)

    svg = f"""<svg viewBox="0 0 {_W} {_H}" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="Visualización solar de trackers agrovoltaicos"
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

  <rect x="0" y="0" width="{_W}" height="{_H}" rx="22" fill="#ffffff"/>
  <rect x="10" y="10" width="{_W - 20}" height="{_H - 20}" rx="20" fill="url(#sky)"/>

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
  <path d="M10 {_GROUND_Y} C120 {_GROUND_Y - 12}, 230 {_GROUND_Y + 7}, 330 {_GROUND_Y - 2} S530 {_GROUND_Y - 10}, 630 {_GROUND_Y + 3}"
        stroke="#ffffff" stroke-width="2" fill="none" opacity="0.45"/>
  {_crop_row()}

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
  <text x="{label_x:.0f}" y="{label_y:.0f}"
        font-size="13" fill="#a45f00" font-family="-apple-system,BlinkMacSystemFont,sans-serif"
        font-weight="600">{int(irradiance)} W/m²
    <animate attributeName="x" from="{label_x:.0f}" to="{next_label_x:.0f}" dur="{_ANIM_DUR}" fill="freeze"/>
    <animate attributeName="y" from="{label_y:.0f}" to="{next_label_y:.0f}" dur="{_ANIM_DUR}" fill="freeze"/>
  </text>

  <text x="{max(22.0, sun_x - 18):.0f}" y="{min(sun_y + sun_r + 26, 238):.0f}"
        font-size="13" fill="#a45f00" font-family="-apple-system,BlinkMacSystemFont,sans-serif"
        font-weight="700">{int(hour):02d}:00</text>

  <g transform="translate(28 28)">
    <rect x="0" y="0" width="244" height="72" rx="16" fill="rgba(255,255,255,0.76)" stroke="rgba(60,60,67,0.12)"/>
    <rect x="15" y="15" width="18" height="8" rx="3" fill="#1a7cff"/>
    <text x="42" y="22" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif">Ángulo actual ({int(track_angle)}°)</text>
    <rect x="15" y="32" width="18" height="8" rx="3" fill="none" stroke="#2f8f68"
          stroke-width="2" stroke-dasharray="5,3"/>
    <text x="42" y="40" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif">Ángulo recomendado ({int(rec_angle)}°)</text>
    <circle cx="24" cy="58" r="5" fill="#0a84ff" opacity="0.9"/>
    <text x="42" y="62" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif">Orientación visual: {direction}</text>
  </g>
</svg>"""

    return svg
