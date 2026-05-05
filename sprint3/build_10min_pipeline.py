from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from agricultural_rules import (
    CROP_PROFILES,
    build_crop_risk_dataset,
    generate_agricultural_rules_10min,
    write_agricultural_outputs,
)
from ten_min_pipeline import (
    build_modeling_dataset_10min,
    regenerate_candidate_rules_10min,
    write_10min_outputs,
)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MASTER_PATH = BASE_DIR / "outputs" / "master_dataset.csv"
DEFAULT_OUTPUT_DIR = BASE_DIR / "outputs_10min"
DEFAULT_6H_BACKUP_SOURCES = [
    BASE_DIR.parent / "sprint2" / "outputs_sprint2" / "dataset_modelizacion_6h.csv",
    BASE_DIR.parent / "sprint2" / "outputs_sprint2" / "candidate_rotation_rules.csv",
]


def build_10min_pipeline(
    master_path: str | Path = DEFAULT_MASTER_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    backup_6h_paths: list[str | Path] | None = None,
    crop_type: str = "lechuga",
) -> dict[str, Path]:
    master_path = Path(master_path)
    if not master_path.exists():
        raise FileNotFoundError(f"Master dataset not found: {master_path}")

    master_df = pd.read_csv(master_path, parse_dates=["Time"])
    model_10min = build_modeling_dataset_10min(master_df)
    rules_10min = regenerate_candidate_rules_10min(model_10min)
    crop_risk = build_crop_risk_dataset(model_10min, crop_type=crop_type)
    agricultural_rules = generate_agricultural_rules_10min(crop_risk, crop_type=crop_type)
    metadata = {
        "mode": "master_dataset_10min_experimental",
        "source_dataset": str(master_path),
        "crop_type": crop_type,
        "rows": int(len(model_10min)),
        "rules_generated": int(len(rules_10min)),
        "agricultural_rules_generated": int(len(agricultural_rules)),
        "note": (
            "Pipeline experimental a 10 minutos. La version 6h se mantiene como "
            "backup y referencia estable. Las reglas agronomicas son una demo "
            "pensada para sustituir las variables imputadas por sensores reales."
        ),
    }
    paths = write_10min_outputs(
        output_dir=output_dir,
        model_dataset=model_10min,
        rules=rules_10min,
        metadata=metadata,
        backup_6h_paths=backup_6h_paths if backup_6h_paths is not None else DEFAULT_6H_BACKUP_SOURCES,
    )
    paths.update(write_agricultural_outputs(output_dir, crop_risk, agricultural_rules, CROP_PROFILES))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the experimental 10-minute modelling pipeline from sprint3/outputs/master_dataset.csv."
    )
    parser.add_argument("--master-path", type=Path, default=DEFAULT_MASTER_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--crop-type",
        choices=sorted(CROP_PROFILES),
        default="lechuga",
        help="Crop profile used for demo agronomic rules.",
    )
    parser.add_argument(
        "--no-6h-backup",
        action="store_true",
        help="Do not copy existing 6h dataset/rules into the output backup folder.",
    )
    args = parser.parse_args()

    paths = build_10min_pipeline(
        master_path=args.master_path,
        output_dir=args.output_dir,
        backup_6h_paths=[] if args.no_6h_backup else None,
        crop_type=args.crop_type,
    )
    print("10 min pipeline generated")
    print(f"dataset: {paths['dataset']}")
    print(f"rules: {paths['rules']}")
    print(f"metadata: {paths['metadata']}")
    print(f"6h backup: {paths['backup_dir']}")
    print(f"crop risk: {paths['crop_risk']}")
    print(f"agricultural rules: {paths['agricultural_rules']}")
    print(f"crop profiles: {paths['crop_profiles']}")


if __name__ == "__main__":
    main()
