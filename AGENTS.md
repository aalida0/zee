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

## CURRENT TASK — PAPER 1 FEASIBILITY REVIEW; STOP expanding one-loop tasks

**Read `research/full_constraints/PAPER1_SCOPE_DECISION_2026-11-07.md` FIRST.**

The user wants a publishable physics paper on the **Zee Type-II
H2±→H1±Z cascade**, with a genuinely meaningful scan/constraints
and collider prospects, not an indefinite series of standalone
loop implementations. After validated fixed-card Higgs, B and
LFV calculations, the remaining full-physics gates still cannot
be promoted to true exclusions. We must stop repeatedly opening
new higher-loop/width computational tasks without first evaluating
the manuscript's scientific **viability and unique contribution**
versus Herrero-García et al. JHEP 2017 full Zee scan and
Florentino/Romão/Silva EPJC 2021 cascade analysis.

Latest bound at `1986edf`: ATLAS VBF h→bb selected 1σ
width-shift thresholds D7 (-0.857/+2.843) MeV,
F13 (-0.986/+2.279) MeV. Those are endpoint sensitivities
and NOT theory uncertainty bounds. Physical Γtotal,
absolute h125 μ and exclusions are still UNKNOWN.
This weak measurement does **not** justify another
month of off-shell scalar 4f / Majorana hνν loops.
B still `B_FULL_RATE_BLOCKED` pending documented Wilson-
dependent uncertainty specialist input. LFV still
`LFV_FULL_COVERAGE_BLOCKED` with complex missing gauge
operator/coherent rates and corrected nuclear-current issue.
Higgs full remains BLOCKED; scalar/neutrino/EWPO
validated within declared scope; global vacuum UNKNOWN.

**NOW: produce only** `research/full_constraints/PAPER1_FEASIBILITY_REVIEW.md`.
Compare full-text prior 2017 and 2021 figures/scope with proposed
new physics, check old 33 vacuum certified historical IDs
against saved D14 production/cascade inputs (only if source
joins exist), choose at most 4 defensible result figures, give
a peer-review-style novelty and feasibility judgement, and
contrast A fully constrained (requires unresolved theory) vs
B explicitly conditional/scoped (user approval required).
Use only existing saved source data, not new cards/scan.
Do not claim global acceptance or a real physical veto
from B/LFV/Higgs partial subset results. A scoped result can
be shown only as 'conditional on unimplemented constraints',
not 'allowed Zee parameter region'.

No code/gen changes, exploratory pilot or final scan, no
Condor/MG5, no independent new loop derivations.
Frozen Modules0–13/D14 and
`feature/zee-d14-conditional-cascade-scan` at `133a340`
remain protected. Commit/push only review/report evidence
on `research/zee-full-constraints` in English.
The user must explicitly approve any change of paper scope
AND authorize a future single final parameter-space scan.

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
