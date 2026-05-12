import pandas as pd
import numpy as np
from pathlib import Path
import os

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- Configuració de rutes ---
NOTEBOOK_DIR = Path(os.getcwd())
OUT_DIR = NOTEBOOK_DIR / 'outputs'
MASTER_CSV = OUT_DIR / 'master_dataset.csv'
RL_DATASET_CSV = OUT_DIR / 'rl_factored_dataset.csv'

# 1. Càrrega de dades
try:
    df = pd.read_csv(MASTER_CSV, parse_dates=['Time'], index_col='Time')
    print("Dataset mestre carregat correctament.")
except Exception as e:
    print(f"Error carregant {MASTER_CSV}: {e}")
    # Creem un df fictici per poder executar el script si falla la càrrega
    df = pd.DataFrame(index=pd.date_range('2025-06-17 14:00:00', periods=10, freq='10min'))
    for col in ['solar_elevation_deg', 'tracker_angle_deg', 'clearsky_dni_wm2', 'clearsky_dhi_wm2', 'GPOA_mean', 'PAR_R1', 'Tsoil_R1_mean', 'VWC_R1_mean', 'ALBEDO_mean', 'Delta_PAR_S1', 'Delta_Tsoil_S1', 'Delta_VWC_S1', 'air_temp_ext_avg_degc', 'wind_speed_kmh', 'precip_intensity_mm10min', 'solar_azimuth_deg', 'clearsky_ghi_wm2']:
        df[col] = np.random.rand(10)

# 2. Enginyeria de Variables: Rellotge Cíclic
print("Afegint variables cícliques de temps...")
df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24.0)
df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24.0)
df['day_sin'] = np.sin(2 * np.pi * df.index.dayofyear / 365.25)
df['day_cos'] = np.cos(2 * np.pi * df.index.dayofyear / 365.25)

# 3. Solució per a l'Hivern: GPOA_proxy basat en física solar
print("Calculant GPOA_proxy per als períodes sense dades del sensor...")
inc_angle_rad = np.arccos(
    np.cos(np.radians(90 - df['solar_elevation_deg'])) * np.cos(np.radians(df['tracker_angle_deg']))
)
# Posem un límit inferior de 0 per evitar cosinus negatius
gpoa_proxy = (df['clearsky_dni_wm2'] * np.cos(inc_angle_rad).clip(lower=0)) + df['clearsky_dhi_wm2']

# Remplacem els valors nuls de GPOA_mean amb el nostre proxy teòric
nuls_abans = df['GPOA_mean'].isna().sum()
df['GPOA_mean'] = df['GPOA_mean'].fillna(gpoa_proxy)
nuls_despres = df['GPOA_mean'].isna().sum()
print(f"S'han imputat {nuls_abans - nuls_despres} valors de GPOA_mean utilitzant el proxy teòric.")

# Assegurem el "clamping" nocturn
is_night = df['solar_elevation_deg'] < 0
df.loc[is_night, 'GPOA_mean'] = 0.0

# 4. Selecció Purificada de Variables (Arquitectura Factoritzada)
action_col = ['tracker_angle_deg']

cols_exogenes = [
    'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
    'solar_elevation_deg', 'solar_azimuth_deg',
    'clearsky_ghi_wm2', 
    'air_temp_ext_avg_degc', 'wind_speed_kmh', 'precip_intensity_mm10min',
    'PAR_R1', 'Tsoil_R1_mean', 'VWC_R1_mean'
]

# Noteu l'absència d'ALBEDO_mean (57% de NaNs en testing)
cols_endogenes = [
    'GPOA_mean', 
    'Delta_PAR_S1', 'Delta_Tsoil_S1', 'Delta_VWC_S1'
]

rl_features = action_col + cols_exogenes + cols_endogenes
df_rl_ready = df[rl_features].copy()

df_rl_ready = df_rl_ready.round(4)

# Guardar el dataset purificat
df_rl_ready.to_csv(RL_DATASET_CSV)
print(f"\nDataset purificat preparat per RL guardat a: {RL_DATASET_CSV}")
print(f"Dimensions finals: {df_rl_ready.shape}")
print(f"Columnes exògenes ({len(cols_exogenes)}): {cols_exogenes}")
print(f"Columnes endògenes ({len(cols_endogenes)}): {cols_endogenes}")


# ============================================================
# Visualització de la Cobertura Temporal del Dataset RL
# ============================================================
fig, ax = plt.subplots(figsize=(14, 8)) # Ajustem alçada per ~18 columnes

labels_plotted = []

# Definim un buit com un salt superior al doble del BASE_FREQ (20 minuts)
threshold = pd.Timedelta(minutes=20)

for i, col in enumerate(df_rl_ready.columns):
    # Ens quedem només amb els registres on la variable no és nula
    valid_data = df_rl_ready[col].dropna()
    if valid_data.empty:
        continue
        
    first_real = valid_data.index[0]
    last_real  = valid_data.index[-1]
    
    # Calcular diferències de temps per detectar forats
    diffs = valid_data.index.to_series().diff()
    gap_mask = diffs > threshold
    segment_id = gap_mask.cumsum()
    
    # Dibuixar els segments continus de dades (Verd)
    for seg, group in valid_data.groupby(segment_id):
        ax.plot([group.index[0], group.index[-1]], [i, i],
                lw=4, solid_capstyle='round', color='#2A9D8F', zorder=2)
        
    # Dibuixar els buits identificats (Vermell)
    # Cal anar amb compte: iterar sobre els gaps i pintar de la fi del tram anterior a l'inici del gap
    gap_indices = np.where(gap_mask)[0]
    for idx in gap_indices:
        gap_end_time = valid_data.index[idx]
        gap_start_time = valid_data.index[idx - 1]
        ax.plot([gap_start_time, gap_end_time], [i, i],
                lw=4, solid_capstyle='round', color='#E76F51', zorder=3)
                
    # Afegir etiquetes de data (inici i fi) per a cada variable
    # Utilitzem anotacions només a l'inici i final absoluts de cada sèrie
    ax.text(first_real, i + 0.25, first_real.strftime('%Y-%m-%d'),
            fontsize=8, color='#555', ha='left', va='bottom')
    ax.text(last_real,  i + 0.25, last_real.strftime('%Y-%m-%d'),
            fontsize=8, color='#555', ha='right', va='bottom')
            
    labels_plotted.append(col)

# Configuració dels eixos i aspecte general
ax.set_yticks(range(len(labels_plotted)))
ax.set_yticklabels(labels_plotted, fontsize=10)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
# Ajustar el locator depenent del rang temporal (mensual sol ser bo)
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=9)

ax.set_title('Cobertura temporal de les variables del RL Factored Dataset', fontsize=16, pad=15)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.tick_params(axis='y', length=0)
ax.set_ylim(-0.8, len(labels_plotted) - 0.2)

# Llegenda
from matplotlib.lines import Line2D
custom_lines = [Line2D([0], [0], color='#2A9D8F', lw=4),
                Line2D([0], [0], color='#E76F51', lw=4)]
ax.legend(custom_lines, ['Dades presents', 'Buit / NaN'], 
          fontsize=11, loc='lower right', framealpha=0.9, bbox_to_anchor=(1.0, 0.0))

plt.tight_layout()
# Ens assegurem que la carpeta d'outputs existeixi (útil si executem des d'un altre lloc)
import os
os.makedirs('outputs', exist_ok=True)
plt.savefig('outputs/cobertura_temporal_rl_dataset.png', dpi=150, bbox_inches='tight')
plt.show()