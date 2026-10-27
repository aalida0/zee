# Zee Module 5 — Gate C3: bounded 2026 nonlinear-feasibility and exploratory scan triage

## Checkout / immutable baseline
Work ONLY on Git branch `feature/zee-bsgamma-2026-scan-triage` of `aalida0/zee`, forked directly from `5e6914fec7ecaad4f9a8295aa43b9efa2fcdfe2e`. **Local workspace must be under `~/zee/`**, per user preference, e.g. `~/zee/workspaces/zee-bsgamma-c3/`. CAUTION: `~/zee` may already be a Git checkout. If so, keep nested workspace ignored via only the parent checkout's `.git/info/exclude`, or use a safe worktree layout. Do NOT touch a sibling checkout or make an untracked nested Git repo appear in the parent repository. Avoid modifying any tracked parent file to set up the workspace.

Purpose: evaluate feasibility of a defensible **2026 B->Xs gamma** scan filter and offer a reproducible **exploratory (not excluding) linearized sensitivity** across Zee points. The 2026 Letter explicitly allows LO generic NP coefficients for small effects but omits quadratic NP shifts. C2 established native and independent NLO matching PASS with weighted ordinary-basis `(C4^1,C7^1,C8^1)=(0.001068928996949981,0.8549014676214426,0.4962537156147157)` and LO Eq4 NP shift `+0.4094799731787267e-4`. Naive NLO dipole-only increment `-0.07219408951914487e-4` is **NOT a corrected BR, 1sigma error or NLO observable**. C2 curvature/NP uncertainty/covariance remained unknown. Do not repeat BMU kernel integrals, native SARAH matching, full R1-R7, or patch-HyperIso experiments.

Read FIRST only:
- `module5/bsgamma_scan_triage.py`, `tests/test_module5_scan_triage.py`, `module5/example_scan_triage.json` (prewritten, UNEXECUTED candidates; review/debug).
- `module5/bsgamma_2026_linear_diagnostic.py`, `module5/BSGAMMA_2026_CONVENTION.md`.
- `module5/BSGAMMA_2026_ACCURACY.md` and `validation/module5/accuracy_2026.json`.
- `module5/FLAVOR_2026_SOURCES.md`; other files only for concrete blockers.

Frozen READ ONLY: `models/SARAH/ZeeTypeII/`, Modules 0–4, existing `module5/` physics and earlier reports, pinned external HyperIso v1.0.3. Do not retroactively rewrite old statuses. No full flavor or global Zee viability claim.

## Source pins and physical scope
- Misiak et al. `arXiv:2608.29863v1`, 30 Aug 2026: `https://arxiv.org/html/2608.29863v1` Section IV Eq.(4), `mu0=160 GeV`, `Egamma>1.6 GeV`. `1e4 BR=(3.54+/-0.14)-8.51 DeltaC7-2.16 DeltaC8` for small NP shifts, quadratic terms omitted. Experimental average `(3.49+/-0.19)e-4`. 670-GeV exclusion is for **one-state 2HDM-II** with higher-order matching, not either individual Zee state.
- Companion Czaja et al. `arXiv:2608.29864v1` `https://arxiv.org/html/2608.29864v1`, rate bilinear `sum C_i C_j G_ij`, nonperturbative corrections, normalization. **A complete externally validated high-scale ordinary-basis quadratic response in 160-GeV DeltaC7/DeltaC8 with the 2026 photon cut/normalization is NOT supplied as a ready-to-use numeric array in the C2 evidence.** Do not pretend that merely citing this bilinear automatically produces such a response.
- HyperIso native Type-II LO/NLO matching remains independent cross-check; archived HyperIso R3 SM BR is NOT the 2026 baseline. Use C1's explicitly source-proven signed operator basis. Cite sources by exact version; do not infer extra physical theory precision from numerical residuals.

## A. Small focused nonlinear feasibility/decision gate — no massive rate reconstruction
1. Search narrowly in **the two pinned 2026 publications, their actual data/supplementary sources if available, and immediately cited rate-response implementations** for an *executable or tabulated* matching-scale-to-2026-rate quadratic NP response. Document each candidate: actual URL/revision, exact operator basis, matching scale, photon cut, SM baseline, perturbative order, scheme, provided numerical tensors and license/access. Ask whether BOTH C7/C8 quadratic and C4 NLO impacts are consistently captured, with full SM–NP interference and correct low-scale evolution.
2. Make a clear source-grounded **GO/NO-GO** decision about building a complete validated 2026 nonlinear rate in another task. **If exact numeric input is absent or an implementation requires reproducing the full updated SM NNLO pipeline, STOP and declare `C3_QUADRATIC_SOURCE_NOT_READY` with precise missing ingredients.** Do not derive a guessed universal curvature, scale HyperIso R3 to 3.54e-4, digitize the plot to manufacture precision, or assume C4 insignificant. No new large multi-loop calculation.
3. If a suitable numerical source *does* exist, **do not implement the rate here**: specify minimal independent validation plan (zero-NP 2026 result, single-state 2026 one-Higgs reference, high-scale C7/C8 probes, sign reversals, gamma exchange, quadratic curvature, C4, scheme and cut). Gate C3 is source feasibility only.
4. Explicitly separate statistical questions: user-defined SM/exp error correlation, independent/mutually correlated model NP uncertainty, nuisance treatment, CL prescription, and quadratic validity domain. These are not established by quoting 0.14 and 0.19 separately.

## B. Run / validate prewritten EXPLORATORY scan diagnostic (no physical classifier)
1. Audit/fix `module5/bsgamma_scan_triage.py` and tests, which call the unchanged C1 `module5.bsgamma_2026_linear_diagnostic.run_contract` for each input point (six explicit fields). They report the signed `DeltaC7,DeltaC8`, *linearized central* Eq4 result and its difference from experiment for each point, plus **HYPOTHETICAL** normalized pulls under explicitly supplied `rho_SM_exp` and assumed independent Gaussian NP sigma. No default uncertainty assumptions, no allowed/excluded/95% CL, no covariance accepted as physical. Reject tampered, nonfinite, duplicate, wrong-scale and unknown input fields. Keep the formula source and C1 status in output; do not use C0 broken HyperIso patches or C2 NLO matching in Eq4.
2. Run:
```bash
python -m unittest discover -s tests -p 'test_module5_scan_triage.py' -v
python -m unittest discover -s tests -p 'test_module5_bsgamma_2026_linear.py' -v
mkdir -p validation/module5/local
python -m module5.bsgamma_scan_triage --input module5/example_scan_triage.json --output validation/module5/local/c3_scan_example.json
```
Ensure an actual independent arithmetic oracle checks the reported shift and normalized pulls, positive/negative rho, source SHA and no unwanted physical classification. Run a tiny 3–6 point **illustrative** scan varying charged masses and gamma; do not assume those points satisfy scalar stability, neutrino/LFV, flavor, collider constraints.
3. Interpret whether the reported C1 reference point's hypothetical normalized pull changes substantially between assumed NP uncertainty scenarios. A hypothetical pull around ~2 does **not** authorize a 95%-CL exclusion without a justified theory covariance and applicability domain.
4. The script is exploratory and deliberately includes uncertainties as *user-chosen hypothetical scenarios*. Mark `2026_LINEARIZED_FLAVOR_FILTER_READY=false` until physical theory/NP errors and domain are calibrated. Do not invent one-sigma NP error from C2's NLO dipole-only difference or arbitrarily set a universal |Delta BR/BR_SM| <10% threshold.

## C. Deliverable / completion
Create `module5/BSGAMMA_SCAN_TRIAGE.md` with source feasibility GO/NO-GO, exact missing rate ingredients, actual illustrative scan outputs and how sensitive pulls are to assumed nuisance/covariance, and the most efficient **next physical** task. Create compact `validation/module5/scan_triage.json` with actual test counts, SHA/source provenance, quantitative outputs, curvature and filter-readiness statuses. Append **one short paragraph** to `validation/module5/STATUS.md`. No inflated evidence: structural or formula arithmetic tests are not 2026 physical-rate validation. Avoid giant logs, datasets, PDFs, vendoring or endless source exploration.

Reports must distinguish:
- `C3_EXPLORATORY_SCAN_DIAGNOSTIC_PASS`: actual numerical checks of conditional formula/scenarios only;
- `C3_QUADRATIC_SOURCE_READY` vs `C3_QUADRATIC_SOURCE_NOT_READY`: genuine feasibility evidence;
- `2026_LINEARIZED_FLAVOR_FILTER_READY=false` absent defensible domain, model error and covariance;
- `FULL_ZEE_ALLOWED` = NOT_EVALUATED, and no mass cut.

Commit only `module5/bsgamma_scan_triage.py`, `tests/test_module5_scan_triage.py`, `module5/example_scan_triage.json`, new C3 audit/evidence and scoped AGENTS.md changes. Push branch `feature/zee-bsgamma-2026-scan-triage` and verify local `git rev-parse HEAD` equals `git ls-remote origin refs/heads/feature/zee-bsgamma-2026-scan-triage`. If push fails: `PUSH_BLOCKED`. Report SHA, test results, example diagnostic and specific next physics blocker concisely. Minimize Codex tokens: audit details belong in files.
