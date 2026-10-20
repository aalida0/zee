#!/usr/bin/env bash
# One-command E6 on UChicago AF. Never run code on /data.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate
test -d /home/aalida/tools/hsdataset
for gate in \
  work/zee_E2_complete_395_original_vacua_20261020_v1 \
  work/zee_E3_309_multiroot_flavor_optimized_20261020_v1 \
  work/zee_E4h_309_direct_h125_20261020_v1 \
  work/zee_E5_309_h125_HiggsSignals_effective_v1; do
  test -f "$gate/summary.json"
done
python -c 'import numpy,Higgs.predictions,Higgs.signals;print("E6_AF_DEPS_OK")'
python -m py_compile \
 scripts/zee_gateE6_zgamma_mixed_PV.py \
 scripts/zee_gateE6_309_charged_gamma_higgssignals.py \
 tests/test_zee_gateE6_309_charged_gamma_higgssignals.py
python -m unittest discover -s tests \
 -p 'test_zee_gateE6_309_charged_gamma_higgssignals.py' -v
out=work/zee_E6_309_charged_gamma_HS_20261020_v1
args=(
 --e2-dir work/zee_E2_complete_395_original_vacua_20261020_v1
 --e3-dir work/zee_E3_309_multiroot_flavor_optimized_20261020_v1
 --e4h-dir work/zee_E4h_309_direct_h125_20261020_v1
 --e5-dir work/zee_E5_309_h125_HiggsSignals_effective_v1
 --hs-dataset /home/aalida/tools/hsdataset
 --output-dir "$out"
)
if [[ $# -eq 1 && "$1" == "--resume" ]]; then
 args+=(--resume)
elif [[ $# -ne 0 ]]; then
 echo 'usage: bash scripts/zee_gateE6_one_shot.sh [--resume]' >&2
 exit 2
fi
python -u scripts/zee_gateE6_309_charged_gamma_higgssignals.py \
 "${args[@]}" 2>&1 | tee work/zee_E6_309_charged_gamma_HS_20261020_v1_run.log
python - <<'PY'
import json
from pathlib import Path
p=Path("work/zee_E6_309_charged_gamma_HS_20261020_v1/summary.json")
r=json.loads(p.read_text())
assert r["updated_HiggsSignals_hgamma_gamma_models"]==309
assert r["full_Zee_allowed_or_excluded"] is None
assert r["full_h_to_Zgamma_one_loop_scalar_subset_with_mixed_mass_completed"] is True
assert r["full_h_to_Zgamma_higher_order_model_prediction_NOT_completed"] is True
print("E6_FINAL",r["status"])
print("E6_OLD_MEDIAN",r["old_E5_delta_chi2_median"])
print("E6_NEW_GAMMA_ZGAM_MEDIAN",r["scalar_gamma_Zgamma_corrected_delta_chi2_median"])
print("E6_NEW_GAMMA_ZGAM_RANGE",r["scalar_gamma_Zgamma_corrected_delta_chi2_min"],
      r["scalar_gamma_Zgamma_corrected_delta_chi2_max"])
print("E6_PRIORITY_BENCHMARKS",[(tag,round(
   z["delta_chisq_vs_same_SM"],6)) for tag,z in r["target_benchmarks"].items()])
print("E6_ZGAM_OFFDIAGONAL_MIXED_LOOP_INCLUDED",True)
print("E6_FULL_ZEE_ALLOWED_UNKNOWN",True)
PY
