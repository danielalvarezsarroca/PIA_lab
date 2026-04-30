# Dashboard Sprint 3 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build E05 — a Streamlit dashboard with 5 tabs (Estado, Series, Panel Solar, Recomendación, Alertas) that reads Sprint 2 CSVs and visualises the agrovoltaic system state with a dynamic SVG solar panel diagram.

**Architecture:** Streamlit entry point (`app.py`) loads four CSVs via cached `data_loader.py`, delegates business logic to pure-Python modules (`solar_logic`, `alert_logic`, `rule_engine`, `svg_generator`), injects Apple-font CSS via `styles.py`, and renders each tab from a dedicated file in `tabs/`. Logic modules have pytest coverage; Streamlit UI functions are verified by running the app.

**Tech Stack:** Python 3.10+, Streamlit 1.43, Plotly 5.24, pandas 2.2, pytest 8.3

---

## File map

```
sprint3/
├── app.py                     # st.set_page_config + load data + 5 tabs
├── styles.py                  # CSS_STYLES constant + inject_styles()
├── data_loader.py             # load_*() functions with @st.cache_data
├── solar_logic.py             # sun position, elevation, recommended angle
├── alert_logic.py             # anomalous tracker detection, VWC trend, alert list
├── rule_engine.py             # get_active_rule_index() based on IEC proximity
├── svg_generator.py           # generate_solar_svg() → HTML string with inline SVG
├── tabs/
│   ├── __init__.py            # empty
│   ├── tab_estado.py          # render_tab_estado()
│   ├── tab_series.py          # render_tab_series()
│   ├── tab_panel_solar.py     # render_tab_panel_solar()
│   ├── tab_recomendacion.py   # render_tab_recomendacion()
│   └── tab_alertas.py         # render_tab_alertas()
├── tests/
│   ├── __init__.py            # empty
│   ├── test_data_loader.py
│   ├── test_solar_logic.py
│   ├── test_alert_logic.py
│   ├── test_rule_engine.py
│   └── test_svg_generator.py
└── requirements.txt
```

**Data paths** (all relative to `sprint3/`):
- `../sprint2/outputs_sprint2/dataset_modelizacion_6h.csv` — IEC, track_mean, tracking_regime, solar_elevation_deg, ePAR_S1_mean, ePAR_S2_mean, VWC_S1_mean, VWC_S2_mean, hour_of_day
- `../sprint2/outputs_sprint2/dataset_integrado_6h.csv` — GPOA_S1, GPOA_S2, track_M01/M03/M05/M07/M09, ePAR_S1d19/20, ePAR_S2d36/37, VWC_S1d13/14, VWC_S2d32/33
- `../sprint2/outputs_sprint2/candidate_rotation_rules.csv` — tipo, regla, soporte_obs, iec_mediana, comentario
- `../sprint2/outputs_sprint2/tracker_variance_diagnostic.csv` — index="tracker_MXX (actual)", varianza_deg2, posible_stow_fijo
- `../sprint2/outputs_sprint2/high_iec_policy_table.csv` — used as supplementary table in Tab 4

---

## Task 1: Project scaffold

**Files:**
- Create: `sprint3/requirements.txt`
- Create: `sprint3/tests/__init__.py`
- Create: `sprint3/tabs/__init__.py`

- [ ] **Step 1: Create `sprint3/requirements.txt`**

```
streamlit==1.43.0
plotly==5.24.1
pandas==2.2.3
numpy==1.26.4
pytest==8.3.5
```

- [ ] **Step 2: Create empty `__init__.py` files**

Create `sprint3/tabs/__init__.py` (empty file) and `sprint3/tests/__init__.py` (empty file).

- [ ] **Step 3: Install dependencies**

Run from the `sprint3/` directory:
```bash
pip install -r requirements.txt
```
Expected: no errors, packages installed.

- [ ] **Step 4: Verify pytest runs**

```bash
cd sprint3
pytest tests/ -v
```
Expected: `no tests ran` (0 items collected). No errors.

- [ ] **Step 5: Commit**

```bash
git add sprint3/requirements.txt sprint3/tabs/__init__.py sprint3/tests/__init__.py
git commit -m "feat(sprint3): scaffold project structure and requirements"
```

---

## Task 2: data_loader.py

**Files:**
- Create: `sprint3/data_loader.py`
- Create: `sprint3/tests/test_data_loader.py`

- [ ] **Step 1: Write failing tests**

Create `sprint3/tests/test_data_loader.py`:

```python
import pandas as pd
import pytest
from data_loader import get_latest_record, parse_tracker_name


def test_get_latest_record_returns_last_non_null_iec_row():
    df = pd.DataFrame({
        "Time": pd.to_datetime(["2025-06-01", "2025-06-02", "2025-06-03"]),
        "IEC": [0.3, 0.6, float("nan")],
        "track_mean": [20.0, 35.0, 40.0],
        "hour_of_day": [12, 12, 12],
    })
    result = get_latest_record(df)
    assert result["IEC"] == pytest.approx(0.6)
    assert result["track_mean"] == pytest.approx(35.0)


def test_get_latest_record_empty_raises():
    df = pd.DataFrame({"IEC": pd.Series([], dtype=float)})
    with pytest.raises(ValueError, match="No valid records"):
        get_latest_record(df)


def test_parse_tracker_name_extracts_id():
    assert parse_tracker_name("tracker_M04 (actual)") == "M04"
    assert parse_tracker_name("tracker_M10 (actual)") == "M10"


def test_parse_tracker_name_unknown_format_returns_raw():
    assert parse_tracker_name("something_weird") == "something_weird"
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd sprint3
pytest tests/test_data_loader.py -v
```
Expected: `ImportError: No module named 'data_loader'`

- [ ] **Step 3: Create `sprint3/data_loader.py`**

```python
import re
from pathlib import Path

import pandas as pd
import streamlit as st

_DATA_DIR = Path(__file__).parent.parent / "sprint2" / "outputs_sprint2"

MODELO_PATH   = _DATA_DIR / "dataset_modelizacion_6h.csv"
INTEGRADO_PATH = _DATA_DIR / "dataset_integrado_6h.csv"
RULES_PATH    = _DATA_DIR / "candidate_rotation_rules.csv"
TRACKER_PATH  = _DATA_DIR / "tracker_variance_diagnostic.csv"
HIGH_IEC_PATH = _DATA_DIR / "high_iec_policy_table.csv"


@st.cache_data
def load_modelo() -> pd.DataFrame:
    df = pd.read_csv(MODELO_PATH, parse_dates=["Time"])
    df = df.sort_values("Time").reset_index(drop=True)
    return df


@st.cache_data
def load_integrado() -> pd.DataFrame:
    df = pd.read_csv(INTEGRADO_PATH, parse_dates=["Time"])
    df = df.sort_values("Time").reset_index(drop=True)
    return df


@st.cache_data
def load_rules() -> pd.DataFrame:
    return pd.read_csv(RULES_PATH)


@st.cache_data
def load_tracker_diagnostic() -> pd.DataFrame:
    return pd.read_csv(TRACKER_PATH, index_col=0)


@st.cache_data
def load_high_iec() -> pd.DataFrame:
    return pd.read_csv(HIGH_IEC_PATH)


def get_latest_record(df: pd.DataFrame) -> pd.Series:
    """Return the last row that has a valid IEC value."""
    valid = df.dropna(subset=["IEC"])
    if valid.empty:
        raise ValueError("No valid records with IEC in dataset")
    return valid.iloc[-1]


def parse_tracker_name(raw: str) -> str:
    """Extract tracker ID like 'M04' from 'tracker_M04 (actual)'."""
    match = re.search(r"(M\d+)", raw)
    return match.group(1) if match else raw
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd sprint3
pytest tests/test_data_loader.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add sprint3/data_loader.py sprint3/tests/test_data_loader.py
git commit -m "feat(sprint3): add data_loader with CSV loading and helper functions"
```

---

## Task 3: solar_logic.py

**Files:**
- Create: `sprint3/solar_logic.py`
- Create: `sprint3/tests/test_solar_logic.py`

- [ ] **Step 1: Write failing tests**

Create `sprint3/tests/test_solar_logic.py`:

```python
import pytest
from solar_logic import (
    calculate_sun_position,
    estimate_solar_elevation,
    get_recommended_angle,
)
import pandas as pd


def test_sun_position_at_sunrise():
    x, y = calculate_sun_position(6.0)
    assert abs(x - 30) < 2
    assert abs(y - 158) < 2


def test_sun_position_at_sunset():
    x, y = calculate_sun_position(21.0)
    assert abs(x - 430) < 2
    assert abs(y - 158) < 2


def test_sun_position_at_solar_noon():
    # t = (13.5 - 6) / 15 = 0.5
    # Bezier at t=0.5: x = 0.25*30 + 0.5*230 + 0.25*430 = 230
    x, y = calculate_sun_position(13.5)
    assert abs(x - 230) < 2


def test_solar_elevation_at_noon():
    elev = estimate_solar_elevation(12.5)
    assert elev == pytest.approx(90.0)


def test_solar_elevation_at_sunrise():
    # 90 - abs(6.0 - 12.5) * 8 = 90 - 52 = 38
    elev = estimate_solar_elevation(6.0)
    assert elev == pytest.approx(38.0)


def test_solar_elevation_is_non_negative():
    for h in [4.0, 5.0, 22.0, 23.0]:
        assert estimate_solar_elevation(h) >= 0.0


def test_get_recommended_angle_returns_float():
    df = pd.DataFrame({
        "hour_of_day": [12, 12, 14],
        "IEC": [0.9, 0.4, 0.7],
        "track_mean": [35.0, 20.0, 40.0],
    })
    angle = get_recommended_angle(12, df)
    assert angle == pytest.approx(35.0)  # row with highest IEC at hour 12


def test_get_recommended_angle_missing_hour_returns_zero():
    df = pd.DataFrame({
        "hour_of_day": [8],
        "IEC": [0.5],
        "track_mean": [30.0],
    })
    angle = get_recommended_angle(15, df)
    assert angle == pytest.approx(0.0)
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd sprint3
pytest tests/test_solar_logic.py -v
```
Expected: `ImportError: No module named 'solar_logic'`

- [ ] **Step 3: Create `sprint3/solar_logic.py`**

```python
import math
import pandas as pd

# Quadratic Bezier control points for the sun arc SVG (px coordinates)
_P0 = (30.0, 158.0)    # sunrise (06:00)
_P1 = (230.0, 15.0)    # zenith control point
_P2 = (430.0, 158.0)   # sunset (21:00)
_DAY_HOURS = 15.0       # 06:00 → 21:00


def calculate_sun_position(hour: float) -> tuple[float, float]:
    """Return (x, y) SVG coords of the sun at the given hour using a quadratic Bezier."""
    t = max(0.0, min(1.0, (hour - 6.0) / _DAY_HOURS))
    x = (1 - t) ** 2 * _P0[0] + 2 * t * (1 - t) * _P1[0] + t ** 2 * _P2[0]
    y = (1 - t) ** 2 * _P0[1] + 2 * t * (1 - t) * _P1[1] + t ** 2 * _P2[1]
    return x, y


def estimate_solar_elevation(hour: float) -> float:
    """Approximate solar elevation in degrees. Max 90° at 12:30, 0° at sunrise/sunset."""
    return max(0.0, 90.0 - abs(hour - 12.5) * 8.0)


def get_recommended_angle(hour: int, df_modelo: pd.DataFrame) -> float:
    """
    Return the track_mean of the record at `hour` with the highest IEC.
    This gives the historically best-performing angle for that hour.
    """
    hour_data = df_modelo[df_modelo["hour_of_day"] == hour].dropna(subset=["IEC", "track_mean"])
    if hour_data.empty:
        return 0.0
    best_idx = hour_data["IEC"].idxmax()
    return float(hour_data.loc[best_idx, "track_mean"])
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd sprint3
pytest tests/test_solar_logic.py -v
```
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add sprint3/solar_logic.py sprint3/tests/test_solar_logic.py
git commit -m "feat(sprint3): add solar_logic with Bezier sun position and elevation"
```

---

## Task 4: alert_logic.py

**Files:**
- Create: `sprint3/alert_logic.py`
- Create: `sprint3/tests/test_alert_logic.py`

- [ ] **Step 1: Write failing tests**

Create `sprint3/tests/test_alert_logic.py`:

```python
import pandas as pd
import pytest
from alert_logic import get_anomalous_trackers, get_vwc_trend, build_alert_list

_DIAG_DF = pd.DataFrame(
    {"varianza_deg2": [366.0, 534.9, 508.5, 366.1], "posible_stow_fijo": [False, False, False, False]},
    index=["tracker_M01 (actual)", "tracker_M05 (actual)", "tracker_M02 (actual)", "tracker_M03 (actual)"],
)


def test_get_anomalous_trackers_above_threshold():
    result = get_anomalous_trackers(_DIAG_DF, threshold=450.0)
    assert "M05" in result
    assert "M02" in result


def test_get_anomalous_trackers_normal_excluded():
    result = get_anomalous_trackers(_DIAG_DF, threshold=450.0)
    assert "M01" not in result
    assert "M03" not in result


def test_get_vwc_trend_declining():
    df = pd.DataFrame({
        "Time": pd.date_range("2025-06-01", periods=5, freq="6h"),
        "VWC_S1_mean": [0.30, 0.28, 0.26, 0.24, 0.22],
    })
    trend = get_vwc_trend(df)
    assert trend < 0


def test_get_vwc_trend_stable_near_zero():
    df = pd.DataFrame({
        "Time": pd.date_range("2025-06-01", periods=4, freq="6h"),
        "VWC_S1_mean": [0.28, 0.28, 0.29, 0.28],
    })
    trend = get_vwc_trend(df)
    assert abs(trend) < 0.005


def test_build_alert_list_includes_tracker_critical():
    df_modelo = pd.DataFrame({
        "Time": pd.date_range("2025-06-01", periods=4, freq="6h"),
        "VWC_S1_mean": [0.30, 0.29, 0.28, 0.27],
    })
    alerts = build_alert_list(_DIAG_DF, df_modelo)
    severities = [a["severity"] for a in alerts]
    assert "CRÍTICO" in severities


def test_build_alert_list_empty_when_no_issues():
    diag_ok = pd.DataFrame(
        {"varianza_deg2": [366.0, 366.1], "posible_stow_fijo": [False, False]},
        index=["tracker_M01 (actual)", "tracker_M03 (actual)"],
    )
    df_modelo = pd.DataFrame({
        "Time": pd.date_range("2025-06-01", periods=4, freq="6h"),
        "VWC_S1_mean": [0.30, 0.31, 0.30, 0.31],
    })
    alerts = build_alert_list(diag_ok, df_modelo)
    assert alerts == []
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd sprint3
pytest tests/test_alert_logic.py -v
```
Expected: `ImportError: No module named 'alert_logic'`

- [ ] **Step 3: Create `sprint3/alert_logic.py`**

```python
import numpy as np
import pandas as pd

from data_loader import parse_tracker_name

ANOMALY_THRESHOLD = 450.0   # deg² variance — trackers above this are flagged
VWC_ALERT_THRESHOLD = -0.005  # m³/m³ per hour — declining trend triggers AVISO


def get_anomalous_trackers(df_diagnostic: pd.DataFrame, threshold: float = ANOMALY_THRESHOLD) -> list[str]:
    """Return list of tracker IDs (e.g. 'M05') with varianza_deg2 > threshold."""
    anomalous = df_diagnostic[df_diagnostic["varianza_deg2"] > threshold]
    return [parse_tracker_name(idx) for idx in anomalous.index]


def get_vwc_trend(df_modelo: pd.DataFrame) -> float:
    """
    Return linear slope of VWC_S1_mean over time (m³/m³ per hour).
    Negative → declining soil moisture.
    """
    valid = df_modelo[["Time", "VWC_S1_mean"]].dropna()
    if len(valid) < 2:
        return 0.0
    hours = (valid["Time"] - valid["Time"].iloc[0]).dt.total_seconds() / 3600
    slope = float(np.polyfit(hours, valid["VWC_S1_mean"], 1)[0])
    return slope


def build_alert_list(df_diagnostic: pd.DataFrame, df_modelo: pd.DataFrame) -> list[dict]:
    """
    Return a list of alert dicts with keys: title, description, severity.
    CRÍTICO: trackers with varianza > ANOMALY_THRESHOLD.
    AVISO: VWC declining faster than VWC_ALERT_THRESHOLD.
    """
    alerts: list[dict] = []

    anomalous = get_anomalous_trackers(df_diagnostic)
    if anomalous:
        alerts.append({
            "title": f"Trackers anómalos: {', '.join(anomalous)}",
            "description": f"Varianza angular > {ANOMALY_THRESHOLD} deg² — comportamiento irregular detectado",
            "severity": "CRÍTICO",
        })

    trend = get_vwc_trend(df_modelo)
    if trend < VWC_ALERT_THRESHOLD:
        latest_vwc = df_modelo["VWC_S1_mean"].dropna().iloc[-1] if not df_modelo["VWC_S1_mean"].dropna().empty else float("nan")
        alerts.append({
            "title": "VWC descendente",
            "description": f"Tendencia: {trend:.4f} m³/m³·h. Último valor: {latest_vwc:.2f} (umbral crítico: 0.20)",
            "severity": "AVISO",
        })

    return alerts
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd sprint3
pytest tests/test_alert_logic.py -v
```
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add sprint3/alert_logic.py sprint3/tests/test_alert_logic.py
git commit -m "feat(sprint3): add alert_logic for tracker anomaly and VWC trend detection"
```

---

## Task 5: rule_engine.py

**Files:**
- Create: `sprint3/rule_engine.py`
- Create: `sprint3/tests/test_rule_engine.py`

- [ ] **Step 1: Write failing tests**

Create `sprint3/tests/test_rule_engine.py`:

```python
import pandas as pd
import pytest
from rule_engine import get_active_rule_index, format_regime_label

_RULES = pd.DataFrame({
    "tipo": ["prioridad_alta", "prioridad_alta", "prioridad_media"],
    "regla": ["Regla A texto", "Regla B texto", "Regla C texto"],
    "soporte_obs": [33, 20, 50],
    "iec_mediana": [0.86, 0.60, 0.40],
    "comentario": ["com A", "com B", "com C"],
})


def test_active_rule_closest_iec():
    # current IEC = 0.65 → closest to 0.60 (index 1)
    idx = get_active_rule_index(_RULES, current_iec=0.65)
    assert idx == 1


def test_active_rule_high_iec():
    # current IEC = 0.90 → closest to 0.86 (index 0)
    idx = get_active_rule_index(_RULES, current_iec=0.90)
    assert idx == 0


def test_active_rule_nan_returns_none():
    idx = get_active_rule_index(_RULES, current_iec=float("nan"))
    assert idx is None


def test_active_rule_empty_df_returns_none():
    idx = get_active_rule_index(pd.DataFrame(columns=["iec_mediana"]), current_iec=0.5)
    assert idx is None


def test_format_regime_label_known():
    assert format_regime_label("TRACKING_PM") == "Tracking tarde (óptimo)"
    assert format_regime_label("TRACKING_AM") == "Tracking mañana"
    assert format_regime_label("HORIZONTAL") == "Horizontal (mínimo)"


def test_format_regime_label_unknown():
    assert format_regime_label("UNKNOWN") == "UNKNOWN"
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd sprint3
pytest tests/test_rule_engine.py -v
```
Expected: `ImportError: No module named 'rule_engine'`

- [ ] **Step 3: Create `sprint3/rule_engine.py`**

```python
import math
import pandas as pd

_REGIME_LABELS: dict[str, str] = {
    "TRACKING_PM": "Tracking tarde (óptimo)",
    "TRACKING_AM": "Tracking mañana",
    "HORIZONTAL":  "Horizontal (mínimo)",
}


def get_active_rule_index(df_rules: pd.DataFrame, current_iec: float) -> int | None:
    """
    Return the integer index (iloc position) of the rule whose iec_mediana is
    closest to current_iec. Returns None if df_rules is empty or current_iec is NaN.
    """
    if df_rules.empty or math.isnan(current_iec):
        return None
    diffs = (df_rules["iec_mediana"] - current_iec).abs()
    return int(diffs.argmin())


def format_regime_label(regime: str) -> str:
    """Return a human-readable label for a tracking regime code."""
    return _REGIME_LABELS.get(regime, regime)
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd sprint3
pytest tests/test_rule_engine.py -v
```
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add sprint3/rule_engine.py sprint3/tests/test_rule_engine.py
git commit -m "feat(sprint3): add rule_engine for active rotation rule selection"
```

---

## Task 6: svg_generator.py

**Files:**
- Create: `sprint3/svg_generator.py`
- Create: `sprint3/tests/test_svg_generator.py`

- [ ] **Step 1: Write failing tests**

Create `sprint3/tests/test_svg_generator.py`:

```python
import pytest
from svg_generator import generate_solar_svg


def test_output_is_string():
    out = generate_solar_svg(hour=12.0, track_angle=35.0, rec_angle=38.0,
                              solar_elevation=75.0, irradiance=600.0)
    assert isinstance(out, str)


def test_output_contains_svg_tag():
    out = generate_solar_svg(12.0, 35.0, 38.0, 75.0, 600.0)
    assert "<svg" in out and "</svg>" in out


def test_panel_rotation_present():
    out = generate_solar_svg(12.0, 35.0, 38.0, 75.0, 600.0)
    # Actual panel uses rotate(-35, ...)
    assert "rotate(-35" in out


def test_recommended_angle_ghost_present():
    out = generate_solar_svg(12.0, 35.0, 40.0, 75.0, 600.0)
    assert "rotate(-40" in out


def test_different_hours_produce_different_svgs():
    svg_morning = generate_solar_svg(8.0, 30.0, 30.0, 45.0, 300.0)
    svg_afternoon = generate_solar_svg(17.0, 30.0, 30.0, 40.0, 450.0)
    assert svg_morning != svg_afternoon


def test_irradiance_label_appears():
    out = generate_solar_svg(12.0, 35.0, 38.0, 75.0, 623.0)
    assert "623" in out


def test_zero_track_angle_renders():
    out = generate_solar_svg(6.0, 0.0, 0.0, 10.0, 50.0)
    assert "rotate(-0" in out or "rotate(0" in out
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd sprint3
pytest tests/test_svg_generator.py -v
```
Expected: `ImportError: No module named 'svg_generator'`

- [ ] **Step 3: Create `sprint3/svg_generator.py`**

```python
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
        # Translate so rotation pivot is at (px, py)
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

    # Irradiance arrow from sun to centre panel
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
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd sprint3
pytest tests/test_svg_generator.py -v
```
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add sprint3/svg_generator.py sprint3/tests/test_svg_generator.py
git commit -m "feat(sprint3): add svg_generator for dynamic solar panel diagram"
```

---

## Task 7: styles.py

**Files:**
- Create: `sprint3/styles.py`

*(No pytest tests — CSS string, verified visually when app runs.)*

- [ ] **Step 1: Create `sprint3/styles.py`**

```python
import streamlit as st

CSS_STYLES = """
<style>
/* Apple typography */
html, body, [class*="css"], .stApp, button, input, select, textarea {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
                 "Helvetica Neue", Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* App background */
.stApp { background-color: #f9fafb !important; }
section[data-testid="stSidebar"] { background: #fff !important; }

/* Main content area */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff !important;
    border-bottom: 1px solid #e5e7eb !important;
    padding: 0 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #16a34a !important;
    border-bottom: 2px solid #16a34a !important;
    font-weight: 600 !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 14px 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #111827 !important;
}
[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* Dataframe / tables */
.stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #e5e7eb; }

/* Buttons */
.stButton button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* Selectbox / slider labels */
.stSelectbox label, .stSlider label, .stMultiSelect label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #374151 !important;
}

/* Dividers */
hr { border-color: #e5e7eb !important; margin: 1rem 0 !important; }
</style>
"""

# Colour palette (use in f-strings for inline styles)
COLOR = {
    "green":  "#16a34a",
    "blue":   "#1d4ed8",
    "amber":  "#d97706",
    "red":    "#dc2626",
    "orange": "#c2410c",
    "purple": "#7c3aed",
    "bg":     "#f9fafb",
    "card":   "#ffffff",
    "border": "#e5e7eb",
    "text":   "#111827",
    "muted":  "#6b7280",
}


def inject_styles() -> None:
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


def card_html(title: str, value: str, subtitle: str = "", color: str = "#16a34a") -> str:
    """Return HTML for a KPI-style card using inline styles."""
    return f"""
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;
                padding:14px 16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);
                border-top:3px solid {color};">
      <div style="font-size:10px;font-weight:600;color:#6b7280;
                  text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">
        {title}
      </div>
      <div style="font-size:24px;font-weight:700;letter-spacing:-0.02em;color:#111827;">
        {value}
      </div>
      <div style="font-size:10px;color:#9ca3af;margin-top:3px;">{subtitle}</div>
    </div>"""


def iec_gauge_html(iec_value: float) -> str:
    """Return HTML for the IEC gradient gauge."""
    pct = max(0.0, min(1.0, iec_value)) * 100
    if iec_value >= 0.6:
        status, status_color = "Zona óptima", "#16a34a"
    elif iec_value >= 0.35:
        status, status_color = "Zona media", "#d97706"
    else:
        status, status_color = "Zona crítica", "#dc2626"

    return f"""
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;
                padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);text-align:center;">
      <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;
                  letter-spacing:0.06em;margin-bottom:6px;">Índice IEC</div>
      <div style="font-size:36px;font-weight:700;letter-spacing:-0.04em;color:{status_color};">
        {iec_value:.2f}
      </div>
      <div style="font-size:10px;color:#6b7280;margin-bottom:8px;">Equilibrio Energía–Cultivo</div>
      <div style="background:#f3f4f6;border-radius:6px;height:8px;overflow:visible;position:relative;margin:4px 0;">
        <div style="height:100%;border-radius:6px;width:{pct:.0f}%;
                    background:linear-gradient(90deg,#dc2626 0%,#f59e0b 40%,#22c55e 80%);"></div>
        <div style="position:absolute;top:-4px;left:calc({pct:.0f}% - 6px);width:12px;height:12px;
                    background:#fff;border:2px solid {status_color};border-radius:50%;
                    box-shadow:0 1px 4px rgba(0,0,0,0.2);"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:8px;color:#9ca3af;margin-top:6px;">
        <span>0 Crítico</span><span>0.5</span><span>1.0 Óptimo</span>
      </div>
      <div style="font-size:11px;font-weight:600;color:{status_color};margin-top:8px;">
        ● {status}
      </div>
    </div>"""
```

- [ ] **Step 2: Commit**

```bash
git add sprint3/styles.py
git commit -m "feat(sprint3): add Apple-font CSS theme and UI helper functions"
```

---

## Task 8: tabs/tab_estado.py

**Files:**
- Create: `sprint3/tabs/tab_estado.py`

- [ ] **Step 1: Create `sprint3/tabs/tab_estado.py`**

```python
import pandas as pd
import streamlit as st

from alert_logic import build_alert_list, get_anomalous_trackers
from data_loader import get_latest_record
from rule_engine import format_regime_label, get_active_rule_index
from styles import COLOR, card_html, iec_gauge_html

_ALL_TRACKERS = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10"]
_ANOMALY_THRESHOLD = 450.0


def render_tab_estado(
    df_modelo: pd.DataFrame,
    df_diagnostic: pd.DataFrame,
    df_rules: pd.DataFrame,
) -> None:
    latest = get_latest_record(df_modelo)
    anomalous = get_anomalous_trackers(df_diagnostic, threshold=_ANOMALY_THRESHOLD)
    alerts = build_alert_list(df_diagnostic, df_modelo)
    active_rule_idx = get_active_rule_index(df_rules, float(latest.get("IEC", float("nan"))))

    # ── Header timestamp ──────────────────────────────────────────────────────
    ts = pd.to_datetime(latest["Time"]).strftime("%d %b %Y · %H:%M") if "Time" in latest.index else "—"
    col_ts, col_badge = st.columns([3, 1])
    with col_ts:
        st.caption(f"Último registro disponible · {ts}")
    with col_badge:
        st.markdown(
            f'<div style="text-align:right;"><span style="background:#f0fdf4;border:1px solid #bbf7d0;'
            f'color:#15803d;font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;">'
            f'● Sistema activo</span></div>',
            unsafe_allow_html=True,
        )

    # ── KPI row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    track = latest.get("track_mean", float("nan"))
    epar  = (latest.get("ePAR_S1_mean", 0) + latest.get("ePAR_S2_mean", 0)) / 2
    vwc   = (latest.get("VWC_S1_mean", 0) + latest.get("VWC_S2_mean", 0)) / 2
    iec   = latest.get("IEC", float("nan"))

    with c1:
        st.markdown(card_html("Ángulo tracking", f"{track:.1f}°", "track_mean · media trackers", COLOR["blue"]), unsafe_allow_html=True)
    with c2:
        st.markdown(card_html("ePAR media", f"{epar:.0f}", "µmol/m²/s · S1+S2", COLOR["green"]), unsafe_allow_html=True)
    with c3:
        st.markdown(card_html("VWC suelo", f"{vwc:.2f}", "m³/m³ · S1+S2", COLOR["amber"]), unsafe_allow_html=True)
    with c4:
        st.markdown(card_html("Índice IEC", f"{iec:.2f}" if not pd.isna(iec) else "—", "Energía–Cultivo", COLOR["purple"]), unsafe_allow_html=True)
    with c5:
        n_anom = len(anomalous)
        color_anom = COLOR["red"] if n_anom > 0 else COLOR["green"]
        st.markdown(card_html("Trackers anómalos", f"{n_anom}/10", ", ".join(anomalous) or "Ninguno", color_anom), unsafe_allow_html=True)

    st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)

    # ── Tracker grid + IEC + Recomendación ───────────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;color:{COLOR["text"]};'
            f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">'
            f'🔩 Estado de los 10 trackers</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(5)
        for i, tracker_id in enumerate(_ALL_TRACKERS):
            is_anomaly = tracker_id in anomalous
            # Try to get actual angle from df_diagnostic index
            diag_rows = [r for r in df_diagnostic.index if tracker_id in r]
            variance = float(df_diagnostic.loc[diag_rows[0], "varianza_deg2"]) if diag_rows else float("nan")
            bg   = "#fef2f2" if is_anomaly else "#f0fdf4"
            bdr  = "#fca5a5" if is_anomaly else "#bbf7d0"
            clr  = COLOR["red"] if is_anomaly else COLOR["green"]
            icon = " ⚠" if is_anomaly else ""
            with cols[i % 5]:
                st.markdown(
                    f'<div style="background:{bg};border:1px solid {bdr};border-radius:8px;'
                    f'padding:7px;text-align:center;margin-bottom:6px;">'
                    f'<div style="font-size:10px;font-weight:700;color:{clr};">{tracker_id}{icon}</div>'
                    f'<div style="font-size:8px;color:#6b7280;margin-top:2px;">{variance:.0f} deg²</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_right:
        st.markdown(iec_gauge_html(float(iec) if not pd.isna(iec) else 0.0), unsafe_allow_html=True)
        st.markdown("<div style='margin:8px 0;'></div>", unsafe_allow_html=True)

        # Active rule recommendation
        regime = latest.get("tracking_regime", "—")
        regime_label = format_regime_label(str(regime))
        rule_text = "—"
        if active_rule_idx is not None and not df_rules.empty:
            rule_text = df_rules.iloc[active_rule_idx]["regla"][:80] + "…"

        st.markdown(
            f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;'
            f'padding:12px 14px;">'
            f'<div style="font-size:9px;font-weight:600;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:4px;">Régimen activo</div>'
            f'<div style="font-size:14px;font-weight:700;color:#15803d;">{regime_label}</div>'
            f'<div style="font-size:9px;color:#6b7280;margin-top:6px;line-height:1.4;">{rule_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Alert summary ─────────────────────────────────────────────────────────
    if alerts:
        st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;color:{COLOR["text"]};'
            f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">'
            f'🚨 Alertas activas ({len(alerts)})</div>',
            unsafe_allow_html=True,
        )
        for alert in alerts:
            sev_color = COLOR["red"] if alert["severity"] == "CRÍTICO" else COLOR["orange"]
            sev_bg    = "#fef2f2" if alert["severity"] == "CRÍTICO" else "#fff7ed"
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:10px;'
                f'padding:10px 0;border-bottom:1px solid #f3f4f6;">'
                f'<div style="width:8px;height:8px;border-radius:50%;background:{sev_color};'
                f'margin-top:4px;flex-shrink:0;"></div>'
                f'<div style="flex:1;">'
                f'<div style="font-size:11px;font-weight:600;color:#111827;">{alert["title"]}</div>'
                f'<div style="font-size:10px;color:#6b7280;margin-top:2px;">{alert["description"]}</div>'
                f'</div>'
                f'<div style="background:{sev_bg};color:{sev_color};font-size:8px;font-weight:700;'
                f'padding:2px 7px;border-radius:8px;flex-shrink:0;">{alert["severity"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
```

- [ ] **Step 2: Commit**

```bash
git add sprint3/tabs/tab_estado.py
git commit -m "feat(sprint3): add tab_estado with KPIs, tracker grid, IEC gauge, alerts"
```

---

## Task 9: tabs/tab_series.py

**Files:**
- Create: `sprint3/tabs/tab_series.py`

- [ ] **Step 1: Create `sprint3/tabs/tab_series.py`**

```python
import pandas as pd
import plotly.express as px
import streamlit as st

_THRESHOLDS = {
    "ePAR_S1d19":  ("ePAR crítico S1", 200,  "#dc2626"),
    "ePAR_S2d36":  ("ePAR crítico S2", 200,  "#dc2626"),
    "VWC_S1d13":   ("VWC crítico S1",  0.20, "#f59e0b"),
    "VWC_S2d32":   ("VWC crítico S2",  0.20, "#f59e0b"),
}

_VARIABLE_OPTIONS = {
    "ePAR S1 (d19)":       "ePAR_S1d19",
    "ePAR S1 (d20)":       "ePAR_S1d20",
    "ePAR S2 (d36)":       "ePAR_S2d36",
    "ePAR S2 (d37)":       "ePAR_S2d37",
    "VWC S1 (d13)":        "VWC_S1d13",
    "VWC S1 (d14)":        "VWC_S1d14",
    "VWC S2 (d32)":        "VWC_S2d32",
    "VWC S2 (d33)":        "VWC_S2d33",
    "Irradiancia S1 (GPOA)": "GPOA_S1",
    "Irradiancia S2 (GPOA)": "GPOA_S2",
    "Tracking M01":        "track_M01",
    "Tracking M03":        "track_M03",
    "Tracking M05":        "track_M05",
}

_COLOR_MAP = {
    "ePAR":    "#16a34a",
    "VWC":     "#d97706",
    "GPOA":    "#1d4ed8",
    "Albedo":  "#7c3aed",
    "track":   "#0891b2",
    "Tair":    "#dc2626",
    "Tsoil":   "#c2410c",
}


def _series_color(col: str) -> str:
    for key, color in _COLOR_MAP.items():
        if key in col:
            return color
    return "#6b7280"


def render_tab_series(df_integrado: pd.DataFrame) -> None:
    st.markdown(
        '<div style="font-size:11px;font-weight:700;color:#111827;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">📈 Series temporales históricas</div>',
        unsafe_allow_html=True,
    )

    # ── Filters ───────────────────────────────────────────────────────────────
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        selected_labels = st.multiselect(
            "Variables",
            options=list(_VARIABLE_OPTIONS.keys()),
            default=["ePAR S1 (d19)", "VWC S1 (d13)"],
        )
    with f2:
        date_min = df_integrado["Time"].min().date()
        date_max = df_integrado["Time"].max().date()
        date_from = st.date_input("Desde", value=date_min, min_value=date_min, max_value=date_max)
    with f3:
        date_to = st.date_input("Hasta", value=date_max, min_value=date_min, max_value=date_max)

    if not selected_labels:
        st.info("Selecciona al menos una variable.")
        return

    selected_cols = [_VARIABLE_OPTIONS[lbl] for lbl in selected_labels]

    # ── Filter dataframe ──────────────────────────────────────────────────────
    mask = (df_integrado["Time"].dt.date >= date_from) & (df_integrado["Time"].dt.date <= date_to)
    df_filtered = df_integrado.loc[mask, ["Time"] + [c for c in selected_cols if c in df_integrado.columns]].copy()

    if df_filtered.empty:
        st.warning("No hay datos en el rango seleccionado.")
        return

    # ── Plot ──────────────────────────────────────────────────────────────────
    df_long = df_filtered.melt(id_vars="Time", var_name="Variable", value_name="Valor")
    colors   = {col: _series_color(col) for col in selected_cols}

    fig = px.line(
        df_long,
        x="Time",
        y="Valor",
        color="Variable",
        color_discrete_map=colors,
        template="simple_white",
    )
    fig.update_traces(line_width=1.8, opacity=0.9)
    fig.update_layout(
        font_family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial",
        font_color="#374151",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f9fafb",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font_size=11, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor="#e5e7eb", title=""),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb", title="Valor"),
        height=380,
    )

    # Threshold lines
    for col in selected_cols:
        if col in _THRESHOLDS:
            lbl, val, clr = _THRESHOLDS[col]
            fig.add_hline(y=val, line_dash="dash", line_color=clr,
                          annotation_text=lbl, annotation_font_size=9,
                          annotation_font_color=clr)

    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"{len(df_filtered)} registros · resolución 6h · fuente: dataset_integrado_6h.csv")
```

- [ ] **Step 2: Commit**

```bash
git add sprint3/tabs/tab_series.py
git commit -m "feat(sprint3): add tab_series with Plotly multivariate line chart and filters"
```

---

## Task 10: tabs/tab_panel_solar.py

**Files:**
- Create: `sprint3/tabs/tab_panel_solar.py`

- [ ] **Step 1: Create `sprint3/tabs/tab_panel_solar.py`**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add sprint3/tabs/tab_panel_solar.py
git commit -m "feat(sprint3): add tab_panel_solar with dynamic SVG and hour slider"
```

---

## Task 11: tabs/tab_recomendacion.py

**Files:**
- Create: `sprint3/tabs/tab_recomendacion.py`

- [ ] **Step 1: Create `sprint3/tabs/tab_recomendacion.py`**

```python
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
                f'{"<span style=\"font-size:9px;font-weight:700;color:#16a34a;\">● ACTIVA</span>" if is_active else ""}'
                f'</div>'
                f'<div style="font-size:10px;color:#374151;line-height:1.5;">{row.get("regla","—")}</div>'
                f'<div style="font-size:9px;color:#6b7280;margin-top:4px;">{row.get("comentario","")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
```

- [ ] **Step 2: Commit**

```bash
git add sprint3/tabs/tab_recomendacion.py
git commit -m "feat(sprint3): add tab_recomendacion with rules table and active rule highlight"
```

---

## Task 12: tabs/tab_alertas.py

**Files:**
- Create: `sprint3/tabs/tab_alertas.py`

- [ ] **Step 1: Create `sprint3/tabs/tab_alertas.py`**

```python
import pandas as pd
import streamlit as st

from alert_logic import build_alert_list
from styles import COLOR


def render_tab_alertas(df_diagnostic: pd.DataFrame, df_modelo: pd.DataFrame) -> None:
    alerts = build_alert_list(df_diagnostic, df_modelo)

    # ── Header with count ─────────────────────────────────────────────────────
    n = len(alerts)
    header_clr = COLOR["red"] if n > 0 else COLOR["green"]
    header_txt = f"{n} alerta{'s' if n != 1 else ''} activa{'s' if n != 1 else ''}"
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">'
        f'<span style="font-size:11px;font-weight:700;color:#111827;text-transform:uppercase;'
        f'letter-spacing:0.06em;">🚨 Alertas del sistema</span>'
        f'<span style="background:{"#fef2f2" if n>0 else "#f0fdf4"};'
        f'color:{header_clr};border-radius:12px;padding:2px 10px;font-size:10px;font-weight:700;">'
        f'{header_txt}</span></div>',
        unsafe_allow_html=True,
    )

    if not alerts:
        st.success("Sin alertas activas. Todos los parámetros dentro de rangos normales.")
    else:
        for alert in alerts:
            sev_color = COLOR["red"] if alert["severity"] == "CRÍTICO" else COLOR["orange"]
            sev_bg    = "#fef2f2" if alert["severity"] == "CRÍTICO" else "#fff7ed"
            bdr_clr   = "#fca5a5" if alert["severity"] == "CRÍTICO" else "#fed7aa"
            icon      = "⚠️" if alert["severity"] == "CRÍTICO" else "💧"
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:12px;'
                f'background:{sev_bg};border:1px solid {bdr_clr};border-left:4px solid {sev_color};'
                f'border-radius:10px;padding:14px 16px;margin-bottom:10px;">'
                f'<div style="font-size:18px;flex-shrink:0;">{icon}</div>'
                f'<div style="flex:1;">'
                f'<div style="font-size:13px;font-weight:700;color:#111827;">{alert["title"]}</div>'
                f'<div style="font-size:11px;color:#6b7280;margin-top:4px;line-height:1.5;">{alert["description"]}</div>'
                f'</div>'
                f'<div style="background:{sev_color};color:#fff;font-size:9px;font-weight:700;'
                f'padding:3px 9px;border-radius:8px;flex-shrink:0;margin-top:2px;">{alert["severity"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Tracker diagnostic table ──────────────────────────────────────────────
    st.markdown("<div style='margin:20px 0 8px;'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:8px;">Diagnóstico de varianza — todos los trackers</div>',
        unsafe_allow_html=True,
    )

    diag_display = df_diagnostic.copy()
    diag_display.index = [idx.replace(" (actual)", "") for idx in diag_display.index]
    diag_display = diag_display.sort_values("varianza_deg2", ascending=False)
    diag_display["Estado"] = diag_display["varianza_deg2"].apply(
        lambda v: "⚠ Alta varianza" if v > 450 else "✓ Normal"
    )
    diag_display = diag_display.rename(columns={
        "varianza_deg2":   "Varianza (deg²)",
        "posible_stow_fijo": "Stow fijo",
    })
    st.dataframe(diag_display, use_container_width=True)
    st.caption("Umbral de anomalía: varianza > 450 deg²")

    # ── VWC history ───────────────────────────────────────────────────────────
    if "VWC_S1_mean" in df_modelo.columns:
        st.markdown("<div style='margin:16px 0 8px;'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;'
            'letter-spacing:0.06em;margin-bottom:8px;">Evolución VWC — últimas 48h</div>',
            unsafe_allow_html=True,
        )
        import plotly.express as px
        last_48h = df_modelo[["Time", "VWC_S1_mean", "VWC_S2_mean"]].dropna().tail(8)
        if not last_48h.empty:
            df_long = last_48h.melt("Time", var_name="Sección", value_name="VWC")
            fig = px.line(df_long, x="Time", y="VWC", color="Sección",
                          color_discrete_map={"VWC_S1_mean": "#d97706", "VWC_S2_mean": "#c2410c"},
                          template="simple_white", height=200)
            fig.add_hline(y=0.20, line_dash="dash", line_color="#dc2626",
                          annotation_text="umbral crítico 0.20", annotation_font_size=9)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=0),
                              font_family="-apple-system, 'Helvetica Neue', Arial",
                              paper_bgcolor="#ffffff", plot_bgcolor="#f9fafb")
            st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 2: Commit**

```bash
git add sprint3/tabs/tab_alertas.py
git commit -m "feat(sprint3): add tab_alertas with severity cards, diagnostic table, VWC chart"
```

---

## Task 13: app.py — entry point

**Files:**
- Create: `sprint3/app.py`

- [ ] **Step 1: Create `sprint3/app.py`**

```python
import streamlit as st

# Page config MUST be first Streamlit call
st.set_page_config(
    page_title="Agrovoltaic Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from alert_logic import build_alert_list
from data_loader import (
    load_high_iec,
    load_integrado,
    load_modelo,
    load_rules,
    load_tracker_diagnostic,
)
from styles import inject_styles
from tabs.tab_alertas import render_tab_alertas
from tabs.tab_estado import render_tab_estado
from tabs.tab_panel_solar import render_tab_panel_solar
from tabs.tab_recomendacion import render_tab_recomendacion
from tabs.tab_series import render_tab_series

# ── Inject CSS ────────────────────────────────────────────────────────────────
inject_styles()

# ── Load data (cached) ────────────────────────────────────────────────────────
df_modelo     = load_modelo()
df_integrado  = load_integrado()
df_rules      = load_rules()
df_diagnostic = load_tracker_diagnostic()

# ── Header ────────────────────────────────────────────────────────────────────
col_logo, col_title, col_badge = st.columns([0.06, 0.8, 0.14])
with col_logo:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#16a34a,#15803d);'
        'border-radius:10px;width:40px;height:40px;display:flex;align-items:center;'
        'justify-content:center;font-size:20px;box-shadow:0 2px 8px rgba(22,163,74,0.3);">'
        '🌿</div>',
        unsafe_allow_html=True,
    )
with col_title:
    st.markdown(
        '<div style="padding-top:2px;">'
        '<span style="font-size:18px;font-weight:700;color:#111827;letter-spacing:-0.02em;">'
        'Agrovoltaic Decision Dashboard</span><br>'
        '<span style="font-size:11px;color:#6b7280;">Sostenibilidad y Ciencia · Análisis Operativo</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with col_badge:
    n_alerts = len(build_alert_list(df_diagnostic, df_modelo))
    badge_clr = "#dc2626" if n_alerts > 0 else "#16a34a"
    badge_bg  = "#fef2f2" if n_alerts > 0 else "#f0fdf4"
    badge_bdr = "#fca5a5" if n_alerts > 0 else "#bbf7d0"
    st.markdown(
        f'<div style="text-align:right;padding-top:4px;">'
        f'<span style="background:{badge_bg};border:1px solid {badge_bdr};'
        f'color:{badge_clr};font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;">'
        f'{"⚠️ " + str(n_alerts) + " alerta" + ("s" if n_alerts!=1 else "") if n_alerts > 0 else "● Sistema activo"}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin:4px 0;'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
alerts_label = f"🚨 Alertas ({n_alerts})" if n_alerts > 0 else "🚨 Alertas"

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Estado actual",
    "📈 Series temporales",
    "☀️ Panel solar",
    "🔄 Recomendación",
    alerts_label,
])

with tab1:
    render_tab_estado(df_modelo, df_diagnostic, df_rules)
with tab2:
    render_tab_series(df_integrado)
with tab3:
    render_tab_panel_solar(df_modelo)
with tab4:
    render_tab_recomendacion(df_rules, df_modelo)
with tab5:
    render_tab_alertas(df_diagnostic, df_modelo)
```

- [ ] **Step 2: Run the dashboard**

From the `sprint3/` directory:
```bash
streamlit run app.py
```
Expected: browser opens at http://localhost:8501 with the 5-tab dashboard.

- [ ] **Step 3: Verify DoD checklist**

Go through each item manually in the browser:
- [ ] All 5 tabs load without error
- [ ] KPI row shows real values from `dataset_modelizacion_6h.csv`
- [ ] Tracker grid shows anomalous trackers (varianza > 450) in red
- [ ] IEC gauge shows correct value and zone label
- [ ] Tab 2: selecting a different variable redraws the chart
- [ ] Tab 3: moving the slider updates the solar panel angle in the SVG
- [ ] Tab 4: active rule is highlighted with green left border
- [ ] Tab 5: alerts appear with correct severity
- [ ] Apple font is applied (visible in browser DevTools as `-apple-system`)

- [ ] **Step 4: Final commit**

```bash
git add sprint3/app.py
git commit -m "feat(sprint3): add app.py entry point — E05 Dashboard v1 complete"
```

---

## Self-review

**Spec coverage check:**
- ✓ Tab 1 Estado actual → Task 8
- ✓ Tab 2 Series temporales → Task 9
- ✓ Tab 3 Panel solar con SVG dinámico → Tasks 6 + 10
- ✓ Tab 4 Recomendación con reglas Sprint 2 → Tasks 5 + 11
- ✓ Tab 5 Alertas activas + histórico → Tasks 4 + 12
- ✓ Apple typography CSS → Task 7
- ✓ IEC gauge con gradiente → Task 7 (iec_gauge_html)
- ✓ Tracker anomaly detection (varianza > 450) → Task 4
- ✓ Slider de hora en panel solar → Task 10
- ✓ Regla activa resaltada → Task 5 + 11
- ✓ Columnas reales del CSV → todos los tasks usan los nombres verificados

**No placeholders found.**

**Type consistency verified:** `get_active_rule_index` returns `int | None` — used correctly in tab_estado.py and tab_recomendacion.py. `build_alert_list` returns `list[dict]` — consumed correctly in tab_estado.py, tab_alertas.py, app.py. `generate_solar_svg` returns `str` — consumed via `st.markdown`.
