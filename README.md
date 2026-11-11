# mechcalc

Verified mechanical engineering design calculations in plain Python: beams, stress and failure theories, fatigue, bolted joints, and thermal resistance networks.

Every formula is unit-tested against hand calculations or textbook worked examples (Shigley's *Mechanical Engineering Design*, Incropera's *Heat Transfer*). The goal is a small, readable reference that can be used to check engineering answers quickly, including answers produced by AI models.

## Modules

| Module | What it covers |
|---|---|
| `beams` | Second moments of area, cantilever and simply supported deflection, slope and moment, flexure stress |
| `stress` | Mohr's circle principal stresses, von Mises, Tresca, ductile safety factor, shaft bending plus torsion, thin-wall pressure vessels |
| `fatigue` | Marin factors (surface, size, reliability), corrected endurance limit, Goodman, Soderberg and Gerber criteria, S-N life |
| `fasteners` | Torque-preload relation, ISO 898-1 recommended preload, bolt and member stiffness, joint separation |
| `heat` | Conduction and convection resistances, series and parallel networks, junction temperature, heatsink sizing, fin efficiency |

## Quick start

```bash
git clone https://github.com/kevinfajardo25/mechcalc.git
cd mechcalc
pip install -e ".[test]"
pytest -q
```

```python
from mechcalc import beams, fatigue, heat

I = beams.rect_second_moment(b=0.05, h=0.10)                 # m^4
print(beams.cantilever_point_load(P=1000, L=1.0, E=200e9, I=I))

Se = fatigue.marin_endurance_limit(Sut_mpa=690, finish="machined", d_mm=28, reliability=0.99)
print(fatigue.goodman_safety_factor(sigma_a=69.6, sigma_m=48.2, Se=Se, Sut=690))

# Max heatsink resistance for a 25 W chip, Tj max 100 C, ambient 40 C
print(heat.required_sink_resistance(25, 100, 40, r_jc=0.5, r_tim=0.2))  # 1.7 K/W
```

## Worked example

`examples/shaft_design.py` sizes a rotating AISI 1050 CD shaft for infinite life with a Goodman safety factor of 2.0 at 99% reliability:

```
 d (mm)  Se (MPa)  sa (MPa)  sm (MPa)  n_Goodman  n_yield
     16     206.5     373.0     258.4       0.46     0.92
     ...
     25     196.9      97.8      67.7       1.68     3.50
     28     194.5      69.6      48.2       2.34     4.92  <-- selected
```

## Conventions

* SI units throughout (N, m, Pa, K, W) unless a function name says otherwise (for example `Sut_mpa`, `d_mm`), since fatigue correlations are published in MPa and mm.
* Loads are treated as magnitudes; functions return positive maxima.
* Each function's docstring states the formula and its validity limits.

## Why this exists

When reviewing or training AI models on engineering problems, the most common errors are not exotic: a missing factor of 2 in torsion, Tresca applied where von Mises was asked, an endurance limit used without Marin factors, or mixed units. This library is a set of small, trustworthy reference implementations for catching exactly those mistakes. See the companion repo [mecheng-llm-eval](https://github.com/kevinfajardo25/mecheng-llm-eval) for an evaluation set built on top of it.

## License

MIT
