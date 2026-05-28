# Respuesta a licitacion: Data Augmentation and Decision Support System

## Mensaje principal

El proyecto ya no se presenta solo como un dashboard, sino como un prototipo de sistema de ayuda a la decision para agri-PV. Combina datos reales del piloto, reglas agronomicas comprensibles, un modelo temporal tipo gemelo digital y una politica DQN que recomienda angulo, placas y riego.

El resultado numerico que podemos defender ahora es una estimacion offline: al aplicar la politica DQN sobre 23.043 registros comparables, el indice energia-cultivo sube de 0,258 a 0,320, una mejora del 24,19%. El reward multiobjetivo sube de 0,322 a 0,519, una mejora del 61,52%. Es una validacion historica, no una prueba experimental en campo.

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

| Semana | Trabajo | Entregable |
| --- | --- | --- |
| 1 | Cerrar contrato de datos, variables, restricciones y criterios de seguridad. | Documento de variables, restricciones y API de datos. |
| 2-3 | Calibrar modelo biologico y robustecer gemelo digital. | Gemelo digital validado con historico y primeras metricas de error. |
| 4-5 | Crear modulo Data Augmentation y comparador DSS biologico vs data-driven. | Generador de escenarios y vista de comparacion de modelos. |
| 6-7 | Integrar DSS con control del piloto en modo sombra. | API de recomendaciones, limites de seguridad y pruebas en seco. |
| 8 | Validacion, documentacion, transferencia y cierre. | Informe final, demo, manual de uso y plan de despliegue. |

## Organizacion del trabajo

- IA y datos: DQN, reward, validacion offline, Data Augmentation y metricas.
- Modelado agronomico: variables biologicas, umbrales, restricciones y lectura de riesgo.
- Software e integracion: dashboard, API, datos vivos, conectores y pruebas.
- Validacion de piloto: modo sombra, comparacion historica, pruebas en campo y criterios de aceptacion.
- Gestion: seguimiento semanal, riesgos, presupuesto y coordinacion con la empresa.

## Presupuesto orientativo

| Partida | Importe |
| --- | ---: |
| Personal tecnico y agronomico | 30.000 EUR |
| Infraestructura cloud/datos | 2.000 EUR |
| Integracion piloto y validacion | 3.500 EUR |
| Documentacion, formacion y transferencia | 1.500 EUR |
| Contingencia 10% | 3.700 EUR |
| **Total sin IVA** | **40.700 EUR** |

Supuestos: 8 semanas de trabajo, equipo reducido, sin compra de sensores ni actuadores nuevos, y disponibilidad tecnica de la planta piloto para integrar datos y control.

## Guion corto para la presentacion

La licitacion pide tres cosas: entender el sistema biologico, simularlo y tomar mejores decisiones. Nuestro trabajo ya cubre la base: hemos identificado variables agronomicas y energeticas, hemos creado un dashboard de decision y hemos entrenado una politica DQN que recomienda acciones de placas y riego.

La mejora que podemos cuantificar hoy es offline: en 23.043 registros historicos, nuestro sistema mejora el indice energia-cultivo un 24,19% y el reward multiobjetivo un 61,52% respecto a las decisiones historicas. Esto no sustituye una prueba en campo, pero demuestra que hay margen real de optimizacion.

Para completar la licitacion faltan tres pasos claros: formalizar el comparador entre modelo biologico y modelo data-driven, convertir los escenarios sinteticos en un modulo de Data Augmentation reutilizable y conectar el DSS al control real del piloto en modo seguro. Proponemos hacerlo en 8 semanas, con un presupuesto orientativo de 40.700 EUR + IVA.

## Verificacion

La cobertura de licitacion se valida con:

```bash
python3 sprint3/reports/verificar_cobertura_licitacion.py
```

El script comprueba que los apartados i-v tienen estado, evidencia real en el repositorio, mensaje de presentacion, faena pendiente, capacidad de finalizacion y presupuesto.
