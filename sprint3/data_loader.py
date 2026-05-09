import re
from pathlib import Path

import pandas as pd
import streamlit as st

from agricultural_rules import build_crop_risk_dataset, generate_agricultural_rules_10min
from rl_policy import build_offline_rl_policy
from ten_min_pipeline import build_modeling_dataset_10min, regenerate_candidate_rules_10min

_SPRINT3_DIR = Path(__file__).parent
_DATA_DIR = Path(__file__).parent.parent / "sprint2" / "outputs_sprint2"
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


def _read_time_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Time"])
    return df.sort_values("Time").reset_index(drop=True)


def _load_master_10min() -> pd.DataFrame:
    return _read_time_csv(MASTER_10MIN_PATH)


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


def _uses_default_crop_risk(crop_type: str, crop_zone: str) -> bool:
    return crop_type == "lechuga" and crop_zone == "S1"


@st.cache_data
def load_crop_risk(crop_type: str = "lechuga", crop_zone: str = "S1") -> pd.DataFrame:
    if CROP_RISK_10MIN_PATH.exists() and _uses_default_crop_risk(crop_type, crop_zone):
        return _read_time_csv(CROP_RISK_10MIN_PATH)
    if MASTER_10MIN_PATH.exists() or MODELO_10MIN_PATH.exists():
        return build_crop_risk_dataset(load_modelo(), crop_type=crop_type, crop_zone=crop_zone)
    return pd.DataFrame()


@st.cache_data
def load_crop_risk_for_crop(crop_type: str, crop_zone: str = "S1") -> pd.DataFrame:
    if MASTER_10MIN_PATH.exists() or MODELO_10MIN_PATH.exists():
        return build_crop_risk_dataset(load_modelo(), crop_type=crop_type, crop_zone=crop_zone)
    return pd.DataFrame()


@st.cache_data
def load_agricultural_rules(crop_type: str = "lechuga", crop_zone: str = "S1") -> pd.DataFrame:
    if AGRICULTURAL_RULES_10MIN_PATH.exists() and _uses_default_crop_risk(crop_type, crop_zone):
        return pd.read_csv(AGRICULTURAL_RULES_10MIN_PATH)
    crop_risk = load_crop_risk(crop_type, crop_zone=crop_zone)
    if crop_risk.empty:
        return pd.DataFrame()
    return generate_agricultural_rules_10min(crop_risk, crop_type=crop_type)


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
    crop_risk = load_crop_risk(crop_type, crop_zone=crop_zone)
    if crop_risk.empty:
        return pd.DataFrame()
    return build_offline_rl_policy(load_modelo(), crop_risk)


@st.cache_data
def load_rl_policy_for_crop(crop_type: str, crop_zone: str = "S1") -> pd.DataFrame:
    crop_risk = load_crop_risk_for_crop(crop_type, crop_zone=crop_zone)
    if crop_risk.empty:
        return pd.DataFrame()
    return build_offline_rl_policy(load_modelo(), crop_risk)


@st.cache_data
def load_tracker_diagnostic() -> pd.DataFrame:
    return pd.read_csv(TRACKER_PATH, index_col=0)


@st.cache_data
def load_high_iec() -> pd.DataFrame:
    return pd.read_csv(HIGH_IEC_PATH)


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
