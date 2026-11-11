"""Stress transformation and failure theories for ductile and brittle materials."""
from __future__ import annotations

import math


def principal_stresses_2d(sx: float, sy: float, txy: float) -> dict:
    """Principal stresses and max in-plane shear for a 2D (plane stress) element.

    Returns sigma_1 >= sigma_2, tau_max (in-plane) and the principal angle in degrees.
    """
    center = (sx + sy) / 2.0
    radius = math.hypot((sx - sy) / 2.0, txy)
    theta_p = 0.5 * math.degrees(math.atan2(2 * txy, sx - sy))
    return {
        "sigma_1": center + radius,
        "sigma_2": center - radius,
        "tau_max_inplane": radius,
        "theta_p_deg": theta_p,
    }


def von_mises_2d(sx: float, sy: float, txy: float) -> float:
    """Von Mises equivalent stress for plane stress."""
    return math.sqrt(sx**2 - sx * sy + sy**2 + 3 * txy**2)


def von_mises_3d(s1: float, s2: float, s3: float) -> float:
    """Von Mises equivalent stress from three principal stresses."""
    return math.sqrt(((s1 - s2) ** 2 + (s2 - s3) ** 2 + (s3 - s1) ** 2) / 2.0)


def tresca_2d(sx: float, sy: float, txy: float) -> float:
    """Tresca equivalent stress (sigma_max - sigma_min) including the out-of-plane 0."""
    p = principal_stresses_2d(sx, sy, txy)
    stresses = (p["sigma_1"], p["sigma_2"], 0.0)
    return max(stresses) - min(stresses)


def safety_factor_ductile(sx: float, sy: float, txy: float, Sy: float, theory: str = "von_mises") -> float:
    """Static factor of safety against yield for a ductile material."""
    theory = theory.lower()
    if theory in ("von_mises", "dist", "distortion_energy"):
        eq = von_mises_2d(sx, sy, txy)
    elif theory in ("tresca", "mss", "max_shear"):
        eq = tresca_2d(sx, sy, txy)
    else:
        raise ValueError(f"unknown theory: {theory}")
    return math.inf if eq == 0 else Sy / eq


def shaft_combined_stress(d: float, M: float, T: float) -> dict:
    """Bending + torsion in a solid round shaft.

    sigma = 32M/(pi d^3), tau = 16T/(pi d^3), von Mises = sqrt(sigma^2 + 3 tau^2).
    """
    if d <= 0:
        raise ValueError("d must be positive")
    sigma = 32 * abs(M) / (math.pi * d**3)
    tau = 16 * abs(T) / (math.pi * d**3)
    return {"sigma": sigma, "tau": tau, "von_mises": math.sqrt(sigma**2 + 3 * tau**2)}


def thin_wall_pressure_vessel(p: float, r: float, t: float) -> dict:
    """Hoop and longitudinal stress in a thin-walled cylinder (valid for r/t > ~10)."""
    if t <= 0 or r <= 0:
        raise ValueError("r and t must be positive")
    return {"hoop": p * r / t, "longitudinal": p * r / (2 * t), "valid_thin_wall": r / t >= 10}
