#!/usr/bin/env bash
# Minimal genuine smoke test of Priority-1 source contracts on UChicago AF.
# It deliberately reports missing full-physics backends, NOT allowed points.
set -euo pipefail
cd /home/aalida/zee
python3 -m py_compile \
 scripts/zee_priority1_contracts.py \
 scripts/zee_priority1_higgstools.py \
 scripts/zee_priority1_cli.py \
 scripts/zee_priority1_neutrino_gaussian.py \
 scripts/zee_priority1_coherent_lfv.py \
 scripts/zee_priority1_streaming.py \
 scripts/zee_priority1_charged_width_export.py \
 scripts/zee_priority1_production_lhe.py
python3 -m unittest discover -s tests \
 -p 'test_zee_priority1_global_contracts.py' -v
python3 -m unittest discover -s tests \
 -p 'test_zee_priority1_numerics.py' -v
python3 -m unittest discover -s tests \
 -p 'test_zee_priority1_unification.py' -v
python3 -m unittest discover -s tests \
 -p 'test_gateB3_general_zee_charged_lepton_widths.py' -v
python3 -m unittest discover -s tests \
 -p 'test_zee_priority1_real_charged_widths.py' -v
mkdir -p work
TEMP="$(mktemp -d /home/aalida/zee/work/priority1_contracts_smoke_XXXXXX)"
cat > "$TEMP/points.csv" <<'CSV'
id,mH1,mH2,mh2,ma,gamma,tanbeta,candidate_status
B4_EXAMPLE,210,680,590,630,1.12,5.6,SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED
CSV
python3 -u scripts/zee_priority1_cli.py \
  --points "$TEMP/points.csv" --out "$TEMP/report"
python3 - "$TEMP/report/summary.json" <<'PY'
import json,sys
z=json.load(open(sys.argv[1]))
assert z["points"]==1
assert z["full_Zee_model_allowed_or_excluded"] is None
assert z["per_candidate_higgstools_API_calls"]==0
assert all(v.get("BLOCKED_NO_BACKEND_INPUT")==1
           for v in z["per_component_status_counts"].values())
print("PRIORITY1_SMOKE_PASS_NO_FALSE_EXCLUSIONS",sys.argv[1])
PY

python3 -u scripts/zee_priority1_cli.py \
  --points "$TEMP/points.csv" --out "$TEMP/streaming_report" \
  --stream-coverage
python3 - "$TEMP/streaming_report/summary.json" <<'PY'
import json,sys
s=json.load(open(sys.argv[1]))
assert s["original_candidate_count"]==1
assert s["full_Zee_allowed_or_excluded"] is None
assert s["P1_other_five_scientific_backends_completed"] is False
print("PRIORITY1_STREAMING_SMOKE_PASS",sys.argv[1])
PY
