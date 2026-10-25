#!/usr/bin/env bash
# F20 four-shard HTCondor worker; no AF needed, no MadWidth rerun.
set -Eeuo pipefail
shard="${1:?F20 requires shard index 0..3}"
[[ "$shard" =~ ^[0-3]$ ]] || exit 2
job="$PWD"
mkdir -p "$job/backend" "$job/physics_results"
cd "$job/backend"
tar -xzf "$job/F20_scripts_bundle.tar.gz"
export PYTHONPATH="$job/backend/scripts"
cd "$job"
python3 -c 'import numpy,scipy; print("F20_WORKER_NUMPY_SCIPY_READY",flush=True)'
code=0
python3 -u "$job/backend/scripts/zee_paper1_F20_integrated_large_campaign.py" \
  --f18 "$job/F18.json" --f19 "$job/F19.json" \
  --f19b "$job/F19b.json" --f19c "$job/F19c.json" \
  --f19d "$job/F19d.json" \
  --output "$job/physics_results/F20_shard_$shard" \
  --shard "$shard" \
  --steps 5000 --chains 8 --quad 64 \
  --fits 30 --trials 90 --optimize-seeds 2 --opt-evals 180 \
  --vacuum 12 --vacuum-starts 64 --vacuum-iters 350 \
  >"$job/F20_shard_$shard.log" 2>&1 || code=$?
printf 'F20_SHARD_%s_EXIT_CODE=%s\n' "$shard" "$code" >"$job/F20_shard_$shard.exit"
echo "F20_SHARD_END shard=$shard return=$code"
tail -n 30 "$job/F20_shard_$shard.log" || true
tar -czf "$job/F20_result_shard_${shard}.tar.gz" \
  "F20_shard_$shard.exit" "F20_shard_$shard.log" "physics_results"
[[ "$code" == 0 ]] || echo "F20_SHARD_FAILED_DIAGNOSTIC_ARCHIVED shard=$shard code=$code"
# The archive must transfer even on a numerical issue. Merger is fail-closed.
exit 0
