# Dashboard Sprint 3 — Rediseño Interactivo Tab 1
**Fecha:** 2026-04-30
**Alcance:** E05 — hacer Tab 1 completamente reactivo al slider de hora, tipografía Apple más legible

---

## Motivación

El Tab 1 actual muestra el último registro estático. El Tab 3 tiene el slider de hora pero actualiza solo el SVG — las métricas no responden. La app hace rerun completo en cada interacción, lo que la hace lenta. El usuario quiere una pantalla principal interactiva donde mover el slider de hora actualice instantáneamente el SVG, IEC, ángulo, régimen, ePAR, VWC y recomendaciones.

---

## Cambios de arquitectura

### Tabs: 4 en vez de 5

| Tab | Antes | Después |
|-----|-------|---------|
| Tab 1 | Estado actual (estático) | Dashboard interactivo (slider + todo) |
| Tab 2 | Series temporales | Sin cambios |
| Tab 3 | Panel Solar (slider aislado) | **Eliminado** — absorbido en Tab 1 |
| Tab 4 | Recomendación | Sin cambios (vista detallada) |
| Tab 5→4 | Alertas | Sin cambios |

### `@st.fragment` para reactividad

La función `_render_interactive_section(df_modelo, df_rules)` se decora con `@st.fragment`. Streamlit 1.43 lo soporta: cuando el slider cambia, solo esa función hace rerun — no el resto de la app, no la carga de datos, no el tracker grid.

```
app rerun completo → solo al cargar la página
@st.fragment rerun  → cada vez que se mueve el slider
```

---

## Layout Tab 1

### Sección interactiva — dentro de `@st.fragment`

1. **Slider de hora** — ancho completo, rango 6–21h, paso 1h, label prominente
2. **Dos columnas (60/40):**
   - Izquierda: SVG panel solar generado por `generate_solar_svg()`
   - Derecha: IEC gauge + 4 metric cards (ángulo actual, ángulo recomendado, régimen, elevación solar)
3. **Fila de 4 KPI cards** — ePAR S1, ePAR S2, VWC S1, VWC S2 — todos del registro de esa hora
4. **Tabla de reglas candidatas** — compacta, regla activa con borde verde izquierdo y badge "● ACTIVA"

Todos los valores de la sección interactiva se obtienen de `df_modelo[df_modelo["hour_of_day"] == hour]` usando la fila con mayor IEC para esa hora. Si no hay datos para esa hora, se usan los valores del registro más cercano.

### Sección estática — fuera del fragment

- Grid de 10 trackers (varianza no cambia con la hora)
- Resumen de alertas activas

---

## Lógica de datos por hora

```python
def _get_hour_record(df_modelo, hour):
    rows = df_modelo[df_modelo["hour_of_day"] == hour].dropna(subset=["IEC", "track_mean"])
    if rows.empty:
        # fallback: hora más cercana
        rows = df_modelo.dropna(subset=["IEC", "track_mean"])
        idx = (df_modelo["hour_of_day"] - hour).abs().idxmin()
        return df_modelo.loc[idx]
    return rows.loc[rows["IEC"].idxmax()]  # fila con mayor IEC en esa hora
```

Columnas usadas (todas en `dataset_modelizacion_6h.csv`):
- `track_mean` → ángulo actual
- `IEC` → gauge + regla activa
- `tracking_regime` → régimen
- `ePAR_S1_mean`, `ePAR_S2_mean` → KPI cards
- `VWC_S1_mean`, `VWC_S2_mean` → KPI cards
- `solar_elevation_deg` → elevación solar (real del dataset, no calculada)
- `hour_of_day` → filtro

`get_recommended_angle(hour, df_modelo)` ya existe en `solar_logic.py` — devuelve `track_mean` de la fila con mayor IEC para esa hora.

---

## Tipografía y tamaños

CSS reescrito en `styles.py`:

| Elemento | Antes | Después |
|----------|-------|---------|
| Base app | implícito ~13px | **15px** |
| Label de card | 10px | **13px** |
| Valor de card | 24px | **30px** |
| Subtítulo de card | 10px | **11px** |
| Títulos de sección | 11px | **13px** |
| Slider label | heredado | **15px bold** |
| Valor métrico (panel) | 18px | **22px** |
| Tab labels | 13px | **14px** |

La fuente `font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial` ya está definida — se fuerza con `!important` en más selectores para cubrir widgets internos de Streamlit.

---

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `sprint3/tabs/tab_estado.py` | Reescritura completa — añade `@st.fragment`, lookup por hora, tabla reglas |
| `sprint3/styles.py` | Actualización de tamaños de fuente en `CSS_STYLES` |
| `sprint3/app.py` | 4 tabs, eliminar import/llamada de `tab_panel_solar` |
| `sprint3/tabs/tab_panel_solar.py` | Eliminar (contenido migrado a tab_estado) |

---

## Definition of Done

- [ ] Mover el slider de hora actualiza SVG + IEC + ángulo + régimen + ePAR + VWC + regla activa sin recargar la página completa
- [ ] La tabla de reglas candidatas aparece en Tab 1 con la activa resaltada
- [ ] El texto es notablemente más grande y legible
- [ ] La fuente Apple se aplica visualmente (verificar en DevTools)
- [ ] Los 4 tabs cargan sin error
- [ ] El tracker grid y alertas siguen funcionando (sección estática)
- [ ] `streamlit run app.py` arranca sin errores
