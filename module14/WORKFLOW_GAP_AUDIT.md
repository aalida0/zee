# Final workflow gap audit

Active task: WORKFLOW_COMPLETION_TASK.md. Historical campaigns are read-only.
No new proposals or physics jobs are needed to close the code gaps below.

| Stage | Existing mechanism and limitation | Code action |
|---|---|---|
| Config/generation | scan.generate uses index-seeded RNG, stable IDs and legacy/correlated arms; no final strict contract or source/template lock | Add a strict final config wrapper, leave legacy inputs reproducible; template has null user decisions |
| Theory | scalar_gates calls frozen reconstruction/BFB/unitarity/EWPO/D10 | Preserve APIs; D10 miss UNKNOWN permits family evaluation |
| Neutrino | NO/IO inverse families are index/source seeded, labelled NuFIT6.1 secondary coordinates | Preserve inputs and limits; check family ordering, hashes and stage bindings |
| Flavor | worker D9B is optional and separate from conditional_scan.flavor Eq.(4) at 160 GeV | Preserve both; never turn diagnostic disfavor into physical FAIL |
| LFV | coherent implemented Module4 subset plus optional Module3 tree subset | Public-source audit before further physics; PARTIAL remains diagnostic |
| Decays | D4 verifies complete on-shell tree two-body inventory per family | Reuse saved tables, verify BR identities including H1 tb |
| Higgs | external.higgstools reuses D13 approximate h125; incomplete channels | Retain diagnostics; tighten supplied production identity/documentation |
| Production | sidecar checks source point and artifact hashes, but accepts any documented scheme and one energy per family | Add explicit expected contract, distinct 13/14 channels and exact cascade-times-tb rate |
| Runtime | runtime_info records versions, no preflight/dependency enforcement | Add no-physics preflight with source, imports, binary/data hashes, resource and filesystem checks |
| Condor | archive/commit checked; config/settings/shard not tied to one pack receipt | Add final execution lock consumed by worker, collector and packer; preserve legacy packing |
| Restart/cache | complete output/receipt resume only, atomic hard-link publication, hash-keyed scalar and D9B caches | Retain bounded-shard atomic retry; reject stale settings, source and malformed cache/output |
| Collection | disk index checks duplicates and identities, but stage-family links/runtime not fully checked | Add fail-closed consistency validation with legacy receipt compatibility |
| Export | conditional join produces nested JSON; ranking omits H1 tb; row order follows triples | Add deterministic versioned JSONL/CSV, scoped ranking, cutflows, table/plot and omission fields |
| Verification | old tests draw proposals and rerun worker kernels | Replace proposal tests with immutable saved replay and mock-only worker tests |

Scientific gaps are separate: full Zee LFV, nonlinear 2026 B-rate/error,
vacuum completeness, h125 charged loops and complete Higgs production/widths,
production uncertainties and detector sensitivity remain unvalidated. Public
packages are optional research tools, not automatic PASS gates. See
EXTERNAL_CAPABILITY_MATRIX.md and FINAL_WORKFLOW_READINESS.md for measured
evidence and the final code gate.

Implemented closure: `final_config.py` / `final_config.schema.json`,
`final_workflow.py`, final-aware Condor prepare/job and worker receipts,
`final_export.py` / `final_plot.py`, public source probes and immutable replay
fixtures. Generation writes a manifest/shard receipt; packing requires it
and checks exact original partition bytes; final workers and collection bind
the full original manifest digest. Required backend absence, runtime changes,
inconsistent cutflows and computational errors fail closed. Completed-shard
resume uses collector validation; partial-shard restart is deliberately not
supported. Input-construction errors now retain scalar/seed identity and
ERROR status rather than escaping family exception handling.

All new final-contract behavior is tested with synthetic metadata over saved
coordinates and mocked kernels. Legacy compatibility is tested against the
original 100-point output and receipt, not regenerated proposals. Frozen
historical source hashes remain historical; the one test of the old workflow
hash reads that exact blob from baseline commit 26bdcf3 instead of requiring
today's orchestration to have the old bytes.

**PHYSICS_GAP:** no operative public Zee backend was added merely because
generic code exists. Source audits and the upstream LFV control are separate
from constraints. Full real-field vacuum export, additional FlavorKit
operators, general one-loop Zee decays, and a two-loop singlet-aware LFV map
remain model-validation tasks. They are not code freeze blockers for the
explicit conditional workflow. Postprocessing RAM scales with saved family
rows; bounded worker shards do not bound the in-memory join/export.
