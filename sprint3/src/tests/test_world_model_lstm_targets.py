from sprint3.world_model_dataset import DETERMINISTIC_STATE_COLUMNS, LEARNED_ENDO_COLUMNS


def test_lstm_does_not_learn_minutes_since_last_irrigation():
    assert "minutes_since_last_irr" in DETERMINISTIC_STATE_COLUMNS
    assert "minutes_since_last_irr" not in LEARNED_ENDO_COLUMNS


def test_lstm_still_learns_continuous_soil_and_radiation_targets():
    assert "VWC_R1_sim" in LEARNED_ENDO_COLUMNS
    assert "Delta_VWC_S1_sim" in LEARNED_ENDO_COLUMNS
    assert "Tsoil_R1_sim" in LEARNED_ENDO_COLUMNS
    assert "Delta_Tsoil_S1_sim" in LEARNED_ENDO_COLUMNS
    assert "GPOA_mean" in LEARNED_ENDO_COLUMNS
    assert "Delta_PAR_S1" in LEARNED_ENDO_COLUMNS
