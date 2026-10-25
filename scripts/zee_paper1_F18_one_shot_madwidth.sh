#!/usr/bin/env bash
# F18: one real MadGraph/MadWidth campaign, all three source-validated
# ZeeTypeII physical CKM/complex lepton cards, 2-body bootstrap then
# 2+3-body decays. All output is model LO, NOT an allowed-point claim.
set -euo pipefail
cd "${ZEE_LOCAL_REPO:-$HOME/zee}"
: "${ZEE_F16_DIR:?Set ZEE_F16_DIR to the original F16 source directory}"
d="$ZEE_F16_DIR"
f17d="${ZEE_F17D_DIR:-$d/F17d_original_UFO_source_matched_TEST_CARDS_20261023T113206Z}"
f17e="${ZEE_F17E_REPORT:-$d/F17e_real_UFO_amplitude_gate_20261023T115044Z.json}"
f17f="${ZEE_F17F_DIR:-$d/F17f_real_UFO_unitary_complex_CKM_20261023T120345Z}"
[[ -f "$f17d/summary.json" && -f "$f17e" && -f "$f17f/report.json" ]] || {
 echo "F18_ORIGINAL_REAL_F17D_F17E_F17F_SOURCE_MISSING" >&2; exit 2; }
mkdir -p "$d"
out="$d/F18_MadWidth_exact_three_$(date -u +%Y%m%dT%H%M%SZ)"
args=(--f16-dir "$d" --f17d-dir "$f17d" --f17e-report "$f17e"
      --f17f-dir "$f17f" --output "$out" --continue-after-failure)
if [[ -n "${ZEE_MG5_BIN:-}" ]]; then
 args+=(--mg5-bin "$ZEE_MG5_BIN")
fi
if [[ -n "${ZEE_F14_CSV:-}" ]]; then
 args+=(--f14-csv "$ZEE_F14_CSV")
fi
python3 -u scripts/zee_paper1_F18_complete_madwidth_campaign.py "${args[@]}"
echo "F18_3_CASE_MODEL_LO_REPORT $out/summary.json"
