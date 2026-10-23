#!/usr/bin/env bash
# F17d: real original exported SARAH UFO, exact three F13 F16/F17 inputs.
# Emits PREVALIDATION SLHA only: CKM=I test basis, never MadWidth.
set -euo pipefail
cd "${ZEE_LOCAL_REPO:-$HOME/zee}"
: "${ZEE_F16_DIR:?Export ZEE_F16_DIR for the transferred original F16 source}"
source_dir="$ZEE_F16_DIR"
f17="$source_dir/F17_original_SARAH_UFO_inventory_20261023T085545Z"
f17c="$source_dir/F17c_real_UFO_results_20261023T100447Z.json"
[[ -f "$f17/summary.json" && -f "$f17/F17_UFO_external_parameters.csv" && -f "$f17c" ]] || {
    echo "F17D_REQUIRED_ORIGINAL_F17_AND_F17C_REPORTS_MISSING" >&2; exit 2;
}
out="$source_dir/F17d_original_UFO_source_matched_TEST_CARDS_$(date -u +%Y%m%dT%H%M%SZ)"
python3 -u scripts/zee_paper1_F17d_source_matched_prevalidation_cards.py \
  --f16-dir "$source_dir" \
  --f17-report "$f17/summary.json" \
  --f17c-report "$f17c" \
  --external-csv "$f17/F17_UFO_external_parameters.csv" \
  --output "$out"
echo "F17D_ONLY_TEST_CARDS_NOT_MADWIDTH $out"
