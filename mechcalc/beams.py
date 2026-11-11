"""Closed-form beam formulas (Euler-Bernoulli, small deflection, linear elastic).

All functions use consistent SI units: N, m, Pa. Deflection is returned as a
positive magnitude in meters.
"""
from __future__ import annotations

import math


def rect_second_moment(b: float, h: float) -> float:
    """Second moment of area of a solid rectangle about its centroidal axis, b*h^3/12."""
    _positive(b=b, h=h)
    return b * h**3 / 12.0


def circle_second_moment(d: float) -> float:
    """Second moment of area of a solid round section, pi*d^4/64."""
    _positive(d=d)
    return math.pi * d**4 / 64.0


def tube_second_moment(d_outer: float, d_inner: float) -> float:
    """Second moment of area of a round tube, pi*(Do^4 - Di^4)/64."""
    _positive(d_outer=d_outer)
    if not 0 <= d_inner < d_outer:
        raise ValueError("d_inner must be >= 0 and smaller than d_outer")
    return math.pi * (d_outer**4 - d_inner**4) / 64.0


def cantilever_point_load(P: float, L: float, E: float, I: float) -> dict:
    """Cantilever with point load P at the free end.

    Returns max deflection (PL^3/3EI), max slope (PL^2/2EI) and max moment (PL),
    all occurring at the free end (moment at the fixed end).
    """
    _positive(L=L, E=E, I=I)
    return {
        "max_deflection": abs(P) * L**3 / (3 * E * I),
        "max_slope": abs(P) * L**2 / (2 * E * I),
        "max_moment": abs(P) * L,
    }


def cantilever_udl(w: float, L: float, E: float, I: float) -> dict:
    """Cantilever with uniformly distributed load w (N/m). Deflection wL^4/8EI."""
    _positive(L=L, E=E, I=I)
    return {
        "max_deflection": abs(w) * L**4 / (8 * E * I),
        "max_slope": abs(w) * L**3 / (6 * E * I),
        "max_moment": abs(w) * L**2 / 2,
    }


def simply_supported_center_load(P: float, L: float, E: float, I: float) -> dict:
    """Simply supported beam with point load P at midspan. Deflection PL^3/48EI."""
    _positive(L=L, E=E, I=I)
    return {
        "max_deflection": abs(P) * L**3 / (48 * E * I),
        "max_slope": abs(P) * L**2 / (16 * E * I),
        "max_moment": abs(P) * L / 4,
    }


def simply_supported_udl(w: float, L: float, E: float, I: float) -> dict:
    """Simply supported beam with UDL w (N/m). Deflection 5wL^4/384EI."""
    _positive(L=L, E=E, I=I)
    return {
        "max_deflection": 5 * abs(w) * L**4 / (384 * E * I),
        "max_slope": abs(w) * L**3 / (24 * E * I),
        "max_moment": abs(w) * L**2 / 8,
    }


def bending_stress(M: float, c: float, I: float) -> float:
    """Flexure formula sigma = M*c/I (Pa)."""
    _positive(I=I)
    return abs(M) * c / I


def _positive(**kwargs: float) -> None:
    for name, value in kwargs.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")
