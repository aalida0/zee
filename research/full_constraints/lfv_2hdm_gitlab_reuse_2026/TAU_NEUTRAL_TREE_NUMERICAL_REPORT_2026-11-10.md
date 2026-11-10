# Zee tau three-lepton neutral tree vs dipole subset — source-linked CI result

**2026-11-10 | Status: numerically executed restricted subsets. Physical LFV=UNKNOWN; global_acceptance=null.**

## Reproduction evidence

Exact neutral h,H,A amplitude using the frozen `module3.core.vertices` and
`module3.tree.width` integration (including exchange of two identical leptons,
finite lepton masses, and exact propagators) on the four SHA-locked D12 cards.

GitHub Actions execution: https://github.com/aalida0/zee/actions/runs/42818232458
(commit `c8da378d57c44b4214d9e87f0cf855976c3bf914`; four focused
source-linked tests PASS at quadrature order 10, and a separate numerical
execution at order 14 completed). Original script invocation initially failed
because the repository root was not on sys.path; fixed by invoking
`python -m research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_neutral_tree`.
No physics expression changed for that fix.

Inputs and scope: original `validation/module12/d12_benchmarks.json` and corrected neutral-fermion Barr–Zee + native Zee one-loop radiative
numbers from `NATIVE_ZEE_TAU_RADIATIVE_LFV_GATE_2026-11-10.json`.
The 3-body dipole factors are the leading logs with alpha(0)
(3e/eγ = 0.0104975811678193, 3μ/μγ = 0.002241353578249).

## Numerical subset results

| Card | tau->3e neutral tree BR | tau->3e dipole-only partial BR | tau->3mu neutral tree BR | tau->3mu dipole-only partial BR | tree/partial dipole 3mu |
| --- | ---: | ---: | ---: | ---: | ---: |
| D7 NO | 2.81659229e-23 | 4.77492977e-16 | 8.06619387e-16 | 4.10167705e-14 | 0.0196656 |
| D7 IO | 3.03902789e-22 | 2.84715396e-15 | 1.20163273e-15 | 4.70639424e-14 | 0.0255319 |
| F13 NO | 4.88302208e-28 | 6.12911774e-20 | 2.89815317e-21 | 5.46554070e-18 | 0.000530259 |
| F13 IO | 3.58223076e-27 | 3.73524933e-19 | 6.85945351e-21 | 6.27108318e-18 | 0.00109382 |

**Do not sum these BR columns.** The tree and photon dipole
amplitudes can interfere. Even a complete tree+dipole coherent calculation
would omit off-shell K1, Z penguins, boxes and the mixed charged-gauge
Zee-specific two-loop terms. The author's corrected general-2HDM
code is **not** a complete model of the Zee charged-singlet sector.
A comparison to current experimental limits cannot certify full-model
LFV acceptance or any benchmark exclusion.

Tau->3mu tree exchange is a few percent of the calculated dipole subset
*in rate* for the D7 snapshots, but that does not bound total interference:
the amplitude-level ratio is the square root of that number. Robust
quantitative total rate/error budgeting requires a fully source-matched
common operator basis.

## To reproduce

```sh
python3 -m unittest research.full_constraints.lfv_2hdm_gitlab_reuse_2026.test_tau_neutral_tree -v
python3 -m research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_neutral_tree --order 14
```

GitHub Actions publishes `zee-tau-neutral-tree-subset` JSON with both
source SHA records and all four tree/dipole subset rates.

**Still missing:** tau three-body contact/box/photon interference with
matching scheme, finite-q² correction, complete gauge-consistent Zee
mixed F/W/H1/H2 two-loop amplitudes, and modern conversion scheme/uncertainty.
No scan-wide FULL_LFV_PASS or physically allowed points.
