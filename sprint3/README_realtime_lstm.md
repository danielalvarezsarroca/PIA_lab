# Real-time LSTM retraining workflow

This workflow trains the Sprint 3 LSTM world model without using future
timestamps in training, scaling, or validation.

## Design decisions

- Source of truth: `sprint3/outputs/world_model_training_dataset.csv`.
- Required precursor: regenerate `master_dataset_world_model.csv` and then
  `world_model_training_dataset.csv` before training.
- Initial split: the newest 20% of unique timestamps is reserved as simulated
  real-time data.
- Split rule: the same timestamp cutoff is applied to every `policy_id`, because
  irrigation scenarios reuse timestamps.
- Scalers: `x_scaler` and `y_scaler` are fit only on the training window set.
- Stream holdout: saved as `sprint3/outputs/world_model_lstm_stream_holdout.csv`.
- Retraining cadence: weekly in simulated time, based on stream timestamps.
- Inference API: `predict_next_state(...)` remains compatible with the dashboard.

## Commands

Create and use a local virtual environment from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pandas streamlit plotly pytest scikit-learn joblib torch
```

The available Python on this machine is 3.13, so `numpy==1.26.4` from
`sprint3/src/requirements.txt` cannot be installed. Use a Python 3.13 compatible
NumPy in this venv, or use Python 3.11 if available.

Initial leakage-safe training:

```powershell
.\.venv\Scripts\python.exe sprint3\train_world_model_lstm.py --mode initial --stream-frac 0.20
```

Weekly simulated retraining:

```powershell
.\.venv\Scripts\python.exe sprint3\train_world_model_lstm.py --mode simulate-retraining --stream-frac 0.20 --retrain-frequency-days 7
```

Smoke test with fewer epochs:

```powershell
.\.venv\Scripts\python.exe sprint3\train_world_model_lstm.py --epochs 1 --batch-size 512 --output-dir C:\tmp\lstm_smoke
```

## Metadata written to artifacts

The scaler payload and metrics JSON include:

- `split_metadata`
- `stream_frac`
- `retrain_frequency_days`
- `scaler_fit_scope`
- `feature_cols`
- `target_cols`
- `window_size`
- model dimensions

`scaler_fit_scope` must be `train_only` for this workflow.
