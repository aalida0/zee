#!/usr/bin/env bash
# F21b corrected: 24 broad independent stratified Zee jobs, preserving failed six.
# Read-only inputs: exact F18-F19d JSON and F20 corrected merge summary/CSV.
set -Eeuo pipefail
run="$HOME/zee_F21b_wide_stratified_24_20261024"
eos="/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F21b_wide_24shards_20261024"
[[ ! -e "$run" && ! -e "$eos" ]] || {
 echo "F21_REFUSE_OVERWRITE_AFS_OR_EOS_OUTPUT $run $eos" >&2;exit 2; }
[[ -s "$HOME/F21_scripts_bundle.tar.gz" && -f "$HOME/zee_paper1_F21_condor_worker.sh" ]] || {
 echo "F21_SOURCE_ARCHIVE_OR_WORKER_MISSING" >&2; exit 2; }
f18="$HOME/zee_f18_lxplus_submit_20261024/F18_final_three_benchmarks/F18_CONDOR_three_source_verified.json"
f19="$HOME/zee_f19_scalar_ewpo_20261024/F19_results/F19_integrated_three_constraint_ledger_NOT_ALLOWED.json"
f19b="$HOME/zee_f19b_exact_neutrino_partial_LFV_20261024/F19b_results/F19b_exact_complex_neutrino_partial_LFV_NOT_ALLOWED.json"
f19c="$HOME/zee_f19c_three_vacuum_witness_64_20261024/F19c_results/F19c_three_vacuum_witnesses_NOT_GLOBAL.json"
f19d="$HOME/zee_f19d_analytic_LO_bsgamma_20261024/F19d_analytic_LO_three_source_matched_NOT_PRECISION.json"
f20c="$HOME/zee_F20_leptonic_corrected_20261024/F20_ALL_shards_scalar_LO_flavor_NOT_EXCLUSION.csv"
f20s="$HOME/zee_F20_leptonic_corrected_20261024/F20_PRODUCTION_exploratory_summary.json"
for f in "$f18" "$f19" "$f19b" "$f19c" "$f19d" "$f20c" "$f20s"; do
 [[ -s "$f" ]] || { echo "F21_MISSING_SOURCE $f" >&2;exit 2; }
done
# Explicit source consistency check before wasting large Condor slots.
python3 - "$f18" "$f19" "$f19b" "$f19c" "$f19d" "$f20c" "$f20s" <<'PY'
import sys,json,hashlib,pathlib
A=[pathlib.Path(x) for x in sys.argv[1:]]
J=[json.loads(x.read_text()) for x in A[0:5]]
H=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
for i,key in enumerate(("F18","F19","F19b","F19c")):
 assert J[4]["actual_CERN_F18_F19_F19b_F19c_source_SHA256"][key]==H(A[i]),key
S=json.loads(A[6].read_text())
assert S["four_complete_shards"] is True
assert S["output_files_SHA256"][A[5].name]==H(A[5])
assert S["calibrated_model_exclusions_or_accepted_points"] is None
assert S["original_exact_three_F18_F19_F19b_F19c_F19d_SHA256"]=={
 key:H(v) for key,v in zip(("F18","F19","F19b","F19c","F19d"),A[:5])}
print("F21_ALL_ORIGINAL_F18_F19D_F20_SOURCE_SHA_CHECKS_PASSED")
PY
# Authenticate the *staged/renamed* F20 CSV using the corrected
# canonical filename-independent SHA contract BEFORE submitting 24 jobs.
# Also import all real science backends and replay an actual F19 scalar seed.
preflight="$(mktemp -d "$HOME/.F21b_source_preflight_XXXXXX")"
trap 'rm -rf "$preflight"' EXIT
tar -xzf "$HOME/F21_scripts_bundle.tar.gz" -C "$preflight"
PYTHONPATH="$preflight/scripts" python3 - \
    "$f18" "$f19" "$f19b" "$f19c" "$f19d" "$f20c" "$f20s" <<'PY'
import sys
from pathlib import Path
from zee_paper1_F21_stratified_wide_mass_mix_scan import (
    f20_source,verify,candidate,region,scalar_screen)
import numpy as np
paths=list(map(Path,sys.argv[1:]))
_,_,cohort=verify(*paths[:5])
pool,report=f20_source(paths[5],paths[6])
assert len(pool)==5075, "Unexpected validated F20 population"
assert len(cohort[1])==3, "Original physical F19 scalar cohort absent"
known=next(iter(cohort[1].values()))["scalar_original_F16_inputs"]
assert scalar_screen(known) is not None,"F21 source original physical BFB check failed"
rng=np.random.default_rng(21)
for stratum in (0,4,20,40,60,80,99):
    p=candidate(rng,stratum)
    assert p is not None and region(p)[0] is not None
print("F21B_PRE_SUBMIT_REAL_F18_F20_SOURCE_AND_WIDE_GENERATOR_PASS",
      "F20_rows",len(pool),"M2_SHELLS",5,flush=True)
PY
rm -rf "$preflight"
trap - EXIT
mkdir -p "$run/logs" "$eos"
cp "$HOME/F21_scripts_bundle.tar.gz" "$run/"
cp "$HOME/zee_paper1_F21_condor_worker.sh" "$run/F21_worker.sh"
chmod +x "$run/F21_worker.sh"
cp "$f18" "$run/F18.json"
cp "$f19" "$run/F19.json"
cp "$f19b" "$run/F19b.json"
cp "$f19c" "$run/F19c.json"
cp "$f19d" "$run/F19d.json"
cp "$f20c" "$run/F20scalar.csv"
cp "$f20s" "$run/F20summary.json"
(cd "$run";sha256sum F*.json F20scalar.csv F21_scripts_bundle.tar.gz F21_worker.sh > F21_SOURCE_SHA256.txt)
cat >"$run/F21b_wide_24shards.sub" <<EOF
universe = vanilla
executable = F21_worker.sh
arguments = \$(shard)
request_cpus = 2
request_memory = 12288MB
request_disk = 12000000KB
+MaxRuntime = 86400
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = F21_scripts_bundle.tar.gz,F18.json,F19.json,F19b.json,F19c.json,F19d.json,F20scalar.csv,F20summary.json
transfer_output_files = F21_result_shard_\$(shard).tar.gz
output_destination = root://eosuser.cern.ch/${eos}/
output = logs/F21_\$(ClusterId).\$(ProcId)_\$(shard).out
error = logs/F21_\$(ClusterId).\$(ProcId)_\$(shard).err
log = logs/F21_\$(ClusterId).log
queue shard from (
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
)
EOF
cd "$run"
condor_submit F21b_wide_24shards.sub
echo "F21B_SUBMITTED_WIDE_H2_2P5TEV_TANB_0P7_35 24_SHARDS"
echo "F21B_ARCHIVES $eos"
