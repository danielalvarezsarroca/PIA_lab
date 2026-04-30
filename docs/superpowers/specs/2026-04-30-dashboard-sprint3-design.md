# Dashboard Sprint 3 — Design Spec
**Proyecto:** Análisis y Optimización Operativa de Sistemas Agrovoltaicos Dinámicos  
**Fecha:** 2026-04-30  
**Entregable:** E05 — Dashboard v1 (prototipo funcional)

---

## Decisiones de diseño

| Decisión | Elección | Razón |
|----------|----------|-------|
| Framework | Streamlit | Compatible con Python/pandas existente; `st.tabs()` nativo; despliegue con `streamlit run` |
| Layout | Tabs horizontales (5 tabs) | Separación clara de secciones; badge de alertas siempre visible |
| Tema visual | Fondo blanco, paleta multicolor | Legible para presentaciones académicas y entrega zip |
| Tipografía | Apple system (`-apple-system, SF Pro`) | Vía CSS custom inyectado con `st.markdown` |
| Gráficas | Plotly Express | Interactivo, compatible con Streamlit, exportable |
| Panel solar | SVG dinámico generado en Python | Permite animar el ángulo del panel en función de la hora seleccionada |

---

## Estructura de tabs

### Tab 1 — Estado actual
- 5 KPI cards: Ángulo tracking M01, ePAR, VWC, IEC, Trackers anómalos
- Grilla de 10 trackers (M01–M10) con estado OK / ANOMALÍA (M02, M06, M10 en rojo)
- Gauge del Índice IEC con barra de gradiente rojo→ámbar→verde y marcador en 0.71
- Box de recomendación activa (regla R2 del Sprint 2)
- Resumen de alertas (2 activas: trackers + VWC descendente)
- **"Último registro disponible"**: se carga la última fila del dataset_integrado_6h.csv

### Tab 2 — Series temporales
- Gráfica Plotly interactiva (line chart)
- Filtros: variable (ePAR, VWC, Tracking °, IEC, Irradiancia), sección (S1, S2)
- Selector de rango de fechas
- Línea horizontal de umbral crítico (ePAR < 200, VWC < 0.20)
- Fuente: `sprint2/outputs_sprint2/dataset_integrado_6h.csv`

### Tab 3 — Panel solar
- SVG generado dinámicamente en Python (via `st.components.v1.html`)
- Escena: arco solar del día completo con marcadores horarios, sol en posición actual, 3 paneles inclinados, cultivo bajo los paneles, flechas de irradiancia, sombras
- Ángulo actual (azul sólido) vs ángulo recomendado (verde discontinuo)
- Slider de hora (`st.slider` de 6 a 21h) que actualiza en tiempo real:
  - Posición del sol en el arco
  - Ángulo de rotación óptimo según regla activa del Sprint 2
  - Elevación solar estimada
- Panel de métricas: ángulo actual, ángulo recomendado, elevación solar, estado (en rango / fuera de rango)

### Tab 4 — Recomendación de rotación
- Tabla de las 6 reglas candidatas del Sprint 2 (`candidate_rotation_rules.csv`)
- Regla activa resaltada (borde verde izquierdo) según condición del último registro
- Box de recomendación: ángulo óptimo + IEC + regla activada
- Fuente: `sprint2/outputs_sprint2/candidate_rotation_rules.csv`, `high_iec_policy_table.csv`

### Tab 5 — Alertas
- Lista de alertas activas con severidad CRÍTICO / AVISO
- **Alertas hardcodeadas por lógica:**
  - CRÍTICO: Trackers M02, M06, M10 — ángulo fijo 50.6°, varianza cero
  - AVISO: VWC descendente — si tendencia_vwc < -0.02/día
- Fuente: `sprint2/outputs_sprint2/tracker_variance_diagnostic.csv`
- Histórico de alertas con timestamp (tabla scrollable)

---

## Datos de entrada

| Archivo | Uso |
|---------|-----|
| `sprint2/outputs_sprint2/dataset_integrado_6h.csv` | Series temporales (ePAR por sensor, VWC, irradiancia, tracking) |
| `sprint2/outputs_sprint2/dataset_modelizacion_6h.csv` | Estado actual (última fila): track_mean, IEC, regimen, solar_elevation |
| `sprint2/outputs_sprint2/candidate_rotation_rules.csv` | Tabla de reglas Tab 4 (tipo, regla, iec_mediana, comentario) |
| `sprint2/outputs_sprint2/high_iec_policy_table.csv` | Política IEC alta para Tab 4 |
| `sprint2/outputs_sprint2/tracker_variance_diagnostic.csv` | Detección de trackers anómalos (varianza > 450 deg²) |

---

## Arquitectura de archivos

```
sprint3/
├── app.py                  # Entrada principal: st.set_page_config + tabs
├── styles.py               # CSS custom (tema blanco + tipografía Apple)
├── data_loader.py          # Carga y caché de los 4 CSVs con @st.cache_data
├── tabs/
│   ├── tab_estado.py       # Tab 1: KPIs + trackers + IEC + recomendación
│   ├── tab_series.py       # Tab 2: Plotly time series + filtros
│   ├── tab_panel_solar.py  # Tab 3: SVG dinámico + slider de hora
│   ├── tab_recomendacion.py# Tab 4: tabla de reglas + regla activa
│   └── tab_alertas.py      # Tab 5: alertas activas + histórico
└── requirements.txt        # streamlit, plotly, pandas
```

---

## Lógica de la visualización del panel solar (Tab 3)

1. El slider devuelve una hora `h` ∈ [6, 21]
2. Elevación solar estimada: `elev = max(0, 90 - abs(h - 12.5) * 8)` (simplificación geométrica)
3. Posición del sol en el arco SVG: interpolación cuadrática Bezier con t = (h-6)/15
4. Ángulo recomendado según hora: aplicar la regla activa del Sprint 2 para la condición del registro más cercano a esa hora en el dataset
5. Panel dibujado con `transform="rotate(-angulo, pivot_x, pivot_y)"` en el SVG generado como string Python → `st.components.v1.html()`

---

## CSS custom (tema)

Inyectado una sola vez en `app.py` vía `st.markdown(css, unsafe_allow_html=True)`:
- `font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif`
- Fondo body: `#f9fafb`
- Cards: `background: #ffffff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04)`
- Paleta: verde `#16a34a`, azul `#1d4ed8`, ámbar `#d97706`, rojo `#dc2626`, naranja `#c2410c`, morado `#7c3aed`

---

## KPIs — fuente de datos y columnas reales

El dashboard usa **dos CSVs** según el tab:
- `dataset_integrado_6h.csv` → series temporales y estado actual (última fila)
- `dataset_modelizacion_6h.csv` → IEC, solar_elevation_deg, tracking_regime (más completo)

| KPI | Columna real | Dataset |
|-----|-------------|---------|
| Ángulo tracking (media) | `track_mean` | modelizacion_6h |
| Régimen activo | `tracking_regime` (HORIZONTAL / TRACKING_AM / TRACKING_PM) | modelizacion_6h |
| ePAR S1 | `ePAR_S1_mean` | modelizacion_6h |
| ePAR S2 | `ePAR_S2_mean` | modelizacion_6h |
| VWC S1 | `VWC_S1_mean` | modelizacion_6h |
| VWC S2 | `VWC_S2_mean` | modelizacion_6h |
| IEC | `IEC` (rango real: 0.06–0.93, media 0.40) | modelizacion_6h |
| Elevación solar | `solar_elevation_deg` | modelizacion_6h |
| Irradiancia | `GPOA_S1`, `GPOA_S2` | integrado_6h |
| Temp aire | `Tair_WS`, `Tair_S1_center` | modelizacion_6h |
| Trackers anómalos | varianza desde `tracker_variance_diagnostic.csv` | diagnostic |

### Tracker anomaly detection (datos reales)
Basado en `tracker_variance_diagnostic.csv` — columna `varianza_deg2`:
- Cluster normal (~366 deg²): M01, M03, M04, M08, M09
- Cluster alta varianza (~509–535 deg²): M02, M05, M06, M07, M10
- Umbral de anomalía: trackers con varianza > 450 deg² → marcados en rojo
- Ningún tracker tiene `posible_stow_fijo = True` en los datos actuales

### IEC — valores reales
- Media: 0.397 | Mediana: 0.360 | Máx: 0.925
- Por régimen: HORIZONTAL (0.20) < TRACKING_AM (0.44) < TRACKING_PM (0.74)
- La gauge IEC mostrará el valor real del último registro (no 0.71)

---

## Fuera de alcance (E05)

- Datos en tiempo real / streaming
- Autenticación de usuarios
- Persistencia de alertas en base de datos
- Predicción futura del ángulo (eso es Sprint 4)
- Multi-idioma

---

## Definition of Done (E05)

- [ ] `streamlit run sprint3/app.py` ejecuta sin errores
- [ ] Los 5 tabs cargan sin excepción con los CSVs del Sprint 2
- [ ] La visualización del panel solar responde al slider de hora
- [ ] Los trackers M02/M06/M10 aparecen en rojo en Tab 1 y Tab 5
- [ ] La regla activa se resalta correctamente en Tab 4 según último registro
- [ ] CSS Apple aplicado y visible en todos los tabs
- [ ] Revisado por al menos una persona del equipo
