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


def test_irradiance_label_appears():
    out = generate_solar_svg(12.0, 35.0, 38.0, 75.0, 623.0)
    assert "623" in out


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
