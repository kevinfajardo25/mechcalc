"""High-cycle fatigue helpers for steels (Shigley-style approach)."""
from __future__ import annotations

import math

# Surface factor constants ka = a * Sut^b, Sut in MPa (Shigley Table 6-2)
_SURFACE = {
    "ground": (1.58, -0.085),
    "machined": (4.51, -0.265),
    "cold_drawn": (4.51, -0.265),
    "hot_rolled": (57.7, -0.718),
    "as_forged": (272.0, -0.995),
}

_RELIABILITY = {0.50: 1.0, 0.90: 0.897, 0.95: 0.868, 0.99: 0.814, 0.999: 0.753, 0.9999: 0.702}


def endurance_limit_unmodified(Sut_mpa: float) -> float:
    """Rotating-beam endurance limit Se' for steel: 0.5*Sut up to 1400 MPa, else 700 MPa."""
    return 0.5 * Sut_mpa if Sut_mpa <= 1400 else 700.0


def surface_factor(Sut_mpa: float, finish: str) -> float:
    a, b = _SURFACE[finish]
    return a * Sut_mpa**b


def size_factor(d_mm: float) -> float:
    """Size factor kb for a rotating round bar in bending or torsion."""
    if d_mm <= 2.79:
        return 1.0
    if d_mm <= 51:
        return 1.24 * d_mm**-0.107
    if d_mm <= 254:
        return 1.51 * d_mm**-0.157
    raise ValueError("size factor correlation only valid up to 254 mm")


def reliability_factor(reliability: float) -> float:
    try:
        return _RELIABILITY[reliability]
    except KeyError as exc:
        raise ValueError(f"supported reliabilities: {sorted(_RELIABILITY)}") from exc


def marin_endurance_limit(Sut_mpa: float, finish: str, d_mm: float, reliability: float = 0.50,
                          kc: float = 1.0, kd: float = 1.0, kf_misc: float = 1.0) -> float:
    """Corrected endurance limit Se = ka*kb*kc*kd*ke*kf*Se' (MPa)."""
    return (surface_factor(Sut_mpa, finish) * size_factor(d_mm) * kc * kd
            * reliability_factor(reliability) * kf_misc * endurance_limit_unmodified(Sut_mpa))


def goodman_safety_factor(sigma_a: float, sigma_m: float, Se: float, Sut: float) -> float:
    """Modified Goodman: 1/n = sa/Se + sm/Sut."""
    inv = sigma_a / Se + max(sigma_m, 0.0) / Sut
    return math.inf if inv == 0 else 1.0 / inv


def soderberg_safety_factor(sigma_a: float, sigma_m: float, Se: float, Sy: float) -> float:
    """Soderberg (conservative): 1/n = sa/Se + sm/Sy."""
    inv = sigma_a / Se + max(sigma_m, 0.0) / Sy
    return math.inf if inv == 0 else 1.0 / inv


def gerber_safety_factor(sigma_a: float, sigma_m: float, Se: float, Sut: float) -> float:
    """Gerber parabola solved for n (Shigley Eq. 6-47)."""
    if sigma_a == 0:
        return Sut / sigma_m if sigma_m > 0 else math.inf
    if sigma_m <= 0:
        return Se / sigma_a
    r = (2 * sigma_m * Se) / (Sut * sigma_a)
    return 0.5 * (Sut / sigma_m) ** 2 * (sigma_a / Se) * (-1 + math.sqrt(1 + r**2))


def basquin_life(sigma_a: float, Sut_mpa: float, Se_mpa: float, f: float = 0.9) -> float:
    """Cycles to failure from the S-N line between 10^3 and 10^6 cycles.

    Uses a = (f*Sut)^2/Se and b = -1/3*log10(f*Sut/Se). Returns inf below Se.
    """
    if sigma_a <= Se_mpa:
        return math.inf
    a = (f * Sut_mpa) ** 2 / Se_mpa
    b = -math.log10(f * Sut_mpa / Se_mpa) / 3.0
    return (sigma_a / a) ** (1.0 / b)
