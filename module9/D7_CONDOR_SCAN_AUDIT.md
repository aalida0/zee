# D7 local implementation and manual CERN handoff audit

2026-10-28. Branch `feature/zee-d7-lxplus-condor-scan-pilot`, verified descendant
of D6 `a39afed7cd0ee7f4358dabdbde32729818f1f909`. Only D7 files changed.
Parent `/home/amine/zee/.git/info/exclude` already ignores `/workspaces/`;
no parent tracked files or older worktrees were changed.

**CERN jobs submitted/executed: 0/0; no Cluster/Proc IDs.** The user explicitly
reserved all LXPLUS access and submission for manual execution. SSH was never
attempted; this is not an access failure. CERN account/quota/authentication,
worker OS, JobFlavour and scientific Python environment remain unverified.
No local `condor_submit` exists, so no native submit-file parser validation or
scheduler dry run is claimed. The [manual runbook](D7_MANUAL_CERN_RUNBOOK.md)
contains the exact clone, preflight, staging, four-job submission, queue/history
and collection commands. The collector now requires `--condor-history` for a
CERN completion claim.

| Gate | Status |
| --- | --- |
| D7_GRID_GENERATION_PASS | true: 32 distinct NO inputs, four eight-point shards |
| D7_LOCAL_WORKER_PASS | true: D0 NO source oracle and four real local sandbox executions |
| D7_LOCAL_AGGREGATE_PASS | true: 32 content-verified local results, no evaluation errors |
| D7_LXPLUS_CONDOR_EXECUTION_PASS | false; manual execution pending |
| D7_AGGREGATE_PASS | false for CERN; real four-job receipts/history absent |
| D7_BATCH_PILOT_COMPLETE | false; local simulation only |
| Global acceptance / complete constraints | null / false, always |

The executed source was committed before staging:
`aded8e1496d99a5edb33586378114988d9ec3dd4`.
Its `git archive HEAD | gzip -n` bundle SHA256 is
`021b1a3061198ec5e3e82bc0372ed2a3331f9d21a075748d68b0960646f192bc`.
The subsequent evidence-only commit adds this audit and
[`validation/module9/d7_pilot.json`](../validation/module9/d7_pilot.json);
it does not alter executed code. Stage the delivered final HEAD on CERN: that
new archive will have its own commit/hash in its generated manifest. The
recorded local execution SHA must not be substituted for a later CERN run.

Implementation fixes bind the exact illustrative NO seed, inverse coefficients,
nonvaried scalar inputs and all Module3/2/1 IDs. Module2 and Module3 schemas,
frozen foundations, scalar SHA, finite numbers and open charged mass ordering
are checked before physical evaluation. Inputs with wrong datasets/orderings,
changed targets/families, stale hashes or incompatible IDs are rejected.
Numerical exceptions/nonfinite diagnostics become `EVALUATION_ERROR`, distinct
from `SCOPED_FAIL_OR_UNKNOWN`. Every output declares incomplete constraints.

Staging refuses dirty trees and existing run directories. Archive generation,
shards and copied scripts use the same committed tree. The wrapper checks bundle
SHA before source imports, validates the archive's embedded Git commit and safe
members, compares the wrapper with its archived copy, then uses the archived
runtime setup. Receipts include commit/bundle/shard/result hashes, actual host,
Python executable/hash, library versions, environment setup and package-inventory
hashes, pip version, runtime, peak RSS and exit/cutflow counts. Workers and
collector refuse existing output files.

Collection verifies the deterministic manifest/input inventory, exact canonical
shard bytes, submit-side artifact hashes, all returned row identities, scalar
inputs, gate/status consistency, neutrino residuals, receipt counts/runtime and
source origin. It rejects extra or duplicate results and changed content even
when a result checksum is recomputed. Missing workers or evaluation errors
keep the full denominator and prevent completion. CERN mode additionally needs
one four-job cluster, matching receipt IDs, one Owner and recorded execution
host/runtime with successful nonsignaled exits. These are consistency checks,
not independent cryptographic remote attestation. The history tests use clearly
marked synthetic fixtures; they are not CERN evidence.

Local validation used Python 3.10.12, numpy 2.2.6, scipy 1.15.3, mpmath 1.3.0 and
jsonschema 4.23.0. The laptop initially lacked jsonschema; it was installed only
in ignored `validation/module9/local/venv` with system-site-packages. No worker
package installation is performed. The default setup is explicitly marked
`SYSTEM_PYTHON_UNVERIFIED_ON_CERN`; no CVMFS path was guessed. A verified CERN
setup, if needed, must be committed and restaged per the runbook.

Reproducible local checks (activate that environment on this laptop):

```bash
source validation/module9/local/venv/bin/activate
python3 -m unittest discover -s tests -p 'test_module9_*.py' -v
python3 -m module9.d7_prepare --seed module3/example.json \
  --output-dir validation/module9/local/local_prepare_v2
python3 -m module9.d7_worker \
  --shard validation/module9/local/local_prepare_v2/shards/part_000.jsonl \
  --output validation/module9/local/local_prepare_v2/test_results_0.jsonl \
  --receipt validation/module9/local/local_prepare_v2/test_receipt_0.json
# From a clean committed tree, fresh output directory only:
bash scripts/zee_d7_stage.sh validation/module9/local/staged_local_v1
```

These paths already contain evidence; use fresh versioned names on repeats.
For the four sandbox runs, copy `worker.sh`, `scan_bundle.tar.gz`, `bundle.sha256`,
`source_commit.txt` and the corresponding `shards/part_00N.jsonl` into four fresh
sandbox directories. Run `bash worker.sh part_00N.jsonl` in each (one argument
explicitly marks local simulation), copy returned `results.jsonl` and
`receipt.json` to `results/result_N.jsonl` and `status/receipt_N.json`, then:

```bash
python3 -m module9.d7_collect \
  --manifest validation/module9/local/staged_local_v1/manifest.json \
  --shards validation/module9/local/staged_local_v1/shards \
  --results validation/module9/local/staged_local_v1/results \
  --receipts validation/module9/local/staged_local_v1/status \
  --output validation/module9/local/staged_local_v1/summary.json
bash -n scripts/zee_d7_stage.sh scripts/zee_d7_preflight.sh \
  module9/condor/worker.sh module9/condor/environment.sh
git diff --check
```

All **25 focused tests passed** in 16.466 seconds; Bash syntax and whitespace
checks passed. The independently prepared shard bytes matched the committed
archive's generated shards. Restaging into an existing directory failed with
exit 66. Four local wrappers exited 0, with 32/32 returned results. Sum of
worker-reported elapsed times: 6.215 seconds; maximum Python-process peak RSS:
97,812 KiB. These are laptop measurements, not CERN performance estimates.
Compact hashes, receipts and selected examples are committed; raw inputs,
outputs, archives and logs remain ignored.

| Sequential scoped cutflow | Points remaining |
| --- | ---: |
| Generated / reconstructed | 32 / 32 |
| Sufficient BFB | 18 |
| Tree unitarity after BFB | 1 |
| Scalar STU/EWPO after preceding gates | 1 |
| Algebraic NO closure | 1 |
| Evaluation errors | 0 |

Independently evaluated gate counts: BFB 18 PASS / 14 FAIL, unitarity 1 PASS /
31 FAIL, EWPO 4 PASS / 28 FAIL. Final outcomes: one scoped survivor and 31
`SCOPED_FAIL_OR_UNKNOWN`. The retained point is
`d7_NO_neutral_near_heavy_07`, with mH1 = 298.726655 GeV and mH2 = 532.932913 GeV,
and NO inverse relative residual `3.875782149384548e-14`. The separate D0 NO
source oracle gave `3.029000106635716e-15`. Maximum scalar reconstruction
spectrum relative residual: `1.0080137971084283e-09`; maximum tadpole/v³:
`5.989674669630367e-15`; maximum mixing residual: `1.3969838619232178e-09 GeV²`.

Charged support spans mH1 = 254.955–1192.873 GeV and mH2 = 532.933–1917.274 GeV.
Nineteen points have mH2 > 1 TeV; none passes the scoped combination. Examples
mH1/mH2 = 1042.825/1917.274, 1108.515/1914.099 and 1179.801/1752.607 GeV all
fail scoped screening. This is a small exploratory LHS support design, not
justified priors, representative coverage, experimental exclusion thresholds,
a model-wide allowed fraction or a publication novelty result. The source NO
matrix has not been relabeled IO, and no NuFIT joint likelihood was evaluated.

Global vacuum, complete LFV/Wgamma, official NuFIT joint likelihood, validated
physical B→Xsγ, RG closure, other flavor and collider constraints remain UNKNOWN.
No D8 implementation was undertaken. Next is a separate, physically motivated
multi-TeV NO plus genuinely sourced IO scan, efficient scalar screening,
representative complex inverse-Yukawa families and full D4 charged decays.
Conditional Module5 flavor/LFV must remain labeled incomplete. Study potential
flavor–collider correlations and backgrounds/reach after calibrated physical
signal selection; no EPJC novelty is promised.
