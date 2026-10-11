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


## User-run Gate 8A numerical result: 2026-10-11

The user executed `gate8a_bsgamma_lo_screen.py` on AF and supplied the
result `work/gate8a_bsgamma_lo_screen.json`: LO charged-scalar
`DeltaC7=-0.06296082441633362`, `DeltaC8=-0.06612190677250937`.
The beta, charged masses, and mixing weights match the intended point:
`tanbeta=5.597170833`, `mH1=300`, `mH2=700`,
`cos²gamma=0.21471339019`, `sin²gamma=0.78528660981`.
Relative to a single Type-II 580 GeV charged state in the **same
LO matching convention**, the contributions are `1.06365651`
and `1.03171185` times the reference values.

**Status:** numerical LO matching implementation ran successfully;
**no numerical flavor exclusion/viability verdict is justified**.

### Critical input-dependence: 2024 HFLAV experimental update

Florentino et al. (2021) used the historical experimental average
BR(B→Xsγ)=(3.32±0.15)e−4 and old single-H+ 580 GeV Type-II
95% bound for context (see Sect. 4.3, Appendix C).

More recent [HFLAV (arXiv:2411.18639)]
(https://arxiv.org/abs/2411.18639) supplies
`BR(B→Xsγ)=(3.49±0.19)e−4` as quoted and utilized by
[EPJC 2025 96 GeV scalar phenomenology]
(https://doi.org/10.1140/epjc/s10052-025-14630-y).
The latter paper finds *approximately* 500 GeV rather than
580–800 GeV in one Type-II-SINGLE charged state treatment with
SuperIso v4.1 and its 2σ error prescription.
This is NOT a validated 500 GeV bound for our two-state Zee model.
Any claimed bound MUST specify flavor theory order, photon cut,
experimental average, uncertainty prescription and whether
R_gamma is included. Avoid importing the 580 GeV threshold as a
hard cut or inferring status from 6% matching differences.

### Next physics gate

Implement or validate the **two-state NLO-compatible matching**
for C7/C8 (plus C4) and evolve to the low scale using an
independent trusted scheme (e.g. a verified customized SuperIso
implementation). Demonstrate reproduction of the exact
single charged-scalar Type-II result for gamma=0 and gamma=pi/2,
compare to Florentino Appendix C and evaluate current HFLAV
measurement at an explicit CL/theory-uncertainty prescription.
Then test the full charged-singlet contribution to oblique S/T/U.
