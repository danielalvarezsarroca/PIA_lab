from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from world_model_dataset import ACTION_COLUMNS, DETERMINISTIC_STATE_COLUMNS, ENDO_COLUMNS, EXO_COLUMNS, LEARNED_ENDO_COLUMNS
from world_model_lstm import WorldModelLSTM
from world_model_lstm_dataset import (
    fit_window_scalers,
    make_policy_windows,
    split_training_and_stream_by_time,
    split_windows_chronologically,
    transform_windows,
    weekly_retraining_cutoffs,
)
from world_model_lstm_training import predict, regression_metrics, save_artifacts, train_model


SPRINT3_DIR = Path(__file__).resolve().parents[2]
TRAINING_DATASET = SPRINT3_DIR / "outputs" / "world_model_training_dataset.csv"
OUTPUT_DIR = SPRINT3_DIR / "outputs"


def _require_dataset(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"World-model training dataset not found: {path}. "
            "Regenerate sprint3/outputs/master_dataset_world_model.csv and "
            "sprint3/outputs/world_model_training_dataset.csv before training."
        )


def _make_clean_frame(df: pd.DataFrame, feature_cols: list[str], target_cols: list[str]) -> pd.DataFrame:
    return df.dropna(subset=feature_cols + target_cols).sort_values(["policy_id", "Time"]).reset_index(drop=True)


def _evaluate_targets(
    model: WorldModelLSTM,
    x_scaled,
    y_scaled,
    y_scaler,
    target_cols: list[str],
    device: str | None = None,
) -> dict[str, dict[str, float]]:
    if len(x_scaled) == 0:
        return {}
    y_pred_scaled = predict(model, x_scaled, device=device)
    y_pred = y_scaler.inverse_transform(y_pred_scaled)
    y_true = y_scaler.inverse_transform(y_scaled)
    return regression_metrics(y_true, y_pred, target_cols)


def _train_once(
    clean_df: pd.DataFrame,
    feature_cols: list[str],
    target_cols: list[str],
    args: argparse.Namespace,
    split_metadata: dict[str, object],
    run_label: str,
) -> tuple[WorldModelLSTM, dict, dict, pd.DataFrame]:
    x_raw, y_raw = make_policy_windows(clean_df, feature_cols, target_cols, window_size=args.window_size)
    scaled = fit_window_scalers(x_raw, y_raw)
    split = split_windows_chronologically(scaled.x_scaled, scaled.y_scaled)

    model = WorldModelLSTM(
        input_size=scaled.x_scaled.shape[-1],
        hidden_size=args.hidden_size,
        output_size=scaled.y_scaled.shape[-1],
        num_layers=args.num_layers,
    )
    history = train_model(
        model,
        split.x_train,
        split.y_train,
        split.x_val,
        split.y_val,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
    )
    y_pred_scaled = predict(model, split.x_test)
    y_pred = scaled.y_scaler.inverse_transform(y_pred_scaled)
    y_true = scaled.y_scaler.inverse_transform(split.y_test)
    target_metrics = regression_metrics(y_true, y_pred, target_cols)
    metrics = {
        "run_label": run_label,
        "rows_loaded": int(len(clean_df)),
        "window_size": int(args.window_size),
        "x_shape": list(scaled.x_scaled.shape),
        "y_shape": list(scaled.y_scaled.shape),
        "history": history,
        "target_metrics": target_metrics,
        "split_metadata": split_metadata,
        "stream_frac": float(args.stream_frac),
        "retrain_frequency_days": int(args.retrain_frequency_days),
        "scaler_fit_scope": "train_only",
    }
    sample = pd.DataFrame(y_true[:250], columns=[f"actual_{column}" for column in target_cols])
    pred = pd.DataFrame(y_pred[:250], columns=[f"pred_{column}" for column in target_cols])
    predictions_sample = pd.concat([sample, pred], axis=1)
    scalers = {
        "x_scaler": scaled.x_scaler,
        "y_scaler": scaled.y_scaler,
        "feature_cols": feature_cols,
        "target_cols": target_cols,
        "window_size": int(args.window_size),
        "hidden_size": int(args.hidden_size),
        "num_layers": int(args.num_layers),
        "deterministic_state_cols": DETERMINISTIC_STATE_COLUMNS,
        "learned_endo_cols": LEARNED_ENDO_COLUMNS,
        "split_metadata": split_metadata,
        "stream_frac": float(args.stream_frac),
        "retrain_frequency_days": int(args.retrain_frequency_days),
        "scaler_fit_scope": "train_only",
    }
    return model, scalers, metrics, predictions_sample


def _simulate_weekly_retraining(
    train_df: pd.DataFrame,
    stream_df: pd.DataFrame,
    feature_cols: list[str],
    target_cols: list[str],
    args: argparse.Namespace,
    base_metadata: dict[str, object],
) -> list[dict[str, object]]:
    runs: list[dict[str, object]] = []
    for cutoff in weekly_retraining_cutoffs(stream_df, frequency_days=args.retrain_frequency_days):
        observed = stream_df[pd.to_datetime(stream_df["Time"]) <= cutoff]
        retrain_df = pd.concat([train_df, observed], ignore_index=True).sort_values(["policy_id", "Time"])
        metadata = dict(base_metadata)
        metadata.update({
            "retrain_cutoff": cutoff.isoformat(),
            "observed_stream_rows": int(len(observed)),
        })
        _, _, metrics, _ = _train_once(
            retrain_df,
            feature_cols,
            target_cols,
            args,
            split_metadata=metadata,
            run_label=f"weekly_retrain_{cutoff.date().isoformat()}",
        )
        runs.append({
            "cutoff": cutoff.isoformat(),
            "observed_stream_rows": int(len(observed)),
            "target_metrics": metrics["target_metrics"],
            "history": metrics["history"],
        })
    return runs


def main() -> None:
    parser = argparse.ArgumentParser(description="Train LSTM World Model on reward-enriched agrovoltaic transitions.")
    parser.add_argument("--dataset", type=Path, default=TRAINING_DATASET)
    parser.add_argument("--window-size", type=int, default=12)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--num-layers", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--stream-frac", type=float, default=0.20)
    parser.add_argument("--retrain-frequency-days", type=int, default=7)
    parser.add_argument("--mode", choices=["initial", "simulate-retraining"], default="initial")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    _require_dataset(args.dataset)
    df = pd.read_csv(args.dataset, parse_dates=["Time"])
    feature_cols = EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS
    target_cols = [f"next_{column}" for column in LEARNED_ENDO_COLUMNS]
    clean_df = df.dropna(subset=feature_cols + target_cols).sort_values(["policy_id", "Time"]).reset_index(drop=True)
    time_split = split_training_and_stream_by_time(clean_df, stream_frac=args.stream_frac)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    stream_path = output_dir / "world_model_lstm_stream_holdout.csv"
    time_split.stream.to_csv(stream_path, index=False)

    model, scalers, metrics, predictions_sample = _train_once(
        time_split.train,
        feature_cols,
        target_cols,
        args,
        split_metadata=time_split.metadata,
        run_label="initial_train",
    )

    x_stream_raw, y_stream_raw = make_policy_windows(
        time_split.stream,
        feature_cols,
        target_cols,
        window_size=args.window_size,
    )
    if len(x_stream_raw) > 0:
        stream_scaled = transform_windows(x_stream_raw, y_stream_raw, scalers["x_scaler"], scalers["y_scaler"])
        metrics["stream_shape"] = list(stream_scaled.x_scaled.shape)
        metrics["stream_target_metrics"] = _evaluate_targets(
            model,
            stream_scaled.x_scaled,
            stream_scaled.y_scaled,
            scalers["y_scaler"],
            target_cols,
        )
    else:
        metrics["stream_shape"] = [0, int(args.window_size), len(feature_cols)]
        metrics["stream_target_metrics"] = {}

    if args.mode == "simulate-retraining":
        metrics["weekly_retraining_runs"] = _simulate_weekly_retraining(
            time_split.train,
            time_split.stream,
            feature_cols,
            target_cols,
            args,
            base_metadata=time_split.metadata,
        )

    save_artifacts(
        output_dir,
        model,
        scalers,
        metrics,
        predictions_sample,
    )
    print(f"train rows: {len(time_split.train):,}")
    print(f"stream rows: {len(time_split.stream):,}")
    print(f"X shape: {tuple(metrics['x_shape'])}")
    print(f"y shape: {tuple(metrics['y_shape'])}")
    print(f"final train loss: {metrics['history']['train_loss'][-1]:.6f}")
    print(f"final val loss: {metrics['history']['val_loss'][-1]:.6f}")
    print(f"stream holdout: {stream_path}")
    print(f"metrics: {output_dir / 'world_model_lstm_metrics.json'}")
    print(f"model: {output_dir / 'world_model_lstm.pt'}")


if __name__ == "__main__":
    main()
