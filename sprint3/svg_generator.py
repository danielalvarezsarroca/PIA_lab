from solar_logic import calculate_sun_position

# SVG canvas dimensions
_W, _H = 460, 200
# Panel pivot points (x, y) for 3 panels
_PIVOTS = [(130, 160), (230, 155), (330, 160)]
_PANEL_W, _PANEL_H = 80, 9


def _sun_rays(cx: float, cy: float, r: float) -> str:
    import math
    lines = []
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        x1 = cx + r * math.cos(rad)
        y1 = cy + r * math.sin(rad)
        x2 = cx + (r + 8) * math.cos(rad)
        y2 = cy + (r + 8) * math.sin(rad)
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                     f'stroke="#fbbf24" stroke-width="1.5" opacity="0.7"/>')
    return "\n".join(lines)


def generate_solar_svg(
    hour: float,
    track_angle: float,
    rec_angle: float,
    solar_elevation: float,
    irradiance: float,
) -> str:
    """
    Return a full HTML string containing an inline SVG that shows:
    - Sky gradient, sun arc, sun at position for `hour`
    - Three solar panels tilted at `track_angle` (solid blue)
    - Ghost panel at `rec_angle` (dashed green)
    - Irradiance arrow + label
    - Crop emoji row on ground
    """
    sun_x, sun_y = calculate_sun_position(hour)
    sun_r = 16

    panels_solid = []
    panels_ghost = []
    for px, py in _PIVOTS:
        tx = px - _PANEL_W // 2
        ty = py - _PANEL_H // 2
        panels_solid.append(
            f'<rect x="{tx}" y="{ty}" width="{_PANEL_W}" height="{_PANEL_H}" rx="3" '
            f'fill="#1d4ed8" transform="rotate(-{int(track_angle)},{px},{py})"/>'
        )
        panels_ghost.append(
            f'<rect x="{tx}" y="{ty}" width="{_PANEL_W}" height="{_PANEL_H}" rx="3" '
            f'fill="none" stroke="#16a34a" stroke-width="1.5" stroke-dasharray="5,3" '
            f'opacity="0.6" transform="rotate(-{int(rec_angle)},{px},{py})"/>'
        )

    cx, cy = _PIVOTS[1]
    arrow_x2, arrow_y2 = cx - 10, cy - 15

    svg = f"""<svg viewBox="0 0 {_W} {_H}" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-height:240px;border-radius:12px;">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#bfdbfe"/>
      <stop offset="100%" stop-color="#e0f2fe"/>
    </linearGradient>
    <linearGradient id="gnd" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#bbf7d0"/>
      <stop offset="100%" stop-color="#86efac"/>
    </linearGradient>
    <marker id="arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#f59e0b"/>
    </marker>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Sky -->
  <rect x="0" y="0" width="{_W}" height="168" fill="url(#sky)" rx="10"/>

  <!-- Sun arc -->
  <path d="M 30 168 Q 230 15 430 168"
        stroke="#fed7aa" stroke-width="1.5" fill="none" stroke-dasharray="5,3" opacity="0.7"/>

  <!-- Sun -->
  <circle cx="{sun_x:.1f}" cy="{sun_y:.1f}" r="{sun_r + 4}" fill="#fbbf24"
          filter="url(#glow)" opacity="0.85"/>
  <circle cx="{sun_x:.1f}" cy="{sun_y:.1f}" r="{sun_r}" fill="#fde68a"/>
  {_sun_rays(sun_x, sun_y, sun_r)}

  <!-- Hour labels -->
  <text x="18"  y="181" font-size="8" fill="#6b7280" font-family="-apple-system,sans-serif">06h</text>
  <text x="218" y="181" font-size="8" fill="#6b7280" font-family="-apple-system,sans-serif">13h</text>
  <text x="415" y="181" font-size="8" fill="#6b7280" font-family="-apple-system,sans-serif">21h</text>

  <!-- Ground -->
  <rect x="0" y="168" width="{_W}" height="32" fill="url(#gnd)"/>
  <text x="10" y="186" font-size="10" font-family="-apple-system,sans-serif">
    🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱
  </text>

  <!-- Panel mounting poles -->
  {''.join(f'<line x1="{px}" y1="168" x2="{px}" y2="{py+2}" stroke="#9ca3af" stroke-width="2.5" stroke-linecap="round"/>' for px, py in _PIVOTS)}

  <!-- Ghost panels (recommended angle) -->
  {''.join(panels_ghost)}

  <!-- Actual panels -->
  {''.join(panels_solid)}

  <!-- Irradiance arrow -->
  <line x1="{sun_x:.1f}" y1="{sun_y + sun_r + 2:.1f}"
        x2="{arrow_x2}" y2="{arrow_y2}"
        stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,2"
        marker-end="url(#arr)" opacity="0.8"/>
  <text x="{(sun_x + arrow_x2)/2 - 10:.0f}" y="{(sun_y + arrow_y2)/2:.0f}"
        font-size="8" fill="#d97706" font-family="-apple-system,sans-serif"
        font-weight="600">{int(irradiance)} W/m²</text>

  <!-- Current time label -->
  <text x="{max(5.0, sun_x - 12):.0f}" y="{min(sun_y + sun_r + 18, 165):.0f}"
        font-size="8" fill="#d97706" font-family="-apple-system,sans-serif"
        font-weight="700">{int(hour):02d}:00</text>

  <!-- Legend -->
  <rect x="8" y="8" width="10" height="5" rx="1" fill="#1d4ed8"/>
  <text x="21" y="14" font-size="7.5" fill="#374151" font-family="-apple-system,sans-serif">Ángulo actual ({int(track_angle)}°)</text>
  <rect x="8" y="18" width="10" height="5" rx="1" fill="none" stroke="#16a34a"
        stroke-width="1.5" stroke-dasharray="4,2"/>
  <text x="21" y="24" font-size="7.5" fill="#374151" font-family="-apple-system,sans-serif">Ángulo recomendado ({int(rec_angle)}°)</text>
</svg>"""

    return f"<div style='background:#f0f9ff;border-radius:12px;padding:8px;'>{svg}</div>"
