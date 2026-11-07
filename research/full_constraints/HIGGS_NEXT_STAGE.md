# Next Higgs stage — validate source-bound model predictions and actual analysis coverage

**Branch:** `research/zee-full-constraints`.
**Entry baseline:** commit `da6e85846bca7c050a70cfff06323c067f6ec75b`.
**Status at start:** B `B_FULL_RATE_BLOCKED`; LFV `LFV_FULL_COVERAGE_BLOCKED`; Higgs `NOT_EVALUATED` in this research branch.
**Goal:** Move the Higgs constraint as far as source-validated public software genuinely allows, in an explicitly bounded effort. Do NOT assert all-three-constraints completion.

**Read first:**
`research/full_constraints/PLAN.md`,
`research/full_constraints/HIGGS_TASK.md`,
`research/full_constraints/FEASIBILITY_GATE.md`,
`research/full_constraints/LFV_EXECUTION_REPORT.md`,
`module14/FINAL_PHYSICS_FREEZE.md`,
`module14/PHYSICS_ADAPTER_READINESS.md`,
`module13/higgstools.py`,
`module14/external.py`,
`module14/decays.py`,
`module14/conditional_scan/PRODUCTION_MAP_REPORT.md`.
Actual pinned source: HiggsTools 1.1.3, experimental HB/HS dataset commits recorded in original source-controlled evidence; SARAH original Zee restricted model / UFO / Module7 complete tree two-body widths; 16 actual H2 LO tb-associated 13-TeV rates, and 3 real 14-TeV rates, only at already calculated scalar IDs.

## Phase 0 — Source, dataset and process coverage inventory FIRST (mandatory)

1. Enumerate **all** HiggsBounds `limit.id()` for actual retained dataset source, and matching HiggsSignals measurements. For the saved D12 witnesses and original D14 benchmark candidates, assign a deterministic per-analysis status:
   - `APPLICABLE_INPUT_COMPLETE`, after explicit mass range, resonance width, energy, production, decay, channel/charge and source checks;
   - `NOT_APPLICABLE`, only if **proven** from an actual mass, threshold, forbidden vertex, collision energy or search selection;
   - `MISSING_PREDICTION`, if required production, BR, coupling or width is absent;
   - `MISSING_EXPERIMENTAL_COVERAGE`, for a physically relevant channel without a corresponding loaded limit.
   Never call `NOT_APPLICABLE` merely because a rate was not computed.
2. For every applicable limit, list the exact required `HiggsTools` input, perturbative order, energy, supported production mode and which source actually calculates it. Preserve explicit dataset and library byte hashes.
3. Distinguish `h125` signal-strength data, `H/A` neutral searches, `H1/H2` charged searches, and novel `H2→H1Z` cascades. Do not imply the latter are tested merely because the HB library includes generic single-charged searches.
4. Make a machine-readable gap and applicability matrix with source links and limitations. This inventory decides whether source-backed *full* Higgs exclusion is feasible without an external large production campaign.

## Phase A — h125 physically matched charged-loop calculation (one concrete deliverable)

1. Existing `module13/higgstools.py:h125` uses tree Yukawa/gauge kappas via `effectiveCouplingInput`, and does not include Zee H1/H2 charged loops. Use the **already validated native SARAH restricted-model scalar potential and diagonal hH+H− trilinears**, explicitly both charged eigenstates, with a published charged-scalar loop function for h→γγ. Cross-check its signs, normalization, electric charge, mass/mixing limits and dimensional conventions with an **independent** source/formula. Ward identity and charged scalar QED control where relevant.
2. On frozen original D12 cards, calculate complete **leading one-loop h→γγ amplitude** including W and fermion loops plus both charged scalars in **one common physical tree-input scheme**. Do not splice a `SPheno` full-loop width onto the tree spectrum: saved full-loop SPheno neutrinos, h pole masses and widths are unphysical. Validate the pure SM and decoupling limits plus the scalar-loop difference against independently documented reference.
3. Investigate h→Zγ similarly only if a source-validated mixed H1/H2 Z current and associated complete counterterm/gauge group can be established. The off-diagonal Zee Z charge is nonzero, so `Zγ` cannot be obtained by naively doubling a 2HDM diagonal scalar contribution; show all allowed charged matrices, signed mixing, and gauge identities. Otherwise `hZgamma=UNKNOWN`.
4. For HiggsSignals/Boson h125, feed validated **complete normalized** widths/BR/kappas in supported input mode (with loop channels); check total-width consistency, LFV h→ll if calculated, effective-coupling conventions and no double counting. A corrected isolated h→γγ ratio is not itself a complete h125 likelihood; do not promote that unless all required channels are covered with source-bound predictions.

## Phase B — Existing fixed-card charged and neutral searches

1. For the **existing** 16 13-TeV associated H2 production cards, bind exactly `mH1,mH2,tanbeta,gamma`, full Yukawa hash, PDF, generator order, energy, both-charge process and event definition. Match frozen D4 tree **full on-shell two-body** BRs and identify which HiggsBounds analyses genuinely accept that process and these mass/width regions.
2. Do not invent 13-TeV H1 production, H/A gg/bb production, 8-TeV equivalents, pair production or NLO K-factors. If missing and materially applicable, `MISSING_PREDICTION`. Numerically evaluate only *existing* source-backed results; no new mass-grid run.
3. Source inventory H/A neutral and charged production tools (SusHi, vh@nnlo, 2HDMC/HDECAY, MadGraph, etc.) **only if needed** to identify an implementation path, and distinguish genuine model transfer from a Type-II proxy. Do not install packages merely to claim coverage.
4. A single fully validated applicable observed search with excluded signal strength may establish a **scoped physical FAIL** even though other applicable channels are missing. A `NOT_EXCLUDED` point under a *full Higgs dataset* requires all declared mandatory applicable channels and h125 inputs complete. Never attach physical PASS to a partial search set.
5. Use original HiggsTools dataset source and numerical input conventions. Include resonance width/rate validity and reference experimental CL, not just an observed ratio >1 from an inconsistent or incomplete source.

## Phase C — Strict physics adapter if justified, otherwise an exact gap

1. Write a source/observable-specific adapter **only for independently validated channels**. Input includes full scalar/family, source hashes, experiment dataset hash, scheme, energy, missing channels and error; output must not silently imply global completeness. Preserve original frozen Module13/Module14 APIs, and keep new code under `research/full_constraints/higgs/` (and optional isolated adapters), tests in that research directory.
2. Exclusion statuses: `VALIDATED_SCOPED_FAIL` if one fully computed applicable analysis establishes a model-specific exclusion; `VALIDATED_FULL_HIGGS_PASS` only if all relevant target analyses and h125 measurements are covered; otherwise `HIGGS_FULL_COVERAGE_BLOCKED` with per-analysis `NOT_EVALUATED` reasons.
3. Mark experimental search channels not in the loaded HB dataset as `MISSING_EXPERIMENTAL_COVERAGE`. Do not convert the absence of a public limit to physical allowedness.

## Validation and completion

- Fix **no** old Modules3/4 test branch-name expectations: archived research LFV result 73/75 passes with two failures that assert now-incorrect branch names only; preserve this transparent accounting.
- Source-bound existing D12 cards/16 historical H2 rates, SM/decoupling controls, independent amplitude/width normalization checks, and error-injection tests. Do not generate parameter-space proposals or a physics scan, submit Condor, rerun original 19 MG5 integrations or perform broad new production.
- `git diff --check`, numerical test logs, exact source + experimental dataset SHA receipts, and documented nonoverwriting scratch results.
- Deliver:
  `research/full_constraints/HIGGS_COVERAGE.md`,
  `HIGGS_EXECUTION_REPORT.md`,
  `HIGGS_VALIDATION.json`,
  source-locked `higgs/` tests/adapter if actually validated.
- Update `research/full_constraints/VALIDATION_MATRIX.json` and `CONSTRAINT_COMPLETION_READINESS.md` but **never** promote B/LFV from blocked to validated.
- Expected status is either `HIGGS_FULL_COVERAGE_VALIDATED` supported by all channel tests, or `HIGGS_FULL_COVERAGE_BLOCKED` with concrete missing sources, and independent `HIGGS_SCOPED_CHANNEL_VALIDATED` if actually achieved.

## Stop condition

Do not launch a new spectrum/production/scanning campaign as a workaround for absent Higgs input. If source coverage says all required neutral/charged production cannot be computed within current resources or exact theory scheme, document each blocker and STOP the full-coverage claim. A source-verified hγγ correction or individual HiggsBounds analysis may still be useful, but is not a global Higgs exclusion.

**The user's objective remains three complete exclusions before the final scan. This task does NOT authorize the final scan.**
