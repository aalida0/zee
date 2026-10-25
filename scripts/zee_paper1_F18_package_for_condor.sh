#!/usr/bin/env bash
# Package the exact validated F18 inputs + local MG5 + repository scripts
# once, to transfer them to an HTCondor submit node. Never package the large
# previous F18 output trees, and never alter original F16/F17f source.
set -euo pipefail
if [[ $# -ne 3 && $# -ne 4 ]]; then
  echo "Usage: $0 ORIGINAL_F16_DIR MG5_DIRECTORY EMPTY_PAYLOAD_DIR [COMPLETED_LOCAL_F18_CAMPAIGN]" >&2
  exit 2
fi
src="$(realpath "$1")"
mg5="$(realpath "$2")"
dest="$(realpath -m "$3")"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "$(basename "$mg5")" != MG5_aMC ]]; then
  echo "F18_CONDOR_REQUIRES_MG5_aMC_DIRECTORY_BASENAME $mg5" >&2;exit 2
fi
if [[ ! -f "$mg5/bin/mg5_aMC" ]]; then
  echo "F18_CONDOR_MG5_NOT_FOUND $mg5/bin/mg5_aMC" >&2; exit 2
fi
[[ ! -e "$dest" ]] || { echo "Refuse overwriting existing payload $dest" >&2;exit 2; }
required=(
  F16_three_exact_F13_Zee_input_reconstruction.json
  F17_three_F13_exact_complex_matrices_from_F16.json
  F16_ZeeTypeII_LO_UFO_EXPORTED_UNVALIDATED
  F17d_original_UFO_source_matched_TEST_CARDS_20261023T113206Z
  F17e_real_UFO_amplitude_gate_20261023T115044Z.json
  F17f_real_UFO_unitary_complex_CKM_20261023T120345Z
)
for item in "${required[@]}"; do
  [[ -e "$src/$item" ]] || { echo "F18_CONDOR_MISSING_SOURCE $src/$item" >&2;exit 2; }
done
mkdir -p "$dest"
echo "F18_CONDOR_PACK_SOURCE"
tar -czf "$dest/F18_source_bundle.tar.gz" -C "$src" "${required[@]}"
echo "F18_CONDOR_PACK_REPO_SCRIPTS"
tar -czf "$dest/F18_scripts_bundle.tar.gz" -C "$repo" scripts
echo "F18_CONDOR_PACK_MG5_INSTALLATION"
# Keep all MG5 source/compiler templates; discard only git metadata, caches,
# and user-generated heavy event samples that are not part of MG5 installation.
tar -czf "$dest/F18_mg5_bundle.tar.gz" -C "$mg5/.." \
  --exclude='*/.git' --exclude='*/__pycache__' --exclude='*/.pytest_cache' \
  "$(basename "$mg5")"
cp "$repo/scripts/zee_paper1_F18_condor_worker.sh" "$dest/F18_condor_worker.sh"
cp "$repo/scripts/zee_paper1_F18_merge_condor_results.py" "$dest/F18_merge_condor_results.py"
cp "$repo/scripts/zee_paper1_F18_prepare_lxplus_submission.sh" "$dest/F18_prepare_lxplus_submission.sh"
chmod +x "$dest/F18_condor_worker.sh"
if [[ $# -eq 4 ]]; then
  echo "F18_CONDOR_PRESERVE_PREVIOUSLY_COMPLETED_LOCAL_BENCHMARK"
  python3 "$repo/scripts/zee_paper1_F18_archive_local_success.py" \
    --local-campaign "$4" \
    --benchmark F13_heavy_0001330 \
    --output "$dest/F18_local_completed_F13_heavy_0001330.tar.gz"
  submit_name="F18_2remaining.sub"
else
  submit_name="F18_3cases.sub"
fi
cat >"$dest/$submit_name" <<'EOF'
universe = vanilla
executable = F18_condor_worker.sh
arguments = $(case)
request_cpus = 2
request_memory = 8192MB
request_disk = 25000000KB
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = F18_source_bundle.tar.gz,F18_scripts_bundle.tar.gz,F18_mg5_bundle.tar.gz
transfer_output_files = F18_result_$(case).tar.gz
output = logs/F18_$(ClusterId).$(ProcId)_$(case).out
error = logs/F18_$(ClusterId).$(ProcId)_$(case).err
log = logs/F18_$(ClusterId).log
EOF
if [[ "$submit_name" == "F18_2remaining.sub" ]]; then
  cat >>"$dest/$submit_name" <<'EOF'
queue case from (
F13_heavy_0000981
F13_heavy_0001003
)
EOF
else
  cat >>"$dest/$submit_name" <<'EOF'
queue case from (
F13_heavy_0001330
F13_heavy_0000981
F13_heavy_0001003
)
EOF
fi
mkdir -p "$dest/logs"
(
  cd "$dest"
  sha256sum F18_*bundle.tar.gz F18_condor_worker.sh F18_merge_condor_results.py F18_prepare_lxplus_submission.sh "$submit_name" \
    > F18_condor_payload_SHA256.txt
  if [[ -f F18_local_completed_F13_heavy_0001330.tar.gz ]]; then
    sha256sum F18_local_completed_F13_heavy_0001330.tar.gz >> F18_condor_payload_SHA256.txt
  fi
)
echo "F18_CONDOR_PACKAGE_READY $dest"
du -h "$dest/"*.tar.gz
echo "Next: rsync -avP $dest/ YOUR_CONDOR_SUBMIT_HOST:YOUR_DEST_DIR/"
echo "Then: cd YOUR_DEST_DIR && condor_submit $submit_name"
echo "After remaining jobs: python3 F18_merge_condor_results.py --results-dir . --output-dir F18_final"
