#!/usr/bin/env bash
# Default is system Python; this is NOT a claim about CERN worker packages.
# If preflight requires CVMFS, replace this with a verified pinned setup path,
# record its release/OS/Python identity below, test, commit, push, then restage.
export ZEE_D7_ENV_ID="SYSTEM_PYTHON_UNVERIFIED_ON_CERN"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
