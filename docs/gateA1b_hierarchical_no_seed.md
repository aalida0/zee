# Gate A1B — General Zee hierarchical normal-ordering seed

Previous step: Chen (2025), arXiv:2508.18757 Table I **B2** texture
reproduced as an algebraic validation. Its `sum_mnu~0.220 eV` exceeds
the 2026-era strong CMB+BAO bounds under minimal Lambda-CDM.
It is NOT our physically accepted Zee benchmark.

## Purpose

Construct ONE independent **general-Zee** lepton Yukawa seed, using
the project's *separate* scalar masses `(300,700) GeV` and charged
mixing `gamma=1.089`, with a normally ordered hierarchical neutrino
spectrum. The construction fixes the low-energy target and solves the
one-loop complex linear equations. **No physical LFV or scalar
constraints have been evaluated.**

Target: `m1=0.001 eV`; `dm21^2=7.49e-5 eV^2`,
`dm31^2=2.534e-3 eV^2`; NuFIT 6.0 illustrative central mixing
angles; `delta=240 deg`, two Majorana phases zero.

Result: `sum mnu=0.0600608441 eV`, satisfying the *numerical threshold*
`sum mnu<0.0642 eV` from DESI DR2+Planck/ACT under stated Lambda-CDM
assumptions (not model-independent acceptance). Reference:
https://arxiv.org/abs/2503.14744. Other analyses and priors give
different bounds, some even below the normal-ordering minimum.

## Analytical method and limitations

In Chen's Higgs-basis convention,
`Mnu = kappa * [f Ml Y + (f Ml Y).T]`, where `f=-f.T`.

A rank-2 antisymmetric `f` has null vector `n`. For fixed target
`Mnu`, solvability requires `n.T @ Mnu @ n = 0` (NOT `n.dagger`).
Set `n=(1,x,t)` with `t=0.25+0.1i`, solve the resulting complex
quadratic for `x`, and construct
`f = scale*[[0,t,-x],[-t,0,1],[x,-1,0]]`.
The scale is chosen to make `max|f|=0.001`.

With `kappa` computed from the scalar candidate, solve 6 independent
complex neutrino-mass equations for 9 complex Yukawas by a
**minimum Euclidean-norm** solution. The resulting complex linear
system has rank 5; its consistency is verified at machine precision.
Neutrino masses alone leave a four-complex-parameter freedom. The
minimum-norm prescription is **a numerical choice, not a physical
flavour symmetry, likelihood fit, or evidence of LFV compatibility**.

## Run on AF

This is a *stacked* PR based on the Gate A1 branch:

```bash
cd /home/aalida/zee
git fetch origin gateA1b-general-zee-hierarchical-no-seed
git switch gateA1b-general-zee-hierarchical-no-seed
python3 -m unittest discover -s tests -p 'test_gateA1b_hierarchical_no_seed.py' -v
python3 scripts/gateA1b_hierarchical_no_seed.py --output work/gateA1b_hierarchical_no_seed.json
```

## Stop/go

**PASS criteria:** complex-matrix closure, rank-five solvability,
input PMNS recovery, a hierarchical sum below a stated cosmological
threshold, open cascade kinematics.

**NOT PASSED/NOT TESTED:** LFV and mu-e conversion; scalar flavour
stability, Type-II quark implementation, b->s gamma, S/T/U, Higgs
bounds, physical charged-Higgs widths and collider signal rates.

Next: Evaluate the candidate against LFV *at the same full scalar
spectrum*; start with a convention-validated implementation of
`tau -> 3mu` and the radiative LFV channels. Do not claim a viable
Paper 1 benchmark before all constraints pass.

References:
- Chen 2025: https://arxiv.org/abs/2508.18757
- Herrero-Garcia et al. 2017: https://arxiv.org/abs/1701.05345
- DESI DR2 neutrino cosmology: https://arxiv.org/abs/2503.14744
- Kitagawa et al. 2026 on textures: https://arxiv.org/abs/2607.08384
