#!/usr/bin/env bash
# CERN HTCondor sandbox worker; no network, no shared mutable input needed.
set -euo pipefail
if [[ $# -ne 1 || ! "$1" =~ ^part_[0-9]{3}\.jsonl$ ]]; then
    echo "D7_INVALID_SHARD_ARG" >&2
    exit 64
fi
shard="$1"
[[ -s "$shard" && -s scan_bundle.tar.gz ]] || { echo D7_MISSING_TRANSFER_INPUT >&2; exit 66; }
mkdir -p source
tar -xzf scan_bundle.tar.gz -C source
# The runtime MUST be prevalidated on CERN worker or bound via a documented
# site CVMFS view in the submission environment. Never run pip from workers.
export PYTHONPATH="$PWD/source"
python3 -c 'import numpy, scipy, jsonschema; import module1.scalar_constraints; import module2.interface; import module3.interface'
python3 -m module9.d7_worker \
    --shard "$PWD/$shard" \
    --output "$PWD/results.jsonl" \
    --receipt "$PWD/receipt.json"
