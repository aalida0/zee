#!/usr/bin/env bash
# Starts a REAL, persistent AF scalar+neutrino+partial-LFV feasibility scan.
# No physical Zee ALLOWED claim is emitted by this screening campaign.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -m py_compile \
  scripts/zee_paper1_florentino_feasibility_scan.py \
  tests/test_zee_paper1_florentino_feasibility_scan.py
python3 -m unittest discover -s tests \
  -p 'test_zee_paper1_florentino_feasibility_scan.py' -v
# Give every run a new source-pinned directory; never overwrite old physics.
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="${ZEE_PAPER1_OUT:-$ROOT/work/zee_paper1_florentino_pilot_$stamp}"
mkdir -p "$(dirname "$out")"
printf 'PAPER1_PHYSICS_CAMPAIGN_LAUNCH %s\n' "$out"
python3 -u scripts/zee_paper1_florentino_feasibility_scan.py \
  --output "$out" "$@" 2>&1 | tee "${out}_console.log"
printf 'PAPER1_CONDENSED_RESULT %s\n' "$out/summary.json"
