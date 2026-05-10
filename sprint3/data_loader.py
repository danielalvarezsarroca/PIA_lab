import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from agricultural_rules import build_crop_risk_dataset, generate_agricultural_rules_10min
from dashboard_lstm import format_model_status
from rl_policy import build_offline_rl_policy
from world_model_dataset import build_dashboard_model_frame, load_world_model_dataset

_DATA_DIR = Path(__file__).parent.parent / "sprint2" / "outputs_sprint2"
_SPRINT3_DIR = Path(__file__).parent

MODELO_PATH    = _DATA_DIR / "dataset_modelizacion_6h.csv"
INTEGRADO_PATH = _DATA_DIR / "dataset_integrado_6h.csv"
RULES_PATH     = _DATA_DIR / "candidate_rotation_rules.csv"
TRACKER_PATH   = _DATA_DIR / "tracker_variance_diagnostic.csv"
HIGH_IEC_PATH  = _DATA_DIR / "high_iec_policy_table.csv"
WORLD_MODEL_TRAINING_PATH = _SPRINT3_DIR / "outputs" / "world_model_training_dataset.csv"
WORLD_MODEL_PATH = _SPRINT3_DIR / "outputs" / "master_dataset_world_model.csv"
WORLD_MODEL_LSTM_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm.pt"
WORLD_MODEL_LSTM_SCALERS_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm_scalers.joblib"
WORLD_MODEL_LSTM_METRICS_PATH = _SPRINT3_DIR / "outputs" / "world_model_lstm_metrics.json"


@st.cache_data
def load_modelo() -> pd.DataFrame:
    df = pd.read_csv(MODELO_PATH, parse_dates=["Time"])
    df = df.sort_values("Time").reset_index(drop=True)
    return df


@st.cache_data
def load_integrado() -> pd.DataFrame:
    df = pd.read_csv(INTEGRADO_PATH, parse_dates=["Time"])
    df = df.sort_values("Time").reset_index(drop=True)
    return df


@st.cache_data
def load_rules() -> pd.DataFrame:
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
def load_world_model_lstm_prediction_sample() -> pd.DataFrame:
    path = _SPRINT3_DIR / "outputs" / "world_model_lstm_predictions_sample.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


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
        return pd.DataFrame()
    return build_crop_risk_dataset(model_df, crop_type=crop_type, crop_zone=crop_zone)


@st.cache_data
def load_crop_risk(crop_type: str = "lechuga", crop_zone: str = "S1") -> pd.DataFrame:
    return load_crop_risk_for_crop(crop_type, crop_zone=crop_zone)


@st.cache_data
def load_agricultural_rules_for_crop(crop_type: str, crop_zone: str = "S1") -> pd.DataFrame:
    crop_risk = load_crop_risk_for_crop(crop_type, crop_zone=crop_zone)
    if crop_risk.empty:
        return pd.DataFrame()
    return generate_agricultural_rules_10min(crop_risk, crop_type=crop_type)


@st.cache_data
def load_rl_policy_for_crop(crop_type: str, crop_zone: str = "S1") -> pd.DataFrame:
    model_df = load_world_model_dashboard_frame(crop_zone=crop_zone)
    crop_risk = load_crop_risk_for_crop(crop_type, crop_zone=crop_zone)
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
