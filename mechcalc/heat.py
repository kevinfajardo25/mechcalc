"""1D steady-state heat transfer and thermal resistance networks (electronics cooling)."""
from __future__ import annotations

import math


def r_conduction_plane(L: float, k: float, A: float) -> float:
    """Plane wall conduction resistance L/(kA), K/W."""
    return L / (k * A)


def r_conduction_cylinder(r_in: float, r_out: float, k: float, length: float) -> float:
    """Radial conduction resistance ln(ro/ri)/(2 pi k L), K/W."""
    return math.log(r_out / r_in) / (2 * math.pi * k * length)


def r_convection(h: float, A: float) -> float:
    """Convection resistance 1/(hA), K/W."""
    return 1.0 / (h * A)


def series(*resistances: float) -> float:
    return sum(resistances)


def parallel(*resistances: float) -> float:
    return 1.0 / sum(1.0 / r for r in resistances)


def junction_temperature(power_w: float, t_ambient: float, *resistances: float) -> float:
    """Tj = Ta + Q * sum(R) for a series path (e.g. junction-case-TIM-sink-air)."""
    return t_ambient + power_w * series(*resistances)


def required_sink_resistance(power_w: float, tj_max: float, t_ambient: float,
                             r_jc: float, r_tim: float) -> float:
    """Max allowable heatsink-to-air resistance to keep Tj <= tj_max."""
    budget = (tj_max - t_ambient) / power_w
    return budget - r_jc - r_tim


def fin_efficiency_straight(h: float, k: float, t: float, L: float) -> float:
    """Efficiency of a straight rectangular fin with adiabatic tip (corrected length Lc = L + t/2)."""
    m = math.sqrt(2 * h / (k * t))
    Lc = L + t / 2
    return math.tanh(m * Lc) / (m * Lc)
