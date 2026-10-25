# Module 0 — single complete validation

Run `20261025T025501.309151Z`; committed source `8ead13a593c3963b4f298985df84889d511fd31e`.
One empty workspace; no prior or partial run contributes acceptance.

| Gate | Status |
|---|---|
| 1. Load / CheckModel | **PASS** |
| 2. Scalars | **PASS** |
| 3. Gauge / complex Yukawa vertices | **PASS** |
| 4. Complex Majorana loop | **PASS** |
| 5. SPheno / FlavorKit | **BLOCKED** |
| 6. Regression suites | **PASS** |

Mathematica 15.0.1; SARAH 4.15.4. 31 unit tests; 31 independent numerical checks.
Maximum complex Majorana residual **2.508e-15 eV** (absolute tolerance 5e-11 eV, relative 1e-8).

Residuals/counts: [report/native_residuals.json](report/native_residuals.json), [report/majorana_physical.json](report/majorana_physical.json). All CheckModel diagnostics: [report/checkmodel_diagnostics.json](report/checkmodel_diagnostics.json); disposition and physical derivation: [CONVENTIONS.md](CONVENTIONS.md). Commands, SHA256 provenance and local artifact manifest: [report/](report/). Essential benchmark values: [fixtures/](fixtures/).

Detailed evidence stays locally at `validation/module0/local/runs/20261025T025501.309151Z/`. Legacy detailed runs remain locally ignored.

Reproduce from this checkout with committed sources:

```sh
python3 scripts/zee_sarah_module0.py --publish
```

SPheno/FlavorKit was not developed, generated, compiled or run: model-specific `SPheno.m` is absent and no valid SPheno installation was identified. The same Zee Lagrangian and Majorana packaging are retained. These passes cover the stated identities, representative inputs and physical limits; they do not establish RG closure, a global vacuum, a 309-point archive or full phenomenological viability. The original `~/zee` repository is untouched.

Finalization: fixed scalar diagnostic indexing and a symbol-guard side effect, then repeated the **entire** suite from committed code. Model and coupling implementation hashes are unchanged. [CLEANUP.json](CLEANUP.json) verifies that 1,135 removed Git artifacts remain local. The 31 unit tests include three orchestration regressions; these are not substitutes for the independently executed native physics gates.
