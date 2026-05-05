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

El comando genera:

- `outputs_10min/dataset_modelizacion_10min.csv`
- `outputs_10min/candidate_rotation_rules_10min.csv`
- `outputs_10min/crop_risk_10min.csv`
- `outputs_10min/agricultural_rules_10min.csv`
- `outputs_10min/crop_profiles.json`
- `outputs_10min/pipeline_10min_metadata.json`
- `outputs_10min/backup_6h/dataset_modelizacion_6h.csv`
- `outputs_10min/backup_6h/candidate_rotation_rules.csv`

## Acciones agronomicas modelables

Con las variables actuales se generan recomendaciones para:

- `regar`: VWC por debajo del umbral de confort.
- `pausar_riego`: VWC alto o lluvia reciente.
- `riego_preventivo`: deficit hidrico combinado con calor.
- `aumentar_sombreado`: estres termico o radiacion excesiva.
- `reducir_sombreado`: PAR baja sin estres termico ni lluvia.
- `posicion_segura`: viento elevado.
- `alerta_frio`: temperatura de suelo demasiado baja.

Estas reglas son interpretables y utiles para la demo, pero sus umbrales son
perfiles aproximados para `lechuga`, `brocoli` y `generico_horticola`. Antes de
automatizar riego, sombreado o manejo de cultivo deben validarse con el cliente
o un especialista agricola.

## Diferencia con el pipeline 6h

La version 6h agrega la operacion en franjas muy amplias y es mas estable para
una demo conservadora. La version 10 min conserva los cambios rapidos de angulo,
radiacion y microclima, por lo que puede generar reglas mas dinamicas y
sensibles al contexto.

Para produccion, esta rama deberia validarse con criterios agronomicos y con un
suavizado de recomendaciones antes de actuar sobre trackers reales.
