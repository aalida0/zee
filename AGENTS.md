# Module 0 — SARAH Zee model validation only

Scope: `models/SARAH/ZeeTypeII/`, `scripts/zee_sarah_*`, and their direct `scripts/gate6_*`, `scripts/gateA1[b-f]_*`, `scripts/gateB[23]_*` dependencies; `tests/test_zee_sarah_source.py`, `tests/test_gate6_benchmark.py`.
Do not search other branches, commit histories, remote documents, or broad repository code unless a specific test proves the dependency necessary. Read individual files only when needed; avoid bulk dumping logs, source files, or full model matrices into context. Keep useful test results in files.

Objective: validate the *same* ZeeTypeII Majorana model, scalar potential, Type-II quark sector, and complex general charged-lepton Fzee/Ye2 sector, without silently replacing it by a 2HDM or a Dirac Zee variant.

Essential physics gates:
1. SARAH 4.15.4 loads; report **all** CheckModel diagnostics and resolve genuine problems without silently adding forbidden operators.
2. Independently compare CP-even, CP-odd, and charged Hessians; Goldstones, mass eigenvalues, phase/sign/normalizations, quartic and trilinear couplings.
3. Verify physical charged Z/W vertices and complex antisymmetric f, general complex lepton Yukawas, gauge-index/chiral/orientation conventions against independently computed analytic identities.
4. Critically test SARAH one-loop Majorana Zee neutrino-mass matrix **including complex phases** and independent finite-loop formula/limits. Explicit prior blocker: the E3 Majorana loop self-energy correspondence was NOT independently proven; passing static tests must not rebrand it as validated.
5. Generate SPheno outputs only if genuine model-specific support works. Confirm required `SPheno.m` and valid SPheno installation before attempting native compilation. Model validation does not require claiming SPheno/FlavorKit works without a real run.
6. Run full relevant static, Wolfram, numerical integration and independent benchmark regression suites. Preserve multiple unrelated representative parameter choices and physical edge cases.

Source constraints: keep original convention and model; no file rewrites solely to silence test assertions. Any analytic equivalence must be explicitly derived and numerically checked. A synthetic mocked test is not a physics validation.
Outputs: `validation/module0/` immutable machine-readable trace, per-gate source provenance/SHA, commands, residuals, and a short final `validation/module0/STATUS.md` recording PASS/PARTIAL/BLOCKED per gate. Record versions of Mathematica/SARAH/SPheno, exact native runs, residual tolerances, and benchmark input values. No "full model allowed" claim.
Commit changes on this branch only, in cohesive batches. Never merge this isolated snapshot branch wholesale into the full Zee repo: its first commit intentionally removed unrelated tree files. Cherry-pick **only subsequent validated model/test commits** into the main integration branch. Do not include downloads, Wolfram licenses, generated binaries, or sensitive files in commits.

Efficiency: one capability inventory, one dependency plan, one consolidated native runner, rerun failed gates after corrections; do not send incremental lengthy reports. If Wolfram/SARAH/native dependencies are unavailable, identify the exact blocker, execute all possible source/static tests, and label native physics validation BLOCKED rather than fabricating results.
