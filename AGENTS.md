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

## CURRENT TASK — finish complete physical h125→Zgamma, D7/F13

**Read `research/full_constraints/HIGGS_ZGAMMA_COMPLETE_H125_TASK.md` first.**
Also read the source audit `HIGGS_ZGAMMA_2021_RESCUE.md`, original
`ZGAMMA_SOURCE_EVIDENCE.json`, saved Higgs neutral and h→γγ
evidence, and the 7-Nov literature citation index.

At `45a9d11` three independent methods (native LoopTools
2.13, analytical/parameter integrals, scalar Ward/UV) agreed on
the **physical photon-adjacent mass ordering** in unequal-mass
h→Zgamma charged-scalar loops; literal Flo21 D.20 differs by
0.232% D7 and 0.0388% F13 **of the mixed scalar kernel**.
The corrected candidate is strongly validated **as a subthreshold
scalar loop in our explicit PV convention**. It does NOT yet
include correct relative W/fermion/scalar signs, complete SM
normalization or CP-odd diagonal-lepton contributions.
Do NOT hold independent physics back solely to demand that
an ambiguously printed formula matches verbatim; document
the source ambiguity, retain falsifying Ward test, and validate
the final full amplitude against independent SM and one-state
2HDM benchmarks.

**The target is ONE completed observable:** physical one-loop
`Γ(h125→Zgamma)` for exact saved D7/F13 cards, with SM
benchmark, full tensor/W+fermion+mixed scalar interference
and source hashes. Do NOT extend to heavy H/A yet; thresholds
and A's CP tensor need a separate new stage. No tau-tau
HiggsBounds likelihood and no final scan until inputs
are independently qualified. Higgs overall remains BLOCKED
even if this h125 sub-observable passes.

LFV last work `77148f0` finished bounded F-only box,
on-shell Z controls and confirmed FlavorKit scalar
proton/neutron interchange; NPointFunctions needs newer
FeynArts/FormCalc, so complete one-loop and two-loop LFV
remain UNKNOWN. Do not retry those packages in this task.
B still `B_FULL_RATE_BLOCKED`, pending specialist
Wilson-dependent uncertainty. Vacuum global UNKNOWN.

All `research/zee-full-constraints` work must preserve
frozen Modules0–13, original D14 and
`feature/zee-d14-conditional-cascade-scan` at `133a340`.
No model-space point generation, exploratory/full scans,
Condor, broad MG5, fictitious Higgs widths, or global pass.
Run actual numerical checks and commit/push only proven
scoped physics output in English.

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
