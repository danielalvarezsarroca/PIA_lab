# Respuesta a licitacion: Data Augmentation and Decision Support System

## Mensaje principal

El proyecto ya no se presenta solo como un dashboard, sino como un prototipo de sistema de ayuda a la decision para agri-PV. Combina datos reales del piloto, reglas agronomicas comprensibles, un modelo temporal tipo gemelo digital y una politica DQN que recomienda angulo, placas y riego.

El resultado numerico que podemos defender ahora es una estimacion offline: al aplicar la politica DQN sobre 23.043 registros comparables, el indice energia-cultivo sube de 0,258 a 0,320, una mejora del 24,19%. El reward multiobjetivo sube de 0,322 a 0,519, una mejora del 61,52%. Es una validacion historica, no una prueba experimental en campo.

## Primera version implementada en codigo

La demo de licitacion ya esta implementada en el dashboard como una pestana propia: `Licitacion DSS`.
El nucleo esta en `sprint3/src/core/licitacion_system.py` y la vista en
`sprint3/src/tabs/tab_licitacion.py`.

La pestana permite mostrar en directo:

- cobertura de los apartados i-v de la licitacion;
- variables y restricciones usadas por el sistema;
- snapshot del gemelo digital con datos historicos reales;
- comparacion entre regla biologica simple y politica DQN;
- escenarios sinteticos basicos para probar sequia, calor, baja radiacion y final de dia;
- primera propuesta de ley de control con modo supervisado y limites de seguridad.

## Que podemos responder ya

| Apartado de licitacion | Estado | Que tenemos hoy | Como explicarlo |
| --- | --- | --- | --- |
| i. Variables y restricciones biologicas | Cubierto | Variables de humedad, temperatura, luz, meteorologia, angulo, riego y restricciones agronomicas en `agricultural_rules.py` y `ESPECIFICACIO_REG_AUTOMATIC_MDP.md`. | Sabemos que variables mira el sistema y que limites agronomicos no debe romper. |
| ii. Gemelo digital y acceso a datos | Parcial | World model LSTM, inferencia temporal, simulacion en dashboard y datasets historicos en `sprint3/outputs`. | Ya hay prototipo data-driven; falta conectarlo a datos vivos del piloto. |
| iii. DSS para comparar modelo biologico y data-driven | Parcial | Reglas agronomicas + DQN + dashboard + validacion offline. | Ya recomienda acciones; falta una vista explicita de acuerdos y desacuerdos entre modelos. |
| iv. Datos sinteticos para acelerar entrenamiento | Parcial | Escenarios de riego, dosis, intervalos y jitter documentados para generar situaciones alternativas. | Ya existe la base de escenarios; falta empaquetarla como modulo reusable para futuros cultivos. |
| v. Conexion con control agri-PV | Planificado | La politica ya produce acciones operativas: siguiente angulo objetivo, accion de placas y riego. | Falta API/PLC, modo sombra, limites de seguridad y validacion en planta piloto. |

## Faena restante y capacidad

- Modelo biologico formal: completar calibracion por cultivo, bibliografia y validacion de campo. Capacidad alta porque las reglas ya estan separadas del DQN.
- Gemelo digital operativo: pasar de CSV historico a API o stream del piloto. Capacidad media-alta porque la inferencia LSTM ya existe.
- Comparador DSS: anadir pantalla de acuerdo/desacuerdo entre reglas biologicas y DQN, con variables que mas influyen. Capacidad alta porque ambos bloques ya generan salidas separadas.
- Data Augmentation: convertir escenarios actuales en modulo configurable por cultivo, clima, estacion y restricciones. Capacidad media porque hay base tecnica, pero falta producto final.
- Control real: conectar recomendaciones al sistema de placas/riego con limites de seguridad, modo sombra y autorizacion humana. Capacidad media porque depende de acceso tecnico al piloto.

## Plan temporal propuesto

| Semana | Work package | Entregable |
| --- | --- | --- |
| 1 | WP1 - Variables biologicas y restricciones | Catalogo agronomico, matriz de variables y criterios de comparacion. |
| 2 | WP2 - Data augmentation | Modulo sintetico reproducible: interpolacion, riego simulado y escenarios basicos. |
| 3 | WP3 - Gemelo digital offline | Simulador inicial con world model, metricas de ajuste y separacion real/sintetico. |
| 4 | WP4 - DSS comparativo | Vista cliente que compara modelo biologico, DQN y explicacion de discrepancias. |
| 5 | WP5 + QA - Integracion supervisada | Demo final, especificacion de control seguro, validacion y documentacion. |

## Organizacion del trabajo

- IA y datos: DQN, reward, validacion offline, Data Augmentation y metricas.
- Modelado agronomico: variables biologicas, umbrales, restricciones y lectura de riesgo.
- Software e integracion: dashboard, API, datos vivos, conectores y pruebas.
- Validacion de piloto: modo sombra, comparacion historica, pruebas en campo y criterios de aceptacion.
- Gestion: seguimiento semanal, riesgos, presupuesto y coordinacion con la empresa.

## Presupuesto propuesto de continuidad

| Bloque | Importe |
| --- | ---: |
| Modelos biologicos y restricciones agronomicas | 3.000 EUR |
| Modulo de datos sinteticos y data augmentation | 4.000 EUR |
| Gemelo digital y world model | 5.000 EUR |
| DSS comparativo y dashboard cliente | 5.000 EUR |
| Integracion con datos reales y control agri-PV | 5.500 EUR |
| Validacion piloto y QA | 2.500 EUR |
| Gestion de proyecto y documentacion | 2.000 EUR |
| Contingencia tecnica | 1.500 EUR |
| **Total continuidad licitacion** | **28.500 EUR** |
| Coste acumulado prototipo SAMO | 35.860 EUR |
| **Total programa completo** | **64.360 EUR** |

Supuestos: continuidad intensiva de 5 semanas desde el prototipo SAMO actual, sin compra de sensores ni actuadores nuevos, integracion real primero en modo observador/supervisado, y validacion dependiente de disponibilidad de planta piloto y apoyo agronomico.

## Guion corto para la presentacion

La licitacion pide tres cosas: entender el sistema biologico, simularlo y tomar mejores decisiones. Nuestro trabajo ya cubre la base: hemos identificado variables agronomicas y energeticas, hemos creado un dashboard de decision y hemos entrenado una politica DQN que recomienda acciones de placas y riego.

La mejora que podemos cuantificar hoy es offline: en 23.043 registros historicos, nuestro sistema mejora el indice energia-cultivo un 24,19% y el reward multiobjetivo un 61,52% respecto a las decisiones historicas. Esto no sustituye una prueba en campo, pero demuestra que hay margen real de optimizacion.

Para completar la licitacion faltan tres pasos claros: formalizar el comparador entre modelo biologico y modelo data-driven, convertir los escenarios sinteticos en un modulo de Data Augmentation reutilizable y conectar el DSS al control real del piloto en modo seguro. Proponemos hacerlo en 5 semanas, con una continuidad estimada de 28.500 EUR desde el prototipo actual. Si se presenta como programa completo, el total es 64.360 EUR al sumar los 35.860 EUR ya ejecutados.

## Verificacion

La cobertura de licitacion se valida con:

```bash
python3 sprint3/reports/verificar_cobertura_licitacion.py
```

El script comprueba que los apartados i-v tienen estado, evidencia real en el repositorio, mensaje de presentacion, faena pendiente, capacidad de finalizacion y presupuesto.
