# NEXT ACTION — Execute SusHi neutral production on EXISTING Zee cards; connect validated decays to HiggsTools

**Working branch:** `research/zee-full-constraints`. **User's immediate focus:** use public physics codes rather than implement ScannerS from scratch.
**Starting commit:** `f1cf65ce55de3f694b2ed5ad3a0093c121490a9a`.
**Protected frozen scan source:** `feature/zee-d14-conditional-cascade-scan` at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## Outcome (actual computation, NOT a new inventory)

Produce **at least one independently executed, source- and card-locked SusHi cross section** for `gg→H/A` or `bb→H/A` at **13 TeV on the existing D7 and/or F13 benchmark**, with its original physical Type-II quark couplings and documented PDF/order/scales, and independently verify the Yukawa/CP convention. If unavailable or unsupported, give the exact compiler/dependency/model limitation with a reproducible command and log. Then determine if **anyHdecay/HDECAY can provide transferable partial widths** and explicitly add the extra Zee channels. Connect only validated predictions to the already working HiggsTools research adapter.

This task advances the previously built `HIGGS_COVERAGE.md` / 310 HB + 159 HS inventory. Do NOT rerun broad package surveys, refactor the working D14 scan engine or try ScannerS's own parameter scanner. **Do not call output a full Higgs exclusion unless full applicable analysis coverage and uncertainties pass.**

Read before coding:
- `research/full_constraints/SCANNERS_HIGGS_REUSE.md`
- `research/full_constraints/HIGGS_COVERAGE.md`, `HIGGS_EXECUTION_REPORT.md`, `higgs/COVERAGE.json`
- `research/full_constraints/HIGGS_TASK.md`, `PLAN.md`, `PROGRESS_TO_FINAL_SCAN.md`
- `module13/higgstools.py`, `module14/external.py`, `module14/decays.py`, frozen original D12 inputs, model CP-even/CP-odd Type-II quark vertices and original D4 tree on-shell widths.

## Phase 1 — Pin and run ONE independent SusHi calculation

1. Select an actual public compatible SusHi release, **pin the full source archive/hash and exact version**; record compiler and dependent LHAPDF/LoopTools versions and source licenses. Do not use unpinned `master` binaries, assume runtime installed, vendor sources/binaries or use unvalidated precomputed lookup tables.
2. Identify SusHi model configuration supporting neutral CP-even `H` and CP-odd `A` with **quark Type-II neutral Yukawas**. Translate the native Zee `alpha, beta` and quark-sign conventions to SusHi's `h/H/A` input. Explicitly verify `g_Htt, g_Hbb, g_Att, g_Abb` versus independent native Zee vertices at one original D7 or F13 card. The Zee charged singlet does not change the tree neutral Type-II quark Yukawa couplings in this restricted model; it DOES create additional width modes and higher-order corrections. Preserve masses and CP assignments; never feed H1/H2 charged states to a neutral SusHi table.
3. **Execute a real original-card ggF rate at 13 TeV**, first at a single perturbative accuracy where both Yukawas, interference and a consistent PDF/alpha_s set are available (LO comparison if necessary; NLO/NNLO only with validated inputs and implementation). If compatible, obtain `bbH` at the same card/energy and a second existing D12 card. No new scalar proposals. Record stdout, actual SLHA/SusHi cards, input parameter and source digest, PDF member, QCD order, muR/muF, number of flavours, mb scheme, kinematic threshold, integration error and charge/CP convention. Avoid treating any non-SM NLO correction as universal.
4. Independently check the **LO amplitude/coupling scaling** (including top-bottom interference for ggF and scalar vs pseudoscalar form factors), and SM/2HDM coupling-limit controls using *analytical reference assignments* rather than generating random new Zee spectra. Compare with published SusHi reference points wherever possible. Nonzero agreement and error injection should be tested, not only JSON receipt matching.

**Stop gate:** If SusHi cannot compile or execute with available pinned dependencies after one source-correct and one targeted dependency fix, save exact blocker; do not synthesize a `σ` or spend unlimited time on installation.

## Phase 2 — Transferable neutral partial widths with anyHdecay/HDECAY (after Phase 1)

1. Examine actual source and pin version for a compatible **anyHdecay or HDECAY** implementation that accepts our CP-even/odd masses and neutral Type-II Yukawas. Calculate at one **original existing** benchmark only, with explicit convention/pole mass/alpha_s and scheme; record raw outputs, not values copied from previously committed data.
2. Mark precise transferable channels, e.g. neutral quark/lepton SM-type, gg/γγ and WW*/ZZ* with source-specific limitations. **Nonstandard Zee lepton LFV neutral Yukawas, H/A→H1/H2 W, exotic H/A→scalar scalar, and all effects of the extra charged mass eigenstate are NOT provided automatically**. Reuse original native tree 2-body D4/Module7 rates where appropriate, and cross-check model-correct neutral exotic widths against generated SARAH vertices or independent analytic formula on the exact card.
3. Assemble `Γ_total=Σ Γ_independent_disjoint_channels`. Verify branching fractions sum to one, conjugates/multiplicity, kinematic thresholds, off-shell modes and perturbative consistency; do not add a loop-induced or inclusive derived channel twice. **If essential channels are not known, the width is INCOMPLETE, and a physical Higgs exclusion cannot be asserted.**
4. If no compatible anyHdecay/HDECAY output is available, give an explicit **source-verified** missing-channel ledger rather than code a bespoke width calculator.

## Phase 3 — Consume only validated inputs in existing HiggsTools

1. Create an isolated `research/full_constraints/higgs/sushi_bridge.py` and optional `decays_bridge.py` with strict input/energy/source/scheme/width provenance, unit, PDF, flavour and scalar identity contracts. Do not modify frozen Module13 or Module14. Existing h125→γγ independently validated result should be reused (no rederivation).
2. Feed actual validated neutral rates and **complete** competing BRs to pinned HiggsTools 1.1.3 for **only the analyses whose process/energy/mass and source signal hypotheses match**. Return per-analysis `VALIDATED_SCOPED`, `MISSING_PREDICTION` or `NOT_APPLICABLE`, including experimental dataset commits. No missing→0, h→Zγ made-up ratio, or shifted production energy.
3. For potential observed-limit failures, review line shape/NWA, Γ/M, QCD order/uncertainties and signal-model acceptance before declaring `VALIDATED_SCOPED_FAIL`. An **isolated central LO observed ratio** remains DIAGNOSTIC_ONLY. A global Higgs PASS requires all mandatory applicable channels and HiggsSignals qualification, not one passing limit.
4. Keep B `B_FULL_RATE_BLOCKED` and LFV `LFV_FULL_COVERAGE_BLOCKED` unchanged. The separate independent HEPfit B rate task `HEPFIT_RATE_EXECUTION_TASK.md` remains queued, not canceled. No work on that task in this branch milestone.

## Validation and deliverables

- New report `research/full_constraints/HIGGS_SUSHI_EXECUTION.md` recording **actual** SusHi execution (or exact failure), source/version/sha/environment, original D7/F13 card data and cross sections, independent LO/reference checks, and any anyHdecay matching/competing-width evidence.
- `research/full_constraints/higgs/SUSHI_EVIDENCE.json` (computed rates only if executed), code/adapters in `higgs/` with unit and invalid-input falsification tests, source manifests and logs; no unqualified hard veto.
- Update `HIGGS_COVERAGE.md`, `VALIDATION_MATRIX.json`, `CONSTRAINT_COMPLETION_READINESS.md`, `PROGRESS_TO_FINAL_SCAN.md` with **measured** changes, not the presence of code or reference links.
- Tests against original input hashes, LO coupling reference, energy/PDF/CP scheme, matching widths; `git diff --check`. Preserve all historical and frozen outputs.
- No parameter-space proposal generation, no ScannerS `scan`, no large production grid, no Condor, no MG5 integration campaigns, no final scan launch. Commit/push only validated scoped research changes.

**A genuinely executed and validated neutral production rate is success for this task even if `HIGGS_FULL_COVERAGE_BLOCKED` remains the final scientific verdict.** Never claim to have 'completed Higgs constraints' from SusHi alone.
