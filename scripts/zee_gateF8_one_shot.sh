#!/usr/bin/env bash
# F8: original archived F6 executable and all 309 source-pinned Zee spectra.
# Validate TypeII 670 same-vendor comparator, and 6 fixed-mass gamma slices.
# Do NOT interpret any same-legacy-rate comparison as a modern Zee 95% CL.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate

SRC=work/zee_F6_309_two_charged_full_legacy_bsgamma_20261020_v1
test -f "$SRC/summary.json"
test -f "$SRC/manifest.json"
test -f "$SRC/f6_pinned_A1U_inclusive_br"

python -m py_compile \
 scripts/zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing.py \
 tests/test_zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing.py

for pat in \
 'test_zee_gateF6_309_full_legacy_bsgamma.py' \
 'test_zee_gateF7_309_2026_bsgamma_tension_sensitivity.py' \
 'test_zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing.py'; do
 echo "F8_SOURCE_REGRESSION $pat"
 python -m unittest discover -s tests -p "$pat" -v
done

OUT=work/zee_F8_309_670TypeII_same_kernel_mixing_20261020_v1
if [[ -e "$OUT" ]]; then
 echo "F8 cannot overwrite an existing output $OUT" >&2; exit 2
fi

python -u scripts/zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing.py \
 --f6-dir "$SRC" --output-dir "$OUT" \
 2>&1 | tee work/zee_F8_309_670TypeII_same_kernel_mixing_20261020_v1_run.log

python - <<'PY'
import json
from pathlib import Path
p=Path("work/zee_F8_309_670TypeII_same_kernel_mixing_20261020_v1/summary.json")
z=json.loads(p.read_text())
assert z["original_F6_Zee_models"] == 309
assert z["same_source_legacy_TypeII_670_reference_run_per_model"] == 309
assert z["number_fixed_mass_gamma_counterfactual_rows"] == 132
assert z["num_actual_original_gamma_points_in_counterfactual_slices"] == 6
assert z["published_2026_TypeII_mass_bound_imposed_on_Zee"] is False
assert z["F8_2026_modern_model_likelihood_completed"] is False
assert z["fully_model_allowed_or_excluded"] is None
print("F8_FINAL",z["status"],"309/309",flush=True)
print("F8_SAME_LEGACY_RATIO_MIN_MEDIAN_MAX",
    z["source_legacy_NP_over_TypeII670_ratio_min_median_max"])
print("F8_TYPEII670_COMPARISON_COUNT_NOT_EXCLUSIONS",
    z["num_Zee_higher_than_TypeII670_in_same_legacy_kernel"])
print("F8_SIX_BENCHMARKS")
for k,source in z["six_priority_actual_source"].items():
 print(k,"NP_ratio",round(source[
      "NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"],6),
     "cascade_proxy",round(source[
      "E7_cascade_included_channels_proxy_NOT_rate"],6),
     "E6_delta_chi2",round(source["E6_HS_delta_chi2_NOT_CL"],6))
print("F8_NO_ZEE_95CL_INFERRED_FROM_TYPEII670",True)
PY
