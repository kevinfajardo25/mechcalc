"""Tests checked against hand calculations and textbook worked examples (Shigley 10th ed.)."""
import math

import pytest

from mechcalc import beams, fasteners, fatigue, heat, stress


def approx(x, rel=1e-3):
    return pytest.approx(x, rel=rel)


# ---------- beams ----------
def test_rect_second_moment():
    assert beams.rect_second_moment(0.05, 0.1) == approx(4.1667e-6)


def test_cantilever_point_load_deflection():
    # 1 kN at end of 1 m steel cantilever, 50x100 mm section
    I = beams.rect_second_moment(0.05, 0.1)
    out = beams.cantilever_point_load(1000, 1.0, 200e9, I)
    assert out["max_deflection"] == approx(1000 / (3 * 200e9 * I))
    assert out["max_moment"] == 1000


def test_simply_supported_udl_ratio():
    # Center load equivalent: 5/384 wL^4 vs 1/48 PL^3 with P = wL -> ratio 5/8
    I, E, L, w = 1e-6, 200e9, 2.0, 500.0
    udl = beams.simply_supported_udl(w, L, E, I)["max_deflection"]
    pt = beams.simply_supported_center_load(w * L, L, E, I)["max_deflection"]
    assert udl / pt == approx(5 / 8)


def test_negative_dimension_rejected():
    with pytest.raises(ValueError):
        beams.rect_second_moment(-1, 1)


# ---------- stress ----------
def test_principal_stresses_mohr_circle():
    p = stress.principal_stresses_2d(80, -40, 25)
    assert p["sigma_1"] == approx(85.0)
    assert p["sigma_2"] == approx(-45.0)
    assert p["tau_max_inplane"] == approx(65.0)


def test_von_mises_pure_shear():
    # Pure shear tau -> sqrt(3) * tau
    assert stress.von_mises_2d(0, 0, 50) == approx(math.sqrt(3) * 50)


def test_von_mises_2d_matches_3d():
    p = stress.principal_stresses_2d(120, 30, 40)
    assert stress.von_mises_2d(120, 30, 40) == approx(stress.von_mises_3d(p["sigma_1"], p["sigma_2"], 0))


def test_tresca_more_conservative_than_von_mises():
    for state in [(100, 0, 0), (100, -100, 0), (60, 20, 45)]:
        assert stress.tresca_2d(*state) >= stress.von_mises_2d(*state) - 1e-9


def test_shaft_combined_stress():
    out = stress.shaft_combined_stress(0.03, 200, 150)
    assert out["sigma"] == approx(32 * 200 / (math.pi * 0.03**3))
    assert out["tau"] == approx(16 * 150 / (math.pi * 0.03**3))


def test_pressure_vessel():
    out = stress.thin_wall_pressure_vessel(2e6, 0.5, 0.01)
    assert out["hoop"] == approx(100e6)
    assert out["longitudinal"] == approx(50e6)
    assert out["valid_thin_wall"]


# ---------- fatigue ----------
def test_surface_factor_machined_shigley_example():
    assert fatigue.surface_factor(520, "machined") == approx(0.860, rel=5e-3)


def test_size_factor_32mm():
    assert fatigue.size_factor(32) == approx(0.858, rel=5e-3)


def test_endurance_cap():
    assert fatigue.endurance_limit_unmodified(1600) == 700


def test_goodman_simple():
    assert fatigue.goodman_safety_factor(100, 200, 200, 400) == approx(1.0)


def test_gerber_less_conservative_than_goodman():
    g = fatigue.goodman_safety_factor(80, 150, 200, 600)
    ger = fatigue.gerber_safety_factor(80, 150, 200, 600)
    assert ger > g


def test_basquin_bounds():
    Sut, Se = 600.0, 250.0
    assert fatigue.basquin_life(0.9 * Sut, Sut, Se) == approx(1e3, rel=1e-6)
    assert fatigue.basquin_life(Se * 1.000001, Sut, Se) == approx(1e6, rel=1e-3)
    assert fatigue.basquin_life(Se * 0.9, Sut, Se) == math.inf


# ---------- fasteners ----------
def test_recommended_preload_m10_88():
    assert fasteners.recommended_preload("M10", "8.8") == approx(0.75 * 58.0 * 600)


def test_torque_preload_roundtrip():
    F = fasteners.preload_from_torque(50, 0.010, 0.2)
    assert F == approx(25000)
    assert fasteners.torque_for_preload(F, 0.010, 0.2) == approx(50)


def test_joint_separation():
    out = fasteners.joint_analysis(Fi=20000, P=10000, kb=1e9, km=3e9)
    assert out["joint_constant"] == approx(0.25)
    assert out["bolt_load"] == approx(22500)
    assert out["separation_safety_factor"] == approx(20000 / 7500)
    assert not out["separated"]


def test_member_stiffer_than_bolt_typical():
    d, L = 0.012, 0.040
    assert fasteners.member_stiffness(d, L) > fasteners.bolt_stiffness(d, L)


# ---------- heat ----------
def test_junction_temperature_chain():
    tj = heat.junction_temperature(25, 40, 0.5, 0.2, 1.3)
    assert tj == approx(90.0)


def test_required_sink_resistance():
    assert heat.required_sink_resistance(25, 100, 40, 0.5, 0.2) == approx(1.7)


def test_parallel_resistors():
    assert heat.parallel(2.0, 2.0) == approx(1.0)


def test_fin_efficiency_limits():
    assert 0 < heat.fin_efficiency_straight(25, 200, 0.002, 0.03) < 1
    # Very short fin approaches 100% efficiency
    assert heat.fin_efficiency_straight(25, 200, 0.002, 1e-5) == approx(1.0, rel=1e-2)
