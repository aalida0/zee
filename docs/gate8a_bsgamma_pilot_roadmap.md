# Gate 7D closed; Gate 8A preliminary B→Xsγ LO matching screen

## Gate 7D: user-confirmed electroweak scheme closure

AF script `gate7_ew_scheme_audit.py` reported:

- input 1/alpha=127.9, GF=1.16637e-5 GeV^-2;
- UFO derived MW=79.8243597462 GeV, sin²θW=0.23369913342,
  gW=0.6483971672;
- Gate6 width H2→W hheavy=1.07103074347 GeV with its
  different EW inputs;
- scheme adjustment ratio=1.02092436304;
- predicted with UFO inputs: Γ=1.09344137957 GeV;
- MadWidth: Γ=1.09340023452 GeV;
- relative residual = −3.7628957e−5 (0.003763%).

**Gate 7D LO numerical benchmark validation PASSED.**
This statement is limited to LO scalar/quark amplitude/partial-width
diagnostics, *not physical or experimental viability*.

## Gate 8A: flavor screening priority

The primary collider signal `tbHheavy→tb(Z Hlight)` depends on the
same Type-II doublet mixing that enters charged-Higgs contributions
to b→sγ. The 300 GeV light charged state may be flavor relevant
even though it has a suppressed doublet fraction.

Reference: Florentino, Romão and Silva, EPJC 81 (2021) 1148
(https://doi.org/10.1140/epjc/s10052-021-09956-2),
Eq. (B.9) and Appendix C: contributions of both charged scalars
are summed with couplings (X1,Y1)∝cosγ and (X2,Y2)∝sinγ.

With γ=1.089, beta=1.394, mHlight=300, mHheavy=700 GeV:

- cos²γ=0.21471339019, sin²γ=0.78528660981;
- simple 1/m²-weighted heuristic mass ≈500.731 GeV.
  This is **not** a flavor mass limit or a Wilson-coefficient fit.

New `scripts/gate8a_bsgamma_lo_screen.py` evaluates standard
**leading-order matching-scale** charged-scalar ΔC7/ΔC8:

`ΔC_i = Σ_{k=1,2} [ |Y_k|² F_i^(1)(y_k)/3 + X_k Y_k F_i^(2)(y_k)]`,
`y_k = mt²/mHk²`, Type-II `Xk = tanβ (cosγ,-sinγ)`,
`Yk = cotβ (cosγ,-sinγ)`.

At mt input=172 GeV, LO matching values:

| item | ΔC7 | ΔC8 |
|---|---:|---:|
| mixed Zee charged pair | -0.06296082442 | -0.06612190677 |
| single Type-II 580 GeV | -0.05919281628 | -0.06408950982 |
| pair/reference ratio | 1.06365651 | 1.03171185 |

**Caveat:** A 580 GeV historical single-state 2HDM reference
from the 2021 paper is *not* a valid pass/fail threshold for this
two-state Zee model. As of 2025 papers cite bounds anywhere from
~500 to ~800 GeV depending on updated input and treatment.
LO Wilson coefficients alone are NOT BR(B→Xsγ); they exclude
RG running, SM interference, high-order QCD and theory covariance.
Do not label this benchmark excluded, viable or constrained
at a specified CL from this exploratory diagnostic.

## AF commands

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests -v
python3 scripts/gate8a_bsgamma_lo_screen.py \
  --output work/gate8a_bsgamma_lo_screen.json
```

Then implement or run a **validated B→Xsγ full prediction**
using two charged states, reproduce the gamma→0 Type-II
limit and up-to-date experimental/theoretical inputs;
the approved **oblique S/T/U** formulae for mixtures of charged
doublet and singlet must also be evaluated.
Next add Higgs signal/direct searches and optional full neutrino/LFV
fit; the default f_ab=0 diagnostic makes neutrino masses vanish.
