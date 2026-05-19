# Validacion offline de mejora energia-cultivo

## Objetivo

Estimar de forma numerica la mejora del sistema propuesto respecto al comportamiento historico/tradicional, usando el indice combinado energia-cultivo.

## Muestra analizada

- Datos historicos de 10 minutos.
- 23.043 registros comparables.
- 241 dias comparables.
- Franja operativa aproximada: 06:00-21:00.
- Comparacion realizada sobre registros con indice energia-cultivo valido.

## Metodo de comparacion

Se compara:

1. **Sistema historico/tradicional**: media del indice energia-cultivo observado en los datos historicos.
2. **Sistema propuesto con DQN**: estimacion offline del resultado esperado al aplicar las acciones recomendadas por la politica DQN, usando resultados historicos observados para acciones equivalentes o similares.

El calculo reproducible esta implementado en:

```text
sprint3/reports/calcular_mejora_offline_energia_cultivo.py
```

Para regenerar la validacion:

```bash
sprint3/.venv/bin/python sprint3/reports/calcular_mejora_offline_energia_cultivo.py
```

El script genera una salida estructurada en:

```text
sprint3/reports/validacion_offline_mejora_energia_cultivo.json
```

La mejora se calcula como:

```text
mejora (%) = ((indice_sistema_DQN - indice_historico) / indice_historico) * 100
```

## Resultado principal

```text
Indice historico medio:       0,258
Indice sistema DQN estimado:  0,320
Mejora estimada:              +24,2%
```

Por tanto, el sistema propuesto mejora el indice combinado energia-cultivo en aproximadamente un **24,2%** respecto al comportamiento historico/tradicional.

## Resultado complementario

Tambien se calculo la mejora usando la recompensa interna del agente, que combina energia, salud del cultivo y penalizaciones por situaciones agronomicas criticas.

```text
Recompensa historica media:       0,322
Recompensa sistema DQN estimada:  0,519
Mejora estimada:                  +61,5%
```

Este segundo valor es util como referencia tecnica, pero para el informe se recomienda usar como cifra principal la mejora del **24,2%**, porque esta directamente ligada al indice energia-cultivo mostrado en la interfaz.

## Texto recomendado para el informe

En una validacion offline sobre 23.043 registros historicos de 10 minutos, correspondientes a 241 dias comparables, el sistema propuesto incremento el indice combinado energia-cultivo de 0,258 a 0,320 de media. Esto supone una mejora estimada del 24,2% respecto al comportamiento historico/tradicional.

Este resultado debe interpretarse como una estimacion offline basada en datos historicos, no como una prueba experimental en campo.

## Nota de rigor

No se recomienda reportar la mejora calculada directamente a partir del valor Q bruto del modelo DQN, porque en esta validacion aparece saturado en 1,0 y podria sobreestimar artificialmente la mejora real del sistema.
