from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
SPRINT3_DIR = ROOT_DIR / "sprint3"
if str(SPRINT3_DIR) not in sys.path:
    sys.path.insert(0, str(SPRINT3_DIR))

from daily_update import DEMO_NOTICE, regenerate_candidate_rules  # noqa: E402

DEFAULT_INPUT_PATH = SPRINT3_DIR / "outputs_daily" / "dataset_modelizacion_6h_updated.csv"
DEFAULT_OUTPUT_DIR = SPRINT3_DIR / "outputs_daily"


def retrain_from_updated_dataset(
    input_path: str | Path = DEFAULT_INPUT_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Path]:
    """
    Regenerate Sprint 2 demo rules from the daily updated dataset.

    This is the integration point where a future real retraining job can replace
    the demo rule generator once SCADA/sensor ingestion is available.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Updated dataset not found: {input_path}")

    updated_df = pd.read_csv(input_path, parse_dates=["Time"])
    rules = regenerate_candidate_rules(updated_df)
    output_dir.mkdir(parents=True, exist_ok=True)

    rules_path = output_dir / "candidate_rotation_rules_updated.csv"
    metadata_path = output_dir / "retrain_metadata.json"
    rules.to_csv(rules_path, index=False)

    metadata: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "demo_rule_regeneration",
        "input_dataset": str(input_path),
        "rows_used": int(len(updated_df)),
        "rules_generated": int(len(rules)),
        "output_rules": str(rules_path),
        "notice": DEMO_NOTICE,
        "future_integration": (
            "Sustituir este generador demo por el entrenamiento real del Sprint 2 "
            "cuando exista ingesta diaria de sensores/SCADA."
        ),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"rules": rules_path, "metadata": metadata_path}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate demo Sprint 2 rules from the daily updated dataset."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    paths = retrain_from_updated_dataset(args.input, args.output_dir)
    print(f"Reglas actualizadas: {paths['rules']}")
    print(f"Metadatos de reentrenamiento: {paths['metadata']}")


if __name__ == "__main__":
    main()
