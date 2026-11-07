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

## CURRENT TASK — decisive Candidate A tree-vacuum / charged-mixing investigation (7 Nov 2026)

**This supersedes the completed flavor–charged-cascade novelty NO-GO and collider inventory tasks.** The user has authorized **one comprehensive, bounded scalar-theory study** with public-code reuse and a final GO/NO-GO paper decision, not a new unconstrained model scan or event simulation.

**READ FIRST AND EXECUTE IN FULL:** `research/full_constraints/CANDIDATE_A_GLOBAL_VACUUM_MIXING_DECISIVE_TASK.md`. Follow its 8 work packages, source/equation/code/literature gate, CPU/RAM budgets, explicit necessary-versus-sufficient proof standards, reproducibility deliverables, and decision criteria. Begin with frozen D10 exact potential and original 2005/2021 primary papers, including 2005 Eq. (23), not previously completed collider/LFV tasks. Use public SOS/homotopy/algebra tools if practicable, with actual installed versions and evidence.

**Precise user authorization override for this task only:** deterministic scalar-only 1D Mu4 continuation of existing D10 cards and trial-field search within the task's numerical point/resource limits is permitted to test vacuum/mixing bounds. This overrides the general ban on **new scalar-only diagnostic evaluation points only within this narrowly authorized study**; it does **not** permit a new broad scalar/neutrino/flavor scan, a full model acceptance campaign, changes to frozen modules, or Condor/MG5/Pythia/Delphes/collider simulations. The eventual one final full-constraint scan remains unauthorized.

- Source exact CP-conserving full-ten-real-field D10 potential (not the most general complex Zee theory); prove identities/gauge coverage/field-space inequalities.
- Both rigorously sufficient global-vacuum certificates and rigorously necessary no-deeper-witness inequalities; test and potentially **refute** the previously estimated P2 Mu4 <=~1346.14 GeV bound.
- Recalculate charged masses and signed mixing consistently on every cubic-coupling deformation; connect only to source-validated off-diagonal Z coupling and conditional tree partial width, no detector reach.
- Cross-examine 2005 and 2021 published results, generic public algebra/vacuum codes and citing literature. GO only if an independently verified new reusable result with material scalar physics consequences is demonstrably distinct. Otherwise NO-GO or explicit INCONCLUSIVE.
- All original modules/inputs/receipts remain read-only; write compact evidence and standalone adapters under `research/full_constraints/candidate_a/`, summarize in `research/full_constraints/CANDIDATE_A_DECISIVE_REPORT.md`. Commit and push to research branch only.
- Keep `global_acceptance=null`; do not infer quantum/thermal vacuum stability, full B/LFV/Higgs allowedness, physical 95% exclusion or HL-LHC/FCC-hh sensitivity.

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

Execute `research/full_constraints/CANDIDATE_A_GLOBAL_VACUUM_MIXING_DECISIVE_TASK.md` completely. Produce one decisive report, public-code/literature ledger, exact positive/negative certificate objects and source-bound mixing/partial-width results as supported. End in GO_SCALAR_THEORY_PAPER_CANDIDATE, NO_GO_CANDIDATE_A or INCONCLUSIVE_METHOD_BLOCKED. No follow-on scan authorization.
