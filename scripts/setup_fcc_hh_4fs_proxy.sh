#!/usr/bin/env bash
# Create a fresh FCC-hh LO 4FS Type-II tbH± production PROXY.
# NOT the complete Zee model. Output must be in /home.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
case "$ROOT" in
  /data/*) echo "ERROR: MG5 must run from /home/aalida/zee, not /data" >&2; exit 2 ;;
esac
ENERGY_TEV=100
if [ "$#" -gt 0 ]; then ENERGY_TEV="$1"; fi
case "$ENERGY_TEV" in
  80|90|100) ;;
  *) echo "Usage: bash scripts/setup_fcc_hh_4fs_proxy.sh [80|90|100]" >&2; exit 2 ;;
esac
MODEL="$ROOT/models/2HDMtII_NLO"
[[ -f "$MODEL/particles.py" ]] || { echo "Missing $MODEL/particles.py" >&2; exit 2; }
if [[ -v MG5_BIN ]]; then
    MG5="$MG5_BIN"
else
    MG5="$(command -v mg5_aMC || true)"
fi
[[ -n "$MG5" && -f "$MG5" ]] || { echo "Set MG5_BIN=/absolute/path/to/mg5_aMC" >&2; exit 2; }
OUT="$ROOT/work/ZeeProductionProxy_4FS_$ENERGY_TEV"TeV
[[ ! -e "$OUT" ]] || { echo "Output exists; refusing overwrite: $OUT" >&2; exit 2; }
mkdir -p "$ROOT/work"
CARD="$ROOT/work/setup_$ENERGY_TEV"TeV_4fs.mg5
cat > "$CARD" <<EOF
set automatic_html_opening False
import model $MODEL
define p = g u d s c u~ d~ s~ c~
generate p p > t~ b h+ QCD=2 QED=1
add process p p > t b~ h- QCD=2 QED=1
output $OUT -f
EOF
echo "Generating 2HDM production proxy at sqrt(s)=$ENERGY_TEV TeV"
"$MG5" "$CARD" 2>&1 | tee "$ROOT/work/setup_$ENERGY_TEV"TeV_4fs.log
python3 "$ROOT/scripts/set_proxy_cards.py" "$OUT" --sqrt-s-tev "$ENERGY_TEV"
echo "Review cards; then cd $OUT and run ./bin/generate_events run_01 -f"
echo "ALWAYS multiply 2HDM LO rate by sin(gamma)^2 for the Zee H2 rate."
