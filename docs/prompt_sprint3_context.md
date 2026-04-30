# Contexto completo — Sprint 3 Dashboard Agrovoltaico
**Pega este prompt al inicio de cualquier conversación nueva sobre este proyecto.**

---

## Instrucciones de trabajo para el LLM

Eres un asistente de ingeniería de software trabajando en el Sprint 3 de un dashboard Streamlit agrovoltaico. Sigue estas reglas en cada tarea:

1. **Usa todas las skills disponibles antes de responder.** Si tienes acceso a un sistema de skills/plugins (superpowers, brainstorming, writing-plans, subagent-driven-development, TDD, executing-plans, etc.), invócalos siempre que apliquen. No empieces a implementar sin pasar primero por las skills relevantes.

2. **TDD obligatorio.** Para cualquier función nueva: primero escribe el test que falla, luego implementa. Los tests van en `sprint3/tests/`. Se ejecutan con `pytest` desde `sprint3/`.

3. **No añadas features no pedidas.** YAGNI estricto. Si la tarea pide un fix, solo arregla eso. No refactorices de paso ni añadas validaciones que no se pidieron.

4. **Sin comentarios de código** salvo que el WHY sea no obvio (restricción oculta, invariante sutil, workaround de un bug específico).

5. **Commits frecuentes y atómicos.** Un commit por tarea o subtarea. Mensaje en inglés, formato `feat/fix/refactor(sprint3): descripción`.

6. **No uses `streamlit run` directamente en Windows PowerShell** — no está en el PATH. Siempre `python -m streamlit run app.py` desde `sprint3/`.

7. **Verifica visualmente** cualquier cambio en la UI arrancando la app. Los tests verifican lógica, no que el dashboard se vea bien.

8. **Diseño: no toques colores ni tipografía** sin que se pida explícitamente. El usuario tiene gustos definidos: paleta verde (#16a34a), tipografía Apple, cards con bordes suaves. Ver sección CSS.

---

## Requisitos de UX — NO negociables

Estos dos requisitos los eligió el usuario explícitamente tras malas experiencias previas. Cualquier cambio que los rompa es un bug aunque el código funcione:

### 1. Tipografía Apple — obligatoria en todos los componentes

La fuente del sistema **DEBE** ser siempre:
```
-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif
```
Reglas:
- Se aplica con `!important` en todos los selectores CSS para cubrir los widgets internos de Streamlit.
- **No usar** `font-family: sans-serif` ni `font-family: inherit` desnudos en elementos nuevos.
- Si añades un componente nuevo (card, badge, tabla), fuerza la fuente Apple explícitamente en su `style`.
- Los tamaños base son intencionadamente más grandes que el default de Streamlit (15px base, 30px valores de KPI). Mantener o aumentar — nunca reducir.

### 2. App fluida — el slider actualiza instantáneamente

El usuario descartó versiones anteriores porque "la web no va fluida". La arquitectura actual resuelve esto con dos mecanismos que **NUNCA** deben eliminarse:

| Mecanismo | Archivo | Por qué no tocarlo |
|-----------|---------|-------------------|
| `@st.cache_data` en todas las funciones de carga | `data_loader.py` | Los CSVs se cargan una sola vez al arrancar |
| `@st.fragment` en `_render_interactive_section` | `tab_estado.py` | Al mover el slider solo se re-ejecuta esa función — NO toda la app |

**Prohibido:**
- Añadir `st.rerun()` dentro de `_render_interactive_section` o en callbacks del slider — causa rerun completo.
- Mover la carga de datos dentro de funciones sin `@st.cache_data` — vuelve a leer CSV en cada interacción.
- Eliminar el `@st.fragment` o sacar el slider fuera de él.
- Usar `@st.experimental_rerun()` (deprecado) en cualquier sitio nuevo.

**Objetivo de rendimiento**: mover el slider de hora debe sentirse instantáneo (< 100 ms de respuesta visual). Si una feature nueva lo degrada, revisar si está dentro o fuera del fragment.

---

## Qué es este proyecto

Proyecto académico (UPC, Q6 PIA) de un sistema **agrovoltaico**: instalación de paneles solares de seguimiento (*trackers*) sobre cultivos agrícolas. El objetivo es maximizar simultáneamente la producción energética y la salud del cultivo.

El índice que mide ese equilibrio se llama **IEC** (Índice Energía-Cultivo):
- Rango real: 0.06 – 0.925
- Media global: ≈ 0.40
- < 0.35 → zona crítica | 0.35–0.60 → zona media | ≥ 0.60 → zona óptima

Hay **10 trackers** (M01–M10) que pueden estar en tres regímenes de seguimiento:

| Régimen | Código | IEC mediano | Descripción |
|---------|--------|-------------|-------------|
| Tracking tarde | `TRACKING_PM` | ≈ 0.74 | El mejor. Sigue el sol de tarde. |
| Tracking mañana | `TRACKING_AM` | ≈ 0.44 | Sigue el sol de mañana. |
| Horizontal | `HORIZONTAL` | ≈ 0.20 | Posición de reposo plana. El peor. |

El Sprint 3 es el **dashboard Streamlit operativo** construido encima de los análisis y reglas de rotación del Sprint 2.

---

## Directorio de trabajo

```
C:\Users\dania\OneDrive - Universitat Politècnica de Catalunya\UPC\Q6\PIA\
```

La app está en `sprint3/`. Los datos vienen de `sprint2/outputs_sprint2/` (un nivel arriba de `sprint3/`).

Rama activa: `main`.

---

## Estructura de archivos

```
sprint3/
├── app.py                        # Entrada. 4 tabs. page_config AQUÍ.
├── data_loader.py                # Carga CSVs con @st.cache_data
├── solar_logic.py                # Posición solar (Bezier) + ángulo recomendado
├── alert_logic.py                # Detección anomalías trackers + tendencia VWC
├── rule_engine.py                # Selección de regla activa por IEC
├── svg_generator.py              # SVG animado del panel solar
├── styles.py                     # CSS Apple-font + helpers card_html / iec_gauge_html
├── tabs/
│   ├── tab_estado.py             # Tab 1 — Dashboard interactivo (el más importante)
│   ├── tab_series.py             # Tab 2 — Series temporales (Plotly)
│   ├── tab_recomendacion.py      # Tab 3 — Detalle reglas de rotación
│   └── tab_alertas.py            # Tab 4 — Alertas activas + diagnóstico
└── tests/
    ├── test_data_loader.py
    ├── test_solar_logic.py
    ├── test_alert_logic.py
    ├── test_rule_engine.py
    └── test_svg_generator.py

sprint2/outputs_sprint2/
├── dataset_modelizacion_6h.csv       # Dataset principal (solo h=0,6,12,18)
├── dataset_integrado_6h.csv          # Series temporales completas (Tab 2)
├── candidate_rotation_rules.csv      # Reglas de rotación del Sprint 2
└── tracker_variance_diagnostic.csv   # Diagnóstico de varianza por tracker
```

---

## Datos de entrada — columnas y quirks

### `dataset_modelizacion_6h.csv` (el más usado)

Columnas clave: `Time`, `hour_of_day`, `IEC`, `track_mean`, `tracking_regime`, `ePAR_S1_mean`, `ePAR_S2_mean`, `VWC_S1_mean`, `VWC_S2_mean`, `solar_elevation_deg`

**QUIRK CRÍTICO**: `hour_of_day` solo tiene los valores **[0, 6, 12, 18]**. El slider de hora del dashboard va de 6 a 21, pero la mayoría de horas no tienen datos directos. **Toda la lógica usa snap al nearest hour** — nunca busca por hora exacta.

```python
# Patrón correcto — SIEMPRE así, nunca df[df["hour_of_day"] == hour] sin fallback
def _get_hour_record(df_modelo, hour):
    rows = df_modelo[df_modelo["hour_of_day"] == hour].dropna(subset=["IEC", "track_mean"])
    if not rows.empty:
        return rows.loc[rows["IEC"].idxmax()]
    valid = df_modelo.dropna(subset=["IEC", "track_mean"])
    idx = (valid["hour_of_day"] - hour).abs().idxmin()
    return valid.loc[idx]
```

### `tracker_variance_diagnostic.csv`

Índice = nombre del tracker con formato `"tracker_M04 (actual)"`. Columna clave: `varianza_deg2`.

Para extraer el ID limpio: `parse_tracker_name()` en `data_loader.py` usa regex `(M\d+)`.

### `candidate_rotation_rules.csv`

Columnas: `regla` (texto de la condición), `tipo` (ej. `"prioridad_alta"`), `iec_mediana`, `soporte_obs`, `comentario`.

---

## Arquitectura del Tab 1 — `tab_estado.py`

Es el tab principal. Usa **`@st.fragment`** (Streamlit ≥ 1.43) para que mover el slider solo rehaga la sección interactiva, no toda la app.

```
render_tab_estado(df_modelo, df_diagnostic, df_rules)
│
├── _render_interactive_section(df_modelo, df_rules)   ← @st.fragment
│   ├── Slider hora (6–21, step=1, format="%d:00")
│   ├── Caja justificación NL (_angle_justification)   ← fondo verde/azul/gris según régimen
│   ├── col_svg (60%): SVG via components.html         ← NO st.markdown (ver sección SVG)
│   ├── col_info (40%): iec_gauge_html + 4 metric cards
│   ├── Fila 4 KPI cards: ePAR S1/S2, VWC S1/S2 con status (_epar_label, _vwc_label)
│   └── Tabla reglas candidatas con badge "● ACTIVA"
│
└── Sección estática (fuera del fragment, no rerrendiza con el slider)
    ├── Grid 10 trackers: varianza + (✓ Normal / ⚠ Alta varianza) (_tracker_label)
    │   + párrafo explicativo debajo del título
    └── Alertas activas (build_alert_list)
```

---

## SVG del panel solar — por qué `components.html` y no `st.markdown`

**`st.markdown(unsafe_allow_html=True)` usa DOMPurify** que elimina silenciosamente:
- `<defs>`, `<linearGradient>`, `<filter>`, `<feGaussianBlur>`, `<feMerge>`, `<marker>`

Sin esos elementos el SVG renderiza solo el fondo y las plantas — los paneles son invisibles. **Siempre usar `st.components.v1.html()`** para el SVG:

```python
import streamlit.components.v1 as components

components.html(
    f"<html><body style='margin:0;padding:0;background:transparent;'>{svg_html}</body></html>",
    height=252,
    scrolling=False,
)
```

### Geometría del SVG (`svg_generator.py`)

Canvas 460×200 px. El sol sigue una curva de Bézier cuadrática:
- P0 = (30, 158) — amanecer 06:00h
- P1 = (230, 15) — cénit (punto de control)
- P2 = (430, 158) — atardecer 21:00h
- `t = (hour - 6) / 15`

Tres paneles en pivotes `(130,160)`, `(230,155)`, `(330,160)` con `_PANEL_W=80, _PANEL_H=9`:
- Azul sólido `#1d4ed8` = ángulo actual (`track_angle`)
- Verde discontinuo `#16a34a` = ángulo recomendado (`rec_angle`)

Ángulos del tracker: negativos = paneles orientados al este, positivos = al oeste. Rango típico: -32° a +33°.

---

## `solar_logic.py` — lógica solar

```python
calculate_sun_position(hour: float) -> tuple[float, float]
    # Devuelve (x, y) SVG coords usando Bezier cuadrático

estimate_solar_elevation(hour: float) -> float
    # Aproximación: max 90° a las 12:30, 0° en amanecer/atardecer
    # Fórmula: max(0, 90 - abs(hour - 12.5) * 8)

get_recommended_angle(hour: int, df_modelo: DataFrame) -> float
    # Snap al nearest hour disponible, devuelve track_mean del mejor IEC
    # ANTES devolvía 0.0 para horas sin datos — ya está corregido
```

---

## `rule_engine.py` — selección de regla activa

```python
get_active_rule_index(df_rules, current_iec) -> int | None
    # Devuelve iloc de la regla con iec_mediana más próxima al IEC actual
    # Devuelve None si df_rules vacío o current_iec es NaN

format_regime_label(regime: str) -> str
    # "TRACKING_PM" -> "Tracking tarde (óptimo)"
    # "TRACKING_AM" -> "Tracking mañana"
    # "HORIZONTAL"  -> "Horizontal (mínimo)"
```

---

## `alert_logic.py` — detección de anomalías

```python
ANOMALY_THRESHOLD = 450.0    # deg² — trackers por encima son anómalos
VWC_ALERT_THRESHOLD = -0.005 # m³/m³·h — tendencia descendente

get_anomalous_trackers(df_diagnostic, threshold=450.0) -> list[str]
    # Devuelve IDs limpios: ["M05", "M07"]

get_vwc_trend(df_modelo) -> float
    # Slope lineal de VWC_S1_mean sobre tiempo (m³/m³·h)
    # Negativo = humedad bajando

build_alert_list(df_diagnostic, df_modelo) -> list[dict]
    # Cada dict: {title, description, severity}
    # severity: "CRÍTICO" (trackers) o "AVISO" (VWC)
```

---

## Umbrales de referencia

| Variable | Umbral / Zona | Significado |
|----------|--------------|-------------|
| `varianza_deg2` | > 450 deg² | Tracker anómalo |
| `VWC_S1/S2_mean` | ≥ 0.30 = bien hidratado | — |
| `VWC_S1/S2_mean` | 0.20–0.30 = adecuado | — |
| `VWC_S1/S2_mean` | < 0.20 = crítico | Riego necesario |
| `ePAR_S1/S2_mean` | ≥ 500 = óptimo | Alta irradiancia PAR |
| `ePAR_S1/S2_mean` | 200–500 = normal | Cultivo activo |
| `ePAR_S1/S2_mean` | < 200 = crítico | Bajo umbral cultivo |
| IEC | < 0.35 = crítico | — |
| IEC | 0.35–0.60 = medio | — |
| IEC | ≥ 0.60 = óptimo | — |
| Tendencia VWC | < -0.005 m³/m³·h | Alerta descendente |

---

## CSS y tipografía — `styles.py`

**No cambiar sin que se pida.** Fuente Apple: `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial`. Se fuerza con `!important` en todos los selectores.

Tamaños actuales (ya aumentados respecto al default de Streamlit):
- Base app: 15px
- Tab labels: 14px (activo: weight 700, underline verde)
- Slider label: 15px bold
- KPI card title: 13px uppercase, valor: 30px
- IEC gauge valor: 42px
- Metric labels (`stMetricLabel`): 13px, valores (`stMetricValue`): 30px

Paleta `COLOR` (dict en `styles.py`, úsalo en f-strings inline):
```python
COLOR = {
    "green":  "#16a34a",   # color principal del sistema
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
```

Helpers en `styles.py`:
```python
card_html(title, value, subtitle="", color="#16a34a") -> str
    # Retorna HTML de una KPI card con borde superior de color

iec_gauge_html(iec_value: float) -> str
    # Gauge con gradiente rojo-ámbar-verde y dot indicador
```

---

## Tab 2 — Series temporales (`tab_series.py`)

Multiselect de variables + filtro de fechas. Usa Plotly Express con `template="simple_white"`. Variables disponibles: ePAR S1/S2, VWC S1/S2, GPOA S1/S2, Tracking M01/M03/M05. Líneas horizontales de umbral (ePAR 200, VWC 0.20) en rojo/ámbar.

## Tab 3 — Recomendación (`tab_recomendacion.py`)

Layout 2 columnas: box de régimen activo (fondo verde claro) + tabla de reglas candidatas. Usa `get_latest_record(df_modelo)` para el IEC estático (no cambia con hora). Regla activa con borde izquierdo verde y badge `● ACTIVA`.

## Tab 4 — Alertas (`tab_alertas.py`)

Lista de alertas con icono/color por severidad + tabla de diagnóstico completa de los 10 trackers ordenada por varianza descendente + gráfico Plotly de VWC últimas 48h con línea de umbral 0.20.

---

## Tests existentes

```
sprint3/tests/
├── test_solar_logic.py     # sun position, elevation, recommended angle
├── test_alert_logic.py     # anomalous trackers, VWC trend, build_alert_list
├── test_rule_engine.py     # get_active_rule_index, format_regime_label
├── test_svg_generator.py   # SVG generation smoke tests
└── test_data_loader.py     # CSV loading, parse_tracker_name
```

Ejecutar: `cd sprint3 && pytest` o `pytest tests/test_nombre.py::test_funcion -v`

---

## Errores ya resueltos — NO repetir

| Bug | Causa | Solución aplicada |
|-----|-------|------------------|
| SVG invisible (solo fondo/plantas) | `st.markdown` usa DOMPurify — elimina `<defs>`, gradientes, filtros, markers | Usar `st.components.v1.html()` |
| Ángulo recomendado siempre 0° | `get_recommended_angle` buscaba hora exacta; dataset solo tiene h=0,6,12,18 | Snap al nearest hour disponible |
| SyntaxError f-string (tab_recomendacion.py) | Backslash dentro de expresión f-string (Python < 3.12) | Extraer variable antes del f-string |
| `streamlit` not recognized (PowerShell) | No está en PATH de Windows | `python -m streamlit run app.py` |

---

## Estado actual del código (2026-04-30)

Todos los archivos están comiteados en `main`. La app arranca sin errores con `python -m streamlit run app.py` desde `sprint3/`.

Commits recientes:
- `6c6e796` — justificación lenguaje natural + labels de estado en métricas + UI varianza trackers
- `530e39e` — fix ángulo recomendado (snap nearest hour)
- `a0fb7e2` — fix SVG (components.html en vez de st.markdown)
- `c5437db` — 4 tabs, eliminado tab_panel_solar.py (absorbido en Tab 1)
- `9f72ac3` — @st.fragment + Tab 1 interactivo completo con slider
- `b67c823` — CSS tipografía Apple aumentada

**Funcionalidades implementadas y funcionando:**
- Tab 1: slider de hora (6–21) → actualiza instantáneamente SVG + IEC + ángulo + régimen + ePAR + VWC + regla activa via `@st.fragment`
- Justificación en lenguaje natural por régimen (TRACKING_PM/AM/HORIZONTAL)
- KPI cards con etiquetas de estado contextuales (colores por umbral)
- Grid de 10 trackers con varianza y badge Normal/Alta varianza
- Alertas CRÍTICO/AVISO en header y Tab 4
- Series temporales con selector de variables y fechas
- Tabla de reglas candidatas con regla activa resaltada
