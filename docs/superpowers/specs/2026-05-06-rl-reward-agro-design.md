# Diseño: Reward RL con IEC + penalización agronómica

## Objetivo

Definir un reward para la política RL que mantenga el equilibrio energía-cultivo usando IEC como base (coherente con sprint 2) y aplique una penalización fuerte cuando exista riesgo de daño agronómico según umbrales por cultivo referenciados.

## Alcance

Incluye:
- Definición formal del reward.
- Regla de penalización por daño agronómico.
- Umbrales por cultivo basados en fuentes ya integradas.
- Trazabilidad en metadatos de la política RL.

Fuera de alcance:
- Entrenamiento RL online o simulador causal.
- Validación agronómica experimental.

## Variables y fuentes

Variables ya disponibles en el pipeline 10 min:
- `IEC`, `energy_score`, `crop_health_score`.
- `crop_risk_score`, `stress_type`.
- `Tair_WS`, `Tsoil_S1_mean`, `VWC_S1_mean`, `ePAR_S1_mean`, `ePAR_R1_mean`, `wind_speed_kmh`, `precip_intensity_mm10min`.

Fuentes referenciadas (ya presentes en `agricultural_rules.py`):
- FAO-56 (marco hídrico).
- RuralCat (recomendaciones de riego).
- Illinois Extension (lechuga).
- Oregon State Extension (brócoli).
- UMN Extension (riego con sensores).

## Definición del reward

Reward base:

- `reward_base = IEC`.
- IEC = `0.5*energy_score + 0.5*crop_health_score`.

Penalización por daño:

- `reward = reward_base - penalty_damage`.
- `penalty_damage` se activa cuando el cultivo entra en daño agronómico.

Definición de daño:

- Daño se considera cuando se cumple cualquiera de:
  - Déficit hídrico crítico (VWC por debajo de umbral crítico del cultivo).
  - Exceso hídrico crítico (VWC por encima de umbral crítico o lluvia intensa).
  - Estrés térmico crítico (Tair/Tsoil por encima del umbral crítico del cultivo).
  - Frío crítico (Tsoil por debajo del umbral de frío).
  - Radiación excesiva crítica (PAR relativa alta combinada con estrés térmico o déficit hídrico).

Penalización propuesta:

- Penalización fija: `penalty_damage = 0.35` cuando hay daño.
- Variante progresiva (opcional):
  - `penalty_damage = 0.35 + 0.10*(crop_risk_score - umbral_dano)` acotada a [0.35, 0.6].

## Umbrales por cultivo

Se definen a partir de `CROP_PROFILES` existentes.

Ejemplos de parámetros usados por cultivo:
- `vwc_critical_low` / `vwc_critical_high`.
- `air_temp_critical_high_c`.
- `soil_temp_critical_high_c`.
- `soil_temp_warn_low_c`.
- `par_fraction_high`.
- `rain_pause_mm10min`.

El umbral de daño se define como una condición booleana compuesta con estos límites. No se añade un número nuevo si no es necesario; se usa la condición crítica ya definida por cultivo.

## Impacto esperado en la política

- La política sigue maximizando IEC, pero evita estados con daño agronómico.
- Se preserva la interpretabilidad: se puede explicar la penalización en términos de umbrales agronómicos documentados.

## Trazabilidad

En `rl_policy_metadata.json` se incluirá:

- `reward_base: IEC`.
- `penalty_rule: daño agronómico por cultivo`.
- `penalty_value` y si se usa versión fija o progresiva.
- `crop_threshold_sources` con las fuentes ya referenciadas.

## Riesgos y mitigaciones

- Riesgo: penalización demasiado agresiva reduce acciones energéticas útiles.
  - Mitigación: calibrar `penalty_damage` con análisis de sensibilidad.
- Riesgo: umbrales no validados con agrónomo.
  - Mitigación: documentar que son referenciados y preparados para recalibración.

## Criterios de aceptación

- El reward se calcula como IEC menos penalización por daño.
- La penalización se activa solo con condiciones críticas por cultivo.
- La política RL registra en metadatos la regla de penalización y las fuentes.
- Las salidas 10 min reflejan cambios en `rl_reward` cuando hay daño.
