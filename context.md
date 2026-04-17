# Contexto del proyecto: Sistemas Agrovoltaicos Dinámicos

## Descripción general
Estoy trabajando en un proyecto académico/profesional centrado en el análisis y optimización operativa de **sistemas agrovoltaicos dinámicos**. El proyecto parte de unos vídeos de presentación del cliente/stakeholders y de un acta de constitución ya definida.

La idea central es que las placas solares **no son estáticas**, sino que tienen **eje de rotación** y pueden moverse automáticamente. Ese movimiento afecta no solo a la **producción energética**, sino también al **microclima del cultivo** situado debajo de las placas.

Por tanto, el proyecto **no consiste solo en maximizar energía**, sino en encontrar un **equilibrio dinámico entre producción energética y condiciones favorables para el cultivo**.

---

## Organización y contexto institucional
La organización patrocinadora es **Sostenibilidad y Ciencia**, una entidad centrada en generar conocimiento aplicado para acelerar la transición ecológica sin comprometer la competitividad económica ni el bienestar social.

Sus áreas estratégicas son:
1. Energía y transición energética
2. Sistemas agroalimentarios sostenibles
3. Digitalización aplicada a la gestión ambiental

Su cultura se basa en:
- toma de decisiones basada en datos
- orientación a impacto real
- transformación de datos en decisiones operativas

---

## Nombre del proyecto
**Análisis y Optimización Operativa de Sistemas Agrovoltaicos Dinámicos**

---

## Misión del proyecto
**Optimizar simultáneamente la producción energética y el equilibrio microclimático del cultivo.**

---

## Problema que resuelve el proyecto
En los sistemas agrovoltaicos dinámicos, la rotación de los paneles afecta al mismo tiempo a:

- la **producción energética**
- el **microclima agrícola**
- potencialmente, el **rendimiento del cultivo**

Optimizar únicamente la energía puede perjudicar variables clave del cultivo, como:
- radiación disponible
- temperatura del suelo
- humedad del suelo
- equilibrio hídrico
- estrés térmico

Además, aunque existen datos históricos de sensores, actualmente **no hay un sistema que transforme esos datos en decisiones operativas claras**.

---

## Objetivo principal
Diseñar, desarrollar e implementar un **sistema de soporte a la decisión semi-automatizado** que, mediante un **modelo multiobjetivo basado en datos históricos**, permita:

- optimizar simultáneamente la producción energética y el equilibrio microclimático del cultivo
- generar recomendaciones operativas automáticas de rotación
- supervisar el movimiento automático de las placas y su control operativo
- desplegar la solución en el entorno del cliente con un esquema definido de mantenimiento y soporte técnico

---

## Qué se espera construir
Se espera construir una solución compuesta por:

1. **Pipeline de datos reproducible**
   - limpieza
   - integración
   - sincronización temporal
   - tratamiento de nulos
   - documentación

2. **Análisis exploratorio riguroso (EDA)**
   - detección de patrones
   - correlaciones entre rotación, energía y microclima
   - identificación de no linealidades
   - detección de umbrales críticos
   - análisis de efectos retardados (lag effects)

3. **Modelo de decisión multiobjetivo**
   - reglas operativas de rotación
   - equilibrio energía-cultivo
   - validación conceptual con criterio agronómico

4. **Sistema de monitorización y control operativo**
   - seguimiento del ángulo de las placas
   - supervisión del movimiento automático
   - detección de anomalías
   - alertas configurables

5. **Dashboard interactivo**
   - visualización del estado del sistema
   - indicadores clave
   - sugerencias operativas
   - trazabilidad de eventos y alertas

---

## Datos disponibles
Se dispone de aproximadamente **10 datasets CSV**, integrables mediante la variable temporal `Time`.

### Variables energéticas / fotovoltaicas
- ángulo de rotación
- irradiancia (GPOA, Albedo)
- temperatura de panel
- grado de insolación

### Variables agrícolas / microclimáticas
- ePAR
- VWC (contenido volumétrico de agua del suelo)
- temperatura del suelo
- humedad superficial

### Variables atmosféricas / meteorológicas
- temperatura del aire
- humedad relativa
- punto de rocío
- precipitación

### Características del dataset
- datos históricos de **6 meses a 1 año**
- frecuencias heterogéneas:
  - algunos registros cada 10 minutos
  - otros horarios
- presencia potencial de:
  - valores NA
  - desfases temporales
  - distintas resoluciones
  - datos meteorológicos no completamente depurados

---

## Contexto técnico del experimento
Se han probado distintos algoritmos de rotación de paneles, entre ellos:
- seguimiento solar completo
- seguimiento parcial
- posiciones fijas en determinadas franjas

El objetivo inicial del experimento era estudiar la eficiencia energética, pero se observó que el **microclima bajo las placas cambia significativamente según la orientación y el momento del día**.

---

## Idea científica clave
Los cultivos **no responden de forma lineal**.

No siempre se cumple:
- más sol = mejor
- más sombra = peor

Existen:
- **umbrales**
- **efectos acumulativos**
- **efectos retardados**

Por ello, el sistema debe evitar el error de optimizar una sola variable. El proyecto debe modelar un **equilibrio dinámico entre electricidad y cultivo**.

---

## KPIs / resultados esperados
- Limpieza e integración exitosa de los 10 datasets mediante `Time`
- Identificación de correlaciones clave entre rotación/ángulo, irradiancia y microclima
- Definición de al menos **3 reglas operativas** validadas conceptualmente
- Identificación de umbrales críticos en **ePAR** y **VWC**
- Propuesta de un **índice combinado Energía–Cultivo**
- Dashboard funcional con sugerencias operativas automáticas
- Capacidad de monitorización, alertas y registro histórico de eventos

---

## Índice combinado Energía–Cultivo
Una parte importante del proyecto es definir un **índice combinado** que ayude a evaluar el equilibrio operativo entre:
- eficiencia energética
- protección/estabilidad del cultivo

Ese índice no debe centrarse solo en la energía, sino incorporar explícitamente variables agrícolas y microclimáticas.

---

## Alcance del proyecto (In Scope)
- integración temporal de datasets
- limpieza y tratamiento de valores nulos
- sincronización de series temporales
- análisis exploratorio cruzado
- identificación de patrones, umbrales y efectos retardados
- definición de reglas operativas de rotación
- desarrollo del dashboard
- monitorización del sistema
- detección de anomalías
- sistema de alertas
- despliegue conceptual/funcional en entorno cliente
- soporte técnico y esquema de mantenimiento

---

## Fuera de alcance (Out of Scope)
- calibración física del hardware de sensores
- validación técnica del hardware
- evaluación económica completa de la planta
- modelos meteorológicos predictivos avanzados
- evaluación directa del rendimiento agrícola final
- experimentación agronómica completa fuera de los proxies disponibles

---

## Riesgos clave del proyecto
Los principales riesgos a tener presentes son:

1. **Calidad y continuidad de los datos**
   - valores NA
   - inconsistencias
   - falta de datos suficientes

2. **Desalineación temporal entre sensores**
   - distintas frecuencias
   - agregación incorrecta
   - pérdida de información relevante

3. **No linealidad y efectos retardados no capturados**
   - relaciones complejas entre rotación y variables agrícolas

4. **Sesgo hacia la optimización energética**
   - riesgo de perjudicar el cultivo

5. **Sobreajuste al histórico disponible**
   - baja generalización a otras condiciones

6. **Fallo en el pipeline o en la ingesta**
   - datos incompletos
   - dashboard desactualizado
   - recomendaciones erróneas

7. **Privacidad y seguridad de los datos operativos**
   - cifrado en tránsito y reposo
   - control RBAC
   - cumplimiento RGPD
   - NDA para acceso a datos

---

## Stakeholders relevantes
- **Sponsor ejecutivo:** Carla González
- **Responsable técnica de datos/energía:** Eva Jackson
- **Especialista agrícola del experimento:** perfil orientado a fisiología vegetal/agronomía
- **Director del proyecto / equipo:** Daniel Álvarez / equipo Chacorocalfarobar
- **Usuarios finales:** analistas y operadores de la planta agrovoltaica

---

## Enfoque deseado al ayudarme con este proyecto
Cuando me ayudes con este proyecto, debes tener en cuenta estas reglas:

### 1. No trates el proyecto como solo un problema de machine learning
Es un proyecto de:
- análisis de datos
- soporte a la decisión
- control operativo
- digitalización aplicada
- optimización multiobjetivo

### 2. No optimices solo energía
Siempre debes considerar el equilibrio entre:
- producción energética
- microclima del cultivo
- lógica agronómica

### 3. Prioriza propuestas accionables
Las soluciones deben poder traducirse a:
- reglas operativas
- visualizaciones útiles
- dashboards
- recomendaciones claras
- alertas o monitorización

### 4. Ten en cuenta la automatización y el control industrial
El sistema no solo recomienda; también debe:
- supervisar el movimiento automático de las placas
- contemplar lógica de control operativo
- detectar anomalías
- facilitar seguimiento en tiempo real

### 5. Cuando propongas análisis, prioriza
- EDA riguroso
- análisis temporal
- correlaciones cruzadas
- lag analysis
- segmentación por tipo de algoritmo de rotación
- detección de umbrales
- relaciones no lineales
- comparación entre estrategias de rotación

### 6. Cuando propongas dashboards o presentaciones
Debes priorizar:
- claridad visual
- poco texto
- foco en decisiones
- enfoque profesional/consultoría
- mensajes claros para stakeholders técnicos y no técnicos

---

## Tipo de ayuda que necesito del agente
Quiero que el agente me ayude a:
- redactar documentación técnica y académica
- preparar presentaciones
- proponer estructura de slides
- definir análisis exploratorios útiles
- traducir objetivos a entregables concretos
- redactar riesgos, alcance, metodología y KPIs
- diseñar dashboards conceptuales
- convertir ideas complejas en mensajes claros para exponer
- ayudarme a justificar decisiones del proyecto de forma profesional

---

## Estilo de respuesta deseado
- Responde en **español**
- Sé **claro, técnico y directo**
- Prioriza contenido **útil para presentación o informe**
- Evita relleno y explicaciones genéricas
- Si propones algo, que esté alineado con el proyecto real
- Si detectas que una idea está demasiado enfocada a energía y olvida cultivo, corrígelo
- Si una propuesta suena poco accionable, tradúcela a decisiones, reglas o entregables concretos

---

## Resumen ejecutivo en una frase
Proyecto orientado a transformar datos históricos de sensores agrovoltaicos en un sistema inteligente de análisis, supervisión y decisión operativa que equilibre producción energética y microclima del cultivo.