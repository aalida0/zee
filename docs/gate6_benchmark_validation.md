# Gate 6: Zee scalar benchmark reconstruction (provisional)

**Status:** `SCALAR_THEORY_SCREEN_PASS_NOT_VALIDATED_PHYSICAL_POINT`.

Reference: R. R. Florentino, J. C. Romão, J. P. Silva,
[arXiv:2106.08332](https://arxiv.org/abs/2106.08332),
Eqs. (16), (18)–(39), (40), (55), (81)–(82), Appendix C.

## Critical P2 input corrections

The published P2 inputs are:
`mh1=125`, `mh2=580.7`, `mA=633.7` GeV;
`alpha=1.398`, `gamma=1.089` rad;
`m12^2=5.77e4 GeV^2`, `lambdaC=4.473`, `k1=1.082`,
`k2=3.98e-3`, **`k12=-1.266e-3`**.
Previous notes transcribed `k12` with the wrong sign/magnitude.
The paper scans both charged masses and slightly varying beta;
it does not certify every independently chosen mass pair and fixed beta.

## Benchmark used here

`mH1=300 GeV`, `mH2=700 GeV` are still illustrative.
**beta=alpha=1.398 fails BFB**, yielding `lambda1≈-1.609`
(necessary stability test violated).

At `beta=1.394` (tanbeta ≈5.59717), inverse tree-level
mass matching yields (v=246.21965 GeV):

| λ1 | λ2 | λ3 | λ4 | λ5 |
|---:|---:|---:|---:|---:|
| 2.53233 | 0.25231 | 2.64510 | -1.21054 | -1.12678 |

- Charged mixing μ4≈943.400 GeV; charged Goldstone eigenvalue≈0.
- Exact reconstructed masses: 125, 580.7, 633.7, 300, 700 GeV.
- Conservative algebraic **sufficient** quartic BFB proof passes;
  lower-bound coefficients in (x1x2,x1xc,x2xc) are
  (0.30777, 1.080734, 0.002714), all positive.
- Eigenvalues of four scalar-scattering matrices from Appendix C obey
  the tree-level unitarity bound: max |Λ| ≈ 18.137 < 8π≈25.133.
- Gauge-fixed multistart search (7 real fields, allowing complex charged
  directions) found no deeper vacuum in an exploratory scan, but
  **this does not prove global vacuum stability**.
- A coarse beta scan passes these *specific* BFB/unitarity gates
  approximately for `1.3878≲beta≲1.3965`; this is NOT a viable-physics interval.

## Partial tree-level two-body decay inventory at beta=1.394

Approximate widths in GeV, derived using leading tree interactions:

| H2+ channel | partial width (GeV) |
|---|---:|
| H1+ Z | 9.41134 |
| t bbar (Type-II, mb=4.7, mt=172) | 1.55811 |
| W+ h2 (580.7 GeV neutral) | 1.07103 |
| H1+ h125 (scalar-potential trilinear) | 0.26704 |
| tau+ nu (Type-II component) | 0.03568 |
| W+ h125 | 0.00122 |

Summing ONLY the included channels gives a conditional
`Γ(H2→H1Z)/ΣΓincluded≈0.7624` and `Γ(H1→tb)/ΣΓincluded≈0.9559`.
These are **NOT physical Zee branching fractions**. In particular,
the true Zee singlet has independent lepton-flavor couplings used for
radiative neutrino masses and subject to LFV constraints; those
couplings may add substantial charged-scalar leptonic widths.
Loop corrections, small-flavor modes and off-shell processes are also absent.

## Still required to claim a physical benchmark

1. **Full Zee Lagrangian/UFO**: two charged mass eigenstates, quark
   Type-II Yukawas, lepton antisymmetric Yukawas, all scalar, EW and
   gauge vertices, including the off-diagonal ZH1H2.
2. Full gauge/Ward-identity and coupling/width closure tests.
3. Electroweak oblique S,T,U; B→X_sγ; current Higgs limits and
   scalar searches; neutrino-mass and charged-lepton-flavor-violation fit.
4. A certified neutral global vacuum or stronger numerical evidence
   than the current finite multistart search.
5. Recompute MG5 associated-production cross sections at the *shifted*
   tanbeta≈5.597 rather than reuse the old tanbeta≈5.729 normalization.
6. Re-estimate branching ratios and signal acceptances before Delphes.

**Do not call this point experimentally allowed or the model implementation complete.**
