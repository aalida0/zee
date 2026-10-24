#!/usr/bin/env bash
# F19 real scalar/oblique screen on the completed three F18 benchmarks.
# CERN LXPLUS: source/repo archive remains on EOSUSER, tiny numerical
# Gate6/A1H scripts are unpacked to AFS, results written to new AFS folder.
set -Eeuo pipefail
if [[ $# -ne 3 ]]; then
  echo "Usage: $0 EOS_F18_PAYLOAD_DIR EXACT_F18_MERGED_JSON NEW_F19_AFS_WORKDIR" >&2
  exit 2
fi
eos="$1"
eos="$(realpath "$eos")"
f18="$(realpath "$2")"
work="$(realpath -m "$3")"
[[ "$eos" == /eos/user/a/aalida/* ]] || {
  echo "F19_REQUIRE_ORIGINAL_AALIDA_EOS_F18_PAYLOAD" >&2;exit 2; }
[[ "$work" == "$HOME"/* && "$work" != /eos/* ]] || {
  echo "F19_REQUIRE_NEW_AFS_WORKDIR" >&2;exit 2; }
[[ ! -e "$work" ]] || {
  echo "F19_REFUSE_OVERWRITE_PRIOR_RUN $work" >&2;exit 2; }
[[ -f "$eos/F18_scripts_bundle.tar.gz" ]] || {
  echo "F19_MISSING_ORIGINAL_REPOSITORY_SCRIPTS_ARCHIVE" >&2;exit 2; }
[[ -f "$eos/F18_source_bundle.tar.gz" ]] || {
  echo "F19_MISSING_ORIGINAL_F16_F17F_MODEL_SOURCE_ARCHIVE" >&2;exit 2; }
[[ -f "$f18" ]] || {
  echo "F19_MISSING_COMPLETED_F18_FINAL_MERGED_RESULTS" >&2;exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"
driver="$here/zee_paper1_F19_integrated_scalar_EWPO_constraints.py"
[[ -f "$driver" ]] || {
  echo "F19_DRIVER_MISSING_NEAR_LAUNCHER $driver" >&2;exit 2; }
command -v python3 >/dev/null || { echo "F19_PYTHON_MISSING" >&2;exit 2; }
python3 -c 'import numpy, scipy; print("F19_NUMPY_SCIPY_AVAILABLE")'
mkdir -p "$work/backend"
tar -xzf "$eos/F18_scripts_bundle.tar.gz" -C "$work/backend"
[[ -f "$work/backend/scripts/gate6_benchmark.py" ]] || {
  echo "F19_ORIGINAL_GATE6_BACKEND_NOT_IN_EOS_BUNDLE" >&2;exit 2; }
[[ -f "$work/backend/scripts/gateA1h_correlated_stu_ewpo.py" ]] || {
  echo "F19_ORIGINAL_STU_BACKEND_NOT_IN_EOS_BUNDLE" >&2;exit 2; }
echo "F19_SOURCE_SHA256 $(sha256sum "$eos/F18_source_bundle.tar.gz")"
echo "F19_F18_FINAL_SHA256 $(sha256sum "$f18")"
echo "F19_LAUNCHER_SHA256 $(sha256sum "$0")"
echo "F19_DRIVER_SHA256 $(sha256sum "$driver")"
(
  PYTHONPATH="$work/backend/scripts" \
    python3 -u "$driver" \
      --f18-merged "$f18" \
      --f16-source-bundle "$eos/F18_source_bundle.tar.gz" \
      --output-dir "$work/F19_results" \
      --quadrature-nodes 160
) 2>&1 | tee "$work/F19_run.log"
(
 cd "$work"
 sha256sum F19_results/* > F19_final_SHA256.txt
)
echo "F19_COMPLETED_SOURCE_SCREENED_NOT_FULL_ALLOWED $work/F19_results"
