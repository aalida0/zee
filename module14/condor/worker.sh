#!/usr/bin/env bash
# Run inside a fresh HTCondor scratch directory.
if [[ $# -ne 1 || ! "$1" =~ ^shard_[0-9]+\.jsonl$ ]]; then echo 'Invalid shard name' >&2; exit 64; fi
shard="$1"
for file in "$shard" scan_bundle.tar.gz bundle.sha256 source_commit.txt config.json job_settings.json; do
    if [[ ! -s "$file" ]]; then echo "Missing $file" >&2; exit 66; fi
done
if [[ -e source || -e results.jsonl || -e receipt.json ]]; then echo 'Sandbox already used' >&2; exit 66; fi
if ! [[ "$(cat bundle.sha256)" =~ ^[0-9a-f]{64}'  scan_bundle.tar.gz'$ ]]; then echo 'Invalid checksum format' >&2; exit 65; fi
sha256sum -c bundle.sha256 || exit 65
export ZEE_D14_SOURCE_COMMIT="$(cat source_commit.txt)"
export ZEE_D14_BUNDLE_SHA256="$(cut -d ' ' -f 1 bundle.sha256)"
if ! [[ "$ZEE_D14_SOURCE_COMMIT" =~ ^[0-9a-f]{40}$ ]]; then exit 65; fi
python3 - <<'PY'
import os
from pathlib import PurePosixPath
import tarfile
with tarfile.open('scan_bundle.tar.gz', 'r:gz') as a:
    if a.pax_headers.get('comment') != os.environ['ZEE_D14_SOURCE_COMMIT']:
        raise ValueError('Archive commit mismatch')
    for m in a:
        p = PurePosixPath(m.name)
        if p.is_absolute() or '..' in p.parts or not (m.isfile() or m.isdir()):
            raise ValueError('Unsafe archive member')
PY
if [[ $? -ne 0 ]]; then exit 65; fi
mkdir source || exit 66
tar -xzf scan_bundle.tar.gz -C source || exit 65
cmp "$0" source/module14/condor/worker.sh || exit 65
export PYTHONPATH="$PWD/source"
python3 -m module14.condor.job "$PWD/$shard"
