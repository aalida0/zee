# D14 FINAL — Complete and freeze the workflow code BEFORE the one final large scan

**Branch:** `feature/zee-d14-conditional-cascade-scan`
**Baseline:** `26bdcf33db91c4f1f2ffc3868841d7cb947c3c96` (completed validated physics data), with earlier task definitions archived.
**User decision (2026-11-06):** No more exploratory, pilot, intermediate, 20k, 100k or benchmark production campaigns. **Finish the workflow code first; the user will execute ONE final large parameter-space scan only after freeze and manual approval.**

## Scope and definition of done

Deliver a robust, reproducible, configurable **end-to-end Zee conditional parameter-scan workflow** covering proposal generation, all *implemented* physics gates, cache/restart, Condor packing and deterministic collection, conditional B→Xsγ screening, optional source-bound production/HiggsTools input, per-family cascade rates, auditable classifications and analysis-ready outputs.

**Code completion is NOT the same as global physical validation.** Modern B→Xsγ NP theory uncertainty remains uncalibrated, LFV amplitudes are incomplete, HiggsTools channels are incomplete, many D10 sufficient vacuum checks yield UNKNOWN, and production theory uncertainties are not validated. Keep each limitation explicit. Do not apply the Type-II single-state 670 GeV mass bound separately to Zee eigenstates. Preserve `global_acceptance=null` unless all required physical gates actually become validated.

The user does NOT want an additional scan for testing. Test with mocked/unit examples and **replay existing immutable datasets** only; do not generate fresh proposals even for a 'small local pilot'. Do not submit Condor, rerun MG5 integrations, launch vacuum searches, rebuild flavor backends or start author outreach. Archive prior 100k/20k proposal plans but do not act on them.

## Read-only source-of-truth evidence

1. `module14/D14A_INTEGRATED_SCAN_AUDIT.md`, `module14/AF_RUNBOOK.md`, `module14/COLLECTION.md`, `module14/scan.py`, `module14/collect.py`, `module14/condor/{prepare.py,worker.sh,d14.sub}`, `module14/{lfv.py,decays.py,external.py}`.
2. `module14/CONDITIONAL_SCAN_READINESS.md`, `module14/conditional_scan/{workflow.py,flavor.py,AF_COMMANDS.md,CANDIDATE_FOLLOWUP.md,PRODUCTION_MAP_REPORT.md,production_map_13_14.json}`.
3. Complete already collected 20,000/225 AF input manifests, data and receipts (original 225 dataset SHA256: `2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9`). They were already verified. Use them **read-only**, including partial fixture copies checked by hashes. If the full dataset isn't available in a checkout, use committed tests/fixtures and mark integration replay unavailable; do NOT synthesize a fake remote collection.
4. Modules 0–13 are frozen physics APIs and should not be changed. Existing D14 evidence, archived integration receipts and separate flavor branch stay untouched.

## Phase 0 — Inventory the actual workflow and identify only code defects

Create `module14/WORKFLOW_GAP_AUDIT.md`, mapping each implemented stage from source, tests and serialized outputs:

| Stage | Required documented status |
| --- | --- |
| Config/generation | deterministic source, seed, physical parameter ranges, proposal-arm identity, no duplicate IDs |
| Theory | reconstruction, BFB, unitarity, EWPO, D10 sufficient vacuum certificate |
| Neutrino | NO/IO inverse reconstruction, per-family Yukawas, perturbativity, actual target labels and coverage |
| Flavor | 2026 ordinary LO `ΔC7/8` **conditional** diagnostic; legacy D9B independently labelled; LFV partial |
| Decays | D3 cascade, complete D4 **on-shell tree two-body** widths and BRs, per-family validation |
| Higgs | h125 approximate HiggsTools and charged/heavy-neutral missing production/width coverage |
| Production | strict optional **external source-bound** per-family 13/14 TeV cards; no absent-rate zero and no arbitrary energy rescaling |
| Infrastructure | source-bundled Condor execution, atomic data persistence, restart/retry, collection, deterministic post-processing, error/UNKNOWN propagation |
| Final dataset | complete point/family provenance, hard FAIL vs UNKNOWN vs diagnostic, per-arm cutflows, plots and benchmark ranking only with documented rates |

Prioritize **genuine defects** and missing end-to-end orchestration over new scientific calculation modules. Before new code, explain for every proposed change exactly which existing mechanism is insufficient.

## Phase 1 — Final configuration and source-locked execution

1. Create a **strict, machine-validated final config schema**, explicit scientific options and source version. Provide one *template* final-scan config with deliberate placeholders for requested total count, seed, shard size and selected sampling-arm weights; **do not choose the final requested statistics on behalf of the user and do not generate any manifests**. Validate all ranges, gamma/mass ordering, cascade-threshold margin, positive tanbeta, correct neutral scalar parameters, full Yukawa-family choices, arm weights, count/shard divisibility, and mutually dependent physics options. Reject invalid inputs with readable errors.
2. Separate generation, compute and postprocessing, optionally cheap and expensive stages within **the same original manifest**. An 'expensive follow-up' may reuse exact source point IDs/inputs only; it may NOT redraw a second scan or silently drop UNKNOWN points. Preserve deterministic RNG independent of shard distribution and worker restarts.
3. Implement a `preflight --config ... --backend ...` command checking *all intended* runtime dependencies (Python pinned versions, source git clean/frozen commit, packed bundle hashes, imported physics modules, required external binaries and hashes, HiggsTools data, output writable free space, atomic-link semantics, supported CPU/RAM/request settings and available source locked caches), without generating physics points. Support explicit disabled/partial stages; report NOT_EVALUATED rather than treating disabled backends as PASS.
4. Do not introduce new default NP uncertainty, a pseudo-global likelihood or full-model allowed flag. Make incomplete constraint coverage a **prominent explicit preflight report**. Provide an `--acknowledge-conditional-physics` mechanism or similarly deliberate confirmation before preparing the final batch if unresolved gates are part of the chosen workflow.

## Phase 2 — Worker, retry and collection hardening

1. Make staged evaluation and optional caches robust. Audit family ID/source/card hashing, serialization, source pinning, all expected outcomes (`PASS, FAIL, UNKNOWN, NOT_EVALUATED, ERROR, DIAGNOSTIC_ONLY` and scoped `PARTIAL`), exception handling, timeouts, deterministic branching and truncation of invalid/NaN input. Explicitly define whether a D10 certificate miss permits further neutrino evaluation (it may, with vacuum UNKNOWN retained).
2. Audit `--resume`: current worker appears able to reuse an **already complete** shard-output/receipt pair, not an interrupted partial shard. Implement a safe partial-shard checkpoint/restart only if justified and testable without modifying legacy receipt semantics; otherwise state this clearly and use **bounded short shards plus atomic retry** as the supported fault recovery. Never append to unverified output or accept stale cache entries.
3. Separate point-level scientific FAILs, computational ERRORs, missing optional backends and interrupted jobs. A computed incomplete shard must never pass as COMPLETE. Ensure retries and duplicate results are detected. Check file races and cache atomicity on AF filesystem.
4. Condor `prepare`, worker and collector must agree on exact source commit, bundle, manifest/config/shard checksums, runtime dependencies, backend versions, family count and settings. Avoid implicit mutable external path dependencies. Improve packaging/validation tests only where required; do not launch batch.
5. Assert collector invariants: same point ID/source/card/no duplicates/missing, expected family count and ordering, hash/checksum of inputs and outputs, correct stage coverage, reproducible cutflows, source and settings across shards, **fail closed** on source mismatch or a required backend being absent.

## Phase 3 — Integrate existing conditional physics outputs as post-processing

1. Reuse `module14/conditional_scan/flavor.py` / C1 implementation, source-locking Eq.(4) at `μ0=160 GeV`. If the original worker uses legacy D9B, keep this additional 2026 Eq.(4) output separately labelled and never collapse diagnostic and physical constraints.
2. Reuse D4 complete decay table verification and measured on-shell tree two-body `BR(H2→H1Z)`, per NO/IO family. Add family-specific `BR(H1→tb)` and exact product `σ(H2) × BR(H2→H1Z) × BR(H1→tb)` **only when same-point real externally supplied production has correct hashes, energy, process, charge convention, PDF/order/scale and positive finite σ**. Without it, return null (not a fabricated interpolation or zero). Support both 13 and 14 TeV as distinct data channels; no measured three-point ratio is a universal correction.
3. No need to run MG5 for every proposed scalar point: define a scalable **post-scan production enrichment contract** for saved promising IDs with associated provenance while keeping the single final proposal manifest immutable. The pre-scanned sources and 16-point map remain reference fixtures.
4. Export a stable, documented versioned JSONL/CSV schema: one record per scalar point and optionally per family; all statuses, actual results, omission flags, source hashes and proposal-arm labels. Provide deterministic plot/table tools with accurate axis labels and captions; plots must disclose diagnostic flavor and missing constraints. Don't claim experimental sensitivity without efficiency/background model.
5. Include a scoped benchmark selection that never promotes a diagnostic pull to a physical PASS. Record verified source data and traceable reasons for each ranking or null.

## Phase 4 — Verification **without another scan**

Use:
- Unit tests and **small synthetic fixture rows** built in memory (not new physics proposal generation).
- Replay of the *existing* 225-point collected dataset and existing 16 real production rates when available.
- Corruption injection: changed config/binary/archive checksum, altered family/point, duplicates, missing results, truncated files, invalid floating point, wrong energy, wrong PDF/scheme, stale cache, absent backend, unsupported physics combination, interrupted shard, malformed receipt and incompatible source/commit.
- Boundary tests: closed on-shell cascade; gamma 0 and ±pi/2; decay BR identity; no production; vacuum UNKNOWN; approximate B DISFAVORED but **not physical FAIL**.
- A deterministic end-to-end **fixture replay** through manifest validation, saved worker output, collector, conditional sidecar and final exporter. Explicitly do **not** execute new `generate` proposals or expensive physics kernels for test data; use the prior pilot only as a frozen reference fixture.
- `git diff --check` and all relevant focused suite tests. Keep tests fast and no external-download/Condor requirement.

**No new scan of 100, 500, 20k, 100k, or any other number of physics proposals.**

## Deliverables and freeze gate

Deliver within `module14/`, `module14/conditional_scan/`,
`module14/condor/` where necessary, `scripts/zee_d14_*`, focused
`tests/test_module14_*` and docs. No change to Modules0–13 and
no overwrite of historical validation files.

Required files:
- `module14/WORKFLOW_GAP_AUDIT.md`: precise source-level gaps, fixes, scientific limitations.
- `module14/FINAL_WORKFLOW_RUNBOOK.md`: single manual AF final-run protocol with preflight, config approval, immutable generation, submit, monitor, retry, collect, sidecar, production enrichment, export and audit; start with `--help` / placeholders for user-configured size/seed, not a fixed unrequested 100k run.
- `module14/FINAL_WORKFLOW_READINESS.md`: honest checklist with binary `CODE_READY/CODE_BLOCKED` and separate `PHYSICS_CONDITIONAL/PHYSICS_VALIDATED` (expected conditional), measured fixture test evidence and exact remaining external requirements.
- `module14/final_config_template.json` plus corresponding schema/validator and deterministic final output/export code.
- Versioned JSON schema or documented canonical column contract; tests of all failure modes.

**Stop condition:** If required functionality is impossible without new scientific calculations (e.g. full LFV or 2026 nonlinear B theory), make that a scoped `PHYSICS_GAP` and keep the code capable of preserving UNKNOWN. Do not embark on new two-loop work or recast missing physics as a coding bug.

Final reply must state `WORKFLOW_CODE_READY_PHYSICS_CONDITIONAL` only if the code gates and fixture replay PASS; otherwise `WORKFLOW_CODE_BLOCKED` with exact source/test blockers. Commit/push only audited changes to this branch. **Do not start the final large scan.** The user will separately authorize it after reading `FINAL_WORKFLOW_READINESS.md`.
