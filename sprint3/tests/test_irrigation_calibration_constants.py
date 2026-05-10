import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _notebook_source() -> str:
    notebook = json.loads((ROOT / "Master_dataset_reg.ipynb").read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])


def test_irrigation_calibration_uses_moderate_soil_water_response():
    source = _notebook_source()

    assert 'K_IN    = {"R1": 0.0100, "S1": 0.0110}' in source
    assert 'K_ET    = {"R1": 0.10,   "S1": 0.085}' in source
    assert "K_DRAIN = 0.05" in source
    assert "ET_C0      = 0.006" in source
