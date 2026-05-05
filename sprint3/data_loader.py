import re
from pathlib import Path

import pandas as pd
import streamlit as st

from agricultural_rules import build_crop_risk_dataset, generate_agricultural_rules_10min
from ten_min_pipeline import build_modeling_dataset_10min

_DATA_DIR = Path(__file__).parent.parent / "sprint2" / "outputs_sprint2"
_SPRINT3_DIR = Path(__file__).parent

MODELO_PATH    = _DATA_DIR / "dataset_modelizacion_6h.csv"
INTEGRADO_PATH = _DATA_DIR / "dataset_integrado_6h.csv"
RULES_PATH     = _DATA_DIR / "candidate_rotation_rules.csv"
TRACKER_PATH   = _DATA_DIR / "tracker_variance_diagnostic.csv"
HIGH_IEC_PATH  = _DATA_DIR / "high_iec_policy_table.csv"
MASTER_10MIN_PATH = _SPRINT3_DIR / "outputs" / "master_dataset.csv"
OUTPUTS_10MIN_DIR = _SPRINT3_DIR / "outputs_10min"
CROP_RISK_PATH = OUTPUTS_10MIN_DIR / "crop_risk_10min.csv"
AGRICULTURAL_RULES_PATH = OUTPUTS_10MIN_DIR / "agricultural_rules_10min.csv"


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
def _build_agronomy_from_master(crop_type: str = "lechuga") -> tuple[pd.DataFrame, pd.DataFrame]:
    master = pd.read_csv(MASTER_10MIN_PATH, parse_dates=["Time"])
    model = build_modeling_dataset_10min(master)
    crop_risk = build_crop_risk_dataset(model, crop_type=crop_type)
    agricultural_rules = generate_agricultural_rules_10min(crop_risk, crop_type=crop_type)
    return crop_risk, agricultural_rules


@st.cache_data
def load_crop_risk(crop_type: str = "lechuga") -> pd.DataFrame:
    if CROP_RISK_PATH.exists():
        df = pd.read_csv(CROP_RISK_PATH, parse_dates=["Time"])
        return df.sort_values("Time").reset_index(drop=True)
    if MASTER_10MIN_PATH.exists():
        return _build_agronomy_from_master(crop_type=crop_type)[0]
    return pd.DataFrame()


@st.cache_data
def load_agricultural_rules(crop_type: str = "lechuga") -> pd.DataFrame:
    if AGRICULTURAL_RULES_PATH.exists():
        return pd.read_csv(AGRICULTURAL_RULES_PATH)
    if MASTER_10MIN_PATH.exists():
        return _build_agronomy_from_master(crop_type=crop_type)[1]
    return pd.DataFrame()


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
