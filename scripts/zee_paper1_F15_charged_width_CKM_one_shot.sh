#!/usr/bin/env bash
# F15 exact-source F13/F14 width closure plus all CKM TypeII two-body modes.
# No physical total, 2026 NNLO allowed, or FCC 85/100TeV sigma fabricated.
set -euo pipefail
cd /home/aalida/zee
python3 -m py_compile scripts/zee_paper1_F15_charged_width_CKM_mass_scheme_audit.py tests/test_zee_paper1_F15_charged_width_CKM_mass_scheme_audit.py
python3 -m unittest discover -s tests -p 'test_zee_paper1_F15_charged_width_CKM_mass_scheme_audit.py' -v
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="$PWD/work/zee_paper1_F15_CKM_charged_widths_$stamp"
python3 -u scripts/zee_paper1_F15_charged_width_CKM_mass_scheme_audit.py --f13-dir "$PWD/work/zee_paper1_F13_heavy_final_20261021T125623Z" --f14-dir "$PWD/work/zee_paper1_F14_LHCHXSWG_13TeV_production_20261021T133239Z" --output "$out" "$@"
