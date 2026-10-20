#!/usr/bin/env bash
# E7 one shot: revalidate original E6 source, recompute 309 exact-neutrino
# general Zee charged-lepton widths, produce combined experimental/cascade
# diagnostic Pareto frontier. No fake heavy HiggsBounds pass/fail.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate

for gate in \
  work/zee_E2_complete_395_original_vacua_20261020_v1 \
  work/zee_E3_309_multiroot_flavor_optimized_20261020_v1 \
  work/zee_E4h_309_direct_h125_20261020_v1 \
  work/zee_E5_309_h125_HiggsSignals_effective_v1 \
  work/zee_E6_309_charged_gamma_HS_20261020_v1; do
  test -f "$gate/summary.json" || {
    echo "E7 SOURCE MISSING: $gate/summary.json" >&2
    exit 2
  }
done
test -d /home/aalida/tools/hsdataset || {
 echo "HiggsSignals dataset missing" >&2
 exit 2
}
python -c 'import numpy,Higgs.predictions,Higgs.signals;print("E7_REQUIRED_DEPS_OK")'
python -m py_compile \
 scripts/zee_gateE7_309_general_lepton_width_pareto.py \
 tests/test_zee_gateE7_309_general_lepton_width_pareto.py

# One combined regression command: the complete width solver, the E5
# effective h125 coupling adapter, both charged scalar loop channels E6,
# and E7 source/claim/Pareto/width consistency (not the entire repo suite).
for pattern in \
 'test_gateB3_general_zee_charged_lepton_widths.py' \
 'test_zee_gateE5_309_h125_higgssignals_effective.py' \
 'test_zee_gateE6_309_charged_gamma_higgssignals.py' \
 'test_zee_gateE7_309_general_lepton_width_pareto.py'; do
 echo "E7_REGRESSION_SUITE $pattern"
 python -m unittest discover -s tests -p "$pattern" -v
done

OUT=work/zee_E7_309_optimized_Zee_charged_widths_Pareto_20261020_v1
# No overwrite of E2-E6 or prior E7 output.
if [[ -e "$OUT" ]]; then
 echo "E7 refuses to overwrite previous E7 output: $OUT" >&2
 exit 2
fi

python -u scripts/zee_gateE7_309_general_lepton_width_pareto.py \
 --e2-dir work/zee_E2_complete_395_original_vacua_20261020_v1 \
 --e3-dir work/zee_E3_309_multiroot_flavor_optimized_20261020_v1 \
 --e4h-dir work/zee_E4h_309_direct_h125_20261020_v1 \
 --e5-dir work/zee_E5_309_h125_HiggsSignals_effective_v1 \
 --e6-dir work/zee_E6_309_charged_gamma_HS_20261020_v1 \
 --hs-dataset /home/aalida/tools/hsdataset \
 --output-dir "$OUT" \
 --high-cascade-threshold .4 \
 2>&1 | tee work/zee_E7_309_optimized_Zee_charged_widths_Pareto_20261020_v1_run.log

python - <<'PY'
import csv,json
from pathlib import Path
out=Path("work/zee_E7_309_optimized_Zee_charged_widths_Pareto_20261020_v1")
z=json.loads((out/"summary.json").read_text())
assert z["original_models"]==309
assert z["neutrino_closure_full_309_checked"]
assert z["HiggsBounds_model_exclusion_not_evaluated"]
assert z["full_allowed_and_excluded_Zee_counts"] is None
print("E7_FINAL",z["status"])
print("E7_OLD_MEDIAN_UPPER_PROXY",z["original_B4_nonleptonic_proxy_median"])
print("E7_NEW_MEDIAN_INCLUDED_ONLY_PROXY",z["new_B3_general_lepton_included_proxy_median"])
print("E7_LOWER_UPPER_PROXY_COUNT",z["num_proxy_decreased"],z["num_proxy_increased"])
print("E7_PARETO_CASES",z["Pareto_frontier_count"])
p=out/"E7_Pareto_HS_vs_general_Zee_cascade_NOT_ALLOWED.csv"
with p.open(newline="") as f:
 rows=list(csv.DictReader(f))
print("E7_PARETO_ALL (delta chi2, included-channel production proxy)")
for t in rows:
 print(t["candidate_id"],
       round(float(t["HS_delta_chi2_E6_vs_fixed_SM"]),4),
       round(float(t["charged_cascade_included_channel_proxy_NOT_physical_rate"]),6),
       "BR_H2_H1Z_INCLUDED",
       round(float(t["included_channel_BR_H2_to_H1Z"]),5),
       "BR_H1_tb_INCLUDED",
       round(float(t["included_channel_BR_H1_to_tb"]),5))
print("E7_HIGGSBOUNDS_HEAVY_STATES_NOT_EVALUATED (missing complete rates)")
print("E7_NO_FULL_MODEL_ALLOWED_OR_EXCLUDED",True)
PY
