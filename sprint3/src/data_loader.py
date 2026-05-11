import json
import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

_SPRINT3_DIR = Path(__file__).parent.parent
if str(_SPRINT3_DIR) not in sys.path:
    sys.path.insert(0, str(_SPRINT3_DIR))

from agricultural_rules import build_crop_risk_dataset, generate_agricultural_rules_10min
from dashboard_lstm import format_model_status
from rl_policy import build_offline_rl_policy
from ten_min_pipeline import build_modeling_dataset_10min, regenerate_candidate_rules_10min
from world_model_dataset import build_dashboard_model_frame, load_world_model_dataset

_DATA_DIR = Path(__file__).parent.parent.parent / "sprint2" / "outputs_sprint2"
_OUTPUTS_10MIN_DIR = _SPRINT3_DIR / "outputs_10min"

MODELO_PATH    = _DATA_DIR / "dataset_modelizacion_6h.csv"
INTEGRADO_PATH = _DATA_DIR / "dataset_integrado_6h.csv"
RULES_PATH     = _DATA_DIR / "candidate_rotation_rules.csv"
TRACKER_PATH   = _DATA_DIR / "tracker_variance_diagnostic.csv"
HIGH_IEC_PATH  = _DATA_DIR / "high_iec_policy_table.csv"
MASTER_10MIN_PATH = _SPRINT3_DIR / "outputs" / "master_dataset.csv"
MODELO_10MIN_PATH = _OUTPUTS_10MIN_DIR / "dataset_modelizacion_10min.csv"
RULES_10MIN_PATH = _OUTPUTS_10MIN_DIR / "candidate_rotation_rules_10min.csv"
CROP_RISK_10MIN_PATH = _OUTPUTS_10MIN_DIR / "crop_risk_10min.csv"
AGRICULTURAL_RULES_10MIN_PATH = _OUTPUTS_10MIN_DIR / "agricultural_rules_10min.csv"
RL_POLICY_10MIN_PATH = _OUTPUTS_10MIN_DIR / "rl_policy_actions_10min.csv"
WORLD_MODEL_TRAINING_PATH = _SPRINT3_DIR / "outputs" / "world_model_training_dataset.csv"
WORLD_MODEL_PATH = _SPRINT3_DIR / "outputs" / "master_dataset_world_model.csv"
WORLD_MODEL_LSTM_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm.pt"
WORLD_MODEL_LSTM_SCALERS_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm_scalers.joblib"
WORLD_MODEL_LSTM_METRICS_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm_metrics.json"
WORLD_MODEL_LSTM_STREAM_HOLDOUT_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm_stream_holdout.csv"
WORLD_MODEL_LSTM_PREDICTIONS_SAMPLE_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm_predictions_sample.csv"


def _read_time_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Time"])
    return df.sort_values("Time").reset_index(drop=True)


def _load_master_10min() -> pd.DataFrame:
    return _read_time_csv(MASTER_10MIN_PATH)


def _uses_default_crop_risk(crop_type: str, crop_zone: str) -> bool:
    return crop_type == "lechuga" and crop_zone == "S1"


@st.cache_data
def load_modelo() -> pd.DataFrame:
    if MODELO_10MIN_PATH.exists():
        return _read_time_csv(MODELO_10MIN_PATH)
    if MASTER_10MIN_PATH.exists():
        return build_modeling_dataset_10min(_load_master_10min())
    return _read_time_csv(MODELO_PATH)


@st.cache_data
def load_integrado() -> pd.DataFrame:
    if MASTER_10MIN_PATH.exists():
        return _load_master_10min()
    return _read_time_csv(INTEGRADO_PATH)


@st.cache_data
def load_rules() -> pd.DataFrame:
    if RULES_10MIN_PATH.exists():
        return pd.read_csv(RULES_10MIN_PATH)
    if MASTER_10MIN_PATH.exists():
        return regenerate_candidate_rules_10min(load_modelo())
    return pd.read_csv(RULES_PATH)


@st.cache_data
def load_tracker_diagnostic() -> pd.DataFrame:
    return pd.read_csv(TRACKER_PATH, index_col=0)


@st.cache_data
def load_high_iec() -> pd.DataFrame:
    return pd.read_csv(HIGH_IEC_PATH)


@st.cache_data
def load_world_model_training_dataset() -> pd.DataFrame:
    if not WORLD_MODEL_TRAINING_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(WORLD_MODEL_TRAINING_PATH, parse_dates=["Time"])


@st.cache_data
def load_world_model_lstm_metrics() -> dict:
    if not WORLD_MODEL_LSTM_METRICS_PATH.exists():
        return {}
    return json.loads(WORLD_MODEL_LSTM_METRICS_PATH.read_text(encoding="utf-8"))


@st.cache_data
def _load_world_model_lstm_stream_holdout(path_str: str) -> pd.DataFrame:
    path = Path(path_str)
    if not path.exists():
        return pd.DataFrame()
    return _read_time_csv(path)


def load_world_model_lstm_stream_holdout() -> pd.DataFrame:
    return _load_world_model_lstm_stream_holdout(str(WORLD_MODEL_LSTM_STREAM_HOLDOUT_PATH))


@st.cache_data
def load_world_model_lstm_prediction_sample() -> pd.DataFrame:
    if not WORLD_MODEL_LSTM_PREDICTIONS_SAMPLE_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(WORLD_MODEL_LSTM_PREDICTIONS_SAMPLE_PATH)


def get_world_model_lstm_artifact_availability() -> dict[str, bool]:
    return {
        "model": WORLD_MODEL_LSTM_PATH.exists(),
        "scalers": WORLD_MODEL_LSTM_SCALERS_PATH.exists(),
        "metrics": bool(load_world_model_lstm_metrics()),
        "stream_holdout": WORLD_MODEL_LSTM_STREAM_HOLDOUT_PATH.exists(),
        "prediction_sample": WORLD_MODEL_LSTM_PREDICTIONS_SAMPLE_PATH.exists(),
    }


@st.cache_data
def load_world_model_recent_window(crop_zone: str = "S1", policy_id: str | None = None, rows: int = 12) -> pd.DataFrame:
    if not WORLD_MODEL_PATH.exists():
        return pd.DataFrame()
    world_df = load_world_model_dataset(WORLD_MODEL_PATH)
    if policy_id is not None and "policy_id" in world_df.columns:
        scoped = world_df[world_df["policy_id"].astype(str).eq(str(policy_id))]
        if not scoped.empty:
            world_df = scoped
    return world_df.sort_values(["policy_id", "Time"]).tail(rows).reset_index(drop=True)


def get_world_model_lstm_status() -> dict[str, str]:
    return format_model_status(
        load_world_model_lstm_metrics(),
        model_exists=WORLD_MODEL_LSTM_PATH.exists(),
        scalers_exist=WORLD_MODEL_LSTM_SCALERS_PATH.exists(),
    )


@st.cache_data
def load_world_model_dashboard_frame(crop_zone: str = "S1") -> pd.DataFrame:
    if not WORLD_MODEL_PATH.exists():
        return pd.DataFrame()
    world_df = load_world_model_dataset(WORLD_MODEL_PATH)
    return build_dashboard_model_frame(world_df, crop_zone=crop_zone)


@st.cache_data
def load_crop_risk_for_crop(crop_type: str, crop_zone: str = "S1") -> pd.DataFrame:
    model_df = load_world_model_dashboard_frame(crop_zone=crop_zone)
    if model_df.empty:
        model_df = load_modelo() if MASTER_10MIN_PATH.exists() or MODELO_10MIN_PATH.exists() else pd.DataFrame()
    if model_df.empty:
        return pd.DataFrame()
    return build_crop_risk_dataset(model_df, crop_type=crop_type, crop_zone=crop_zone)


@st.cache_data
def load_crop_risk(crop_type: str = "lechuga", crop_zone: str = "S1") -> pd.DataFrame:
    if CROP_RISK_10MIN_PATH.exists() and _uses_default_crop_risk(crop_type, crop_zone):
        return _read_time_csv(CROP_RISK_10MIN_PATH)
    return load_crop_risk_for_crop(crop_type, crop_zone=crop_zone)


@st.cache_data
def load_agricultural_rules(crop_type: str = "lechuga", crop_zone: str = "S1") -> pd.DataFrame:
    if AGRICULTURAL_RULES_10MIN_PATH.exists() and _uses_default_crop_risk(crop_type, crop_zone):
        return pd.read_csv(AGRICULTURAL_RULES_10MIN_PATH)
    return load_agricultural_rules_for_crop(crop_type, crop_zone=crop_zone)


@st.cache_data
def load_agricultural_rules_for_crop(crop_type: str, crop_zone: str = "S1") -> pd.DataFrame:
    crop_risk = load_crop_risk_for_crop(crop_type, crop_zone=crop_zone)
    if crop_risk.empty:
        return pd.DataFrame()
    return generate_agricultural_rules_10min(crop_risk, crop_type=crop_type)


@st.cache_data
def load_rl_policy(crop_type: str = "lechuga", crop_zone: str = "S1") -> pd.DataFrame:
    if RL_POLICY_10MIN_PATH.exists() and _uses_default_crop_risk(crop_type, crop_zone):
        return pd.read_csv(RL_POLICY_10MIN_PATH)
    return load_rl_policy_for_crop(crop_type, crop_zone=crop_zone)


@st.cache_data
def load_rl_policy_for_crop(crop_type: str, crop_zone: str = "S1") -> pd.DataFrame:
    model_df = load_world_model_dashboard_frame(crop_zone=crop_zone)
    crop_risk = load_crop_risk_for_crop(crop_type, crop_zone=crop_zone)
    if model_df.empty and (MASTER_10MIN_PATH.exists() or MODELO_10MIN_PATH.exists()):
        model_df = load_modelo()
    if model_df.empty or crop_risk.empty:
        return pd.DataFrame()
    return build_offline_rl_policy(model_df, crop_risk)


def get_latest_record(df: pd.DataFrame) -> pd.Series:
    """Return the last row that has a valid IEC value."""
    valid = df.dropna(subset=["IEC"])
    if valid.empty:
        raise ValueError("No valid records with IEC in dataset")
    return valid.iloc[-1]


def parse_tracker_name(raw: str) -> str:
    """Extract tracker ID like 'M04' from 'tracker_M04 (actual)'."""
    match = re.search(r"(M\d+)", raw)
    return match.group(1) if match else raw
