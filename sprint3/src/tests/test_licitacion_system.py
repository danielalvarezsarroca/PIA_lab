from agricultural_rules import build_crop_risk_dataset
from licitacion_system import (
    build_biological_baseline,
    build_synthetic_scenarios,
    build_tender_demo_system,
    build_variable_catalog,
)
from rl_policy import build_offline_dqn_policy
from ten_min_pipeline import build_modeling_dataset_10min
from tests.test_agricultural_rules import _stress_sample


def test_variable_catalog_documents_operational_inputs():
    catalog = build_variable_catalog()

    assert not catalog.empty
    assert {
        "variable",
        "nombre_simple",
        "uso_en_sistema",
        "restriccion_biologica",
    }.issubset(catalog.columns)
    assert {"GPOA_mean", "VWC_S1_mean", "Tsoil_S1_mean", "ePAR_S1_mean"}.issubset(
        set(catalog["variable"])
    )


def test_biological_baseline_returns_clear_actions_and_reason():
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga", crop_zone="S1")

    baseline = build_biological_baseline(model.iloc[-1], crop_risk.iloc[-1])

    assert baseline["source"] == "modelo_biologico_simple"
    assert baseline["panel_action"] in {
        "mantener_placas",
        "aumentar_sombreado",
        "reducir_sombreado",
        "posicion_segura",
    }
    assert baseline["crop_management_action"]
    assert baseline["explanation"]


def test_synthetic_scenarios_are_bounded_and_demo_ready():
    model = build_modeling_dataset_10min(_stress_sample())

    scenarios = build_synthetic_scenarios(model.iloc[-1])

    assert len(scenarios) >= 5
    assert scenarios["salud_cultivo_pct"].between(0, 100).all()
    assert scenarios["eficiencia_energetica_pct"].between(0, 100).all()
    assert scenarios["uso_demo"].str.len().gt(0).all()


def test_tender_demo_system_covers_dss_digital_twin_and_control_law():
    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga", crop_zone="S1")
    policy = build_offline_dqn_policy(model, crop_risk, epochs=3, seed=11)

    demo = build_tender_demo_system(model, crop_risk, policy)

    assert demo["coverage"][0]["status"] == "implementado_demo"
    assert demo["digital_twin"]["crop_zone"] == "S1"
    assert demo["dss_comparison"]["dqn"]["source"] == "offline_dqn_double_dqn"
    assert demo["control_law"]["target_angle_deg"] is not None
    assert not demo["synthetic_scenarios"].empty


def test_licitacion_tab_renders_demo_contract(monkeypatch):
    import tabs.tab_licitacion as tab_licitacion

    class FakeColumn:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    class FakeStreamlit:
        def __init__(self):
            self.dataframe_calls = 0

        def markdown(self, *args, **kwargs):
            pass

        def caption(self, *args, **kwargs):
            pass

        def warning(self, *args, **kwargs):
            pass

        def info(self, *args, **kwargs):
            pass

        def columns(self, count):
            return [FakeColumn() for _ in range(count)]

        def dataframe(self, *args, **kwargs):
            self.dataframe_calls += 1

    model = build_modeling_dataset_10min(_stress_sample())
    crop_risk = build_crop_risk_dataset(model, crop_type="lechuga", crop_zone="S1")
    policy = build_offline_dqn_policy(model, crop_risk, epochs=3, seed=11)
    fake_st = FakeStreamlit()

    monkeypatch.setattr(tab_licitacion, "st", fake_st)

    tab_licitacion.render_tab_licitacion(model, crop_risk, policy)

    assert fake_st.dataframe_calls == 3
