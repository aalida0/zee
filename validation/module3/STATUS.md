# Module 3 validation status

Overall scientific status: **PARTIAL**. Numerical validation: **PASS**.
Real tests: 133; failures: 0; errors: 0; skipped: 0.
Scope: ALL_REPOSITORY_TESTS. Counts per source test module are in results.json.

| Gate | Status | Declared scope |
|---|---|---|
| provenance_and_mapping | PARTIAL | Frozen hashes, strict Module1/2 roundtrip, complex E3 conversion and source-derived vertices |
| neutral_tree | PASS | All five massive coherent h/H/A tree subsets with both contractions |
| scalar_one_loop | PASS | All h/H/A e/mu/tau and H1/H2 F,D terms; m_nu=0 and external-invariant expansion |
| exact_one_loop | PARTIAL | Finite-neutrino-mass and external-invariant corrections absent |
| interference_and_normalization | PASS | Signed complex rephasing, chirality, conjugation, photon trace, scalar g-2, helicity sums |
| higgs_LFV_partial_widths | PASS | h,H,A; all flavor pairs; exact fermion masses and both charge orientations |
| universality | PARTIAL | Leading F-only with muon GF subtraction |
| interfaces_and_evidence | PASS | Strict JSON/JSONL, six full current Module2 family witnesses; tampering/negative cases |
| full_LFV | PARTIAL | No full prediction, experimental comparison or exclusion |

PASS validates the stated calculation; it is not full phenomenological acceptance.
Three-body output is TREE_SUBSET_ONLY. Radiative output is
SCALAR_ONE_LOOP_APPROXIMATION. Universality is SUBSET_DIAGNOSTIC.
COMPLETE_LFV=false; global acceptance=null; no LFV experimental limit is applied.

Frozen Module 2 physics tag: `zee-neutrino-module2-physics-v1`, at
`571046e7dce3b99b60c4aaa6e6cdef2e66a494d4`. The annotated tag was pushed and independently
remote-verified during delivery. Its scope explicitly excludes authentic
official NuFIT 6.1 archive validation, which remains PENDING_EXTERNAL_DATA.

Raw SARAH real/complex vertex archives are absent from this snapshot. Available
frozen component/source identities and complex E3 fixtures are tested; a fresh
SARAH validation is not claimed. See module3/CONVENTIONS.md for derivations
and the signed legacy discrepancies. Frozen sources remain unchanged.

Reproduce: `bash scripts/run_module3_validation.sh --all-tests`.
One point: `python -m module3.interface --input module3/example.json --output /tmp/lfv.json`.
Batch: add `--jsonl` and supply one complete input per line.
Numerical residuals, all six NO/IO witness spectra, four complex family
coefficients and signed checks are in results.json; hashes are in
source_manifest.json. Detailed logs and downloaded primary PDFs are ignored
under validation/module3/local/. Branch/remote commit verification is reported
in the delivery message; reports identify validated content by SHA256.
