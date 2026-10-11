#!/usr/bin/env bash
# Gate 7D: compute matched charged-Higgs LO 2-body widths with MadWidth.
# Diagnostic Zee-Type-II test limit (f_ab=0), NOT physical neutrino masses.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UFO="$ROOT/work/Zee_TypeII_LO_UFO"
CARD="$ROOT/work/gate7_typeii_diagnostic_param_card.dat"
WORK="$ROOT/work/gate7_madwidth"
MG5_DEFAULT="/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/madgraph5amc/3.5.9-3xnfke/bin/mg5_aMC"
MG5_EXEC="$(printenv MG5_BIN 2>/dev/null || true)"
if [[ -z "$MG5_EXEC" ]]; then MG5_EXEC="$MG5_DEFAULT"; fi

if [[ ! -f "$UFO/vertices.py" || ! -f "$CARD" || ! -f "$MG5_EXEC" ]]; then
    echo "ERROR: required UFO, param card or MG5 executable missing." >&2
    exit 2
fi
if [[ -e "$WORK" ]]; then
    echo "ERROR: $WORK exists. Keep evidence; rename it before rerunning." >&2
    exit 2
fi
mkdir -p "$WORK"
# Create an immutable input snapshot; do NOT replace original Card/DECAY.
cp "$CARD" "$WORK/diagnostic_input_param_card.dat"
cat > "$WORK/madwidth.mg5" <<EOF
set automatic_html_opening False
import model $UFO
compute_widths H+ h+ --body_decay=2 --path=$WORK/diagnostic_input_param_card.dat --output=$WORK/madwidth_output_param_card.dat
EOF
echo "MadWidth two-body computations: H+ (PDG 227), h+ (PDG 228)"
echo "INPUT = $WORK/diagnostic_input_param_card.dat"
echo "OUTPUT = $WORK/madwidth_output_param_card.dat"
set -o pipefail
"$MG5_EXEC" "$WORK/madwidth.mg5" 2>&1 | tee "$WORK/madwidth.log"
if [[ ! -s "$WORK/madwidth_output_param_card.dat" ]]; then
    echo "ERROR: MadWidth did not create nonempty output card." >&2
    exit 3
fi
python3 "$ROOT/scripts/gate7_check_madwidth.py" \
    --card "$WORK/madwidth_output_param_card.dat" \
    --output "$WORK/width_comparison.json"
echo "COMPLETE: check Gate 6 analytic partial-width comparison, not raw BRs."
