#!/usr/bin/env bash
# Production-rate-only proxy. This is NOT a two-charged-Higgs Zee UFO.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="$ROOT/models/2HDMtII_NLO"
OUT="$ROOT/work/ZeeProductionProxy_4FS_14TeV"
if [[ ! -f "$MODEL/particles.py" ]]; then
  echo "ERROR: place the extracted 2HDMtII_NLO UFO in $MODEL" >&2; exit 2
fi
MG5="${MG5_BIN:-$(command -v mg5_aMC || true)}"
if [[ -z "$MG5" || ! -f "$MG5" ]]; then
  echo "ERROR: MG5_BIN=/path/to/bin/mg5_aMC bash scripts/setup_4fs.sh" >&2; exit 2
fi
mkdir -p "$ROOT/work"
if [[ -e "$OUT" ]]; then
  echo "ERROR: process output already exists: $OUT; refusing to overwrite." >&2; exit 2
fi
CARD="$ROOT/work/setup_4fs.mg5"
cat > "$CARD" <<EOF
set automatic_html_opening False
import model $MODEL
define p = g u d s c u~ d~ s~ c~
generate p p > t~ b h+ QCD=2 QED=1
add process p p > t b~ h- QCD=2 QED=1
output $OUT -f
EOF
echo "Generating 2HDM production PROXY (not full Zee model): $OUT"
"$MG5" "$CARD" 2>&1 | tee "$ROOT/work/setup_4fs.log"
python3 "$ROOT/scripts/set_proxy_cards.py" "$OUT"
echo "Review Cards/*.dat before running ./bin/generate_events run_01 -f"
