> **Current task (2026-11-06):** `research/bsgamma_rate_validation/M2026_ROUTE_TASK.md` takes priority.
> The previous independent-benchmark attempt finished `BSG_PHYSICAL_ACCURACY_BLOCKED`.
> Use the published 2026 LO-NP equation with an explicit validity-domain gate;
> without source-supported remainder bounds, retain DIAGNOSTIC_ONLY and draft
> an author question. Do not repeat physical-rate backend reconstruction.

# Codex instructions — Zee B→Xsγ independent rate validation

> **Current Codex task (2026-11-06):** Read and execute
> `research/bsgamma_rate_validation/FINAL_VALIDATION_TASK.md` first.
> Start from the already working EOS evolution at commit `3207b6d`;
> do not reopen solved RG/matching work. The new task prioritizes an
> independently matched physical-rate benchmark, a justified uncertainty
> domain and then (only if validated) a research-only scan filter.
> All existing conservative physics-status safeguards below remain in force.

This file is scoped to branch `research/zee-bsgamma-rate-validation`.
It replaces the D14-only instructions in this branch; the source branch
`feature/zee-d14-integrated-scan` and its files must remain untouched.

## Scientific objective

Establish whether an **existing independent, public flavor-physics backend**
can produce a reproducible, accurate nonlinear `BR(B→X_s gamma, E_gamma>1.6 GeV)`
for the real Type-II Zee quark sector with *two charged Higgs states*.
Reuse the already validated LO/NLO QCD **ordinary-basis** matching
`Delta C4, Delta C7, Delta C8`; do not start another matching, gauge,
two-loop or multi-month symbolic-calculation project.

The immediate deliverable is a **bounded independently executed rate comparison**,
not a global scan, mass exclusion, complete NNLO solver, or full LFV calculation.
Publishability and 2026 exclusion-readiness must remain UNKNOWN until validated.

## Existing authoritative evidence

Read before editing:
- `module5/D9B_SUPERISO_REPAIR_AUDIT.md`: patched SuperIso v5.0 internal
  Q1–Q8 NLO matching/observable consistency; this is a **legacy backend**,
  not an independently validated modern rate.
- `module5/BSGAMMA_2026_ACCURACY.md`, `module5/BSGAMMA_2026_CONVENTION.md`,
  `module5/BSGAMMA_SCAN_TRIAGE.md` for independent BMU/HyperIso matching,
  ordinary/effective-basis conventions and missing quadratic accuracy.
- `module14/D14A_INTEGRATED_SCAN_AUDIT.md`: current D14
  B-physics classification is **DIAGNOSTIC_ONLY**; no global acceptance.
- `scripts/zee_module5_bmu_nlo.py`, `scripts/zee_d9b_rate_validate.py`,
  and `module14/external.py` only as needed to understand existing interfaces.

Example *diagnostic* point: mH1=550 GeV, mH2=900 GeV,
tanbeta=5.3, gamma=1.09. In the frozen convention the full ordinary
matching is the coherent sum with weights cos²gamma and sin²gamma.
The archived patched SuperIso NLO legacy result is about
3.88229911548e-4, **not** an external physical-rate oracle.

## Allowed work and execution order

1. Inventory *actual executable support* in current flavio+wilson, EOS and
   HEPfit. Verify documented observables, Wilson basis/scale, operator
   coverage, whether arbitrary BSM coefficients can enter the physical rate,
   normalization, perturbative order, photon cut, supported SM inputs,
   uncertainty interfaces and installation requirements. Do not assume
   capabilities from a package name or version. Prefer small tests over
   lengthy speculative source audits.
2. Select one feasible independent backend, pin an upstream release/commit,
   dependencies and input card, and run an **actual zero-NP SM result**.
   Record exactly which published theoretical prediction it represents.
3. Run a minimal independently reproducible one-state set: decoupling,
   550/900 GeV, multiple tanbeta values and a physically opposite-coupling
   sign *as a diagnostic only*. Vary C7 and C8 separately with ± perturbations,
   and C4 if supported, to assess nonlinear/finite-basis effects. Keep
   SM/NP coefficient bookkeeping explicit and avoid double evolution,
   double `alpha_s/(4pi)` factors and ordinary/effective C7 confusion.
4. If supported, inject the **coherent two-state coefficient vector ONCE**,
   not a weighted sum of branching ratios. Verify gamma=0, pi/2, equal-mass
   and interchange identities. Compare to the legacy SuperIso output only
   under genuinely matched inputs/order. A difference between defaults is
   not a backend failure.
5. Assess what is still missing before a statistically defensible 2026
   exclusion: current SM prediction vs legacy baseline, cutoff dependence,
   NP quadratic terms, C4, perturbative truncation, finite-ms/primed/light
   quark effects, uncertainty and covariance. Mark unvalidated coverage
   `NOT_EVALUATED` or `DIAGNOSTIC_ONLY`; never invent a universal mass
   cut or calibrate by rescaling a legacy SM central value.
6. Once a rate interface is demonstrably valid, design a *separate*
   integration adapter for D14; do not alter D14 accepted-point logic in this
   exploratory branch. Include exact next steps if it is not ready.

## Code, environment and output discipline

- Put experiments in `research/bsgamma_rate_validation/` with a short README,
  version-locked setup instructions, source references, executable commands,
  machine-readable run results and a concise RESULT.md. Add focused tests.
- Do not edit existing Modules 0–14, historical audits, frozen patches, source
  evidence, `main`, or another Git branch. Existing backend code is read-only.
- Use local ignored `research/bsgamma_rate_validation/local/` for external
  repositories, environments, generated files, downloaded archives, binaries
  and voluminous outputs. Do not vendor third-party sources or binaries.
- Inspect license terms before reusing external code. Do not invent formulas,
  missing numerical reference points or precision claims.
- Work in bounded, testable increments; after each supported result run
  focused tests and `git diff --check`. Commit only useful, reproducible
  artifacts to this branch. If an external backend is inaccessible or lacks
  necessary API support, document the concrete blocker and test the next
  candidate, rather than rewriting its entire flavor framework.
- Do not run a large physics scan, HTCondor submission or expensive symbolic
  calculation for this investigation.
