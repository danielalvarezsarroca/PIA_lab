# Branch: iec-sensitivity-dashboard

## Objetivo

Esta rama prueba mejoras sobre el dashboard del Sprint 3 y sobre la interpretacion del indice combinado Energia-Cultivo (IEC).

La idea principal es no tratar el IEC como una verdad fija, sino como un indice operativo configurable que permite comparar escenarios con diferentes prioridades:

- equilibrio energia-cultivo
- prioridad energetica
- prioridad agricola/cultivo

## Cambios principales

### 1. Analisis de sensibilidad del IEC

Se ha anadido el script:

```text
sprint3/iec_sensitivity_analysis.py
```

Este script recalcula el IEC con tres escenarios de pesos:

| Escenario | Peso energia | Peso cultivo |
|---|---:|---:|
| Equilibrado | 0.5 | 0.5 |
| Priorizar energia | 0.7 | 0.3 |
| Priorizar cultivo | 0.3 | 0.7 |

Genera dos salidas:

```text
sprint3/outputs_sprint3/iec_sensitivity_by_regime.csv
sprint3/outputs_sprint3/iec_sensitivity_policy_by_hour.csv
```

Estas tablas permiten ver como cambia el IEC y la politica recomendada si se modifica la importancia relativa entre energia y cultivo.

## Resultado observado

El analisis muestra que `TRACKING_PM` sigue siendo el regimen mas fuerte en la franja productiva principal, especialmente a las 12:00.

Resumen interpretativo:

- En modo equilibrado, `TRACKING_PM` mantiene el IEC mas alto.
- Al priorizar energia, `TRACKING_PM` se refuerza todavia mas.
- Al priorizar cultivo, `TRACKING_PM` baja algo, pero sigue siendo competitivo.
- `HORIZONTAL` mejora relativamente cuando se prioriza cultivo, pero no supera a los modos activos en las horas productivas.

Esto sugiere que la conclusion general del Sprint 2 es razonablemente estable, aunque sigue dependiendo de la definicion provisional del IEC.

## Cambios en el dashboard

El dashboard ahora incluye:

- selector de prioridad operativa:
  - `Equilibrado`
  - `Priorizar energia`
  - `Priorizar cultivo`
- recalculo dinamico del IEC segun los pesos elegidos
- slider de hora con pasos de 5 minutos
- simulacion visual de las placas segun hora e IEC ponderado
- visualizacion de incidencia solar hacia los paneles
- comparacion entre:
  - IEC escenario
  - IEC ponderado usado
  - IEC original
  - `energy_score`
  - `crop_score`
- estimacion de confianza historica segun observaciones similares
- reglas candidatas plegadas dentro de un desplegable para reducir ruido visual

## Cambios tecnicos relevantes

Archivos modificados:

```text
sprint3/app.py
sprint3/solar_logic.py
sprint3/svg_generator.py
sprint3/tabs/tab_estado.py
sprint3/tests/test_solar_logic.py
```

Archivos nuevos:

```text
.gitignore
sprint3/iec_sensitivity_analysis.py
sprint3/outputs_sprint3/iec_sensitivity_by_regime.csv
sprint3/outputs_sprint3/iec_sensitivity_policy_by_hour.csv
sprint3/README_iec_sensitivity_dashboard.md
```

## Como ejecutar el analisis

Desde `sprint3`:

```powershell
..\venv\Scripts\python.exe iec_sensitivity_analysis.py
```

## Como ejecutar el dashboard

Desde `sprint3`:

```powershell
..\venv\Scripts\python.exe -m streamlit run app.py
```

Despues abrir la URL que indique Streamlit, normalmente:

```text
http://localhost:8501
```

## Tests

Se han ejecutado los tests del Sprint 3:

```text
36 passed
```

Comando:

```powershell
..\venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```

## Limitaciones

El IEC sigue siendo provisional.

Puntos que deben indicarse en documentacion o presentacion:

- Los pesos energia/cultivo son una decision de negocio o agronomica, no una verdad matematica.
- Los valores objetivo de ePAR, VWC y temperatura del suelo requieren validacion agronomica.
- El dashboard es un sistema de soporte a la decision, no un sistema de control automatico validado.
- La resolucion del dataset de modelizacion es de 6 horas, por lo que las simulaciones de 5 minutos son visuales/interpoladas, no nuevas mediciones reales.
- Las reglas son candidatas interpretables derivadas del Sprint 2 y deben revisarse antes de automatizar decisiones.

## Mensaje recomendado para presentar

El IEC se mantiene como indice operativo interpretable para comparar estrategias energia-cultivo, pero se ha ampliado el dashboard para mostrar sensibilidad ante diferentes prioridades y el nivel de soporte historico de cada recomendacion.
