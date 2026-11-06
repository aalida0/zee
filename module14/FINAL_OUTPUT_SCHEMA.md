# Canonical final output contract, version 1

`python -m module14.final_export --help` consumes the original manifest,
config and selected receipt-checked shard triples. It validates the complete
collection before interpretation, uses frozen Eq.(4) flavor postprocessing,
and checks saved D4 decay inventories. No worker, inverse solve, new
proposal, production calculation or vacuum search runs in this step.

- `families.jsonl`: canonical sorted-key JSON, finite numbers, LF newline;
  schema `d14-final-family-1`, sorted by integer point ID, ordering and family.
  A scalar with no family evaluation has one row with null family identity,
  never a fabricated Yukawa family. Evaluated points retain every family,
  including FAIL/ERROR/UNKNOWN outcomes.
- `families.csv`: fixed columns in `final_export.COLUMNS`; nulls are empty
  cells, while real closed-channel BRs may be numeric zero. Consult JSONL
  for omission reasons, complete original results and nested provenance.
- `cutflows.json`: arm-dependent scalar gate counts and evaluated family
  statuses by NO/IO. The collector retains the full expected family-slot
  cutflow including NOT_EVALUATED slots; it is in the joined collection.
  These are proposal-dependent counts, not model-volume fractions.
- `collection.json`: complete collector report, including all expected
  family slots, omitted-stage counts, resources and source provenance.
- `benchmarks.json`: only rows with a defined conditional rate rank; empty
  if no qualified production was supplied. Ranking uses the exact tb
  cascade product within a specified production contract, with deterministic
  ID/ordering/family tie breaks. A nominal B disfavor is never a physical cut.
- `audit.json`: schema `d14-final-export-1`; written last, COMPLETE only after
  all tables were written; exact input digest, contract digest, row/point
  counts and output-file SHA256. An interrupted directory without this
  valid receipt is incomplete and must be retried at a new path.

Every row records scalar/card/family hashes, arm, all scalar/family statuses,
original input and actual saved results, worker commit/bundle, matching-card
hash, sidecar source hashes and explicit omissions. `global_acceptance`
and `np_theory_sigma` stay null; `bsg_physical_status` stays UNKNOWN. Scoped
LFV PARTIAL remains visible. Numerical ERROR is never scientific FAIL.
Disabled optional stages stay NOT_EVALUATED. The new final collector rejects
computational ERROR as a successful final collection.

Rates and BR columns: `BR_H2_H1Z`, `BR_H1_tb`, `sigma_13_pb`, `sigma_14_pb`,
`cascade_tb_13_pb`, `cascade_tb_14_pb`. Each non-null rate is independently
bound to that same scalar and Yukawa family. The reported decay precision
is complete on-shell tree two-body, with no loop/off-shell uncertainty.
CSV ranks are conditional benchmark ranks, never global acceptance ranks.

Production enrichment is a separate **saved-ID input contract**. It does
not generate cards, choose new points, submit jobs or alter the proposal
manifest. Supply files named `FAMILY_INPUT_SHA.13TeV.json` and/or
`FAMILY_INPUT_SHA.14TeV.json`; each follows `conditional_scan.workflow.production`:

```json
{
  "scalar_sha256": "EXACT_SCALAR_HASH",
  "module2_input_sha256": "EXACT_FAMILY_INPUT_HASH",
  "yukawa_sha256": {"F":"HASH", "D":"HASH", "Ye":"HASH", "Ye2":"HASH"},
  "model": "ZeeTypeII", "state": "H2", "energy_TeV": 13,
  "sigma_pb": "REPLACE_WITH_POSITIVE_FINITE_NUMBER",
  "process": "EXACT_PROCESS", "charge_definition": "EXACT_CHARGE_SUM",
  "order": "EXACT_ORDER", "pdf": "EXACT_PDF_SET_AND_MEMBER",
  "scale_scheme": "EXACT_SCALE_AND_FLAVOR_SCHEME",
  "documentation": "SOURCE_AND_VALIDATION_DESCRIPTION",
  "uncertainty": "EXPLICIT_MEASURED_SCOPE_OR_UNKNOWN",
  "artifacts_sha256": {"relative/path/to/real/artifact":"SHA256"}
}
```

All artifact paths must stay beneath the card's directory and exist with
matching hashes. The separate `--production-contract` JSON maps keys `13`
and/or `14` to exactly `energy_TeV, process, charge_definition, order, pdf,
scale_scheme`. Values must match every supplied card. Include the flavor
scheme, PDF member and scale values/rule explicitly in those strings.
Wrong energy/PDF/order/process/charge/scale fails closed; no interpolation
or universal energy rescaling is supported. A missing card is null, never
zero. Bad supplied data raises an error rather than becoming missing data.
The historical 16+3 rate map is a reference, not a new-point interpolator.

`python -m module14.final_plot --export-dir EXPORT --output NEW.svg` verifies
export hashes and makes a deterministic 13/14 TeV rate plot. Missing rates
are disclosed. Matplotlib 3.10.9 is pinned; set MPLCONFIGDIR to a writable
scratch directory. The caption discloses conditional physics; no experimental
sensitivity is inferred. JSON/table exports are deterministic for the same
saved input and source, irrespective of shard argument order. Resource totals
and receipt hashes remain original provenance and may differ for genuinely
different executions or partitioning. Postprocessing currently materializes
the joined rows in memory: provision RAM according to saved family count;
it does not have the worker's fixed 2 GB memory envelope.
