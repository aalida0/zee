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

## CURRENT TASK — bounded flavor–charged-cascade novelty kill test (7 Nov 2026)

**This task supersedes the completed collider-feasibility pilot.** The collider pilot's result is `BACKGROUND_MODEL_BLOCKED` and is preserved as historical evidence; do NOT repeat collider inventory, generate events, run Delphes, or restart LFV two-loop calculations. The user authorized a **source-bound examination of existing D12/D14 cards** to decide whether Paper 1 has a substantive new flavor–charged-Higgs physics result *without event generation*, **not** a new parameter-space scan.

**READ AND EXECUTE:** `research/full_constraints/FLAVOR_CASCADE_NOVELTY_PILOT_TASK.md`. Its detailed source, model, novelty, comparison, validation, and stop policies are binding. Read the full `PAPER1_FEASIBILITY_REVIEW.md`, `D12_FLAVOR_COLLIDER_AUDIT.md`, `LFV_TEXTURE_MATERIALITY_RESULT.md`, and 2017/2021 primary papers before any positive novelty claim.

- Existing D12's 136 Yukawa designs show large conditional leptonic daughter BR changes, but already state **novelty not established**, and full LFV is UNKNOWN.
- D14 maps **16** unique tree-vacuum-certificate spectra at 13 TeV, **3** at 14 TeV; NO/IO/family cascade differences at fixed spectrum are small. D12 D7/F13 are **not** the same exact scalar cards as D14 map IDs.
- Quantify paired exact-fixed-card `H1→tb`, `H1→ℓν`, `H2→H1Z`, and cascade daughter BRs from **existing saved** model data, not rounded table joins or guessed generator rates. Compare what the 2017 JHEP and 2021 EPJC papers already established plus relevant later sources/citations; attempt to **disprove** proposed novelty.
- Return `GO_CONDITIONAL_PAPER_CANDIDATE`, `NO_GO_CURRENT_PAPER1_CENTER`, or `SOURCE_BLOCKED` with reviewer-level evidence. No experimental allowedness or sensitivity claim.
- Save a compact report, machine-readable witness matrix, and source comparison **only** under `research/full_constraints/`. Commit/push validated files to `research/zee-full-constraints` only.
- Preserve `global_acceptance=null`, scalar/vacuum/EWPO/neutrino scoped selections, full B/LFV/Higgs UNKNOWN statuses, the frozen source files and the one-final-scan approval requirement.

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

Execute `research/full_constraints/FLAVOR_CASCADE_NOVELTY_PILOT_TASK.md`: fixed-card quantitative and literature novelty audit, no new scan or event generation. Output `FLAVOR_CASCADE_NOVELTY_PILOT_REPORT.md`, `flavor_cascade/NOVELTY_WITNESS_MATRIX.json`, `flavor_cascade/LITERATURE_COMPARISON.md` under `research/full_constraints/`, with a clear GO/NO-GO.
