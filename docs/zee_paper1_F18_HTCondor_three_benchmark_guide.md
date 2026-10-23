# F18 three-benchmark MadWidth campaign on HTCondor (AF)

Use this **instead of running 3-body MadWidth exhaustively on a laptop**.
The existing successful F16–F17f scalar/CKM/lepton source physics inputs
remain immutable. Jobs are independent: one original F13 benchmark per
HTCondor job. Each job runs the same two-body bootstrap followed by
two-plus-three-body MadWidth as local F18, with `--nb-core=2`
and `request_cpus=2`. Three-body `min_br=0` may be very expensive;
time limits, scheduler policies, and whether gfortran/Python dependencies
are available on execute hosts must be checked for the target pool.

## Local Ubuntu machine: package only the essential scientific inputs

Run in `~/zee` after pulling `feature/global-scan-priority1`:

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only
export ZEE_F16_DIR="$HOME/zee/work/zee_paper1_F16_exact_SARAH_three_heavy_20261021T143647Z"
bash scripts/zee_paper1_F18_package_for_condor.sh \
  "$ZEE_F16_DIR" \
  /home/amine/codes/tools/MG5_aMC \
  "$HOME/zee/work/F18_condor_payload_20261023"
```

The package contains source F16/F17 complex JSON, original genuine SARAH
UFO, F17d/e/f validated cards and reports, repository scripts and the
locally installed MG5 distribution. **Previous huge failed/running F18
output directories are not packed.** Check `du -h` of the tarballs before
moving them; full MG5 installs may be large.

## Transfer to the UChicago AF submit host

The exact hostname and destination depend on current site access.
Example consistent with previous AF operations:

```bash
rsync -avP "$HOME/zee/work/F18_condor_payload_20261023/" \
  aalida@login01.af.uchicago.edu:/data/aalida/F18_condor_payload_20261023/
```

Run `rsync` only after verifying access and `/data/aalida` storage quota.
Only source and code go to the AF, not prior F18 outputs.

## On the submit host: submit once, disconnect

```bash
ssh aalida@login01.af.uchicago.edu
cd /data/aalida/F18_condor_payload_20261023
command -v condor_submit
condor_submit F18_3cases.sub
condor_q "$USER"
```

There are exactly 3 independent jobs, **2 requested cores each**,
8 GiB memory and 25 GB scratch disk. On each worker, Condor file-transfer
moves the three tarballs to the worker scratch directory. The runner
checks `python3` + numpy/scipy, gfortran and make, extracts its own
MG5 installation, computes exactly one point, and transfers back a
single archive: `F18_result_F13_heavy_<ID>.tar.gz`. Archived failures
contain MG5 logs and diagnostic JSON when available. These transfers
are compatible with workers that do **not** share `/data/aalida` mounts.

This is **one HTCondor layer only**; MG5 runs in local multicore mode
inside each allocated slot, not by submitting further nested Condor jobs.
The requested resource sizes are initial estimates, not a guarantee of
adequacy or eligibility for long-running jobs. Check local AF quotas and
maximum wall time; jobs can be evicted or held if the policy is exceeded.

## Inspect or stop

```bash
condor_q "$USER"
condor_q -better-analyze <cluster-id>
condor_history "$USER" -limit 10
tail -f logs/F18_<cluster-id>.0_F13_heavy_0001330.out
# To remove the submitted campaign (this discards still-running work):
# condor_rm <cluster-id>
```

Your currently running **local** MadWidth calculation cannot automatically
resume in Condor: this launches three new independent jobs. Decide whether
to let the local first benchmark finish or interrupt it before submitting,
to avoid duplicated CPU expense.

## After three output archives arrive

On the AF, from the same payload folder:

```bash
PYTHONPATH="$PWD" python3 -c "import sys; sys.path.insert(0, 'scripts'); from zee_paper1_F18_merge_condor_results import merge; merge('.', 'F18_final_three_benchmarks')"
```

The merger checks the worker exit status, complete F18 per-case result,
actual MadWidth input provenance, shared MG5 binary SHA and exact F17f
source report hashes. It creates:

- `F18_final_three_benchmarks/F18_CONDOR_three_source_verified.json`
- `F18_final_three_benchmarks/F18_CONDOR_three_summary.csv`

It refuses to claim precision QCD, off-shell all-orders corrections,
full 2026 flavor/Higgs/vacuum allowance or ATLAS exclusion. MadWidth's
`--body_decay=3` is a tree-level NWA calculation with the model and
numerical settings in the job logs. 
