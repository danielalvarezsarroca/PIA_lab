# Sprint 2 - Modelizacion y Politica de Rotacion

## Objetivo
Este sprint desarrolla la parte tecnica de modelizacion para proponer una politica de rotacion de placas que equilibre produccion energetica y condiciones favorables para el cultivo.

El entregable principal es el notebook [sprint2_modelizacion_agrovoltaica.ipynb](./sprint2_modelizacion_agrovoltaica.ipynb), y este documento resume de forma clara que se ha hecho, que resultados salen y que reglas candidatas quedan.

## Alcance cubierto
Se ha cubierto la parte tecnica de las historias:
- `S2-01` Definicion de target y features
- `S2-02` Preparacion y limpieza del dataset de modelizacion
- `S2-03` Entrenamiento y evaluacion de dos enfoques
- `S2-04` Traduccion a reglas interpretables
- `S2-05` Publicacion del codigo del modelo

No se incluye aqui la parte de gestion (`Change Request`, riesgos, presupuesto, review y retrospective).

## Pipeline de datos
Se ha mantenido la misma filosofia que en Sprint 1: un unico notebook como entregable. Dentro del notebook se han formalizado las funciones clave del pipeline:
- `strip_unit`
- `load_csv`
- `resample_to_6h`

La mejora importante frente al Sprint 1 es que `strip_unit` ahora soporta correctamente columnas `string` de `pandas`, no solo columnas `object`. Eso evita que varias variables numericas quedasen vacias al convertir unidades como `41.4 °`, `28.8 °C` o `1024 W/m²`.

## Dataset integrado y ventana util
Se han integrado los datasets principales de:
- temperatura del aire
- ePAR
- irradiancia
- temperatura de panel
- temperatura del suelo
- VWC del suelo
- tracking
- velocidad de viento

La resolucion de trabajo es de `6 horas`, igual que en Sprint 1.

Resultados del solapamiento util:
- Dataset integrado: `1462` filas y `30` variables base seleccionadas
- Periodo total integrado: `2025-02-12 06:00:00` a `2026-02-12 12:00:00`
- Observaciones finalmente modelables: `337`
- Ventana realmente util para modelizacion: `2025-06-18 12:00:00` a `2025-10-05 00:00:00`
- Particion temporal: `269` filas de train y `68` filas de test

El dataset final se ha guardado en [outputs/dataset_modelizacion_6h.csv](./outputs/dataset_modelizacion_6h.csv).

## Feature engineering
Se han creado las features pedidas para el sprint:
- `hour_of_day`
- `day_of_year`
- `solar_elevation_deg`
- medias por seccion para `ePAR`, `VWC` y temperatura de suelo
- `Tsoil_S1_mean_lag_6h`
- `Tsoil_S1_mean_lag_12h`
- `VWC_diff_S1_minus_S2`
- `tracking_regime`
- `track_mean`

El `tracking_regime` se clasifica de forma operativa en:
- `TRACKING_AM`
- `TRACKING_PM`
- `HORIZONTAL`
- `STOW`
- `UNKNOWN`

## Target propuesto: IEC
Como todavia no existe un target validado por el equipo, se ha definido un indice combinado provisional llamado `IEC` (`Indice Energia-Cultivo`).

Formulacion:
- `energy_score`: proxy energetico a partir de la media de `GPOA_S1` y `GPOA_S2`, normalizada por su percentil 95.
- `crop_score`: combinacion ponderada de tres proxys agronomicos:
  - `ePAR` medio centrado en `600`
  - `VWC` medio centrado en `30%`
  - temperatura media de suelo centrada en `28 C`
- `IEC = 0.5 * energy_score + 0.5 * crop_score`

Interpretacion:
- valores altos de `IEC` implican mejor equilibrio energia-cultivo
- valores bajos implican peores condiciones combinadas

Importante: esta formulacion es util para el Sprint 2, pero sigue pendiente de validacion con el equipo tecnico y agronomico.

## Modelos entrenados
Se han entrenado dos modelos:

### 1. Decision Tree Regressor
Objetivo:
- maximizar interpretabilidad
- obtener reglas if-then candidatas

Configuracion:
- `max_depth=4`
- `min_samples_leaf=20`

### 2. ElasticNetCV
Objetivo:
- mejorar generalizacion
- obtener una lectura mas robusta de relaciones lineales regularizadas

## Resultados de evaluacion
Metricas sobre el conjunto de test temporal:

| Modelo | MAE | RMSE | R2 |
|---|---:|---:|---:|
| ElasticNet | 0.0384 | 0.0515 | 0.9478 |
| DecisionTree | 0.0730 | 0.0936 | 0.8276 |

Lectura:
- `ElasticNet` generaliza mejor y es el mejor modelo predictivo de esta iteracion.
- `DecisionTree` rinde peor, pero sigue siendo suficientemente bueno para extraer reglas operativas interpretables.

Las metricas se guardan en [outputs/model_metrics.csv](./outputs/model_metrics.csv).

## Variables mas influyentes
### En el arbol
Las variables que dominan el arbol son:
- `Albedo_S1`
- `Albedo_S2`
- `solar_elevation_deg`
- `VWC_S1_mean`
- `GPOA_S1`

Esto sugiere que el comportamiento del sistema en esta ventana temporal depende mucho de:
- las condiciones radiativas
- la humedad del suelo
- la altura solar

### En ElasticNet
Los coeficientes mas influyentes incluyen:
- `tracking_regime_HORIZONTAL` con efecto negativo
- `GPOA_S1` y `GPOA_S2` con efecto positivo
- `tracking_regime_TRACKING_PM` con efecto positivo
- `Tsoil_S2_mean` y `VWC_S2_mean` con efecto positivo moderado

Interpretacion compacta:
- `HORIZONTAL` penaliza el equilibrio global
- `TRACKING_PM` aparece asociado a mejor `IEC`
- mas irradiancia productiva ayuda, siempre dentro del compromiso con el cultivo

## Reglas candidatas de rotacion
Las reglas extraidas se han basado en:
- el arbol de decision
- la tabla de casos con `IEC` alto
- el comportamiento agregado por regimen

Las reglas candidatas guardadas en [outputs/candidate_rotation_rules.csv](./outputs/candidate_rotation_rules.csv) quedan mejor formuladas en `6` reglas:

1. Si la franja es `12:00` y el sistema opera en `TRACKING_PM`, mantener un angulo cercano a `31.8°`.
2. Si la franja es `06:00` y el sistema opera en `TRACKING_AM`, mantener un angulo cercano a `-32.2°`.
3. Evitar `HORIZONTAL` en las franjas productivas cuando existan condiciones para tracking activo.
4. Si `Albedo_S1 > 55.7` y la elevacion solar supera `68°`, priorizar tracking activo de tarde: es el escenario de mayor `IEC` detectado por el arbol.
5. Si `Albedo_S1 <= 55.7`, `Albedo_S2 <= 18.0`, `VWC_S1 <= 22.2` y `GPOA_S2 <= 35.5`, no forzar una politica orientada a produccion: el `IEC` esperado es muy bajo.
6. Si `Albedo_S1 <= 55.7` pero `Albedo_S2 > 18.0` y `VWC_S1 > 20.0`, usar tracking suave o una transicion controlada antes que `HORIZONTAL` permanente.

## Regla final resumida
Si hubiera que resumir la politica resultante de este sprint en una sola idea:

> En las horas productivas, conviene operar con tracking activo y angulos intermedios de aproximadamente `-32°` por la manana y `+32°` al mediodia, evitando posiciones horizontales y reservando reglas de cautela para escenarios de baja irradiancia y baja humedad del suelo.

## Evidencia por regimen
Resumen del `IEC` medio por regimen:

| Regimen | Count | Mean IEC | Median IEC |
|---|---:|---:|---:|
| HORIZONTAL | 169 | 0.204 | 0.184 |
| TRACKING_AM | 84 | 0.440 | 0.429 |
| TRACKING_PM | 84 | 0.742 | 0.741 |

Lectura:
- `TRACKING_PM` domina claramente en esta ventana de datos
- `TRACKING_AM` tambien mejora a `HORIZONTAL`
- `HORIZONTAL` queda como el peor regimen en terminos de equilibrio energia-cultivo

## Observaciones sobre trackers
En Sprint 1 se habia marcado como pendiente confirmar el estado de `M02`, `M06` y `M10`.

En la ejecucion de Sprint 2, el diagnostico simple por varianza no muestra a esos trackers como casos claros de `stow` fijo. Eso significa dos cosas:
- no hay evidencia suficiente para declarar fallo mecanico solo con este chequeo
- la validacion con el equipo de planta sigue siendo necesaria

El diagnostico se ha guardado en [outputs/tracker_variance_diagnostic.csv](./outputs/tracker_variance_diagnostic.csv).

## Limitaciones
Las principales limitaciones de este sprint son:
- el `IEC` sigue siendo provisional
- falta validar el tipo real de cultivo
- faltan umbrales agronomicos oficiales de `ePAR`, `VWC` y temperatura de suelo
- la ventana util de modelizacion es parcial y no cubre un ciclo anual completo
- las reglas no deben pasar al dashboard sin revision del especialista agricola

## Archivos clave generados
- [sprint2_modelizacion_agrovoltaica.ipynb](./sprint2_modelizacion_agrovoltaica.ipynb)
- [outputs/model_metrics.csv](./outputs/model_metrics.csv)
- [outputs/candidate_rotation_rules.csv](./outputs/candidate_rotation_rules.csv)
- [outputs/high_iec_policy_table.csv](./outputs/high_iec_policy_table.csv)
- [outputs/decision_tree_rules.txt](./outputs/decision_tree_rules.txt)
- [outputs/decision_tree_interpretability.png](./outputs/decision_tree_interpretability.png)
- [outputs/elasticnet_coefficients.csv](./outputs/elasticnet_coefficients.csv)

## Conclusion
El Sprint 2 deja una primera politica de rotacion cuantificada y defendible:
- tracking activo mejor que horizontal en franjas productivas
- angulos intermedios alrededor de `-32°` por la manana y `+32°` al mediodia
- un conjunto mas completo de `6` reglas, incluyendo reglas operativas y de excepcion
- `ElasticNet` como mejor modelo predictivo
- `DecisionTree` como mejor soporte para reglas interpretables

La siguiente iteracion deberia centrarse en validar agronomicamente estas reglas y convertirlas en logica operativa para el dashboard.
