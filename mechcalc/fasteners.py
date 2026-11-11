"""Bolted joint helpers: torque/preload, stiffness and joint separation."""
from __future__ import annotations

import math

# ISO metric coarse thread tensile stress areas (mm^2)
TENSILE_AREA_MM2 = {
    "M3": 5.03, "M4": 8.78, "M5": 14.2, "M6": 20.1, "M8": 36.6,
    "M10": 58.0, "M12": 84.3, "M16": 157.0, "M20": 245.0, "M24": 353.0,
}

# ISO 898-1 proof strength (MPa) by property class
PROOF_STRENGTH_MPA = {"4.6": 225, "5.8": 380, "8.8": 600, "10.9": 830, "12.9": 970}


def preload_from_torque(T: float, d: float, K: float = 0.2) -> float:
    """Short-form torque equation F = T / (K*d). T in N*m, d in m, returns N."""
    if d <= 0 or K <= 0:
        raise ValueError("d and K must be positive")
    return T / (K * d)


def torque_for_preload(F: float, d: float, K: float = 0.2) -> float:
    return K * F * d


def recommended_preload(size: str, grade: str, reusable: bool = True) -> float:
    """Shigley guidance: Fi = 0.75*Fp (reusable) or 0.90*Fp (permanent). Returns N."""
    Fp = TENSILE_AREA_MM2[size] * PROOF_STRENGTH_MPA[grade]
    return (0.75 if reusable else 0.90) * Fp


def bolt_stiffness(d: float, L_grip: float, E: float = 207e9) -> float:
    """Simple bolt stiffness kb = A*E/L using the nominal shank area."""
    return (math.pi * d**2 / 4) * E / L_grip


def member_stiffness(d: float, L_grip: float, E: float = 207e9) -> float:
    """Member stiffness via the 30-degree frustum (Shigley Eq. 8-23) for identical members."""
    num = math.pi * E * d * math.tan(math.radians(30))
    den = 2 * math.log(5 * (L_grip * math.tan(math.radians(30)) + 0.5 * d)
                       / (L_grip * math.tan(math.radians(30)) + 2.5 * d))
    return num / den


def joint_analysis(Fi: float, P: float, kb: float, km: float) -> dict:
    """Load sharing for an external tensile load P on a preloaded joint."""
    C = kb / (kb + km)
    Fb = Fi + C * P
    Fm = Fi - (1 - C) * P
    n_sep = Fi / (P * (1 - C)) if P > 0 else math.inf
    return {"joint_constant": C, "bolt_load": Fb, "member_load": Fm,
            "separation_safety_factor": n_sep, "separated": Fm <= 0}
