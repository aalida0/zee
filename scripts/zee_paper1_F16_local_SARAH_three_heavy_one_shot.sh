#!/usr/bin/env bash
# Run from LOCAL Mathematica workstation, after AF F16 fixture transfer.
set -euo pipefail
cd "${ZEE_LOCAL_REPO:-$HOME/zee}"
: "${ZEE_F16_DIR:?Set ZEE_F16_DIR to an absolute transferred AF fixture directory}"
if [[ ! -f "$ZEE_F16_DIR/F16_three_exact_F13_Zee_SARAH_charged_vertices.m" ]]; then
  echo "F16_MISSING_EXACT_THREE_F13_FIXTURE" >&2
  exit 2
fi
python3 scripts/zee_paper1_F16_verify_AF_to_local_bundle.py --directory "$ZEE_F16_DIR"
python3 scripts/zee_paper1_F16_wolfram_syntax_lint.py \
  scripts/zee_paper1_F16_SARAH_three_heavy_vertex_audit.m \
  scripts/zee_paper1_F16_SARAH_MakeUFO_after_vertex_gate.m \
  scripts/zee_paper1_F16_SARAH_context_vevs.m \
  scripts/zee_paper1_F16_SARAH_context_vevs_selftest.m \
  scripts/zee_paper1_F16_strict_real_lepton_width_residual.m \
  scripts/zee_paper1_F16_strict_real_lepton_width_selftest.m
if ! command -v math >/dev/null 2>&1; then
  echo "F16_LOCAL_MATHEMATICA_KERNEL_MISSING" >&2
  exit 3
fi
# Exercise actual Wolfram replacement semantics for VEV symbols in
# Global, SARAH and Susyno contexts before loading the full SARAH model.
# Mathematica may return zero on nonfatal parse messages: inspect status too.
math -script scripts/zee_paper1_F16_SARAH_context_vevs_selftest.m \
  2>&1 | tee "$ZEE_F16_DIR/F16_local_VEV_context_selftest.log"
if ! grep -qx "F16_VEV_CONTEXT_SELFTEST_PASS" \
    "$ZEE_F16_DIR/F16_local_VEV_context_selftest.log"; then
  echo "F16_FAIL_CLOSED_PHYSICAL_VEV_CONTEXT_REGRESSION" >&2
  exit 11
fi
# Independently exercise exact Wolfram numeric behavior on F13
# "real + 0 I" leptonic widths. Old Max[complex,real] was symbolic and
# incorrectly let the physics audit claim PASS. This gate must print an
# explicit PASS even when Mathematica returns exit code zero on errors.
math -script scripts/zee_paper1_F16_strict_real_lepton_width_selftest.m \
  2>&1 | tee "$ZEE_F16_DIR/F16_local_lepton_width_selftest.log"
if ! grep -qx "F16_LEPTON_WIDTH_NUMERICAL_SELFTEST_PASS" \
   "$ZEE_F16_DIR/F16_local_lepton_width_selftest.log"; then
  echo "F16_FAIL_CLOSED_NONNUMERIC_CHARGED_LEPTON_WIDTH_REGRESSION" >&2
  exit 14
fi
# Prevent a stale PASS from an earlier run from hiding a Mathematica
# syntax error, which can otherwise produce a zero exit code.
rm -f "$ZEE_F16_DIR/F16_local_SARAH_vertex_status.txt"
math -script scripts/zee_paper1_F16_SARAH_three_heavy_vertex_audit.m \
  2>&1 | tee "$ZEE_F16_DIR/F16_local_SARAH_console.log"
if [[ ! -f "$ZEE_F16_DIR/F16_local_SARAH_vertex_status.txt" ]]; then
  echo "F16_FAIL_CLOSED_NO_MATHEMATICA_STATUS_OUTPUT" >&2
  exit 12
fi
echo "F16_AUDIT_STATUS:"
cat "$ZEE_F16_DIR/F16_local_SARAH_vertex_status.txt"
expected="F16_THREE_HEAVY_SARAH_MASS_GAUGE_CUBIC_COMPLEX_LEPTON_PASS_NOT_MADWIDTH"
if [[ "$(tr -d '\r\n' < "$ZEE_F16_DIR/F16_local_SARAH_vertex_status.txt")" != "$expected" ]]; then
  echo "F16_FAIL_CLOSED_SARAH_NUMERIC_VALIDATION_NOT_PASS" >&2
  exit 13
fi
if [[ "${ZEE_F16_EXPORT_UFO:-0}" == "1" ]]; then
  math -script scripts/zee_paper1_F16_SARAH_MakeUFO_after_vertex_gate.m \
    2>&1 | tee "$ZEE_F16_DIR/F16_local_MakeUFO_console.log"
fi
