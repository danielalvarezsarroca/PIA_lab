# Sprint 3 — Agrovoltaic Decision Dashboard

Dashboard de monitorización operativa de trackers, cultivo y equilibrio energía-cultivo para el proyecto agrovoltaico SAMO.

## Estructura del repositorio

```
sprint3/
├── src/                          # Código fuente del dashboard
│   ├── .streamlit/
│   │   └── config.toml           # Configuración de Streamlit
│   ├── tabs/                     # Pestañas del dashboard
│   │   ├── tab_alertas.py        # Tab de alertas activas
│   │   ├── tab_estado.py         # Tab de estado general (Dashboard)
│   │   ├── tab_recomendacion.py  # Tab de recomendación de ángulo
│   │   └── tab_series.py         # Tab de series temporales
│   ├── tests/                    # Tests unitarios
│   │   ├── test_alert_logic.py
│   │   ├── test_data_loader.py
│   │   ├── test_rule_engine.py
│   │   ├── test_solar_logic.py
│   │   ├── test_svg_generator.py
│   │   └── test_vwc_thresholds.py
│   ├── app.py                    # Punto de entrada de la aplicación
│   ├── alert_logic.py            # Lógica de detección de alertas
│   ├── data_loader.py            # Carga y caché de datos CSV
│   ├── rule_engine.py            # Motor de reglas de rotación
│   ├── solar_logic.py            # Cálculo de elevación solar
│   ├── styles.py                 # Estilos CSS y componentes HTML
│   ├── svg_generator.py          # Generación de SVG del tracker solar
│   └── requirements.txt          # Dependencias Python
├── actes de reunió/              # Actas de reunión del sprint
│   ├── Acta de reunió 5.pdf
│   └── Acta de reunió 6.pdf
├── E05_Informe_Dashboard_v1.pdf  # Informe técnico del dashboard
├── Gestion_Proyecto_Sprint3.pdf  # Plan de gestión del sprint
└── README.md
```

## Requisitos previos

- Python 3.11
- Los datos del Sprint 2 deben estar en `../sprint2/outputs_sprint2/` relativos a la carpeta `sprint3/`

## Instalación

Desde la carpeta `sprint3/src/`:

```bash
pip install -r requirements.txt
```

## Ejecutar el dashboard

Desde la carpeta `sprint3/`:

```bash
streamlit run src/app.py
```

El dashboard se abrirá en el navegador en `http://localhost:8501`.

## Ejecutar los tests

Desde la carpeta `sprint3/src/`:

```bash
pytest tests/
```

## Datos necesarios

El dashboard lee los siguientes ficheros generados en el Sprint 2:

| Fichero | Descripción |
|---|---|
| `dataset_modelizacion_6h.csv` | Dataset principal con IEC, VWC y ángulos |
| `dataset_integrado_6h.csv` | Dataset integrado para series temporales |
| `candidate_rotation_rules.csv` | Reglas de rotación de trackers |
| `tracker_variance_diagnostic.csv` | Diagnóstico de varianza por tracker |
| `high_iec_policy_table.csv` | Tabla de política para IEC alto |
