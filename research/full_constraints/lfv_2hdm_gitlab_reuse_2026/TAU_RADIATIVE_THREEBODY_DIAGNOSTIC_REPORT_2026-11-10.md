# Tau radiative and dipole-only three-body LFV diagnostic — 10 November 2026

**Scope: new leading-log three-body subset, not a complete three-body or full Zee LFV prediction. PHYSICAL_LFV=UNKNOWN.**

## Input and provenance

Read without modifying the existing frozen
`research/full_constraints/lfv_lo_closure_2026/NATIVE_ZEE_TAU_RADIATIVE_LFV_GATE_2026-11-10.json`.
The source gate documents 4/4 original SARAH 4.15.4 one-loop tau radiative calculations and coherent addition of only the corrected, source-matched pure-neutral-fermion Barr–Zee subset to the Zee result. The corrected authors' thdm.py SHA256 is checked against
`9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193`.
Mixed Zee singlet/gauge two-loop terms remain uncomputed. The new module does not rerun the private Fortran or GitLab source.

For identical same-flavour final-state leptons and *dipole dominance*, the leading QED logarithm is

```
BR(tau -> 3 ell)_dipole / BR(tau -> ell gamma)
  = alpha(0)/(3*pi) * [ log(m_tau**2/m_ell**2) - 11/4 ] + subleading terms.
```

With alpha(0)=1/137.035999084, m_tau=1.77686 GeV, m_mu=0.1056583755 GeV and m_e=0.00051099895 GeV:

- 3e / e-gamma: **0.0104975811678**
- 3mu / mu-gamma: **0.00224135357825**

Finite-mass effects, non-dipole photon form factors, Z penguins, tree neutral Higgs exchange, boxes, interference and QED radiative corrections are not included. **These dipole-only contributions cannot be compared as total decay rates or used to certify a pass.** In particular, the nonzero tau-flavour neutral Yukawas mean tree-level four-lepton terms cannot be assumed negligible without calculation.

## Calculated dipole-only subset branching fractions

The column labelled *partial* means coherent Zee one-loop plus **only** the author-corrected neutral-fermion Barr–Zee amplitude, followed by the leading-log virtual-photon conversion. It does **not** mean all Zee two-loop amplitudes have been included.

| Card | BR(tau->3e), native one-loop dipole | BR(tau->3e), partial dipole | BR(tau->3mu), native one-loop dipole | BR(tau->3mu), partial dipole |
|---|---:|---:|---:|---:|
| D7 NO | 8.35601e-20 | 4.77493e-16 | 7.29825e-18 | 4.10168e-14 |
| D7 IO | 4.98531e-19 | 2.84715e-15 | 8.36612e-18 | 4.70639e-14 |
| F13 NO | 3.65714e-23 | 6.12912e-20 | 1.39311e-22 | 5.46554e-18 |
| F13 IO | 6.20648e-23 | 3.73525e-19 | 1.64663e-22 | 6.27108e-18 |

## Experimental sensitivity of the radiative partial amplitudes, **not a missing-diagram bound**

Using the frozen Belle 2021 90% CL comparisons BR(tau->e gamma)<5.6e-8, BR(tau->mu gamma)<4.2e-8, define
`kappa_max = sqrt(BR_limit/BR_partial)-1`. For any independently demonstrated bound
`||A_missing|| <= kappa ||A_partial||` in a consistent radiative amplitude scheme, triangle inequality is a sufficient (not necessary) condition for allowed rate when `kappa < kappa_max`.

| Card | Max assumed missing / partial amplitude for tau->mu gamma |
|---|---:|
| D7 NO | 46.9070 |
| D7 IO | **43.7235** |
| F13 NO | 4149.1450 |
| F13 IO | 3873.4365 |

For the *assumption* kappa=40, all eight radiative channels satisfy the sufficient inequality; for kappa=50 both D7 tau->mu gamma channels fail the sufficient inequality (they are **not** thereby experimentally excluded). Neither kappa=40 nor any other bound on missing Zee diagrams has been derived.

## Reproduction and protection

From repository root:

```sh
python3 -m unittest research.full_constraints.lfv_2hdm_gitlab_reuse_2026.test_tau_radiative_threebody_diagnostic -v
python3 research/full_constraints/lfv_2hdm_gitlab_reuse_2026/tau_radiative_threebody_diagnostic.py --kappa 40
```

Eight focused tests validate independent analytic ratios, four-card numbers, conditional threshold, the strict source identity and fail-closed physical acceptance. Local validation used a reconstructed copy of the four saved gate rows; GitHub CI is configured to use the authoritative committed gate file. It does not independently validate full SARAH Fortran amplitudes.

**Next required physics**, not supplied by this diagnostic: full tau->3l tree/contact/box/photon amplitudes and destructive interference; gauge-complete mixed F/W/H1/H2 Zee two-loop dipoles; finite-q² mu3e and coherent conversion uncertainty. Keep `physical_lfv=UNKNOWN` and `global_acceptance=null`.
