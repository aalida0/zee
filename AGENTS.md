# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## Mandatory source-first literature gate (new: 7 Nov 2026)

Before claiming any Zee-specific loop calculation, scalar/vacuum constraint,
flavor uncertainty, or numerical implementation is absent from the literature,
**read** `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`
and the actual paper full text, then check relevant **references AND citing works**.
Document DOI/arXiv, exact equation, physical particle content, Yukawa
restrictions, source/code version, and a tested limiting case. A previous
false absence claim overlooked Florentino–Romão–Silva 2021 App. D.3 Eq(D.20)
for mixed charged-scalar h→Zγ, Hue 2018 unequal-mass PV formulas,
Bilenky–Santamaria 1994 singlet EFT, and old Zee LFV box/Z-penguin formulas.
Do **not** call an unimplemented published expression nonexistent; do not call
a restricted formula complete general Zee physics. Citation-search indexing is
not exhaustive; report limitations. Always preserve original frozen modules.

## CURRENT TASK — execute source-matched full one-loop Zee LFV operators

**Read `research/full_constraints/LFV_SOURCE_TO_CODE_TASK.md` first**,
then `LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`,
`LFV_EXECUTION_REPORT.md` and `LFV_COVERAGE.md`.

After the two-way citation audit we now know directly relevant
published source formulas:
- Bilenky & Santamaria 1994, gauge-invariant singlet-F EFT;
- Mitsuda & Sasaki 2001, TWO mixed charged-scalar F^4 mu3e box;
- Ghosal et al. 2001, mixed charged-scalar on-shell LFV Z vertex;
- Primulando et al. 2022, conversion operator controls;
- FlexibleSUSY NPointFunctions 2024, generic tree+one-loop mu3e
  and mu-e conversion, with real generated coefficients;
- Altmannshofer et al. 2025 public 2HDM two-loop LFV: existing
  neutral fermion/photon subset is ALREADY in Module4.

**STOP broad surveys and speculative new symbolic two-loop work.**
Produce an **actually executed**, complete tree+one-loop
`μ→3e` **complex operator-vector cross-check** on the original
D7/F13 fixed physical cards and independent conversion tests,
or prove exact code/physics limitation after one bounded setup
attempt. Check full penguin/box/gauge topology coverage and
correctness; do not confuse a restricted paper's F-only form
with a full Zee one-loop calculation.

Current previously validated: charged F dipoles and neutral
photon subset, full 3-body rate kernel against Dirac traces,
gold-target FlavorKit scalar isovector **6.972% rate difference**
which must be checked against another nuclear matching.
Unvalidated complete amplitude remains UNKNOWN.
Full two-loop Wγ/gauge Barr–Zee groups remain separate; do NOT
claim `LFV_FULL_COVERAGE_VALIDATED` from one-loop alone.

Higgs `HIGGS_ZGAMMA_2021_RESCUE_TASK.md` is **queued**, now
with 2019 Zee and 2018 general unequal-mass reference for
source-independent checks. B rate is queued for specialist
answer, `B_FULL_RATE_BLOCKED`; do NOT rerun HEPfit code.
Higgs `HIGGS_FULL_COVERAGE_BLOCKED` at prior fixed cards.
No new scalar points, scans of any size, Condor, MG5 production
or use of broken SPheno full-loop masses. Frozen
`feature/zee-d14-conditional-cascade-scan` and Modules0–13
unchanged. Work only on research branch and commit/push
source-verified, independently tested code/evidence in English.

## Mandatory physics safeguards

- "Complete" means all materially relevant contributions at the
  **explicitly declared perturbative order** with justified numerical
  and theoretical uncertainties, correct interference and physical
  confidence interpretation. Not literally all perturbative orders.
- Two mixed Zee charged states are NOT separately subject to the
  single Type-II 670 GeV bound. Use coherent Wilson coefficients.
- The corrected general 2HDM two-loop LFV backend is NOT complete Zee;
  the neutral fermion/photon subset is already in Module4 and must
  not be double-counted.
- SARAH/SPheno **full-loop observables are unavailable** (unphysical
  ~10^6 GeV WW loop widths and eV neutrino input-scheme mismatches).
  Compiling the backend did not validate its physics.
- HiggsTools requires source-bound rates for every applicable
  channel and collision energy; missing predictions are NOT zeros.
- A validated single failing observable can yield PHYSICAL_FAIL.
  `global_acceptance=PASS` requires all mandatory observables
  independently covered. Any uncomputed mandatory observable -> UNKNOWN.
- Original Modules0–13, D14 scanners/reports, 20k/225 collections,
  16-point MG5 map, all frozen source/receipts and separate B research
  branch are **read-only**. Work in `research/full_constraints/` and
  isolated optional adapters, retaining complete provenance and tests.
- No new parameter-space proposals (even a pilot), no exploratory
  scans, no Condor submission, no production campaign, no unauthorized
  merge into the frozen final-scan branch. Existing saved cards and
  analytic model-limit controls may be evaluated for validation only.
- Timebox/source-gate every area. A blocked full-physics result must
  remain UNKNOWN, not become a soft/conditional claim mislabeled 95% CL.
- Use English for all Codex sessions, notes, code review and commits.

## Current deliverable

A source-verified B→Xsγ feasibility and full-rate path
(`FEASIBILITY_GATE.md`, `BSGAMMA_COVERAGE.md`), with executable
bounded controls only if scientifically supported. Commit and push
to this research branch. Retain unvalidated results explicitly
research-only and the original conditional pipeline unchanged.
