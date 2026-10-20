#!/usr/bin/env bash
# F7 single read-only 309 F6 legacy-to-2026 SM sensitivity and robustness.
# Diagnostic only; no matched NNLO Zee BR, no experiment exclusion.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate
SOURCE=work/zee_F6_309_two_charged_full_legacy_bsgamma_20261020_v1
for f in "$SOURCE/summary.json" "$SOURCE/manifest.json" \
 "$SOURCE/F6_309_legacy_two_state_BtoXsgamma_NOT_2026_EXCLUSION.jsonl";do
 test -f "$f" || { echo "F7_SOURCE_NOT_FOUND $f" >&2;exit 2; }
done

python -m py_compile \
 scripts/zee_gateF7_309_2026_bsgamma_tension_sensitivity.py \
 tests/test_zee_gateF7_309_2026_bsgamma_tension_sensitivity.py
# Recheck original F6 physics code, source-safe regressions and new sensitivity audit.
for pat in \
 'test_zee_gateF6_309_full_legacy_bsgamma.py' \
 'test_zee_gateF7_309_2026_bsgamma_tension_sensitivity.py'; do
 echo "F7_REGRESSION $pat"
 python -m unittest discover -s tests -p "$pat" -v
done

OUT=work/zee_F7_309_2026_bsgamma_precision_sensitivity_20261020_v1
test ! -e "$OUT" || { echo "F7_CANNOT_OVERWRITE_EXISTING_OUTPUT $OUT" >&2;exit 2; }

python -u scripts/zee_gateF7_309_2026_bsgamma_tension_sensitivity.py \
 --f6-dir "$SOURCE" \
 --output-dir "$OUT" \
 2>&1 | tee work/zee_F7_309_2026_bsgamma_precision_sensitivity_20261020_v1_run.log

python - <<'PY'
import json
from pathlib import Path
p=Path("work/zee_F7_309_2026_bsgamma_precision_sensitivity_20261020_v1/summary.json")
z=json.loads(p.read_text())
assert z["total_source_models"]==309
assert z["num_sensitivity_scenarios"]==36
assert z["all_309_Zee_allowed_or_excluded"] is None
assert z["full_experimental_likelihood_evaluated"] is False
assert z["2026_model_BSM_matching_derived"] is False
print("F7_FINAL",z["status"],"309/309")
print("F7_REFERENCE_2026_SM_AND_EXPERIMENT",z["modern_2026_SM_and_exp_reference_used"])
print("F7_ILLUSTRATIVE_GAUSSIAN_MIN_MEDIAN_MAX",
      z["purely_illustrative_Gaussian_pull_min_median_max"])
print("F7_ILLUSTRATIVE_BAND_COUNT_NOT_95CL_MODEL_EXCLUSIONS",
      z["purely_illustrative_above_positive_1p96_count"])
print("F7_SOURCE_LOCKED_RESULTS",p)
print("F7_NO_VALIDATED_MODERN_TWO_HIGGS_BRANCHING_RATIO_OR_EXCLUSION",True)
PY
