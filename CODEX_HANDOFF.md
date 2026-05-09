# CODEX HANDOFF - SAMO / PIA_lab

Resumen rapido del estado del proyecto para continuar el trabajo sin perder contexto.

## Objetivo del proyecto

SAMO es un sistema agrovoltaico de monitorizacion y optimizacion. El proyecto combina:

- Analisis historico de sensores de una planta agrovoltaica.
- Modelado de reglas energeticas para orientar placas solares.
- Extension agronomica para proteger cultivos.
- Dashboard Streamlit con estetica tecnologica/minimalista tipo Apple.
- Pipeline experimental a 10 minutos para alimentar un modelo RL y generar reglas.

## Estado actual de ramas y worktrees

- Workspace principal:
  `/Users/joelalfaro/Documents/UPC/Q6/PIA/PIA_lab`
  Rama actual: `codex/sprint3-10min-pipeline`
  Enfoque: pipeline de 10 minutos, masterdataset, reglas energeticas/agronomicas y documentacion de fuentes.

- Dashboard:
  Integrado dentro de esta rama en `sprint3/app.py` junto con sus modulos auxiliares.

- Repositorio remoto usado:
  `https://github.com/danielalvarezsarroca/PIA_lab.git`

- Importante:
  El workspace principal ya contiene el dashboard autocontenido en `sprint3/`.

## Estructura principal

### Raiz del repo

- `data/`
  Datos historicos originales de sensores: irradiancia, temperatura, humedad, ePAR, VWC, angulos de tracking, etc.

- `sprint1/`
  EDA, localizacion, notebooks, graficos e informes iniciales.

- `sprint2/`
  Modelizacion original con resolucion de 6 horas.
  Incluye dataset modelizado, reglas candidatas, arbol de decision, metricas y visualizaciones.

- `sprint3/`
  Sprint actual de integracion:
  - masterdataset
  - pipeline 10 minutos
  - RL
  - reglas energeticas
  - reglas agronomicas
  - perfiles de cultivo

- `docs/superpowers/`
  Specs y planes de implementacion generados durante el trabajo.

## Archivos clave de sprint3

En el workspace principal:

- `sprint3/build_10min_pipeline.py`
  Construye el pipeline experimental a 10 minutos.

- `sprint3/ten_min_pipeline.py`
  Logica base para adaptar/generar datos de 10 minutos.

- `sprint3/agricultural_rules.py`
  Reglas agronomicas demo con umbrales por cultivo.

- `sprint3/README_pipeline_10min.md`
  Explicacion del pipeline, entradas, salidas y limitaciones.

- `sprint3/outputs/master_dataset.csv`
  Masterdataset base.

- `sprint3/outputs/rl_factored_dataset.csv`
  Dataset factorizado para RL.

- `sprint3/outputs_10min/dataset_modelizacion_10min.csv`
  Dataset experimental a 10 minutos.

- `sprint3/outputs_10min/candidate_rotation_rules_10min.csv`
  Reglas energeticas candidatas a 10 minutos.

- `sprint3/outputs_10min/agricultural_rules_10min.csv`
  Reglas agronomicas demo.

- `sprint3/outputs_10min/crop_risk_10min.csv`
  Riesgo agronomico por instante/cultivo.

- `sprint3/outputs_10min/crop_profiles.json`
  Perfiles de cultivo: lechuga, brocoli y generico horticola.

- `sprint3/outputs_10min/backup_6h/`
  Backup estable del pipeline anterior a 6 horas.

Dashboard integrado en `sprint3/`:

- `sprint3/app.py`
  App principal Streamlit.

- `sprint3/rl_policy.py`
  Politica RL / decision de acciones.

- `sprint3/svg_generator.py`
  Visualizacion SVG de placas, sol, sombra y cultivo.

- `sprint3/data_loader.py`
  Carga de datasets.

- `sprint3/solar_logic.py`
  Calculos solares y comportamiento de placas.

- `sprint3/rule_engine.py`
  Motor de reglas.

- `sprint3/styles.py`
  Estilos del dashboard.

- `sprint3/alert_logic.py`
  Logica de alertas.

## Como ejecutar el pipeline 10 minutos

```bash
cd /Users/joelalfaro/Documents/UPC/Q6/PIA/PIA_lab/sprint3
source .venv/bin/activate
python build_10min_pipeline.py
```

Para probar otro cultivo:

```bash
python build_10min_pipeline.py --crop-type brocoli
```

Cultivos contemplados ahora:

- `lechuga`
- `brocoli`
- `generico_horticola`
- `tomate`
- `cebolla`
- `patata`

## Como ejecutar el dashboard

El dashboard actualizado esta integrado en esta rama:

```bash
cd /Users/joelalfaro/Documents/UPC/Q6/PIA/PIA_lab/sprint3
source .venv/bin/activate
streamlit run app.py
```

Si Streamlit abre otro puerto, usar la URL que indique la terminal, normalmente `http://localhost:8501` o similar.

## Requisito sobre app.py y archivos ejecutables

Al entregar o pedir trabajo a otro agente, dejar muy claro esto:

- `sprint3/app.py` debe existir dentro del repositorio principal y ser el punto de entrada oficial del dashboard.
- La app debe poder ejecutarse con:

```bash
cd /Users/joelalfaro/Documents/UPC/Q6/PIA/PIA_lab/sprint3
source .venv/bin/activate
streamlit run app.py
```

- No debe depender de archivos que solo existan en `/private/tmp/pia_dashboard_main`.
- Si se integra codigo del worktree del dashboard, copiar tambien todos los modulos que `app.py` importa, por ejemplo:
  - `data_loader.py`
  - `rl_policy.py`
  - `svg_generator.py`
  - `solar_logic.py`
  - `rule_engine.py`
  - `styles.py`
  - `alert_logic.py`
  - cualquier carpeta auxiliar usada por la app, como `tabs/`, `assets/`, `outputs/` u otras.
- El objetivo no es solo copiar `app.py`, sino dejar el paquete completo autocontenido dentro de `sprint3/`.
- Despues de integrar, probar siempre `streamlit run app.py` desde `sprint3/` y verificar que no aparecen errores de imports ni rutas absolutas rotas.

## Decisiones de diseno/modelado

- El pipeline de 10 minutos es experimental y se mantiene el de 6 horas como backup.
- La parte energetica usa datos historicos reales de sensores.
- La parte agronomica no tiene etiquetas reales de salud, biomasa o rendimiento del cultivo, asi que se modela como reglas expertas referenciadas.
- Las reglas agronomicas deben explicarse como una demo defendible hasta integrar sensores reales de cultivo.
- El pipeline esta pensado para recibir datos reales diarios desde sensores/SCADA, aunque ahora se usa imputacion/prediccion demo.
- Open-Meteo se puede usar como enriquecimiento meteorologico externo.
- Coordenadas recibidas del usuario:
  `41º17'16.4"N 2º02'38.2"E`
  Aproximacion decimal: `41.287889, 2.043944`
  Validar coordenadas exactas antes de defenderlo como dato final.

## Acciones modelizables actualmente

Energeticas / placas:

- mover angulo de placas
- aumentar sombreado
- reducir sombreado
- posicion segura
- mantener placas

Agronomicas:

- activar riego
- pausar riego
- riego preventivo
- alerta de frio
- manejo de sombreado para proteger cultivo

Acciones como poda son interesantes, pero solo deberian mostrarse si estan justificadas por variables disponibles o como recomendacion no automatica. Ahora mismo son menos defendibles que riego/sombreado/frio porque el dataset no contiene variables directas de crecimiento vegetal o fenologia.

## Pendientes importantes

1. Mantener la rama de integracion limpia.
   El dashboard ya esta integrado con el pipeline de `codex/sprint3-10min-pipeline`; faltaria revisar si se quiere abrir PR o mergear a la rama de entrega.

2. Mantener seleccion de un solo cultivo.
   El usuario decidio que solo se planta una cosa a la vez. Al cambiar cultivo, deben recalcularse umbrales, reward RL, recomendaciones y dashboard.

3. Separar acciones energeticas y agronomicas.
   No mostrar todo en un unico texto ambiguo. Debe verse claramente:
   - accion energetica: placa, angulo, sombra
   - accion agronomica: riego, frio, sombreado, etc.

4. Mejorar visualizacion general.
   Mostrar la sombra que genera la placa y el efecto de cada accion. Ya se pidieron animaciones para riego y acciones agronomicas.

5. Confirmar que el dashboard usa realmente el modelo RL.
   El usuario quiere que el RL se use tanto a nivel energetico como agronomico, no solo reglas estaticas.

6. Hacer que el riego aparezca en algunos casos.
   Ajustar rewards/umbrales para que, con ciertos cultivos y condiciones criticas, el RL active riego de forma visible en la demo.

7. Integrar Open-Meteo como complemento opcional.
   Usar las coordenadas exactas para traer temperatura, humedad, viento, radiacion/precipitacion si procede.

8. Documentar claramente demo vs integracion real.
   En README o dashboard debe quedar claro:
   - ahora se imputan/predicen datos como demo
   - en produccion entrarian datos reales de sensores/SCADA
   - las reglas agronomicas se basan en bibliografia/umbrales expertos hasta tener labels reales

9. Limpiar archivos generados antes de commit.
   Hay `.DS_Store`, `__pycache__`, `streamlit.log` y otros no trackeados. Revisar antes de borrar o commitear.

10. Verificar todo antes de merge.
    Ejecutar tests, pipeline y dashboard smoke test.

## Comandos de verificacion

Desde el workspace principal:

```bash
cd /Users/joelalfaro/Documents/UPC/Q6/PIA/PIA_lab
git status --short
cd sprint3
source .venv/bin/activate
python build_10min_pipeline.py
pytest tests
```

Dashboard integrado:

```bash
cd /Users/joelalfaro/Documents/UPC/Q6/PIA/PIA_lab/sprint3
source .venv/bin/activate
streamlit run app.py
```

## Riesgos / cosas a vigilar

- No mezclar el dashboard antiguo con el dashboard bueno.
  El dashboard bueno queda integrado en esta rama; si se hace merge manual, comparar antes para no pisar `sprint3/app.py` ni modulos auxiliares.

- No perder el pipeline de 10 minutos.
  La parte de masterdataset y RL de sprint3 es lo mas importante para la integracion.

- No presentar la agronomia como aprendida de datos reales si no hay labels reales.
  Defenderlo como reglas expertas integradas en reward/decision RL.

- Revisar si `sprint3/tabs/` contiene solo cache o si falta restaurar archivos reales.

- Antes de hacer merge, comparar:
  - `codex/sprint3-10min-pipeline`
  - `codex/sprint3-unificado-rl-dashboard`
  - `main` remoto

## Proximo paso recomendado

1. Revisar visualmente el dashboard con `streamlit run app.py`.
2. Decidir si esta rama se abre como PR o se mergea a la rama de entrega.
3. Si hay tiempo, conectar un enriquecimiento meteorologico real y sustituir progresivamente las imputaciones demo por sensores/SCADA.
4. Documentar en la memoria que el componente agronomico actual es experto/sintetico hasta tener labels reales de rendimiento o salud del cultivo.
