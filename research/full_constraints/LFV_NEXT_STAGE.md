# Next executable task — LFV source-level completion and a validated new observable

**Working branch:** `research/zee-full-constraints` (baseline B feasibility commit `64bdf27bb5337d9a6f60c5890ddda0fa4153b70b`).
**B gate already completed:** `research/full_constraints/FEASIBILITY_GATE.md` says `B_FULL_RATE_BLOCKED`, due to missing independent physical finite-cut rate validation and Zee NP theory uncertainty. Do not rerun D9B matching/response or pretend the B gate passed. Its source-verified blocker remains listed in the global readiness.

## Aim

Proceed independently on **publication-grade Zee LFV**. Deliver *actual* model-specific coherent operator calculations and validation **where public code supports them**. First remove confusion about whether the existing Module4 radiative-LFV amplitudes are complete: they are NOT. The source-level gaps are concrete:
- `module4/amplitudes.py:MISSING`: `W_gamma` gauge-matched group; `fermion_Z_gamma`; `W_Z_gamma`; `charged_current_WZ`; `additional_bosonic_two_loop`; `QED_running_and_radiation`; external-invariant/neutrino-mass limitations.
- `module4/charged_scalar.py` has validated H1/H2 charged-scalar/photon loops, but this is not the missing full bosonic gauge result.
- `module14/lfv.py` computes radiative LFV **PARTIAL** and optional tree `mu→3e`; the latter does not include 1-loop penguins or boxes and cannot be declared a complete physical constraint.
- `module14/physics_adapters/lfv_reference_evidence.json` already establishes high-precision agreement with corrected general-2HDM **neutral fermion/photon** terms; those contributions ALREADY exist in Module4. Do not double count.
- SARAH 4.15.4/SPheno 4.0.5 generated full-loop builds, but current full-loop pole masses/widths are unphysical. Isolate **operator coefficients at existing fixed physical input** only if source-conventions and precision are validated, not by pretending SPheno output is already fully reliable.

Read `research/full_constraints/PLAN.md`, `LFV_TASK.md`, `FEASIBILITY_GATE.md`,
`module14/PHYSICS_ADAPTER_READINESS.md`,
`module14/FINAL_PHYSICS_FREEZE.md`,
`module4/{amplitudes,charged_scalar,interface}.py`,
`module14/lfv.py`,
`module14/physics_adapters/{lfv_reference_evidence,spheno_build_evidence}.json`.

## Phase 1 — Identify and qualify reusable actual code

1. Inspect pinned corrected `general-2hdm-pheno` at
   `b5035cd58d2a7e4a91e9790d045df062b97adffe` and
   published erratum doi:10.1007/JHEP07(2026)184. Identify its **complete gauge-invariant groups**, coefficient normalization and exactly which group(s) carry charged Higgs loop dependence. No wholesale 2HDM-total→Zee replacement; no individual W/Z/ghost terms cherry picked from a dependent set.
2. Inspect existing SARAH-generated Zee FlavorKit operators and
   `Lto3Lp` / `MuEconversion` source and original saved research
   `research/zee-spheno-flavorkit-pilot` evidence. Source-lock versions,
   parameter input cards, mass-scheme conversions, Fzee and both H1/H2
   eigenstates, gauge/Goldstones and number of operators.
3. Search only **existing repo branches/commits and publicly source-qualified papers/code** for previously derived gauge-matched Wγ/charged-current amplitudes before starting new symbolic loop work. Record hashes and diagrams. Do not claim a result because a public package emits a nonzero number.

## Phase 2 — One genuinely new fully validated *coherent* LFV contribution or observable

Choose the **most promising feasible missing element**, prioritizing:
- complete fixed-scheme `mu→3e` and selected tau three-body amplitudes from tree + dipole + photon/Z penguin + box, including exact complex interference; OR
- a genuinely completed **gauge-invariant** missing radiative two-loop group in `W_gamma`/charged-current (must validate full Ward/IR cancellations and the relative chiral convention).

Choose based on actual source availability, independent derivation/validation, and finite execution cost; do not promise both.

Concrete gates:
1. Input uses original D12 cards with immutable scalar+neutrino hashes; no new parameter points.
2. Operator matching at complex coefficient level, including physical masses, chirality, conjugation and gauge/Goldstone conventions.
3. Verify relevant symmetries/limits: F antisymmetry, F→0, one-state/singlet-decoupling, gamma endpoints, real/complex phases, photon Ward/IR where applicable, full interference and correct BR/total-width normalization.
4. Require a nonzero independently calculated reference/analytic formula and numerical tolerances; a symbolic reference multiplied by its own normalization is not independent.
5. Only when **the entire stated physical observable** is present at the claimed accuracy and experimental CL/input is source backed, an *opt-in* `PASS/FAIL` may be used. A validated new **subset** stays `PARTIAL`; the total LFV gate remains UNKNOWN while materially interfering terms are absent.
6. No runtime SPheno full-loop mass/width output may be substituted. Do not edit frozen Modules0–13 or overwrite original data; store research adapter under `research/full_constraints/lfv/` or `module14/physics_adapters/` only with provenance. If no independent source support for a new full observable exists, document exactly why and mark `LFV_FULL_COVERAGE_BLOCKED` instead of creating another incomplete calculator.

## Phase 3 — Ready-to-merge source-locked research output

Deliver `research/full_constraints/LFV_COVERAGE.md` (topology × operator × source × validation × omission),
`research/full_constraints/LFV_EXECUTION_REPORT.md`,
`research/full_constraints/LFV_VALIDATION.json`, focused tests (using original cards);
and a scoped adapter only if it passes all gates.

For `mu→3e`, `tau→3\ell`, `mu→e` conversion distinguish radiative dipole, off-shell photon/Z, tree neutral, box, and nuclear inputs at declared order. Do not conflate `mu→3e` tree amplitude alone with full amplitude. Any experimental limit and branching ratio denominator must be explicitly cited and versioned.

Run all focused tests, original frozen receipt replays when accessible, `git diff --check`, commit/push only research branch. The frozen main-scanning branch stays untouched.

**Completion:** `LFV_FULL_COVERAGE_VALIDATED` only for genuinely complete declared mandatory LFV set. Otherwise `LFV_FULL_COVERAGE_BLOCKED` and precise missing diagram list. A smaller individually complete observable may be declared `LFV_SCOPED_OBSERVABLE_VALIDATED` without implying global LFV completeness. Do not re-open B or move on to Higgs unless the evidence and research scope are cleanly separated. No new scans, Condor jobs, mass grids, or MG5 production.
