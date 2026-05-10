import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_master_dataset_reg_uses_nanosecond_timestamps_for_episode_ids():
    notebook = json.loads((ROOT / "Master_dataset_reg.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert 'to_numpy(dtype="datetime64[ns]")' in source


def test_policy_timestamp_ids_are_unique_for_all_scenarios():
    compact = pd.read_csv(ROOT / "outputs" / "master_dataset.csv", parse_dates=["Time"], index_col="Time")
    timestamp_ids = compact.index.to_numpy(dtype="datetime64[ns]").astype("int64") // 10**9

    ids = {
        f"{interval_h}h_{dose_mm}mm_{timestamp_id}"
        for interval_h in [4, 6, 8, 12]
        for dose_mm in [1.0, 2.0, 3.0]
        for timestamp_id in timestamp_ids
    }

    assert len(ids) == len(compact) * 12
