# Sprint 3 - Agrovoltaic Decision Dashboard

Carpeta del Sprint 3 del proyecto SAMO. Contiene el dashboard agrovoltaico, los modulos de modelado, los datasets generados, los notebooks de exploracion y la documentacion entregable del sprint.

## Estructura

```text
sprint3/
├── README.md                    # Mapa de la carpeta y comandos principales
├── .streamlit/                  # Configuracion de Streamlit al ejecutar desde sprint3/
├── data/                        # CSV normalizados usados para construir el master dataset
├── outputs/                     # Artefactos generados: datasets, metricas, modelo LSTM e imagenes
├── docs/                        # Documentacion tecnica y READMEs especificos
├── meetings/                    # Actas de reunion del sprint
├── notebooks/                   # Notebooks de limpieza, EDA y generacion de datasets
├── reports/                     # Informes PDF entregables
└── src/                         # Aplicacion, modulos reutilizables y tests
    ├── app.py                   # Punto de entrada del dashboard Streamlit
    ├── data_loader.py           # Carga y cache de datos para la app
    ├── alert_logic.py           # Logica de alertas
    ├── rule_engine.py           # Motor de reglas de trackers
    ├── solar_logic.py           # Calculos solares
    ├── styles.py                # Estilos HTML/CSS del dashboard
    ├── svg_generator.py         # Visualizacion SVG del tracker
    ├── core/                    # Modelado, pipelines, reglas agronomicas, RL y LSTM
    ├── tabs/                    # Pestañas del dashboard
    └── tests/                   # Tests unitarios y de integracion
```

## Contenido por carpeta

- `src/core/`: codigo de soporte del sprint que no es interfaz directa del dashboard. Incluye `agricultural_rules.py`, `ten_min_pipeline.py`, `rl_policy.py`, los modulos del world model LSTM y scripts de generacion/entrenamiento.
- `src/tabs/`: componentes de cada pestaña de Streamlit: estado, series temporales, recomendacion, cultivo, simulacion LSTM y alertas.
- `src/tests/`: cobertura automatizada de reglas, dashboard, pipeline 10 min, RL, world model y utilidades.
- `data/`: series CSV limpias por variable fisica, usadas por los notebooks de preparacion.
- `outputs/`: resultados versionados del sprint, incluyendo `master_dataset.csv`, datasets RL, metricas, scalers y pesos del modelo LSTM.
- `docs/`: especificaciones y documentacion tecnica complementaria, incluyendo el pipeline 10 min y el modelo LSTM en tiempo real.
- `notebooks/`: notebooks de EDA, limpieza y construccion de datasets. Estan agrupados aqui para separar exploracion de codigo ejecutable.
- `reports/`: informes PDF finales del sprint.
- `meetings/`: actas de reunion.

## Ejecutar el dashboard

Desde la carpeta `sprint3/`:

```bash
pip install -r src/requirements.txt
streamlit run src/app.py
```

## Ejecutar tests

Desde la raiz del repositorio:

```bash
python -m pytest sprint3/src/tests
```

## Datos externos esperados

El dashboard puede reutilizar salidas del Sprint 2 si no existen los artefactos de 10 minutos en Sprint 3. Esos ficheros se esperan en `../sprint2/outputs_sprint2/`:

| Fichero | Uso |
|---|---|
| `dataset_modelizacion_6h.csv` | Dataset principal de modelizacion a 6 h |
| `dataset_integrado_6h.csv` | Series temporales integradas |
| `candidate_rotation_rules.csv` | Reglas candidatas de rotacion |
| `tracker_variance_diagnostic.csv` | Diagnostico de varianza por tracker |
| `high_iec_policy_table.csv` | Politica para escenarios de IEC alto |
