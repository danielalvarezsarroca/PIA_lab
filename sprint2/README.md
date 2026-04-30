# Sprint 2 — Modelización y política de rotación

**Proyecto:** Análisis y Optimización Operativa de Sistemas Agrovoltaicos Dinámicos  
**Organización:** Sostenibilidad y Ciencia  
**Equipo:** Chacorocalfarobar — PM: Daniel Álvarez Sarroca  
**Fecha:** Abril 2026

---

## Objetivo del sprint

Desarrollar el modelo o conjunto de reglas que defina la **política óptima de rotación** de las placas solares para maximizar simultáneamente la generación eléctrica y la calidad del cultivo, traduciendo los resultados a reglas operativas interpretables.

---

## Entregables técnicos

| Código | Descripción | Archivo |
|--------|-------------|---------|
| E03 | Informe de modelización y política de rotación | `E03_Informe_Modelizacion_Sprint2.docx.pdf` |
| E04 | Notebook replicable del modelo | `sprint2_modelizacion_agrovoltaica.ipynb` |

---

## Documentación de gestión

| Documento | Archivo |
|-----------|---------|
| **Plan de Gestión del Proyecto (Sprint 2)** — ver secciones detalladas abajo | `Gestion_Proyecto_Sprint2.pdf` |
| Presentación Sprint 2 | `SPRINT2.pptx` |
| Acta de reunión 3 | `Actes Reunions/Acta_de_reunió 3.pdf` |
| Acta de reunión 4 | `Actes Reunions/Acta de reunió 4.pdf` |

### Contenido de `Gestion_Proyecto_Sprint2.pdf`

El documento de gestión es el artefacto central de este sprint e integra todos los elementos requeridos por el paquete documental:

| Sección | Contenido |
|---------|-----------|
| §1 — Equipo y roles | Composición del equipo Chacorocalfarobar y responsabilidades |
| §2 — Sprint Backlog | 28 tareas (S2-01 a S2-28), responsables, story points y estado. Velocidad: 91% (43/47 SP) |
| §3 — Sprint Review del Sprint 1 | Fecha: 17/04/2026. Entregables demostrados (E01, E02), hallazgos presentados al cliente y feedback recibido |
| §4 — Retrospectiva del Sprint 1 | Qué fue bien, qué mejorar y 6 acciones de mejora (A01–A06) incorporadas al Sprint 2 |
| §5–8 — Trabajo técnico Sprint 2 | Descripción del análisis, metodología, feature engineering, resultados y reglas candidatas |
| §9 — Entregables y outputs | Lista completa de artefactos generados con responsable y estado |
| §10 — Limitaciones | 6 limitaciones identificadas con impacto e implicaciones para el Sprint 3 |
| §11 — Registro de riesgos actualizado | 11 riesgos preexistentes actualizados (R1–R11) + 3 nuevos (R12–R14) con planes de mitigación |
| §12 — Seguimiento del presupuesto | Coste acumulado por rol. Presupuesto total: 37.977,50 €. Contingencia consumida S2: 175 € (circularidad GPOA). Remanente: 2.927,50 € |
| §13 — Verificación del DoD | 11 criterios verificados, todos completados |
| §14 — Relación con Sprint 3 | Inputs técnicos del Sprint 2 para el dashboard y decisiones de diseño orientadas desde la modelización |
| §15 — Lecciones aprendidas | 4 lecciones (LL-08 a LL-11): circularidad GPOA, nomenclatura de carpetas, validación agronómica del IEC, planificación de revisiones de calidad |

---

## Outputs del modelo (`outputs_sprint2/`)

### Datos procesados
| Archivo | Descripción |
|---------|-------------|
| `dataset_integrado_6h.csv` | Dataset integrado de todos los sensores a resolución 6h |
| `dataset_integrado_cobertura.csv` | Cobertura temporal por sensor y zona |
| `dataset_modelizacion_6h.csv` | Dataset final usado para entrenamiento del modelo |

### Modelo y evaluación
| Archivo | Descripción |
|---------|-------------|
| `model_metrics.csv` | Métricas de evaluación de los modelos entrenados |
| `model_predictions_vs_actual.png` | Visualización de predicciones vs valores reales |
| `decision_tree_feature_importance.csv` | Importancia de variables según árbol de decisión |
| `decision_tree_interpretability.png` | Visualización del árbol de decisión |
| `decision_tree_rules.txt` | Reglas operativas extraídas del árbol |
| `elasticnet_coefficients.csv` | Coeficientes del modelo ElasticNet |
| `elasticnet_coefficients.png` | Visualización de coeficientes ElasticNet |

### Política de rotación e índice IEC
| Archivo | Descripción |
|---------|-------------|
| `candidate_rotation_rules.csv` | Reglas candidatas de rotación validadas conceptualmente |
| `high_iec_policy_table.csv` | Tabla de política para condiciones de IEC alto |
| `iec_summary.csv` | Resumen del Índice combinado Energía–Cultivo (IEC) |
| `iec_overview.png` | Visión general del IEC por franja horaria y condición |
| `regime_summary_iec.csv` | Resumen de regímenes operativos según IEC |
| `policy_rules_diagnostics.png` | Diagnóstico visual de las reglas de política |

### Diagnóstico de trackers
| Archivo | Descripción |
|---------|-------------|
| `tracker_variance_diagnostic.csv` | Detección de trackers con varianza anómala (posibles fallos) |
| `tracker_variance_diagnostic.png` | Visualización del diagnóstico de trackers |
| `dataset_integrado_cobertura.png` | Mapa de cobertura de datos por sensor |

---

## Resumen técnico

El sprint 2 produjo:

1. **Pipeline de datos reproducible** — integración de 16 CSV heterogéneos a resolución uniforme de 6h, con limpieza de unidades embebidas en string y tratamiento de nulos.

2. **Índice combinado Energía–Cultivo (IEC)** — métrica multiobjetivo que equilibra generación fotovoltaica y condiciones microclimáticas del cultivo (ePAR, VWC, temperatura suelo).

3. **Dos enfoques de modelización comparados:**
   - Árbol de decisión interpretable → extracción directa de reglas operativas
   - ElasticNet → análisis de importancia lineal de variables

4. **6 reglas candidatas de rotación** derivadas del árbol de decisión y el análisis observacional por régimen, ordenadas por IEC esperado decreciente (de 0.862 a 0.093).

5. **Diagnóstico de trackers** — identificación de M02, M06 y M10 con ángulo constante (~50.6°), posible fallo o posición stow fija.

---

## Relación con sprints anteriores y siguientes

- Parte de los hallazgos del **Sprint 1 (EDA):** no linealidad tracking–ePAR, lag ~6–12h irradiancia–temperatura suelo, zonas S1 y S2 como secciones experimentales válidas.
- El índice IEC y las reglas de rotación son la **base del módulo de recomendaciones del Sprint 3 (Dashboard v1)**.
