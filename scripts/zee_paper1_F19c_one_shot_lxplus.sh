#!/usr/bin/env bash
# F19c exact three Zee scalar charge/CP-breaking vacuum witness search.
# Uses already source-verified F18/F19/F19b results, no MadWidth rerun.
set -Eeuo pipefail
if [[ $# -lt 5 || $# -gt 7 ]]; then
  echo "Usage: $0 F18_EOS_DIR F18_FINAL_JSON F19_SCALAR_JSON F19B_COMPLEX_JSON NEW_AFS_WORKDIR [MULTISTART=64] [MAXITER=350]" >&2
  exit 2
fi
eos="${1%/}";f18="$2";f19="$3";f19b="$4";work="${5%/}"
starts="${6:-64}";iters="${7:-350}"
[[ "$eos" == /eos/user/a/aalida/* ]] || {
  echo "F19C_EXPECT_USER_EOS_PATH $eos" >&2;exit 2; }
[[ "$work" == "$HOME"/* && "$work" != "$HOME" ]] || {
  echo "F19C_EXPECT_FRESH_AFS_HOME_WORKDIR $work" >&2;exit 2; }
[[ ! -e "$work" ]] || {
  echo "F19C_NEVER_OVERWRITE_EXISTING_WORKDIR $work" >&2;exit 2; }
for f in "$eos/F18_scripts_bundle.tar.gz" "$f18" "$f19" "$f19b"; do
  [[ -f "$f" ]] || { echo "F19C_REQUIRED_ORIGINAL_INPUT_MISSING $f" >&2;exit 2; }
done
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for script in zee_paper1_F19c_exact_three_vacuum_witness.py \
  zee_paper1_F19b_exact_F17f_neutrino_partial_LFV.py \
  zee_paper1_F19_integrated_scalar_EWPO_constraints.py; do
 [[ -f "$here/$script" ]] || {
    echo "F19C_REQUIRED_NEW_PYTHON_DRIVER_MISSING $here/$script" >&2;exit 2; }
done
python3 -c 'import numpy,scipy; print("F19C_NUMPY_SCIPY_PASS")'
mkdir -p "$work/original_backends"
tar -xzf "$eos/F18_scripts_bundle.tar.gz" -C "$work/original_backends"
for script in zee_gateC1_joined_uv_pilot.py \
  zee_gateC5_charge_breaking_vacuum_search.py \
  zee_section8_Q4_independent_dimensional_scalar_gate.py \
  zee_section8_Q4_independent_scalar_hessian_gate.py; do
 [[ -f "$work/original_backends/scripts/$script" ]] || {
    echo "F19C_ORIGINAL_SCALAR_BACKEND_MISSING $script" >&2;exit 2; }
done
echo "F19C_SOURCE_F18_SHA256 $(sha256sum "$f18")"
echo "F19C_SOURCE_F19_SHA256 $(sha256sum "$f19")"
echo "F19C_SOURCE_F19B_SHA256 $(sha256sum "$f19b")"
echo "F19C_DRIVER_SHA256 $(sha256sum "$here/zee_paper1_F19c_exact_three_vacuum_witness.py")"
(
 PYTHONPATH="$work/original_backends/scripts:$here" \
   python3 -u "$here/zee_paper1_F19c_exact_three_vacuum_witness.py" \
     --f18 "$f18" \
     --f19 "$f19" \
     --f19b "$f19b" \
     --output-dir "$work/F19c_results" \
     --multistart "$starts" \
     --maxiter "$iters"
) 2>&1 | tee "$work/F19c_run.log"
( cd "$work"; sha256sum F19c_results/* > F19c_results_SHA256.txt )
echo "F19C_FINISHED_VACUUM_WITNESS_NOT_GLOBAL_PROOF $work/F19c_results"
