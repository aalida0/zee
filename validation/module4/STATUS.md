# Module 4: PARTIAL

Fermion-photon matching is independently derived and included coherently with the frozen Module3 components. W matching remains blocked and W candidates are excluded. Overall rates remain INCLUDED_TOPOLOGIES_ONLY; no experimental allowance or exclusion is inferred.

| Gate | Status | Scope |
|---|---|---|
| A | PASS | Native vertices and signed component/contact normalization checks |
| B | PARTIAL | Physical fermion-photon matching derived with outgoing photon crossing and Wick/Dirac projection; three primary diagonal checks; all nine species coherently included; mass/Yukawa scheme nominal |
| C | PARTIAL | Exact CHK-Ilisie-Abe decomposition; off-shell P/pinch Ward identity checked; complete LFV B,C projections and Rxi cancellation unresolved; W excluded |
| D | PARTIAL | Native diagonal/off-diagonal trilinears, polynomial derivative, scalar F2, transverse effective tensor checked; general LFV matching not closed |
| E | PARTIAL | CHK Zgamma Eqs12,17,19, set C; Ilisie mixed charged-current topologies inventoried, no amplitudes added |
| coherent_combination | PARTIAL | Frozen Module3 scalar one-loop plus validated photon-fermion two-loop subset |

Current branch: 125 tests; failures 0; errors 0; skipped 0. Full regression: True.

Inherited Module3: 37 tests, 0 failures, 0 errors, 0 skips, in an ephemeral clone of the exact component tag on its original branch name. No branch guard is changed or waived. Current-branch compatibility is tested separately.

Native status: VERTEX_COMPONENTS_PASS; maximum absolute coefficient residual: 4.636291350834654e-13.

Source-to-equation derivation: [MATCHING_AUDIT.md](../../module4/MATCHING_AUDIT.md). Conventions and remaining topologies: [CONVENTIONS.md](../../module4/CONVENTIONS.md). Numerical residuals: [results.json](results.json). Hashes: [source_manifest.json](source_manifest.json).

Reproduce: `bash scripts/run_module4_validation.sh --all-tests`. Logs/raw dumps/PDFs remain in ignored `validation/module4/local/`.

Modules 0–3, including their open NuFIT, global-vacuum, RG and phenomenology limitations, are unchanged. Three-body interference and mu-e conversion are outside this module.
