#!/usr/bin/env bash
# P1 N3: original archived N2 -> 309 potential-derived Hhh/HAA partial
# widths. /home execution, all old E2/E3/B3/N1/N2 outputs read-only.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate

python3 -m py_compile \
 scripts/zee_priority1_neutral_scalar_cubics.py \
 scripts/zee_priority1_N3_309_one_shot.py \
 tests/test_zee_priority1_neutral_scalar_cubics.py \
 tests/test_zee_priority1_N3_original_N2_join.py

for pat in \
 'test_zee_priority1_neutral_bosonic_two_body.py' \
 'test_zee_priority1_neutral_bosonic_309_join.py' \
 'test_zee_priority1_neutral_scalar_cubics.py' \
 'test_zee_priority1_N3_original_N2_join.py';do
 echo "P1_N3_SOURCE_REGRESSION $pat"
 python3 -m unittest discover -s tests -p "$pat" -v
done

N2=work/p1_original_309_neutral_bosonic_N2_20261020_v2
test -f "$N2/summary.json" || {
  echo "P1_N3 missing completed original 309 N2 stage $N2/summary.json" >&2
  exit 2
}
OUT=work/p1_original_309_neutral_scalar_cubics_N3_20261020_v1
test ! -e "$OUT" || {
  echo "P1_N3 refusing to overwrite previous N3 $OUT" >&2
  exit 2
}
python3 -u scripts/zee_priority1_N3_309_one_shot.py \
  --prior-n2 "$N2" --out "$OUT"

python3 - <<'PY'
import json
from pathlib import Path
file=Path("work/p1_original_309_neutral_scalar_cubics_N3_20261020_v1/summary.json")
r=json.loads(file.read_text())
assert r["source_original_309"]==309
assert r["independent_potential_derivative_numerically_checked_309"]==309
assert r["five_state_physical_total_widths_computed"] is False
assert r["HiggsBounds_model_exclusions_computed"] is False
assert r["full_model_allowed_or_excluded"] is None
print("P1_N3_FINAL",r["status"],"309/309","HIGGSBOUNDS_EXCLUSIONS 0",flush=True)
for k,x in r["prioritized_spectra"].items():
 print("P1_N3_CHECK",k,
       "H_LO_BEFORE",x["N2_H_included_not_physical_GeV"],
       "H_LO_AFTER",x["N3_H_included_not_physical_GeV"],
       "H_TO_hh_PARTIAL",x["H_hh_identical_GeV"],
       "H_TO_AA_PARTIAL",x["H_AA_identical_GeV"],
       "NO_PHYSICAL_TOTAL",flush=True)
print("P1_N3_REPORT",file,flush=True)
PY
