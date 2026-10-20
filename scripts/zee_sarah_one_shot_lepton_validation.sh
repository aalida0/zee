#!/usr/bin/env bash
# Single-entry consolidated ZeeTypeII tree-level lepton gate.
# Do NOT interpret a PASS as neutrino-loop, LFV or experimental validation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p work/sarah_zee

echo "ZEE_INTEGRATED_GATE_BEGIN"
python3 -m unittest discover -s tests -p 'test_zee_sarah_source.py' -v
python3 scripts/zee_sarah_gate6_fixture.py

# math -script writes an explicit status and exits nonzero on gate failure.
# pipefail propagates Mathematica failures through tee.
math -script scripts/zee_sarah_integrated_lepton_validation.m \
  2>&1 | tee work/sarah_zee/integrated_lepton_console.log

echo "ZEE_INTEGRATED_GATE_RESULT"
cat work/sarah_zee/integrated_lepton_status.txt
echo "ZEE_INTEGRATED_GATE_DETAILS work/sarah_zee/integrated_lepton_residuals.txt"
