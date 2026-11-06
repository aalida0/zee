# Final manual workflow runbook

**No final scan is authorized by this document.** The user must separately
approve final statistics, seed, shard size and sampling arms after reviewing
FINAL_WORKFLOW_READINESS.md. The commands below are a manual protocol with
placeholders, not an executable submitted campaign. Never run historical
pilot/production/vacuum scripts to test this workflow.

Start with help and the fast, offline no-scan verification:

```sh
python3 -m module14.final_workflow --help
python3 -m module14.final_export --help
python3 module14/condor/prepare.py --help
python3 scripts/zee_d14_workflow_tests.py
git diff --check
```

The committed replay fixture contains original pilot input/output/receipt
bytes, compressed with deterministic gzip. Hashes are checked before reading.
No proposal generation is used by the focused tests. Frozen D12 unit checks
are limited to the existing exact benchmark inputs. Optional raw-native
artifact checks skip when those historical artifacts are unavailable.
The saved 225-point dataset can be replayed read-only if present:

```sh
python3 scripts/zee_d14_replay_saved.py --dataset EXISTING_225_DATASET.json --output NEW_REPLAY_REPORT.json
```

It requires SHA256
`2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9`.
This rechecks saved records and the existing production map; it never
reconstructs a remote collection or reruns production.

## Configure, freeze, preflight (after separate authorization)

Work on `feature/zee-d14-conditional-cascade-scan`. Keep runtime configs,
reports and output directories **outside the source checkout** so the source
can remain clean. Start from `final_config_template.json`. Its null count,
seed, shard size, source commit and arm weight deliberately fail validation.
Its numeric ranges are an example copied from historical configuration,
not selected final sampling arms. The user must explicitly review them.
The fixed family rule is d14-neutrino-v1: both NO/IO, the requested family
count per ordering, source-ID/ordering/index derived seeds, original cone,
phase, scale and free-coefficient distributions in scan.neutrino_input.
Targets are NuFIT6.1 secondary best-fit coordinates, not a joint likelihood.

The final wrapper validates source-relative scalar template bytes, finite
ordered ranges, positive tanbeta, mass ordering, principal signed gamma,
neutral-mass bounds, the supported 20 GeV on-shell cascade margin, arm
identities/weights, count divisibility, family count/perturbativity, dependent
stage choices and exact runtime versions. Invalid configuration fails before
writing manifests. Full physics eligibility is determined by frozen gates.
Choose all desired implemented worker stages in this single immutable config.
The additional Eq.(4) sidecar remains separate from legacy D9B.

Freeze a clean commit after tests pass. Set source_commit to its full SHA.
Python 3.10.12 and all exact package pins in the config must be installed on
both login and execution hosts. Optional D9B binaries and HB/HS datasets must
be explicitly provisioned at the configured paths on execution hosts and
match the specified SHA256; nothing is downloaded or rebuilt automatically.
HB/HS pins are `digest(module13.higgstools.dataset(PATH)['files'])`; pin their
Git checkout and retain it because the existing D13 API reads Git metadata.
A D9B pin must also match the frozen validated binary evidence. Required
missing backends fail preflight; disabled ones report NOT_EVALUATED. External
research packages in EXTERNAL_CAPABILITY_MATRIX.md are not required backends.

```sh
python3 -m module14.final_workflow validate --config USER_APPROVED_CONFIG.json
python3 -m module14.final_workflow preflight --config USER_APPROVED_CONFIG.json --backend condor --output-dir EXISTING_WRITABLE_DATA_DIR --output NEW_PREFLIGHT.json
```

Preflight checks clean/frozen Git source, package versions/imports, configured
binary/data hashes, CPUs/RAM/disk, writable output and exclusive atomic hard
links. It runs no physics. `--bundle SOURCE_ARCHIVE.tar.gz` additionally
checks packed commit and source-file bytes. The preflight report records
source hashes, explicit disabled/conditional stages and prominent scientific
limitations; it is revalidated by packing, workers and final collection.
Run preflight on the actual AF environment. Host RAM checks do not certify
site quota or cgroup allocations; confirm the scheduler resource request.
The supported worker model is one CPU per bounded shard. Pin thread settings
consistently across jobs; runtime receipts must agree.

## Generate once, prepare, submit manually

Only after the user's separate final-scan authorization:

```sh
python3 -m module14.final_workflow generate --config USER_APPROVED_CONFIG.json --preflight-report NEW_PREFLIGHT.json --acknowledge-conditional-physics --output NEW_IMMUTABLE_MANIFEST_DIR
```

Preserve manifest/config checksums immediately. The RNG is based on the
original scalar index/seed and family identity, not shard number or worker
restart. Generation and compute are separate. Never redraw an expensive
follow-up or delete UNKNOWN points. D10 certificate misses explicitly permit
further neutrino evaluation while keeping vacuum UNKNOWN.

Prepare from the **same clean commit**, passing every existing shard exactly
once (use a locally constructed argument list, not a new proposal generator):

```sh
python3 module14/condor/prepare.py --commit FROZEN_COMMIT --config USER_APPROVED_CONFIG.json --manifest ORIGINAL_MANIFEST.jsonl --generation-receipt ORIGINAL_GENERATION_RECEIPT.json --preflight-report NEW_PREFLIGHT.json --acknowledge-conditional-physics --shard EXISTING_SHARD_0.jsonl --shard EXISTING_SHARD_1.jsonl --output NEW_BATCH_DIR
```

The repeated shard arguments above are placeholders; include the actual full
set. The packer enforces count, shard size, disjoint IDs, settings and source.
It writes an exact Git archive, SHA256, transfer-file pack manifest, pinned
preflight, submit file and job settings. Runtime resources/timeout are taken
from config. Workers recheck the bundle, source, every transfer checksum,
config and runtime before evaluation. Explicit external paths are never
trusted without their pins. Caches are optional and source-addressed; every
hit checks key/value hashes, and stale-source entries cannot be hits.

Review the complete batch directory and site paths. Submit manually from the
AF `/home` area, with data on the approved `/data` filesystem:

```sh
cd USER_REVIEWED_BATCH_DIR
condor_submit d14.sub
condor_q
```

These commands are documentation only; Codex did not submit anything.
Monitor logs, holds, exit status, resource use and receipts. Timeouts are
computational interruptions, not physical FAILs. Treat nonzero jobs or
missing/incomplete receipt pairs as incomplete.

## Retry, collect, enrich and export

Recovery supports **completed-shard resume and whole-shard atomic retry**,
not partial-row checkpoint continuation. Choose bounded short shards when
the user sets shard_size. Publication uses exclusive same-directory hard
links. A valid complete pair is rechecked through collector invariants before
resume. A lone output, malformed receipt, source mismatch or ERROR requires
a retry to fresh paths/scratch. Never append to an unverified output. Keep
old attempts for audit; cluster/process-specific output remaps prevent
replacement. Select exactly one valid attempt per original shard. Duplicate
attempts fail collection. Local worker invocations must pass the exact
config-derived settings, pinned preflight and bundle/commit environment;
use the prepared worker wrapper on AF.

```sh
python3 -m module14.collect --manifest ORIGINAL_MANIFEST.jsonl --config USER_APPROVED_CONFIG.json --part SHARD RESULT RECEIPT --families CONFIG_FAMILIES --perturbativity-limit CONFIG_LIMIT --source-commit FROZEN_COMMIT --source-bundle-sha256 EXACT_BUNDLE_HASH --preflight-report NEW_PREFLIGHT.json --output NEW_COLLECTION.json
```

Repeat --part for every chosen shard. Missing points, family hashes/order,
wrong stage settings, changed runtime/source/config/binary, duplicates and
nonfinite/truncated records fail closed. A final collection with any
computational ERROR is not COMPLETE. Scientific UNKNOWN and diagnostics
remain intact and may be analyzed conditionally.

```sh
python3 -m module14.final_export --manifest ORIGINAL_MANIFEST.jsonl --config USER_APPROVED_CONFIG.json --part SHARD RESULT RECEIPT --matching-card module14/conditional_scan/matching_card.json --source-commit FROZEN_COMMIT --source-bundle-sha256 EXACT_BUNDLE_HASH --preflight-report NEW_PREFLIGHT.json --output NEW_EXPORT_DIR
python3 -m module14.final_plot --export-dir NEW_EXPORT_DIR --output NEW_PLOT.svg
```

Final export uses config family settings and the original manifest. Supply all
--part triples. It reruns only deterministic saved-data verification and
conditional flavor postprocessing. It does not rerun workers or production.
The final CLI uses SQLite for manifest lookup, joined rows, export sorting,
duplicate detection and ranks. Set TMPDIR and SQLITE_TMPDIR to provisioned scratch. Allow disk for several
complete row stores plus the final tables; memory is bounded by a row and small SQLite
caches. The 6,000-row synthetic replay peaked at 93,872 KiB (256 MiB limit).
`join(..., streaming=True)` returns a DiskRows iterable that callers must
close; the default legacy join and plotting can still consume proportional
RAM. Scientific labels and output schemas are unchanged.

Export publishes by a same-filesystem atomic rename under an exclusive
sibling `.export-lock`; exceptions/KeyboardInterrupt clean temporary output.
After SIGKILL or machine failure, verify the owner has stopped before removing
the stale lock and its hidden scratch directory and retrying to a fresh target.
An existing published export is never overwritten. See
PHYSICS_ADAPTER_READINESS.md for native build validation and unresolved physics;
none of those research backends has become an operative worker constraint.

Optional production enrichment adds `--production-dir EXISTING_RATE_CARDS
--production-contract EXPECTED_PRODUCTION_CONTRACT.json` to export. See
FINAL_OUTPUT_SCHEMA.md for exact family hashes, artifact checks and separate
13/14 TeV channels. This consumes already externally validated inputs; it
never runs MG5 or transfers a rate between points. Retain nulls for absence.
Benchmark ranks use the exact tb cascade product and are scoped to a common
production contract. They do not imply physical acceptance or sensitivity.
Archive manifest, config, preflight, source archive/commit, selected receipts,
collection, export hashes and optional production provenance together.
