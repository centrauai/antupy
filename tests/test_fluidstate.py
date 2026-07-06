from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

import antupy as ap

@pytest.mark.parametrize(
    "kwargs",
    [
        {"fluid": "water", "temp": ap.Var(450, "degC"), "p": ap.Var(2, "MPa")},
        {"fluid": "water", "temp": ap.Var(450, "degC"), "rho": ap.Var(999.84, "kg/m3")},
        {"fluid": "water", "p": ap.Var(2, "MPa"), "rho": ap.Var(999.84, "kg/m3")},
        {"fluid": "water", "p": ap.Var(0.1, "MPa"), "temp": ap.Var(300, "K")},
        {"fluid": "water", "p": ap.Var(1, "atm"), "q": ap.Var(1.0, "-")},
        {"fluid": "R134a", "p": ap.Var(200, "kPa"), "temp": ap.Var(-10, "degC")},
    ],
)
def test_fluidstate_main_examples_solve_to_determined(kwargs):
    state = ap.FluidState(**kwargs)

    assert state.status == "DETERMINED"
    assert state.phase in {
        "liquid",
        "gas",
        "twophase",
        "supercritical_liquid",
        "supercritical_gas",
        "supercritical",
        "not_imposed",
    }

    assert isinstance(state.temp, ap.Var)
    assert isinstance(state.rho, ap.Var)
    assert isinstance(state.p, ap.Var)
    assert isinstance(state.v, ap.Var)
    assert isinstance(state.u, ap.Var)
    assert isinstance(state.h, ap.Var)
    assert isinstance(state.s, ap.Var)
    assert isinstance(state.q, ap.Var)


def test_fluidstate_warns_when_no_properties_are_provided():
    with pytest.warns(UserWarning, match="No property provided"):
        state = ap.FluidState(fluid="water")

    assert state.status == "CLEAN"


def test_fluidstate_warns_for_iso_curve_and_update_resolves_state():
    with pytest.warns(UserWarning, match="status is ISO-CURVE"):
        state = ap.FluidState(fluid="water", temp=ap.Var(300, "K"))

    assert state.status == "ISO-CURVE"

    state.update(p=ap.Var(101.325, "kPa"))

    assert state.status == "DETERMINED"
    assert isinstance(state.h, ap.Var)


def test_fluidstate_clean_status_raises_on_property_retrieval():
    with pytest.warns(UserWarning, match="No property provided"):
        state = ap.FluidState(fluid="water")

    assert state.status == "CLEAN"
    with pytest.raises(ValueError, match="No property provided"):
        _ = state.temp


def test_fluidstate_iso_curve_only_allows_provided_property():
    with pytest.warns(UserWarning, match="status is ISO-CURVE"):
        state = ap.FluidState(fluid="water", temp=ap.Var(300, "K"))

    assert state.status == "ISO-CURVE"
    assert state.temp == ap.Var(300, "K")

    with pytest.raises(ValueError, match="Only one property provided"):
        _ = state.p


def test_fluidstate_overdetermined_warns_and_finishes_determined():
    with pytest.warns(UserWarning, match="More than 2 properties provided"):
        state = ap.FluidState(
            fluid="water",
            temp=ap.Var(450, "degC"),
            rho=ap.Var(999.84, "kg/m3"),
            p=ap.Var(2, "MPa"),
        )

    assert state.status == "DETERMINED"
    assert set(state.props_provided) == {"temp", "rho", "p"}


def test_fluidstate_lazy_mode_solves_on_first_property_access():
    state = ap.FluidState(fluid="water", temp=ap.Var(450, "degC"), p=ap.Var(2, "MPa"), lazy=True)

    assert state.status == "CLEAN"
    _ = state.h
    assert state.status == "DETERMINED"


def test_fluidstate_update_with_two_properties_recomputes_state():
    state = ap.FluidState(fluid="water", temp=ap.Var(450, "degC"), p=ap.Var(2, "MPa"))
    state.update(temp=ap.Var(300, "K"), p=ap.Var(101.325, "kPa"))

    assert state.status == "DETERMINED"
    assert set(state.props_provided) == {"temp", "p"}
    assert state.temp == ap.Var(300, "K")
