#!/usr/bin/env bash
# One shot: stage real CERN F18-F19d records and four large F20 HTCondor shards.
# Expected on LXPLUS HOME: F20_scripts_bundle.tar.gz and F20_condor_worker.sh
set -Eeuo pipefail
eosbase=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024
run="$HOME/zee_F20_integrated_20261024"
eos="$eosbase/F20_4shards_20261024"
[[ ! -e "$run" ]] || { echo "F20_REFUSE_EXISTING_AFS_RUN_DIR $run" >&2;exit 2; }
[[ ! -e "$eos" ]] || { echo "F20_REFUSE_EXISTING_EOS_PRODUCTION_DIR $eos" >&2;exit 2; }
[[ -s "$HOME/F20_scripts_bundle.tar.gz" && -f "$HOME/zee_paper1_F20_condor_worker.sh" ]] || {
 echo "F20_LOCAL_SCRIPTS_ARCHIVE_OR_WORKER_MISSING" >&2;exit 2; }
f18="$HOME/zee_f18_lxplus_submit_20261024/F18_final_three_benchmarks/F18_CONDOR_three_source_verified.json"
f19="$HOME/zee_f19_scalar_ewpo_20261024/F19_results/F19_integrated_three_constraint_ledger_NOT_ALLOWED.json"
f19b="$HOME/zee_f19b_exact_neutrino_partial_LFV_20261024/F19b_results/F19b_exact_complex_neutrino_partial_LFV_NOT_ALLOWED.json"
f19c="$HOME/zee_f19c_three_vacuum_witness_64_20261024/F19c_results/F19c_three_vacuum_witnesses_NOT_GLOBAL.json"
f19d="$HOME/zee_f19d_analytic_LO_bsgamma_20261024/F19d_analytic_LO_three_source_matched_NOT_PRECISION.json"
# The exact F19d JSON filename must be resolved from its known producer.
f19d="$HOME/zee_f19d_analytic_LO_bsgamma_20261024/F19d_analytic_LO_three_source_matched_NOT_PRECISION.json"
if [[ ! -f "$f19d" ]]; then
  f19d="$HOME/zee_f19d_analytic_LO_bsgamma_20261024/F19d_analytic_LO_three_source_matched_NOT_PRECISION.json"
fi
for f in "$f18" "$f19" "$f19b" "$f19c" "$f19d"; do
  [[ -s "$f" ]] || { echo "F20_SOURCE_JSON_MISSING $f" >&2;exit 2; }
done
# Check source provenance BEFORE submission: no job queue wasted on bad hashes.
PYTHONPATH="/dev/null" python3 - "$f18" "$f19" "$f19b" "$f19c" "$f19d" <<'PY'
import sys,json,hashlib
files=sys.argv[1:];D=[json.load(open(x)) for x in files]
sha=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()
labels=('F18','F19','F19b','F19c')
assert all(D[4]['actual_CERN_F18_F19_F19b_F19c_source_SHA256'][label]==sha(f)
           for label,f in zip(labels,files[:4]))
assert len(D[4]['rows'])==9 and D[4]['status'].startswith('F19D_')
print('F20_PRE_SUBMIT_F18_F19C_SHA_AND_F19D_COMPLETE_PASS')
PY
mkdir -p "$run/logs" "$eos"
cp "$HOME/F20_scripts_bundle.tar.gz" "$run/F20_scripts_bundle.tar.gz"
cp "$HOME/zee_paper1_F20_condor_worker.sh" "$run/F20_condor_worker.sh"
chmod +x "$run/F20_condor_worker.sh"
cp "$f18" "$run/F18.json"
cp "$f19" "$run/F19.json"
cp "$f19b" "$run/F19b.json"
cp "$f19c" "$run/F19c.json"
cp "$f19d" "$run/F19d.json"
(
cd "$run"
sha256sum F*.json F20_scripts_bundle.tar.gz F20_condor_worker.sh >F20_input_manifest_SHA256.txt
)
# ROOT output destination uses EOSUSERS preferred write endpoint. Original
# source JSONs never need to be modified nor staged through an AF server.
cat >"$run/F20_4shards.sub" <<EOF
universe = vanilla
executable = F20_condor_worker.sh
arguments = \$(shard)
request_cpus = 2
request_memory = 12288MB
request_disk = 12000000KB
+MaxRuntime = 86400
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = F20_scripts_bundle.tar.gz,F18.json,F19.json,F19b.json,F19c.json,F19d.json
transfer_output_files = F20_result_shard_\$(shard).tar.gz
output_destination = root://eosuser.cern.ch//$eos/
output = logs/F20_\$(ClusterId).\$(ProcId)_\$(shard).out
error = logs/F20_\$(ClusterId).\$(ProcId)_\$(shard).err
log = logs/F20_\$(ClusterId).log
queue shard from (
0
1
2
3
)
EOF
echo "F20_INPUT_MANIFEST $run/F20_input_manifest_SHA256.txt"
echo "F20_RESULTS_EOS $eos"
cd "$run"
condor_submit F20_4shards.sub
echo "F20_LARGE_BATCH_SUBMITTED_EOS $eos"
echo "F20_CONDOR_STATUS_CMD condor_q $USER"
