# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## CURRENT TASK — execute independent HEPfit B→Xsγ rates

**Read `research/full_constraints/HEPFIT_RATE_EXECUTION_TASK.md` first.**
Also read `research/full_constraints/FEASIBILITY_GATE.md`,
`research/full_constraints/BSGAMMA_COVERAGE.md`,
`research/full_constraints/PROGRESS_TO_FINAL_SCAN.md` and
`research/full_constraints/SOURCE_MANIFEST.json`.

The SusHi/HDECAY Higgs stage is **complete as a bounded task** at
commit `2356cea`: SusHi 1.7.0 genuinely executes validated 13-TeV
LO ggF/bbH for H/A on both original D7/F13 cards, with LO coupling
and PDF/scale controls; anyHdecay/HDECAY 6.60 gives transferable
D7 neutral partial widths and native Zee H/A→H1W/lepton additions.
Its total widths remain **INCOMPLETE**. Higgs
`HIGGS_FULL_COVERAGE_BLOCKED` is not promoted. Do not repeat
this stage or overwrite its evidence.

**Now calculate real, independently executed HEPfit
B→Xsγ one-state rates and, if feasible, a coherent Zee
two-charged-state order-separated matching bridge.** The objective
is an independently validated finite-cut physical rate and an
independently justified NP uncertainty prescription, not more
source inventories. Use the pinned HEPfit source and the original
D12 model points. A compiled/running central rate without model-
appropriate accuracy and uncertainties remains
`B_FULL_RATE_BLOCKED`; do not fabricate exclusion.

LFV remains `LFV_FULL_COVERAGE_BLOCKED`.
The frozen original Modules0–13 and D14 study plus
`feature/zee-d14-conditional-cascade-scan` at `133a340`
must remain untouched. No new scalar parameter proposals, pilot
or large scan, HTCondor submission, MG5 production, or final
global acceptance claim. Keep new work and test receipts under
`research/full_constraints/bsgamma_hepfit/`; English in
all logs/commits. Commit/push only source-verified code and reports.

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
