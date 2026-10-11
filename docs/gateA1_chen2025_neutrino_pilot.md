# Gate A1 — Chen 2025 Zee neutrino benchmark pilot

**Scope:** limited reproduction of the lepton-sector neutrino mass matrix
from Chuan-Hung Chen, [arXiv:2508.18757](https://arxiv.org/abs/2508.18757),
Eqs. (5), (6), (11), Table I (normal ordering). This is **not** a complete,
physically allowed Type-II-quark Zee benchmark or an LFV validation.

## AF commands

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests -p 'test_gateA1_chen2025.py' -v
python3 scripts/gateA1_chen2025_pilot.py --output work/gateA1_chen2025.json
```

Dependencies: Python 3, NumPy, SciPy. No MG5/UFO/ScannerS required.

## Physical interpretation

1. Eq. (5) in Chen's convention is
   `Mnu = kappa*(f @ diag(me,mm,mtau) @ Y + (f @ diag(me,mm,mtau) @ Y).T)`.
   Do **not** mix `kappa` and Yukawa normalizations from different papers.
2. The printed parameters are rounded. A fit restricted **only to each
   printed last-digit rounding interval** yields five oscillation observables
   in the *individual marginal* NuFIT 6.0 normal-ordering 3-sigma bands.
   This is neither a correlated likelihood nor a reconstruction of the
   author's unknown unrounded parameter values.
3. The Chen reference assumes `kappa=1e-5`. The separate illustrative
   300/700 GeV scalar spectrum at `gamma=1.089` implies
   `kappa≈-0.01246336` by Chen Eq. (6). Holding Y fixed and replacing
   `f -> f*kappa_ref/kappa_scalar` preserves Mnu algebraically.
   This does **not** preserve the LFV predictions.
4. The 700 -> 300 + Z charged-scalar decay is kinematically allowed, and
   its off-diagonal Z coupling is nonzero. No full width, allowed branching
   fraction or collision rate is established.
5. Y(mu,mu) is of order 0.118. Any complete charged-scalar width must
   include the corresponding leptonic modes **without double-counting**
   the previously estimated Type-II leptonic pieces.

## Blockers before interpreting as a physically allowed benchmark

- The benchmark leptonic fit must satisfy up-to-date LFV constraints,
  notably mu->e gamma, tau->mu gamma, tau->3mu and mu->e conversion,
  including neutral Higgs and charged scalar contributions.
- Chen's illustrative 150/200 GeV neutral scalar masses are not the
  project's 580.7/633.7 GeV scalar masses.
- Neutrino sum near 0.22 eV can be in tension with restrictive
  cosmological fits; cosmological-model assumptions must be specified.
- Type-II quark plus general lepton Yukawas require a coherent flavour
  model and radiative-stability assessment.
- Two-state b->s gamma, S/T/U, HiggsTools bounds, full widths and
  production are not included here.

**Gate A1 result:** neutrino algebra and a rounding-compatible
oscillation reproduction PASS. **Full physical benchmark: UNVALIDATED.**
Next: compute full LFV at one matched scalar/lepton point, not a broad scan.
