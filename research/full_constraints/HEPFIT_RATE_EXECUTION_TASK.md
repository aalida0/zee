# NEXT EXECUTION — Independent HEPfit B→Xsγ rate validation (not another audit)

**Working branch:** `research/zee-full-constraints`; begin after complete `e72c7b4` Higgs stage.
**Primary objective:** Produce an **independently executed, source-qualified physical B→Xsγ rate** using the HEPfit THDM calculation and demonstrate that an explicitly coherent two-state Zee matching maps to its NLO observable prescription. An unresolved source or theory-uncertainty mismatch must remain `B_FULL_RATE_BLOCKED`.

This is a narrow calculation task. Do NOT do a fresh broad code search, restart LO/NLO scalar matching, regenerate mass points or expand project scope. HEPfit may be a useful independent oracle, not an automatic source of physically calibrated Zee NP uncertainty. No experimental exclusion before source and numerical checks.

## Existing inputs / exact source pins

Read:
- `research/full_constraints/PROGRESS_TO_FINAL_SCAN.md`
- `research/full_constraints/FEASIBILITY_GATE.md`, `BSGAMMA_COVERAGE.md`, `SOURCE_MANIFEST.json`
- `research/full_constraints/REUSED_RATE_RESPONSE.json`
- `module5/BSGAMMA_2026_ACCURACY.md`, `module5/D9B_SUPERISO_REPAIR_AUDIT.md`
- `scripts/zee_module5_bmu_nlo.py`
- `module14/conditional_scan/flavor.py`
- frozen D12 card source hashes and archived two-state rate receipts

**Pinned HEPfit source**:
`https://github.com/silvest/HEPfit/tree/322bd73a2dadd94ce94a6d71cb79d616e569120a`.
Already verified:
- `THDM/src/THDMMatching.cpp`: SHA256 `29a27053026acd083c70cd679542651b0af093b0f1864471fc438dd030f16d21`
- `Flavour/src/bsgamma.cpp`: SHA256 `4bd90900c218ce05703e3176670f752b23a03b7971c20fbba2a662638e1f48e8`
- `FlavourWilsonCoefficient/src/FlavourWilsonCoefficientMatching.cpp`: SHA256 `f063c7df7fef1a6abeffb25512f698ca9f6e1a3dede700f2b8fdaacb0bd174af`

Prior audit shows THDMMatching has eight **order-separated** coefficients and bsgamma consumes nonlinear NLO pieces, while FlavourWilsonCoefficientMatching generic DC7g input does not expose the full coherent C4/C7/C8 basis. Therefore **do not try to pass Module5 high-scale NLO coefficients through stock generic low-scale DC7-only API**.

Existing primary research prescription: SuperIso 5.0 D9B source-pinned patched module, NDR BMU ordinary C4^(1),C7^(0,1),C8^(0,1), μ0=160 GeV, photon cut 1.6 GeV. Prior D12 cards have scalar masses (298.7267, 532.9329) and (572.2316,873.2077) GeV; archived BR respectively 4.22625081294e−4 and 3.88665197906e−4, **diagnostic only**. HEPfit comparison must hold conventions/inputs fixed or transparently explain irreducible differences.

## Gate 1 — Actually compile and execute the independent HEPfit THDM rate

1. Use source at **exact pinned SHA**, with a source-locked build environment and compiler/dependency/CMake receipt. Keep downloaded source, build intermediates and binaries in ignored scratch. Respect third-party license; don't vendor full HEPfit.
2. Find the smallest **working upstream test/example or driver** invoking HEPfit THDMMatching and B→Xsγ at Eγ>1.6 GeV. Verify HEPfit's actual SM rate and one-charged-state THDM prediction for selected physical masses and Type-II Yukawa convention, with full printed SM parameters, CKM, scales, order, semileptonic normalization, matching/Wilson arrays and observables.
3. Output at least one ***independently generated*** physical numerical rate, not a transcription of previous D9B/EOS results or another JSON assertion. Record exact executable, CMake/build SHA, source and input files and stdout/parsed numbers.
4. Inspect order tags and the actual `alpha_s/(4π)` weighting, effective vs ordinary C7/8 scheme maps, C4^(1), WCs and normalization. Check that `HEPfit` THDM context enforces *one* charged doublet; do not inject a second charged eigenstate by simply appending two BRs.

**Bounded failure:** If pinned HEPfit cannot be compiled with available dependencies after one documented source-correct configuration and one focused environment fix, report `HEPFIT_RUNTIME_BLOCKED` including error transcript and exact missing dependency. Do not fake outputs. Then identify whether an independent published one-state oracle at same order can be implemented without rewriting HEPfit.

## Gate 2 — Coherent two-state Zee matching bridge

1. Derive order-separated high-scale **NP** WCs from the frozen native module:
   `ΔC_i^Zee=cos²γ ΔC_i^II(mH1)+sin²γ ΔC_i^II(mH2)` for the validated Type-II quark matching domain.
   Do not add the SM component twice. Preserve Hamiltonian sign, CKM, C4 NLO, GIM/effective-basis finite shifts and the native mu0/mt scheme.
2. Adapt HEPfit via an isolated source- and symbol-verified **custom matching subclass or controlled THDMMatching extension** that passes a single coherent order-tagged operator vector into HEPfit's rate engine. Avoid an unsafe generic DC7-only route; avoid copying full upstream code to the repo.
3. Validate **SM** (ΔC=0), exact one-state endpoints γ=0 and γ=π/2, exchanged masses + γ→γ+π/2, same-mass identity, threshold/scale behavior and both actual D12 scalar cards. Include independent C4/C7/C8 sign/variation probes and held-out algebraic cross terms. Keep sources and inputs pinned.
4. If HEPfit's THDM rate and D9B rate disagree, **show source-located decomposition**, not arbitrary intercept alignment. Compare matching, semileptonic normalization, μ_b, m_c, m_b, QED/HQE/resolved-photon and truncation choices. Do not treat backend spread as theory sigma.

## Gate 3 — Physical prediction and uncertainty (required for exclusion)

1. Adopt a clearly defined **internally consistent rate scheme** at a stated perturbative accuracy (NLO NP matching/evolution/rate plus its model-relevant residual terms). Explicitly identify which HEPfit terms correspond to the perturbative NP expansion, and whether its available theory error is SM-only, full-model or NP-dependent. Document the declared materiality domain in mH1,mH2, gamma,tanβ and input scheme. Exclude unsupported imaginary/primed or electroweak sectors if non-negligible.
2. Determine whether HEPfit offers **published/source-validated** uncertainty parameters, correlations and scale variation that cover the two-state NP domain. If not, report `UNCERTAINTY_CALIBRATION_BLOCKED`; no ad-hoc 4% shift, 2026 SM sigma, or D9B/EOS spread masquerading as error.
3. Reproduce one established one-charged-state Type-II limit under that *same scheme and statistical prescription* (not blindly the 2026 670 GeV bound). Then, and only then, attempt a two-state physical exclusion on existing fixed cards.
4. A central BR from a working two-state executable without these checks is `INDEPENDENT_RATE_EXECUTABLE` but NOT `B_FULL_RATE_VALIDATED`.

## Deliverables / stop

Under `research/full_constraints/bsgamma_hepfit/` provide:
- Source-pinned minimal driver/adapter or exact build and run scripts (not vendored HEPfit);
- real stdout and normalizations; `HEPFIT_EXECUTION.json` with SM, Type-II one-state, endpoint tests and D12 original two-state computations **only if actually executed**;
- test suite and falsifiers for operator-order, scale, source digest, duplicating SM, wrong energy cut, gamma endpoint, wrong C4, missing theoretical uncertainty;
- `HEPFIT_RATE_REPORT.md`: observed numerical reproduction/residuals, explicitly separated internal vs independent physical validation and uncertainty gates;
- updated `BSGAMMA_COVERAGE.md`, `VALIDATION_MATRIX.json`, `CONSTRAINT_COMPLETION_READINESS.md`, `PROGRESS_TO_FINAL_SCAN.md` only when measurements justify status changes.

**Pass labels must be exact:**
- `HEPFIT_RUNTIME_PASS` or `HEPFIT_RUNTIME_BLOCKED`;
- `INDEPENDENT_RATE_MATCHED` / `INDEPENDENT_RATE_MISMATCH` / `NOT_EVALUATED`;
- `B_FULL_RATE_VALIDATED` only with actual validated physical prescription and **justified** theory errors; otherwise `B_FULL_RATE_BLOCKED` with remaining source-level blocker.

**No other B→Xsγ code exploration**, no LFV/Higgs new work, no new scalar proposals, no scans, HTCondor or MG5 production, no experimental confidence claims based on partial evidence. The branch `feature/zee-d14-conditional-cascade-scan` and Modules0–13 remain untouched. Commit and push only audited research changes.
