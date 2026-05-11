***

## Definició de l'Estat del MDP (Markov Decision Process) per al World Model

Per entrenar el *World Model* del sistema agrovoltaic, hem optat per una **arquitectura factoritzada**. En lloc de demanar a la xarxa neuronal que predigui tot l'entorn (incloent-hi la meteorologia o la posició del sol, coses que el moviment de les plaques no pot alterar), dividim les variables en dos grans blocs: **Exògenes** i **Endògenes**.

A més, per evitar problemes de colinealitat (com la forta correlació entre les zones S1 i S2 en moure's sota la mateixa consigna de control) i reduir la càrrega cognitiva del model, hem seleccionat un subconjunt purificat de 19 variables essencials.

### 1. Acció ($A_t$)
L'única variable de control que l'agent de RL pot manipular:
*   `tracker_angle_deg`: Angle d'inclinació de les plaques fotovoltaiques (de -60° a +60°).

### 2. Variables Exògenes ($Exo_t$) - El Context
Aquestes variables actuen com a condicions de contorn (el clima i el temps). Són independents de l'acció $A_t$ i **no han de ser predites per la xarxa neuronal**. En simulació, aquests valors s'injecten des de dades històriques o models externs.

*   **Rellotge Cíclic (Temps i Estacionalitat):**
    *   `hour_sin`, `hour_cos`: Codificació de l'hora del dia.
    *   `day_sin`, `day_cos`: Codificació del dia de l'any.
    *   *Justificació:* Permet al model entendre els cicles diaris (dia/nit) i estacionals sense els salts abruptes de les variables numèriques estàndard (ex: de 23:59 a 00:00).
*   **Radiació i Posició Solar Teòrica:**
    *   `solar_elevation_deg`: Elevació del sol sobre l'horitzó.
    *   `solar_azimuth_deg`: Azimut solar (útil si hi ha asimetries matí/tarda o muntanyes properes).
    *   `clearsky_ghi_wm2`: Irradiància Global Horitzontal teòrica en cel clar. Actua com a límit màxim teòric de l'energia solar disponible.
*   **Meteorologia Local Externa:**
    *   `air_temp_ext_avg_degc`: Temperatura de l'aire a l'exterior.
    *   `wind_speed_kmh`: Velocitat del vent.
    *   `precip_intensity_mm10min`: Intensitat de pluja.
*   **Baseline Agronòmic (Sensor R1 - Referència sense plaques):**
    *   `PAR_R1`: Radiació Fotosintèticament Activa a ple sol.
    *   `Tsoil_R1_mean`: Temperatura del sòl a ple sol.
    *   `VWC_R1_mean`: Humitat del sòl a ple sol.
    *   *Justificació:* Aquests sensors actuen com el "clima base" del sòl sense l'efecte de l'ombra.

### 3. Variables Endògenes ($Endo_t$) - L'Estat del Sistema (Objectiu de Predicció)
Aquestes són les úniques variables que el *World Model* ha d'aprendre a predir: $Endo_{t+1} = f(Endo_t, Exo_t, A_t)$. Representen l'impacte directe del moviment de les plaques sobre el microclima i la generació.

*   **Producció d'Energia:**
    *   `GPOA_mean`: Irradiància Global al Pla de la Matriu (W/m²). És la principal mètrica per avaluar la generació elèctrica.
    *   `ALBEDO_mean`: Radiació reflectida pel sòl, útil com a indicador de l'estat del sòl i per a càlculs d'energia si les plaques són bifacials.
*   **Efecte Microclimàtic (Variables Delta - Zona S1):**
    *   `Delta_PAR_S1`: Diferència de PAR entre la zona sota la placa (S1) i el control a ple sol (R1).
    *   `Delta_Tsoil_S1`: Diferència de temperatura del sòl.
    *   `Delta_VWC_S1`: Diferència d'humitat del sòl.

#### **Justificació de l'ús de Variables "Delta" i l'exclusió de S2:**

1.  **Exclusió de la Zona S2 per Colinealitat:** L'anàlisi de correlació mostra que S1 i S2 responen de manera gairebé idèntica a l'acció del tracker. Incloure S2 només aporta redundància i augmenta la complexitat de l'espai d'estats.
2.  **Aïllament de la Causalitat:** Si intentéssim predir el valor absolut `PAR_S1`, el model hauria d'aprendre a predir el pas de núvols (impossible) sumat a l'ombra de la placa. Predint `Delta_PAR_S1`, el model només ha d'aprendre l'atenuació geomètrica que causa la placa respecte a la llum disponible (`PAR_R1`).
3.  **Generalització i Robustesa:** L'enfocament Delta permet que el model sigui resilient a condicions climàtiques anòmales que no hagi vist en l'entrenament, ja que aprèn relacions relatives (ex: "el panell bloqueja un X% de llum") i no magnituds absolutes.