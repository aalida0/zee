#!/usr/bin/env bash
# Exact 13 TeV official LHCHXSWG YR4 heavy H+ TypeII Santander-matched XS.
# Returns 8 source-backed F13 included-channel cascade production estimates.
set -euo pipefail
cd /home/aalida/zee
python3 -m unittest discover -s tests -p 'test_zee_paper1_F14_LHCHXSWG_13TeV_physical_unit_cascade.py' -v
grid="${ZEE_LHCHXSWG_13TEV:-$PWD/data/lhchxswg/mflechl_xsec_13TeV_tHp_2016_2_5.txt}"
if [[ ! -f "$grid" ]]; then
  mkdir -p "$(dirname "$grid")"
  echo "F14_DOWNLOADING_ORIGINAL_LHCHXSWG_DATA $grid"
  curl --fail --location --retry 2 --connect-timeout 15 --max-time 90 --silent --show-error "https://twiki.cern.ch/twiki/pub/LHCPhysics/LHCHWGMSSMCharged/mflechl_xsec_13TeV_tHp_2016_2_5.txt" -o "$grid"
fi
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="$PWD/work/zee_paper1_F14_LHCHXSWG_13TeV_production_$stamp"
python3 -u scripts/zee_paper1_F14_LHCHXSWG_13TeV_physical_unit_cascade.py --grid "$grid" --f13-dir "$PWD/work/zee_paper1_F13_heavy_final_20261021T125623Z" --output "$out" "$@"
