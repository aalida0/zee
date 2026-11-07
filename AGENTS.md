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

## CURRENT TASK — one measurable h125 VBF→bb rate or exact materiality blocker

**Read** `research/full_constraints/HIGGS_H125_VBF_BB_OBSERVABLE_GATE_TASK.md`
first, then `HIGGS_H125_SIGNAL_STRENGTH_REPORT.md`,
`HIGGS_ZGAMMA_COMPLETE_H125.md`, HiggsTools pinned source and
ATLAS `2011.08280` VBF bb 13-TeV measurement.

The most recent fixed-card `654794f` h125 integration completed
and source-pinned all normal partial widths, including corrected
HDECAY charm input, LFV and validated γγ/Zγ. Its known-channel
widths are **4.280495766 MeV (D7)** and **4.005236276 MeV
(F13)**, NOT certified Γtotal. Three width-independent
signal-strength ratios are proven (D7 γγ/WW* VBF 0.933958096,
Zγ/WW* VBF 0.981041588; F13 0.975031103/0.989596141).
Absolute μ and experimental constraints are UNKNOWN.

**Goal:** assess the source-matched ATLAS `μ_VBF,bb≈0.99±0.35`
observable first. Set its sensitivity requirement before chasing
arbitrary sub-1% corrections; identify and (if possible) bound
virtual Zee exotic h125 off-shell states, radiative hνν and
interference with existing SM 4-body widths. Preserve correct
reference normalization `SMHiggsEW σ×BR=2.20257783862 pb`;
the pinned source is an **absolute rate**, not μ=2.16.
Qualify actual model signal rate+uncertainty+acceptance; run a
single exact measurement if justified. Otherwise stop with
`H125_ABSOLUTE_MU_BLOCKED` and a quantitative, source-specific
missing input. DO NOT create arbitrary 5/10% theory errors,
treat closed on-shell scalars as proof of zero virtual widths,
or claim one observation makes full Higgs PASS.
**No heavy H/A loop or ττ likelihood work in this task**;
it currently has far less projected value on D7/F13.

B stays `B_FULL_RATE_BLOCKED` pending flavor specialist; LFV
`LFV_FULL_COVERAGE_BLOCKED` pending full 1-loop/gauge terms,
with confirmed FlavorKit scalar conversion proton/neutron bug;
vacuum global UNKNOWN. Do not restart any of those during this
task. Keep Modules0–13, original D14 data and scan branch
`feature/zee-d14-conditional-cascade-scan` at `133a340`
frozen. No parameter-space points/scans of any size, Condor,
MG5 production or SPheno broken full-loop masses.
Research branch only, source-pinned numeric tests and English
commits/reports, commit/push scope-validated findings.

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
