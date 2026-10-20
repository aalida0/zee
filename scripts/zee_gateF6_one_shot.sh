#!/usr/bin/env bash
# F6 single AF run: 309 genuine old-vendor inclusive b->s gamma two-state BRs.
# STRICTLY no modern-2026 NNLO / experimental likelihood / model exclusion.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate
for p in \
 work/zee_E7_309_optimized_Zee_charged_widths_Pareto_20261020_v1/summary.json \
 work/zee_F5_309_two_charged_C7eff_projector_20261020_v1/summary.json \
 work/gateA1u_legacy_zee_br_v1/legacy_two_state_br.json \
 work/gateA1r_observable_v1/gateA1r_br_pilot.json \
 work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
 work/gateA1m_isolated_nlo_v1/isolated_superiso/src/libsuperiso.a; do
 if [[ ! -f "$p" ]]; then echo "F6_REQUIRED_HISTORICAL_SOURCE_MISSING $p" >&2;exit 2;fi
done

python -m py_compile \
 scripts/zee_gateF6_309_full_legacy_bsgamma.py \
 tests/test_zee_gateF6_309_full_legacy_bsgamma.py
for t in \
 'test_gateA1u_legacy_two_state_br.py' \
 'test_zee_gateF5_309_source_pinned_C7_dipole_pareto.py' \
 'test_zee_gateF6_309_full_legacy_bsgamma.py'; do
 echo "F6_REGRESSION $t"
 python -m unittest discover -s tests -p "$t" -v
done

OUT=work/zee_F6_309_two_charged_full_legacy_bsgamma_20261020_v1
if [[ -e "$OUT" ]];then
 echo "F6 refuses to overwrite old output $OUT" >&2
 exit 2
fi
python -u scripts/zee_gateF6_309_full_legacy_bsgamma.py \
 --e7-dir work/zee_E7_309_optimized_Zee_charged_widths_Pareto_20261020_v1 \
 --f5-dir work/zee_F5_309_two_charged_C7eff_projector_20261020_v1 \
 --a1u-result work/gateA1u_legacy_zee_br_v1/legacy_two_state_br.json \
 --a1r-result work/gateA1r_observable_v1/gateA1r_br_pilot.json \
 --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
 --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
 --output-dir "$OUT" \
 2>&1 | tee work/zee_F6_309_full_legacy_bsgamma_20261020_v1.log

python - <<'PY'
import json
from pathlib import Path
f=Path("work/zee_F6_309_two_charged_full_legacy_bsgamma_20261020_v1/summary.json")
z=json.loads(f.read_text())
assert z["original_source_points"]==309
assert z["A1U_historical_full_inclusive_kernel_reproduced"] is True
assert z["modern_2026_matching_and_theory_uncertainties_calibrated"] is False
assert z["experimental_95CL_likelihood_validated"] is False
assert z["Zee_allowed_or_excluded"] is None
print("F6_FINAL",z["status"],"309/309")
print("F6_LEGACY_SUPERISO_SM_BR",z["legacy_SM_BR"])
print("F6_LEGACY_ZEE_BR_MIN_MEDIAN_MAX",z["legacy_BR_min_median_max"])
print("F6_LEGACY_NP_BR_SHIFT_MIN_MEDIAN_MAX",z["legacy_NP_minus_SM_min_median_max"])
print("F6_LEGACY_ZEE_ABOVE_SAME_LEGACY_SM",
      z["legacy_BtoXsGamma_above_same_legacy_SM"])
print("F6_6_PARETO_LEGACY_BR_CONTEXT_ONLY")
for k,v in z["priority_six"].items():
 print(k,"BR",f'{v["legacy_BR"]:.10g}',
       "NP_MINUS_SM",f'{v["legacy_BR_NP_minus_SM"]:.8g}',
       "E6_HS",round(v["E6_HiggsSignals_delta"],4),
       "E7_CASCADE",round(v["E7_cascade"],6))
print("F6_NO_2026_NNLO_EXCLUSION_OR_LIKELIHOOD",True)
PY
