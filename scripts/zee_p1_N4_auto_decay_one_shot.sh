#!/usr/bin/env bash
# No more hand-built decay gates: prepare actual UFO/MadWidth route.
# The original E2/E3/B3/N1/N2/N3 outputs stay read-only; /home execution.
set -euo pipefail
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate

for spec in \
 'test_zee_p1_complex_flavor_feynrules.py' \
 'test_zee_p1_ufo_model_audit.py' \
 'test_zee_p1_e3_complex_flavor_fragments.py' \
 'test_zee_p1_madwidth_driver.py'; do
 echo "P1_DECAY_MODEL_AUTOMATION_TEST $spec"
 python3 -m unittest discover -s tests -p "$spec" -v
done

python3 -u scripts/zee_p1_N4_complete_decay_generator_preflight.py "$@"

python3 - <<'PY'
import json
from pathlib import Path
s=Path('work/p1_auto_decay_full_ufo_N4_20261020_v1/summary.json')
x=json.loads(s.read_text())
assert x['source_original_309']==309
assert x['real_309_complex_lepton_Y_f_exported'] is True
assert x['full_scalar_potential_Higgs_basis_mapping_validated'] is False
assert x['five_state_full_HiggsTools_production_and_widths_complete'] is False
assert x['full_Zee_allowed_or_excluded'] is None
print('P1_N4_DONE',x['status'])
print('P1_N4_FREYNRULES',x['feynrules_complex_typeII_source']['status'])
print('P1_N4_ORIGINAL_E3_MAX_Y_IMAG',x['max_abs_E3_Y_imaginary'])
print('P1_N4_RESULT',s)
PY
