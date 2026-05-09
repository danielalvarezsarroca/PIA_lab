import pytest
from svg_generator import generate_solar_svg


def test_output_is_string():
    out = generate_solar_svg(hour=12.0, track_angle=35.0, rec_angle=38.0,
                              solar_elevation=75.0, irradiance=600.0)
    assert isinstance(out, str)


def test_output_contains_svg_tag():
    out = generate_solar_svg(12.0, 35.0, 38.0, 75.0, 600.0)
    assert "<svg" in out and "</svg>" in out


def test_panel_rotation_present():
    out = generate_solar_svg(12.0, 35.0, 38.0, 75.0, 600.0)
    assert "rotate(-35" in out


def test_recommended_angle_ghost_present():
    out = generate_solar_svg(12.0, 35.0, 40.0, 75.0, 600.0)
    assert "rotate(-40" in out


def test_different_hours_produce_different_svgs():
    svg_morning = generate_solar_svg(8.0, 30.0, 30.0, 45.0, 300.0)
    svg_afternoon = generate_solar_svg(17.0, 30.0, 30.0, 40.0, 450.0)
    assert svg_morning != svg_afternoon


def test_irradiance_value_is_not_rendered_as_fixed_label():
    out = generate_solar_svg(12.0, 35.0, 38.0, 75.0, 623.0)
    assert "623 W/m" not in out
    assert "W/m²" not in out


def test_zero_track_angle_renders():
    out = generate_solar_svg(6.0, 0.0, 0.0, 10.0, 50.0)
    assert "rotate(-0" in out or "rotate(0" in out


def test_next_state_adds_smooth_animation():
    out = generate_solar_svg(
        12.0, 30.0, 35.0, 75.0, 500.0,
        next_hour=13.0, next_track_angle=40.0, next_rec_angle=42.0,
    )
    assert 'dur="3s"' in out
    assert 'to="-40.0' in out
    assert 'animateTransform attributeName="transform" type="translate"' in out


def test_night_hours_use_night_ambient_palette():
    out = generate_solar_svg(20.0, 0.0, 0.0, 5.0, 30.0)
    assert "#172554" in out


def test_positive_angle_labels_west_orientation():
    out = generate_solar_svg(12.0, 35.0, 38.0, 75.0, 600.0)
    assert "Orientación visual: Oeste" in out


def test_negative_morning_angle_keeps_clockwise_visual_tilt():
    out = generate_solar_svg(6.0, -31.0, -30.0, 42.0, 220.0)
    assert "rotate(31" in out
    assert "Orientación visual: Este" in out


def test_svg_contains_management_action_overlay():
    svg = generate_solar_svg(
        hour=12,
        track_angle=10,
        rec_angle=15,
        solar_elevation=50,
        irradiance=500,
        management_action="poda_sanitaria",
        panel_action="reducir_sombreado",
    )
    assert "management-overlay" in svg
    assert "data-management-action=\"poda_sanitaria\"" in svg


def test_svg_badge_contains_two_labels():
    svg = generate_solar_svg(
        hour=12,
        track_angle=10,
        rec_angle=15,
        solar_elevation=50,
        irradiance=500,
        management_action="activar_riego",
        panel_action="reducir_sombreado",
    )
    assert "AGRONOMICA" in svg
    assert "ENERGETICA" in svg
    assert "Riego activo" in svg
    assert "Reducir sombra" in svg
    assert "Riesgo" not in svg


def test_svg_uses_selected_crop_visual_traits():
    svg = generate_solar_svg(
        hour=12,
        track_angle=10,
        rec_angle=15,
        solar_elevation=50,
        irradiance=500,
        crop_type="tomate",
    )
    assert 'data-crop-type="tomate"' in svg
    assert 'data-crop-shape="vine_fruit"' in svg
    assert "Tomate" in svg
    assert 'data-crop-icon="tomate"' not in svg


def test_svg_renders_pepper_with_distinct_icon_from_tomato():
    tomato_svg = generate_solar_svg(
        hour=12,
        track_angle=10,
        rec_angle=15,
        solar_elevation=50,
        irradiance=500,
        crop_type="tomate",
    )
    pepper_svg = generate_solar_svg(
        hour=12,
        track_angle=10,
        rec_angle=15,
        solar_elevation=50,
        irradiance=500,
        crop_type="pimiento",
    )

    assert 'data-crop-shape="vine_fruit"' in tomato_svg
    assert 'data-crop-shape="pepper_bush"' in pepper_svg
    assert "Pimiento" in pepper_svg
    assert tomato_svg != pepper_svg


def test_svg_supports_allium_and_tuber_crop_icons():
    onion_svg = generate_solar_svg(
        hour=12,
        track_angle=10,
        rec_angle=15,
        solar_elevation=50,
        irradiance=500,
        crop_type="cebolla",
    )
    potato_svg = generate_solar_svg(
        hour=12,
        track_angle=10,
        rec_angle=15,
        solar_elevation=50,
        irradiance=500,
        crop_type="patata",
    )

    assert 'data-crop-type="cebolla"' in onion_svg
    assert 'data-crop-shape="allium"' in onion_svg
    assert "Cebolla" in onion_svg
    assert 'data-crop-type="patata"' in potato_svg
    assert 'data-crop-shape="tuber"' in potato_svg
    assert "Patata" in potato_svg


def test_svg_renders_s1_s2_crop_zone_panel():
    svg = generate_solar_svg(
        hour=12,
        track_angle=10,
        rec_angle=15,
        solar_elevation=50,
        irradiance=500,
        crop_type="tomate",
        crop_type_s1="tomate",
        crop_type_s2="patata",
    )

    assert 'id="crop-zone-panel"' in svg
    assert 'data-crop-zone="S1"' in svg
    assert 'data-crop-zone="S2"' in svg
    assert 'data-crop-type="tomate"' in svg
    assert 'data-crop-type="patata"' in svg
    assert 'id="crop-row-s1"' in svg
    assert 'id="crop-row-s2"' in svg
    assert "S1" in svg
    assert "S2" in svg
    assert "Tomate" in svg
    assert "Patata" in svg


def test_svg_can_render_independent_zone_scene_without_zone_panel():
    svg = generate_solar_svg(
        hour=11,
        track_angle=0,
        rec_angle=10,
        solar_elevation=45,
        irradiance=500,
        management_action="activar_riego",
        panel_action="mantener_placas",
        crop_type="fresa",
        crop_type_s1="lechuga",
        crop_type_s2="fresa",
        zone_label="S2",
        show_zone_panel=False,
    )

    assert 'id="crop-zone-panel"' not in svg
    assert "ZONA S2" in svg
    assert 'data-crop-type="fresa"' in svg
    assert 'data-management-action="activar_riego"' in svg
    assert "Fresa" in svg
