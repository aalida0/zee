# Next execution: model-consistent Zee H/A widths and one genuinely applicable HiggsBounds search

**Branch:** `research/zee-full-constraints`. **Baseline:** `59e919f9bd606ad4c9cdd52e275aa2c4c159ceb4`.

**Why this task:** independent `B→Xsγ` HEPfit rate, nuisance propagation and historical confidence controls have reached `B_FULL_RATE_BLOCKED`. The precise remaining Wilson-dependent nonlocal covariance and materiality input are written in `bsgamma_hepfit/specialist_question.md`; stop standalone B computational work pending actual specialist input. LFV also remains blocked. The most actionable remaining track is to convert already executed SusHi and anyHdecay results into **physical model-matched Higgs search predictions** on *existing original D7/F13 cards*, if scientifically possible.

Read:
- `research/full_constraints/HIGGS_SUSHI_EXECUTION.md`
- `HIGGS_COVERAGE.md`, `HIGGS_EXECUTION_REPORT.md`
- `higgs/COVERAGE.json`, `higgs/SUSHI_EVIDENCE.json`, `higgs/SUSHI_SOURCE_MANIFEST.json`
- `higgs/diphoton.py`, `higgs/decays_bridge.py`, `higgs/sushi_bridge.py`
- `module13/higgstools.py`, `module14/decays.py`, `module14/external.py`
- `BSGAMMA_COVERAGE.md`, `bsgamma_hepfit/UNCERTAINTY_REPORT.md`
- `PROGRESS_TO_FINAL_SCAN.md`.
Keep frozen `module0`–`module13`, original D14 data, and B/LFV calculations **read-only**. No new model-space proposals or scans.

## Physics objective and strict meaning of success

On D7 and F13 existing complete scalar+Yukawa cards:
1. **Actually produce validated model-consistent H/A partial widths and, only if coverage is sufficient, normalized physical total widths/BRs**, with all relevant competing SM and exotic channels and documented perturbative scheme/uncertainty and mass/finite-width domain.
2. Combine with original **already validated** 13 TeV SusHi LO ggF/bbH cross sections and actual corresponding HiggsBounds analysis dataset. Test **at least one selected potentially applicable neutral Higgs search**. Return an observed limit ratio as `PHYSICAL_SCOPED_EVALUATED` ONLY if the full production, BR, acceptance/hypothesis, width treatment and theory uncertainties are qualified; otherwise `CENTRAL_DIAGNOSTIC_ONLY`. Do not choose an analysis just because it yields an exclusion.
3. Add full coverage to HiggsTools ONLY if actually validated. Missing channels `MISSING_PREDICTION` or materiality `UNKNOWN` are **not** zero. No `globally_allowed=PASS` or full-Higgs-pass while mandatory channels remain absent.

## Phase A — Complete useful neutral partial-width calculations, do not redo SusHi

A1. Reuse executed anyHdecay 1.1.0/HDECAY 6.60 and original D7 transfer. **Execute the corresponding F13 original saved input** (same source pins, no new scalar parameters) for transferable `H/A→tt,bb,cc,ss,gg,WW^{(*)},ZZ^{(*)},hh,hZ` where physically present. Carefully distinguish source-disabled IONSH/IONWZ switches from true physical absence. Verify native neutral Type-II quark coupling, mixing and masses and actual HDECAY source scheme; never adopt HDECAY's ordinary single-charged 2HDM total width or diagonal/lepton branching ratios as Zee total.

A2. Calculate **LO H and A→γγ on exactly D7/F13** in the same physical tree-input convention as the already validated `h125→γγ`:
- H: W, all charged fermions, both physical mixed charged scalar loops, exact trilinears and complex general-lepton Yukawas.
- A: relevant fermion CP-odd form factors; in the restricted CP-conserving scalar potential, diagonal A H_i+H_i− couplings vanish, and photon charge is diagonal; independently prove relevant charged scalar photon graphs vanish at this order.
- Independently test signs/form factors, CP, seagull/EM Ward, SM/2HDM limiting amplitudes, identical photons and partial width normalization. **Do not claim a complete Zγ contribution** from two diagonal 2HDM formulas when Zee G12 Z21 is nonzero.

A3. For existing cards only, add **all model-correct neutral Zee exotic on-shell widths** not supplied by HDECAY from the frozen scalar potential, SARAH vertex source and D4 kernels: H/A→H1/H2 W (both charges), scalar-scalar final states and tree general complex-lepton channels including LFV. Preserve correct identical particles, charge counting, transverse-polarization normalization, thresholds and physical scheme. Check independent analytic or SARAH vertices and total-width sum in the no-double-count convention.

A4. Explicitly inventory remaining channels required to call the result an *adequate physical total width*, e.g. mixed H/A→Zγ (one-loop), loop A→VV, H/A off-shell charged-W tails near thresholds, additional neutral/charged thresholds, first-generation quarks, QCD/EW higher orders, finite daughter widths, possible H/A→Higgs cascades. If omitting a channel, give a **numerical published-bound or independently demonstrated relative contribution/error** on those exact cards, not a claim of negligibility. If a required channel lacks a defensible bound, `TOTAL_WIDTH_INCOMPLETE`: print the sum of known disjoint widths and separately a missing-channel ledger, **do not normalize it to unity as full BRs**.

## Phase B — One real HiggsBounds analysis with physical input

B1. Use `higgs/COVERAGE.json` to identify source-specific, genuinely applicable observed 13-TeV neutral analyses at **mH,mA actually represented** by D7/F13, preferring simple inclusive rates when experimental signal hypothesis can be reproduced (e.g. a neutral fermion final state). Source-lock process/CP/width grid, production mode ggF/bbH, decay final state, mass interpolation/extrapolation restrictions and 95% CL use.

B2. Feed exact same-card SusHi cross sections, qualified total Γ and BR, into pinned HiggsTools 1.1.3 **only if the signal is complete**. Cross-check its observed/expected ratio directly against the corresponding analysis limit data at the exact mass.

B3. **Theory/signal validity**: current SusHi values are LO (with separately executed 7-point scale and 50-PDF error-member bands), not NLO; check whether LO accuracy supports the experimental limit hypothesis, how σ×BR uncertainty is propagated, whether finite width/interference affects the selected neutral channel, and whether process shape/acceptance transfer from the experimental model is valid. A 13-TeV total ggF rate is not automatically an experimental ttbar or tau-tau signal model; do not claim physical 95% CL without qualification.

B4. Outcomes:
- `HIGGS_SCOPED_OBSERVED_SEARCH_VALIDATED`: at least one fully specified observed analysis with all mandatory inputs/uncertainties and source-matched signal assumptions; **can give exclusion for that one selected analysis only**.
- `HIGGS_SCOPED_SEARCH_BLOCKED`: central diagnostic or incomplete width/acceptance and exact remaining missing inputs.
- Global full Higgs remains blocked until the declared *entire applicable* dataset (and h125 HiggsSignals) is qualified; no false globally-allowed point.

## Phase C — Tests, evidence and stop

1. Keep independent cross-check of the previously validated h125→γγ result (D7 width ratio 0.9317959556, F13 0.9750252264), and existing LO SusHi 13-TeV H/A numbers with old hashes. Do not re-run 52 production controls unnecessarily. Execute HDECAY **only on existing F13** and fixed-card loop/width validations. No new independent mass grids, broad MG production, or randomized parameter samples.
2. Strict tests of CP-even/odd, charged mixed loop normalization, one-state decoupling, all threshold and interference cases, source digest tampering, missing partial width handling, process/energy/mass/width grid mismatch, production uncertainty promotion and BR sum. Retain native logs. Test new results against exact source-model inputs.
3. Deliver:
   - `research/full_constraints/HIGGS_NEUTRAL_WIDTH_SEARCH_REPORT.md`
   - `higgs/NEUTRAL_WIDTH_EVIDENCE.json`, one or more fixed-card source-hashed execution receipts
   - `higgs/neutral_widths.py`, `higgs/test_neutral_widths.py` **only if backed by independently validated formulas**.
   - `higgs/OBSERVED_SEARCH_COVERAGE.json` with exact experimental analysis selection or proven blockers
   - update `HIGGS_COVERAGE.md`, `CONSTRAINT_COMPLETION_READINESS.md`, `VALIDATION_MATRIX.json`, `PROGRESS_TO_FINAL_SCAN.md` only when measured evidence changes actual milestone completion.
4. If genuinely material missing width or experimental acceptance cannot be calculated with existing sources after bounded validation, STOP and report **precise** missing theory inputs. No filler 'new physics adapter' merely to add more tests. Keep `physical_higgs=UNKNOWN`, `global_acceptance=null` and do not merge into frozen scan branch.
5. No parameter-space scan, no Condor, no broad MadGraph integration, no LFV/B matching code edits and **no full scan authorization**. Commit and push only source-qualified research changes to `research/zee-full-constraints`.

**This is intended to deliver a usable real neutral-Higgs experimental comparison or an exact research stopping barrier, not merely another package/source inventory.**
