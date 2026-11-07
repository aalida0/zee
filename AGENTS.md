# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## CURRENT TASK — independently execute HEPfit B→Xsγ physical rate

User wants **actual complete LFV, B→Xsγ and Higgs exclusions** before
one final large scan. We have completed bounded feasibility and
Higgs/LFV source studies. **No complete physical exclusion is yet
validated.**

**Read `research/full_constraints/HEPFIT_RATE_EXECUTION_TASK.md` first.**
Also read `research/full_constraints/PROGRESS_TO_FINAL_SCAN.md`,
`FEASIBILITY_GATE.md`, `BSGAMMA_COVERAGE.md` and source pins.

The current task is an **actual, independently executed** pinned
HEPfit THDM B→Xsγ benchmark, followed if feasible by an isolated
coherent two-mixed-state order-separated NLO Wilson adapter and
research comparison to the frozen D9B rate. We do NOT want another
generic public-code inventory, code-only self-tests or rederived
Module5 matching. Output an executed physical rate, or exact build/
source blocker. The theory/NP uncertainty gate is separate; a
numerical rate does NOT imply a 95% CL exclusion.

After source-validated calculation, update the real milestone
scorecard; never inflate completion percentages from additional
scripts/tests alone. If independent full physical rate validation or
justified NP theory errors are absent, keep
`B_FULL_RATE_BLOCKED`.

Frozen parent `feature/zee-d14-conditional-cascade-scan` at
`133a340` is protected and untouched. Original Modules0–13,
previous D14 evidence, LFV and Higgs research outputs are read-only.
No random proposals, small/big scans, Condor, MG5 production,
or final scan without explicit separate authorization.
Use English for commits/docs/logs.

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
