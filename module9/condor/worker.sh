#!/usr/bin/env bash
# Sandbox wrapper. One argument is a LOCAL SIMULATION; three identify Condor.
set -euo pipefail
if [[ ( $# -ne 1 && $# -ne 3 ) || ! "$1" =~ ^part_00[0-3]\.jsonl$ ]]; then
    echo D7_INVALID_SHARD_ARG >&2; exit 64
fi
shard="$1"
export ZEE_D7_EXECUTION_MODE=LOCAL_SIMULATION
unset ZEE_D7_CLUSTER_ID ZEE_D7_PROC_ID
if [[ $# -eq 3 ]]; then
    [[ "$2" =~ ^[0-9]+$ && "$3" =~ ^[0-3]$ ]] || { echo D7_INVALID_JOB_ID >&2; exit 64; }
    export ZEE_D7_EXECUTION_MODE=HTCONDOR ZEE_D7_CLUSTER_ID="$2" ZEE_D7_PROC_ID="$3"
fi
[[ -s "$shard" && -s scan_bundle.tar.gz && -s bundle.sha256 && -s source_commit.txt ]] || { echo D7_MISSING_TRANSFER_INPUT >&2; exit 66; }
[[ ! -e source && ! -e results.jsonl && ! -e receipt.json ]] || { echo D7_REFUSE_REUSED_SANDBOX >&2; exit 66; }
# Strict single-file checksum contract before importing any archived source.
[[ "$(cat bundle.sha256)" =~ ^[0-9a-f]{64}'  scan_bundle.tar.gz'$ ]] || { echo D7_INVALID_BUNDLE_CHECKSUM >&2; exit 65; }
sha256sum --check bundle.sha256
export ZEE_D7_SOURCE_COMMIT="$(cat source_commit.txt)"
export ZEE_D7_BUNDLE_SHA256="$(cut -d ' ' -f 1 bundle.sha256)"
[[ "$ZEE_D7_SOURCE_COMMIT" =~ ^[0-9a-f]{40}$ ]] || { echo D7_INVALID_COMMIT >&2; exit 65; }
# stdlib only: bind archive's Git commit header; reject unsafe archive members.
python3 - <<'PY'
import os
from pathlib import PurePosixPath
import tarfile
with tarfile.open('scan_bundle.tar.gz', 'r:gz') as archive:
    if archive.pax_headers.get('comment') != os.environ['ZEE_D7_SOURCE_COMMIT']:
        raise ValueError('D7_ARCHIVE_COMMIT_MISMATCH')
    for member in archive.getmembers():
        if PurePosixPath(member.name).is_absolute() or '..' in PurePosixPath(member.name).parts or not (member.isfile() or member.isdir()):
            raise ValueError('D7_UNSAFE_ARCHIVE_MEMBER')
PY
mkdir source
tar -xzf scan_bundle.tar.gz -C source
cmp -- "$0" source/module9/condor/worker.sh
source source/module9/condor/environment.sh
export PYTHONPATH="$PWD/source"
python3 -c 'import numpy, scipy, jsonschema, mpmath; import module1.scalar_constraints; import module2.interface; import module3.interface'
python3 -m module9.d7_worker --shard "$PWD/$shard" \
    --output "$PWD/results.jsonl" --receipt "$PWD/receipt.json"
