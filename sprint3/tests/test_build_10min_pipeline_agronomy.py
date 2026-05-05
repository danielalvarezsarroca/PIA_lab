import pandas as pd

from build_10min_pipeline import build_10min_pipeline
from tests.test_agricultural_rules import _stress_sample


def test_build_10min_pipeline_writes_agricultural_demo_outputs(tmp_path):
    master_path = tmp_path / "master_dataset.csv"
    _stress_sample().to_csv(master_path, index=False)

    paths = build_10min_pipeline(
        master_path=master_path,
        output_dir=tmp_path / "outputs",
        backup_6h_paths=[],
        crop_type="lechuga",
    )

    assert paths["crop_risk"].exists()
    assert paths["agricultural_rules"].exists()
    assert paths["crop_profiles"].exists()
    assert pd.read_csv(paths["agricultural_rules"])["cultivo"].eq("lechuga").all()
