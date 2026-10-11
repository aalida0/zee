#!/usr/bin/env python3
"""Create an *isolated* SuperIso v5.0 source copy with four NLO clipping
statements disabled for controlled physics validation. Do not patch vendor.

The exact upstream wilson.c SHA256 is pinned to the AF Gate A1L audit.
This is a debug experiment, NOT a peer-reviewed NLO/NNLO implementation.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil

EXPECTED_WILSON_SHA256 = "b3679eec2244917bf062420e69730f91e2bb32a679febd5d0d28db6af5b707bd"
INDICES = (7, 8, 9, 10)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def patch_wilson(source):
    """Return isolated diagnostic variant; reject every unexpected source."""
    lines = source.splitlines(keepends=True)
    patched = list(lines)
    changed = {}
    for i in INDICES:
        symbol = f"C{i}H_1"
        needle = (f"if(cabs({symbol})*alphas_mu/4./pi>cabs(C0w[{i}])) "
                  f"{symbol}*=cabs(C0w[{i}])/cabs({symbol})*4.*pi/alphas_mu;")
        matching = [n for n, line in enumerate(lines) if line.strip()==needle]
        if len(matching)!=1:
            raise ValueError(f"Expected exactly one exact NLO limiter for {symbol}, found {len(matching)}")
        n=matching[0]
        changed[symbol]=n+1
        newline="\n" if lines[n].endswith("\n") else ""
        patched[n] = (f"\t/* Gate A1M DIAGNOSTIC ONLY: remove premature zeroing "
                      f"of {symbol} before C0w[{i}] is set. */"+newline)
    return "".join(patched),changed

def create_isolated(vendor, destination, expected_sha=EXPECTED_WILSON_SHA256):
    vendor=Path(vendor).expanduser().resolve()
    destination=Path(destination).expanduser().resolve()
    if not (vendor/"Makefile").is_file() or not (vendor/"src/wilson.c").is_file():
        raise ValueError("Require complete SuperIso vendor source with Makefile/src/wilson.c")
    if destination == vendor or vendor in destination.parents:
        raise ValueError("Patched destination must be outside the official vendor tree")
    if destination in vendor.parents:
        raise ValueError("Patched destination cannot replace a vendor parent")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite already-existing source directory: {destination}")
    source_path=vendor/"src/wilson.c"
    before=source_path.read_bytes()
    actual_hash=digest(before)
    if actual_hash != expected_sha:
        raise ValueError(f"Unknown vendor wilson.c SHA256 {actual_hash}; expected {expected_sha}")
    try:
        original=before.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Could not decode wilson.c as UTF-8") from exc
    replacement, line_map=patch_wilson(original)
    if len(line_map)!=4:
        raise AssertionError("Not exactly four NLO lines patched")
    shutil.copytree(vendor,destination,symlinks=False)
    new_path=destination/"src/wilson.c"
    new_path.write_text(replacement)
    if digest(source_path.read_bytes()) != actual_hash:
        raise RuntimeError("Vendor wilson.c changed during copying: abort")
    diff="".join(difflib.unified_diff(
        original.splitlines(keepends=True),replacement.splitlines(keepends=True),
        fromfile="vendor/src/wilson.c",tofile="isolated/src/wilson.c",
        n=2,
    ))
    return {
        "status":"ISOLATED_NLO_SOURCE_PATCH_NOT_VALIDATED_FOR_PHYSICAL_BR",
        "vendor_dir":str(vendor),"isolated_dir":str(destination),
        "vendor_wilson_sha256":actual_hash,
        "patched_wilson_sha256":digest(new_path.read_bytes()),
        "changed_symbols":line_map,
        "changed_statement_count":len(line_map),
        "vendor_source_modified":False,
        "patch_diff":diff,
        "physical_Zee_BR_calculated":False,
        "note":"Only diagnostic removal of four premature NLO limiters; "
               "independent formula, scale, and Type-II controls still required.",
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vendor-dir",type=Path,required=True)
    parser.add_argument("--isolated-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    r=create_isolated(args.vendor_dir,args.isolated_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2)+"\n")
    print("Wrote",args.output)
    print("Isolated patched SuperIso:",r["isolated_dir"])
    print("Changed:",r["changed_symbols"])
    print("STATUS:",r["status"])
if __name__=="__main__":
    main()
