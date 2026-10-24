#!/usr/bin/env bash
# F17 local actual SARAH UFO and source-pinned F13 scalar/complex matrices.
# Does not generate a full MadWidth parameter card.
set -euo pipefail
cd "${ZEE_LOCAL_REPO:-$HOME/zee}"
: "${ZEE_F16_DIR:?Set ZEE_F16_DIR to original transferred F16 directory}"
[[ -f "$ZEE_F16_DIR/F16_local_SARAH_vertex_status.txt" ]] || {
 echo "F17_STOP_SOURCE_F16_VERTEX_GATE_NOT_PRESENT" >&2; exit 2;
}
[[ -d "$ZEE_F16_DIR/F16_ZeeTypeII_LO_UFO_EXPORTED_UNVALIDATED" ]] || {
 echo "F17_STOP_ORIGINAL_SARAH_UFO_MISSING" >&2; exit 3;
}
python3 scripts/zee_paper1_F16_verify_AF_to_local_bundle.py --directory "$ZEE_F16_DIR"
python3 scripts/zee_paper1_F16_wolfram_syntax_lint.py \
 scripts/zee_paper1_F17_exact_complex_F16_json.m \
 scripts/zee_paper1_F17_exact_complex_json_helpers.m \
 scripts/zee_paper1_F17_complex_json_selftest.m
if ! command -v math >/dev/null 2>&1; then
 echo "F17_LOCAL_MATHEMATICA_KERNEL_MISSING" >&2; exit 7
fi
# Test the SAME helper used by the exporter in a real Mathematica kernel.
math -script scripts/zee_paper1_F17_complex_json_selftest.m \
 2>&1 | tee "$ZEE_F16_DIR/F17_complex_json_selftest.log"
if ! grep -qx 'F17_COMPLEX_MATRIX_JSON_SELFTEST_PASS' \
   "$ZEE_F16_DIR/F17_complex_json_selftest.log"; then
 echo "F17_FAIL_CLOSED_COMPLEX_JSON_MATHEMATICA_SELFTEST" >&2; exit 8
fi
source="$ZEE_F16_DIR/F17_three_F13_exact_complex_matrices_from_F16.json"
# The earlier failed Export may have left an invalid generated F17 file.
# Preserve it under a quarantined filename; do not touch any F16 source.
if [[ -f "$source" ]] && \
   ! python3 scripts/zee_paper1_F17_verify_complex_json.py "$source"; then
 broken="$source.invalid_$(date -u +%Y%m%dT%H%M%SZ)_$"
 mv -- "$source" "$broken"
 echo "F17_QUARANTINED_INVALID_GENERATED_JSON $broken"
fi
if [[ ! -f "$source" ]]; then
 echo "F17_EXPORTING_ORIGINAL_COMPLEX_F13_MATRIX_INPUTS"
 math -script scripts/zee_paper1_F17_exact_complex_F16_json.m \
  2>&1 | tee "$ZEE_F16_DIR/F17_original_complex_matrix_export.log"
 if ! grep -q '^F17_COMPLEX_SOURCE_EXPORT_OK ' \
  "$ZEE_F16_DIR/F17_original_complex_matrix_export.log"; then
  echo "F17_FAIL_MATHEMATICA_EXACT_COMPLEX_SOURCE_EXPORT" >&2; exit 4
 fi
fi
python3 scripts/zee_paper1_F17_verify_complex_json.py "$source"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="$ZEE_F16_DIR/F17_original_SARAH_UFO_inventory_$timestamp"
python3 -u scripts/zee_paper1_F17_inspect_real_SARAH_UFO.py \
 --f16-dir "$ZEE_F16_DIR" --output "$out"
echo "F17_SOURCE_PINNED_UFO_INSPECTION_DIR $out"
