#!/usr/bin/env bash
# Stage only committed code. Never connects to CERN or submits jobs.
set -euo pipefail
[[ $# -le 1 ]] || { echo 'Usage: zee_d7_stage.sh [fresh_output_dir]' >&2; exit 64; }
repo="$(git rev-parse --show-toplevel)"
cd "$repo"
[[ "$(git branch --show-current)" == feature/zee-d7-lxplus-condor-scan-pilot ]] || { echo D7_WRONG_BRANCH >&2; exit 65; }
git merge-base --is-ancestor a39afed7cd0ee7f4358dabdbde32729818f1f909 HEAD
[[ -z "$(git status --porcelain)" ]] || { echo D7_REFUSE_DIRTY_TREE >&2; exit 65; }
run="${1:-$repo/validation/module9/local/d7_pilot}"
[[ ! -e "$run" ]] || { echo "D7_REFUSE_OVERWRITE_EXISTING_BATCH_RUN: $run" >&2; exit 66; }
mkdir -p "$run"
run="$(cd "$run" && pwd)"
git archive --format=tar HEAD | gzip -n -c > "$run/scan_bundle.tar.gz"
snapshot="$(mktemp -d)"
trap 'rm -rf -- "$snapshot"' EXIT
tar -xzf "$run/scan_bundle.tar.gz" -C "$snapshot"
# Generate and copy from the archive, never an untracked local Python module.
(cd "$snapshot" && PYTHONPATH="$snapshot" python3 -m module9.d7_prepare \
    --seed module3/example.json --output-dir "$run/input")
mv "$run/input/manifest.json" "$run/input/shards.txt" "$run/input/shards" "$run/"
rmdir "$run/input"
cp "$snapshot/module9/condor/worker.sh" "$run/worker.sh"
cp "$snapshot/module9/condor/d7_pilot.sub" "$run/d7_pilot.sub"
chmod 700 "$run/worker.sh"
mkdir "$run/logs" "$run/results" "$run/status"
(cd "$run" && sha256sum scan_bundle.tar.gz > bundle.sha256)
git rev-parse HEAD > "$run/source_commit.txt"
python3 - "$run" <<'PY'
import hashlib
import json
from pathlib import Path
import sys
p = Path(sys.argv[1])
m = json.loads((p / 'manifest.json').read_text())
m['execution_source_commit'] = (p / 'source_commit.txt').read_text().strip()
m['source_bundle_sha256'] = (p / 'bundle.sha256').read_text().split()[0]
import tarfile
with tarfile.open(p / 'scan_bundle.tar.gz') as archive:
    m['environment_setup_sha256'] = hashlib.sha256(archive.extractfile('module9/condor/environment.sh').read()).hexdigest()
m['staged_artifact_sha256'] = {name:hashlib.sha256((p / name).read_bytes()).hexdigest()
    for name in ('worker.sh','d7_pilot.sub','source_commit.txt','bundle.sha256','shards.txt')}
(p / 'manifest.json').write_text(json.dumps(m, sort_keys=True, indent=2, allow_nan=False)+'\n')
PY
echo "D7_STAGED_UNSUBMITTED $run"
echo 'Validate CERN environment, account/quota and submit policy before manual submission.'
