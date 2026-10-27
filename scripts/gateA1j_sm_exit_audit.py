#!/usr/bin/env python3
"""Audit SuperIso v5 SM driver completion and source-defined exit status.

SuperIso 5.0 vendor sm.c ends with 'return 1;' even after printing all
SM predictions. Accept exit 1 ONLY if that exact trailing source-code
contract and a complete, sane output are independently observed.
Never patch vendor sources or silently discard execution errors.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re


def _without_comments(source: str) -> str:
    """Remove C comments for precise trailing-return check."""
    source = re.sub(r"/\*[\s\S]*?\*/", "", source)
    return re.sub(r"//[^\n]*", "", source)


def audit_sm_exit(source: Path, log: Path, exit_code: int) -> dict:
    c_source = source.read_text(errors="replace") if source.is_file() else ""
    output = log.read_text(errors="replace") if log.is_file() else ""
    # The final statement must be literally return 1; at the end of main.
    source_returns_one = bool(
        re.search(r"\breturn\s+1\s*;\s*}\s*$",
                  _without_comments(c_source))
    )
    match = re.search(
        r"(?m)^BR\(b->s gamma\)\s+"
        r"([0-9]+(?:\.[0-9]*)?(?:[eE][+-]?[0-9]+)?)\s*$",
        output,
    )
    br = float(match.group(1)) if match else None
    br_sensible = br is not None and math.isfinite(br) and 1e-4 <= br <= 6e-4
    has_header = ("SuperIso v5.0 - 2025" in output
                  and "Standard Model predictions" in output)
    # The final kaon-mode observable appears after all other SM entries in
    # the actual v5 sm.c / AF output. Prevent truncated runs from passing.
    last_observable = bool(re.search(
        r"(?m)^Br\(KL->pi0mumu\)_dest-interf\.:\s*"
        r"[0-9]+(?:\.[0-9]*)?(?:[eE][+-]?[0-9]+)?\s*$",
        output,
    ))
    complete = bool(has_header and br_sensible and last_observable)
    conventional = exit_code == 0 and complete
    known_upstream = exit_code == 1 and source_returns_one and complete
    accepted = conventional or known_upstream
    return {
        "status": ("PASS_SOURCE_VERIFIED_EXIT1" if known_upstream else
                   "PASS_EXIT0" if conventional else "FAIL_INCOMPLETE_OR_UNKNOWN_EXIT"),
        "sm_exit_code": exit_code,
        "sm_c_ends_in_return_1": source_returns_one,
        "expected_sm_header_present": has_header,
        "br_b_to_s_gamma_sm": br,
        "br_b_to_s_gamma_sane": br_sensible,
        "last_printed_observable_present": last_observable,
        "output_complete": complete,
        "smoke_accepted": accepted,
        "interpretation": "SM driver smoke test; NOT a Zee prediction",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("sm_source", type=Path)
    p.add_argument("sm_output_log", type=Path)
    p.add_argument("exit_code", type=int)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = audit_sm_exit(a.sm_source, a.sm_output_log, a.exit_code)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"SM exit audit: {result['status']}; "
          f"BR_SM={result['br_b_to_s_gamma_sm']}; exit={a.exit_code}")
    return 0 if result["smoke_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
