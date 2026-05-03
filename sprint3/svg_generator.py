from solar_logic import calculate_sun_position

_W, _H = 760, 360
_PIVOTS = [(250, 263), (380, 252), (510, 263)]
_PANEL_W, _PANEL_H = 118, 14


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _format_hour(hour: float) -> str:
    total_minutes = int(round(hour * 60))
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def _sun_rays(cx: float, cy: float, r: float) -> str:
    import math

    lines = []
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        x1 = cx + (r + 4) * math.cos(rad)
        y1 = cy + (r + 4) * math.sin(rad)
        x2 = cx + (r + 15) * math.cos(rad)
        y2 = cy + (r + 15) * math.sin(rad)
        lines.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#f59e0b" stroke-width="2" stroke-linecap="round" opacity="0.68"/>'
        )
    return "\n".join(lines)


def _panel(px: int, py: int, angle: float, idx: int) -> str:
    angle = _clamp(angle, -45.0, 45.0)
    tx = px - _PANEL_W / 2
    ty = py - _PANEL_H / 2
    delay = idx * 0.08
    return f"""
    <g class="panel-live" data-angle="rotate(-{angle:.1f},{px},{py})">
      <animateTransform attributeName="transform" type="rotate"
        from="0 {px} {py}" to="-{angle:.1f} {px} {py}"
        dur="720ms" begin="{delay:.2f}s" fill="freeze"
        calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
      <rect x="{tx:.1f}" y="{ty:.1f}" width="{_PANEL_W}" height="{_PANEL_H}" rx="4"
        fill="url(#panelFill)" stroke="#172554" stroke-width="1.2"/>
      <line x1="{tx + 10:.1f}" y1="{ty + 2:.1f}" x2="{tx + 10:.1f}" y2="{ty + _PANEL_H - 2:.1f}" stroke="#93c5fd" opacity="0.75"/>
      <line x1="{tx + 34:.1f}" y1="{ty + 2:.1f}" x2="{tx + 34:.1f}" y2="{ty + _PANEL_H - 2:.1f}" stroke="#93c5fd" opacity="0.75"/>
      <line x1="{tx + 58:.1f}" y1="{ty + 2:.1f}" x2="{tx + 58:.1f}" y2="{ty + _PANEL_H - 2:.1f}" stroke="#93c5fd" opacity="0.75"/>
      <line x1="{tx + 82:.1f}" y1="{ty + 2:.1f}" x2="{tx + 82:.1f}" y2="{ty + _PANEL_H - 2:.1f}" stroke="#93c5fd" opacity="0.75"/>
    </g>
    <circle cx="{px}" cy="{py}" r="4.3" fill="#334155" stroke="#f8fafc" stroke-width="1.5"/>
    """


def _ghost_panel(px: int, py: int, angle: float) -> str:
    angle = _clamp(angle, -45.0, 45.0)
    tx = px - _PANEL_W / 2
    ty = py - _PANEL_H / 2
    return f"""
    <rect x="{tx:.1f}" y="{ty:.1f}" width="{_PANEL_W}" height="{_PANEL_H}" rx="4"
      fill="none" stroke="#16a34a" stroke-width="2" stroke-dasharray="7,5"
      opacity="0.72" transform="rotate(-{angle:.1f},{px},{py})"/>
    """


def _incidence_beams(sun_x: float, sun_y: float, opacity: float) -> str:
    beams = []
    for i, (px, py) in enumerate(_PIVOTS):
        beam_opacity = _clamp(opacity + 0.12 - i * 0.02, 0.34, 0.72)
        beams.append(
            f"""
    <g class="incidence-beam">
      <line x1="{sun_x:.1f}" y1="{sun_y + 24:.1f}" x2="{px:.1f}" y2="{py - 13:.1f}"
        stroke="#f59e0b" stroke-width="3.2" stroke-dasharray="10,7"
        marker-end="url(#arr)" opacity="{beam_opacity:.2f}"/>
      <line x1="{sun_x:.1f}" y1="{sun_y + 24:.1f}" x2="{px:.1f}" y2="{py - 13:.1f}"
        stroke="#fde68a" stroke-width="8" stroke-linecap="round" opacity="{beam_opacity * 0.14:.2f}"/>
    </g>"""
        )
    return "\n".join(beams)


def generate_solar_svg(
    hour: float,
    track_angle: float,
    rec_angle: float,
    solar_elevation: float,
    irradiance: float,
    target_iec: float | None = None,
    matched_iec: float | None = None,
) -> str:
    """
    Return HTML with an inline SVG solar-tracker scene.

    Blue panels represent the angle selected by the IEC/hour scenario. The
    dashed green outline is the historically recommended angle for that hour.
    """
    raw_sun_x, raw_sun_y = calculate_sun_position(hour)
    sun_x = (raw_sun_x - 30.0) * ((_W - 100.0) / 400.0) + 50.0
    sun_y = _clamp(raw_sun_y * 1.18 - 20.0, 42.0, 230.0)
    sun_r = 22
    elev_pct = _clamp(solar_elevation / 90.0, 0.0, 1.0)
    light_opacity = 0.18 + 0.42 * elev_pct
    target_label = "--" if target_iec is None else f"{target_iec:.2f}"
    matched_label = "--" if matched_iec is None else f"{matched_iec:.2f}"
    hour_label = _format_hour(hour)

    poles = "\n".join(
        f'<line x1="{px}" y1="292" x2="{px}" y2="{py + 2}" stroke="#64748b" '
        f'stroke-width="5" stroke-linecap="round"/>'
        for px, py in _PIVOTS
    )
    incidence = _incidence_beams(sun_x, sun_y, light_opacity)
    ghost = "\n".join(_ghost_panel(px, py, rec_angle) for px, py in _PIVOTS)
    panels = "\n".join(_panel(px, py, track_angle, i) for i, (px, py) in enumerate(_PIVOTS))

    svg = f"""<svg viewBox="0 0 {_W} {_H}" xmlns="http://www.w3.org/2000/svg"
  style="width:100%;height:auto;border-radius:12px;display:block;">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#dbeafe"/>
      <stop offset="58%" stop-color="#ecfeff"/>
      <stop offset="100%" stop-color="#f8fafc"/>
    </linearGradient>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#bbf7d0"/>
      <stop offset="100%" stop-color="#65a30d"/>
    </linearGradient>
    <linearGradient id="panelFill" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#60a5fa"/>
      <stop offset="45%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#1e3a8a"/>
    </linearGradient>
    <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fde68a" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
    </radialGradient>
    <marker id="arr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#f59e0b"/>
    </marker>
    <filter id="softShadow">
      <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#0f172a" flood-opacity="0.18"/>
    </filter>
    <style>
      .label {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; fill:#334155; }}
      .small {{ font-size:13px; }}
      .tiny {{ font-size:11px; }}
      .strong {{ font-weight:700; }}
      .panel-live {{ filter:url(#softShadow); }}
      .sun-core {{ animation:pulse 2.4s ease-in-out infinite; transform-origin:{sun_x:.1f}px {sun_y:.1f}px; }}
      .ray, .incidence-beam {{ animation:rayFade 2.4s ease-in-out infinite; }}
      @keyframes pulse {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.06); }} }}
      @keyframes rayFade {{ 0%,100% {{ opacity:.22; }} 50% {{ opacity:.45; }} }}
    </style>
  </defs>

  <rect x="0" y="0" width="{_W}" height="306" fill="url(#sky)" rx="12"/>
  <path d="M 50 232 Q 380 28 710 232" stroke="#fdba74" stroke-width="2"
    fill="none" stroke-dasharray="8,8" opacity="0.72"/>

  <g class="ray">
    <line x1="{sun_x:.1f}" y1="{sun_y + sun_r:.1f}" x2="380" y2="248"
      stroke="#f59e0b" stroke-width="3" stroke-dasharray="8,8"
      marker-end="url(#arr)" opacity="{light_opacity:.2f}"/>
    <path d="M {sun_x - 55:.1f} {sun_y + 72:.1f} Q 380 178 {sun_x + 70:.1f} {sun_y + 82:.1f}"
      fill="none" stroke="#fbbf24" stroke-width="18" opacity="{light_opacity * 0.35:.2f}"/>
  </g>
  {incidence}

  <circle cx="{sun_x:.1f}" cy="{sun_y:.1f}" r="58" fill="url(#sunGlow)"/>
  <g class="sun-core">
    <circle cx="{sun_x:.1f}" cy="{sun_y:.1f}" r="{sun_r}" fill="#fde047" stroke="#f59e0b" stroke-width="2"/>
    {_sun_rays(sun_x, sun_y, sun_r)}
  </g>
  <text x="{max(18.0, sun_x - 28):.1f}" y="{min(260.0, sun_y + 46):.1f}" class="label small strong">{hour_label}</text>

  <rect x="0" y="292" width="{_W}" height="68" fill="url(#ground)"/>
  <path d="M0 292 C120 280 210 302 330 290 C470 276 560 306 760 288 L760 360 L0 360 Z"
    fill="#86efac" opacity="0.62"/>
  <g opacity="0.65">
    <path d="M96 323 q8 -21 17 0 M113 323 q9 -18 18 0" stroke="#15803d" stroke-width="3" fill="none" stroke-linecap="round"/>
    <path d="M625 326 q8 -20 17 0 M642 326 q10 -22 19 0" stroke="#15803d" stroke-width="3" fill="none" stroke-linecap="round"/>
  </g>

  {poles}
  {ghost}
  {panels}

  <rect x="18" y="18" width="238" height="86" rx="10" fill="#ffffff" opacity="0.88" stroke="#e2e8f0"/>
  <rect x="34" y="36" width="24" height="8" rx="2" fill="#2563eb"/>
  <text x="68" y="44" class="label tiny">Angulo por IEC ({track_angle:.1f} deg)</text>
  <rect x="34" y="58" width="24" height="8" rx="2" fill="none" stroke="#16a34a" stroke-width="2" stroke-dasharray="6,4"/>
  <text x="68" y="66" class="label tiny">Referencia por hora ({rec_angle:.1f} deg)</text>
  <text x="34" y="88" class="label tiny strong">IEC objetivo {target_label} · historico {matched_label}</text>

  <rect x="564" y="18" width="174" height="72" rx="10" fill="#ffffff" opacity="0.88" stroke="#e2e8f0"/>
  <text x="584" y="43" class="label tiny">Irradiancia</text>
  <text x="584" y="69" class="label strong" style="font-size:24px;fill:#d97706;">{int(irradiance)} W/m2</text>

  <text x="38" y="324" class="label tiny">06h</text>
  <text x="368" y="324" class="label tiny">13h</text>
  <text x="696" y="324" class="label tiny">21h</text>
</svg>"""

    return f"<div style='background:#f8fafc;border-radius:12px;padding:8px;border:1px solid #e5e7eb;'>{svg}</div>"
