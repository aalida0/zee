#!/usr/bin/env bash
# F9: inspect ORIGINAL fully computed F8 309+132 outputs; no SuperIso rerun.
# AF /home only; all existing output archived SHA, never overwrite F8.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate

SRC=work/zee_F8_309_670TypeII_same_kernel_mixing_20261020_v1
for f in "$SRC/summary.json" "$SRC/manifest.json" \
  "$SRC/F8_309_Zee_legacy_vs_670TypeII_NOT_EXCLUSION.jsonl" \
  "$SRC/F8_309_legacy_typeII_670_same_kernel_DIAGNOSTIC.csv" \
  "$SRC/F8_six_fixed_mass_gamma_counterfactual_NOT_MODEL_POINTS.csv";do
  test -f "$f" || { echo "F9 missing immutable F8 source $f" >&2;exit 2; }
done

python -m py_compile \
 scripts/zee_gateF9_F8_mixing_flavor_geometry_132.py \
 tests/test_zee_gateF9_F8_mixing_flavor_geometry_132.py

# The original F8 tests also run first; no heavy AF physics recalc.
for pat in \
 'test_zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing.py' \
 'test_zee_gateF9_F8_mixing_flavor_geometry_132.py';do
 echo "F9_REGRESSION $pat"
 python -m unittest discover -s tests -p "$pat" -v
done

OUT=work/zee_F9_132_original_F8_gamma_geometry_tradeoff_20261020_v1
test ! -e "$OUT" || {
 echo "F9 will not overwrite a previous source-checked F9 report $OUT" >&2
 exit 2
}
python -u scripts/zee_gateF9_F8_mixing_flavor_geometry_132.py \
 --f8-dir "$SRC" --output-dir "$OUT" \
 2>&1 | tee work/zee_F9_132_gamma_geometry_tradeoff_20261020_v1_run.log

python - <<'PY'
import json
from pathlib import Path
p=Path("work/zee_F9_132_original_F8_gamma_geometry_tradeoff_20261020_v1/summary.json")
r=json.loads(p.read_text())
assert r["archived_original_Zee_points"]==309
assert r["archived_gamma_counterfactual_rows"]==132
assert r["one_real_original_gamma_source_per_priority_case"]==6
assert r["modern_2026_Zee_B_to_Xs_gamma_complete_model_likelihood_evaluated"] is False
assert r["physically_consistent_new_Zee_scalar_neutrino_Yukawa_reoptimization_evaluated"] is False
assert r["full_Zee_allowed_excluded"] is None
print("F9_FINAL",r["status"])
print("F9_ACTUAL_ORIGINAL_R_GT_1_COUNT",
      r["num_original_source_models_vs_same_legacy_TypeII670_above"])
print("F9_ACTUAL_ORIGINAL_R_LT_1_COUNT",
      r["num_original_source_models_vs_same_legacy_TypeII670_below"])
print("F9_FAVORABLE_LEGACY_GAUGE_GEOMETRY_COUNTS_OUT_OF_SIX")
for k,v in r["six_priority_gamma_counts_below_reference_with_retention"].items():
 print(k,v)
print("F9_ALL_SIX")
for k,x in r["six_priority_summaries"].items():
 print(k,"ORIGINAL_R",round(x[
      "original_legacy_Zee_over_TypeII670_NP_shift_ratio"],5),
     "BEST_G80",x["gauge_retention_ge_80pct"],
     "BEST_P80",x["prodweighted_geometry_retention_ge_80pct"])
print("F9_NO_2026_ZEE_MODEL_EXCLUSION",True)
PY
