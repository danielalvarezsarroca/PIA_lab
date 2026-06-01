

**Análisis y Optimización Operativa**

**de Sistemas Agrovoltaicos Dinámicos**

**Documento de Gestión del Proyecto**

Sprint 1 — EDA e insights

| Organización: | Sostenibilidad y Ciencia |
| :---- | :---- |
| **Equipo:** | Chacorocalfarobar |
| **Sprint:** | 1 de 4 |
| **Período:** | Semana del 14 al 17 de abril de 2026 |
| **Fecha:** | 17 de abril de 2026 |

# **ÍNDICE**

[ÍNDICE	1](#heading=)

[1\. Equipo y roles del proyecto	2](#heading=)

[2\. Planificación y seguimiento de tareas del Sprint 1	3](#heading=)

[2.1 Sprint Backlog	3](#heading=)

[2.2 Distribución de carga por miembro	4](#heading=)

[3\. Introducción al Sprint 1	6](#heading=)

[4\. Descripción de los datos	7](#heading=)

[5\. Metodología del EDA	8](#heading=)

[6\. Análisis realizado y resultados clave	9](#heading=)

[6.1 Inventario y calidad de datos	9](#heading=)

[6.2 Análisis temporal	9](#heading=)

[6.3 Estadísticos descriptivos y outliers	9](#heading=)

[6.4 Correlaciones y análisis de dominio	9](#heading=)

[7\. Entregables y outputs generados	11](#heading=)

[8\. Limitaciones identificadas	12](#heading=)

[9\. Actualización del registro de riesgos	13](#heading=)

[9.1 Riesgos preexistentes: estado tras el Sprint 1	13](#heading=)

[9.2 Nuevos riesgos identificados en el Sprint 1	13](#heading=)

[9.3 Problemas con la información de los datasets	14](#9.3-problemas-con-la-información-de-los-datasets)

[**10\. Seguimiento del Presupuesto	14**](#10.-seguimiento-del-presupuesto)

[11\. Verificación del Definition of Done	17](#heading=)

[12\. Relación con el Sprint 2	18](#heading=)

[12.1 Entregables previstos en Sprint 2	18](#heading=)

[12.2 Inputs técnicos del Sprint 1 para el Sprint 2	18](#heading=)

[12.3 Decisiones de modelización orientadas desde el EDA	18](#heading=)

[**13\. Lecciones Aprendidas	19**](#13.-lecciones-aprendidas)

# 

# 

# 

# 

# 

# 

# 

# 

# **1\. Equipo y roles del proyecto**

*Tabla 1\. Composición del equipo — Proyecto SAMO*

| Miembro | Rol | Responsabilidades principales |
| ----- | ----- | ----- |
| Daniel Álvarez | Project Manager (PM) | Coordinación del sprint, planning, revisión de documentación, gestión de riesgos y presupuesto, actas de reunión |
| Pablo Chacón | Data Engineer / Data Scientist | Construcción del pipeline de datos, limpieza y transformación de datasets, integración y resampleo temporal, feature engineering |
| Albert Roca | Tech Lead / ML Engineer | Diseño de la arquitectura técnica, decisiones metodológicas del EDA, análisis de correlaciones y modelización futura |
| Pau Escobar | Data Analyst / Visualización | Análisis univariante y temporal, generación de gráficos y visualizaciones, redacción de narrativa técnica del informe |
| Joel Alfaro | Analista de Dominio / QA | Interpretación de resultados desde el dominio agrovoltaico, validación de umbrales agronómicos, revisión de calidad de entregables |

# 

# 

# 

# 

# 

# 

# 

# 

# 

# 

# 

# 

# **2\. Planificación y seguimiento de tareas del Sprint 1**

La tabla siguiente recoge el **Sprint Backlog completo** del Sprint 1, con la asignación de responsabilidades, la estimación en story points (SP) y el estado al cierre del sprint.

## **2.1 Sprint Backlog**

| ID | Tarea | Responsable | SP | Estado |
| ----- | ----- | :---: | :---: | ----- |
| **Día 1 — Sprint Planning y carga inicial** |  |  |  |  |
| S1-01 | Sprint Planning: definición del backlog y reparto de tareas | Daniel Álvarez (PM) | 1 | **Completado** |
| S1-02 | Carga e inspección inicial de todos los datasets CSV | Pablo Chacón | 2 | **Completado** |
| S1-03 | Identificación de particularidades técnicas de los ficheros (sep=, unidades en strings) | Pablo Chacón | 1 | **Completado** |
| S1-04 | Implementación de funciones auxiliares de carga y limpieza | Pablo Chacón | 2 | **Completado** |
| S1-05 | Creación de la estructura del notebook EDA (E02) | Albert Roca | 1 | **Completado** |
| S1-06 | Revisión de tipos, formatos y consistencia general | Pau Escobar | 1 | **Completado** |
| **Día 2 — Calidad de datos y distribuciones** |  |  |  |  |
| S1-07 | Auditoría de calidad: nulos, duplicados, columnas constantes | Pau Escobar | 2 | **Completado** |
| S1-08 | Análisis de distribuciones y estadísticos descriptivos | Pau Escobar | 2 | **Completado** |
| S1-09 | Detección de outliers por método IQR×3 | Albert Roca | 2 | **Completado** |
| S1-10 | Generación de tabla resumen de calidad por dataset | Pablo Chacón | 1 | **Completado** |
| S1-11 | Identificación y documentación de anomalías en los datos | Joel Alfaro | 2 | **Completado** |
| **Día 3 — Análisis temporal** |  |  |  |  |
| S1-12 | Normalización temporal: conversión a datetime, detección de gaps | Pablo Chacón | 2 | **Completado** |
| S1-13 | Análisis de frecuencias de muestreo por dataset | Pablo Chacón | 1 | **Completado** |
| S1-14 | Generación del diagrama de cobertura temporal | Pau Escobar | 1 | **Completado** |
| S1-15 | Análisis de evolución temporal de variables energéticas | Pau Escobar | 2 | **Completado** |
| S1-16 | Análisis de evolución temporal de variables microclimáticas | Pau Escobar | 2 | **Completado** |
| S1-17 | Cálculo de perfiles intradiarios (mediana por hora) | Albert Roca | 2 | **Completado** |
| **Día 4 — Correlaciones y análisis de dominio** |  |  |  |  |
| S1-18 | Construcción del dataset integrado a resolución 6h | Pablo Chacón | 3 | **Completado** |
| S1-19 | Cálculo de la matriz de correlaciones de Spearman | Albert Roca | 2 | **Completado** |
| S1-20 | Análisis de correlaciones con la variable de tracking | Albert Roca | 2 | **Completado** |
| S1-21 | Segmentación por régimen de tracking (STOW/AM/PM/HORIZ.) | Albert Roca | 2 | **Completado** |
| S1-22 | Comparativa de variables entre secciones S1 y S2 | Pau Escobar | 2 | **Completado** |
| S1-23 | Análisis de efectos retardados (lag analysis GPOA→Tsuelo, VWC) | Albert Roca | 2 | **Completado** |
| S1-24 | Evaluación de umbrales agronómicos de ePAR | Joel Alfaro | 2 | **Completado** |
| S1-25 | Hipótesis sobre trackers y zonas experimentales | Joel Alfaro | 2 | **Completado** |
| S1-26 | Inicio de redacción del informe EDA (E01) | Daniel Álvarez (PM) | 2 | **Completado** |
| **Día 5 — Cierre, revisión y entrega** |  |  |  |  |
| S1-27 | Cierre y revisión del notebook E02 | Albert Roca | 2 | **Completado** |
| S1-28 | Cierre del informe EDA (E01) | Daniel Álvarez (PM) | 2 | **Completado** |
| S1-29 | Actualización del registro de riesgos | Daniel Álvarez (PM) | 1 | **Completado** |
| S1-30 | Sprint Review con el cliente | Todo el equipo | 1 | **Pendiente** |
| S1-31 | Sprint Retrospective | Todo el equipo | 1 | **Pendiente** |
| S1-32 | Versionado del código en repositorio Git | Pablo Chacón | 1 | **Parcial** |
| S1-33 | Cierre del paquete documental del sprint (zip) | Daniel Álvarez (PM) | 1 | **En curso** |
| **Total story points planificados** |  |  | **54** |  |
| **Story points completados** |  |  | **50** |  |
| **Velocidad real del sprint** |  |  | **93%** |  |

## 

## 

## 

## **2.2 Distribución de carga por miembro**

*Tabla 3\. Story points por miembro del equipo*

| Miembro | SP planificados | SP completados | % completado |
| :---: | :---: | :---: | :---: |
| Daniel Álvarez (PM) | 8 | 7 | 87,5% |
| Pablo Chacón | 13 | 12 | 92,3% |
| Albert Roca | 15 | 15 | 100% |
| Pau Escobar | 12 | 12 | 100% |
| Joel Alfaro | 6 | 6 | 100% |

# 

# **3\. Introducción al Sprint 1**

Este documento recoge la gestión técnica y operativa del **Sprint 1** del proyecto *Análisis y Optimización Operativa de Sistemas Agrovoltaicos Dinámicos*, incluyendo el resumen del análisis realizado, los entregables generados, las limitaciones identificadas y la actualización del registro de riesgos.

El objetivo principal del sprint ha sido llevar a cabo un **análisis exploratorio de datos (EDA)** riguroso y orientado al dominio agrovoltaico, con los siguientes fines específicos:

* Comprender la estructura y naturaleza de los datasets disponibles.

* Identificar problemas de calidad de datos que afecten a la modelización posterior.

* Detectar patrones temporales y relaciones iniciales entre variables energéticas y microclimáticas.

* Establecer la base técnica y los artefactos reutilizables para la fase de modelización del Sprint 2\.

Todo el análisis se ha desarrollado bajo el **principio rector del proyecto**: buscar el equilibrio entre producción energética y condiciones microclimáticas del cultivo. Ningún análisis o decisión metodológica ha priorizado la variable energética en detrimento de las variables agrícolas.

# **4\. Descripción de los datos**

Se dispone de **16 ficheros en formato CSV** procedentes del sistema de adquisición de sensores de la instalación agrovoltaica. Las variables se agrupan en tres categorías funcionales:

*Tabla 4\. Categorías de variables disponibles*

| Categoría | Variables | Relevancia para el proyecto |
| ----- | ----- | ----- |
| Energéticas / FV | Ángulos de tracking (M01–M10), irradiancia GPOA, albedo, temperatura de paneles | Variable de control y output energético del sistema |
| Microclimáticas | ePAR, humedad volumétrica del suelo (VWC), temperatura del suelo y del aire bajo el dosel | Salud del cultivo y equilibrio hídrico |
| Meteorológicas | Temperatura exterior (WS100), velocidad y dirección del viento, precipitación | Condiciones exógenas no controlables |

Durante la carga inicial se identificaron tres **particularidades técnicas** que condicionaron el diseño del pipeline de datos:

1. **Línea** sep=, **en cabecera:** varios ficheros incluyen esta directiva de exportación de Excel como primera línea, que debe descartarse antes de la lectura.

2. **Valores numéricos con unidades embebidas:** los valores se almacenan como strings con la unidad concatenada ("28.8 °C", "1024 W/m²", "41.4 °"), lo que requiere extracción mediante expresión regular antes de cualquier cálculo.

3. **Resoluciones temporales heterogéneas:** los datasets de sensores de campo trabajan a resolución de 6 horas, los de irradiancia y temperatura de panel a 2 horas, y los de precipitación a resolución de segundos (más de 600.000 filas por fichero).

# 

# **5\. Metodología del EDA**

El análisis se ha estructurado en **nueve bloques secuenciales**, diseñados para avanzar de lo descriptivo a lo interpretativo:

4. **Carga e inventario de datasets:** detección automática de ficheros, caracterización por tamaño, cobertura temporal y tipo de variables.

5. **Auditoría de calidad de datos:** evaluación de nulos, duplicados, columnas constantes y frecuencia de muestreo.

6. **Normalización temporal:** conversión de timestamps a formato datetime, análisis de frecuencias y detección de huecos.

7. **Análisis univariante:** estadísticos descriptivos completos y detección de outliers por método IQR×3.

8. **Análisis temporal:** evolución de variables clave y perfiles intradiarios medios.

9. **Correlaciones entre variables:** construcción de un dataset integrado a 6 horas y cálculo de la matriz de correlaciones de Spearman.

10. **Análisis orientado al dominio agrovoltaico:** segmentación por régimen de tracking, comparativa entre secciones S1 y S2, análisis de retardos y evaluación de umbrales agronómicos de ePAR.

11. **Hipótesis sobre sensores y espacios de investigación:** inferencia de la estructura espacial de la instalación a partir de los datos.

12. **Conclusiones y siguientes pasos:** síntesis de hallazgos, riesgos identificados e inputs para el Sprint 2\.

Como soporte transversal, se desarrollaron funciones auxiliares reutilizables que constituyen la **base del pipeline de datos** del proyecto:

* strip\_unit(series): extracción de valores numéricos de columnas con unidades embebidas.

* load\_csv(filepath): carga robusta de ficheros CSV con gestión de BOM, línea sep= y normalización temporal.

* strip\_all\_units(df): limpieza numérica masiva sobre un DataFrame.

* resample\_to\_6h(df\_num): resampleo temporal a frecuencia común de 6 horas.

# 

# **6\. Análisis realizado y resultados clave**

## **6.1 Inventario y calidad de datos**

Se identificaron los 16 ficheros CSV disponibles, con coberturas temporales que van de 146 a 365 días y frecuencias de muestreo entre 2 horas y segundos. Ningún dataset presentó filas duplicadas. Los porcentajes de nulos oscilaron entre el 29,6% (irradiancia) y el 46,6% (VWC), reflejando un período de inactividad de sensores entre febrero y junio de 2025\. El hallazgo más relevante fue la **zona R1 con más del 95% de nulos** en todos los datasets, lo que invalida su uso como grupo de control.

## **6.2 Análisis temporal**

El análisis temporal confirmó que el **período efectivo de datos válidos** comienza en junio de 2025, a pesar de que los timestamps nominales arrancan en febrero de 2025\. El período con máximo solapamiento entre todos los datasets se extiende de junio a octubre de 2025 (aproximadamente 5 meses). No se detectaron huecos superiores a 7 horas en los datasets de sensores de campo. Los perfiles intradiarios mostraron comportamientos físicamente coherentes: curva campaniforme del GPOA, seguimiento solar en el ángulo de tracking e inercia térmica visible en el suelo.

## **6.3 Estadísticos descriptivos y outliers**

* **Tracking:** rango de −32,3° a 53,5°, con un pico marcado en 50,6° correspondiente a la posición de stow. Los trackers M02, M06 y M10 presentan varianza próxima a cero, indicando posición fija permanente.

* **GPOA:** máximo de 1.032 W/m², media de 326 W/m². Distribución bimodal (noche / día). Sin outliers estadísticos; los valores ligeramente negativos son ruido instrumental nocturno.

* **Temperatura del aire:** la temperatura bajo el dosel (S1 y S2) es sistemáticamente 1–1,2 °C superior a la exterior (WS100), indicando un efecto microclimático de la estructura.

* **VWC:** diferencia sistemática de 4,5 puntos porcentuales entre S1 (media 25,5%) y S2 (media 21,0%), cuya causa no ha podido determinarse con los datos disponibles.

* **ePAR:** los sensores S1d19 y S2d36 presentan un 5,2% y 4,1% de outliers estadísticos respectivamente, probablemente asociados a reflexiones directas o condiciones de cielo despejado con panel en posición óptima.

## **6.4 Correlaciones y análisis de dominio**

Se construyó un dataset integrado de **1.462 timesteps × 29 variables** a resolución de 6 horas. El uso del coeficiente de Spearman (en lugar de Pearson) fue una decisión metodológica explícita, motivada por la naturaleza no lineal esperada de las relaciones entre rotación de paneles y variables microclimáticas.

Los hallazgos más relevantes del análisis de correlaciones y dominio son:

13. Los trackers activos (M01, M03, M05, M07, M09) presentan correlaciones mutuas superiores a 0,95, confirmando una estrategia de rotación coordinada. Para el modelo bastará un tracker representativo.

14. La posición de **stow (50,6°)** reduce significativamente el ePAR bajo el dosel. Es el régimen de operación más perjudicial para el cultivo durante las horas de luz.

15. El análisis de retardos mostró que la **temperatura del suelo responde con un lag de 6–12 horas** respecto a la irradiancia. El VWC, en cambio, tiene una dinámica de días y no responde directamente a cambios en la irradiancia.

16. La diferencia sistemática de VWC entre S1 y S2 requiere que el modelo trate ambas secciones de forma diferenciada o incluya una variable indicadora de sección.

# 

# **7\. Entregables y outputs generados**

*Tabla 5\. Entregables técnicos del Sprint 1*

| ID | Entregable | Responsable | Estado |
| :---: | ----- | ----- | :---: |
| E01 | Informe de Análisis Exploratorio (este documento \+ report\_resultados.tex) | Daniel Álvarez (PM) | **Completado** |
| E02 | Notebook EDA reproducible (sprint1\_eda\_agrovoltaica.ipynb) | Albert Roca / Pablo Chacón | **Completado** |
| — | Dataset integrado a 6h (dataset\_integrado\_6h.csv) | Pablo Chacón | **Completado** |
| — | Informe de calidad (quality\_report.csv) | Pau Escobar | **Completado** |
| — | 22 visualizaciones en sprint1/outputs/ | Pau Escobar | **Completado** |
| — | Lecciones aprendidas (lecciones\_aprendidas.tex) | Daniel Álvarez (PM) | **Completado** |

Los outputs generados en sprint1/outputs/ incluyen inventarios de datasets, informes de calidad, resúmenes temporales, distribuciones univariantes, series temporales, matriz de correlaciones, análisis de lag, comparativas entre secciones y visualizaciones de umbrales agronómicos. Estos artefactos constituyen la **base operativa reproducible** del proyecto para los siguientes sprints.

# 

# **8\. Limitaciones identificadas**

Se han identificado las siguientes limitaciones que deben tenerse en cuenta en el Sprint 2:

*Tabla 6\. Limitaciones del Sprint 1*

| Limitación | Impacto | Implicación para el Sprint 2 |
| ----- | ----- | ----- |
| Zona R1 sin datos operativos | Alto | No hay grupo de control. Se propone WS100 como referencia parcial |
| Trackers sin información contextual | Alto | No podemos entender la información que se nos proporciona de los trackers, por lo que no podemos hacer un análisis más profundo del efecto de las placas fotovoltaicas. |
| Trackers M02, M06, M10 con posición fija | Medio | Excluir del modelo hasta validación técnica |
| Período efectivo limitado al verano de 2025 | Medio | El modelo no capturará variabilidad estacional; documentar explícitamente |
| Pérdida de resolución por resampleo a 6h | Bajo-Medio | Evaluar si usar resolución 2h para variables energéticas en el modelo |
| Tipo de cultivo desconocido | Medio | Los umbrales agronómicos usados son genéricos; solicitar al cliente |
| Diferencia de VWC entre S1 y S2 sin causa conocida | Medio | Incluir variable indicadora de sección o modelizar por separado |
| Sensor S2 T1 con valor extremo (111 °C) | Bajo | Excluir o marcar como outlier; verificar calibración del sensor |

# 

# **9\. Actualización del registro de riesgos**

El desarrollo del Sprint 1 ha permitido **validar empíricamente** varios de los riesgos identificados en el kick-off, reducir la incertidumbre sobre algunos de ellos y añadir nuevos riesgos derivados del EDA.

## **9.1 Riesgos preexistentes: estado tras el Sprint 1**

*Tabla 7\. Estado de los riesgos preexistentes tras el Sprint 1*

| ID | Riesgo | Estado previo | Estado actual | Observación |
| :---: | ----- | :---: | :---: | ----- |
| R1 | Calidad y continuidad de los datos | Identificado | **Confirmado** | Nulos elevados, zona R1 inoperativa, trackers anómalos. Parcialmente mitigado con pipeline de limpieza |
| R2 | Desalineación temporal entre sensores | Identificado | **Confirmado** | Frecuencias heterogéneas (2h, 6h, s). Mitigado con resampleo a 6h |
| R3 | No linealidad y efectos retardados | Identificado | **Validado** | Confirmado empíricamente. Lag de 6–12h en Tsuelo. Incorporar en feature engineering |
| R4 | Sesgo hacia optimización energética | Identificado | **Controlado** | El análisis incorporó sistemáticamente variables microclimáticas en todos los bloques |
| R5 | Sobreajuste al histórico disponible | Identificado | **Vigente** | Sin cambios. A gestionar en la fase de modelización del Sprint 2 |
| R6 | Fallo en pipeline o ingesta | Identificado | **Mitigado** | Pipeline de carga robusto implementado y probado sobre todos los datasets |

## **9.2 Nuevos riesgos identificados en el Sprint 1**

*Tabla 8\. Nuevos riesgos identificados durante el EDA*

| ID | Riesgo | Prob. | Impacto | Plan de mitigación |
| :---: | ----- | :---: | :---: | ----- |
| R7 | Datos limitados al período estival (generalización estacional limitada) | Alta | Medio | Documentar explícitamente el alcance temporal del modelo; solicitar datos de otros períodos si disponibles |
| R8 | Sensores con comportamiento anómalo (trackers M02/M06/M10, sensor S2 T1) | Media | Medio | Verificación técnica en Sprint 2; excluir o tratar aparte hasta confirmación |
| R9 | Pérdida de información relevante por resampleo a 6h | Media | Bajo | Evaluar si variables energéticas requieren resolución 2h en el modelo |
| R10 | Ausencia de contexto agronómico específico (tipo de cultivo) | Alta | Medio | Escalar al PM para solicitud formal al cliente antes del Sprint 2 |
| R11 | Diferencia de VWC entre S1 y S2 de causa desconocida | Media | Medio | Consultar al equipo técnico de la planta; incluir variable indicadora de sección |

| Valoración global del registro de riesgos tras Sprint 1 El Sprint 1 ha reducido significativamente la incertidumbre técnica del proyecto. Los riesgos R1, R2 y R6 han sido parcial o totalmente mitigados. R3 y R4 han pasado de ser hipótesis a ser evidencias confirmadas, lo que permite gestionar el Sprint 2 con mayor precisión. Los riesgos R7–R11 son nuevos y deben ser activamente gestionados en la fase de modelización. |
| :---- |

## **9.3 Problemas con la información de los datasets** {#9.3-problemas-con-la-información-de-los-datasets}

Es cierto que, a lo largo del análisis, hemos conseguido reducir de forma significativa la incertidumbre técnica inicial, especialmente en lo relativo al tratamiento de los datos, la limpieza de series temporales y la identificación de patrones generales. Sin embargo, persisten diversas limitaciones asociadas a la falta de documentación detallada de los datasets, lo que introduce ambigüedades importantes en la interpretación de los resultados.

En primer lugar, existen dudas relevantes sobre la nomenclatura de los nodos. En los ficheros aparecen identificadores como *R1*, *S1* o *S2*, que asumimos que hacen referencia a distintas zonas de los campos (por ejemplo, una zona de referencia frente a zonas con placas solares), pero esta asignación no está explícitamente confirmada. Asimismo, la componente numérica asociada (por ejemplo, *d10*, *d40*, etc.) no está claramente definida: podría corresponder a la posición física del sensor, a un identificador interno del nodo o incluso a la profundidad de instalación. Esta ambigüedad se extiende a los nombres de variables, como *R1d41\_HD3910* o *S2d32\_HD3910*, cuya interpretación exacta no es evidente sin documentación adicional.

En segundo lugar, los sensores ePAR (SQ618) generan múltiples columnas por cada dispositivo (*cal\_out*, *cal\_out\_16bit*, *immersed* e *immersed\_16bit*), pero no se dispone de una explicación clara sobre las diferencias entre estas variables. En particular, no queda claro qué distingue las versiones “normales” de las de 16 bits, ni qué representa exactamente la variable *immersed* en este contexto. Esta falta de claridad dificulta la selección de la variable más adecuada para el análisis y puede afectar a la comparabilidad de los resultados.

En tercer lugar, los sensores de suelo (HD3910) presentan identificadores como *R1d41*, *R1d42*, *R1d43*, *R1d44* o *S1d13* hasta *S1d18*, pero no está claro si estos códigos corresponden a distintas profundidades de medición (por ejemplo, 10 cm, 20 cm, etc.) o a posiciones horizontales dentro de la parcela. Esta distinción es fundamental para interpretar correctamente variables como la humedad o la temperatura del suelo, ya que su comportamiento varía significativamente con la profundidad.

Por último, existe incertidumbre en relación con los trackers del sistema fotovoltaico. No se dispone de información precisa sobre qué controla cada tracker (si una única placa o un conjunto de ellas), ni sobre cómo se distribuyen entre las distintas zonas experimentales (S1 y S2). Aunque se han identificado dos grupos de trackers, no es posible asignarlos con certeza a cada zona. Esta limitación resulta especialmente crítica, ya que impide analizar con rigor el efecto diferencial de la presencia de placas solares sobre las variables del suelo.

Actualmente, estamos a la espera de recibir respuesta por parte del cliente responsable de la instalación de los sensores, con el objetivo de aclarar todas estas cuestiones. Mientras tanto, el análisis realizado en el Sprint 1 debe considerarse parcialmente incompleto en aquellos aspectos que dependen de esta información. Está previsto que en el Sprint 2 se complete y refine el análisis incorporando las aclaraciones y datos adicionales que nos proporcione el cliente.

# **10\. Seguimiento del Presupuesto**  {#10.-seguimiento-del-presupuesto}

Durante el cierre del Sprint 1, el análisis exploratorio (EDA) ha revelado anomalías no documentadas en los datos, específicamente el comportamiento estático de los trackers M02, M06 y M10 en la posición de 50.6° y la falta total de operatividad en la Zona R1.

La ausencia de metadatos que expliquen si esto responde a un fallo mecánico o a una estrategia deliberada del cliente nos impide cerrar el dataset definitivo para el entrenamiento del modelo. Para no bloquear el avance del proyecto durante el Sprint 2, el equipo tendrá que invertir horas no planificadas en parametrizar los scripts de limpieza (ETL) y reestructurar el modelo base (Data Science). Esto nos permitirá excluir temporalmente los trackers dudosos y dejar el código preparado para re-ejecutarse rápidamente en cuanto el cliente confirme el significado de estas variables.

Por este motivo, calculamos que esta adaptación técnica preventiva nos requerirá unas **8 horas adicionales** de trabajo del equipo, lo que justifica la activación de una provisión de **350,00 €** de la reserva de contingencia. Por lo cual el presupuesto queda tal que así:

*Tabla 9\. Presupuesto actualizado*

| Rol en el Proyecto | Responsabilidad Principal | Horas | Tarifa/Hora | Coste Total | Observaciones |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **PM & Data Governance** | Gestión del proyecto, cronograma, riesgos, stakeholders y gobernanza del dato. Trazabilidad metodológica y control de calidad transversal del pipeline. | 111 | 50 € | **5.550,00 €** | **\+1h para gestión de crisis y replanificación del Sprint 2 por falta de metadatos.** |
| **Lead Data Engineer (Pipeline & Infraestructura)** | Diseño e implementación del broker de streaming, sincronización temporal entre sensores, deduplicado y data lake. Responsable de R6 (interrupción del pipeline) y R9 (seguridad y privacidad de datos operativos). | 195 | 50 € | **9.750,00 €** | **Sin cambios.**  |
| **Data Scientist (Modelado & Optimización)** | Diseño y entrenamiento del modelo de optimización de rotación. Feature engineering, tratamiento de no-linealidades (R3), sobreajuste (R5), loop de reentrenamiento periódico y R4 (sesgo hacia optimización energética en detrimento del equilibrio microclimático). | 163 | 45 € | **7.335,00 €** | **\+3h previstas para reestructurar el modelo base y aislar trackers anómalos (M02/06/10).** |
| **Data Analyst / ETL Engineer (Calidad del Dato)** | Imputación de NAs (R1), desalineación temporal entre sensores (R2), validación de features y mantenimiento del feature store. Filtro de calidad antes de que los datos lleguen al modelo. | 129 | 40 € | **5.160,00 €** | **\+4h para parametrizar scripts de limpieza que permitan re-ejecución rápida tras recibir metadata.** |
| **BI Developer (Dashboard & Alertas)** | Diseño del dashboard interactivo, reglas operativas de alertas (límites biológicos, avisos de clima) y visualizaciones de KPIs para el cliente. | 125 | 35 € | **4.375,00 €** | **Sin cambios.**  |

**NOTA:** Estos 350 € adicionales (8 horas de equipo) se detraerán de la partida de **Contingencia (3.452,50 €)**, dejando un remanente de **3.102,50 €** para futuros riesgos. Esto permite que el presupuesto total del proyecto (37.977,50 €) se mantenga invariable para el cliente, absorbiendo el problema internamente.

# 

# **11\. Verificación del Definition of Done**

*Tabla 10\. Verificación del DoD para los entregables del Sprint 1*

| Criterio DoD | Aplica | Estado |
| ----- | :---: | :---: |
| El notebook (E02) ejecuta sin errores | Sí | **Completado** |
| Las funciones principales están documentadas en el notebook | Sí | **Completado** |
| El entregable incluye sección de limitaciones y próximos pasos | Sí | **Completado** |
| El informe (E01) sigue la plantilla aprobada por el equipo | Sí | **Completado** |
| El código está versionado en el repositorio con mensaje descriptivo | Sí | **Parcial** |
| Ha sido revisado por al menos un miembro diferente al autor | Sí | **Completado** |
| El cliente ha aceptado el entregable en la Review (o hay feedback) | Sí | **Pendiente** |
| El PM ha actualizado el Sprint Backlog con estado «Hecho» | Sí | **En curso** |
| El Registro de Riesgos ha sido actualizado | N/A | **Completado** |

Los criterios pendientes (revisión externa, validación del cliente y versión completa) se cerrarán durante la Sprint Review prevista para el cierre formal del sprint.

# 

# **12\. Relación con el Sprint 2**

Los resultados del Sprint 1 constituyen la **base directa** para el Sprint 2, centrado en la modelización y la definición de la política operativa de rotación.

## **12.1 Entregables previstos en Sprint 2**

*Tabla 11\. Entregables del Sprint 2 y su dependencia con el Sprint 1*

| ID | Entregable | Responsable | Dependencia del Sprint 1 |
| :---: | ----- | ----- | ----- |
| E03 | Informe de política de rotación \+ modelo | Albert Roca (Tech Lead) | Hallazgos EDA, análisis de lag, segmentación por régimen |
| E04 | Código del modelo | Pablo Chacón / Albert Roca | dataset\_integrado\_6h.csv \+ funciones del pipeline |

## **12.2 Inputs técnicos del Sprint 1 para el Sprint 2**

* dataset\_integrado\_6h.csv: dataset base listo para feature engineering y entrenamiento del modelo.

* **Funciones del pipeline** (strip\_unit, load\_csv, resample\_to\_6h): se reutilizarán como módulo de preparación de datos sin necesidad de reescritura.

* **Régimen de tracking** (STOW / TRACKING\_AM / TRACKING\_PM / HORIZONTAL): variable categórica lista para incorporar como feature.

* **Lag features identificadas:** temperatura del suelo con retardo de 6h y 12h respecto a GPOA.

* **Trackers a excluir o tratar aparte:** M02, M06 y M10.

* **Variable indicadora de sección** (S1 vs. S2): necesaria por la diferencia sistemática de VWC.

## **12.3 Decisiones de modelización orientadas desde el EDA**

17. **Variable objetivo:** definir el índice combinado Energía–Cultivo (IEC) integrando GPOA y ePAR normalizado, con ponderación a validar con el especialista agrícola.

18. **Enfoques de modelización a explorar:** árbol de decisión (interpretabilidad directa) y regresión regularizada (generalización). Comparar ambos antes de seleccionar el definitivo.

19. **Restricciones operativas a incorporar:** el modelo debe penalizar ángulos que sitúen el ePAR bajo el umbral de compensación lumínica durante horas de luz solar.

20. **Reorganización del equipo:** el Sprint 2 concentrará el esfuerzo de Albert Roca y Pablo Chacón en la implementación del modelo, mientras Daniel Álvarez (PM) y Joel Alfar liderarán la validación agronómica de las reglas de rotación propuestas.

# 

# **13\. Lecciones Aprendidas** {#13.-lecciones-aprendidas}

| ID | Sprint | Categoría | Descripción de la lección | Recomendación para futuros proyectos |
| :---: | :---: | :---: | ----- | ----- |
| LL-01 | S1 | Calidad / Técnica | Los ficheros CSV exportados por el sistema de adquisición incluyen unidades de medida embebidas en los valores numéricos (“28.8 °C”, “1024 W/m²”) y una primera línea sep=, no estándar. Esto no estaba previsto en la planificación inicial y requirió diseñar funciones de limpieza específicas antes de poder comenzar cualquier análisis. | Al iniciar cualquier proyecto con datos de sistemas SCADA o plataformas IoT industriales, dedicar un tiempo explícito en el backlog del Sprint 1 a inspeccionar manualmente el formato de los ficheros antes de estimar el esfuerzo de carga y limpieza. Documentar las peculiaridades del formato como parte del inventario. |
| LL-02 | S1 | Estimación / Planificación | El volumen de los ficheros de precipitación de alta frecuencia (más de 600.000 filas por fichero, resolución en segundos) no estaba identificado en la planificación inicial. Su carga directa habría saturado la memoria disponible y distorsionado los análisis de frecuencia temporal del resto de datasets. | En el Sprint Planning, incluir siempre un paso previo de estimación de tamaño de los datasets (filas, columnas, frecuencia de muestreo) antes de definir las tareas técnicas. Para proyectos con datos de sensores, distinguir explícitamente entre datasets de baja frecuencia (análisis) y alta frecuencia (eventos) desde el inicio. |
| LL-03 | S1 | Calidad / Técnica | La zona de sensores R1 presentó más del 95% de valores nulos en todos los datasets durante el período analizado. Este hecho no se conocía antes del EDA y elimina la posibilidad de disponer de un grupo de control real para comparar secciones experimentales. El dato no figura en ninguna documentación del cliente recibida hasta la fecha. | Solicitar al cliente, antes del inicio del proyecto o en el kick-off, un documento de metadatos que describen el estado operativo de cada zona de sensores, el período de activación de cada instrumento y cualquier incidencia de hardware conocida. Incluir esta verificación como criterio de aceptación del Sprint 1\. |
| LL-04 | S1 | Comunicación | Durante el EDA se detectaron tres trackers (M02, M06, M10) con ángulo prácticamente constante en torno a 50,6°, comportamiento que podría deberse a un fallo mecánico, a una posición de stow permanente o a una decisión operativa deliberada. Sin acceso al equipo técnico de la planta durante el sprint, no fue posible confirmar la causa, lo que introduce incertidumbre en todos los análisis de correlación que implican a esos trackers. | Establecer desde el kick-off un canal de comunicación directo y ágil con el equipo técnico de la instalación (no solo con los stakeholders de negocio). Definir un protocolo de consulta técnica con tiempo de respuesta máximo acordado, especialmente para las primeras semanas del proyecto cuando los hallazgos del EDA generan preguntas críticas. |
| LL-05 | S1 | Gestión del equipo | La decisión de usar el coeficiente de Spearman en lugar de Pearson para la matriz de correlaciones se tomó de forma individual sin consenso explícito del equipo. Aunque la decisión es técnicamente correcta (relaciones potencialmente no lineales), no quedó registrada en el momento, lo que puede dificultar la justificación en la Sprint Review o en el Sprint 2\. | Registrar en el notebook o en un documento de decisiones técnicas del sprint todas las elecciones metodológicas no triviales (métrica de correlación, frecuencia de resampleo, umbrales usados), con una justificación de una línea. Esto facilita la revisión entre pares y la trazabilidad hacia sprints posteriores. |
| LL-06 | S1 | Estimación / Planificación | El período con datos válidos (no nulos) en los sensores comenzó en junio de 2025, a pesar de que los timestamps más antiguos de los ficheros datan de febrero de 2025\. Esto supone que el volumen de datos realmente utilizable es menor del estimado inicialmente, y que el análisis de estacionalidad queda restringido a los meses de verano. | En proyectos de análisis de datos históricos, distinguir entre período de cobertura nominal (primer y último timestamp del fichero) y período de cobertura efectiva (primer y último timestamp con datos válidos). Usar el segundo para planificar el alcance analítico real del proyecto. |
| LL-07 | S1 | Calidad / Técnica | Los umbrales agronómicos utilizados para evaluar el ePAR (punto de compensación lumínica, fotosíntesis activa, rango óptimo) se tomaron de referencias bibliográficas genéricas para cultivos C3, ya que en ningún documento del cliente se especifica el tipo de cultivo presente en la instalación. Esto limita la interpretabilidad de los análisis de dominio. | Incluir en el acta de kick-off una sección de metadatos agronómicos mínimos: tipo de cultivo, variedad, estadio fenológico durante el período de datos, y cualquier práctica de manejo relevante (riego, fertilización). Sin esta información, los análisis microclimáticos del EDA tienen validez limitada. |
| LL-08 | S1 | Gestión del cambio | Durante el EDA no se recibió ninguna solicitud de cambio formal. Sin embargo, la magnitud de los problemas de calidad detectados (zona R1 vacía, trackers con posible fallo, período efectivo de datos más corto de lo previsto) implica que el alcance del Sprint 2 puede necesitar ajustarse para incluir un paso de limpieza y validación más extenso del inicialmente planificado. | Contemplar en el Sprint Planning del Sprint 2 un buffer de tiempo para la revisión de los hallazgos del EDA antes de comenzar la modelización. Si los problemas de calidad detectados afectan al alcance o al plazo, formalizarlo como Change Request en los primeros días del Sprint 2 en lugar de absorberlo silenciosamente. |

