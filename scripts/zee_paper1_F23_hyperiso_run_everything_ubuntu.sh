#!/usr/bin/env bash
# ONE integrated F23 real-physics run from Ubuntu with CERN F22 input recovery.
# No Condor, no extra scalar scan, and no low-fidelity quick proxies.
set -Eeuo pipefail
zee="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$HOME/zee_F22_frozen_benchmarks_20261025"
output="$HOME/zee_F23_hyperiso_157_20261025"
remote="aalida@lxplus.cern.ch:/afs/cern.ch/user/a/aalida/zee_F22_frozen_benchmarks_20261025"
for exe in python3 git cmake ninja g++ scp; do
    command -v "$exe" >/dev/null || {
       echo "F23_REQUIRED_EXECUTABLE_MISSING: $exe" >&2;exit 2; }
done
if command -v dpkg-query >/dev/null; then
    missing=()
    for dep in libgsl-dev libeigen3-dev libboost-dev libopenblas-dev liblapack-dev; do
        dpkg-query -W -f='${Status}' "$dep" 2>/dev/null | grep -qx 'install ok installed' ||
            missing+=("$dep")
    done
    if (( ${#missing[@]} )); then
        echo "F23_MISSING_UBUNTU_NATIVE_BUILD_DEPENDENCIES: ${missing[*]}" >&2
        echo "Install once: sudo apt-get install -y ${missing[*]} libboost-filesystem-dev libboost-system-dev libboost-thread-dev" >&2
        exit 2
    fi
fi
resume_args=()
if [[ -e "$output" ]]; then
    if [[ ! -f "$output/F23_input_source_sha256.json" ]] ||
       [[ -f "$output/F23_conditional_157_model_summary.json" ]]; then
        echo "F23_REFUSE_OVERWRITE_UNVERIFIED_OR_COMPLETED_RUN $output" >&2
        exit 2
    fi
    resume_args=(--resume)
    echo "F23_RESUME_EXISTING_SOURCE_VERIFIED_HYPERISO_BUILD $output"
fi
mkdir -p "$source_dir"
for entry in \
 F22_freeze_SHA256_manifest.json \
 F22_mass_stratified_priority_complex_fY_dossier_NOT_ALLOWED.json \
 F22_ALL_157_original_complex_fY_sources_NOT_FULL_ALLOWED.jsonl.gz; do
    if [[ ! -s "$source_dir/$entry" ]]; then
        echo "F23_TRANSFER_SOURCE_PINNED_F22 $entry"
        scp "$remote/$entry" "$source_dir/$entry"
    fi
done
echo "F23_ONE_LARGE_NATIVE_PHYSICS_CAMPAIGN_START 157_REAL_F22_ZEE_MODELS"
python3 "$zee/scripts/zee_paper1_F23_hyperiso_one_shot_integrated_157.py" \
 --repo "$zee" --f22-dir "$source_dir" --output "$output" "${resume_args[@]}"
