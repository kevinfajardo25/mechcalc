"""Worked example: size a rotating steel shaft for infinite fatigue life.

Problem
-------
A machined AISI 1050 CD shaft (Sut = 690 MPa, Sy = 580 MPa) carries a fully
reversed bending moment of 150 N*m and a steady torque of 120 N*m.
Find the smallest standard diameter that gives a Goodman factor of safety >= 2.0
at 99% reliability. Stress concentration is ignored for this first pass.

Run:  python examples/shaft_design.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mechcalc import fatigue  # noqa: E402

SUT, SY = 690.0, 580.0          # MPa
M_A, T_M = 150.0, 120.0         # N*m (alternating bending, mean torque)
TARGET_N = 2.0
STANDARD_D_MM = [16, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 45, 50]

print(f"{'d (mm)':>7} {'Se (MPa)':>9} {'sa (MPa)':>9} {'sm (MPa)':>9} {'n_Goodman':>10} {'n_yield':>8}")
for d_mm in STANDARD_D_MM:
    d = d_mm / 1000
    Se = fatigue.marin_endurance_limit(SUT, "machined", d_mm, reliability=0.99)
    sigma_a = 32 * M_A / (math.pi * d**3) / 1e6                 # bending, fully reversed
    sigma_m = math.sqrt(3) * 16 * T_M / (math.pi * d**3) / 1e6  # von Mises of steady torsion
    n_f = fatigue.goodman_safety_factor(sigma_a, sigma_m, Se, SUT)
    n_y = SY / (sigma_a + sigma_m)                              # conservative first-cycle yield check
    flag = "  <-- selected" if n_f >= TARGET_N else ""
    print(f"{d_mm:>7} {Se:>9.1f} {sigma_a:>9.1f} {sigma_m:>9.1f} {n_f:>10.2f} {n_y:>8.2f}{flag}")
    if n_f >= TARGET_N:
        break
