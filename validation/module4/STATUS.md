# Module 4: PARTIAL

Native vertices and mathematical kernels are checked. New two-loop coefficients remain source-specific diagnostics: a signed Davidson/Ilisie conflict is unresolved. They are excluded from coherent rates. No experimental allowance or exclusion is inferred.

| Gate | Status | Scope |
|---|---|---|
| A | PASS | Native vertices and signed component/contact normalization checks |
| B | PARTIAL | All nine charged-fermion photon candidates, three scalars/channels; analytic kernels and complex chirality checks pass; coherent inclusion forbidden |
| C | PARTIAL | CHK BI+Goldstone photon kernel and native WW/Goldstone sum rules; no independent Rxi diagram cancellation; coherent inclusion forbidden |
| D | PARTIAL | Native diagonal/off-diagonal trilinears, polynomial derivative, scalar F2, transverse effective tensor checked; general LFV matching not closed |
| E | PARTIAL | CHK Zgamma Eqs12,17,19, set C; Ilisie mixed charged-current topologies inventoried, no amplitudes added |
| coherent_combination | PARTIAL | Frozen Module3 scalar one-loop only |

Tests: 155; failures 1; errors 0; skipped 0. Full regression: True.

The unchanged inherited Module3 branch guard requires feature/zee-lfv-module3 and fails on the mandatory Module4 branch. Its failure is explicitly counted, not skipped or patched; the Module4 replacement checks the correct branch, hashes and ancestry.

Native status: VERTEX_COMPONENTS_PASS; maximum absolute coefficient residual: 4.636291350834654e-13.

Source equations, sign conflicts and remaining topologies: [CONVENTIONS.md](../../module4/CONVENTIONS.md). Numerical residuals: [results.json](results.json). Hashes: [source_manifest.json](source_manifest.json).

Reproduce: `bash scripts/run_module4_validation.sh --all-tests`. Logs/raw dumps/PDFs remain in ignored `validation/module4/local/`.

Modules 0–3, including their open NuFIT, global-vacuum, RG and phenomenology limitations, are unchanged. Three-body interference and mu-e conversion are outside this module.
