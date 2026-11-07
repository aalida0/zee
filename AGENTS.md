# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## CURRENT TASK — execute SusHi H/A production and neutral width bridge

**Read `research/full_constraints/HIGGS_SUSHI_EXECUTION_TASK.md` first.**
Also read `SCANNERS_HIGGS_REUSE.md`, `HIGGS_COVERAGE.md`,
`HIGGS_EXECUTION_REPORT.md` and `PROGRESS_TO_FINAL_SCAN.md`.

User's immediate focus is to **reuse physics calculators** for
missing Zee Higgs exclusions instead of extending ScannerS itself.
The job is to actually **run** pinned SusHi on D7/F13 ORIGINAL saved
points and qualify its neutral Type-II quark Yukawa mapping; then
evaluate transferable HDECAY/anyHdecay widths and model-specific
additional Zee channels. Report an executed value or exact compile/
source blocker, not another long inventory. Use HiggsTools 1.1.3 as
the consumer of only complete model-matched channel inputs.

B→Xsγ and LFV remain independently BLOCKED at their recorded
source/scientific gates. The separate HEPfit rate execution task
`research/full_constraints/HEPFIT_RATE_EXECUTION_TASK.md` is
**queued, not canceled**. Do not run both streams in one Codex
session or claim one resolves the other.

Do not rewrite existing full LO h→γγ or frozen Modules0–13,
or use pathological full-loop SPheno widths. Preserve the
frozen `feature/zee-d14-conditional-cascade-scan` at `133a340`.
No new random scalar cards, exploratory/large parameter scans,
HTCondor submissions, MG5 production campaigns or user final scan.
Source-pin source/package versions and only original fixed D12/D14
cards for numerical validation. If required rate or decay channels
cannot be source-qualified, mark `MISSING_PREDICTION` rather than
zero. No hard Higgs exclusion until full applicable signal/uncertainty
requirements are met. Work only on research branch, commit/push
validated artifacts, and use English in all progress/report text.

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
