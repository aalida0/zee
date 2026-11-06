# Zee Type-II: publication-grade full-constraint completion program

**Purpose:** The user explicitly superseded the previous conditional-physics freeze. The goal is now to validate and operationalize **complete, scientifically defensible LFV, B→Xsγ, and Higgs exclusions** before any final large parameter-space scan.

**Working branch:** `research/zee-full-constraints` from frozen `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.
**Protected base:** `feature/zee-d14-conditional-cascade-scan` remains untouched. Modules 0–13 and all production/scan receipts remain immutable unless a scientifically justified change passes independent tests and is separately reviewed.
**No scan authorization:** No exploratory mass grid, no new generated proposals, no HTCondor jobs or broader MG5 production. Testing on a SMALL FIXED SET OF EXISTING 2017/2021/published limiting cases and original D12/D14 cards is allowed and necessary to test physics. No silent auto-promotion of an external tool into a hard exclusion.

## Defining 'complete' responsibly

'Complete' means **all materially relevant amplitudes/channels for each claimed experimental exclusion at a specified perturbative order, correctly interfering and with justified uncertainty treatment**. It does NOT mean all orders in perturbation theory, all conceivable future searches, or that an unvalidated numerical generator makes the prediction correct.

An individual hard failure can exclude a point once its observable is validated, but a globally allowed point requires ALL stated mandatory physics/experimental constraints to have valid coverage. With any mandatory gate UNKNOWN, `global_acceptance=null`.

The 2026 Misiak et al. linear Eq.(4) is not a full validated Zee nonlinear rate. The 2HDM-II single charged-Higgs mass lower bound 670 GeV is NOT independently a cut on either Zee charged eigenstate. Neither a shifted legacy rate intercept nor EOS/SuperIso disagreements are justified theory uncertainties.

Do not assume the general-2HDM corrected two-loop LFV code contains the charged singlet Fzee or both H1/H2 mixed gauge/potential terms. Do not treat stock SPheno full-loop predictions as usable: the saved full-loop build has mismatched eV neutrinos, 302/358-GeV light h and 10^6-GeV widths, including pathological WW loop channels; source forensics did NOT validate a repair. Prefer compatible analytic or bounded independent amplitude sources with proper basis and IR/Ward checks.

## Scientific targets and hard gates

### A. B→Xsγ (CRITICAL-PATH feasibility FIRST)

- Build a source-backed **complete NP Wilson-operator inventory** in the model's Type-II quark sector, with both H1,H2 doublet projections, explicit mass, tanβ, gamma, CKM, chiral structures and renormalization schemes. Test exact one-state 2HDM limits and doublet/singlet mixing endpoints.
- Reuse Modules 5/D9B matching, C4^(1), C7^(0,1), C8^(0,1) and check high-scale convention/complex phases; determine any other operator contributions relevant at the adopted order.
- Evaluate an *internally consistent* B→Xsγ branching-ratio prediction including the source-prescribed full quadratic interference and perturbative NP treatment, using **SuperIso 5.0**, **HEPfit**, **flavio/wilson** or EOS only when the actual source implementation supports the required Wilson basis and order. Pick one primary backend; use another as a cross-check. Do not combine the 2026 SM intercept with old code's nonlinear response without a derived conversion.
- Specify photon cut Eγ>1.6 GeV, CP/isospin average, RG/bottom-mass scheme, mb/mt and scales; separate experimental, input, perturbative, and nonperturbative uncertainty with a **cited** methodology. Test SM limit; one-state 2HDM Type II reference bound **for that backend and prescription**, multiple two-state points, 2026 linear small-NP derivative vs Eq.(4); varied scales and regimes where NP is not small.
- Before doing major coding, **read source and test whether any backend exposes a consistent, calibrated NP rate**. If none, issue a source-backed BLOCKED decision; don't produce a fabricated 95% CL.
- Deliver an operational exclusion adapter only if rate normalization, nonlinear dependence, scale and theory uncertainty all pass. Otherwise `physical_bsgamma=UNKNOWN`.

### B. LFV complete within stated leading accuracy

- Produce a topology/operator coverage ledger for `mu→eγ, tau→eγ, tau→muγ` (all 1-loop and relevant dominant 2-loop neutral/charged/bosonic classes); `mu→3e`, `tau→3l` (tree, penguins, boxes, interference); and `mu→e` conversion (dipole, leptonic/quark scalar/vector interactions and target nuclear inputs). Explicitly decide which additional Higgs LFV decays are handled by HiggsTools, not double-counted.
- Use source-pinned SARAH/SPheno/FlavorKit and corrected Altmannshofer et al. general-2HDM two-loop code; its previously independently validated **neutral fermion-photon subset already exists in Module4** and cannot be added again. Identify *each* additional genuinely missing Zee diagram with Fzee or two charged mixed scalars. Gauge-invariant groups, phase/chirality conventions, complex interference, tree-vs-dipole effects and branching-ratio normalization must be independently checked.
- Do not use pathological SPheno one-loop pole spectra. A tree/physical-scheme operator-only adapter is acceptable only if it is manifestly internally consistent. Validate on frozen D12 cards, analytic decoupling/symmetry limits and an independent implementation or published test.
- Update experimental limits and confidence levels with source/date; do not silently substitute prospective sensitivities for observed limits. Implement source-locked uncertainty handling and a per-channel PASS/FAIL/UNKNOWN decision only for complete validated rates. `lfv_complete=true` only if the declared mandatory observable set is covered.
- If source lacks charged-singlet two-loop classes or their gauge completion, **explicitly BLOCKED rather than claim full radiative-LFV exclusion**.

### C. HiggsTools/HiggsBounds/HiggsSignals **complete applicable-channel coverage**

- Before running, make an exhaustive dataset-coverage matrix for the actual frozen HiggsTools version and actual theory spectra, recording applicable channels and energies; distinguish `NOT_APPLICABLE` (proved outside mass/search/process domain) from `NOT_EVALUATED` (missing required prediction). Never treat absent cross sections as zero or wrongly label 13.6/14 TeV rates as 13 TeV.
- Build internally consistent complete h125 predictions: mass, total width, all relevant partial widths/BR including LFV, SM-like production/normalized kappas, charged **H1 and H2** loop contributions to h→γγ and Zγ, and other loop effects required by target analyses. Validate Ward/gauge identities, charge and mass-mixing and SM/2HDM limits; do not use SPheno's invalid pole masses/loop widths.
- Populate heavy neutral `H/A` production at required collision energies and their complete relevant widths (fermion, vector, Higgs-to-Higgs, charged W cascades, and loop-induced when relevant); charged `H1/H2` tb-associated rates and additional relevant production modes, full on-shell 2-body and consequential 3-body/off-shell channels when physically open/competitive. Source-lock LO/NLO accuracy and systematic variations for relevant production; no arbitrary K-factors.
- Reuse validated Module7 tree decay inventory and existing 16 H2 production receipts, but don't misinterpret 16 actual points as production coverage over the final scan. Any new production computation must be **only on existing fixed witness cards** for validation; broad sample production is a separately designed post-scan expensive enrichment step on same immutable manifest after explicit authorization.
- Feed HiggsTools 1.1.3 with actual matched h/H/A/H1/H2 predictions; verify HiggsBounds analyses loaded, processes and signal-rates, HiggsSignals effective-coupling/width conventions, dataset/provenance and pass/fail criteria at benchmark and SM/decoupling control. Make per-analysis coverage explicit.
- A full-model Higgs `PASS` requires every mandatory applicable search and measurement covered at published scope. If some remain missing, `HIGGS_PARTIAL`; do not promote a selected-channel result to a globally allowed point.

## Shared implementation / stop rules

1. **Begin with B-rate feasibility gate** and document a source-verified path or concrete impossibility. Don't spend a month first expanding three other backends if B remains impossible at desired accuracy.
2. For each area, make a standalone **operator/channel/accuracy/uncertainty matrix**, with citations/links, pinned code versions, exact frozen Zee card input mapping and missing terms.
3. Implement in isolated `research/full_constraints/` or `module14/physics_adapters/` adapters, only when their independent physics gates PASS. Unvalidated output is research evidence, not a D14 hard veto. Existing production/scans and Modules0–13 remain unchanged.
4. Add robust benchmark controls: two-state→one-state, gamma endpoints, phase reversals, zero-Fzee and complex-Yukawa limits, Ward/IR relations, SM baseline, width sums, energy+PDF+scale contract; test all required observables, not just status serialization.
5. Each physics adapter exports `PASS/FAIL/UNKNOWN/ERROR`, confidence prescription, theoretical accuracy, input/source hashes, explicit missing terms and a **strict validation assertion**. Return UNKNOWN if any validation evidence is absent.
6. Never add a made-up NP theory sigma, drop interfering diagrams, silently use 2HDM total rates as Zee, replace correct spectra with SPheno's invalid full-loop pole predictions or call a numerical method 'complete' without evidence.
7. Implement testing with **existing frozen D12/D14 cards and published limits**, not a new parameter scan. No Condor submission, no 20k/100k toy sample and no new model-space points. Synthetic unit-test fixtures are fine.
8. Stop and report `B_FULL_RATE_BLOCKED`, `LFV_FULL_COVERAGE_BLOCKED`, `HIGGS_FULL_COVERAGE_BLOCKED` if source/provenance does not support a responsible completion. At these gates, the user decides whether to narrow the paper's claimed constraint scope or obtain additional specialist/theory input. Do not turn a blocked physics task into more infrastructure.
9. Frozen conditional branch is read-only. After all three adapters are validated, **and only then**, propose a reviewed merge to the final-scanning branch with end-to-end evidence.
10. The final big scan is **NOT authorized** by this work.

## First phase deliverables

- `research/full_constraints/FEASIBILITY_GATE.md`: evidence-backed B→Xsγ full-NP rate path, or why it is blocked; realistic definition of perturbative completeness and uncertainty.
- `research/full_constraints/BSGAMMA_COVERAGE.md`
- `research/full_constraints/LFV_COVERAGE.md`
- `research/full_constraints/HIGGS_COVERAGE.md`
- `research/full_constraints/VALIDATION_MATRIX.json` with statuses only as actually established.
- Source-pinned minimal bounded tests and numerical controls as relevant, commits in this branch only.
- A final `CONSTRAINT_COMPLETION_READINESS.md` that counts operative vs diagnostic constraints and whether a fully constrained final scan is **actually** supported.

**First Codex task:** Read this file and the frozen project evidence, then complete the B→Xsγ feasibility gate with source-level inspection/one-state and two-state saved-card validation design, before heavy coding. Report precise blockers and select the primary backend only after verifying real capabilities. No overclaiming. Commit validated progress.
