#!/usr/bin/env bash
# REAL six Zee benchmarks: LO NP C7/C8 + flavio inclusive rate.
# Historical flavio SM normalization; no modern 2026 full-NNLO exclusion.
set -euo pipefail
cd /home/aalida/zee
repo="$PWD"
venv="$repo/.venv_paper1_F11_flavio"
if [[ ! -x "$venv/bin/python" ]]; then
  python3 -m venv "$venv"
fi
if ! "$venv/bin/python" - <<'PY'
import importlib.metadata as md
want={"flavio":"2.7.1","wilson":"2.5.2","particle":"0.26.2"}
assert all(md.version(k)==v for k,v in want.items())
PY
then
  "$venv/bin/python" -m pip install --disable-pip-version-check \
    -r "$repo/requirements/paper1_F11_flavio.txt"
fi
export PYTHONNOUSERSITE=1
"$venv/bin/python" -m unittest discover -s tests \
  -p 'test_zee_paper1_F11_six_real_flavio_LO_NP_rate.py' -v
"$venv/bin/python" - <<'PY'
from particle import data
from pathlib import Path
base=Path(str(data.basepath))
assert (base/"particle2022.csv").is_file(), "flavio 2.7.1 legacy PDG file missing"
import flavio, wilson
print("F11_BACKEND_CHECK",flavio.__version__,wilson.__version__)
PY
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
folder="$repo/work/zee_paper1_F11_real_flavio_six_$timestamp"
"$venv/bin/python" -u scripts/zee_paper1_F11_six_real_flavio_LO_NP_rate.py \
  --f10-dir "$repo/work/zee_paper1_F10_legacy_six_20261021T113910Z" \
  --output-dir "$folder" "$@"
