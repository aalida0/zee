# D14F — Final physics-adapter integration BEFORE the one authorized large scan

**Current source branch:** `feature/zee-d14-conditional-cascade-scan`.
**Starting commit:** `bff3e5241f7454dd2c8fc2fe5bcff1067a9fa480`.
**User-approved goal:** Try to close the *specific remaining physics integrations* using public source code and finish the final workflow. **No new parameter proposals/scans**, no further exploratory benchmark production campaigns, and no HTCondor submission. The final big scan is separately user-authorized after a physics/software freeze.

## Outcome we actually want

Deliver practical source-validated improvements to Zee LFV, vacuum and Higgs coverage wherever feasible, without replacing a careful `UNKNOWN` with an unsupported `PASS`. Ensure final postprocessing scales without assuming all family rows fit in RAM. Prefer **validated, limited production-ready observable coverage** to a speculative attempt to declare the entire Zee model fully constrained.

The B→Xs gamma author was already contacted and has not responded. Do NOT restart a high-order flavor calculation or pretend EOS/SuperIso provides a 2026 uncertainty. Eq.(4) LO-NP remains conditional. Do NOT impose a single-state Type-II 670 GeV bound on each Zee mass.

**Read first:** `module14/FINAL_WORKFLOW_READINESS.md`,
`module14/EXTERNAL_CAPABILITY_MATRIX.md`,
`module14/PUBLIC_CODE_REUSE_AUDIT.md`,
`module14/public_spheno_evidence.json`,
`module14/FINAL_OUTPUT_SCHEMA.md`,
`module14/final_export.py`,
`module14/final_workflow.py`, and original `module14/FINAL_WORKFLOW_RUNBOOK.md`.
Check source and environment first; do not repeat completed general source searches.

## Working restrictions

- Leave Modules 0–13, original D14 20k/225 data, D14C/D14D actual production receipts and research branch untouched. Add adapters under `module14/physics_adapters/` or `module14/conditional_scan/`, scripts under `scripts/zee_d14_*`, tests under `tests/test_module14_*`. Modifications to final_export/runbook allowed with backward-compatibility tests.
- Never vendor compiled binaries, entire third-party source, temporary Fortran outputs or GPL source into this repository. Pin exact upstream commit/release, license, generated-card/source hashes, container/compiler/runtime and tests. Use ignored `validation/module14/local/` or a separate research checkout for builds.
- All new physics tests use **existing original D12/D14 cards or published benchmark/analytic limiting cases**, not new random parameter proposals. A deterministic smoke test on a fixed existing point, such as 15591, is allowed. If an existing package needs a numerical evaluation of these preexisting points for comparison, it is permitted; do NOT turn it into a scan.
- If an external source is absent, do not download an unpinned latest binary; document it and use the existing pinned source checkout or explicitly acquire a version-pinned archive in an isolated research workspace. Preserve source and license provenance.
- Do not broaden scope into new two-loop symbolic calculations, multi-month precision backends, detector analyses, cosmology or a new LFV/vacuum package of our own. Bounded stop decisions below.

## Phase A — SPheno 4.0.5 + SARAH 4.15.4: fix the *actual* build blocker

This is the **first, highest-priority task**. A separate prior checkout
`research/zee-spheno-flavorkit-pilot` at saved commit
`81cd376294e223c7311fba134f643db5c02bbad0`
contains actual generated Zee Fortran, four D12 reference cards and
experimental 1-loop scalar dipole comparisons. Their evidence hashes and
`K2L=-conj(C_L), K2R=-conj(C_R)` mapping are in
`module14/public_spheno_evidence.json`.

1. Inspect the actual generator-produced build error: undeclared
   `ZRUNoMatrix`, `ZRUNoMatrixc` with full one-loop decays enabled.
   Determine whether this originates in SARAH `LoopDecays` code,
   absent neutrino rotation definitions, out-of-date generated
   `Model_Data` interfaces, declaration order, or a mismatched
   SARAH/SPheno configuration. Save a **minimal original failing
   compile command and compiler log**. No assumption that declaring
   dummy variables is a correct fix.
2. Compare generated source and underlying model `SPheno.m` /
   particles/parameters with the pinned original. Implement a minimal
   *model-correct* fix in an isolated research build (e.g. corrected
   generator/model configuration or consistently regenerated source),
   **not** a hack that sets mixing matrices to identity or suppresses
   physical modes. If a full one-loop model cannot compile without
   model redesign, document the precise deficiency and keep
   `LOOP_DECAYS_UNAVAILABLE`.
3. Once the full backend compiles, validate actual runtime on **the
   four existing D12 cards**: neutrino/charged-scalar mixings, masses,
   dipole chirality and phase conventions, gauge/Goldstone classes,
   `mu→eγ`, tau radiative decays, and 1-loop h125 channels. Check
   tree-level widths against frozen D4; no mixing/BR replacement
   without documented scheme and numerical benchmark tolerances.
   Log exact source hashes and per-observable completeness.
4. Inspect and if genuinely covered test `mu→3e`,
   `tau→3\ell`, and \(\mu\to e\) conversion operators. Their existence
   in generated `Lto3Lp` or `MuEconversion` source does NOT
   establish complete Zee operator coverage. Validate at least
   one nonzero reference and correct scalar/box/penguin interference;
   if unavailable return `UNVALIDATED`.
5. Produce a strict optional D14 `SPheno/ZeeFlavorKit` adapter
   to consume **only** validated observables and match exact original
   parameter cards, masses, flavor basis, complex matrices, source
   versions, theory order and units. Fail closed on unmatched
   fields, binary versions, or missing operators. No change to
   Module4's existing scoped predictions.

**Bounded stop:** After examining the existing generated code, one
targeted model-correct regeneration/build attempt plus a single
revised build attempt if the failure is unambiguously localized,
if the full build is still broken, document failure and proceed to
the next stage. Do not attempt an endless build-fix loop.

## Phase B — corrected 2026 general-2HDM two-loop LFV code (separate)

Public source: `general-2hdm-pheno` pinned GitLab SHA
`b5035cd58d2a7e4a91e9790d045df062b97adffe`, corresponding
2026 erratum. Source hashes and unchanged upstream example
controls in `module14/public_lfv_control.json`.

1. Identify **the exact subsets that are gauge-invariant and
   model-portable** from a 2HDM with one charged H to our Zee
   scalar/charged-singlet system. Map neutral Higgs-basis
   Yukawas, mixing phases and effective couplings to the frozen
   Zee model at fixed existing D12 cards; compare against Module4
   finite complex dipole coefficients in the doublet/decoupling
   limit. Check sign/chirality/Hamiltonian conventions.
2. For a subset containing no charged singlet and unaffected by
   the charged sector, adapt only if gauge invariance and
   double-counting with existing one-loop operators are established.
   Do NOT arbitrarily sum entire 2HDM LFV BR and an independent
   Zee BR: add amplitudes with compatible chiral normalization.
3. Preserve `two_loop_full_Zee=UNKNOWN` if even one material
   singlet-F/mixed charged/gauge class is omitted. Record operator-
   level coverage, which analytic limit and sample-source residual
   were checked. Do not install an operative exclusion for a
   partial total.

**Bounded stop:** One exact convention map and a finite fixed-card
comparison; if portable subset cannot be independently established,
return `REFERENCE_ONLY`, avoid modifying Module4.

## Phase C — full Zee vacuum backend compatibility

Sources already inspected: Vevacious++ at commit
`657cf31c2489892d1862cd7ba21511e6f2ba863f`,
HomotopyContinuation.jl at
`0cbf1e27d062d7eb01d962c3b948c39444c9a62c`.
The stock THDM model does NOT cover Zee charged singlet.

1. Make a *source-checked* Zee potential/derivative/export contract
   including all neutral, CP, and charged/singlet directions before
   attempting external minimization. Audit gauge fixing or a
   mathematically justified gauge-invariant orbit representation;
   preserve physical stationarity and multiplicities. Verify
   potential, gradients, Hessians, signed field conventions and EW
   stationary energy versus frozen Module1/D10 at **one existing
   D10 PASS and one D10 UNKNOWN** card.
2. Where a valid `MakeVevacious[Version->"++"]` model export
   can be produced with source-pinned SARAH and full scalar
   potential, validate its LHA mapping and polynomial source
   against independent Module1. If no complete mapping can be
   verified, stop at `ZEE_VEVACIOUS_ADAPTER_UNVALIDATED`.
3. If a corrected system can actually be passed to a source-pinned
   polynomial solver, perform only bounded fixed-card
   comparisons; require verified complete stationary-point
   coverage and certified energy ordering to call a global
   tree-vacuum PASS. A numerical search with **no deeper witness
   is still UNKNOWN**. An apparently deeper solution is not a
   physical FAIL until the existing independent high-precision
   stationary/witness check is satisfied.
4. Never import Vevacious's example THDM conclusions into Zee,
   or claim thermal/metastability results from tree tests.

**Bounded stop:** one complete potential/map audit and at most two
existing-point tests. Do not invent a theorem or demand a comprehensive
new minimization framework.

## Phase D — HiggsTools / h125 rates

1. Retain existing HiggsTools 1.1.3 API, experimental datasets
   and original D13 diagnostics. Map only *validated* Zee
   charged-loop inputs (`h125→γγ`, optionally `h125→Zγ` if
   truly supported) or validated SPheno one-loop predictions
   with exact units, phase, couplings, on-/off-shell definitions.
2. Compare independent source calculations for existing cards.
   Ensure decay matrix elements include BOTH charged mass eigenstates
   with correct mixed couplings; avoid treating a Type-II H+
   as an exact substitute. HiggsTools needs appropriately
   normalized widths/branching fractions/effective couplings and
   sufficiently complete channels, not merely an h→γγ amplitude.
3. Existing H2 13-TeV benchmark production is validated; H1/neutral
   rates remain **NOT_EVALUATED** if unavailable. Do NOT rerun MG5
   or substitute a process/energy ratio. An incomplete Higgs model
   should remain `DIAGNOSTIC_ONLY` even when one channel is improved.
4. Implement optional source-bound adapter if there is real,
   independently verified numerical input; otherwise output
   `HIGGS_REMAINING_UNKNOWN` with exact missing items.

## Phase E — scale-proof final exporter (code only)

Current `module14/final_export.py` gathers `dataset['rows']`
in memory, and `module14/conditional_scan/workflow.join` also
accumulates all rows. The collector is already disk-backed.

1. Implement **chunked/spooled/disk-backed** deterministic export,
   preserving the original `d14-final-family-1` JSONL/CSV
   schema and rank semantics (per matching production contract,
   energy/process/PDF/scale). Consider SQLite temporary indexed
   storage and streaming external sort to avoid O(N_families)
   Python list memory. Preserve exact original schemas and
   input/output validation before streaming; verify all hashes.
2. Test equality against the **existing saved 225-point/900 family
   fixture** and original export bytes where appropriate;
   for stress test use synthetic repeated records with new
   mock IDs **without constructing real new physics proposals**.
   Verify bounded maximum RSS under a fixed limit, duplicate
   detection, missing row, wrong source, reversed shard order,
   atomic output, and interrupted export/retry behavior.
3. If re-architecting `join` would risk changing physics,
   keep an explicit legacy path and add a proven streaming path
   with matching fixture outputs. Do not infer "memory safe"
   merely from disk-backed `collect`.
4. Update `FINAL_WORKFLOW_RUNBOOK.md` resource policy and
   `FINAL_OUTPUT_SCHEMA.md` with any schema/version changes.
   Keep output labels and physical `global_acceptance=null`.

## Deliverables, validation and clear completion statuses

New report: `module14/PHYSICS_ADAPTER_READINESS.md`, with separate:
- SPheno full-build status, compiler failure/fix source and
  actual validated LFV operator-by-operator coverage.
- Corrected general-2HDM transfer/decoupling/gauge analysis.
- Zee Vevacious/full-potential export capability, any
  stationary-point/witness checks and remaining vacuum UNKNOWN.
- HiggsTools channel coverage, provenance and omissions.
- Exporter memory scaling and deterministic replay test metrics.
- External tool versions/hashes/licenses; tests, generated-artifact
  provenance and computational cost.
- Explicit **still-missing physics**: particularly 2026
  B→Xsγ NP uncertainty, *full* Zee two-loop LFV if not
  established, and unknown global vacua.

Update `module14/EXTERNAL_CAPABILITY_MATRIX.md`,
`FINAL_WORKFLOW_READINESS.md`, and
`FINAL_WORKFLOW_RUNBOOK.md` only with executed evidence,
not plans. Preserve historical reports/receipts.
Deliver exact stage statuses (no fictional one-line total PASS):
`SPHENO_FULL_BUILD_VALIDATED` or `SPHENO_BUILD_BLOCKED`;
`LFV_FULL_ZEE_VALIDATED` or `LFV_SCOPED_ONLY`;
`VACUUM_FULL_ZEE_VALIDATED` or `VACUUM_SCOPED_UNKNOWN`;
`HIGGS_COVERAGE_VALIDATED` or `HIGGS_PARTIAL`;
`EXPORT_STREAMING_VALIDATED` or `EXPORT_MEMORY_BLOCKED`.

The final umbrella status remains
`WORKFLOW_CODE_READY_PHYSICS_CONDITIONAL` until all
independent physics calculations really support stronger claims.
Scientific failures must **not** cause a runaway code-generation
project or another parameter scan.

Run all existing D14 focused tests plus new adapter unit tests,
a frozen-data end-to-end replay and `git diff --check`.
No new proposals, HTCondor submissions, MG5 jobs, publication
sensitivity or final-run launch. Commit and push only validated
changes to this branch.
