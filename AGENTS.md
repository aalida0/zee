# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## CURRENT TASK — physically justify HEPfit Zee B→Xsγ uncertainty

Read **`research/full_constraints/BSGAMMA_NP_UNCERTAINTY_TASK.md`**
first, plus the pinned **executed** HEPfit rate report and earlier B
coverage ledger. The HEPfit matching and central-rate executable are
**COMPLETE within scoped NLO** at `e2202f1` (37 fixed-card runs,
18 tests). Do NOT reopen BMU matching, build HEPfit again by default,
repeat SuperIso/EOS comparisons or redo previous source searches.

Our immediate missing B physics gate is independently qualified
NLO two-state rate **uncertainty** and one-state published confidence
construction. Execute a **finite fixed-D7/F13 nuisance/scale
propagation**, recording sources, true input covariances and
Wilson-dependent power corrections; compare historical published
one-state prescriptions without silently assigning their NNLO SM
error to our NLO NP model. Demonstrate the exact 95% CL framework
before any physical fail/pass. If irreducible Wilson-dependent
theory covariance or full materiality is unavailable in public
sources, **stop this code stream** and write the exact question to
a flavor specialist. No guessed `theory_sigma` or physical exclusion.

Other tracks: Higgs `HIGGS_FULL_COVERAGE_BLOCKED`, but original
D7/F13 SusHi ggF/bbH and HDECAY partial-width checks are validated.
LFV `LFV_FULL_COVERAGE_BLOCKED` with incomplete gauge and
four-lepton matching. All reports/sources are retained read-only.

Protected parent `feature/zee-d14-conditional-cascade-scan`
at `133a340`, Modules0–13 and earlier D14 production/scans
remain immutable. Do not generate new Zee parameter points,
run a parameter scan, submit Condor, launch MG5 production or
claim global Zee acceptance. Only existing exact saved cards
and published reference limit controls may be evaluated.
Commit/push only source-verified work in this research branch.
Communicate in English.

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
