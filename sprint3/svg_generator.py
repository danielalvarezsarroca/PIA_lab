from solar_logic import calculate_sun_position

_W, _H = 640, 320
_GROUND_Y = 252
_PIVOTS = [(190, 244), (320, 236), (450, 244)]
_PANEL_W, _PANEL_H = 118, 14


def _sun_rays(cx: float, cy: float, r: float) -> str:
    import math

    lines = []
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        x1 = cx + r * math.cos(rad)
        y1 = cy + r * math.sin(rad)
        x2 = cx + (r + 13) * math.cos(rad)
        y2 = cy + (r + 13) * math.sin(rad)
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
) -> str:
    """
    Return a high-resolution inline SVG that shows:
    - sky, sun arc, and sun position for `hour`
    - three solar panels tilted at `track_angle`
    - recommended-angle ghost panels at `rec_angle`
    - irradiance direction and vector crop row
    """
    sun_x, sun_y = _scaled_sun_position(hour)
    sun_r = 23

    panels_solid = []
    panels_ghost = []
    for px, py in _PIVOTS:
        tx = px - _PANEL_W // 2
        ty = py - _PANEL_H // 2
        panels_solid.append(
            f'<g transform="rotate(-{int(track_angle)},{px},{py})">'
            f'<rect x="{tx}" y="{ty}" width="{_PANEL_W}" height="{_PANEL_H}" rx="5" '
            f'fill="url(#panel)" filter="url(#panelShadow)"/>'
            f'<line x1="{tx + 10}" y1="{ty + 4}" x2="{tx + _PANEL_W - 10}" y2="{ty + 4}" '
            f'stroke="#8fb7ff" stroke-width="1" opacity="0.65"/>'
            f"</g>"
        )
        panels_ghost.append(
            f'<rect x="{tx}" y="{ty}" width="{_PANEL_W}" height="{_PANEL_H}" rx="5" '
            f'fill="none" stroke="#2f8f68" stroke-width="2" stroke-dasharray="7,5" '
            f'opacity="0.62" transform="rotate(-{int(rec_angle)},{px},{py})"/>'
        )

    cx, cy = _PIVOTS[1]
    arrow_x2, arrow_y2 = cx - 14, cy - 26

    svg = f"""<svg viewBox="0 0 {_W} {_H}" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="Visualización solar de trackers agrovoltaicos"
     style="width:100%;height:100%;display:block;border-radius:22px;">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#d9ecff"/>
      <stop offset="55%" stop-color="#edf7ff"/>
      <stop offset="100%" stop-color="#f8fbff"/>
    </linearGradient>
    <linearGradient id="gnd" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#c7f0d5"/>
      <stop offset="100%" stop-color="#8fd9a9"/>
    </linearGradient>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1a7cff"/>
      <stop offset="52%" stop-color="#245fd7"/>
      <stop offset="100%" stop-color="#183a93"/>
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
        stroke="#ffd69a" stroke-width="2" fill="none" stroke-dasharray="8,8" opacity="0.78"/>

  <circle cx="{sun_x:.1f}" cy="{sun_y:.1f}" r="{sun_r + 9}" fill="#ffd45f"
          filter="url(#glow)" opacity="0.48"/>
  <circle cx="{sun_x:.1f}" cy="{sun_y:.1f}" r="{sun_r}" fill="#ffe58a"/>
  <circle cx="{sun_x - 6:.1f}" cy="{sun_y - 7:.1f}" r="{sun_r * 0.32:.1f}" fill="#fff4bd" opacity="0.9"/>
  {_sun_rays(sun_x, sun_y, sun_r)}

  <text x="42"  y="288" font-size="13" fill="#6e6e73" font-family="-apple-system,BlinkMacSystemFont,sans-serif">06h</text>
  <text x="304" y="288" font-size="13" fill="#6e6e73" font-family="-apple-system,BlinkMacSystemFont,sans-serif">13h</text>
  <text x="562" y="288" font-size="13" fill="#6e6e73" font-family="-apple-system,BlinkMacSystemFont,sans-serif">21h</text>

  <rect x="10" y="{_GROUND_Y}" width="{_W - 20}" height="58" fill="url(#gnd)"/>
  <path d="M10 {_GROUND_Y} C120 {_GROUND_Y - 12}, 230 {_GROUND_Y + 7}, 330 {_GROUND_Y - 2} S530 {_GROUND_Y - 10}, 630 {_GROUND_Y + 3}"
        stroke="#ffffff" stroke-width="2" fill="none" opacity="0.45"/>
  {_crop_row()}

  {''.join(f'<line x1="{px}" y1="{_GROUND_Y}" x2="{px}" y2="{py+5}" stroke="#9aa3ad" stroke-width="4" stroke-linecap="round"/>' for px, py in _PIVOTS)}

  {''.join(panels_ghost)}
  {''.join(panels_solid)}

  <line x1="{sun_x:.1f}" y1="{sun_y + sun_r + 7:.1f}"
        x2="{arrow_x2}" y2="{arrow_y2}"
        stroke="#f5a623" stroke-width="2" stroke-dasharray="5,4"
        marker-end="url(#arr)" opacity="0.86"/>
  <text x="{(sun_x + arrow_x2)/2 - 10:.0f}" y="{(sun_y + arrow_y2)/2:.0f}"
        font-size="13" fill="#a45f00" font-family="-apple-system,BlinkMacSystemFont,sans-serif"
        font-weight="600">{int(irradiance)} W/m²</text>

  <text x="{max(22.0, sun_x - 18):.0f}" y="{min(sun_y + sun_r + 26, 238):.0f}"
        font-size="13" fill="#a45f00" font-family="-apple-system,BlinkMacSystemFont,sans-serif"
        font-weight="700">{int(hour):02d}:00</text>

  <g transform="translate(28 28)">
    <rect x="0" y="0" width="214" height="54" rx="14" fill="rgba(255,255,255,0.74)" stroke="rgba(60,60,67,0.12)"/>
    <rect x="15" y="15" width="18" height="8" rx="3" fill="#1a7cff"/>
    <text x="42" y="22" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif">Ángulo actual ({int(track_angle)}°)</text>
    <rect x="15" y="32" width="18" height="8" rx="3" fill="none" stroke="#2f8f68"
          stroke-width="2" stroke-dasharray="5,3"/>
    <text x="42" y="40" font-size="12" fill="#1d1d1f" font-family="-apple-system,BlinkMacSystemFont,sans-serif">Ángulo recomendado ({int(rec_angle)}°)</text>
  </g>
</svg>"""

    return (
        "<div style='background:rgba(255,255,255,0.72);border:1px solid rgba(60,60,67,0.12);"
        "border-radius:22px;padding:10px;box-shadow:0 18px 42px rgba(0,0,0,0.075);'>"
        f"{svg}</div>"
    )
