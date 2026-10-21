#!/usr/bin/env bash
# ONE integrated major-stage E3 -> SARAH full-loop test entry point.
# Reuses prior 162-vertex E3/B3 kernel gate, then calls SARAH's OWN
# CalcLoopCorrections[EWSB] for an independent diagram inventory.
# A topology-extraction status is not a numerical Majorana mass PASS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p work/sarah_zee
echo "ZEE_E3_SELFENERGY_MAJOR_GATE_BEGIN"
# Mark this invocation before the prerequisite Python tests run. A failing
# prerequisite must never leave an older loop result looking current.
printf '%s\n' 'SELFENERGY_STAGE_NOT_STARTED' \
  > work/sarah_zee/e3_sarah_selfenergy_status.txt
bash scripts/zee_sarah_e3_one_shot.sh
math -script scripts/zee_sarah_e3_independent_selfenergy_audit.m \
    2>&1 | tee work/sarah_zee/e3_independent_selfenergy_console.log
echo "ZEE_E3_SELFENERGY_MAJOR_GATE_RESULT"
cat work/sarah_zee/e3_sarah_selfenergy_status.txt
echo "ZEE_E3_SELFENERGY_MAJOR_GATE_RAW work/sarah_zee/e3_sarah_selfenergy_neutrino_raw.txt"
echo "ZEE_E3_SELFENERGY_MAJOR_GATE_INVENTORY work/sarah_zee/e3_sarah_selfenergy_inventory.txt"
# Controlled second independent SARAH run in a temporary model namespace.
# The production ZeeTypeII sources are not modified. Both runs belong
# to ONE A/B physics-stage acceptance workflow.
echo "ZEE_E3_MAJORANA_AB_STAGE_BEGIN"
printf '%s\n' 'MAJORANA_AB_STAGE_NOT_STARTED' \
    > work/sarah_zee/e3_majorana_ab_status.txt
python3 scripts/zee_sarah_majorana_spinor_variant.py
math -script scripts/zee_sarah_e3_majorana_ab_validation.m \
    2>&1 | tee work/sarah_zee/e3_majorana_ab_console.log
echo "ZEE_E3_MAJORANA_AB_STAGE_RESULT"
cat work/sarah_zee/e3_majorana_ab_status.txt
echo "ZEE_E3_MAJORANA_AB_SIGMA_FILE work/sarah_zee/e3_majorana_ab_sigma.txt"
