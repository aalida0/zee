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

## CURRENT TASK — scoped paper constraints and matched-energy collider pilot

**User approved this next bounded milestone:** turn our Zee Type-II
H2±→H1±Z paper into a clear **applied-subset** methodology,
assess **actual** source-bound 14 TeV raw pre-detector yields,
and test a small same-energy signal/background trilepton pilot
only where relevant existing samples are available.

**READ FIRST**
`research/full_constraints/PAPER1_CONSTRAINT_AND_COLLIDER_FEASIBILITY_2026-11-07.md`,
then `research/full_constraints/COLLIDER_FEASIBILITY_NEXT_TASK.md`.
Consult original `PAPER1_FEASIBILITY_REVIEW.md`,
`module14/conditional_scan/PRODUCTION_MAP_REPORT.md`
and B/LFV/Higgs coverage reports. Do not restart the
FormCalc/SARAH/FlexibleSUSY investigation or full two-loop
calculations.

**Source-backed starting observations:**
- 16 native 13 TeV LO 5FS charge-summed H2 associated
  integrations on *tree-vacuum-certified* historical points;
  3 separate 14 TeV integrations (IDs 15591,2264,15673).
- 14 TeV at 3000 fb^-1, including stored BR(H1→tb),
  Z→ee/mumu and exactly one direct W→e/mu with the
  other W→hadrons, gives **raw 3l counts** 306.83–306.92,
  149.10–149.13, 96.44–96.59 **before acceptance**.
  See `collider/RAW_14TEV_PREDICTION.json`.
- Reproduce with `python3 research/full_constraints/collider/raw_decay_budget.py`
  and `python3 -m unittest discover -s research/full_constraints/collider -p 'test_*.py' -v`.
  The code and raw JSON have been source-calculated but
  the end-to-end Python command must be run on the repo
  checkout. Report any execution error, do not claim tests
  that were not actually run.

**Physics scope:** Scalar BFB/unitarity/EWPO/one-loop
neutrino closure plus a **sufficient positive tree-vacuum
certificate** are explicitly applied within stated order.
B→Xsγ theory uncertainty, LFV mixed-F/gauge loops,
μ→3e non-dipole interference, μ→e conversion and
Higgs full rates remain **UNKNOWN**. Display their
limited predictions as `DIAGNOSTIC_ONLY`, with explicit
experimental reference scales, *never* as full
model-pass/exclusion or assumed zero. `global_acceptance=null`
and **no new parameter-space scan**.

**Collider scope:** Most promising pilot 3 e/μ with
OSSF Z and top semileptonic/hadronic system; in 5FS,
after H1→tb and both tops→Wb, **three** decay-origin
b quarks (no hard spectator b) before shower. Require
genuine same-energy signal/background. User has
historical 13.6 TeV ATLAS HepMC backgrounds but their
process/weights/availability for this Zee channel are
NOT CONFIRMED. Inventory first. If suitable, stage a
single 13.6 TeV pilot on old exact certified IDs
15591 and 2264 (at most 2000 signal events per card),
with cross section and decay/selection source hashes.
Use existing backgrounds only when same energy and
no overlap. No Condor/heavy production. If missing
background, stop at yield-only feasibility.
**Never** combine 14 TeV signal with 13.6 TeV
backgrounds, or use published 2021 tb search limits
on a different final state. Real CLs requires signal
acceptance, background MC and systematic model.

**Deliverables:** source-bound scoped constraint-contract
JSON plus `research/full_constraints/COLLIDER_FEASIBILITY_PILOT_REPORT.md`
with real pilot cutflow/plots if executed, or an explicit
input blocker, and go/no-go for a larger detector study.
User has NOT authorized the eventual **one final
parameter-space scan**.

Frozen Modules0–13, historical D14 inputs/receipts,
the feature scan branch `feature/zee-d14-conditional-cascade-scan`
at `133a340`, and older B/Higgs/LFV baseline
data are read-only. All output to new research files
and ignored scratch. Record actual test result, diff
and commit/push on `research/zee-full-constraints`.

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

`research/full_constraints/PAPER1_CONSTRAINT_CONTRACT.json`
and `research/full_constraints/COLLIDER_FEASIBILITY_PILOT_REPORT.md`
with source-bound background availability and matched-energy
signal/acceptance or explicit NULL, following
`COLLIDER_FEASIBILITY_NEXT_TASK.md`.
No unsupported HL-LHC reach/physical exclusion and
no scan authorization.
