# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## Current milestone — Higgs coverage and h125 charged-loop integration

The user requires genuinely validated LFV, B→Xsγ and Higgs exclusions
before **one final large scan**. B and LFV source/validation gates are
already executed on this research branch:
- B `B_FULL_RATE_BLOCKED` at `64bdf27`: coherent two-state rates exist
  but independent matched physical rate and theory uncertainty are absent.
- LFV `LFV_FULL_COVERAGE_BLOCKED` at `da6e858`: contact three-body
  rate and interference independently validated, but gauge-invariant
  radiative and complete three-body operator matching remain missing.
  Frozen Module3/4 tests pass 73/75; the two failures assert historical
  branch names and do not signify numerical physics failures.

**Current task: read `research/full_constraints/HIGGS_NEXT_STAGE.md`,
`research/full_constraints/HIGGS_TASK.md` and `PLAN.md`, then
execute the bounded HiggsTools coverage and corrected h125 study.**

First inventory the actual experimental data, analysis processes and
required model-specific rates. Then try to validate the complete
h125 diphoton **W+fermion+both mixed charged scalars** amplitude in a
common physical tree-input scheme, and consume only existing exact
H2 benchmark production. Do not treat a single channel as a full
HiggsTools pass. Full-loop SPheno remains UNAVAILABLE. Preserve
per-analysis `MISSING_PREDICTION`, `NOT_APPLICABLE` and unknown
statuses. A model-correct, validated **scoped fail** may exclude a
point, but no globally allowed point can be declared while applicable
channels are missing.

**Do not rerun B/LFV audits, alter protected Modules0–13, launch
new parameter proposals or pilot scans, submit Condor, run a broad
MG5 production campaign, or touch the frozen conditional branch.**
Current work is a research-only Higgs stage on existing cards.
No final scan authorized. Log/report code and commits in English.

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
