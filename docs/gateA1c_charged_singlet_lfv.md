# Gate A1C — radiative LFV charged-singlet contribution ONLY

This gate uses the hierarchical normal-ordering seed established in
Gate A1B. It computes the **charged-singlet f-only** contributions to
mu->e gamma, tau->mu gamma, and tau->e gamma. It does **not**
compute the physical Zee-model LFV branching fractions.

Reference: Herrero-Garcia, Ohlsson, Riad & Wiren,
JHEP 04 (2017) 130, [arXiv:1701.05345](https://arxiv.org/abs/1701.05345),
Eqs. (3.12) and (3.19). In Florentino's charged-scalar convention
([arXiv:2106.08332](https://arxiv.org/abs/2106.08332), Eq. (22)),
the charged singlet weights are sin(gamma)^2 in H1 and cos(gamma)^2
in H2.

The coefficient computed here is

`C_R^(f) = -(sum_k f[daughter,k]^* f[parent,k]) /
           (48*pi^2) *
           (sin(gamma)^2/mH1^2 + cos(gamma)^2/mH2^2)`

with `BR_fonly = BR(parent->daughter nu nubar) *
48*pi^3*alpha/GF^2 * abs(C_R^(f))^2`.

**IMPORTANT:** `BR_fonly` is an isolated squared contribution,
not a rigorous lower or upper bound on the *physical* rate, since
other amplitudes interfere. A value below the experimental limit
does **not** establish that the complete Zee model passes LFV.

Current selected comparison limits (90% CL):
- mu->e gamma < 1.5e-13, MEG II (2025):
  https://link.springer.com/article/10.1140/epjc/s10052-025-14906-3
- tau->3mu < 1.9e-8, Belle II (2024), **not computed in this gate**:
  https://docs.belle2.org/pub_data/publications/4379/
- tau->mu gamma < 4.2e-8, tau->e gamma < 3.3e-8,
  the standard published Belle bounds retained for reference.
  Revalidate for a final paper.

## Run on AF

This PR is stacked on A1B (it contains A1 and A1B code).

```bash
cd /home/aalida/zee
git fetch origin gateA1c-charged-singlet-lfv-dipole
git switch gateA1c-charged-singlet-lfv-dipole
python3 -m unittest discover -s tests -p 'test_gateA1c_charged_singlet_lfv.py' -v
python3 scripts/gateA1c_charged_singlet_lfv.py \
    --output work/gateA1c_charged_singlet_lfv.json
```

## Interpretation of first checks

At the illustrative A1B seed, approximate expected f-only results:
- mu->e gamma: 1.56e-18
- tau->mu gamma: 1.96e-20
- tau->e gamma: 3.86e-19

These indicate the *f-induced charged-scalar dipoles* alone are
unlikely to constrain this minimum-norm Yukawa seed. The actual
collider/neutrino phenomenology cannot be judged without the full
Y-dependent dipole amplitudes, neutral scalars at the same
mH=580.7, mA=633.7 GeV and the non-aligned h terms (if applicable),
two-loop Barr-Zee diagrams with the Type-II quark Yukawas, and
tree-level LFV and low-energy precision processes.

**STOP: no overall LFV viability has been established.**
