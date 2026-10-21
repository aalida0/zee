#!/usr/bin/env bash
# Run from LOCAL Mathematica workstation, after AF F16 fixture transfer.
set -euo pipefail
cd "${ZEE_LOCAL_REPO:-$HOME/zee}"
: "${ZEE_F16_DIR:?Set ZEE_F16_DIR to an absolute transferred AF fixture directory}"
if [[ ! -f "$ZEE_F16_DIR/F16_three_exact_F13_Zee_SARAH_charged_vertices.m" ]]; then
  echo "F16_MISSING_EXACT_THREE_F13_FIXTURE" >&2
  exit 2
fi
if ! command -v math >/dev/null 2>&1; then
  echo "F16_LOCAL_MATHEMATICA_KERNEL_MISSING" >&2
  exit 3
fi
math -script scripts/zee_paper1_F16_SARAH_three_heavy_vertex_audit.m \
  2>&1 | tee "$ZEE_F16_DIR/F16_local_SARAH_console.log"
echo "F16_AUDIT_STATUS:"
cat "$ZEE_F16_DIR/F16_local_SARAH_vertex_status.txt"
if [[ "${ZEE_F16_EXPORT_UFO:-0}" == "1" ]]; then
  math -script scripts/zee_paper1_F16_SARAH_MakeUFO_after_vertex_gate.m \
    2>&1 | tee "$ZEE_F16_DIR/F16_local_MakeUFO_console.log"
fi
