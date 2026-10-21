#!/usr/bin/env bash
# Compute real six-point LO Zee NP C7/C8 inclusive rate in the older flavio engine.
# Never interpret output as modern 2026 NNLO/exclusion/fully allowed Zee model.
set -euo pipefail
cd /home/aalida/zee
python3 -m unittest discover -s tests -p 'test_zee_paper1_F11_six_real_flavio_LO_NP_rate.py' -v
python3 - <<'PY'
import importlib.util,sys
for package in ("flavio","wilson"):
 if importlib.util.find_spec(package) is None:
  sys.exit("F11_DEPENDENCY_MISSING "+package+
            " -- install in your project Python environment; do not fake a backend")
PY
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
folder="/home/aalida/zee/work/zee_paper1_F11_real_flavio_six_$timestamp"
python3 -u scripts/zee_paper1_F11_six_real_flavio_LO_NP_rate.py \
  --f10-dir /home/aalida/zee/work/zee_paper1_F10_legacy_six_20261021T113910Z \
  --output-dir "$folder" "$@"
