#!/usr/bin/env bash
# MG5 diagram-generation smoke test for a NEW Zee-Type-II LO UFO.
# No integrations/events; not a physics or NLO validation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UFO="$ROOT/work/Zee_TypeII_LO_UFO"
if [ "$#" -gt 0 ]; then UFO="$1"; fi
case "$ROOT" in /data/*) echo "ABORT: work in /home, not /data" >&2; exit 2;; esac
if [[ ! -d "$UFO" ]]; then
  echo "ABORT: missing new LO UFO: $UFO" >&2; exit 2
fi
UFO="$(cd "$UFO" && pwd)"
python3 "$ROOT/scripts/gate7_validate_typeii_ufo.py" "$UFO" \
    --output "$ROOT/work/gate7_typeii_ufo_static.json"

if [[ -z "$(printenv MG5_BIN 2>/dev/null || true)" ]]; then
  MG5_BIN="/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/madgraph5amc/3.5.9-3xnfke/bin/mg5_aMC"
fi
[[ -f "$MG5_BIN" ]] || { echo "ABORT: MG5 executable missing: $MG5_BIN" >&2; exit 2; }
WORK="$ROOT/work/gate7_mg5_typeii_smoke"
[[ ! -e "$WORK" ]] || { echo "ABORT: output exists: $WORK" >&2; exit 2; }
mkdir -p "$WORK"
cat > "$WORK/01_associated.mg5" <<EOF
set automatic_html_opening False
import model $UFO
generate g g > t~ b H+ QCD=2 QED=1
add process g g > t b~ H- QCD=2 QED=1
output $WORK/Associated_4FS -f
EOF
cat > "$WORK/02_mixed_pair.mg5" <<EOF
set automatic_html_opening False
import model $UFO
generate u u~ > H+ h-
add process u u~ > H- h+
output $WORK/Mixed_DY -f
EOF
cat > "$WORK/03_decay.mg5" <<EOF
set automatic_html_opening False
import model $UFO
generate H+ > z h+
output $WORK/H2_to_Z_H1 -f
EOF

for card in "$WORK"/0*.mg5; do
   log="$(dirname "$card")/$(basename "$card" .mg5).log"
   echo "PROCESS-GATE: $card"
   "$MG5_BIN" "$card" 2>&1 | tee "$log"
   if ! grep -qE '[1-9][0-9]* processes? with [1-9][0-9]* diagrams' "$log"; then
       echo "ABORT: no positive diagram counts found in $log" >&2
       exit 3
   fi
done
echo "PASS: 4FS associated, mixed DY and H2->Z H1 diagrams generated."
echo "NOT CHECKED: matrix elements, widths, gauge identities, P2 mapping, NLO."
