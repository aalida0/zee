#!/usr/bin/env bash
# Prepare F18 CERN LXPLUS submit-side files. Large immutable inputs and
# returned job archives remain in EOSUSER; do not submit from EOS/FUSE.
# Run ON lxplus after transferring the pre-existing local F18 2-job payload.
set -euo pipefail
if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo "Usage: $0 EOS_PAYLOAD_DIR NEW_LXPLUS_AFS_SUBMIT_DIR [CPUS=2] [RETRY_TAG]" >&2;exit 2
fi
eos="${1%/}"
submit="${2%/}"
ncores="${3:-2}"
tag="${4:-}"
case "$ncores" in
  1|2|4|8|16) ;;
  *) echo "F18_LXPLUS_CPUS_ALLOWED_1_2_4_8_16 $ncores" >&2;exit 2;;
esac
if [[ -n "$tag" && ! "$tag" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "F18_LXPLUS_INVALID_RETRY_TAG $tag" >&2;exit 2
fi
results="$eos/results"
[[ -z "$tag" ]] || results="$results/$tag"
memory_mb=$((8192+1024*ncores))
disk_kb=40000000
case "$eos" in
  /eos/user/a/aalida/*) ;;
  *) echo "F18_LXPLUS_EXPECT_USER_EOS_UNDER_/eos/user/a/aalida $eos" >&2;exit 2;;
esac
[[ "$eos" != *' '* && "$submit" != *' '* ]] || {
 echo "F18_LXPLUS_SPACES_UNSUPPORTED_IN_PATH" >&2;exit 2; }
case "$submit" in
  "$HOME"/*) ;;
  *) echo "F18_LXPLUS_SUBMIT_DIR_MUST_BE_UNDER_HOME_NOT_EOS" >&2;exit 2;;
esac
case "$submit" in
  /eos/*) echo "F18_LXPLUS_CANNOT_SUBMIT_FROM_EOS" >&2;exit 2;;
esac
if [[ -e "$submit" ]]; then
 echo "F18_LXPLUS_REFUSE_OVERWRITE_SUBMIT_FOLDER $submit" >&2;exit 2
fi
# For core operational security, originals and final width files are
# source-pinned. This verification is cheap relative to MadWidth.
for file in F18_source_bundle.tar.gz F18_scripts_bundle.tar.gz \
            F18_mg5_bundle.tar.gz F18_local_completed_F13_heavy_0001330.tar.gz \
            F18_condor_worker.sh F18_merge_condor_results.py \
            F18_condor_payload_SHA256.txt; do
  [[ -f "$eos/$file" ]] || { echo "F18_LXPLUS_MISSING_EOS_FILE $eos/$file" >&2;exit 2; }
done
(
  cd "$eos"
  sha256sum -c F18_condor_payload_SHA256.txt
)
mkdir -p "$results"
# The merger reads all three archives from ONE location. Preserve and
# hash-check the original successful 1330 alongside the two EOS outputs.
local_good="$eos/F18_local_completed_F13_heavy_0001330.tar.gz"
merged_local="$results/F18_local_completed_F13_heavy_0001330.tar.gz"
if [[ -e "$merged_local" ]]; then
  cmp -s "$local_good" "$merged_local" || {
    echo "F18_LXPLUS_EXISTING_LOCAL_SUCCESS_DIFFERS" >&2;exit 2; }
else
  cp -p "$local_good" "$merged_local"
fi
mkdir -p "$submit/logs"
cp "$eos/F18_condor_worker.sh" "$submit/F18_condor_worker.sh"
cp "$eos/F18_merge_condor_results.py" "$submit/F18_merge_condor_results.py"
chmod u+x "$submit/F18_condor_worker.sh"
# CERN Batch's supported XRootD file-transfer plug-in: input files come
# straight from EOS and only the final result archive is uploaded to EOS.
# Condor scheduler log stays in AFS; XRootD upload may also place
# stdout/stderr in EOS. Do not rely on stdout/err alone as physics proof.
cat > "$submit/F18_LXPLUS_2remaining.sub" <<EOF
universe = vanilla
executable = F18_condor_worker.sh
arguments = \$(case)
request_cpus = $ncores
request_memory = ${memory_mb}MB
request_disk = ${disk_kb}KB
environment = "F18_REQUEST_CPUS=$ncores"
+JobFlavour = "nextweek"
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = root://eosuser.cern.ch/$eos/F18_source_bundle.tar.gz,root://eosuser.cern.ch/$eos/F18_scripts_bundle.tar.gz,root://eosuser.cern.ch/$eos/F18_mg5_bundle.tar.gz
transfer_output_files = F18_result_\$(case).tar.gz
output_destination = root://eosuser.cern.ch/$results/
MY.XRDCP_CREATE_DIR = True
output = logs/F18_\$(ClusterId).\$(ProcId)_\$(case).out
error = logs/F18_\$(ClusterId).\$(ProcId)_\$(case).err
log = logs/F18_\$(ClusterId).log
queue case from (
F13_heavy_0000981
F13_heavy_0001003
)
EOF
cat > "$submit/F18_LXPLUS_storage_paths.txt" <<EOF
ORIGINAL_EOS_PAYLOAD=$eos
ORIGINAL_LOCAL_COMPLETED=$eos/F18_local_completed_F13_heavy_0001330.tar.gz
BATCH_RETURNED_ARCHIVES=$results/
SUBMIT_FILE=$submit/F18_LXPLUS_2remaining.sub
EOF
echo "F18_LXPLUS_SUBMIT_READY $submit/F18_LXPLUS_2remaining.sub"
echo "F18_LXPLUS_EOS_RESULTS $results"
echo "F18_LXPLUS_MADWIDTH_CPUS $ncores"
echo "F18_LXPLUS_MADWIDTH_REQUEST_MEMORY_MB $memory_mb"
echo "F18_LXPLUS_RUN_NEXT cd $submit '&&' condor_submit F18_LXPLUS_2remaining.sub"
echo "F18_LXPLUS_VERIFY_AFTER_JOBS ls -lh $results/F18_result_*.tar.gz"
echo "F18_LXPLUS_MERGE_AFTER_JOBS python3 $submit/F18_merge_condor_results.py --results-dir $results --output-dir $submit/F18_final_three_benchmarks"
