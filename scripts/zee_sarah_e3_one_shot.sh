#!/usr/bin/env bash
# ONE combined Chen/E3 <-> SARAH flavor, width and radiative kernel gate.
# This does NOT generate SARAH one-loop self energies or classify 309 E3 points.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p work/sarah_zee
echo "ZEE_E3_ONE_SHOT_BEGIN"
python3 -m unittest discover -s tests -p 'test_zee_sarah_source.py' -v
python3 scripts/zee_sarah_e3_convention_fixture.py
math -script scripts/zee_sarah_e3_integrated_validation.m \
  2>&1 | tee work/sarah_zee/e3_integrated_console.log
echo "ZEE_E3_ONE_SHOT_STATUS"
cat work/sarah_zee/e3_integrated_status.txt
echo "ZEE_E3_ONE_SHOT_RESIDUALS work/sarah_zee/e3_integrated_residuals.txt"
