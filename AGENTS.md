# Zee D1 — first multi-point coherent inverse-family grid (illustrative, NOT an allowed scan)

## Identity, cost, and immutable foundations
Work only on `feature/zee-scan-d1-family-grid` in `aalida0/zee`, forked from verified D0 `bb3834c5b3679dbfd9cb4cf4a530eecb460fc32e`. On the user's Ubuntu computer create this task's separate workspace **inside `~/zee/`**, e.g. `~/zee/workspaces/zee-scan-d1`. If `~/zee` is already a git checkout, do NOT alter its tracked files; keep nested workspaces ignored using parent `.git/info/exclude` or safe worktrees. Do not touch another local checkout, default branch, or existing validation branches.

Purpose: genuine **multi-point** coherent exploratory calculations, not an experimentally allowed benchmark population or a 95% exclusion. D0 already passed one full NO point with scalar inputs SHA-bound to neutrino inverse family, Module3 one-loop LFV subset and Module5 2026 linear conditional flavor. We have **not** obtained a complete LFV rate, global scalar vacuum proof, authentic NuFIT 6.1 joint likelihood, physical B->Xs gamma filter, RG closure or collider likelihood.

Frozen READ-ONLY: `models/SARAH/ZeeTypeII/`, Modules 0–5, existing Module6 D0 `coherent_pilot.py`, all prior tests/audits/provenance; pinned external HyperIso; no patches to their code. Only edit `module6/d1_family_grid.py`, `tests/test_module6_d1_family_grid.py`, new D1 runner/tests/report, `validation/module6/d1_*.json`, and this task's `AGENTS.md` if necessary.

Read first only: `module6/d1_family_grid.py`, `tests/test_module6_d1_family_grid.py` (both **unexecuted** scaffolding), `module6/coherent_pilot.py`, `module6/COHERENT_PILOT_AUDIT.md`, `module3/example.json`, `module2/interface.py`, `module3/interface.py`, `validation/module6/pilot.json`. More only to fix concrete blockers. No new NLO/BMU/HyperIso re-evaluation or broad literature search.

## Scientific design and falsifiable claims
The generator constructs a six-point, completely source-bound small grid using D0's existing complete `module3/example.json` with the SAME target Majorana mass matrix and original NO ordering:
- Two **illustrative scalar spectra**: original charged H1/H2=300/700 GeV, gamma=1.089; alternative charged H1/H2=450/850 GeV, gamma=0.95; all other scalar inputs retained. This variation can **FAIL** BFB/unitarity/EWPO/vacuum; never preapprove it.
- Three complex **homogeneous inverse-Yukawa family** multipliers `1, 10, 10i` for all four complex homogeneous coefficients. The inverse neutrino equation should remain solved if the implemented null-space family is correct; never assume this without full real evaluation. This is NOT random sampling nor a physics prior on Yukawa magnitudes.
- Each point MUST have a unique benchmark ID, a recomputed canonical SHA256 of its changed *full Module1* input, the same hashed scalar record bound through Module2/3, and the original target neutrino matrix. Flavor masses/mixing/tanbeta derive **only** from that scalar record.
- At **fixed scalar spectrum**, Module5 B->Xs gamma conditional matching should be invariant under varying homogeneous lepton-family coefficients, while Module3 LFV and Higgs-lepton partial widths can vary. At **changed spectrum**, both flavor and lepton sectors must be recomputed with the new scalar and neutrino inverse reconstruction. These are hypotheses to test numerically, not statements that either population is viable.
- The generator does not evaluate any constraints. Audit/code must keep `constraints_complete=false`, `global_zee_acceptance=null`, `COMPLETE_LFV=false`, and every flavor experimental comparison `NOT_EVALUATED`. Do not produce PASS for full LFV/Wgamma, a 2026 physical B->Xs gamma BR, NuFIT likelihood or a 670-GeV per-state bound.

## D1.A — audit and execute the generator
1. Independently audit the prewritten generator/test for validated nested schema, mutation safety, 4-complex homogeneous coefficients, full scalar SHA, benchmark-ID equality, ordering preservation, no default physics inputs, and `NaN/Inf` rejection. Fix actual bugs. The selected six points are development probes, NOT a justified scan distribution.
2. Run:
```bash
python -m unittest discover -s tests -p 'test_module6_d1_family_grid.py' -v
mkdir -p validation/module6/local
python -m module6.d1_family_grid \
  --seed module3/example.json \
  --output-jsonl validation/module6/local/d1_inputs.jsonl \
  --manifest validation/module6/local/d1_manifest.json
```
Record generated JSONL bytes/hash, manifest hash, actual point IDs. Recheck per-row Module3/2 schema and bound scalar SHA independently. Inputs/long outputs stay ignored local.

## D1.B — real multiple coherent executions, bounded
1. Implement a **small** `module6/d1_run_grid.py` (CLI) and separate tests, or a comparably auditable runner; call actual frozen `module6.coherent_pilot.pilot` per record. Use identical, fixed, explicitly source-pinned `mt_MSbar(160)=163.96892236746697 GeV` and reference LHA bytes SHA `984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374`. Never guess mass evolution. Derive all physics inputs from each row; no mixed independent flavor benchmark.
2. Execute at least **four independent points covering both scalar spectra and two homogeneous-family choices**, ideally all six. Give each result individual `PASS_SCOPED` or `BLOCKED_ERROR` execution status, exact error/source hash; do not promote failed runs to PASS. If a point fails a *physics* scalar gate, preserve that gate's FAIL independently of numerical execution. A computational PASS only says code ran. Do not override UNKNOWN vacuum or neutrino likelihood.
3. Record signed C7/C8, 2026 LO-linear value, original target-vs-reconstructed neutrino matrix error, Module3 subset BRs for mu->e gamma and tau channels, one or more Higgs LFV widths, scalar reconstruction/BFB/unitarity/EWPO/vacuum statuses, matrix/Yukawa norm diagnostics, hashes and runtime. Complex numbers must be encoded losslessly as real/imag, and NaN/Inf must fail closed. Show same-spectrum invariant flavor residual and changes in LFV across homogeneous directions; show different-spectrum changes in both sectors, if real results support them.
4. Numerically cross-check 1 NO source point against the EXACT D0 evidence, e.g. `DeltaC7=-0.05955354444399845`, `DeltaC8=-0.06299918381959017`, 2026 conditional value `4.182878900268742` in units 1e-4, and source one-loop mu->e gamma subset BR `5.117059759419609e-19`. Do not compare LFV subset BR with experimental exclusion. Reused D0 evidence is a regression, but at least 3 other real points must be evaluated.
5. Add falsification tests: changed charged masses without recomputed scalar SHA must fail; swapped benchmark IDs fail; wrong mu=160 or incorrect top mass provenance must fail; homogeneous changes leave neutrino target unchanged; no unexpected 'allowed/excluded'/global acceptance; identical spectrum across lepton variants must not change B->Xs gamma within numerical tolerance; no data dependency/missing sectors silently promoted to PASS.
6. Performance: running 300-attempt numerical vacuum sampling separately at every identical spectrum is wasteful. You may implement local **content-addressed memoization** only if keyed by the complete SHA-bound scalar+EW+search+code provenance and verified against actual fresh evaluation for at least one representative. Otherwise execute directly. Do NOT simply stub or skip vacuum and mark certified. Limit D1 to 6 probes; avoid premature general optimization.

## D1.C — publication-relevant, carefully scoped conclusion
Write `module6/D1_FAMILY_SCAN_AUDIT.md` with actual input grid, executed point counts, scalar statuses, NO neutrino residuals, Yukawa/LFV variation and fixed-spectrum flavor invariance, variation of flavor across spectra, provenance, runtime cost, and where constraints remain UNKNOWN. If no LFV variation is observed, report it rather than fabricating correlations. No claim of experimental viability or flavor/collider discovery prospects.

Write compact `validation/module6/d1_family_scan.json` with full SHA hashes, execution status per point, real numeric comparisons and regression/test counts. Keep giant point outputs and logs local; optional small CSV for plotting. State **next actionable paper path**: build a reproducible physically motivated scalar sampler and NO/IO inverse-family solution populations; then prioritized missing experimental constraints / collider production+decay observables. Do not implement large statistical scan here. No paper novelty claim until comparing with 2017 general Zee and 2021 cascade results on actual observables.

## Delivery requirements
Run scoped tests, D0 baseline regression if practical, real JSONL/grid runner, `git diff --check`. Stop with `D1_REAL_GRID_BLOCKED` if real execution cannot be completed; mock tests are not a physics pass. Commit ONLY new Module6 code/tests/evidence and AGENTS if corrected. `git push origin feature/zee-scan-d1-family-grid`; verify `git rev-parse HEAD` equals `git ls-remote origin refs/heads/feature/zee-scan-d1-family-grid`. Return exact SHA and URL, number of real points/tests, correlations or null results, and concrete blockers. `PUSH_BLOCKED` if push fails. Minimize tokens; detail belongs in files.
