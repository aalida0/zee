#!/usr/bin/env bash
# Source-pinned numerical diagnostic on ORIGINAL SARAH UFO and all 3 F13 cards.
# Does NOT trigger MadWidth or promote physical parameter cards.
set -euo pipefail
cd "${ZEE_LOCAL_REPO:-$HOME/zee}"
: "${ZEE_F16_DIR:?Set ZEE_F16_DIR to original F16 exact three-case source directory}"
f17="$ZEE_F16_DIR/F17_original_SARAH_UFO_inventory_20261023T085545Z/summary.json"
f17c="$ZEE_F16_DIR/F17c_real_UFO_results_20261023T100447Z.json"
f17d="${ZEE_F17D_DIR:-$ZEE_F16_DIR/F17d_original_UFO_source_matched_TEST_CARDS_20261023T113206Z}"
[[ -f "$f17" && -f "$f17c" && -f "$f17d/summary.json" ]] || {
 echo "F17E_MISSING_ACTUAL_SOURCE_F17_F17C_F17D" >&2; exit 2;
}
result="$ZEE_F16_DIR/F17e_real_UFO_amplitude_gate_$(date -u +%Y%m%dT%H%M%SZ).json"
python3 -u scripts/zee_paper1_F17e_real_UFO_amplitude_gate.py \
 --f16-dir "$ZEE_F16_DIR" \
 --f17-report "$f17" \
 --f17c-report "$f17c" \
 --f17d-dir "$f17d" \
 --output "$result"
echo "F17E_SOURCE_PINNED_AMPLITUDE_DIAGNOSTIC_NOT_MADWIDTH $result"
