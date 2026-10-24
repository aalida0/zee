# F18 on CERN LXPLUS / HTCondor with heavy inputs and outputs in EOSUSER

**Goal:** reuse locally completed original `F13_heavy_0001330` (tree-level
MadWidth source-verified widths), and run only the remaining
`F13_heavy_0000981` and `F13_heavy_0001003` on CERN's HTCondor pool.

This is the same `F18` physics script as the UChicago AF version. No changes
to the original F16/F17f physics cards, EW matching, or SARAH-generated UFO.

**Storage layout:** single large compressed input tarballs and completed
result archives under `/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024`.
Small submit files and Condor event logs in `$HOME/zee_f18_lxplus_submit_20261024`
on LXPLUS (usually AFS), **not inside EOS**. During execution, MG5 builds
integrands in HTCondor worker-local scratch, never in EOS. CERN documents
support HTCondor `transfer_input_files=root://eosuser.cern.ch//eos/...` and
`output_destination=root://eosuser.cern.ch//eos/...`.

## Step 1: prepare the validated source archive on your Ubuntu PC

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only
export ZEE_F16_DIR="$HOME/zee/work/zee_paper1_F16_exact_SARAH_three_heavy_20261021T143647Z"
bash scripts/zee_paper1_F18_package_for_condor.sh \
  "$ZEE_F16_DIR" \
  /home/amine/codes/tools/MG5_aMC \
  "$HOME/zee/work/F18_lxplus_two_remaining_20261024" \
  "$ZEE_F16_DIR/F18_MadWidth_exact_three_20261023T124259Z"
```

This builds a four-file physics archive set: F16-F17f source bundle,
actual MG5 installation bundle, repo-script bundle, and a **SHA-verified
local successful F18/1330 results archive**, plus scripts and hashes.
No previous huge F18 worker scratch directories are included. The
validated local source case must have both real SLHAs and
`validated_model_LO_widths.json`. The all-cases `summary.json` may be
missing because it was interrupted: the archiver can verify against
`initial_manifest.json` plus immutable F17f card and SLHA hashes.

## Step 2: copy heavy tarballs directly into your EOSUSER directory

From your PC:

```bash
ssh aalida@lxplus.cern.ch \
  'mkdir -p /eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024'

rsync -avP "$HOME/zee/work/F18_lxplus_two_remaining_20261024/" \
  aalida@lxplus.cern.ch:/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/
```

These are only a few compressed files. Check `du -h` and your personal EOS
quota; transferring a very large MG5 installation can take time. No
large directory of tiny files is written to EOS. CERN EOS documentation
discourages intensive write/read operations via FUSE.

## Step 3: on LXPLUS, create the small local submit directory

```bash
ssh aalida@lxplus.cern.ch
export F18_EOS=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024

bash "$F18_EOS/F18_prepare_lxplus_submission.sh" \
  "$F18_EOS" "$HOME/zee_f18_lxplus_submit_20261024"

cd "$HOME/zee_f18_lxplus_submit_20261024"
cat F18_LXPLUS_2remaining.sub
condor_submit F18_LXPLUS_2remaining.sub
condor_q "$USER"
```

The preparer verifies source SHA256 for all input archives, checks
the already completed local 1330 output and stages it into
`$F18_EOS/results` (without overwriting), then writes a 2-job submission
file. **Do not submit the job file directly from EOS.**

Each worker requests `request_cpus=2`, `request_memory=8192MB`,
`request_disk=25000000KB`, and the CERN `nextweek` job flavour. These
are initial resource estimates: they depend on CERN batch policy and
available slots. Each worker requires accessible `python3` with
`numpy,scipy`, `make`, `gfortran`, and ABI-compatible MG5 components
to compile MadWidth code. The worker preflight tests these and returns
a diagnostic result archive if they are missing. On-site GPU is not used.

**EOS authentication:** the submit file relies on CERN's Condor file
transfer plug-in to fetch three `root://eosuser.cern.ch//eos/user/a/aalida/...`
files and return a compact tarball with `output_destination`. If your
Condor submit host cannot authorize transfers to EOSUSER, use
`condor_q -hold` and `condor_q -hold -long` for troubleshooting and
refer to local CERN batch credentials/transfer configuration. Do not put
secrets or Kerberos passwords inside the worker script.

## Step 4: inspect progress and returned EOS results

```bash
condor_q "$USER"
condor_q -hold "$USER"
condor_history "$USER" -limit 10

ls -lh "$F18_EOS/results/"
```

The two new output tarballs should be:

```text
F18_result_F13_heavy_0000981.tar.gz
F18_result_F13_heavy_0001003.tar.gz
```

The completed local case is already there as:

```text
F18_local_completed_F13_heavy_0001330.tar.gz
```

A successful Condor job log does **not** by itself certify the widths:
the F18 merger independently checks JSON agreement, both MadWidth
SLHA hashes, source F17f/MG5 provenance, and missing or duplicate cases.

## Step 5: merge all three WITHOUT rerunning 1330

After both returned tarballs exist:

```bash
python3 "$HOME/zee_f18_lxplus_submit_20261024/F18_merge_condor_results.py" \
  --results-dir "$F18_EOS/results" \
  --output-dir "$HOME/zee_f18_lxplus_submit_20261024/F18_final_three_benchmarks"

# Preserve final comparison on EOS:
cp "$HOME/zee_f18_lxplus_submit_20261024"/F18_final_three_benchmarks/* \
  "$F18_EOS/results/"
```

The merger produces `F18_CONDOR_three_source_verified.json`
and `F18_CONDOR_three_summary.csv`, clearly distinguishing the
precomputed local case from the two HTCondor cases. This is still
source-validated **tree-level** Zee-model phenomenology, not
QCD-NLO-precision widths or comprehensive constraint/exclusion claims.

**Important:** a Condor job interrupted/evicted during an expensive
three-body integration may restart from scratch. The worker does not
implement full MadWidth integration checkpointing. 


## CERN worker preflight failures and optional 16-core isolated retry

If a returned output archive is just a few hundred bytes, the F18 merger
must fail closed: no physics results exist. Inspect the original submit
stdout/stderr before attempting a more expensive batch allocation:

```bash
find "$F18_EOS/results/logs" \
  "$HOME/zee_f18_lxplus_submit_20261024/logs" \
  -type f \( -name '*.out' -o -name '*.err' \) \
  -print -exec tail -60 {} \;
```

The original worker used the bare default CERN Python and did **not** load
the LCG view; that can lead to missing NumPy/SciPy or gfortran on EL9
workers (this is a possible cause, not a diagnosis until logs are read).

The updated worker first sources the CERN EL9 view
`/cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh`,
then checks Python/Fortran prerequisites and preserves
`worker_diagnostic.txt` and `python_preflight.log` inside the returned
result tarball. No original physics cards or validated couplings change.

To retry **without reuploading the large tarball bundles**, on the local
Ubuntu computer:

```bash
cd ~/zee
git switch feature/global-scan-priority1 && git pull --ff-only
ssh aalida@lxplus.cern.ch 'mkdir -p ~/zee_f18_retry_code_20261024'
scp scripts/zee_paper1_F18_condor_worker.sh \
    scripts/zee_paper1_F18_prepare_lxplus_submission.sh \
    aalida@lxplus.cern.ch:zee_f18_retry_code_20261024/
```

Then on LXPLUS:

```bash
export F18_EOS=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024

bash ~/zee_f18_retry_code_20261024/zee_paper1_F18_prepare_lxplus_submission.sh \
    "$F18_EOS" \
    "$HOME/zee_f18_lxplus_retry16_20261024" \
    16 \
    retry16_20261024 \
    "$HOME/zee_f18_retry_code_20261024/zee_paper1_F18_condor_worker.sh"

cd ~/zee_f18_lxplus_retry16_20261024
condor_submit F18_LXPLUS_2remaining.sub
condor_q "$USER"
```

This requests **16 cores/job**, ~24 GB RAM/job and 40 GB of worker
scratch. Each MadWidth invocation uses `--nb-core=16`; worker setup
and the submit script agree. Larger requests can experience longer
queue times; use 8 instead of 16 in the positional `CPUS` argument if
needed.

The new returned results are under
`$F18_EOS/results/retry16_20261024`; the original failed archives in
`$F18_EOS/results` are never overwritten. A source-validated copy of
the completed local `0001330` is also included inside the retry
directory, so the final merge is simply:

```bash
python3 ~/zee_f18_lxplus_retry16_20261024/F18_merge_condor_results.py \
  --results-dir "$F18_EOS/results/retry16_20261024" \
  --output-dir "$HOME/zee_f18_lxplus_retry16_20261024/F18_final_three_benchmarks"
```

Do not resubmit merely because a job returned an exit code of 1. The
error might be due to missing model input, an MG5 runtime failure,
filesystem limits, or other issues for which more CPUs are not a remedy.
