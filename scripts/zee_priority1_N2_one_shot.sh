#!/usr/bin/env bash
# N2 one AF invocation; test real gauge/source and read only prior E2/E3/N1.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate

python3 -m py_compile \
 scripts/zee_priority1_neutral_bosonic_two_body.py \
 scripts/zee_priority1_neutral_bosonic_309_one_shot.py

for pat in \
 'test_gateB3_general_zee_charged_lepton_widths.py' \
 'test_zee_priority1_neutral_two_body.py' \
 'test_zee_priority1_neutral_bosonic_two_body.py' \
 'test_zee_priority1_neutral_bosonic_309_join.py'; do
 echo "P1_N2_SOURCE_REGRESSION $pat"
 python3 -m unittest discover -s tests -p "$pat" -v
done

python3 -u scripts/zee_priority1_neutral_bosonic_309_one_shot.py
python3 - <<'PY'
import json
from pathlib import Path
p=Path("work/p1_original_309_neutral_bosonic_N2_20261020_v2/summary.json")
z=json.loads(p.read_text())
assert z["original_source_points"]==309
assert z["real_N2_neutral_bosonic_calculations"]==309
assert z["N2_Gate6_h_H_charged_cross_cubic_closed"]==309
assert z["physical_five_state_widths_complete"] is False
assert z["HiggsBounds_95CL_evaluations"]==0
assert z["experimental_model_allowed_excluded"] is None
print("P1_N2_FINAL",z["status"],"309/309","FULL_MODEL_ALLOWED_UNKNOWN",flush=True)
for k,row in z["N2_priority_modes_and_N1_comparison"].items():
 print("P1_N2_CHECK",k,
       "H_INCL_BEFORE",row["old_N1_h_H_A_included_sums_NOT_totals_GeV"]["H"],
       "H_INCL_AFTER",row["new_N2_h_H_A_included_sums_NOT_totals_GeV"]["H"],
       "H_to_H1H1",row["N2_H_to_H1plus_H1minus_GeV"],
       "A_to_H1W_both",row["N2_A_to_H1_W_both_charge_modes_GeV"],
       "NO_FULL_BR",flush=True)
print("P1_N2_REPORT",p,flush=True)
PY
