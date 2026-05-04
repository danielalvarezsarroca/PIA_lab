# Actualizacion diaria del dataset

Este modulo deja preparado el Sprint 3 para una actualizacion incremental diaria.
La idea operativa es:

1. Recibir datos reales diarios de planta desde sensores/SCADA.
2. Normalizarlos a resolucion de 6 horas.
3. Anadirlos al dataset de modelizacion.
4. Regenerar reglas candidatas de rotacion.
5. Alimentar el dashboard con los CSV actualizados.

## Estado actual del proyecto

Ahora mismo solo se dispone de datos historicos proporcionados para el proyecto.
Por tanto, el pipeline implementa dos modos:

- `sensor_with_demo_fill`: se han recibido algunas columnas reales en `--sensor-csv` y el resto se rellena desde el historico.
- `demo_imputed`: no hay sensores nuevos; todas las variables internas se imputan desde perfiles historicos por hora.

En ambos casos se genera metadata explicita indicando que el flujo es demostrativo
hasta disponer de conexion diaria real con planta.

## Por que no se entrenan conclusiones reales con datos imputados

Variables como `track_mean`, `VWC_S1_mean`, `ePAR_S1_mean` o `IEC` dependen de
sensores/operacion reales. Si se inventan sin marcarlo, el modelo podria producir
reglas aparentemente precisas pero no validas para operacion.

Por eso, este pipeline:

- conserva el contrato tecnico de actualizacion diaria;
- permite una demo end-to-end;
- marca la procedencia en `data_source`, `sensor_status` y `update_note`;
- deja preparada la entrada `--sensor-csv` para sustituir la imputacion por datos reales.

## Ejecucion demo

Desde la raiz del repositorio:

```bash
cd sprint3
source .venv/bin/activate
python update_daily_dataset.py --target-date 2026-05-03
```

Esto crea:

- `outputs_daily/dataset_modelizacion_6h_updated.csv`
- `outputs_daily/candidate_rotation_rules_updated.csv`
- `outputs_daily/daily_update_metadata.json`

## Ejecucion con sensores reales

Cuando exista un CSV diario de sensores:

```bash
python update_daily_dataset.py \
  --target-date 2026-05-03 \
  --sensor-csv path/al/export_scada.csv
```

El CSV de sensores debe incluir `Time` y puede incluir cualquier columna del modelo:

- `track_mean`
- `tracking_regime`
- `VWC_S1_mean`
- `VWC_S2_mean`
- `ePAR_S1_mean`
- `ePAR_S2_mean`
- `Albedo_S1`
- `Albedo_S2`
- `IEC`
- etc.

Las columnas ausentes se rellenan con el perfil historico para mantener el flujo
de demo, pero seguiran marcadas como pendientes de integracion completa.

## Datos externos por coordenadas

Para enriquecer el pipeline, se podria incorporar una fuente externa como
Open-Meteo, NASA POWER o PVGIS para variables meteorologicas y solares por
coordenadas. Esto serviria para temperatura, radiacion, viento o humedad
meteorologica, pero no sustituye sensores internos de planta como VWC real,
ePAR local o angulo real de trackers.
