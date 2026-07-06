from typing import overload

import numpy as np

from antupy.core.var import Var, C
from antupy.core.array import Array
from antupy.utils.props import Fluid, Air, Water

SIGMA_CONSTANT = C.sigma

@overload
def temp_sky_simplest(temp_amb: Var) -> Var: ...

@overload
def temp_sky_simplest(temp_amb: Array) -> Array: ...

def temp_sky_simplest(temp_amb: Var|Array) -> Var|Array:
    """simplest function to estimate sky temperature. It is just temp_amb-15.[K]

    Args:
        temp_amb (Var): temperature in K

    Returns:
        Var: sky temperature
    """
    delta_temp_ref = Var(15., "K") if isinstance(temp_amb, Var) else Array(15.*np.ones(len(temp_amb)), "K")
    return (temp_amb - delta_temp_ref)


def h_horizontal_surface_upper_hot(
        temp_s: Var,
        temp_inf: Var,
        length: Var,
        p: Var = Var(101325, "Pa"),
        fluid: Air = Air(),
        correlation: str = "NellisKlein"
    ) -> Var:
    """
    Correlation for natural convection in upper hot surface horizontal plate
    T_s, T_inf          : surface and free fluid temperatures [K]
    L                   : characteristic length [m]
    """
    T_av = ( temp_s + temp_inf )/2
    mu = fluid.mu(T_av, p)
    k = fluid.k(T_av, p)
    rho = fluid.rho(T_av, p)
    cp = fluid.cp(T_av, p)
    alpha = k/(rho*cp)
    beta = 1./temp_s
    visc = mu/rho
    Pr = visc/alpha
    g = 9.81
    Ra = g * beta * abs(temp_s - temp_inf) * Var(length.gv("m")**3,"m3") * Pr / (visc*visc)
    if correlation == "Holman":
        if Ra > Var(1e4,"-") and Ra < Var(1e7,"-"):
            Nu = Var(0.54*float(Ra.gv("-"))**0.25,"-")
            h = (k*Nu/length)
        elif Ra>= Var(1e7,"-") and Ra < Var(1e9,"-"):
            Nu = Var(0.15*float(Ra.gv("-"))**(1./3.), "-")
            h = (k*Nu/length)
        else:
            h = Var(1.52*float((temp_s-temp_inf).gv("K"))**(1./3.), "W/m2-K")
        return Var(h)
    elif correlation == "NellisKlein":
        C_lam  = 0.671 / ( 1+ (0.492/float(Pr.gv("-")))**(9/16) )**(4/9)
        Nu_lam = float(1.4/ np.log(1 + 1.4 / (0.835*C_lam*float(Ra.gv("-"))**0.25) ) )
        C_tur  = 0.14*(1 + 0.0107*float(Pr.gv("-")))/(1+0.01*float(Pr.gv("-")))
        Nu_tur = C_tur * float(Ra.gv("-"))**(1/3)
        Nu = (Nu_lam**10 + Nu_tur**10)**(1/10)
        h = (k*Nu/length)
        return h
    else:
        raise ValueError(f"label {correlation} is not a valid correlation label.")
    

def h_ext_flat_plate(
        temp_surf: Var = Var(300, "K"),
        temp_fluid: Var = Var(400, "K"),
        length: Var = Var(1, "m"),
        u_inf: Var = Var(10, "m/s"),
        Re_crit: Var = Var(4e5, "-"),
        fluid: Fluid = Water(),
) -> Var:
    rho = fluid.rho(temp_fluid)
    cp = fluid.cp(temp_fluid)
    mu = fluid.mu(temp_fluid)
    k = fluid.k(temp_fluid)
    Re_L = rho * u_inf * length / mu
    Pr = cp * mu / k
    Nu_L = (
        0.6774 * Pr.v**(1/3) * Re_crit.v**(1./2)
        / (1 + (0.0468/Pr.v)**(2/3))**(1./4)
        + 0.037*Pr.v**(1/3) * (Re_L.v**0.8 - Re_crit.v**0.8)
        )
    return Var(Nu_L * k / length, "W/m2-K")


def h_ext_flat_plane_constant_flux() -> Var:
    return Var(None, "W/m2-K")

def h_ext_cylinder() -> Var:
    # See page 614 from Nellis&Klein
    return Var(None, "W/m2-K")

def h_ext_sphere() -> Var:
    # See page 619 from Nellis&Klein 
    return Var(None, "W/m2-K")

