#!/usr/bin/env bash
# F21: six independently stratified broad Zee mass/mixing shards.
set -Eeuo pipefail
shard="${1:?Provide shard 0..5}"
[[ "$shard" =~ ^[0-5]$ ]] || exit 2
root="$PWD"
mkdir -p "$root/backend" "$root/results"
tar -xzf "$root/F21_scripts_bundle.tar.gz" -C "$root/backend"
export PYTHONPATH="$root/backend/scripts"
python3 -c 'import numpy,scipy;print("F21_CERN_SCIENTIFIC_BACKENDS_IMPORTED")'
ret=0
python3 -u "$root/backend/scripts/zee_paper1_F21_stratified_wide_mass_mix_scan.py" \
 --f18 "$root/F18.json" --f19 "$root/F19.json" \
 --f19b "$root/F19b.json" --f19c "$root/F19c.json" \
 --f19d "$root/F19d.json" \
 --f20-csv "$root/F20scalar.csv" --f20-summary "$root/F20summary.json" \
 --output "$root/results/F21_shard_$shard" \
 --shard "$shard" --global-draws 6000 --local-draws 4000 \
 --fits 40 --trials 90 --optimize-seeds 2 --opt-evals 180 \
 --vacuum 12 --vacuum-starts 64 --vacuum-iters 350 \
 >"$root/F21_shard_$shard.log" 2>&1 || ret=$?
printf 'F21_SHARD_%s_EXIT_CODE=%s\n' "$shard" "$ret" >"$root/F21_shard_$shard.exit"
echo "F21_SHARD_END $shard EXIT $ret"
tail -n 24 "$root/F21_shard_$shard.log" || true
tar -czf "$root/F21_result_shard_${shard}.tar.gz" \
  "F21_shard_$shard.exit" "F21_shard_$shard.log" "results/F21_shard_$shard"
exit 0
