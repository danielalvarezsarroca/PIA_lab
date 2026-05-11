import pandas as pd

from build_10min_pipeline import build_10min_pipeline
from tests.test_rl_policy import _stress_sample_with_night_rows


def test_build_10min_pipeline_writes_agricultural_demo_outputs(tmp_path):
    master_path = tmp_path / "master_dataset.csv"
    _stress_sample_with_night_rows().to_csv(master_path, index=False)

    paths = build_10min_pipeline(
        master_path=master_path,
        output_dir=tmp_path / "outputs",
        backup_6h_paths=[],
        crop_type="lechuga",
    )

    assert paths["crop_risk"].exists()
    assert paths["agricultural_rules"].exists()
    assert paths["crop_profiles"].exists()
    assert paths["rl_policy"].exists()
    assert paths["rl_policy_metadata"].exists()
    assert paths["rl_trajectories"].exists()
    assert paths["rl_trajectories_metadata"].exists()
    assert pd.read_csv(paths["agricultural_rules"])["cultivo"].eq("lechuga").all()
    assert pd.read_csv(paths["rl_policy"])["source"].eq("offline_rl_tabular_masterdataset").all()
    trajectories = pd.read_csv(paths["rl_trajectories"])
    assert trajectories["is_night"].any()
    assert "irrigation_active" in trajectories.columns


def test_build_10min_pipeline_can_generate_independent_crop_zone_outputs(tmp_path):
    master_path = tmp_path / "master_dataset.csv"
    _stress_sample_with_night_rows().to_csv(master_path, index=False)

    paths = build_10min_pipeline(
        master_path=master_path,
        output_dir=tmp_path / "outputs",
        backup_6h_paths=[],
        crop_type="patata",
        crop_zone="S2",
    )

    metadata = pd.read_json(paths["metadata"], typ="series")
    crop_risk = pd.read_csv(paths["crop_risk"])
    rules = pd.read_csv(paths["agricultural_rules"])
    trajectories = pd.read_csv(paths["rl_trajectories"])

    assert metadata["crop_type"] == "patata"
    assert metadata["crop_zone"] == "S2"
    assert crop_risk["crop_type"].eq("patata").all()
    assert crop_risk["crop_zone"].eq("S2").all()
    assert rules["cultivo"].eq("patata").all()
    assert trajectories["crop_type"].eq("patata").all()
    assert trajectories["crop_zone"].eq("S2").all()
    assert "VWC_crop_zone_fraction" in trajectories.columns
