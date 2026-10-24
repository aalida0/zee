#!/usr/bin/env bash
# F16 AF: source-pinned exact F13 complex f/Y + scalar mass/cubics to SARAH.
# Local Mathematica vertex calculation is a SEPARATE actual measurement.
set -euo pipefail
cd /home/aalida/zee
python3 -m unittest discover -s tests \
 -p 'test_zee_paper1_F16_exact_SARAH_three_width_handoff.py' -v
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="$PWD/work/zee_paper1_F16_exact_SARAH_three_heavy_$stamp"
python3 -u scripts/zee_paper1_F16_exact_F13_SARAH_vertex_fixtures.py \
 --f13-dir "$PWD/work/zee_paper1_F13_heavy_final_20261021T125623Z" \
 --f14-dir "$PWD/work/zee_paper1_F14_LHCHXSWG_13TeV_production_20261021T133239Z" \
 --output "$out" "$@"
echo "F16_TRANSFER_FROM_AF_TO_LOCAL $out"
echo "F16_LOCAL_SARAH_CMD: ZEE_F16_DIR=/absolute/transferred/path math -script scripts/zee_paper1_F16_SARAH_three_heavy_vertex_audit.m"
