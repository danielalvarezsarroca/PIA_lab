# Definició del World Model per al sistema agrovoltaic
## Estat del MDP (Markov Decision Process)

***

## Arquitectura general

El *World Model* utilitza una **arquitectura factoritzada** que divideix les variables en tres blocs: **Exògenes**, **Accions** i **Endògenes**.

L'objectiu és que la xarxa neuronal aprengui únicament:

> `Endo_{t+1} = f(Endo_t, Exo_t, A_t)`

Les variables que el moviment de les plaques o el reg no poden alterar (meteorologia, posició del sol) s'injecten com a context extern i no es prediuen.

Per evitar colinealitat (correlació gairebé perfecta entre S1 i S2 sota la mateixa consigna de control) i reduir la complexitat innecessària, S2 s'exclou de totes les variables d'estat i de predicció.

---

## 1. Accions (`A_t`)

L'agent de RL controla **dues accions simultànies** a cada pas de 10 minuts:

| Variable | Tipus | Rang | Descripció |
|---|---|---|---|
| `tracker_angle_deg` | Contínua | −60° a +60° | Angle d'inclinació de les plaques fotovoltaiques |
| `irrigation_on` | Binària | {0, 1} | Decisió de regar o no en aquest pas de temps |
| `irrigation_dose_mm` | Fixa per política | 1.0 / 2.0 / 3.0 mm | Dosi nominal de l'esdeveniment de reg |

**Per què dues variables de reg en lloc d'una?**
Una sola variable contínua `irrigation_mm_10min` generaria una distribució molt desequilibrada (>85% de valors a zero), cosa que dificulta l'aprenentatge. La separació en decisió binària + dosi nominal per política és més natural per a RL i representa millor la realitat operativa: el sistema decideix *si* rega, i la dosi és un paràmetre de configuració de la política.

La dosi real aplicada (amb soroll estocàstic ±10%) es guarda a `WM_META` com a `irrigation_mm_10min` per a diagnòstic i calibratge, però no entra a l'espai d'estat del model.

---

## 2. Variables Exògenes (`Exo_t`) — El Context

Condicions de contorn que **no han de ser predites** pel World Model. S'injecten des de dades històriques o models externs. Cap d'aquestes variables depèn de les accions de l'agent.

### Rellotge Cíclic (Temps i Estacionalitat)

| Variable | Origen | Descripció |
|---|---|---|
| `hour_sin`, `hour_cos` | Calculat al notebook | Codificació de l'hora del dia |
| `day_sin`, `day_cos` | Calculat al notebook | Codificació del dia de l'any |

> **Nota d'implementació:** Aquestes quatre columnes **no existeixen a `master_dataset.csv`**. Cap bloc anterior del notebook les genera. Es calculen directament des del `DatetimeIndex` mitjançant la funció `add_cyclic_features()` dins del bloc de simulació de reg, aplicada a cada còpia del dataset per escenari.

La codificació cíclica evita els salts abruptes de les variables numèriques estàndard (p. ex.: de 23h50 a 00h00, o del dia 365 al dia 1).

### Radiació i Posició Solar Teòrica

| Variable | Descripció |
|---|---|
| `solar_elevation_deg` | Elevació del sol sobre l'horitzó |
| `solar_azimuth_deg` | Azimut solar (asimetries matí/tarda, obstruccions) |
| `clearsky_ghi_wm2` | Irradiància Global Horitzontal en cel clar — límit teòric màxim disponible |

### Meteorologia Local

| Variable | Descripció |
|---|---|
| `air_temp_ext_avg_degc` | Temperatura de l'aire exterior |
| `wind_speed_kmh` | Velocitat del vent |
| `precip_intensity_mm10min` | Intensitat de pluja per interval de 10 min (derivada de la columna acumulada) |

### Baseline Agronòmic — Zona R1 (referència a ple sol)

| Variable | Descripció |
|---|---|
| `PAR_R1` | Radiació Fotosintèticament Activa a ple sol, sense efecte de plaques |

`PAR_R1` és **exògena de veritat**: no depèn ni del tracker ni del reg. A diferència de `VWC_R1_sim` (vegeu Endògenes), que sí respon al reg i per tant és endògena.

---

## 3. Variables Endògenes (`Endo_t`) — Objectiu de Predicció

Les úniques variables que el World Model ha d'aprendre a predir. Representen l'impacte directe de les accions sobre el microclima i la generació.

### Producció d'Energia

| Variable | Descripció |
|---|---|
| `GPOA_mean` | Irradiància Global al Pla de la Matriu (W/m²). Mètrica principal de generació elèctrica |
| `ALBEDO_mean` | Radiació reflectida pel sòl. Útil per a plaques bifacials i com a indicador de l'estat del sòl |

### Efecte Microclimàtic — Ombra del Tracker (Variables Delta, Zona S1)

| Variable | Descripció |
|---|---|
| `Delta_PAR_S1` | Diferència de PAR entre la zona sota la placa (S1) i la referència a ple sol (R1) |
| `Delta_VWC_S1_sim` | Diferència d'humitat del sòl S1 vs R1 (efecte del tracker; el reg es cancel·la en el delta) |
| `Delta_Tsoil_S1_sim` | Diferència de temperatura del sòl S1 vs R1 |

### Dinàmica Hídrica Absoluta

| Variable | Descripció |
|---|---|
| `VWC_R1_sim` | Humitat volumètrica del sòl a la zona de referència. **Endògena** perquè respon directament al reg. Permet a l'agent aprendre *quan regar* |
| `Tsoil_R1_sim` | Temperatura del sòl a la zona de referència. El reg la refreda; la radiació l'escalfa |
| `minutes_since_last_irr` | Minuts transcorreguts des de l'últim esdeveniment de reg. **Endògena** (no metadata): captura la dinàmica temporal del reg, necessària perquè el model aprengui quant triga la humitat a recuperar-se o dissipar-se |

**Per què `VWC_R1_sim` és endògena i `PAR_R1` és exògena?**
`PAR_R1` no depèn de cap acció de l'agent (el sol no canvia si regues o no). `VWC_R1_sim` sí que canvia amb cada esdeveniment de reg, per tant el World Model l'ha de predir.

**Per què variables Delta i no valors absoluts de S1?**
Si es predís `PAR_S1` absolut, el model hauria d'aprendre alhora el pas de núvols i l'ombra de la placa — dues causes impossible de separar. Predint `Delta_PAR_S1`, el model només aprèn l'atenuació geomètrica relativa a la llum disponible (`PAR_R1`), que és la part causada per l'acció del tracker.

---

## 4. Metadades (`WM_META`) — Diagnòstic i Traçabilitat

No entren a l'espai d'estat del World Model, però son necessàries per a auditoria, calibratge i anàlisi post-entrenament.

| Variable | Descripció |
|---|---|
| `policy_id` | Identificador de l'escenari de reg: `fixed_{interval_h}h_{dose_mm}mm` |
| `episode_id` | Clau única per fila: `{policy_id}_{timestamp_unix}`. Essencial perquè el dataset concatena 12 escenaris amb timestamps repetits entre ells |
| `irrigation_mm_10min` | Dosi real aplicada amb soroll estocàstic (±10% de la dosi nominal) |
| `irrigation_duration_min` | Durada real de l'esdeveniment, proporcional a la dosi real |
| `irrigation_cumulative_day_mm` | Acumulat de reg del dia en curs. Útil per detectar sobre-reg |
| `water_input_mm` | Suma de reg + pluja per pas de temps |

---

## 5. Simulació de Dinàmica Hídrica i Tèrmica (Proxy)

Com que no hi ha mesures directes de l'efecte del reg per zona, es fa servir un proxy físicament coherent que simula `VWC_sim` i `Tsoil_sim` per a les zones R1 i S1.

### 5.1 Model de Humitat del Sòl (VWC)

Per cada zona `z ∈ {R1, S1}`, a cada pas de 10 minuts:

```
VWC_{t+1,z} = clamp(VWC_{t,z} + vwc_gain - vwc_loss_et - vwc_loss_drain,  VWC_MIN, VWC_SAT)
```

on:
- `vwc_gain = K_IN[z] * water_input * sat_factor`
- `vwc_loss_et = K_ET[z] * et_proxy * DT_H`
- `vwc_loss_drain = K_DRAIN * max(VWC_{t,z} - VWC_FC, 0)`

Factors no lineals per evitar comportaments absurds als extrems:
- `sat_factor`: redueix la infiltració quan el sòl s'acosta a saturació
- `moisture_factor`: redueix l'ET quan el sòl s'acosta al punt de marcescència

### 5.2 Evapotranspiració Proxy (ET)

Sense mesures directes d'ET0, s'utilitza una aproximació operativa:

```
et_proxy = (ET_C0 + ET_CT_AIR*(Tair-15) + ET_CT_SOIL*(Tsoil-15) + ET_CRAD*rad_norm + ET_CWIND*wind_norm) * moisture_factor
```

### 5.3 Model de Temperatura del Sòl (Tsoil)

```
Tsoil_{t+1,z} = clamp(Tsoil_{t,z} + delta_tsoil,  TSOIL_MIN, TSOIL_MAX)
delta_tsoil = A_AIR*(Tair - Tsoil_{t,z}) + A_RAD[z]*rad_norm - A_WATER*water_input - A_NIGHT*is_night
```

### 5.4 Coeficients per Zona

| Coeficient | R1 | S1 | Justificació |
|---|---|---|---|
| `K_IN` (infiltració) | 0.0030 | 0.0035 | S1 reté lleugerament més (menys evaporació de superfície) |
| `K_ET` (escala ET) | 1.00 | 0.85 | Menys evapotranspiració sota l'ombra de les plaques |
| `A_RAD` (escalfament radiatiu) | 0.30 | 0.24 | Menys radiació directa sota les plaques |

### 5.5 Límits Físics

- `|ΔTsoil| ≤ 0.8 °C` per pas de 10 min
- `VWC ∈ [0.08, 0.42]` (mínim físic, saturació)
- Nocturn: escalfament radiatiu nul, evaporació mínima

---

## 6. Generació d'Escenaris i Soroll Estocàstic

El bloc genera **12 escenaris** combinant 4 intervals de reg (4h, 6h, 8h, 12h) × 3 dosis (1.0, 2.0, 3.0 mm), tots sobre la mateixa base de dades temporals de `compact`.

### Soroll Estocàstic (Jitter)

Per evitar que el World Model memoritza patrons de reg regulars en lloc d'aprendre la física del sòl, cada escenari aplica soroll controlat:

- **Jitter de timing:** cada esdeveniment de reg es desplaça aleatòriament ±1 pas (±10 min) respecte al calendari nominal.
- **Jitter de dosi:** cada dosi aplicada varia ±10% de la dosi base.

El generador aleatori utilitza `RNG_SEED=42` per reproductibilitat.

### Estructura del Dataset Final

El `pd.concat` dels 12 escenaris **no aplica `sort_index()` global** perquè barrejar escenaris per timestamp dificulta el slicing per episodi durant l'entrenament. L'ordre és escenari-primer (totes les files del primer escenari, després les del segon, etc.).

Com que els timestamps es repeteixen entre escenaris (els 12 reutilitzen el mateix rang temporal de `compact`), l'`episode_id` és l'única clau que identifica unívocament cada fila: `{interval_h}h_{dose_mm}mm_{timestamp_unix}`.

---

## 7. Fitxers Generats

| Fitxer | Descripció |
|---|---|
| `outputs/master_dataset.csv` | Dataset base — **immutable**. Font dels sensors reals |
| `outputs/master_dataset_world_model.csv` | Dataset derivat per a entrenament del World Model. Conté les 12 × N files amb totes les columnes EXO + ACTIONS + ENDO + META |