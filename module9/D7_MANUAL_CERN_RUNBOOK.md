# D7 manual CERN execution (32 points, four jobs)

No CERN access or submission was performed by Codex, at the user's request.
This runbook is for the account holder to execute on LXPLUS. No site runtime,
quota, accounting group or worker package availability is assumed verified.

Use a fresh AFS checkout, distinct from the laptop filesystem:

```bash
mkdir -p ~/zee/workspaces
# If ~/zee is tracked, ensure /workspaces/ is locally excluded in its
# .git/info/exclude. Never change the parent's tracked .gitignore.
git clone --branch feature/zee-d7-lxplus-condor-scan-pilot --single-branch \
  https://github.com/aalida0/zee.git ~/zee/workspaces/zee-condor-d7
cd ~/zee/workspaces/zee-condor-d7
git status --short
git rev-parse HEAD
git ls-remote origin refs/heads/feature/zee-d7-lxplus-condor-scan-pilot
```

The two SHAs must match the delivered revision. A pre-existing checkout must
be inspected instead of overwritten. Keep credentials on CERN; never package
tokens, proxies, passwords or keytabs. The source bundle contains tracked files
from Git only.

Preflight and local source oracle, still without submission:

```bash
set -o pipefail
mkdir -p validation/module9/local
bash scripts/zee_d7_preflight.sh | tee validation/module9/local/cern_preflight_v1.txt
python3 -m unittest discover -s tests -p 'test_module9_*.py' -v
```

Confirm the real billed account (`id -un`), AFS submit path and quota, JobFlavour,
OS/CPU, memory and authentication against your current CERN project policy.
Inspect `module9/condor/d7_pilot.sub`: its requests are a template (one CPU,
2 GB memory/disk, longlunch), not verified CERN allocations. The read-only
preflight checks submit-host imports and the D0 NO closure; it cannot establish
worker-node packages. EOS is unused: there are no EOS scheduler log paths or
worker network installations. Any future EOS use requires separate permission,
authentication, transfer and cleanup validation.

`module9/condor/environment.sh` currently uses system Python. If that is not
available with numpy/scipy/jsonschema/mpmath on your matched workers, stop and
select a documented, actually verified CERN CVMFS environment. Change only the
new D7 setup/template, record the pinned release/OS/Python identity, test, commit
and push, then stage a fresh run. Do not guess a CVMFS release or install packages
on workers. `getenv=FALSE` is intentional; sourcing a view only in the interactive
submit shell does not configure the worker. A setup/import/bundle failure may
leave absent output files and held jobs; inspect the four per-job stderr/event
logs. Do not retry over returned evidence.

After confirming the site/account/runtime, stage from the clean committed tree:

```bash
bash scripts/zee_d7_stage.sh
cd validation/module9/local/d7_pilot
sha256sum -c bundle.sha256
cat source_commit.txt
# Inspect the four generated ads without submitting:
condor_submit -dry-run submit.ads d7_pilot.sub
# MANUAL SUBMISSION: exactly four jobs, once only.
condor_submit -terse d7_pilot.sub | tee submission.ids
cluster_id=$(awk 'NR==1 {split($1,a,"."); print a[1]}' submission.ids)
printf '%s\n' "$cluster_id" > cluster_id.txt
condor_q "$cluster_id"
```

Expect one cluster with ProcIds 0–3. Confirm those IDs and your account in
`condor_q`; preserve `submission.ids`, the dry-run ads and per-job logs. Do not
submit the same run directory again. Each rerun needs a fresh versioned stage
path, e.g. `bash scripts/zee_d7_stage.sh validation/module9/local/d7_pilot_v2`.
Staging fails if the directory exists or the tracked/untracked tree is dirty
(ignored local evidence is allowed). The archive, shard generation and copied
scripts all come from the same committed Git tree.

After all four jobs leave the queue, inspect their actual completion and collect:

```bash
# From validation/module9/local/d7_pilot:
cluster_id=$(cat cluster_id.txt)
condor_q "$cluster_id"
condor_history "$cluster_id" -json > condor_history.json
condor_history "$cluster_id" -af ClusterId ProcId Owner JobStatus ExitCode ExitBySignal RemoteHost RemoteWallClockTime MemoryUsage
cd ~/zee/workspaces/zee-condor-d7
python3 -m module9.d7_collect \
  --manifest validation/module9/local/d7_pilot/manifest.json \
  --shards validation/module9/local/d7_pilot/shards \
  --results validation/module9/local/d7_pilot/results \
  --receipts validation/module9/local/d7_pilot/status \
  --condor-history validation/module9/local/d7_pilot/condor_history.json \
  --output validation/module9/local/d7_pilot/summary.json
```

All four history ads must be retained, with matching Cluster/Proc IDs and one
Owner, terminal successful exits, execution hosts and runtime. A failed/missing
job or point evaluation error makes completion false; a scoped physical fail
does not. Collector exit code 2 means incomplete; malformed, changed or incoherent
inputs/outputs are rejected with a nonzero exit. Use a fresh summary filename
for a later collection attempt. Without `--condor-history`, the summary is always
`LOCAL_SIMULATION` and `D7_BATCH_PILOT_COMPLETE=false`, even if every point returned.
Receipts and history establish recorded consistency, not cryptographic remote
attestation. Preserve real scheduler evidence for review.

Scalar PASS covers reconstruction, sufficient BFB, tree unitarity and scalar
STU/EWPO only. NO inverse closure is algebraic; it is not a NuFIT likelihood.
Every result retains `global_zee_acceptance=null`, `constraints_complete=false`.
Zero survivors is legitimate. No model-wide allowed fraction follows from these
32 exploratory LHS support points. IO needs a separately sourced genuine target.

The submit syntax was checked against the [HTCondor submitting-a-job manual](https://htcondor.readthedocs.io/en/main/users-manual/submitting-a-job.html).
The prescribed [CERN retry source](https://batchdocs.web.cern.ch/workarounds/job-retry.html)
returned HTTP 403 to the documentation reader; no retry/site behavior was inferred.
The [2024 CERN/Key4HEP presentation](https://indico.cern.ch/event/1307378/contributions/5729652/attachments/2789482/4864493/fccphysweek24_atd_240130.pdf)
is a historical anchor, not evidence for current CERN configuration.
