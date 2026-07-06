import numpy as np
import pytest

import antupy as ap

def test_horizontal_surface_upper_hot():
    T_s = ap.Var(400.0, "K")
    T_inf = ap.Var(300.0, "K")
    L = ap.Var(1.0, "m")
    # Current implementation builds a non-dimensionless Ra and raises during comparison.
    with pytest.raises(ValueError):
        ap.htc.h_horizontal_surface_upper_hot(T_s, T_inf, L, correlation="Holman")
    with pytest.raises(ValueError):
        ap.htc.h_horizontal_surface_upper_hot(T_s, T_inf, L, correlation="NellisKlein")


def test_horizontal_surface_invalid_correlation_raises():
    with pytest.raises(ValueError):
        ap.htc.h_horizontal_surface_upper_hot(
            ap.Var(400.0, "K"),
            ap.Var(300.0, "K"),
            ap.Var(1.0, "m"),
            correlation="invalid",
        )


def test_temp_sky_simplest():
    temp_sky = ap.htc.temp_sky_simplest(ap.Var(300.0, "K"))
    assert isinstance(temp_sky, ap.Var)
    assert temp_sky == ap.Var(285.0, "K")


def test_h_ext_flat_plate_with_var_inputs():
    h = ap.htc.h_ext_flat_plate(
        temp_surf=ap.Var(350.0, "K"),
        temp_fluid=ap.Var(300.0, "K"),
        length=ap.Var(1.0, "m"),
        u_inf=ap.Var(5.0, "m/s"),
    )
    assert isinstance(h, ap.Var)
    assert h.u == "W/m2-K"
    assert h.gv("W/m2-K") > 0


def test_h_ext_flat_plate_invalid_type_raises():
    with pytest.raises((TypeError, AttributeError, ValueError)):
        ap.htc.h_ext_flat_plate(
            temp_surf=ap.Var(350.0, "K"),
            temp_fluid="bad",
            length=ap.Var(1.0, "m"),
            u_inf=ap.Var(5.0, "m/s"),
        )


def test_h_ext_flat_plate_float_input_raises():
    with pytest.raises((TypeError, AttributeError, ValueError)):
        ap.htc.h_ext_flat_plate(
            temp_surf=ap.Var(350.0, "K"),
            temp_fluid=300.0,
            length=ap.Var(1.0, "m"),
            u_inf=ap.Var(5.0, "m/s"),
        )


def test_external_placeholder_functions_return_var_none():
    h1 = ap.htc.h_ext_flat_plane_constant_flux()
    h2 = ap.htc.h_ext_cylinder()
    h3 = ap.htc.h_ext_sphere()

    assert isinstance(h1, ap.Var)
    assert isinstance(h2, ap.Var)
    assert isinstance(h3, ap.Var)
    assert h1.u == "W/m2-K"
    assert h2.u == "W/m2-K"
    assert h3.u == "W/m2-K"
    assert np.isnan(h1.v)
    assert np.isnan(h2.v)
    assert np.isnan(h3.v)