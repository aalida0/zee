#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
exec "${PYTHON:-python3}" -m module1.validate
