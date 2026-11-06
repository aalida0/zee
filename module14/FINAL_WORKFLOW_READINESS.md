# Final workflow readiness — 2026-11-07

**Code gate: CODE_READY**

**Physics gate: PHYSICS_CONDITIONAL**

**Release status: WORKFLOW_CODE_READY_PHYSICS_CONDITIONAL**

**FINAL_PHYSICS_SCOPE_FROZEN_CONDITIONAL — SPHENO_FULL_LOOP_OPERATIVE=NO.**
See [FINAL_PHYSICS_FREEZE.md](FINAL_PHYSICS_FREEZE.md) for the bounded triage
and exact filter/claims matrix. The enormous h1 width is h1→W−W+; its
amplitude-level cause remains unresolved. Running Yukawa input replacement
explains the eV neutrino enhancement within 1.53% using the existing forward
formula; the scalar effective-SM overwrite is confirmed. No justified model
fix or native rerun was made. Fixed physics scope/warnings are now bound into
preflight; unsupported hard-veto overrides fail closed.

Current adapter evidence: [PHYSICS_ADAPTER_READINESS.md](PHYSICS_ADAPTER_READINESS.md).
`SPHENO_FULL_BUILD_VALIDATED` (build/runtime only), `LFV_SCOPED_ONLY`,
`VACUUM_SCOPED_UNKNOWN`, `HIGGS_PARTIAL`, `EXPORT_STREAMING_VALIDATED`.
No new operative exclusion or globally allowed point is claimed.

This freezes the implemented conditional workflow, not a globally validated
Zee model calculation. No final-scan size, seed, shard size or arm weights
have been selected. The template deliberately remains invalid until the
user supplies those decisions. No new physics proposals, Condor submissions, MG5 runs or vacuum searches
were performed. The subsequent bounded adapter work built the corrected
full-loop backend on four original D12 cards; see PHYSICS_ADAPTER_READINESS.md.

| Required code gate | Measured result |
|---|---|
| Strict config/schema and deliberate placeholders | PASS; invalid ranges, signs, source/template pins, counts, dependent stages and runtime combinations rejected |
| No-physics preflight | PASS in focused tests: runtime/import checks, source cleanliness/commit checks, bundle corruption, missing binaries/data, disk and atomic-link failures; actual AF preflight remains a final-site requirement |
| Immutable execution and packing | PASS on mock metadata over frozen coordinates; original manifest partition and generation receipt, pack hashes, source/bundle/config/settings and runtime pins enforced |
| Worker and failure handling | PASS with mocked kernels; input-construction ERROR preserved, timeouts/unsafe archives rejected, required absent stages and changed family hashes fail closed |
| Restart/cache | PASS; complete-pair resume revalidates collection, corrupt/stale cache rejected; bounded-shard atomic retry is supported, partial-row checkpoint continuation is not |
| End-to-end fixture replay | PASS; original 100-point input/output/receipt replay, saved repartition, mocked final worker -> collection -> Eq.(4) sidecar -> export; no generator/kernel invocation |
| Reproducible export | PASS; reversed shard arguments yield byte-identical JSONL/CSV/audit and SVG; missing production stays null; two-energy mock contracts and exact tb cascade product checked |
| Historical 225-point evidence | PASS; exact dataset SHA256, 900 family records, 16 saved 13 TeV rates, three saved 14 TeV rates and 76 production-family bindings checked |
| Focused suite | **76 tests, 0 failures, 5 optional historical-artifact skips**; `python3 scripts/zee_d14_workflow_tests.py`; includes forensic replay and forbidden-veto/preflight-scope tests |
| Scope and formatting | `git diff --check` and compile checks PASS; Modules0–13, historical datasets/reports/maps/receipts and independent flavor branch unchanged |

The full 225-point saved dataset hash is
`2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9`.
Its original remote raw manifest/shard/receipt triples are not present in this
checkout: **raw 225-shard recollection is NOT_EVALUATED**. No fake remote
collection was synthesized. The committed replay fixture contains the original
100-point pilot bytes and original local receipt, with source hashes checked;
explicitly labelled fixture slices are used only for tests. The five skipped
tests require optional retained raw native evidence. They are separate from
the passing full saved-dataset and committed-rate-map checks.

Reproducible evidence:

- `fixtures/hashes.json`: immutable fixture byte hashes and historical worker identity.
- `fixtures/saved_225_replay_report.json`: saved-data replay scope, counts and source hashes.
- `fixtures/saved_225_export_audit.json`: 900-row final export receipt and exact file hashes; large exported tables remain in scratch.
- `public_source_lock.json`, `public_probe_results.json`: actual source pins and all five read-only source probes.
- `public_lfv_control.json`: corrected upstream example, complex coefficients, rate identities and analytic flavor-diagonal nulls.
- `public_spheno_evidence.json`: source-qualified read-only inspection of existing four-D12-card research comparisons; no new native runs.

**PHYSICS_GAP:** full Zee two-loop LFV and additional FlavorKit observables
remain unvalidated; no 2HDM charged-Higgs result was substituted for two Zee
mixed states and Fzee. No complete gauge-reduced Zee vacuum potential adapter
has been validated for Vevacious++/HomotopyContinuation; numerical
non-discovery cannot certify global stability. The SPheno Zee full-loop build now compiles and runs on four saved cards,
but its observables remain unvalidated for integration. Existing HiggsTools h125 treatment stays approximate;
missing charged loops, neutral/charged production and channels remain
DIAGNOSTIC_ONLY/NOT_EVALUATED. See EXTERNAL_CAPABILITY_MATRIX.md for actual
source coverage, measured comparisons, failed build evidence and omissions.

The published Misiak 2026 Eq.(4) result is an approximate conditional LO-NP
diagnostic, separately labelled from legacy D9B. Physical B->Xs gamma stays
UNKNOWN, `np_theory_sigma=null`, and no Zee 95% CL exclusion is claimed.
Never impose the single-state Type-II 670 GeV bound on individual Zee mixed
states. D10 sufficient certificate misses stay UNKNOWN and may continue to
neutrino evaluation. LFV stays PARTIAL/DIAGNOSTIC_ONLY. All global acceptance
fields remain null. Decays cover the full original on-shell tree two-body
inventory; loop/off-shell corrections and uncertainties are not supplied.
Production enrichment requires exact same-family source artifacts and an
explicit process/charge/PDF/order/scale/energy contract; absent rates stay null.
No detector efficiency/background/sensitivity model is provided.

Remaining external requirements before the separately authorized final scan:

1. User-selected count, seed, shard size, sampling arms/weights and reviewed
   physics options in an external runtime config pinned to the clean frozen
   commit containing this readiness document.
2. Exact Python/package environment on AF; optional validated binary and
   HB/HS Git datasets explicitly provisioned at absolute pinned paths if
   enabled. The public research tools are optional and are not operative gates.
3. Successful actual-site preflight, writable/free-space/atomic-link checks,
   scheduler resource review and explicit conditional-physics acknowledgment.
4. Enough postprocessing scratch disk for SQLite stores and complete output.
   The final CLI now uses disk-backed join/export; measured peak RSS stays
   below 92 MiB for 6,000 synthetic family repetitions. Legacy join/plotting
   have separate memory requirements.
5. A separate user decision to execute the final large scan. This freeze and
   its commit/push do **not** supply that authorization.

Use FINAL_WORKFLOW_RUNBOOK.md for the manual protocol and
FINAL_OUTPUT_SCHEMA.md for export and production-enrichment contracts.
