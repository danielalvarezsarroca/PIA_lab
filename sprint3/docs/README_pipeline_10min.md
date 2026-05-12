# Pipeline experimental a 10 minutos

Esta rama mantiene el pipeline de 6 horas como backup y anade una alternativa
experimental basada directamente en `sprint3/outputs/master_dataset.csv`, que
tiene resolucion de 10 minutos.

## Idea

- Fuente granular: `outputs/master_dataset.csv`.
- Vista de modelizacion: `outputs_10min/dataset_modelizacion_10min.csv`.
- Reglas candidatas: `outputs_10min/candidate_rotation_rules_10min.csv`.
- Riesgo agricola demo: `outputs_10min/crop_risk_10min.csv`.
- Reglas agronomicas demo: `outputs_10min/agricultural_rules_10min.csv`.
- Politica RL offline: `outputs_10min/rl_policy_actions_10min.csv`.
- Trayectorias temporales RL: `outputs_10min/rl_trajectories_10min.csv`.
- Perfiles de cultivo: `outputs_10min/crop_profiles.json`.
- Backup estable: `outputs_10min/backup_6h/`.

El objetivo es demostrar como cambiarian las reglas si el sistema reaccionara a
datos mas frecuentes de la planta, sin perder la version 6h como referencia.
La capa agronomica esta pensada para poder sustituir los valores imputados por
datos diarios de sensores reales cuando la planta este integrada.

## Ejecucion

Desde la raiz del repositorio:

```bash
cd sprint3
source .venv/bin/activate
python build_10min_pipeline.py
```

Se puede cambiar el cultivo demo:

```bash
python build_10min_pipeline.py --crop-type brocoli
```

Tambien se puede generar una zona de cultivo independiente para S1 o S2:

```bash
python build_10min_pipeline.py --crop-type patata --crop-zone S2
```

El comando genera:

- `outputs_10min/dataset_modelizacion_10min.csv`
- `outputs_10min/candidate_rotation_rules_10min.csv`
- `outputs_10min/crop_risk_10min.csv`
- `outputs_10min/agricultural_rules_10min.csv`
- `outputs_10min/rl_policy_actions_10min.csv`
- `outputs_10min/rl_policy_metadata.json`
- `outputs_10min/rl_trajectories_10min.csv`
- `outputs_10min/rl_trajectories_metadata.json`
- `outputs_10min/crop_profiles.json`
- `outputs_10min/pipeline_10min_metadata.json`
- `outputs_10min/backup_6h/dataset_modelizacion_6h.csv`
- `outputs_10min/backup_6h/candidate_rotation_rules.csv`

## Capa agronomica referenciada

Con las variables actuales se generan recomendaciones para:

- `regar`: VWC por debajo del umbral de confort.
- `pausar_riego`: VWC alto o lluvia reciente.
- `riego_preventivo`: deficit hidrico combinado con calor.
- `aumentar_sombreado`: estres termico o radiacion excesiva.
- `reducir_sombreado`: PAR baja sin estres termico ni lluvia.
- `posicion_segura`: viento elevado.
- `alerta_frio`: temperatura de suelo demasiado baja.

Estas reglas no son una recompensa RL aprendida ni un modelo agronomico
supervisado. Son una capa experta interpretable aplicada sobre variables proxy
que si existen en el dataset: `VWC_S1_mean`, `Tsoil_S1_mean`, `Tair_WS`,
`ePAR_S1_mean`, `ePAR_R1_mean`, `wind_speed_kmh` y
`precip_intensity_mm10min`.

Los perfiles de `lechuga`, `brocoli`, `generico_horticola`, `tomate`,
`pimiento`, `fresa`, `espinaca`, `cebolla` y `patata` comparten un esquema
normalizado con:

- rangos de VWC, temperatura de suelo, PAR y temperatura del aire;
- fases de cultivo y dias estimados hasta cosecha;
- requisitos de riego, luz y abonado;
- fuentes tecnicas en `crop_profiles.json`.

- FAO-56 para marco de necesidades hidricas (`ETo`, `Kc`, `ETc`).
- RuralCat como referencia local catalana de recomendaciones de riego.
- Guias de extension agricola para rangos termicos de lechuga y brocoli.
- Extension universitaria sobre uso de sensores de humedad del suelo en
  hortalizas.

## Riego automatico y zonas de cultivo

El actuador de riego no se modela como goteo constante. Se activa solo cuando
la regla agronomica detecta necesidad de agua:

- `activar_riego`: 2.0 mm por intervalo de 10 min, duracion operativa 10 min,
  ajuste proxy de +0.010 en VWC y -0.15 C en temperatura de suelo.
- `riego_preventivo`: 1.2 mm por intervalo de 10 min, duracion operativa 6 min,
  ajuste proxy de +0.006 en VWC y -0.08 C en temperatura de suelo.
- `pausar_riego` y `sin_manejo_directo`: 0 mm.

Las zonas `S1` y `S2` pueden ejecutarse con cultivos diferentes usando el mismo
modelo de forma independiente. Si faltan sensores reales de la zona elegida, el
pipeline completa los campos con proxies trazables:

- primero usa el sensor directo de la zona (`*_S1_*` o `*_S2_*`);
- si S2 no tiene dato, usa S1 como proxy bajo placa;
- si tampoco hay sensor de suelo bajo placa, imputa desde R1:
  `VWC_R1 + 0.015`, `Tsoil_R1 - 0.6 C` de dia, `Tsoil_R1 + 0.2 C` de noche, y
  `ePAR_R1 * 0.78`;
- si todo lo anterior falta, usa el centro del rango agronomico del cultivo.

Estas correcciones son supuestos explicitos para demo, no una prueba de efecto
invernadero medido. Por eso `crop_risk_10min.csv` y `rl_trajectories_10min.csv`
incluyen `VWC_crop_zone_source`, `Tsoil_crop_zone_source` y
`ePAR_crop_zone_source`, de forma que cada fila indica si el dato fue real,
proxy o imputado.

## RL y trayectorias temporales

La accion por instante se define como una accion conjunta factorizada:
`(panel_action, irrigation_action)`. Esto permite recomendar mover placas y
regar en el mismo intervalo cuando la combinacion mejora un unico reward:

```text
reward = alpha * componente_agricola + beta * componente_electrico
```

La politica tabular offline se genera para la demo operativa, y las trayectorias
`rl_trajectories_10min.csv` conservan tambien las filas nocturnas, el historial
reciente de humedad/temperatura y el acumulado de riego para poder entrenar un
modelo con contexto temporal, por ejemplo una LSTM. No se propone Transformer en
esta fase porque el volumen de datos sigue siendo limitado.

La defensa tecnica es: el componente energetico se deriva del historico
sensorizado, mientras que el componente agricola usa reglas expertas
referenciadas hasta disponer de etiquetas reales de salud, biomasa o rendimiento
del cultivo. Antes de automatizar riego, sombreado o manejo de cultivo deben
validarse los umbrales con el cliente o un especialista agricola.

## Diferencia con el pipeline 6h

La version 6h agrega la operacion en franjas muy amplias y es mas estable para
una demo conservadora. La version 10 min conserva los cambios rapidos de angulo,
radiacion y microclima, por lo que puede generar reglas mas dinamicas y
sensibles al contexto.

Para produccion, esta rama deberia validarse con criterios agronomicos y con un
suavizado de recomendaciones antes de actuar sobre trackers reales.
