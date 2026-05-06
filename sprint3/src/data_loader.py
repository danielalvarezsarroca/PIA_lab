import re
from pathlib import Path

import pandas as pd
import streamlit as st

_DATA_DIR = Path(__file__).parent.parent.parent / "sprint2" / "outputs_sprint2"

MODELO_PATH    = _DATA_DIR / "dataset_modelizacion_6h.csv"
INTEGRADO_PATH = _DATA_DIR / "dataset_integrado_6h.csv"
RULES_PATH     = _DATA_DIR / "candidate_rotation_rules.csv"
TRACKER_PATH   = _DATA_DIR / "tracker_variance_diagnostic.csv"
HIGH_IEC_PATH  = _DATA_DIR / "high_iec_policy_table.csv"


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
