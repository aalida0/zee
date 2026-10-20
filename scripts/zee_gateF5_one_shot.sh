#!/usr/bin/env bash
# F5: 309 original E7 Zee points against EXACT pinned F4b SuperIso source RG.
# One AF invocation, no HiggsBounds invented, no physical B->Xs gamma BR.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate

for src in \
  work/zee_E7_309_optimized_Zee_charged_widths_Pareto_20261020_v1/summary.json \
  work/gateF4b_dipole_order_8_v1/summary.json; do
 test -f "$src" || { echo "MISSING F5 SOURCE: $src" >&2; exit 2; }
done

python -m py_compile \
 scripts/zee_gateF5_309_source_pinned_C7_dipole_pareto.py \
 tests/test_zee_gateF5_309_source_pinned_C7_dipole_pareto.py
python -m unittest discover -s tests \
 -p 'test_zee_gateF5_309_source_pinned_C7_dipole_pareto.py' -v

OUT=work/zee_F5_309_two_charged_C7eff_projector_20261020_v1
if [[ -e "$OUT" ]]; then
 echo "F5 cannot overwrite previous report: $OUT" >&2; exit 2
fi
python -u scripts/zee_gateF5_309_source_pinned_C7_dipole_pareto.py \
 --e7-dir work/zee_E7_309_optimized_Zee_charged_widths_Pareto_20261020_v1 \
 --f4b-summary work/gateF4b_dipole_order_8_v1/summary.json \
 --output-dir "$OUT" \
 2>&1 | tee work/zee_F5_309_two_charged_C7eff_projector_20261020_v1.log

python - <<'PY'
import json
from pathlib import Path
p=Path("work/zee_F5_309_two_charged_C7eff_projector_20261020_v1/summary.json")
z=json.loads(p.read_text())
assert z["source_models"]==309
assert z["F4b_source_matched_controls"]==8
assert z["full_model_allowed_or_excluded"] is None
assert z["complete_EOS_NLO_matrix_elements_and_B_to_Xs_gamma_BR"] is False
print("F5_FINAL",z["status"],"MODELS",309)
print("F5_STRICT_C7_PROJECTOR_MIN_MEDIAN_MAX",z["C7_strict_projector_min_median_max"])
print("F5_E7_PARETO_C7_DIAGNOSTIC")
for key,v in z["E7_Pareto_source_diagnostic"].items():
 print(key,"HS",round(v["E6_HS"],4),
       "CASCADE",round(v["E7_partial_cascade"],6),
       "Q7_LO",round(v["Q7eff_NP_LO"],8),
       "Q7_NLO_TRUNC",round(v["Q7eff_NP_truncated_LO_NLO"],8),
       "HIGH_C4",round(v["HighScale_NLO_C4"],8))
print("F5_NO_PHYSICAL_BRANCHING_RATIO_OR_EXCLUSION",True)
PY
