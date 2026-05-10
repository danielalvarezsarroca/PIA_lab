from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from world_model_dataset import ACTION_COLUMNS, DETERMINISTIC_STATE_COLUMNS, ENDO_COLUMNS, EXO_COLUMNS, LEARNED_ENDO_COLUMNS
from world_model_lstm import WorldModelLSTM
from world_model_lstm_dataset import fit_window_scalers, make_policy_windows, split_windows_chronologically
from world_model_lstm_training import predict, regression_metrics, save_artifacts, train_model


BASE_DIR = Path(__file__).resolve().parent
TRAINING_DATASET = BASE_DIR / "outputs" / "world_model_training_dataset.csv"
OUTPUT_DIR = BASE_DIR / "outputs"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train LSTM World Model on reward-enriched agrovoltaic transitions.")
    parser.add_argument("--dataset", type=Path, default=TRAINING_DATASET)
    parser.add_argument("--window-size", type=int, default=12)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--num-layers", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    df = pd.read_csv(args.dataset, parse_dates=["Time"])
    feature_cols = EXO_COLUMNS + ACTION_COLUMNS + ENDO_COLUMNS
    target_cols = [f"next_{column}" for column in LEARNED_ENDO_COLUMNS]
    clean_df = df.dropna(subset=feature_cols + target_cols).sort_values(["policy_id", "Time"]).reset_index(drop=True)
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
        "rows_loaded": int(len(df)),
        "rows_after_dropna": int(len(clean_df)),
        "window_size": int(args.window_size),
        "x_shape": list(scaled.x_scaled.shape),
        "y_shape": list(scaled.y_scaled.shape),
        "history": history,
        "target_metrics": target_metrics,
    }
    sample = pd.DataFrame(y_true[:250], columns=[f"actual_{column}" for column in target_cols])
    pred = pd.DataFrame(y_pred[:250], columns=[f"pred_{column}" for column in target_cols])
    predictions_sample = pd.concat([sample, pred], axis=1)
    save_artifacts(
        OUTPUT_DIR,
        model,
        {
            "x_scaler": scaled.x_scaler,
            "y_scaler": scaled.y_scaler,
            "feature_cols": feature_cols,
            "target_cols": target_cols,
            "window_size": int(args.window_size),
            "hidden_size": int(args.hidden_size),
            "num_layers": int(args.num_layers),
            "deterministic_state_cols": DETERMINISTIC_STATE_COLUMNS,
            "learned_endo_cols": LEARNED_ENDO_COLUMNS,
        },
        metrics,
        predictions_sample,
    )
    print(f"X shape: {scaled.x_scaled.shape}")
    print(f"y shape: {scaled.y_scaled.shape}")
    print(f"final train loss: {history['train_loss'][-1]:.6f}")
    print(f"final val loss: {history['val_loss'][-1]:.6f}")
    print(f"metrics: {OUTPUT_DIR / 'world_model_lstm_metrics.json'}")
    print(f"model: {OUTPUT_DIR / 'world_model_lstm.pt'}")


if __name__ == "__main__":
    main()
