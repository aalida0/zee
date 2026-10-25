#!/usr/bin/env bash
# Final F13 source-pinned P1 heavy mass flavor-guided, neutrino and LFV pilot.
set -euo pipefail
cd /home/aalida/zee
python3 -m py_compile scripts/zee_paper1_F13_heavy_P1_seeds.py scripts/zee_paper1_F13_heavy_flavor_aware_final_scan.py
python3 -m unittest discover -s tests -p 'test_zee_paper1_F13_heavy_flavor_aware_final_scan.py' -v
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="/home/aalida/zee/work/zee_paper1_F13_heavy_final_$stamp"
echo "F13_HEAVY_REAL_START $out"
python3 -u scripts/zee_paper1_F13_heavy_flavor_aware_final_scan.py --output "$out" "$@" 2>&1 | tee "${out}_console.log"
echo "F13_FINAL_RESULTS $out/summary.json"
