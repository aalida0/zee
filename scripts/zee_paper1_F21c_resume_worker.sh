#!/usr/bin/env bash
# F21c recover actual 24 F21b wide scalar/EWPO-screened outputs:
# ZERO re-running initial 240,000 proposals, only f/Y LFV and C5.
set -Eeuo pipefail
shard="${1:?F21c needs shard 0..23}"
[[ "$shard" =~ ^([0-9]|1[0-9]|2[0-3])$ ]] || exit 2
root="$PWD"
mkdir -p "$root/backend" "$root/results"
tar -xzf "$root/F21_scripts_bundle.tar.gz" -C "$root/backend"
export PYTHONPATH="$root/backend/scripts"
python3 -c 'import numpy,scipy;print("F21C_NUMPY_SCIPY_READY",flush=True)'
ret=0
python3 -u "$root/backend/scripts/zee_paper1_F21c_resume_saved_scalar_archive.py" \
 --f18 "$root/F18.json" --f19 "$root/F19.json" \
 --f19b "$root/F19b.json" --f19c "$root/F19c.json" \
 --f19d "$root/F19d.json" \
 --f20-csv "$root/F20scalar.csv" --f20-summary "$root/F20summary.json" \
 --original-scalar-archive "$root/F21_result_shard_${shard}.tar.gz" \
 --output "$root/results/F21_shard_$shard" \
 --shard "$shard" --global-draws 6000 --local-draws 4000 \
 --fits 40 --trials 90 --optimize-seeds 2 --opt-evals 180 \
 --vacuum 12 --vacuum-starts 64 --vacuum-iters 350 \
 >"$root/F21c_shard_$shard.log" 2>&1 || ret=$?
printf 'F21C_SHARD_%s_EXIT_CODE=%s\n' "$shard" "$ret" >"$root/F21c_shard_$shard.exit"
echo "F21C_RESUME_END $shard EXIT $ret"
tail -n 22 "$root/F21c_shard_$shard.log" || true
members=("F21c_shard_$shard.exit" "F21c_shard_$shard.log")
if [[ -d "$root/results/F21_shard_$shard" ]]; then
  members+=("results/F21_shard_$shard")
fi
tar -czf "$root/F21c_resumed_shard_${shard}.tar.gz" "${members[@]}"
# Transport science errors to EOS as diagnostics; merger refuses invalid exit.
exit 0
