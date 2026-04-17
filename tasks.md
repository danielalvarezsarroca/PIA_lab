# Contexto operativo: sprints semanales y tareas del proyecto

## Estructura general del proyecto
El proyecto se organiza en **4 sprints de 1 semana (5 días laborables)**.

Cada sprint sigue esta estructura fija:
1. **Sprint Planning**
2. **Trabajo diario + Daily Standup**
3. **Sprint Review**
4. **Sprint Retrospective**

### Foco de cada sprint
- **Sprint 1:** EDA e insights
- **Sprint 2:** Modelización
- **Sprint 3:** Dashboard v1
- **Sprint 4:** Integración y entrega final

### Entregables principales por sprint
- **Sprint 1:** E01, E02
- **Sprint 2:** E03, E04
- **Sprint 3:** E05
- **Sprint 4:** E06, E07, E08, E09

---

# Entregables/documentación que hay que preparar en CADA sprint
Además del trabajo técnico del sprint, en **cada sprint** hay que preparar un paquete de documentación para entregar en zip.

## Paquete documental recurrente de cada sprint
1. **PowerPoint / presentación**
2. **Plan de Gestión del Proyecto**
3. **Actas de reuniones y evidencias de reunión**
4. **Change Request** (si existe petición de cambio)
5. **Sprint N-1 Review** *(a partir de los sprints posteriores al 1)*
6. **Sprint N-1 Retrospective** *(a partir de los sprints posteriores al 1)*
7. **Seguimiento de presupuesto**
8. **Daily Standup** *(personal y opcional, pero recomendable conservarlo)*
9. **DoD del proyecto**
10. **Informe de lecciones aprendidas**

## Interpretación práctica por sprint
- **Sprint 1:** preparar presentación, plan de gestión, actas, presupuesto, DoD y, si aplica, CR.
- **Sprint 2:** además de lo anterior, adjuntar la **Review y Retrospective del Sprint 1**.
- **Sprint 3:** además de lo anterior, adjuntar la **Review y Retrospective del Sprint 2**.
- **Sprint 4:** además de lo anterior, adjuntar la **Review y Retrospective del Sprint 3** y cerrar el **informe final de lecciones aprendidas**.

---

# Definition of Done (DoD) que aplica a cualquier entregable
Un entregable solo se considera realmente terminado si cumple esto:
- Ha sido revisado por al menos **una persona distinta del autor**
- Si es código, **ejecuta sin errores**
- Si es código, está **comentado** en las funciones principales
- Si es código, está **versionado en repositorio**
- Si es documento, sigue la **plantilla aprobada**
- Incluye **limitaciones y próximos pasos**
- El PM ha actualizado el **Sprint Backlog** a estado *Hecho*
- El cliente/supervisor lo ha aceptado en la **Review** o al menos hay feedback registrado
- Si afecta a riesgos, se ha actualizado el **Registro de Riesgos**

---

# Sprint 1 — EDA e insights
## Objetivo
Comprender la estructura de los datos, detectar patrones iniciales y obtener insights, incluyendo la posible localización de los espacios de investigación.

## Entregables técnicos del sprint
- **E01:** Informe de Análisis Exploratorio (EDA Report)
- **E02:** Notebook / script replicable del EDA

## Backlog del Sprint 1
- Explorar estructura de datos: tipos, nulos, rangos
- Analizar distribución de cada variable y detectar outliers
- Explorar dimensión temporal: tendencias y estacionalidad
- Analizar correlaciones entre variables
- Identificar ubicación geográfica o hipótesis de ubicación a partir de los datos
- Redactar acta de kick-off
- Actualizar registro de riesgos
- Realizar Sprint Review y Retrospective

## Plan semanal recomendado
### Día 1
- Sprint Planning
- Reparto de tareas
- Carga y exploración inicial de datasets
- Revisión de tipos, formatos, nulos y consistencia
- Crear estructura del notebook EDA
- Generar el backlog operativo de la semana

### Día 2
- Análisis de distribuciones
- Detección de outliers y valores extraños
- Primeras visualizaciones
- Revisar si faltan datos críticos para el proyecto

### Día 3
- Análisis temporal por sensor y por variable
- Identificación de tendencias, estacionalidad y huecos temporales
- Revisar sincronización básica de timestamps

### Día 4
- Matriz de correlaciones
- Relaciones entre rotación, variables energéticas y variables microclimáticas
- Hipótesis sobre ubicación de sensores o zonas experimentales
- Empezar redacción del informe E01

### Día 5
- Cierre de E01
- Limpieza y cierre de E02
- Sprint Review con cliente
- Sprint Retrospective
- Actualización del registro de riesgos
- Cierre del paquete documental del sprint

## Documentos que hay que dejar preparados en Sprint 1
- Presentación del sprint
- Plan de gestión actualizado
- Acta de planning / kick-off
- Actas de reuniones celebradas
- E01
- E02
- Seguimiento de presupuesto Sprint 1
- Registro de riesgos actualizado
- DoD aplicado a los entregables
- Daily standups guardados si se hacen
- Change Request solo si aparece uno

---

# Sprint 2 — Modelización y política de rotación
## Objetivo
Desarrollar el modelo o conjunto de reglas que defina la política óptima de rotación de las placas para maximizar simultáneamente generación eléctrica y calidad del cultivo.

## Entregables técnicos del sprint
- **E03:** Informe de política de rotación + modelo
- **E04:** Código del modelo

## Backlog del Sprint 2
- Gestionar el Change Request recibido, si existe
- Definir target y features relevantes
- Preparar dataset de modelización
- Hacer train/test split y normalización si aplica
- Entrenar y evaluar al menos dos enfoques
- Traducir resultados a reglas interpretables
- Redactar informe de política de rotación
- Publicar código del modelo
- Actualizar riesgos y seguimiento de presupuesto
- Review y Retrospective del sprint

## Plan semanal recomendado
### Día 1
- Sprint Planning
- Revisar feedback del Sprint 1
- Si hay cambio solicitado, analizar su impacto y documentarlo
- Definir target y variables relevantes
- Preparar dataset base para modelización

### Día 2
- Limpieza final del dataset de entrenamiento
- Feature engineering
- Normalización, selección de variables y partición train/test
- Documentar decisiones técnicas

### Día 3
- Entrenar al menos dos enfoques de modelización o dos estrategias de generación de reglas
- Comparar resultados
- Validar si el modelo realmente ayuda a definir una política de rotación interpretable

### Día 4
- Extraer reglas interpretables
- Traducir el resultado a una lógica operativa comprensible
- Redactar E03
- Organizar y limpiar E04

### Día 5
- Cierre de E03
- Cierre de E04
- Sprint Review
- Sprint Retrospective
- Actualizar riesgos, presupuesto y backlog
- Cerrar paquete documental

## Documentos que hay que dejar preparados en Sprint 2
- Presentación Sprint 2
- Plan de gestión actualizado
- Actas del sprint
- **Sprint 1 Review**
- **Sprint 1 Retrospective**
- E03
- E04
- Seguimiento de presupuesto Sprint 2
- Registro de riesgos actualizado
- CR documentado, si existe
- DoD revisado
- Daily standups guardados si se hacen

---

# Sprint 3 — Dashboard v1
## Objetivo
Diseñar e implementar la primera versión funcional del dashboard que muestre el estado del sistema agrovoltaico y ofrezca recomendaciones sobre la rotación.

## Entregable técnico del sprint
- **E05:** Dashboard v1 (prototipo funcional)

## Backlog del Sprint 3
- Mostrar estado actual o simulado de sensores clave
- Mostrar series temporales filtrables por sensor o zona
- Integrar recomendación visual del ángulo de rotación óptimo
- Mostrar alertas cuando se superen umbrales críticos
- Documentar decisiones de diseño del dashboard
- Actualizar riesgos y presupuesto
- Review y Retrospective del sprint

## Plan semanal recomendado
### Día 1
- Sprint Planning
- Diseño del wireframe
- Decisión de herramienta (Streamlit / Power BI / Tableau / otra)
- Definir layout del dashboard y flujo de usuario

### Día 2
- Implementación de paneles de estado
- Visualización de variables clave
- Integración de primeras series temporales
- Crear Dashboard v0.5

### Día 3
- Integración del módulo de recomendaciones basado en reglas del Sprint 2
- Añadir filtros por sensor o zona
- Añadir indicadores clave

### Día 4
- Implementar alertas
- Hacer pruebas de usabilidad internas
- Corregir problemas de diseño o rendimiento
- Preparar demo para la Review

### Día 5
- Cierre de E05
- Sprint Review
- Sprint Retrospective
- Actualización de riesgos y presupuesto
- Cerrar paquete documental

## Documentos que hay que dejar preparados en Sprint 3
- Presentación Sprint 3
- Plan de gestión actualizado
- Actas del sprint
- **Sprint 2 Review**
- **Sprint 2 Retrospective**
- E05
- Documento breve de decisiones de diseño del dashboard
- Seguimiento de presupuesto Sprint 3
- Registro de riesgos actualizado
- DoD revisado
- Daily standups guardados si se hacen
- CR si aparece alguno nuevo

---

# Sprint 4 — Integración, refinamiento y entrega final
## Objetivo
Incorporar el feedback de sprints anteriores, completar la versión final del dashboard, producir la documentación técnica completa y preparar la presentación final al cliente.

## Entregables técnicos/finales del sprint
- **E06:** Dashboard v2 final con recomendaciones
- **E07:** Documentación técnica completa
- **E08:** Presentación final al cliente
- **E09:** Documentación de gestión acumulativa

## Backlog del Sprint 4
- Mejorar UX/UI del dashboard
- Añadir funcionalidades pendientes detectadas en reviews previas
- Redactar documentación técnica completa
- Preparar y ensayar presentación final
- Cerrar toda la documentación de gestión
- Realizar presentación final y retrospective de cierre

## Plan semanal recomendado
### Día 1
- Sprint Planning
- Consolidar feedback pendiente
- Priorizar ajustes del dashboard
- Revisar lista completa de entregables finales

### Día 2
- Mejoras de UX/UI
- Cierre funcional del dashboard
- Inicio de E07
- Revisión de reproducibilidad y estructura técnica

### Día 3
- Cierre de E06
- Revisión cruzada de E07
- Verificar que la demo y el dashboard funcionan

### Día 4
- Preparación de E08
- Ensayo interno de presentación
- Reparto de turnos y guion oral
- Revisión final de la documentación de gestión

### Día 5
- Presentación final al cliente
- Retrospective de cierre
- Cierre de E07, E08 y E09
- Redacción final del informe de lecciones aprendidas
- Validación final del archivo zip de entrega

## Documentos que hay que dejar preparados en Sprint 4
- Presentación final
- Plan de gestión actualizado final
- Actas del sprint
- **Sprint 3 Review**
- **Sprint 3 Retrospective**
- E06
- E07
- E08
- E09
- Seguimiento de presupuesto Sprint 4 y total
- Registro de riesgos final
- Informe de lecciones aprendidas
- DoD final revisado
- Daily standups guardados si se hacen
- CR cerrados o trazados si existieron

---

# Roles orientativos por sprint
## PM
- coordina planning, review y retrospective
- redacta actas
- mantiene riesgos
- mantiene presupuesto
- controla backlog y estado de tareas
- consolida documentación de gestión

## Tech Lead / Data Analyst
- lidera EDA
- coordina decisiones técnicas
- apoya interpretación de resultados
- participa en reglas de rotación y documentación

## ML Engineer
- lidera modelización
- define target/features
- evalúa modelos
- traduce resultados a reglas interpretables

## Data Engineer / Dashboard Dev
- integra datos al dashboard
- implementa visualizaciones
- añade alertas y recomendaciones
- refina UX/UI y demo final

---

# Qué debe asumir siempre el agente al ayudarme con sprints
Cuando me ayudes con tareas semanales o sprints de este proyecto, debes asumir que:
- hay que producir **trabajo técnico + documentación de gestión**
- cada sprint tiene una **entrega en zip**
- las actas, riesgos, presupuesto y DoD se deben mantener **actualizados**
- review y retrospective del sprint anterior se adjuntan en sprints posteriores
- el objetivo no es solo “hacer análisis”, sino avanzar hacia entregables reales del sprint
- cualquier propuesta debe poder aterrizarse en:
  - tarea de backlog
  - artefacto del sprint
  - entregable técnico
  - documento para la entrega

---

# Resumen operativo ultracorto
- **Sprint 1:** entender datos y generar EDA
- **Sprint 2:** definir modelo/reglas de rotación
- **Sprint 3:** construir dashboard funcional
- **Sprint 4:** integrar todo, refinar y cerrar entrega final
- **En todos los sprints:** documentación, actas, riesgos, presupuesto, DoD y paquete zip de entrega