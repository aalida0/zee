#!/usr/bin/env bash
# Run manually ON LXPLUS. Read-only; never submits and never prints credentials.
set -euo pipefail
[[ $# -eq 0 ]] || { echo 'Usage: zee_d7_preflight.sh' >&2; exit 64; }
echo 'D7_MANUAL_CERN_PREFLIGHT (does not validate worker-node availability)'
id -un
hostname -f
uname -a
cat /etc/os-release
condor_version
condor_submit -version
source module9/condor/environment.sh
python3 --version
python3 - <<'PY'
import importlib.metadata
import platform
import sys
from module9.d7_inputs import validate_point, seed_input
from module9.d7_worker import run
from module2.interface import canonical_hash
import json
print('Python:', sys.executable, platform.platform())
for name in ('numpy','scipy','jsonschema','mpmath'):
    print(name, importlib.metadata.version(name))
p = seed_input()
validate_point(p)
row = {'point_id':p['benchmark_id'],'arm':'source_oracle','input_sha256':canonical_hash(p),'input':p}
rows, receipt = run((json.dumps(row)+'\n').encode())
assert receipt['evaluation_error'] == 0 and rows[0]['neutrino_status'] == 'INVERSE_TARGET_CLOSURE_PASS'
print('D0_NO_SOURCE_CLOSURE_PASS', rows[0]['neutrino_inverse_relative_residual'])
PY
python3 -m pip --version
python3 -m pip freeze --all | sha256sum
for path in /cvmfs /afs /eos "$HOME"; do
    if [[ -d "$path" ]]; then ls -ld "$path"; fi
done
df -h "$HOME" .
free -m
if command -v klist >/dev/null; then klist -s; fi
if command -v quota >/dev/null; then quota -s; fi
echo 'Confirm AFS submit location/quota, billed CERN account, JobFlavour, OS and worker packages manually.'
echo 'EOS is unused by this pilot; check project EOS credentials/permissions before any future transfer.'
