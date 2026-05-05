# Pipeline experimental a 10 minutos

Esta rama mantiene el pipeline de 6 horas como backup y anade una alternativa
experimental basada directamente en `sprint3/outputs/master_dataset.csv`, que
tiene resolucion de 10 minutos.

## Idea

- Fuente granular: `outputs/master_dataset.csv`.
- Vista de modelizacion: `outputs_10min/dataset_modelizacion_10min.csv`.
- Reglas candidatas: `outputs_10min/candidate_rotation_rules_10min.csv`.
- Backup estable: `outputs_10min/backup_6h/`.

El objetivo es demostrar como cambiarian las reglas si el sistema reaccionara a
datos mas frecuentes de la planta, sin perder la version 6h como referencia.

## Ejecucion

Desde la raiz del repositorio:

```bash
cd sprint3
source .venv/bin/activate
python build_10min_pipeline.py
```

El comando genera:

- `outputs_10min/dataset_modelizacion_10min.csv`
- `outputs_10min/candidate_rotation_rules_10min.csv`
- `outputs_10min/pipeline_10min_metadata.json`
- `outputs_10min/backup_6h/dataset_modelizacion_6h.csv`
- `outputs_10min/backup_6h/candidate_rotation_rules.csv`

## Diferencia con el pipeline 6h

La version 6h agrega la operacion en franjas muy amplias y es mas estable para
una demo conservadora. La version 10 min conserva los cambios rapidos de angulo,
radiacion y microclima, por lo que puede generar reglas mas dinamicas y
sensibles al contexto.

Para produccion, esta rama deberia validarse con criterios agronomicos y con un
suavizado de recomendaciones antes de actuar sobre trackers reales.
