#!/usr/bin/env bash
# F19b exact F17f complex-neutrino + partial LFV audit on CERN LXPLUS.
# No need for Condor, MadGraph, or repackaging EOS source archives.
set -Eeuo pipefail
if [[ $# -ne 4 ]]; then
  echo "Usage: $0 F18_EOS_DIR F18_MERGED_JSON F19_SCALAR_LEDGER NEW_AFS_F19B_RUN" >&2
  exit 2
fi
eos="${1%/}"
f18="$2";f19="$3";work="${4%/}"
[[ "$eos" == /eos/user/a/aalida/* ]] || {
 echo "F19B_EOS_MUST_BE_USER_AALIDA $eos" >&2;exit 2; }
[[ "$work" == "$HOME"/* ]] || {
 echo "F19B_RUN_MUST_BE_IN_AFS_HOME $work" >&2;exit 2; }
for file in "$eos/F18_source_bundle.tar.gz" "$eos/F18_scripts_bundle.tar.gz" "$f18" "$f19"; do
  [[ -f "$file" ]] || { echo "F19B_REQUIRED_SOURCE_MISSING $file" >&2;exit 2; }
done
[[ ! -e "$work" ]] || {
 echo "F19B_REFUSE_OVERWRITE_EXISTING_WORKDIR $work" >&2;exit 2; }
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
driver="$here/zee_paper1_F19b_exact_F17f_neutrino_partial_LFV.py"
[[ -f "$driver" ]] || { echo "F19B_NEW_DRIVER_MISSING $driver" >&2;exit 2; }
python3 -c 'import numpy,scipy; print("F19B_NUMPY_SCIPY_PASS")'
mkdir -p "$work/original_backends"
tar -xzf "$eos/F18_scripts_bundle.tar.gz" -C "$work/original_backends"
for dependency in gateA1b_hierarchical_no_seed.py zee_barr_zee_fermion_dipoles.py zee_gateD4_W_photon_barr_zee_27.py gateB2_zee_neutrino_family_scan.py; do
 [[ -f "$work/original_backends/scripts/$dependency" ]] || {
 echo "F19B_ORIGINAL_LFV_BACKEND_MISSING $dependency" >&2;exit 2; }
done
echo "F19B_CERN_ACTUAL_COMPLEX_SOURCE_SHA256 $(sha256sum "$eos/F18_source_bundle.tar.gz")"
echo "F19B_PREDECESSOR_F19_LEDGER_SHA256 $(sha256sum "$f19")"
echo "F19B_NEW_DRIVER_SHA256 $(sha256sum "$driver")"
(
  PYTHONPATH="$work/original_backends/scripts:$here" \
  python3 -u "$driver" \
    --f19-ledger "$f19" \
    --f18-merged "$f18" \
    --f16-source-bundle "$eos/F18_source_bundle.tar.gz" \
    --output-dir "$work/F19b_results"
) 2>&1 | tee "$work/F19b_run.log"
( cd "$work"; sha256sum F19b_results/* > F19b_outputs_SHA256.txt )
echo "F19B_ACTUAL_PARTIAL_LFV_COMPLETE_NOT_FULL_MODEL_ALLOWED $work/F19b_results"
