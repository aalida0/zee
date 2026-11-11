# B → X_s γ: source-pinned two-state NLO audit and declared-order screening
**11 November 2026 | Zee Type-II, real top-only leading-EW quark sector | Branch `research/zee-full-constraints`**

## Precise status

**B_MATCHING_LO_NLO_PASS; B_FULL_VECTOR_NLO_SOURCE_REPLAY_PASS (16/16); B_2026_PUBLISHED_LO_NP_SCREEN_PASS (16/16); B_FULL_PHYSICAL_RATE_AND_COVARIANCE_UNKNOWN; GLOBAL_ACCEPTANCE=null.**

This is the strongest evidence currently justified, not a completion of all theoretical uncertainties. The 2026 *published leading-NP screening observable* can be applied to benchmark selection, provided the paper states the approximation, error assumptions, and lack of a fully calibrated physical B-likelihood. **No full-model exclusion/pass is inferred.**

## Published source prescription

Misiak et al, arXiv:2608.29863v1, page 4 Eq.(4), with (E_γ>1.6) GeV and matching at (mu_0=160) GeV:
```
10^4 BR(B -> X_s gamma) = (3.54 +/- 0.14) - 8.51 DeltaC7 - 2.16 DeltaC8
BR_exp = (3.49 +/- 0.19) x 10^-4
```
The formula uses **leading-order BSM dipole coefficients** and drops quadratic NP terms; the cited paper recommends this for a practical LO-NP treatment. We independently checked its operator basis against BMU (hep-ph/9904413). The real quark Type-II Zee charged states match with squared doublet fractions:
`DeltaC_i = cos(gamma)^2 C_i^II(mH1) + sin(gamma)^2 C_i^II(mH2)`.
The singlet has no independent direct quark Yukawa. The complete quark-sector NP coefficients are summed *before* computing the inclusive rate.

Our **reference Gaussian-screen** assumes independent normal published SM and experimental errors **only**, and is not the paper's full 2HDM-II confidence prescription or a Zee NP theory covariance:
```
sigma_ref = hypot(0.14,0.19) x 10^-4
upper_2-sided_95 = (3.49 + 1.95996398454*hypot(.14,.19)) x 10^-4
                 = 3.9525681 x 10^-4
```
The 2026 single-charged Type-II full NNLO *model* mass bound **670 GeV** cannot be imposed on either Zee mass in isolation.

## NEW: independent source-verified eight-operator NLO rate, actual execution

Recovered the **official SuperIso 5.0** source from
`https://superiso.in2p3.fr/download/superiso_v5.0.tgz`,
exact source archive SHA256
`7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f`.

Applied original, previously audited `module5/patches/d9b_superiso_v5.0.patch` **unchanged**, compiled native SuperIso static library **serially**, compiled original `scripts/zee_d9b_rate_probe.c`, and executed **67 independent processes** on GitHub Actions. All 16 original D14 scalar cards retain their source identity and tree-vacuum witness. Original D7/F13 full NLO rates reproduce **exactly**:
- D7 = `4.2262508129385407e-4`, residual 0.
- F13 = `3.8866519790644710e-4`, residual 0.

The matched contributions include `DeltaC7,8^(0)` and ordinary `DeltaC4,7,8^(1)` in NDR/MS-bar top at 160 GeV. SuperIso's evolution, interference and NLO numerator are executed with original code's HQE/EW/semileptonic normalization. **This does not implement the August 2026 SM/NNLO upgrade**, and some historical backend terms use a mixed retained order. Source-native C1-8, no full real/complex general-model WET basis and no general primed NP terms.

- [Successful compiled-source 16-point CI](https://github.com/aalida0/zee/actions/runs/43091722057)
- Raw result archive `zee-original-superiso-v5-16-scalar-8operator-NLO-source-evidence` (build logs, all 67 stdout receipts, JSON).
- Uncompressed `NLO_RATE_EVIDENCE.json` SHA256:
  `9f8b9051ecdf4572f28fc10bb2d107bd2c04fbec3f39a22063aa3534eb486a61`.

### All 16 original scalar spectra

The **published 2026 LO-NP** and **SuperIso 5.0 full-vector NLO** columns use *different SM baselines/prescriptions*. Do **not** subtract the entire rates to claim a missing-theory error. Their **NP shifts**, defined relative to each backend's own SM, are comparable as an order/method materiality test.

| Scalar ID | Published 2026 LO-NP BR (×10^-4) | SuperIso 5.0 NLO BR (×10^-4) | SuperIso relative NP shift vs Eq.(4) LO NP | Explicit C4^(1) NLO rate effect |
|---:|---:|---:|---:|---:|
| 2264 | 3.92060 | 3.85847 | −17.04% | 7.11×10^-8 |
| 2616 | 3.81693 | 3.76389 | −20.13% | 4.07×10^-8 |
| 3693 | 3.88687 | 3.82645 | −18.20% | 6.05×10^-8 |
| 4611 | 3.84144 | 3.78511 | −19.59% | 2.97×10^-8 |
| 8294 | 3.85724 | 3.79988 | −18.94% | 6.13×10^-8 |
| 8850 | 3.87176 | 3.81384 | −18.28% | 5.09×10^-8 |
| 9454 | 3.91770 | 3.85348 | −17.72% | 3.30×10^-8 |
| 11016 | 3.75046 | 3.70577 | −22.53% | 2.32×10^-8 |
| 13345 | 3.88288 | 3.82242 | −18.43% | 4.81×10^-8 |
| 14074 | 3.73875 | 3.69614 | −22.81% | 3.19×10^-8 |
| 14187 | 3.84944 | 3.79270 | −19.22% | 4.16×10^-8 |
| 14555 | 3.88782 | 3.82545 | −18.71% | 2.50×10^-9 |
| 14984 | 3.83022 | 3.77581 | −19.69% | 4.40×10^-8 |
| **15591** | **3.88267** | **3.82358** | **−18.04%** | **5.02×10^-8** |
| **15673** | **3.78580** | **3.73680** | **−21.04%** | **2.98×10^-8** |
| 16385 | 3.84864 | 3.79169 | −19.34% | 3.63×10^-8 |

At (mu_0=160) GeV, SuperIso 5.0's executed SM reference is `3.5427236527176535e-4`. Numerical closeness to the 2026 SM `3.54e-4` is **not** a demonstrated equality of theory orders, hadronic inputs or uncertainty covariances.

### Three benchmark-specific NP shifts and known diagnostics

| ID | 2026 Eq4 nominal pull | Eq4 +positive-BR headroom to reference 2-sided 95 edge | Positive headroom / 2026 LO NP | SuperIso 5.0 NP rate shift | Old-flavio quadratic term (not transferred) |
|---:|---:|---:|---:|---:|---:|
| 15591 | 1.66380 | 6.98969×10^-6 | 20.40% | 2.8085183×10^-5 | 1.09993×10^-6 |
| 15673 | **1.25336** | **1.66765×10^-5** | **67.84%** | **1.9407607×10^-5** | 5.65630×10^-7 |
| 2264 | 1.82452 | 3.19648×10^-6 | 8.40% | 3.1574615×10^-5 | 1.35718×10^-6 |

These headrooms are **tolerances** for hypothetical additional signed rate effects, not proof the unknown physical remainder is smaller. The 2026 `0.14e-4` SM uncertainty is **not** a certified new-physics covariance.

### Actually executed NLO matching-scale response (same-backend NP shift)

Scale (mu_0) changes the top running mass and both charged-scalar NLO coefficients simultaneously; only this *one* scale is varied, not the full renormalization/nuisance ensemble.

| ID | NP shift at 120 GeV | at 160 GeV | at 200 GeV | Relative variation from 160 |
|---:|---:|---:|---:|---:|
| 15591 | 2.75202×10^-5 | 2.80852×10^-5 | 2.84244×10^-5 | −2.01%, +1.21% |
| 15673 | 1.89584×10^-5 | 1.94076×10^-5 | 1.96794×10^-5 | −2.31%, +1.40% |
| 2264 | 3.09656×10^-5 | 3.15746×10^-5 | 3.19384×10^-5 | −1.93%, +1.15% |

This is **not** a theory σ or a full μ0/μb/μc variation. HEPfit's older separate seven-input correlation study, resolved-photon effects, and the 2026 kinetic-fit covariance cannot be mixed without source-level scheme matching; see `research/full_constraints/bsgamma_hepfit/UNCERTAINTY_REPORT.md` and `BSGAMMA_COVERAGE.md`.

## Independent flavio cross-check and 2026 one-state falsifier

- [Published Eq4 ↔ independent flavio C7/C8 16-scalar run](https://github.com/aalida0/zee/actions/runs/43085380420): 16/16 inside Eq4 *diagnostic* 95% interval, 14/16 inside all three declared screen prescriptions. Only 2264 and 9454 method-sensitive.
- [Old-flavio quadratic/NP headroom](https://github.com/aalida0/zee/actions/runs/43089287057): symmetric (pmDelta C_{7,8}) *source backend* curvature, exactly quadratic under doubling, no 2026-rate transplant or systematic covariance.
- [NLO dipole matching materiality](https://github.com/aalida0/zee/actions/runs/43090182524): naive one-state Type-II tanβ=50 full NNLO source mass limit 670 GeV maps to **785.0569 GeV** under our LO-NP Eq4 Gaussian surrogate, and **680.6179 GeV** after inserting **only** NLO dipole matching into Eq4. This improved agreement is NOT a matched NLO/NNLO rate and cannot be used to calibrate a NP theory σ.
- `flavio==2.7.1` requires `particle==0.26.2` to retain the PDG2022 dataset. Both are pinned.

## Publication-ready scope, unresolved full rate

**Defensible paper wording:** “We impose the inclusive radiative B-decay constraint using the leading-new-physics Wilson-coefficient approximation of Misiak et al. (2026), with the two charged scalars matched coherently. The underlying matching is checked through NLO QCD against an independently compiled source-verified SuperIso calculation; our parameter-space classifications use the published leading-NP approximation, with explicit perturbative-scheme sensitivity checks. They are not a full NNLO or model-specific statistically calibrated B-decay exclusion.”

**NOT defensible:** “all 16 Zee spectra pass the full physical `B→Xsγ` constraint at 95% CL”; “the 2026 Type-II 670-GeV cut applies to each charged Zee eigenmass”; “scale variation/old flavio quadratic is the full theory error”; “SuperIso 5.0 NLO BR equals 2026 NNLO physical prediction.”

**The precise outstanding full-physics gate** requires either:
1. a public/reproduced full 2026 hadronic NNLO implementation with the two-state NP Wilson matching at matched order and an independently calibrated **BSM-dependent** perturbative+hadronic covariance, plus a one-state full-2026 670 GeV confidence control; **or**
2. an explicitly **lower-order approximation** rather than a “full physical constraint”, with a declared uncertainty strategy justified by a published reference and clear sensitivity robustness, while refraining from strong exclusion statements.

Potentially missing u/c and finite-(m_s) loop structures, primed chirality, scalar four-quark and higher-EW Zee effects must be power counted or bounded in the chosen approximation. NLO `C4` is no longer missing in the validated SuperIso rate, but its materiality does **not** certify these other terms.

**Recommended final project gate for the current benchmark paper:**
```
B_2026_EQ4_LO_NP_SCREEN = PASS_ON_16_ORIGINAL_SOURCE_SCALARS
B_INDEPENDENT_FULL_VECTOR_NLO_BACKEND = PASS_SOURCE_AND_D7_F13_REPLAY
B_UNCERTAINTY_MODEL = UNKNOWN
B_PHYSICAL_FULL_RATE = UNKNOWN
GLOBAL_MODEL_ALLOWED = null
```
**15673** is the most robust *nominal* B screening benchmark. **15591** is plausible with smaller margin. **2264** is method-sensitive and should remain a control.

## Reproduction

From a source checkout on `research/zee-full-constraints`:
```sh
# Full source-pinned SuperIso 5.0 16-scalar NLO execution:
# .github/workflows/zee-B-superiso-full-vector-16.yml
# It downloads the SHA-pinned official source, applies the unchanged D9B patch,
# compiles serially, executes 67 subprocesses and saves all raw logs.

# Independent 2026 Misiak/flavio source compare:
python -m unittest research.full_constraints.bsgamma_flavio_2026.test_published_eq4_triangulation -v
python -m research.full_constraints.bsgamma_flavio_2026.published_eq4_triangulation --output /tmp/zee-B-Eq4.json

# NP quadratic and hypothetical signed-remainder budget:
python -m unittest research.full_constraints.bsgamma_flavio_2026.test_np_remainder_budget -v
python -m research.full_constraints.bsgamma_flavio_2026.np_remainder_budget --output /tmp/zee-B-headroom.json

# Materiality of native NLO dipole-only matching:
python -m unittest research.full_constraints.bsgamma_flavio_2026.test_nlo_dipole_materiality -v
python -m research.full_constraints.bsgamma_flavio_2026.nlo_dipole_materiality --output /tmp/zee-B-NLO-dipoles.json
```
Source status and validations are reproducible through **GitHub Actions**, and model core modules, frozen original D10/14 records and `main` were not edited. A raw artifact zip is also preserved in the current conversation. Artifacts expire on GitHub after 30 days and should be durably backed up.

**VERDICT: ITEM 2 COMPLETED FOR A SOURCE-DEFINED PUBLISHED LO-NP PHENOMENOLOGY SCREEN; FULL PHYSICAL NNLO B-LIKELIHOOD NOT CERTIFIED.**
