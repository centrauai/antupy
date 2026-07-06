from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
from antupy import Var


# _FLUIDSTATE_PATH = Path(__file__).resolve().parents[1] / "dev" / "cat" / "th" / "fluidstate.py"
# _spec = spec_from_file_location("fluidstate_module", _FLUIDSTATE_PATH)
# _fluidstate_module = module_from_spec(_spec)
# assert _spec is not None and _spec.loader is not None
# _spec.loader.exec_module(_fluidstate_module)
# FluidState = _fluidstate_module.FluidState

from dev.cat.th.fluidstate import FluidState


@pytest.mark.parametrize(
    "kwargs",
    [
        {"fluid": "water", "temp": Var(450, "degC"), "p": Var(2, "MPa")},
        {"fluid": "water", "temp": Var(450, "degC"), "rho": Var(999.84, "kg/m3")},
        {"fluid": "water", "p": Var(2, "MPa"), "rho": Var(999.84, "kg/m3")},
        {"fluid": "water", "p": Var(0.1, "MPa"), "temp": Var(300, "K")},
        {"fluid": "water", "p": Var(1, "atm"), "q": Var(1.0, "-")},
        {"fluid": "R134a", "p": Var(200, "kPa"), "temp": Var(-10, "degC")},
    ],
)
def test_fluidstate_main_examples_solve_to_determined(kwargs):
    state = FluidState(**kwargs)

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

    assert isinstance(state.temp, Var)
    assert isinstance(state.rho, Var)
    assert isinstance(state.p, Var)
    assert isinstance(state.v, Var)
    assert isinstance(state.u, Var)
    assert isinstance(state.h, Var)
    assert isinstance(state.s, Var)
    assert isinstance(state.q, Var)


def test_fluidstate_warns_when_no_properties_are_provided():
    with pytest.warns(UserWarning, match="No property provided"):
        state = FluidState(fluid="water")

    assert state.status == "CLEAN"


def test_fluidstate_warns_for_iso_curve_and_update_resolves_state():
    with pytest.warns(UserWarning, match="status is ISO-CURVE"):
        state = FluidState(fluid="water", temp=Var(300, "K"))

    assert state.status == "ISO-CURVE"

    state.update(p=Var(101.325, "kPa"))

    assert state.status == "DETERMINED"
    assert isinstance(state.h, Var)


def test_fluidstate_clean_status_raises_on_property_retrieval():
    with pytest.warns(UserWarning, match="No property provided"):
        state = FluidState(fluid="water")

    assert state.status == "CLEAN"
    with pytest.raises(ValueError, match="No property provided"):
        _ = state.temp


def test_fluidstate_iso_curve_only_allows_provided_property():
    with pytest.warns(UserWarning, match="status is ISO-CURVE"):
        state = FluidState(fluid="water", temp=Var(300, "K"))

    assert state.status == "ISO-CURVE"
    assert state.temp == Var(300, "K")

    with pytest.raises(ValueError, match="Only one property provided"):
        _ = state.p


def test_fluidstate_overdetermined_warns_and_finishes_determined():
    with pytest.warns(UserWarning, match="More than 2 properties provided"):
        state = FluidState(
            fluid="water",
            temp=Var(450, "degC"),
            rho=Var(999.84, "kg/m3"),
            p=Var(2, "MPa"),
        )

    assert state.status == "DETERMINED"
    assert set(state.props_provided) == {"temp", "rho", "p"}


def test_fluidstate_lazy_mode_solves_on_first_property_access():
    state = FluidState(fluid="water", temp=Var(450, "degC"), p=Var(2, "MPa"), lazy=True)

    assert state.status == "CLEAN"
    _ = state.h
    assert state.status == "DETERMINED"


def test_fluidstate_update_with_two_properties_recomputes_state():
    state = FluidState(fluid="water", temp=Var(450, "degC"), p=Var(2, "MPa"))
    state.update(temp=Var(300, "K"), p=Var(101.325, "kPa"))

    assert state.status == "DETERMINED"
    assert set(state.props_provided) == {"temp", "p"}
    assert state.temp == Var(300, "K")
