from __future__ import annotations

import argparse
from pathlib import Path

from world_model_dataset import build_reward_training_dataset, load_world_model_dataset


SPRINT3_DIR = Path(__file__).resolve().parents[2]
DEFAULT_WORLD_MODEL_PATH = SPRINT3_DIR / "outputs" / "master_dataset_world_model.csv"
DEFAULT_OUTPUT_PATH = SPRINT3_DIR / "outputs" / "world_model_training_dataset.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reward-enriched transition dataset for LSTM/RL training.")
    parser.add_argument("--world-model-path", type=Path, default=DEFAULT_WORLD_MODEL_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--crop-type", default="lechuga")
    parser.add_argument("--crop-zone", default="S1")
    args = parser.parse_args()

    world_df = load_world_model_dataset(args.world_model_path)
    dataset = build_reward_training_dataset(world_df, crop_type=args.crop_type, crop_zone=args.crop_zone)
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(args.output_path, index=False)
    print(f"training dataset: {args.output_path}")
    print(f"rows: {len(dataset):,}")
    print(f"policies: {dataset['policy_id'].nunique():,}")
    print(f"reward mean: {dataset['rl_reward'].mean():.4f}")


if __name__ == "__main__":
    main()
