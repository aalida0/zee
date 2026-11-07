# Paper 1 — bounded flavor–charged-cascade novelty kill test

**Date:** 2026-11-07  
**Research branch:** `research/zee-full-constraints`  
**Starting HEAD:** `4ddecc4c4dbfaa45b705ddf4ef7acdce26407f9d`  
**User approval:** ONE bounded, source-bound study of *existing* Zee model records to decide whether Paper 1 has a defensible new physics center **without new event generation**. This is **NOT** approval for any new parameter-space points, final scan, MG5 runs, Delphes, large collider production, two-loop derivation, complete-flavor reimplementation, or physical exclusions. 

## Scientific question / pre-registered null hypothesis

We need to know whether the existing Type-II-quark + general-complex-lepton Zee model calculations reveal a **nontrivial, quantitative, model-specific neutrino/flavor–charged-scalar connection** beyond:

1. Herrero-García, Ohlsson, Riad, Wirén, JHEP 04 (2017) 130, arXiv:1701.05345 — general Zee neutrino/LFV phenomenology *within its published numerical restrictions*;
2. Florentino, Romão, Silva, EPJC 81 (2021) 1148, arXiv:2106.08332 — `H2± → H1± Z`, charged mixing, cascade BR, production/benchmark studies; lepton completion explicitly left for later work;
3. Heeck–Thapa, PLB 841 (2023) 137910, arXiv:2303.13383; Dev–Heeck–Thapa, EPJC 84 (2024) 148, arXiv:2309.06463; and the subsequent literature recorded in the existing source-rescue audit.

**Working null:** saved Yukawa freedom permits dramatic *conditional* charged-decay changes, but the full LFV/B/Higgs acceptance is unknown; the cascade itself hardly varies among D14 neutrino families; and the conceptual ingredients were substantially known. It may be that there is **no sufficiently new result** for an EPJC paper. Your job is to try to falsify that null, not to manufacture a positive verdict.

Do NOT describe this as 'the first Zee neutrino–cascade connection' or as an experimentally viable model scan.

## Source-first reading and immutable evidence

Read `AGENTS.md` and the full documents below BEFORE modifying or calculating:

- `research/full_constraints/PAPER1_FEASIBILITY_REVIEW.md` (notably §§2–5, including its existing **NO-GO** review);
- `research/full_constraints/PAPER1_SCOPE_DECISION_2026-11-07.md`;
- `research/full_constraints/PAPER1_CONSTRAINT_CONTRACT.json`;
- `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`;
- `module12/D12_FLAVOR_COLLIDER_AUDIT.md`;
- `research/full_constraints/LFV_TEXTURE_MATERIALITY_RESULT.md`;
- `research/full_constraints/LFV_COVERAGE.md`, `BSGAMMA_COVERAGE.md`, `HIGGS_COVERAGE.md`;
- `module14/conditional_scan/PRODUCTION_MAP_REPORT.md`;
- `research/full_constraints/COLLIDER_FEASIBILITY_PILOT_REPORT.md`.

Locate actual original fixed-card and family records, rather than reverse-engineering rounded tables. Candidates include `validation/module12/d12_benchmarks.json`, its associated sensitivity/source receipts, and both D14 `module14/conditional_scan/production_map_13TeV_families.csv` / `production_map_14TeV_families.csv`. Read their schema and provenance, check file sizes/SHAs, and note any records that cannot be accessed or reconstructed. The D14 13 TeV family file represents **16 scalar IDs × 4 neutrino families**; 14 TeV covers **3 IDs × 4 families**. D12 D7 and F13 scalar spectra are **different scalar-card identities** and have **no matching D14 production receipt**. NEVER join on rounded mass values, nearest neighbor, or spectrum label resemblance.

Existing D12 result: 112 structured designs plus 24 specified coefficient perturbations, 136 distinct executed solutions, not an unbiased global scan. D12's source report already says **'Novelty not established.'** Repeating this conclusion without checking the numerical reasons is insufficient; contradicting it without new evidence is worse.

## Work package A — reproduce, then quantify *paired* decay phenomenology

1. Locate and validate the original D12 family rows, the exact same-potential scalar cards D7/F13, both NO/IO families, one-loop neutrino closure and all source hashes. Record inputs and whether the derivations are an independent physics check or merely deterministic arithmetic on saved predictions.
2. For each saved D12 witness and appropriate same-card pairing, extract/recalculate *from saved width components* the following observables at the declared tree/on-shell scheme:
   - `BR(H1 → tb)`, `BR(H1 → e nu_all / mu nu_all / tau nu_all)`, `BR(H1 → all charged-lepton nu)`;
   - `BR(H2 → H1 Z)`, `BR(H2 → tb)`, `BR(H2 → charged-lepton nu)`, total widths if complete in the stated source prescription;
   - `B_cascade_tb = BR(H2 → H1 Z) × BR(H1 → tb)`;
   - `B_cascade_lnu = BR(H2 → H1 Z) × Σ_{ell=e,mu,tau} BR(H1 → ell nu_all)` and individual-flavor variants;
   - their ratios where denominators are nonzero, together with each fixed-scalar family's NO/IO differences.
3. Normalize only within a **single identical scalar production card**; at fixed spectrum, `B_cascade_lnu/B_cascade_tb` is a valid production-independent branching-ratio comparison. For exact D14 rows with genuine 13 or 14 TeV production, report `σ_LO^5FS × B` using the saved native rate exactly ONCE, with the original charged-sum convention. D12/F13 and D12/D7 do NOT receive a D14 cross section. Do not manufacture their production rates or 100 TeV production. No effective selected yields, efficiencies, confidence limits, or HL-LHC/FCC-hh 'reach'.
4. Provide paired counterfactuals holding **scalar potential, tanβ, masses, mixing, SM/CKM card, neutrino target/ordering, and generator setup** constant while changing only admissible *stored* homogeneous Yukawa direction/F design. Quantify absolute and relative BR shifts, whether they are traceable to the H1 total width or the H2 total width, and what is/was held constant. Distinguish choices of target/nuisance priors from actual physical predictions.
5. Reproduce the pre-existing D12 'large leptonic BR' examples **and** the low-joint texture examples. A large shift in a high-F/high-joint example with unqualified LFV does not establish an allowed signature. Note source limitations: tree on-shell two-body widths, omitted off-shell/finite-width/QCD/EW effects and complete-model total widths where applicable. If no source-complete saved widths exist for an observable, use null with reason.

### A1 — numerical materiality tests (prospective criteria, not new exclusions)

Report for each *paired same-scalar* contrast:

- Is `|ΔBR(H1 → all ell nu)| >= 0.10` in **absolute branching fraction**?
- Is the conditional cascade branching ratio into a leptonic H1 daughter at least `2×` different across the two stored solutions (when nonzero)?
- Does a large effect persist across **more than one distinct** fixed scalar card or is it a single hand-designed texture?
- Do existing ±1% coefficient variations, where stored, show an obvious fragility, and what directions were **not** perturbed?
- Are the contrasting points even *conditionally supportable* once all declared applied-scope scalar, vacuum certificate, EWPO, neutrino and perturbativity checks are evaluated and **all missing full flavor/Higgs gates remain UNKNOWN**?

These thresholds are a prioritization device for experimental materiality, NOT a claim about statistical sensitivity or sufficient novelty. Document selection/tuning bias; do not interpret observed retention or rates as parameter-space probabilities.

## Work package B — falsify a claimed neutrino–cascade correlation

Using the original D14 16 × 4 matched families (and 3 × 4 at 14 TeV), quantify on actual source-bound rows:

- variation of `BR(H2 → H1 Z)` and `σ × BR` at identical scalar IDs across saved neutrino orders/families;
- variation of `H1` leptonic-flavor BRs and `H1 → tb` within the identical scalar family;
- whether NO/IO conditional distributions overlap when homogeneous Yukawa freedom is varied;
- whether any link to the neutrino fit is **forced** by the model or **chosen** through particular Yukawa textures;
- whether any apparent scalar-mixing correlation is simply the already-known tree `ZH1H2` coupling, or is induced by a selection/certificate bias.

The known D14 cascade BR spread is approximately 0.000573%–0.0291% across families; recompute on full precision and show if that observation persists. If any claimed correlation disappears under same-scalar controls, mark it **NOT SUPPORTED**. NO/IO comparisons are not ordering sensitivity, especially without a joint neutrino likelihood.

## Work package C — source-based novelty and portability check

Read original full text / published versions and the existing literature rescue audit. Conduct one bounded, dated current literature recheck with specific queries for: `Zee H2 H1 Z cascade neutrino`, `Zee charged scalar leptonic branching Yukawa texture`, `general Zee flavor collider phenomenology`, `off-diagonal charged scalar associated production`. Include backward references and relevant forward-citing papers of 2017/2021, prioritizing papers that make the *same mathematical/phenomenological comparison*. Cite exact equations/figures/sections and published errata, model assumptions (Type-II quarks, general leptons, charged mixing), and whether an identical claim was done before. If online search is unavailable, explicitly mark `LITERATURE_RECHECK_INCOMPLETE`; do NOT assert 'not done before' or 'novel'.

Produce a row-per-claim novelty matrix: `claimed result | quantitative saved evidence | closest published antecedent and exact locator | substantive difference | missing physical condition | NEW/INCREMENTAL/ALREADY_DONE/UNSUPPORTED | reviewer objection`.

At minimum compare:
(a) large H1 leptonic BRs from Yukawa freedom; (b) altered `H2→H1Z→(ell nu)Z` conditional topology; (c) suppressed direct e–mu textures and missing mixed-F LFV; (d) NO/IO discrimination; (e) scalar-vacuum certificate/selection; (f) existing 13/14 TeV production rankings. Do not declare novelty solely from running more numerical benchmark points than a cited work.

## Work package D — physics gate / hostile referee decision

Use `PAPER1_CONSTRAINT_CONTRACT.json` **unchanged** as the acceptance source of truth. In particular:

- `global_acceptance=null`; **no globally Zee-allowed points**;
- `B→Xsγ` coherent NLO real/two-state calculation remains **DIAGNOSTIC** without calibrated physical theory uncertainty/confidence;
- `μ→eγ` retained one-loop + photon Barr–Zee is **DIAGNOSTIC**, not a full bound: mixed-F gauge/charged-current terms are unbounded and F†F is nonzero;
- `μ→3e` tree/dipole subset omits penguin/box interference, and `μ→e` conversion is NOT APPLIED;
- Higgs absolute signal strengths/direct exclusions remain incomplete;
- a D10 sufficient tree-global-vacuum certificate is a positive tree witness, NOT loop/thermal stability; absent certificate is UNKNOWN, not exclusion;
- no experimental `S/sqrt(B)`, CLs, exclusion/reach or beam-energy reweighting.

Classify every proposed paper headline as:

1. `SUPPORTED_SCOPED_AND_DISTINCT` — genuine, source-supported *conditional* model-level result, with exact literature difference and disclosed blockers;
2. `INTERESTING_BUT_UNQUALIFIED` — sizeable conditional observable, but full physics/literature or robustness gap prevents a strong claim;
3. `ALREADY_DONE_OR_INCREMENTAL` — results substantially in 2017/2021/subsequent references or only technical repackaging;
4. `NOT_SUPPORTED` — no demonstrated magnitude, matching, or physical validity.

Make a **single primary verdict**:
- `GO_CONDITIONAL_PAPER_CANDIDATE` only if at least one quantitatively material, reproducible, literature-differentiated *conditional* result is found and the central claim does NOT misrepresent incomplete constraints;
- `NO_GO_CURRENT_PAPER1_CENTER` if data merely reproduce published physics, only show tuned/unqualified extremes, or lack a useful paper result;
- `SOURCE_BLOCKED` if essential original records or reference full text cannot be accessed.

A `GO_CONDITIONAL_PAPER_CANDIDATE` is **not** EPJC acceptance, authorization for a full scan, or authorization for physical exclusion plots. Explain how a critical reviewer would reject your positive case. Prefer a negative decision to another month of marginal calculations.

## Deliverables — compact and reproducible

Create **only** new isolated outputs under `research/full_constraints/`:

1. `FLAVOR_CASCADE_NOVELTY_PILOT_REPORT.md`: ~4–6 pages (not a generic proposal). Exact source hashes, numerical comparisons, novelty matrix, status of physical gates, two strongest referee objections, one defensible one-sentence possible headline if one exists, and final GO/NO-GO.
2. `flavor_cascade/NOVELTY_WITNESS_MATRIX.json`: machine-readable source-ID + scenario + observables + exact paired differences + physical-status + novelty tags + null semantics.
3. `flavor_cascade/LITERATURE_COMPARISON.md`: dated queries, exact primary-paper locators and model/perturbative-scope differences, backward/forward coverage and limitations.
4. A small **read-only-source** Python adapter and focused regression tests **only if necessary** to reconstruct saved quantities; never refit, optimize, alter cards, or manufacture numerical points. Produce at most **one** useful figure, only when it objectively tests the discriminating hypothesis and cannot mislead readers into an allowed parameter-space map. The report/table alone are fine.

Validation: real source-file existence/size, SHA256; row count / exact ID joins / same-scalar hashes, no double-counted 13/14 TeV production; BR normalization and source-width checks where meaningful; explicit missing/null assertions; independently checked arithmetic for several paired witnesses; numerical test command and observed output; `git diff --check`; all changed paths and branch HEAD. Never say a test passed if it was not executed.

**Implementation boundaries:** leave Modules 0–14, D12/D14 saved records, current constraint contract, primary LFV/B/Higgs receipts, the original scan branch, and `main` untouched. No new points (including 'quick pilot' ones), no sampling/design/optimization, no MG5 integration, no Pythia/shower, no background/Delphes/Condor, no external large downloads, no SU(2) two-loop derivation. In particular do NOT attempt to solve mixed-F LFV by a new multi-week calculation; document exactly what is missing and stop. Reuse file source evidence, not cross-card interpolations. Keep large outputs out of Git.

Commit and push the evidence-backed small deliverables to **`research/zee-full-constraints` only**, with the actual commit SHA and test results. If blocked, still produce an honest bounded blocker report and verdict.

## End-of-task response (mandatory)

Return a compact summary with:

1. Final verdict and why (1–2 sentences);
2. Best *paired numerical* novelty candidate, or 'none', identifying exact original cards;
3. What 2017/2021 already did and what is truly distinct, if anything;
4. Whether any claimed physically allowed signature or collider reach was established (expected: **NO**);
5. Source/validation status, changed paths, executed tests and pushed commit;
6. The **single** smallest next decision, *without automatically proposing another broad calculation or scan*.
