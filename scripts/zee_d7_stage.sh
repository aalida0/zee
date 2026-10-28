#!/usr/bin/env bash
# D7: source-locked Condor pilot staging, run on LXPLUS in clean Git checkout.
# Usage: bash scripts/zee_d7_stage.sh [output_dir]
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
cd "$repo"
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
    echo "D7_REFUSE_DIRTY_TRACKED_TREE" >&2
    exit 65
fi
if [[ $# -gt 0 ]]; then
    run="$1"
else
    run="$repo/validation/module9/local/d7_pilot"
fi
if [[ -e "$run" ]]; then
    echo "D7_REFUSE_OVERWRITE_EXISTING_BATCH_RUN: $run" >&2
    exit 66
fi
mkdir -p "$run"
python3 -m module9.d7_prepare \
  --seed module3/example.json \
  --output-dir "$run"
git archive --format=tar HEAD | gzip -n -c > "$run/scan_bundle.tar.gz"
cp module9/condor/worker.sh "$run/worker.sh"
cp module9/condor/d7_pilot.sub "$run/d7_pilot.sub"
chmod 700 "$run/worker.sh"
mkdir -p "$run/logs" "$run/results" "$run/status"
(cd "$run" && sha256sum scan_bundle.tar.gz > bundle.sha256)
git rev-parse HEAD > "$run/source_commit.txt"
echo "D7_STAGED_UNSUBMITTED $run"
echo "CERN: cd \"$run\" && condor_submit d7_pilot.sub"
echo "CERN: condor_q; condor_history"
