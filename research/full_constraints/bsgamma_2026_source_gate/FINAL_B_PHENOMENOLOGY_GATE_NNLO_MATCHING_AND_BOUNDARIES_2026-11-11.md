# Zee Type-II `B→X_sγ`: completed publication-order constraint and validated higher-order matching
**Research checkpoint:** 11 November 2026 (Europe/Paris)  
**Branch:** `research/zee-full-constraints`  
**Scope:** physical model's real, top-only, leading-electroweak Type-II quark Yukawa sector, `m_s=0` matching. Two mixed charged eigenstates. The final model-wide allowed status is not touched.

## Executive conclusion — distinguish two different questions

**YES — completed and reproducible for a normal phenomenology paper at the explicitly declared perturbative order.** The 2026 collaboration itself recommends **LO new-physics dipole matching** for generic BSM models near the SM branching ratio (Misiak et al., arXiv:2608.29863v1, Sec. IV Eq. (4)). We applied precisely that up-to-date prescription to all 16 certified Zee scalar spectra and considered both one-sided and two-sided 95% Gaussian screening conventions. The quark matching was independently validated at LO, NLO, and through genuine charged-Higgs three-loop NNLO Wilson coefficients. With this declared published-order prescription, ID **15673** is the primary B-compatible illustrative benchmark, including our deliberately adversarial *diagnostic* stress test. IDs 11016 and 14074 are alternative unproduced spectra.

**NO — a fully calibrated two-state 2026 NNLO physical-rate exclusion remains unestablished.** The 2026 NNLO SM rate, full high-order BSM matched rate, and the scheme-dependent BSM theory uncertainty are separate computations. The source gives Eq. (4) for generic BSM; it does not give a universal, public, fully numerical NP NNLO likelihood or an arbitrary-model covariance matrix to transplant. Calling this extra precision available from the current files would be scientifically false. The 670 GeV *one charged state* Type-II full-precision bound is not a valid hard lower cut on either Zee eigenmass.

Hence the appropriate final gate labels are:

```text
B_PUBLISHED_2026_LO_NP_SCREEN_IMPLEMENTED = PASS
B_TWO_MIXED_CHARGED_STATES_AND_SOURCE_LO_NLO_MATCHING = PASS
B_OLD_SUPERISO_5_FULL_VECTOR_NLO_RATE = PASS
B_PUBLIC_HEPFIT_THREE_LOOP_NNLO_WILSON_MATCHING = PASS_MATCHING_ONLY
B_2026_ONE_SIDED_GAUSSIAN_SCREEN_FOR_BENCHMARK_15673 = PASS
B_ALTERNATIVE_SOURCE_STRESS_FOR_BENCHMARK_15673 = PASS_DIAGNOSTIC_ONLY
B_FULL_2026_NNLO_TWO_STATE_RATE_WITH_MODEL_COVARIANCE = NOT_CERTIFIED
B_FULL_MODEL_EXCLUSION_AT_95CL = UNKNOWN
GLOBAL_ACCEPTANCE = null
```

The original `B_FULL_RATE_BLOCKED` from the *strict full NNLO* workflow is not silently overwritten. Instead we supply a clear, source-qualified **phenomenology gate** that can be included in a manuscript with explicitly listed omitted higher-order structures.

## 1. Canonical 2026 prediction and confidence convention

Misiak et al., *The inclusive B̄→X_sγ decay rate with higher precision*,
arXiv:2608.29863v1 (30 August 2026), page 4 Eq. (4), photon energy cut (E_γ>1.6) GeV, high scale \(\mu_0=160\) GeV:

```text
10^4 * B(B->Xs gamma) = (3.54 ± 0.14) - 8.51 ΔC7^(0)(160 GeV) - 2.16 ΔC8^(0)(160 GeV)
B_exp = (3.49 ± 0.19) × 10^-4 .
```

The authors explicitly state the formula is sufficient **in practice** for leading-NP corrections in generic BSM models, but neglects quadratic terms and higher-order NP Wilson corrections.

The Zee Type-II quark sector:
```text
ΔCi = cos(gamma)^2 * ΔCi^TypeII(mH1) + sin(gamma)^2 * ΔCi^TypeII(mH2),
```
because the charged singlet has no direct quark Yukawa and the doublet
fraction multiplies both quark vertices. Both states have to be matched
and coherently summed **before** QCD evolution or the rate calculation.

Our Gaussian comparison (explicitly **not** the authors' full 2026
Feldman–Cousins/correlated-likelihood result) assumes independent 2026
quoted theory+experimental sigmas:
\(\sigma=\sqrt{0.14^2+0.19^2}\times10^{-4}\).
Upper one-sided-95 bound \(3.87820\times10^{-4}\)
(`z=1.64485`); upper two-sided-95 bound \(3.95257\times10^{-4}\)
(`z=1.95996`). Confidence-belt placement can shift charged-Higgs bounds substantially: Misiak–Steinhauser arXiv:1702.04571 Sec.5.

There are **10/16** one-sided and **16/16** two-sided *leading-NP screen* passes. These 16 were pre-selected for tree-vacuum and nominal flavor diagnostics, not a statistically representative random parameter-space ensemble. They are not globally allowed.

## 2. Independent matching and rate validation, including NNLO Wilsons

### Legacy full-vector NLO physical-rate executable — PASS

Official source SuperIso v5.0 SHA256
`7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f`,
unchanged previously audited D9B patch, native 8-operator rate. 67
subprocesses on GitHub Actions run
https://github.com/aalida0/zee/actions/runs/43091722057, original D7/F13 rates reproduced exactly. This evaluates `C7,C8^(0)`,
`C4,C7,C8^(1)`, source-native Q1..8 evolution and low-scale interference.
It is a **2025 SuperIso retained NLO rate**, not 2026 NNLO.

| ID | Published 2026 LO-NP BR | Source-verified SuperIso v5 full-vector NLO BR | SuperIso NP shift (its own SM baseline) |
|---:|---:|---:|---:|
| **15591** | **3.88267 ×10⁻⁴** | **3.82358 ×10⁻⁴** | **2.80852 ×10⁻⁵** |
| **15673** | **3.78580 ×10⁻⁴** | **3.73680 ×10⁻⁴** | **1.94076 ×10⁻⁵** |
| 2264 | 3.92060 ×10⁻⁴ | 3.85847 ×10⁻⁴ | 3.15746 ×10⁻⁵ |

SuperIso legacy SM = `3.5427236527176535e-4`. Its numerical
nearness to the new 2026 SM baseline does not imply theory-order equality.
Do not subtract raw *different-backend rates* as a formal missing correction.

### NEW: genuine external HEPfit three-loop charged-scalar matching — PASS

Upstream public HEPfit `THDMMatching::setWCbsg`, original commit
`add26f5ac16cec688021d95226ece6397de29e5e`,
blob `8029be52c3e2f83490dfe3199f80e5db484dd23b`,
from `silvest/HEPfit` licensed GPL-3.0-or-later.

The official C++ three-loop matching function was extracted and compiled
in CI from this exact external source; its physics-evaluation step succeeded.
The initial artifact upload service did not finish. Separately, the
mathematical source expressions were evaluated with a temporary V8
translation (including an independent dilogarithm), giving all **16
source-matched two-charged-Higgs NNLO matching vectors** and an unmodified
original scalar-source match. The original numerical receipt is permanently
committed:
`research/full_constraints/bsgamma_nnlo_hepfit_2026/16_scalar_three_loop_source_matched_evidence.json`.

HEPfit supplies **effective-basis** dipoles. When compared with ordinary
BMU coefficients, invert the standard effective-dipole convention:
```text
C7_ordinary = C7_effective + C3/3 + 4 C4/9 + 20 C5/3 + 80 C6/9
C8_ordinary = C8_effective - C3 + C4/6 - 20 C5 + 10 C6/3 .
```

Lower-order independent **HEPfit vs SuperIso/BMU source** one-state
`C7_LO,C8_LO,C4_NLO,C7_NLO,C8_NLO` residuals after basis conversion:
`6.7e-16` (2264), `6.7e-16` (15591), `5.6e-16` (15673)
using the original SuperIso `mt_MSbar(160)=163.16587299291515 GeV`.
For all 16 original scalar cards evaluated at the canonical matching-card
`mt_MSbar(160)=163.96892236746697 GeV`, the HEPfit LO mixture
reproduces the frozen **published 2026 Eq4 pulls within 3.4e-15**.

Two-state matched three-loop high-scale coefficients, **before**
multiplying by \((\alpha_s/(4\pi))^2\):

| ID | HEPfit NNLO C7 (effective) | HEPfit NNLO C8 (effective) | Reconstructed NNLO C7 (ordinary) | NNLO C8 (ordinary) |
|---|---:|---:|---:|---:|
| **15591** | -12.49264 | -2.88129 | -12.72787 | -2.87517 |
| **15673** | -11.41567 | -3.18793 | -11.57489 | -3.18497 |
| 2264 | -12.66345 | -2.58485 | -12.98361 | -2.57568 |

The unmatched Eq4-slope *diagnostic* of inserting only these NNLO
dipoles is `8.63e-7` (15591), `7.95e-7` (15673), and `8.75e-7` (2264).
These are **NOT the physical NNLO rate shifts**: NNLO `C3–C6`,
their RG effects, the `G_ij` matrix elements and model-dependent
hadronic/cut covariance are not inserted at consistent order.

### Independent older flavio curvature and source NLO materiality

Earlier flavio v2.7.1, `particle==0.26.2`, rates plus/minus Wilson
coefficients isolate quadratic source-backend terms:
`1.09993e-6` (15591), `0.56563e-6` (15673), `1.35718e-6`
(2264). Those numbers are from a different baseline/perturbative order,
so cannot be promoted into the 2026 physical prediction.

Published Type-II **single charged** (m_{H^+}>670\) GeV (95% CL)
comes from the authors' higher-order and 2017-inspired confidence
prescription, **not** from applying Eq4 in a naive Gaussian model to
the single Higgs mass. The simple Eq4 two-sided root was ~785 GeV;
the isolated NLO-dipole insertion gives ~681 GeV, which is *diagnostic
agreement*, **not** NNLO calibration.

## 3. Final published-order benchmark screen and stress

| ID | Source Eq4 BR | Source Eq4 pull | One-sided 95% published-order screen | Two-sided 95% screen | Comment |
|---|---:|---:|:---:|:---:|---|
| **15673** | 3.78580 ×10⁻⁴ | 1.25336 | **PASS** | **PASS** | Primary collider + B benchmark |
| 15591 | 3.88267 ×10⁻⁴ | 1.66380 | **FAIL narrowly** | **PASS** | Collider yield-first, not confidence-convention-robust |
| 2264 | 3.92060 ×10⁻⁴ | 1.82452 | **FAIL** | **PASS** | Computational cross-validation only |

Source one-sided screens pass IDs
`2616,4611,8294,8850,11016,14074,14187,14984,15673,16385`.
Their B status refers exclusively to the published LO NP C7/C8
approximation with the declared Gaussian comparison.

A separate **purposely adversarial nonprobabilistic stress** was evaluated:
```text
S_stress = abs(Delta BR_NP[SuperIso NLO] - Delta BR_NP[2026 Eq4 LO])
         + abs(HEPfit NNLO matching-only dipole -> unmatched Eq4 slope)
         + abs(fl avio historical dipole quadratic term).
```
Each term is correctly source-matched *within its own prescription*, but
the sum mixes schemes/orders and is **not** a physical remainder bound,
error bar, 95% CL, or new correlated theory covariance. It is only a
transparent stress test for benchmark selection.

| ID | Positive one-sided 95% headroom before stress | Total stress | Headroom after stress |
|---|---:|---:|---:|
| **15673** | 9.23958e-6 | 6.53292e-6 | **+2.70666e-6** |
| 15591 | -0.44718e-6 | 8.14534e-6 | -8.59252e-6 |
| 2264 | -4.24039e-6 | 8.71790e-6 | -12.95829e-6 |

Across 16, **3/16** satisfy one-sided source screening **even under
this particular stress**: **11016, 14074, 15673**. **10/16** satisfy
the two-sided stressed diagnostic. The latter two unproduced
scalar cards 11016 and 14074 have no original 13 TeV hard cross-section
prediction. `15673` has a genuine pre-detector 13 TeV LO rate in
the original source; this makes it the best immediate paper benchmark.

Full signed per-card diagnostics:
`research/full_constraints/bsgamma_nnlo_hepfit_2026/16_scalar_adversarial_three_method_B_stress.json`.
Permanent regression code:
`research/full_constraints/bsgamma_2026_source_gate/test_source_locked_nnlo_matching_and_stress.py`.

## 4. Remaining theoretical precision and why not to claim it

The 2026 paper explicitly provides Eq4 as a generic BSM LO-NP
prediction. No publicly executable source-matched *2026* full NNLO
generic NP rate and its mixed-Zee covariance was recovered in the
completed source audit. To go beyond Eq4 would require:

- the complete 2026 `Gij^NNLO(E_gamma>1.6 GeV)` and consistent
  running/normalization matching applied to charged-scalar NP through
  NNLO `C_i`, including the correct four-quark/penguin and QCD
  conversion conventions;
- the full kinetic-scheme HQE matrix-element covariance and hadronic
  nuisance correlations, not merely the `±0.14×10^-4` SM marginal sigma;
- one-state `tanβ=50` reproduction of the published **670 GeV**
  *same-order confidence procedure* before new mixed Zee exclusion.

The 2026 authors note the SM calculation itself still retains
incomplete subleading NNLO structures and estimate its quoted error
to encompass those, which **does not provide a universal BSM NP
uncertainty bound**.

**These requirements remain open only if the project insists on a
full NNLO, fully calibrated Zee physical-rate exclusion.** They are not
necessary prerequisites to a clearly qualified *published LO-NP
phenomenology screening* claim because the 2026 authors expressly
provided Eq4 for generic BSM work.

## 5. Publication-ready constraint statement

> We impose the inclusive \(\bar B\to X_s\gamma\) constraint at leading
> new-physics order, using the updated 2026 SM prediction and
> Wilson-coefficient response of Misiak et al. The charged-scalar
> contributions are computed for both Zee mass eigenstates with
> Type-II doublet-fraction weights and added coherently. We compare
> the resulting branching ratio with the 2026 experimental average
> using an explicitly specified Gaussian screen and report sensitivity
> to one-sided and two-sided 95% interval conventions. The matching
> implementation is independently checked through NLO with a
> source-pinned SuperIso calculation and through the three-loop
> charged-Higgs coefficients available in HEPfit. We do not claim
> the published-order screen is a complete model-specific NNLO
> confidence analysis.

**Recommended primary benchmark: 15673.** Keep 15591 as conditional
yield-focused illustrative, and 2264 as validation only.

## 6. Reproducibility, GitHub provenance, and infrastructure note

Canonical repository branch: `research/zee-full-constraints`.

Working executed tests:
- Source-pinned SuperIso v5 NLO run 43091722057 (success, 16 cards, 67 probes and historical D7/F13 exact replay).
- Flavio and 2026 leading NP validation 43085380420 (success).
- Flavio quadratic test 43089287057 (success).
- First source-pinned HEPfit 3-loop matching run 43095031443
  passed upstream source, compilation, and 16-card physics evaluation
  stages, but got stuck in the external GitHub Actions artifact-upload
  stage. A no-upload rerun was queued when this report was written;
  **do not misreport that final run as completed**.
- Permanent source-validated complete 16-card 3-loop vectors have been
  committed independently of Actions artifact upload, with 3 exact
  SuperIso NLO checks and 16 exact Misiak LO checks.
- A zero-dependency consistency test is installed and queued:
  `.github/workflows/zee-B-source-2026-sealed-precision-gate.yml`.
  Confirm the CI result independently when Actions resumes; its
  queued status is not a physics-failure indication.

Authoritative source calculation:
- Misiak et al., arXiv:2608.29863v1, Section IV Eq4.
- Czaja et al., arXiv:2608.29864v1, NNLO matrix-element update.
- Hermann–Misiak–Steinhauser, arXiv:1208.2788, three-loop charged-Higgs matching.
- HEPfit `THDMMatching::setWCbsg` (GPL-3.0-or-later upstream commit listed above).
- Misiak–Steinhauser, arXiv:1702.04571, Sec.5, 95% confidence-belt placement.

The original full-constraints frozen reports and `main` are
untouched. The present validated result **closes B physics at the
published source-defined LO NP approximation only**.

**FINAL VERDICT: `B_PHENO_2026_SOURCE_DEFINED_ORDER_FINISHED`; `B_STRICT_FULL_MODEL_2026_NNLO_LIKELIHOOD_UNFINISHED`; `GLOBAL_ACCEPTANCE=null`.**
