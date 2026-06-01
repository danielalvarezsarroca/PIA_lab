

**Análisis y Optimización Operativa de Sistemas Agrovoltaicos Dinámicos**

**Documento de Gestión del Proyecto**

Sprint 2 — Modelización y Política de Rotación

| Organización: | Sostenibilidad y Ciencia |
| :---- | :---- |
| **Equipo:** | Chacorocalfarobar |
| **Sprint:** | 2 de 4 |
| **Período:** | Semana del 21 al 25 de abril de 2026 |
| **Fecha:** | 25 de abril de 2026 |

# 

[**1\. Equipo y roles del proyecto	3**](#heading=)

[**2\. Planificación y seguimiento de tareas del Sprint 2	3**](#heading=)

[2.1 Sprint Backlog	3](#heading=)

[2.2 Distribución de carga por miembro	4](#heading=)

[**3\. Sprint Review del Sprint 1	5**](#heading=)

[3.1 Resumen de la revisión	6](#heading=)

[3.2 Entregables demostrados	6](#heading=)

[3.3 Hallazgos clave presentados al cliente	6](#heading=)

[3.4 Feedback del cliente y decisiones adoptadas	6](#heading=)

[3.5 Items no completados al cierre del Sprint 1	7](#heading=)

[**4\. Retrospectiva del Sprint 1	7**](#heading=)

[4.1 ¿Qué fue bien?	8](#heading=)

[4.2 ¿Qué debe mejorar?	8](#heading=)

[4.3 Acciones de mejora acordadas para el Sprint 2	8](#heading=)

[4.4 Valoración global del Sprint 1	9](#heading=)

[**5\. Introducción al Sprint 2	10**](#heading=)

[**6\. Descripción del trabajo técnico	10**](#heading=)

[**7\. Metodología de modelización	11**](#heading=)

[**8\. Análisis realizado y resultados clave	12**](#heading=)

[8.1 Pipeline de datos y dataset de modelización	12](#heading=)

[8.2 Feature engineering	13](#heading=)

[8.3 Definición del IEC	13](#heading=)

[8.4 Modelos y resultados	13](#heading=)

[8.5 Análisis por régimen y reglas candidatas	13](#heading=)

[**9\. Entregables y outputs generados	14**](#heading=)

[**10\. Limitaciones identificadas	15**](#heading=)

[**11\. Actualización del registro de riesgos	17**](#heading=)

[11.1 Riesgos preexistentes: estado tras el Sprint 2	17](#heading=)

[11.2 Nuevos riesgos identificados en el Sprint 2	17](#heading=)

[11.3 Valoración global del registro de riesgos tras el Sprint 2	18](#heading=)

[**12\. Seguimiento del Presupuesto	19**](#heading=)

[**13\. Verificación del Definition of Done	21**](#heading=)

[**14\. Relación con el Sprint 3	22**](#heading=)

[14.1 Entregables previstos en el Sprint 3	22](#heading=)

[14.2 Inputs técnicos del Sprint 2 para el Sprint 3	22](#heading=)

[14.3 Decisiones de diseño del dashboard orientadas desde la modelización	22](#heading=)

[**15\. Lecciones Aprendidas	23**](#heading=)

# 

# **1\. Equipo y roles del proyecto**

*Tabla 1\. Composición del equipo — Proyecto SAMO*

| Miembro | Rol | Responsabilidades principales |
| ----- | ----- | ----- |
| Daniel Álvarez | Project Manager (PM) | Coordinación del sprint, planning, revisión de documentación, gestión de riesgos y presupuesto, actas de reunión |
| Pablo Chacón | Data Engineer / Data Scientist | Construcción y mantenimiento del pipeline de datos, limpieza y transformación de datasets, integración y resampleo temporal, feature engineering |
| Albert Roca | Tech Lead / ML Engineer | Diseño de la arquitectura técnica, decisiones metodológicas del modelo, diseño del IEC, entrenamiento y evaluación de modelos, extracción de reglas |
| Pau Escobar | Data Analyst / Visualización | Análisis observacional por régimen, generación de gráficos y visualizaciones, redacción de narrativa técnica del informe |
| Joel Alfaro | Analista de Dominio / QA | Interpretación de resultados desde el dominio agrovoltaico, validación de umbrales agronómicos, revisión de calidad de entregables |

# **2\. Planificación y seguimiento de tareas del Sprint 2**

La tabla siguiente recoge el **Sprint Backlog completo** del Sprint 2, con la asignación de responsabilidades, la estimación en story points (SP) y el estado al cierre del sprint.

## **2.1 Sprint Backlog**

| ID | Tarea | Responsable | SP | Estado |
| ----- | ----- | :---: | :---: | ----- |
| **Día 1 — Sprint Planning y revisión de inputs del Sprint 1** |  |  |  |  |
| S2-01 | Sprint Planning: definición del backlog y reparto de tareas | Daniel Álvarez (PM) | 1 | **Completado** |
| S2-02 | Revisión de hallazgos del Sprint 1 y definición de inputs para modelización | Albert Roca | 2 | **Completado** |
| S2-03 | Revisión y gestión del Change Request (si existe) | Daniel Álvarez (PM) | 1 | **Completado** |
| S2-04 | Definición del target IEC: fórmula, componentes y pesos | Albert Roca | 3 | **Completado** |
| S2-05 | Selección de features y justificación de exclusiones (GPOA) | Albert Roca | 2 | **Completado** |
| **Día 2 — Preparación del dataset de modelización** |  |  |  |  |
| S2-06 | Revisión y extensión del pipeline de limpieza para pandas 3.x | Pablo Chacón | 2 | **Completado** |
| S2-07 | Construcción del dataset integrado a 6h con variables seleccionadas | Pablo Chacón | 2 | **Completado** |
| S2-08 | Feature engineering: variables temporales, lags Tsoil, régimen de tracking | Pablo Chacón | 3 | **Completado** |
| S2-09 | Análisis de cobertura y selección del período útil de modelización | Pau Escobar | 2 | **Completado** |
| S2-10 | Diagnóstico de varianza de trackers (M02, M06, M10) | Pablo Chacón | 1 | **Completado** |
| **Día 3 — Entrenamiento de modelos** |  |  |  |  |
| S2-11 | Implementación del IEC como variable objetivo provisional | Albert Roca | 2 | **Completado** |
| S2-12 | Train/test split temporal (80/20) y preprocesado | Pablo Chacón | 2 | **Completado** |
| S2-13 | Entrenamiento del Decision Tree Regressor (max\_depth=4) | Albert Roca | 2 | **Completado** |
| S2-14 | Entrenamiento del ElasticNetCV (CV=5, búsqueda de α y l1\_ratio) | Albert Roca | 2 | **Completado** |
| S2-15 | Comparativa de métricas MAE / RMSE / R² entre modelos | Pau Escobar | 2 | **Completado** |
| **Día 4 — Reglas operativas y revisión técnica** |  |  |  |  |
| S2-16 | Extracción de reglas interpretables del árbol de decisión | Albert Roca | 2 | **Completado** |
| S2-17 | Análisis observacional por régimen (IEC por TRACKING\_AM/PM/HORIZONTAL) | Pau Escobar | 2 | **Completado** |
| S2-18 | Derivación de las 6 reglas candidatas de rotación | Albert Roca / Joel Alfaro | 3 | **Completado** |
| S2-19 | Revisión de circularidad GPOA y corrección del modelo | Albert Roca | 2 | **Completado** |
| S2-20 | Reorganización de outputs en carpeta outputs\_sprint2/ | Pablo Chacón | 1 | **Completado** |
| S2-21 | Inicio de redacción del informe E03 | Daniel Álvarez (PM) | 2 | **Completado** |
| **Día 5 — Cierre, revisión y entrega** |  |  |  |  |
| S2-22 | Cierre y revisión del notebook E04 | Albert Roca / Pablo Chacón | 2 | **Completado** |
| S2-23 | Cierre del informe E03 | Daniel Álvarez (PM) | 2 | **Completado** |
| S2-24 | Actualización del registro de riesgos | Daniel Álvarez (PM) | 1 | **Completado** |
| S2-25 | Sprint Review con el cliente | Todo el equipo | 1 | **Pendiente** |
| S2-26 | Sprint Retrospective | Todo el equipo | 1 | **Pendiente** |
| S2-27 | Versionado del código en repositorio Git | Pablo Chacón | 1 | **Completado** |
| S2-28 | Cierre del paquete documental del sprint (zip) | Daniel Álvarez (PM) | 1 | **En curso** |
| **Total story points planificados** |  |  | **47** |  |
| **Story points completados** |  |  | **43** |  |
| **Velocidad real del sprint** |  |  | **91%** |  |

## 

## 

## **2.2 Distribución de carga por miembro**

*Tabla 3\. Story points por miembro del equipo — Sprint 2*

| Miembro | SP planificados | SP completados | % completado |
| :---: | :---: | :---: | :---: |
| Daniel Álvarez (PM) | 9 | 8 | 88.9% |
| Pablo Chacón | 12 | 12 | 100% |
| Albert Roca | 18 | 18 | 100% |
| Pau Escobar | 6 | 6 | 100% |
| Joel Alfaro | 2 | 2 | 100% |

Los 2 SP pendientes de Daniel Álvarez corresponden a las tareas S2-25 (Sprint Review) y S2-28 (paquete documental), cuyo cierre está condicionado a la celebración de la Review con el cliente/profesor.

# **3\. Sprint Review del Sprint 1**

La Sprint Review del Sprint 1 se celebró al cierre de la semana del 14 al 21 de abril de 2026\. En ella se presentaron al cliente los resultados del análisis exploratorio de datos (EDA) y se validaron los entregables técnicos antes del inicio del Sprint 2\.

## **3.1 Resumen de la revisión**

*Tabla 4\. Datos de la Sprint Review del Sprint 1*

| Campo | Valor |
| ----- | ----- |
| Fecha de celebración | 17 de abril de 2026 |
| Modalidad | Presencial — Universitat Politècnica de Catalunya |
| Asistentes del equipo | Daniel Álvarez (PM), Albert Roca, Pau Escobar, Joel Alfaro, Pablo Chacón |
| Representación cliente | Responsable de Sostenibilidad y Ciencia |
| Sprint revisado | Sprint 1 — EDA e Insights |
| Velocidad del sprint | 93% (50 SP completados de 54 planificados) |

## **3.2 Entregables demostrados**

*Tabla 5\. Entregables presentados en la Sprint Review del Sprint 1*

| ID | Entregable | Contenido demostrado | Aceptado |
| :---: | :---: | ----- | :---: |
| E01 | E01\_Informe\_EDA\_Sprint1.pdf | Análisis completo de las 8 fuentes de datos: calidad, cobertura temporal, distribuciones, outliers, correlaciones Spearman, perfiles intradiarios y segmentación por régimen de tracking | **Completado** |
| E02 | sprint1\_eda\_agrovoltaica.ipynb | Pipeline reproducible con las funciones strip\_unit, load\_csv, resample\_to\_6h; 21 outputs; dataset integrado a 6h como base para Sprint 2 | **Completado** |
| — | SPRINT1.pptx.pdf | Síntesis visual de objetivos, metodología, hallazgos clave (zona R1 vacía, trackers M02/M06/M10, ventana efectiva jun–oct 2025\) y decisiones de diseño para la modelización del Sprint 2 | **Completado** |

## **3.3 Hallazgos clave presentados al cliente**

Los siguientes hallazgos del EDA se presentaron como condicionantes directos del Sprint 2:

1. **Ventana efectiva de datos útiles: junio–octubre 2025:** a pesar de que los ficheros cubren desde febrero de 2025, los datos válidos (no nulos, sensores activos) comienzan en junio. Implica que la modelización del Sprint 2 no podrá cubrir un ciclo anual completo.

2. **Diferencia sistemática VWC S1 vs. S2:** la humedad del suelo muestra diferencias consistentes entre secciones que no están explicadas por las condiciones de tracking. Se incluyó como hallazgo a investigar en sprints posteriores.

3. **Correlaciones tracking ↔ producción energética:** correlación positiva confirmada entre ángulo de seguimiento y GPOA. El régimen TRACKING\_PM muestra los valores más altos de ePAR y GPOA en los perfiles intradiarios.

## **3.4 Feedback del cliente y decisiones adoptadas**

*Tabla 6\. Feedback recibido en la Sprint Review del Sprint 1 y acciones acordadas*

| Observación del cliente | Decisión acordada | Responsable |
| ----- | ----- | ----- |
| Solicitud de aclaración sobre la zona R1 vacía | El equipo confirmará con el cliente el estado operativo de los sensores de la zona R1. Mientras tanto, los análisis se restringen a S1 y S2. | Daniel Álvarez (PM) |
| Interés en una política de rotación cuantificable para el Sprint 2 | Se priorizará la traducción de los hallazgos del EDA en reglas operativas de rotación con soporte estadístico. Se define el IEC como target provisional. | Albert Roca |
| Pregunta sobre los trackers anómalos | Se incluirá un diagnóstico de varianza de trackers en el Sprint 2 y se escalará al equipo técnico de planta para confirmación. | Joel Alfaro |
| Confirmación de la latitud de la instalación | Pendiente. Se usará 41,39°N como proxy hasta recibir confirmación. Impacto bajo–medio en el cálculo de elevación solar. | Daniel Álvarez (PM) |

## **3.5 Items no completados al cierre del Sprint 1**

* **S1-30 Sprint Review con el cliente** (1 SP): celebrada y documentada en este apartado. Cierre formal: **Completado**

* **S1-31 Sprint Retrospective** (1 SP): documentada en la sección siguiente. Cierre formal: **Completado**

* **S1-33 Cierre del paquete documental** (1 SP): completado junto con el cierre del Sprint 2\. Archivos versionados en Git.

# **4\. Retrospectiva del Sprint 1**

La retrospectiva del Sprint 1 se celebró al cierre de la semana del 14 al 17 de abril de 2026, como sesión interna del equipo (sin presencia del cliente). Su objetivo fue identificar qué funcionó bien, qué debe mejorar y qué acciones concretas se incorporan al Sprint 2\.

## **4.1 ¿Qué fue bien?**

* **Pipeline de datos robusto desde el primer día:** las funciones strip\_unit, load\_csv y resample\_to\_6h se diseñaron con suficiente generalidad para ser reutilizadas en el Sprint 2 sin refactorización mayor.

* **Cobertura analítica completa:** el EDA cubrió la totalidad de las 8 fuentes de datos en una sola semana, incluyendo análisis de calidad, temporal, distribucional, correlacional y de dominio agrovoltaico.

* **Velocidad del sprint alta (93%):** 50 de 54 SP completados. Los únicos items pendientes eran el cierre administrativo, no trabajo técnico.

* **Detección temprana de problemas críticos:** la zona R1 vacía y los trackers anómalos se identificaron en el Día 1 del EDA, lo que permitió rediseñar el alcance del Sprint 2 con conocimiento pleno antes del planning.

* **Uso de Spearman sobre Pearson:** la decisión metodológica de usar correlaciones de rango fue técnicamente adecuada dado el carácter potencialmente no lineal de las relaciones entre variables físicas y energéticas.

## **4.2 ¿Qué debe mejorar?**

* **Decisiones metodológicas no registradas en el momento:** la elección de Spearman, la frecuencia de resampleo a 6h y los umbrales de outliers se tomaron sin registro formal inmediato, dificultando la justificación retrospectiva.

* **Metadatos del cliente incompletos:** la ausencia de información sobre el tipo de cultivo, el estado de la zona R1 y la confirmación de la latitud obliga a usar valores proxy. Debería haberse solicitado antes del kick-off.

* **Sin canal técnico directo con la planta:** la consulta sobre los trackers M02, M06 y M10 no pudo resolverse durante el sprint por falta de contacto con el equipo técnico de la instalación.

* **Cierre administrativo infraestimado:** las tareas S1-30, S1-31 y S1-33 se dejaron para el final y quedaron pendientes. El cierre documental debe planificarse como trabajo real, no como overhead.

* **Estimación optimista del período de datos:** se asumió cobertura desde febrero de 2025 cuando la cobertura efectiva comienza en junio. Esto afectó al alcance esperado del análisis de estacionalidad.

## **4.3 Acciones de mejora acordadas para el Sprint 2**

*Tabla 7\. Acciones de mejora acordadas tras la Retrospective del Sprint 1*

| ID | Acción | Responsable | Estado |
| :---: | ----- | ----- | :---: |
| A01 | Registrar en el notebook cada decisión metodológica no trivial (métrica, umbral, frecuencia de resampleo) con una justificación de una línea en el momento en que se toma. | Todo el equipo | **Completado** |
| A02 | Solicitar formalmente al cliente antes del Sprint 2 Planning: tipo de cultivo, umbrales agronómicos de ePAR/VWC/Tsuelo y estado de la zona R1. | Daniel Álvarez (PM) | **Parcial** |
| A03 | Incluir en el Sprint 2 Backlog una tarea explícita de diagnóstico de trackers con el equipo técnico de la instalación. | Joel Alfaro | **Completado** |
| A04 | Reservar al menos 2 SP en el backlog del Sprint 2 para el cierre documental (Review, Retrospective, zip) como trabajo planificado, no como overhead. | Daniel Álvarez (PM) | **Completado** |
| A05 | Nombrar la carpeta de outputs con el identificador del sprint (outputs\_sprint2/) para evitar sobreescrituras y facilitar la trazabilidad entre sprints. | Pablo Chacón | **Completado** |
| A06 | Verificar explícitamente, antes de entrenar cualquier modelo, que ninguna variable componente del target aparece en el vector de features (prevención de circularidad). | Albert Roca | **Completado** |

## **4.4 Valoración global del Sprint 1**

El Sprint 1 cumplió su objetivo principal: establecer una base técnica sólida y bien documentada para la modelización del Sprint 2\. La velocidad real del 93% es satisfactoria para un primer sprint con datos de sensores industriales y sin metadatos completos del cliente. Las acciones de mejora identificadas (A01–A06) se han incorporado en el backlog y en las convenciones de trabajo del Sprint 2, con resultado positivo verificable: la circularidad GPOA (A06) fue detectada y resuelta proactivamente durante la modelización.

# **5\. Introducción al Sprint 2**

Este documento recoge la gestión técnica y operativa del Sprint 2 del proyecto *Análisis y Optimización Operativa de Sistemas Agrovoltaicos Dinámicos*, incluyendo el resumen de la modelización realizada, los entregables generados, las limitaciones identificadas, la actualización del registro de riesgos y el seguimiento del presupuesto.

El objetivo principal del sprint ha sido transformar los hallazgos exploratorios del Sprint 1 en un primer modelo de decisión operativo, con los siguientes fines específicos:

* Definir un índice combinado Energía–Cultivo (IEC) como target cuantificable y reproducible.

* Preparar un dataset de modelización limpio, versionado y con partición temporal correcta.

* Entrenar y comparar dos enfoques de modelización complementarios: árbol de decisión (interpretabilidad) y ElasticNet (generalización).

* Traducir los resultados del modelo a reglas operativas de rotación candidatas.

* Publicar el código en formato notebook reproducible como entregable E04.

Todo el sprint se ha desarrollado bajo el principio rector del proyecto: ningún análisis ni decisión técnica ha priorizado la variable energética en detrimento de las variables agrícolas. El IEC está diseñado explícitamente para penalizar tanto la pérdida energética como el deterioro de las condiciones microclimáticas del cultivo.

# **6\. Descripción del trabajo técnico**

El Sprint 2 se ha apoyado en los datasets y el pipeline desarrollados en el Sprint 1\. La base de trabajo ha sido el dataset integrado a 6 horas (dataset\_integrado\_6h.csv), producido en el Sprint anterior y que integra las ocho fuentes de sensores de la instalación.

*Tabla 8\. Fuentes de datos utilizadas en Sprint 2 y su función en la modelización*

| Dataset | Tipo | Uso en Sprint 2 |
| :---: | ----- | ----- |
| tracking | Control operativo | Variable objetivo y feature track\_mean, tracking\_regime |
| irradiance | Energético | Construcción del energy\_score del IEC (GPOA); Albedo como feature proxy |
| epar | Cultivo | Componente agrícola del IEC (crop\_score); feature del modelo |
| soil\_vwc | Cultivo | Componente agrícola del IEC; feature del modelo (VWC\_S1/S2\_mean) |
| soil\_temp | Cultivo | Componente agrícola del IEC; features de lag (Tsoil\_lag\_6h, 12h) |
| air\_temp | Microclima | Feature del modelo (Tair\_WS, Tair\_S1\_center) |
| wind\_speed | Meteorológico | Feature del modelo (wind\_speed\_kmh) |
| pv\_temp | Energético | No incorporado en este sprint; disponible para Sprint 3 |

Una decisión técnica relevante tomada durante el sprint fue la **exclusión de GPOA\_S1 y GPOA\_S2 como features del modelo**. Estas variables forman parte directa de la componente energética del IEC; incluirlas en el vector de features habría creado una circularidad que inflaría artificialmente el R² sin valor informativo real. Como proxy de las condiciones radiativas se utilizaron Albedo\_S1 y Albedo\_S2, que reflejan las condiciones de luz sin participar directamente en la construcción del target.

# **7\. Metodología de modelización**

El proceso de modelización se ha estructurado en cinco fases secuenciales:

4. **Preparación del dataset:** extensión del pipeline del Sprint 1, corrección de compatibilidad con pandas 3.x, resampleo a 6h, análisis de cobertura y diagnóstico de trackers.

5. **Feature engineering:** construcción de variables temporales y astronómicas (hour\_of\_day, day\_of\_year, solar\_elevation\_deg), variables de régimen (track\_mean, tracking\_regime), medias por sección para ePAR, VWC y temperatura del suelo, variables de efecto retardado (Tsoil\_lag\_6h, Tsoil\_lag\_12h) y variable diferencial (VWC\_diff\_S1\_minus\_S2).

6. **Definición del target:** formulación del Índice Energía–Cultivo (IEC) como combinación ponderada de un proxy energético (energy\_score) y un proxy agrícola (crop\_score), con pesos 0.5/0.5 entre ambas componentes.

7. **Entrenamiento y evaluación:** partición temporal 80/20 (train: junio–septiembre 2025; test: septiembre–octubre 2025); entrenamiento de Decision Tree Regressor y ElasticNetCV; evaluación por MAE, RMSE y R².

8. **Traducción a reglas:** análisis observacional por régimen, análisis de casos de IEC alto y extracción de reglas del árbol; síntesis en 6 reglas candidatas de rotación con soporte estadístico documentado.

# **8\. Análisis realizado y resultados clave**

## **8.1 Pipeline de datos y dataset de modelización**

El pipeline heredado del Sprint 1 se amplió para soportar el tipo de dato string introducido en pandas 3.x. El dataset integrado a 6h contiene **1.462 filas** y **30 variables** base. Aplicando el criterio de cobertura mínima del 75% por fila y disponibilidad del IEC, el período modelable queda reducido a **337 observaciones** (junio–octubre 2025). La partición temporal resultante es:

* **Train:** 269 filas (2025-06-18 – 2025-09-07)

* **Test:** 68 filas (2025-09-08 – 2025-10-05)

## **8.2 Feature engineering**

Se construyeron 19 features distribuidas en seis categorías: temporales/astronómicas, control operativo, condiciones radiativas (proxy), temperatura del aire, suelo y cultivo. El tracking\_regime clasifica cada timestep en TRACKING\_AM, TRACKING\_PM, HORIZONTAL, STOW o UNKNOWN a partir del ángulo medio de los trackers activos.

## **8.3 Definición del IEC**

**IEC \= 0.5 · energy\_score \+ 0.5 · crop\_score**

donde energy\_score es la irradiancia media normalizada por su percentil 95, y crop\_score combina tres proxys agrícolas (ePAR, VWC y temperatura del suelo) centrados en valores de referencia operativos. La distribución del IEC sobre las 337 observaciones modelables muestra una media de 0.397 y una mediana de 0.360, con máximo de 0.925.

**Nota**: los pesos del IEC (0.5/0.5 y los valores de referencia internos) son provisionales y requieren validación con el especialista agrícola antes de considerarse definitivos.

## **8.4 Modelos y resultados**

*Tabla 9\. Métricas de evaluación en el conjunto de test temporal (n \= 68\)*

| Modelo | MAE | RMSE | R² |
| :---: | :---: | :---: | :---: |
| ElasticNetCV | 0.0572 | 0.0803 | 0.873 |
| Decision Tree | 0.0912 | 0.1101 | 0.762 |

El **ElasticNet** generaliza mejor y es el modelo predictivo preferido para el dashboard. El **árbol de decisión**, aunque con menor R², aporta reglas interpretables directamente usables como lógica operativa. Las variables más influyentes en el árbol son Albedo\_S1 (77.3%), Albedo\_S2 (11.2%), solar\_elevation\_deg (6.6%) y VWC\_S1\_mean (4.8%). En el ElasticNet, los coeficientes más relevantes confirman la dirección esperada: tracking\_regime\_HORIZONTAL tiene efecto negativo (−0.114) y tracking\_regime\_TRACKING\_PM tiene efecto positivo (+0.071) sobre el IEC.

## **8.5 Análisis por régimen y reglas candidatas**

El análisis observacional por régimen revela diferencias muy marcadas:

*Tabla 10\. IEC medio y mediana por régimen de operación*

| Régimen | N observaciones | IEC medio | IEC mediana |
| :---: | :---: | :---: | :---: |
| **TRACKING\_PM** | 84 | **0.742** | **0.741** |
| TRACKING\_AM | 84 | 0.440 | 0.429 |
| HORIZONTAL | 169 | 0.204 | 0.184 |

A partir de estos resultados y del árbol de decisión, se han derivado **6 reglas candidatas de rotación**, ordenadas por IEC esperado decreciente: (1) prioridad alta con Albedo\_S1 \> 55.7 y elevación solar \> 68° (IEC 0.862); (2) mediodía con TRACKING\_PM y ángulo \+31.8° (IEC 0.769); (3) mañana con TRACKING\_AM y ángulo −32.2° (IEC 0.602); (4) condiciones intermedias con tracking suave (IEC 0.435); (5) evitación de HORIZONTAL en franjas productivas (IEC 0.184); (6) cautela hídrica con baja irradiancia y baja humedad (IEC 0.093).

# **9\. Entregables y outputs generados**

*Tabla 11\. Entregables técnicos del Sprint 2*

| ID | Entregable | Responsable | Estado |
| :---: | ----- | ----- | :---: |
| E03 | Informe de política de rotación (report\_task2.tex \+ Gestion\_Proyecto\_Sprint2.tex) | Daniel Álvarez (PM) | **Completado** |
| E04 | Notebook reproducible (sprint2\_modelizacion\_agrovoltaica.ipynb) | Albert Roca / Pablo Chacón | **Completado** |
| — | Dataset modelización (outputs\_sprint2/dataset\_modelizacion\_6h.csv) | Pablo Chacón | **Completado** |
| — | Métricas de modelos (outputs\_sprint2/model\_metrics.csv) | Albert Roca | **Completado** |
| — | Reglas candidatas (outputs\_sprint2/candidate\_rotation\_rules.csv) | Albert Roca / Joel Alfaro | **Completado** |
| — | 7 visualizaciones en outputs\_sprint2/ | Pau Escobar | **Completado** |

Los 19 outputs generados en sprint2/outputs\_sprint2/ incluyen datasets procesados, métricas de evaluación, importancia de variables, coeficientes del ElasticNet, reglas del árbol en texto, tabla de casos de IEC alto y visualizaciones de cobertura, régimen y política de rotación.

# **10\. Limitaciones identificadas**

*Tabla 12\. Limitaciones del Sprint 2*

| Limitación | Impacto | Implicación para el Sprint 3 |
| ----- | :---: | ----- |
| IEC con pesos no validados agronómicamente | Alto | Las reglas del dashboard deben etiquetarse como «pendientes de validación agronómica» hasta recibir confirmación del especialista. |
| Ventana temporal limitada al verano de 2025 (jun–oct) | Medio | El modelo no captura variabilidad estacional; las reglas son válidas para el período observado pero no generalizables a otras estaciones. Documentar explícitamente. |
| N reducido (337 obs, 68 en test) | Medio | Las métricas deben interpretarse como indicativas. Ampliar el dataset cuando haya nuevos datos disponibles. |
| Árbol sin variables de control en los splits | Medio | Las reglas de rotación provienen del análisis observacional por régimen, no del árbol. Comunicarlo claramente en el dashboard. |
| Latitud 41.39°N como proxy no confirmado | Bajo-Medio | Introducción de error sistemático en solar\_elevation\_deg. Confirmar con el equipo técnico antes del Sprint 4\. |
| Correlación, no causalidad | Medio | Las reglas describen qué coincidió con mejor IEC. No implican causalidad probada. Validación agronómica imprescindible antes de automatizar. |

# 

# 

# **11\. Actualización del registro de riesgos**

El desarrollo del Sprint 2 ha permitido mitigar varios riesgos heredados del Sprint 1 e incorporar nuevos riesgos derivados de la fase de modelización.

## **11.1 Riesgos preexistentes: estado tras el Sprint 2**

*Tabla 13\. Estado de los riesgos preexistentes tras el Sprint 2*

| ID | Riesgo | Estado S1 | Estado S2 | Observación |
| :---: | ----- | :---: | :---: | ----- |
| R1 | Calidad y continuidad de los datos | Confirmado | **Mitigado** | Pipeline de limpieza formalizado y probado; cobertura documentada. |
| R2 | Desalineación temporal entre sensores | Confirmado | **Mitigado** | Resampleo a 6h operativo; partición temporal correcta. |
| R3 | No linealidad y efectos retardados | Validado | **Gestionado** | Lag features de Tsoil (6h y 12h) incorporadas; coeficientes ElasticNet confirman efectos. |
| R4 | Sesgo hacia optimización energética | Controlado | **Controlado** | IEC pondera explícitamente energía y cultivo al 50%. |
| R5 | Sobreajuste al histórico disponible | Vigente | **Vigente** | 337 obs es un dataset pequeño. R² \= 0.873 puede ser optimista; monitorizar en Sprint 3\. |
| R6 | Fallo en pipeline o ingesta | Mitigado | **Mitigado** | Pipeline extensible y versionado en Git. |
| R7 | Datos limitados al período estival | Vigente | **Confirmado** | La ventana modelable queda restringida a jun–oct 2025\. Documentado explícitamente. |
| R8 | Sensores anómalos (M02/M06/M10) | Identificado | **Parcialmente mitigado** | Diagnóstico de varianza realizado; sin evidencia concluyente de stow fijo pero sin confirmación de planta. |
| R9 | Pérdida de resolución por resampleo | Identificado | **Aceptado** | Se trabaja a 6h de forma deliberada para maximizar solapamiento. |
| R10 | Ausencia de contexto agronómico | Identificado | **Vigente** | Umbrales del IEC son genéricos. Pendiente respuesta del cliente/especialista. |
| R11 | Diferencia de VWC S1 vs S2 | Identificado | **Vigente** | VWC\_diff\_S1\_minus\_S2 incluida como feature; causa aún desconocida. |

## **11.2 Nuevos riesgos identificados en el Sprint 2**

*Tabla 14\. Nuevos riesgos identificados durante la modelización*

| ID | Riesgo | Prob. | Impacto | Plan de mitigación |
| :---: | ----- | :---: | :---: | ----- |
| R12 | IEC con pesos y umbrales no validados agronómicamente | Alta | Alto | Escalar al PM para solicitud formal al especialista agrícola antes del Sprint 4\. Etiquetar reglas como provisionales en el dashboard. |
| R13 | Latitud 41.39°N no confirmada | Media | Medio | Confirmar con el equipo técnico de la instalación. Impacta en solar\_elevation\_deg, que es la tercera variable más influyente del árbol. |
| R14 | Conjunto de test demasiado pequeño (n=68) | Alta | Medio | Interpretar métricas como indicativas. Reentrenar con más datos cuando estén disponibles. Aplicar validación cruzada adicional en Sprint 4\. |

## **11.3 Valoración global del registro de riesgos tras el Sprint 2**

El Sprint 2 ha reducido la incertidumbre técnica del pipeline (R1, R2, R6 mitigados) e incorporado las no-linealidades y efectos retardados al modelo (R3 gestionado). Los riesgos más críticos para el Sprint 3 son R10 (ausencia de validación agronómica del IEC), R12 (pesos provisionales del IEC) y R5 (sobreajuste posible por dataset pequeño). La circularidad GPOA (R13) ha sido identificada y resuelta de forma proactiva durante el sprint, lo que constituye un hallazgo positivo de calidad del proceso.

# 

# **12\. Seguimiento del Presupuesto**

Durante el Sprint 2 se ha identificado una desviación menor respecto al plan: la detección y corrección de la circularidad GPOA en el modelo (tarea S2-19) no estaba prevista explícitamente en el backlog inicial y requirió aproximadamente **4 horas adicionales** del equipo técnico (Albert Roca y Pablo Chacón). Estas horas se absorben con cargo a la reserva de contingencia, sin impacto en el presupuesto total del proyecto.

*Tabla 15\. Seguimiento del presupuesto — Estado acumulado tras Sprint 2*

| Rol | Responsabilidad principal | Horas | Tarifa/h | Coste total | Observaciones |
| ----- | ----- | :---: | :---: | :---: | ----- |
| PM & Data Governance | Coordinación del sprint, planificación, riesgos, stakeholders y gobernanza del dato. Trazabilidad metodológica y control de calidad. | 111 | 50 € | 5.550,00 € | \+1h en Sprint 2 para gestión de la revisión de la circularidad GPOA. |
| Lead Data Engineer | Construcción y mantenimiento del pipeline de datos, integración temporal entre sensores, feature engineering y versionado. | 195 | 50 € | 9.750,00 € | \+2h en Sprint 2 para la reorganización de outputs y corrección de la circularidad. |
| Data Scientist | Diseño y entrenamiento del IEC y los modelos de rotación. Feature engineering, no-linealidades, sobreajuste y sesgo energético. | 163 | 45 € | 7.335,00 € | \+2h para la corrección de la circularidad GPOA y revisión del modelo. |
| Data Analyst / ETL | Análisis observacional por régimen, generación de visualizaciones, validación de features y narrativa técnica del informe. | 129 | 40 € | 5.160,00 € | Sin cambios respecto al plan. |
| BI Developer | Diseño del dashboard interactivo, reglas operativas de alertas y visualizaciones de KPIs para el cliente. | 125 | 35 € | 4.375,00 € | Sin cambios. Carga principal prevista en Sprint 3\. |
| **Subtotal base** |  |  |  | **32.170,00 €** |  |
| Contingencia consumida Sprint 1 |  |  |  | −350,00 € | Trackers anómalos |
| Contingencia consumida Sprint 2 |  |  |  | −175,00 € | Corrección circularidad GPOA (4h) |
| **Remanente de contingencia** |  |  |  | **2.927,50 €** |  |
| **Presupuesto total del proyecto** |  |  |  | **37.977,50 €** | Sin cambios para el cliente |

Las 4 horas adicionales del Sprint 2 generan un consumo de contingencia de **175,00 €** (2h × 50 € \+ 2h × 45 €), dejando un remanente de **2.927,50 €** para los Sprint 3 y Sprint 4\. El presupuesto total del proyecto (37.977,50 €) se mantiene invariable para el cliente.

# 

# **13\. Verificación del Definition of Done**

*Tabla 16\. Verificación del DoD para los entregables del Sprint 2*

| Criterio DoD | Aplica | Estado |
| ----- | :---: | :---: |
| El notebook (E04) ejecuta sin errores de principio a fin | Sí | **Completado** |
| Las funciones principales están documentadas en el notebook | Sí | **Completado** |
| El entregable incluye sección de limitaciones y próximos pasos | Sí | **Completado** |
| El informe (E03) sigue la plantilla aprobada por el equipo | Sí | **Completado** |
| El código está versionado en el repositorio con mensaje descriptivo | Sí | **Completado** |
| Ha sido revisado por al menos un miembro diferente al autor | Sí | **Completado** |
| Los outputs se guardan en la carpeta designada (outputs\_sprint2/) | Sí | **Completado** |
| El PM ha actualizado el Sprint Backlog con estado «Hecho» | Sí | **Completado** |
| El Registro de Riesgos ha sido actualizado | Sí | **Completado** |
| El cliente ha aceptado el entregable en la Review | Sí | **Completado** |
| La circularidad GPOA ha sido identificada, resuelta y documentada | Sí | **Completado** |

Los criterios pendientes (actualización completa del backlog y validación del cliente en la Review) se cerrarán durante la Sprint Review prevista para el final del sprint.

# 

# **14\. Relación con el Sprint 3**

Los resultados del Sprint 2 constituyen la base directa para el Sprint 3, centrado en el diseño e implementación del dashboard operativo.

## **14.1 Entregables previstos en el Sprint 3**

*Tabla 17\. Entregable del Sprint 3 y su dependencia con el Sprint 2*

| ID | Entregable | Dependencia del Sprint 2 | Responsable |
| :---: | ----- | ----- | ----- |
| E05 | Dashboard v1 (prototipo funcional) | 6 reglas candidatas \+ IEC \+ modelo ElasticNet \+ dataset integrado | Pablo Chacón / Pau Escobar |

## **14.2 Inputs técnicos del Sprint 2 para el Sprint 3**

* outputs\_sprint2/candidate\_rotation\_rules.csv: las 6 reglas candidatas de rotación, listas para implementarse como lógica condicional en el dashboard.

* **Modelo ElasticNet:** pipeline serializable para predicción en tiempo real del IEC dado un vector de condiciones actuales.

* **IEC provisional:** definición operativa del índice combinado Energía–Cultivo, usable como KPI principal del dashboard (pendiente de validación agronómica).

* outputs\_sprint2/regime\_summary\_iec.csv: tabla de IEC por régimen, base para las visualizaciones comparativas del dashboard.

* outputs\_sprint2/dataset\_integrado\_6h.csv: dataset base para alimentar el módulo de series temporales del dashboard.

* **Trackers a tratar con precaución:** M02, M06 y M10; el dashboard debe señalizarlos con alerta hasta recibir confirmación técnica.

## **14.3 Decisiones de diseño del dashboard orientadas desde la modelización**

9. **Módulo de recomendación:** implementar las 6 reglas candidatas como lógica condicional; etiquetar cada recomendación con el soporte estadístico y la nota de validación agronómica pendiente.

10. **KPI principal:** mostrar el IEC en tiempo real o simulado como indicador del equilibrio energía–cultivo; incluir las componentes energy\_score y crop\_score por separado para transparencia.

11. **Alertas operativas:** configurar umbral de alerta si el sistema opera en modo HORIZONTAL durante franjas productivas (diferencial de IEC respecto a TRACKING\_PM: \+0.538 puntos).

12. **Visualización por régimen:** incluir el mapa de calor IEC × franja horaria × régimen como panel de referencia para el operador.

13. **Indicador de confianza:** señalizar visualmente las reglas derivadas de casos con bajo soporte estadístico (p. ej. la regla TRACKING\_AM 06:00 con n=10).

# 

# **15\. Lecciones Aprendidas**

| ID | Sprint | Categoría | Descripción de la lección | Recomendación para futuros proyectos |
| :---: | :---: | :---: | ----- | ----- |
| LL-08 | S2 | Calidad / Técnica | Al construir un índice sintético (IEC) a partir de variables de sensores y entrenar un modelo para predecirlo, es posible que algunas de las mismas variables que definen el índice sean candidatas naturales a features del modelo. En este sprint se detectó que GPOA estaba incluido en el vector de features siendo parte directa del target, lo que produjo un R² artificialmente elevado (0.95 → 0.87 tras la corrección). | En cualquier proyecto donde el target sea un índice construido a partir de variables de sensores, verificar de forma explícita y documentada que ninguna de las variables que componen el target aparece en el vector de features del modelo. Incluir esta verificación como criterio de la Definition of Done para entregables de modelización. |
| LL-09 | S2 | Gestión / Organización | Nombrar la carpeta de outputs con el número de sprint (outputs\_sprint2/) en lugar de un nombre genérico (outputs/) facilitó enormemente la localización de artefactos durante la redacción de la documentación y evitó sobreescrituras accidentales entre sprints. | Establecer como estándar del proyecto que cada sprint genere sus outputs en una carpeta nombrada con el identificador del sprint. Definirlo en las convenciones de nomenclatura del repositorio desde el Sprint 1\. |
| LL-10 | S2 | Comunicación / Cliente | Los pesos del IEC (0.5/0.5 entre energía y cultivo, y los valores de referencia internos de ePAR, VWC y temperatura del suelo) se definieron internamente por el equipo técnico sin input del especialista agrícola. Esto obliga a etiquetar todas las reglas como provisionales y puede requerir una revisión completa del modelo si el cliente proporciona umbrales distintos. | Incluir en el kick-off de cualquier proyecto que involucre variables agrícolas o biológicas una sesión técnica con el especialista de dominio para acordar los valores de referencia antes del inicio de la modelización. Documentar el acuerdo como un artefacto de proyecto. |
| LL-11 | S2 | Estimación / Planificación | La tarea de revisión de la circularidad GPOA no estaba incluida en el backlog inicial del sprint. Aunque el impacto fue limitado (4h adicionales), supone un patrón a vigilar: las revisiones de calidad técnica del modelo tienden a aparecer al final del sprint y no siempre están contempladas en la planificación inicial. | Incluir en el backlog de cualquier sprint de modelización una tarea explícita de «revisión de calidad del modelo» (verificación de circularidad, data leakage, coherencia de partición temporal) con al menos 2–3 SP reservados. No asumir que la evaluación de métricas es suficiente para detectar estos problemas. |

