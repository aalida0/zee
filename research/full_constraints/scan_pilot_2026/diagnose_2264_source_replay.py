#!/usr/bin/env python3
"""Fail-closed provenance diagnostics for historical Zee point 2264 IO family 1.

This script is intentionally read-only. A digest mismatch is an unresolved
provenance failure, even if the numerical neutrino closure or partial LFV
rate happens to agree. It must NOT be interpreted as physical acceptance.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

from module14.scan import digest, neutrino_input
from module2.interface import canonical_hash, evaluate as neutrino_evaluate
from research.full_constraints.scan_pilot_2026.historical_certified_texture import (
    ORIGINAL_DATASET_SHA,
    SCANNER_SEED,
    source_points,
)


def diagnose():
    point = next(p for p in source_points() if p["id"] == 2264)
    original = next(
        f for f in point["families"]
        if f["ordering"] == "IO" and f["family"] == 1
    )
    row = {
        "id": point["id"],
        "scalar": point["input_card"],
        "scalar_sha256": point["scalar_sha256"],
    }
    seed, spec, inp = neutrino_input(row, SCANNER_SEED, "IO", 1)
    seed2, spec2, inp2 = neutrino_input(row, SCANNER_SEED, "IO", 1)
    hashes = {
        "seed": {"frozen": original["seed_sha256"], "regenerated": seed},
        "inverse_input": {
            "frozen": original["input_sha256"],
            "regenerated": digest(inp),
        },
        "target_eV": {
            "frozen": original["target_sha256"],
            "regenerated": digest(inp["target_eV"]),
        },
        "scalar": {
            "frozen": point["scalar_sha256"],
            "regenerated": canonical_hash(point["input_card"]),
        },
    }
    for name, pair in hashes.items():
        pair["identical"] = pair["frozen"] == pair["regenerated"]
    out = {
        "schema": "zee-2264-input-digest-portability-diagnostic-v1",
        "source_20k_dataset_sha256": ORIGINAL_DATASET_SHA,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "seed": SCANNER_SEED,
        "scalar_id": 2264,
        "ordering": "IO",
        "family": 1,
        "hashes": hashes,
        "target_spec_identical": spec == original["target_spec"],
        "two_regenerations_identical_in_same_process": (
            seed == seed2 and spec == spec2 and digest(inp) == digest(inp2)
        ),
        "yukawa_hashes": {},
        "physical_LFV": "UNKNOWN",
        "physical_B": "UNKNOWN",
        "global_acceptance": None,
    }
    try:
        nu = neutrino_evaluate(inp)
        out["neutrino_relative_closure"] = nu["inverse"]["family_relative_residual"]
        out["yukawa_hashes"] = {
            key: {
                "frozen": original["yukawa_sha256"][key],
                "regenerated": canonical_hash(nu[key]),
                "identical": (
                    original["yukawa_sha256"][key] == canonical_hash(nu[key])
                ),
            }
            for key in ("F", "D", "Ye", "Ye2")
        }
    except Exception as exc:
        out["neutrino_replay_error"] = {
            "type": type(exc).__name__, "message": str(exc)
        }
    out["all_frozen_source_hashes_matched"] = (
        all(p["identical"] for p in hashes.values())
        and out["target_spec_identical"]
        and out["two_regenerations_identical_in_same_process"]
        and len(out["yukawa_hashes"]) == 4
        and all(p["identical"] for p in out["yukawa_hashes"].values())
    )
    out["status"] = (
        "ORIGINAL_SOURCE_REPLAY_MATCH"
        if out["all_frozen_source_hashes_matched"]
        else "SOURCE_REPLAY_MISMATCH_NOT_PHYSICS_VALIDATED"
    )
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--require-match", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Never overwrite a diagnostic receipt")
    out = diagnose()
    args.output.write_text(
        json.dumps(out, sort_keys=True, indent=2, allow_nan=False) + "\n"
    )
    print(json.dumps(out, sort_keys=True), flush=True)
    if args.require_match and not out["all_frozen_source_hashes_matched"]:
        sys.exit("FAIL_CLOSED: historical Zee source hashes not reproduced")


if __name__ == "__main__":
    main()
