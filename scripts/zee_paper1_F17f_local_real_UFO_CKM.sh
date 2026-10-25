#!/usr/bin/env bash
# Real numerical UFO CKM source gate; no MadWidth and no assumed full BR.
set -euo pipefail
cd "${ZEE_LOCAL_REPO:-$HOME/zee}"
: "${ZEE_F16_DIR:?Set exact transferred F16 source directory}"
f17d="${ZEE_F17D_DIR:-$ZEE_F16_DIR/F17d_original_UFO_source_matched_TEST_CARDS_20261023T113206Z}"
f17e="$ZEE_F16_DIR/F17e_real_UFO_amplitude_gate_20261023T115044Z.json"
[[ -f "$f17e" && -f "$f17d/summary.json" ]] || {
  echo "F17F_MISSING_COMPLETED_ORIGINAL_F17D_OR_F17E" >&2; exit 2;
}
out="$ZEE_F16_DIR/F17f_real_UFO_unitary_complex_CKM_$(date -u +%Y%m%dT%H%M%SZ)"
python3 -u scripts/zee_paper1_F17f_unitary_CKM_UFO_quark_gate.py \
 --f16-dir "$ZEE_F16_DIR" \
 --f17e-report "$f17e" \
 --f17d-dir "$f17d" \
 --output "$out"
echo "F17F_QUARK_VALIDATION_ONLY_COMPLEX_LEPTON_TOTALS_PENDING $out/report.json"
