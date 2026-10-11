# Gate A1H — complete scalar-sector S,T,U and correlated EWPO screen

**Status:** Candidate **passes the two specific Gaussian oblique-parameter
fits** as a scalar-sector one-loop screening test. This is not a full Zee
phenomenology/global-fit acceptance. This draft PR is stacked on Gate A1G.

## Exact references and conventions

- Grimus et al., [arXiv:0802.4353](https://arxiv.org/abs/0802.4353)
  Eqs. (28), (30), (31), Appendix B/C. The charged-pair coefficient in T
  is **-2** (also Grimus arXiv:0711.4022 Eq.48), not the contradictory
  -1/2 recorded in Herrero-Garcia et al. arXiv:1701.05345 App.A.
- Zee U,V matrices from Florentino et al.
  [arXiv:2106.08332](https://arxiv.org/abs/2106.08332)
  Eqs. (23),(24); **Florentino's h125 alignment** is
  cos(beta-alpha)=1.
- Grimus functions `G` and `Ghat` are evaluated through **finite
  Feynman-parameter quadratures** derived from Eq.(B3),(B11),(C1)-(C5)
  rather than unstable cancellations in the analytic C2/C5 functions.
  These automatically preserve full finite-q² effects and SM Higgs
  subtraction. A numerical value of the independent closed C2 formula
  is tested as an additional check.
- Once translated to physical (unbarred) oblique parameters, both
  Grimus Eqs.(30),(31) carry an overall factor `1/(24*pi)`.
- T imports the identical Gate A1G Grimus -2 implementation. Loop
  EW input `MW=80.379, MZ=91.1876 GeV` is held consistent with Gate
  A1G for apples-to-apples comparison; 2026 fit's W mass input is
  different, and scheme/input variations should be audited before
  publication.

## Scalar benchmark prediction

| Input | Value |
|---|---:|
| mH1+, mH2+ | 300, 700 GeV |
| mh, mH, mA | 125, 580.7, 633.7 GeV |
| alpha, beta, gamma | 1.398, 1.394, 1.089 rad |

```
S = +0.004440433
T = -0.004902178
U = +0.000057337
```

## Documented published correlated fits

**Gfitter July 2026**:
https://project-gfitter.web.cern.ch/Oblique_Parameters/

- Central: `(S,T,U)=(0.03,0.05,-0.03)`
- Sigma: `(0.10,0.12,0.09)`
- Corr ST=+0.92, SU=-0.67, TU=-0.88
- Expected `chi²≈0.872617` relative to fit minimum

**PDG 2025 Table 10.8, with U floating**:
https://pdg.lbl.gov/2025/reviews/rpp2025-rev-standard-model.pdf

- Central: `(0.021,0.04,0.008)`
- Sigma: `(0.096,0.12,0.092)`
- Corr ST=+0.91, SU=-0.62, TU=-0.83
- Expected `chi²≈1.672686`

Use `cov_ij=sigma_i*rho_ij*sigma_j` and
`chi²=(prediction-mean)^T inv(cov) (prediction-mean)`,
with a 3D Gaussian ellipsoid 95% threshold of
`chi²_3d,0.95=7.8147279`. These are *three freely floating oblique
parameters*, not independent 1D upper/lower cuts or a fixed-U fit.

The two cited datasets are alternative **diagnostic comparisons**,
not independent measurements to combine.

## Reproducibility on AF

```bash
cd /home/aalida/zee
git fetch origin gateA1h-correlated-stu-ewpo
git switch gateA1h-correlated-stu-ewpo

python3 -m unittest discover -s tests \
  -p 'test_gateA1h_correlated_stu_ewpo.py' -v

python3 scripts/gateA1h_correlated_stu_ewpo.py \
  --output work/gateA1h_correlated_stu_ewpo.json
```

Regression suite includes (i) independent analytic C2 numerical
cross-check, (ii) large-mass Ghat asymptotic, (iii) integration
convergence 80 vs 200 nodes, (iv) exact charged/neutral mixing,
(v) charged degeneracy/rotation invariance, (vi) T and S,U frozen
numerical benchmarks, (vii) covariance positive-definiteness and
Gaussian likelihood closure, (viii) partial-not-global status.

## Remaining fundamental blockers

1. This EWPO screen only uses scalar self-energies; full new-physics
   flavour/vertex corrections have not been checked.
2. Neutrino and selected one-loop LFV scalar contributions pass,
   but **two-loop Barr–Zee** is missing.
3. **B->Xs gamma** is only at LO screening, not NLO or SuperIso.
4. **HiggsTools and global vacuum** viability are unproven at 300/700.
5. The full Zee Yukawa+Type-II quark symmetries and correct collider
   decay widths/branching fractions require validation.

Next: address flavour and Higgs bounds at this fixed scalar point
before any wide parameter scan or detector-level paper claims.
