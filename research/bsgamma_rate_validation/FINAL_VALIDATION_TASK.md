# BSG-FINAL — Validation and uncertainty for Zee B → X_s gamma

**Branch**: `research/zee-bsgamma-rate-validation`
**Starting point**: commit `3207b6db72d2f5a116b0a88afcc3fd8154722d30`.
**Read this task before doing any work.** Follow root `AGENTS.md`.
**Scientific scope**: inclusive `BR(B→X_s γ)` for `E_γ>1.6 GeV` in the CP-conserving, Type-II Zee quark sector with two mixed charged Higgs bosons. This task is NOT a full B-physics/complete flavor likelihood.

## Why this task exists

Our finite, validated physics components are already present: BMU ordinary QCD matching for NP `C4^(1), C7^(0,1), C8^(0,1)`; mixing `cos²γ,sin²γ`; patched legacy SuperIso v5.0 with internal consistency tests; and native EOS 1.0.21 high-scale evolution to a nonlinear rate. The EOS prototype returns `BR=3.70865222239525e-4` at `mH1=550, mH2=900 GeV, tanβ=5.3, γ=1.09`, with the native EOS prescription. That is **DIAGNOSTIC_ONLY**, NOT a 2026-calibrated prediction.

`RESULT.md` and `BRIDGE.md` at `3207b6d` document the solution to the earlier translator/evolution bottleneck. Do NOT re-derive the two-loop matching, rewrite the ADM, reopen the CKM/JMS exploration or declare the existing successful code blocked merely because an independently matched *physical rate* is missing. Preserve all past code, evidence and statuses.

**Goal**: settle whether there is a defensible rate+uncertainty prescription suitable to filter the final D14 scan, including the lighter Zee masses that would be prematurely discarded by an invalid single-Higgs mass bound. We prefer a *documented, conservative NLO/controlled-NP accuracy domain* over demanding NNLO for every NP contribution. Never assert such a domain without numeric evidence.

## Input and source material (verify exact versions/revisions)

- `research/bsgamma_rate_validation/{RESULT.md,BRIDGE.md,BACKENDS.md,bridge.py,bridge_results.json}`
- `module5/{D9B_SUPERISO_REPAIR_AUDIT.md,BSGAMMA_2026_ACCURACY.md,BSGAMMA_2026_CONVENTION.md,BSGAMMA_SCAN_TRIAGE.md}`
- Frozen matching `scripts/zee_module5_bmu_nlo.py` and D14 audit; read-only.
- Borzumati & Greub, Phys. Rev. D58 074004 (1998), hep-ph/9802391, plus its published addendum; candidate *historical NLO one-state numerical reference*, not assumed matched.
- Hermann/Misiak/Steinhauser arXiv:1208.2788, modern Type-II higher-order reference.
- Misiak et al. arXiv:2608.29863 and companion 2608.29864, for the published 2026 SM/experiment framework and its stated *linearized* generic-NP range. Check final version, references and numerical inputs before use.
- Unmodified upstream EOS 1.0.21; evaluate EOS 1.1 only if it resolves an explicit issue. SuperIso 5.0 native Type-II and patched D9B paths may serve as **independent-code rate comparison** with EOS when genuinely matched, but the two SuperIso paths are not independent of one another.
- HEPfit/flavio/wilson only if their existing, documented interfaces offer a concrete missing ingredient; no wholesale framework replacement.

## Stage A — Source-qualified one-state physical-rate validation (top priority)

1. Find **at least one independently published numerical one-charged-Higgs rate reference** with enough stated information to reproduce: `mH±`, `tanβ`, Yukawa convention, `μ0, μb, μc`, masses, `αs`, CKM, `Eγ` cut, SM/hadronic normalization, power/QED terms, and perturbative counting. A single curve without a reproducible input card is **NOT** an absolute numerical oracle. Cite exact source page/equation/table and record accessible input files, source versions and hashes. Do not use digitized plots as high-precision validation.
2. Attempt to reproduce the reference in the existing native EOS path. The computation must be independent of a custom tuned normalization and must use the same perturbative prescription. If old published conventions cannot be made identical, produce an explicit `matched / intentionally different / missing` input table, *not* a forced PASS.
3. Cross-check at least one exact one-state point between independently implemented **physical rate kernels**, preferably EOS versus a standalone original SuperIso Type-II run or HEPfit where possible. Compare `BR_SM`, `ΔBR = BR(SM+NP)-BR(SM)`, low-scale `C1..C8`, and response to independently signed `C4,C7,C8` perturbations, with the SAME inputs/scale/cut/order when claiming matched agreement.
4. Separate `external published numerical reference reproduced` from `two implementations agree` from `upstream self-regression PASS`. None implies the others. Publish a per-benchmark agreement table, actual signed residuals, and an *a priori* tolerance justified by source precision and matching uncertainties.
5. Minimal numerical cases: zero-NP; one-state 550/900 GeV at tanβ=2,5.3,50; 100 TeV decoupling diagnostic (not a precision point); opposite-sign *nonphysical* control; two-state 550/900 at γ=0, 1.09, π/2; equal mass and interchange. Keep all two-state identities.

If no adequately specified published numerical benchmark exists, document the unsuccessful leads with exact missing pieces; do not pretend regression figures are physical validation. A feasible independent backend calculation of a complete original source card is preferable to endless bibliographic review.

## Stage B — Theory uncertainty and controlled validity region

1. Identify the perturbative order of every ingredient individually: LO and NLO NP matching, EOS RG/mixing, low-scale matrix elements, squared-amplitude and bremsstrahlung terms, SM baseline, CKM/masses/cut, and HQE/resolved-photon corrections. Differentiate `NLO-labelled EOS prescription` from **uniform NLO NP** and from NNLO SM. Where possible, extract an order-separated or consistent truncation using already available backend outputs. Do NOT simply drop an `a_s²` term in isolation and call the result NLO.
2. Evaluate scale variation with recomputation of matching at each `μ0`, RG, and rate at `μb`, plus available mass/QCD input uncertainty. Use a documented finite grid around the default scales (e.g. `μ0={120,160,200} GeV`, and defensible low-scale alternatives). Verify inputs remain in the backend validity domain. Scale variation is a sensitivity estimate, **not automatically a confidence interval or complete missing-order error**.
3. Determine the relative importance and possible conservative bound of: quadratic NP terms, four-quark `C4` and induced `C3,5,6`, primed/finite-ms, light u/c, and enhanced down-Yukawa effects. Do not infer a global bound from a single benchmark or a tiny measured `C4` shift.
4. Cross-check EOS new-physics shift `ΔBR` against the published 2026 linear NP formula *only where its approximations are valid*; use identical high-scale convention, inputs and `μ0`. Do **not** shift or rescale EOS's legacy absolute SM baseline to the 2026 SM number without a demonstrably consistent matching/normalization prescription.
5. If physically justified, define a documented, **explicit finite** mass/tanβ/mixing/NP-coefficient domain with a conservative uncertainty/envelope; validate with independent points not used to choose it. If any major effect is unbounded, return `ACCURACY_DOMAIN_UNKNOWN`, not a guessed 10% or an inflation of experimental sigma.

## Stage C — Statistical prescription for a scan

Only if Stages A/B establish a rate domain:

1. Pin the relevant current experimental world average and source, its measurement definition/cut, the published SM prediction/order and their uncertainties. Record exactly which uncertainties correlate and which do not; treat any NP uncertainty separately and avoid double-counting the SM uncertainty already included by a backend.
2. Design an explicit two-sided `BR(B→X_sγ)` compatibility test (with the chosen confidence criterion, e.g. single-observable Gaussian 95% if justified), including optional nuisance covariance; demonstrate known limit cases and consistency of `χ²` or likelihood normalization.
3. Implement **research-only** `scan_filter_candidate.py` returning structured `PASS / FAIL / UNKNOWN / NOT_EVALUATED`, observable, uncertainty model and hashes. `UNKNOWN` if outside the validated theory domain or missing a relevant contribution. Do not edit D14 accepted-point logic in this branch.
4. Demonstrate on a small **pre-registered** grid including both <1 TeV and >1 TeV charged masses. Report boundaries as conditional, not a universal `mH±>670 GeV` bound; do not optimize the envelope to rescue preferred spectra.

## Quality gates and reporting

- Organize new work only inside `research/bsgamma_rate_validation/`; create `FINAL_VALIDATION.md`, `final_validation.json`, small scripts/tests and exact reproduction commands. Preserve existing evidence unchanged.
- Freeze source, binaries and data hashes. External code and large outputs under ignored `local/`.
- A successful script run or equality of two adapter paths is NOT a physical-rate validation. At least one independent source-qualified physical benchmark and explicit uncertainty/domain argument are required for the final scan gate.
- Execute focused tests (source convention, truncation/scale, benchmark, numerical identities, statistical behavior) and `git diff --check`. Make small commits and push to this branch; leave Modules 0–14, `main`, prior branches and historical evidence unchanged.
- Do not implement new two-loop Feynman diagrams, general QCD ADMs, a new flavor package, a large scan, or silently adjust physical inputs to match a desired result.

## Required final classification

Use ONE of:
- `BSG_SCAN_FILTER_VALIDATED`: independent matched physical benchmark, source-qualified accuracy domain, documented uncertainty/statistical treatment, finite test grid, all PASS.
- `BSG_RESTRICTED_FILTER_VALIDATED`: the same evidence **only within a precisely stated restricted region**; other points remain UNKNOWN.
- `BSG_PHYSICAL_ACCURACY_BLOCKED`: no independently validated theory precision/uncertainty and therefore no exclusion use; present the smallest precise missing input and **two practical alternatives** (e.g. documented LO-NP modern fit restricted to its validity, or an external reference/author collaboration). Do not keep iterating indefinitely.

**First do A, then B, then C.** A is a hard gate: do not fabricate a theory sigma, write a filter, or launch a scan while A is unresolved. The goal is a defensible scientific result, not satisfying an arbitrary PASS flag.
