# Sprint 1 — Índice de entregables y documentación

**Proyecto:** Análisis y Optimización Operativa de Sistemas Agrovoltaicos Dinámicos  
**Organización:** Sostenibilidad y Ciencia  
**Equipo:** Chacorocalfarobar  
**Período:** Semana del 14 al 17 de abril de 2026

---

## Entregables técnicos

| Entregable | Archivo | Descripción |
|---|---|---|
| **E01** — Informe EDA | `E01_Informe_EDA_Sprint1.pdf` | Informe completo del análisis exploratorio de datos: resultados, gráficas, interpretación por secciones y conclusiones accionables para el Sprint 2 |
| **E02** — Notebook EDA | `sprint1_eda_agrovoltaica.ipynb` | Notebook Python reproducible con todo el código del EDA: carga, limpieza, análisis univariante, temporal, correlaciones y análisis de dominio agrovoltaico |

---

## Documentación de gestión

### Presentación del sprint

| Archivo | Descripción |
|---|---|
| `SPRINT1.pptx.pdf` | Presentación de slides del Sprint 1 para la Sprint Review con el cliente. Incluye objetivos, metodología, hallazgos clave y próximos pasos |

---

### Plan de Gestión del Proyecto

| Archivo | Descripción |
|---|---|
| `Gestion_Proyecto_Sprint1.pdf` | Documento principal de gestión del sprint. Contiene el plan de gestión actualizado, la planificación de tareas con asignación por miembro, el seguimiento de story points y la distribución de carga del equipo |

---

### Actas de reuniones y evidencias de reunión

| Archivo | Descripción |
|---|---|
| `actes de reunió/Acta_de_reunió1.pdf` | Acta de la primera reunión del Sprint 1 (Sprint Planning / Kick-off). Recoge el orden del día, decisiones adoptadas y acciones acordadas |
| `actes de reunió/Acta_de_reunió 2.pdf` | Acta de la segunda reunión del Sprint 1. Recoge el seguimiento del sprint, incidencias y acuerdos para el cierre |

---

### Seguimiento de presupuesto

| Archivo | Descripción |
|---|---|
| `Gestion_Proyecto_Sprint1.pdf` | El seguimiento de presupuesto del Sprint 1 (tabla de EV, AC, CPI, SPI por rol) se encuentra incluido dentro de este documento de gestión |

---

### DoD del Proyecto

| Archivo | Descripción |
|---|---|
| `Gestion_Proyecto_Sprint1.pdf` | La verificación del Definition of Done aplicado a los entregables del Sprint 1 se encuentra incluida dentro de este documento de gestión |

---

### Registro de riesgos

| Archivo | Descripción |
|---|---|
| `Registro_Riesgos.xlsx` | Registro de riesgos del proyecto actualizado tras el Sprint 1. Incluye los riesgos preexistentes con su estado actualizado (R1–R6) y los nuevos riesgos identificados durante el EDA (R7–R11) |

---

### Informe de Lecciones Aprendidas

| Archivo | Descripción |
|---|---|
| `Gestion_Proyecto_Sprint1.pdf` | El informe de lecciones aprendidas del Sprint 1 (formato plantilla Apéndice J del Plan de Proyecto) se encuentra incluido dentro de este documento de gestión. Cubre 8 lecciones en las categorías: Calidad/Técnica, Estimación/Planificación, Comunicación, Gestión del equipo y Gestión del cambio |

---

### Daily Standup *(personal y opcional)*

No se han conservado actas formales de daily standup en este sprint. Los impedimentos y el progreso diario se gestionaron de forma informal entre los miembros del equipo.

---

## Outputs del análisis

La carpeta `outputs/` contiene todos los artefactos generados por el notebook EDA:

| Archivo | Descripción |
|---|---|
| `inventario_datasets.csv` | Inventario completo de los 16 ficheros CSV de datos |
| `quality_report.csv` | Métricas de calidad por dataset (nulos, duplicados, frecuencia) |
| `temporal_summary.csv` | Cobertura temporal y huecos por dataset |
| `outliers_summary.csv` | Conteo de outliers IQR×3 por variable |
| `dataset_integrado_6h.csv` | Dataset integrado a resolución 6h (base para Sprint 2) |
| `lag_analysis.csv` | Resultados del análisis de efectos retardados |
| `nulls_by_column.png` | Mapa de nulos por columna y dataset |
| `temporal_coverage.png` | Diagrama de cobertura temporal por dataset |
| `dist_*.png` | Histogramas de distribución por dataset |
| `temporal_energy_vars.png` | Evolución temporal de variables energéticas |
| `temporal_micro_vars.png` | Evolución temporal de variables microclimáticas |
| `intraday_profiles.png` | Perfiles intradiarios medianos (GPOA, tracking, ePAR, T suelo) |
| `correlation_matrix.png` | Matriz de correlaciones de Spearman |
| `correlations_vs_tracking.png` | Correlaciones de todas las variables con el tracker M01 |
| `scatter_key_pairs.png` | Scatter plots de los pares de variables más relevantes |
| `vars_by_tracking_regime.png` | Variables clave segmentadas por régimen de tracking |
| `section_S1_vs_S2.png` | Comparativa entre secciones experimentales S1 y S2 |
| `lag_analysis.png` | Correlación cruzada con desplazamiento temporal |
| `epar_thresholds.png` | Distribución ePAR con umbrales agronómicos |
| `tracker_correlations.png` | Correlaciones y varianza entre trackers M01–M10 |
| `epar_sensor_profile.png` | Perfil de exposición lumínica por sensor ePAR |
| `key_variables_overview.png` | Visión integrada de las 4 variables clave del sistema |

---

## Resumen de estado del sprint

| Documento | Estado |
|---|---|
| E01 — Informe EDA | Completado |
| E02 — Notebook EDA | Completado |
| Presentación Sprint 1 | Completado |
| Plan de Gestión | Completado |
| Actas de reunión (x2) | Completado |
| Registro de riesgos | Completado |
| Lecciones aprendidas | Completado |
| Seguimiento de presupuesto | Completado |
| Daily standup | No aplica (informal) |
| Revisión externa (Sprint Review) | Pendiente |
| Versionado Git | Parcial |
