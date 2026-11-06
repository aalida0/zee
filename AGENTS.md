# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## Current milestone — LFV completion after source-backed B feasibility gate

The user requires fully validated LFV, B→Xsγ and Higgs exclusions
before the one final large scan.

**B source feasibility is complete at `64bdf27`:**
`B_FULL_RATE_BLOCKED`. The nonlinear coherent two-state code is
available, but neither independent matched finite-cut physical
normalization nor a qualified model-specific NP uncertainty is
established. Never mislabel a legacy kernel, 2026 LO linearization,
or backend nuisance as a validated 95% CL Zee exclusion.

**Current task: read and execute**
`research/full_constraints/LFV_NEXT_STAGE.md`,
`research/full_constraints/LFV_TASK.md`,
`research/full_constraints/PLAN.md`, and
`research/full_constraints/FEASIBILITY_GATE.md`.
Focus on **source-level diagram and operator completeness** and an
independently validated new LFV observable/gauge group, if feasible.
Existing corrected general-2HDM neutral-fermion/photon contributions
are ALREADY in Module4, so do not double count.

After LFV reports a real validated scope or exact block, the
independent Higgs coverage task is
`research/full_constraints/HIGGS_TASK.md`. A final all-three-gates
claim is prohibited while B is blocked.

No new parameter-space points or scans of any size, no HTCondor
submission, no model-wide MG5 production. Existing saved cards and
analytic limiting cases are allowed for bounded independent
validation. The original `feature/zee-d14-conditional-cascade-scan`
remains frozen and untouched.

Use English for every Codex title, log, note and commit. Commit and
push only source-verified research changes to this branch.

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
