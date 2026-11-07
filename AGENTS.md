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

## CURRENT TASK — use verified h125 widths for actual signal strengths

Read `research/full_constraints/HIGGS_H125_SIGNAL_STRENGTH_TASK.md`
FIRST; then the completed `HIGGS_ZGAMMA_COMPLETE_H125.md`,
`HIGGS_EXECUTION_REPORT.md`, exact D7/F13 original card evidence
and pinned HiggsTools/HiggsSignals coverage.

At `1166f15`, **complete leading one-loop** h125→Zgamma
is independently VALIDATED at D7/F13, with source-bound HEPfit
SM and signed one-scalar checks. Γ_Zγ/SM=(0.978770448547,
0.989590176981); earlier verified Γ_γγ/SM=(0.9317959556,
0.9750252264). These are source-verified partial widths,
**not** signal strengths or exclusions. Do NOT rederive W,
fermion, mixed scalar or PV routing loops again.

**Now build model-consistent h125 Γtotal and Higgs production ratios**
on these ORIGINAL cards using transferable higher-order standard
decays and native Zee general complex lepton Yukawas plus actual
LFV/exotic channels. Quantify coverage and missing inputs first.
If sufficiently complete, compute 1–3 actual source-matched
h125 signal strengths and try only an experimentally compatible
pinned HiggsSignals category. Do not mix HiggsTools default
Zgamma=0 or conditional legacy χ² with a physical 95% CL.
Use correct energy/production mixtures and theoretically justified
uncertainty; otherwise report explicit observable-specific blocker.

Important prioritization: previous D7/F13 heavy-H/A ττ central
diagnostics were exceptionally small and have no certified
physical exclusion; **do not initiate new heavy-H/A Zgamma,
A→WW/ZZ, multi-body or tau tau likelihood loops in this task**.
New physical h125 channel/experimental result has higher value.

LFV at `77148f0`: complete 1-loop still UNKNOWN; validated
F-only box, on-shell Z and FlavorKit scalar proton/neutron
bug; NPointFunctions needs newer FeynArts/FormCalc, not a proven
Zee-model incompatibility. B `B_FULL_RATE_BLOCKED` for
Wilson-dependent hadronic uncertainty. Vacuum global UNKNOWN.
These statuses are unchanged and are NOT to be re-audited now.

Preserve research-only branch `research/zee-full-constraints`.
Frozen Modules0–13, saved D14 and
`feature/zee-d14-conditional-cascade-scan` at `133a340`
are read-only. No new mass/Yukawa proposals or parameter scans
(including pilot), Condor, broad MG5, fake full widths or
global PASS. Commit/push source-verified work, English reports.

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
