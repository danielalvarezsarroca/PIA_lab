from pathlib import Path

import pandas as pd

from solar_logic import WEIGHT_PRESETS, weighted_iec


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "sprint2" / "outputs_sprint2" / "dataset_modelizacion_6h.csv"
OUT_DIR = Path(__file__).resolve().parent / "outputs_sprint3"


def _summarize_regimes(df: pd.DataFrame, preset: str, energy_weight: float, crop_weight: float) -> pd.DataFrame:
    work = df.dropna(subset=["tracking_regime", "track_mean", "IEC"]).copy()
    work["IEC_weighted"] = weighted_iec(work, energy_weight, crop_weight)
    grouped = (
        work.groupby("tracking_regime")
        .agg(
            n=("IEC_weighted", "size"),
            iec_original_mediana=("IEC", "median"),
            iec_ponderado_mediana=("IEC_weighted", "median"),
            energy_mediana=("energy_score", "median"),
            crop_mediana=("crop_score", "median"),
            angulo_mediano=("track_mean", "median"),
        )
        .reset_index()
    )
    grouped.insert(0, "escenario", preset)
    grouped.insert(1, "peso_energia", energy_weight)
    grouped.insert(2, "peso_cultivo", crop_weight)
    return grouped.round(3)


def _top_policy_by_hour(df: pd.DataFrame, preset: str, energy_weight: float, crop_weight: float) -> pd.DataFrame:
    work = df.dropna(subset=["hour_of_day", "tracking_regime", "track_mean", "IEC"]).copy()
    work["IEC_weighted"] = weighted_iec(work, energy_weight, crop_weight)
    rows = []
    for hour, hour_df in work.groupby("hour_of_day"):
        best = hour_df.loc[hour_df["IEC_weighted"].idxmax()]
        rows.append(
            {
                "escenario": preset,
                "peso_energia": energy_weight,
                "peso_cultivo": crop_weight,
                "hora": int(hour),
                "regimen_recomendado": best["tracking_regime"],
                "angulo_recomendado": round(float(best["track_mean"]), 1),
                "iec_ponderado": round(float(best["IEC_weighted"]), 3),
                "iec_original": round(float(best["IEC"]), 3),
                "energy_score": round(float(best["energy_score"]), 3),
                "crop_score": round(float(best["crop_score"]), 3),
                "soporte_obs_hora": int(len(hour_df)),
            }
        )
    return pd.DataFrame(rows).sort_values(["escenario", "hora"])


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_PATH, parse_dates=["Time"])

    regime_frames = []
    policy_frames = []
    for preset, (energy_weight, crop_weight) in WEIGHT_PRESETS.items():
        regime_frames.append(_summarize_regimes(df, preset, energy_weight, crop_weight))
        policy_frames.append(_top_policy_by_hour(df, preset, energy_weight, crop_weight))

    regime_summary = pd.concat(regime_frames, ignore_index=True)
    policy_summary = pd.concat(policy_frames, ignore_index=True)

    regime_summary.to_csv(OUT_DIR / "iec_sensitivity_by_regime.csv", index=False)
    policy_summary.to_csv(OUT_DIR / "iec_sensitivity_policy_by_hour.csv", index=False)

    print("IEC sensitivity analysis written to:")
    print(f"- {OUT_DIR / 'iec_sensitivity_by_regime.csv'}")
    print(f"- {OUT_DIR / 'iec_sensitivity_policy_by_hour.csv'}")
    print()
    print("Regime summary:")
    print(regime_summary.to_string(index=False))
    print()
    print("Best policy by hour:")
    print(policy_summary.to_string(index=False))


if __name__ == "__main__":
    main()
