#!/usr/bin/env python3
"""Reproduce SELECTED official HyperIso v1.0.3 CLI cases, fail-closed.

This is an upstream R1/R3/R6 *runtime reference* verifier. It is NOT
a Zee two-charged-state integration, convention proof, or 2026 BR prediction.
Uses pinned upstream normalizer/comparator; never changes expected outputs.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

PIN="09d26ac6e71d1528922097a896d15693589f636b"
VERSION="1.0.3"
CASES=("R1","R3","R6")

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise ValueError(f"Cannot load {path}")
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def checked_run(cmd,cwd,timeout=180):
    return subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=timeout)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream",type=Path,required=True,help="External checkout of tag v1.0.3")
    p.add_argument("--binary",type=Path,required=True,help="Built hyperiso-ui binary")
    p.add_argument("--output",type=Path,required=True,help="Ignored local JSON report")
    a=p.parse_args()
    root=a.upstream.resolve(strict=True)
    binary=a.binary.resolve(strict=True)
    if not binary.is_file() or not os.access(binary,os.X_OK):
        raise ValueError("Executable hyperiso-ui required")
    head=checked_run(["git","rev-parse","HEAD"],root)
    if head.returncode or head.stdout.strip()!=PIN:
        raise ValueError("HyperIso checkout is not pinned v1.0.3 release commit")
    version=checked_run([str(binary),"--version"],root)
    if version.returncode or version.stdout.strip()!=VERSION:
        raise ValueError("HyperIso binary version does not equal 1.0.3")
    rep=root/"reproducibility"
    manifest=rep/"manifest.json"
    parsed=json.loads(manifest.read_text())
    if parsed.get("hyperiso_version")!=VERSION:
        raise ValueError("Manifest version mismatch")
    examples={x["id"]:x for x in parsed["examples"]}
    if not set(CASES)<=set(examples):raise ValueError("Missing official cases")
    expected=rep/"expected_outputs"
    normalizer=module(rep/"scripts/normalize_cli_output.py","hyperiso_normalizer")
    checker=module(rep/"scripts/check_expected_outputs.py","hyperiso_checker")
    metadata_errors=checker.validate_reference_metadata(expected,parsed)
    if metadata_errors:raise ValueError("Reference hash/metadata mismatch: "+str(metadata_errors[:3]))
    output_path=a.output.resolve()
    if str(output_path).startswith(str(expected.resolve())+os.sep):
        raise ValueError("Never write into upstream expected_outputs")
    target=output_path.parent/"hyperiso_runtime"
    target.mkdir(parents=True,exist_ok=True)
    results={}
    for case in CASES:
        spec=examples[case]
        argv=shlex.split(spec["command"])
        if not argv or argv[0]!="hyperiso-ui":
            raise ValueError("Invalid frozen command: "+case)
        cmd=[str(binary)]+argv[1:]
        try:
            run=checked_run(cmd,root,timeout=240)
            if run.returncode:raise ValueError(f"CLI exit {run.returncode}: {run.stderr[:500]}")
            if run.stderr.strip():raise ValueError(f"Nonempty stderr: {run.stderr[:500]}")
            normalized=normalizer.normalize(run.stdout)
            path=target/spec["stdout"]
            path.write_text(normalized)
            failures=checker.compare_text(expected/spec["stdout"],path,
                spec["abs_tol"],spec["rel_tol"])
            results[case]={"status":"PASS" if not failures else "FAIL",
                           "failures":failures[:5],
                           "sha256":sha(path),
                           "source_expected_sha256":sha(expected/spec["stdout"]),
                           "qmatch_GeV":81 if case in ("R1","R6") else None}
        except (ValueError,subprocess.TimeoutExpired,OSError) as exc:
            results[case]={"status":"BLOCKED","error":str(exc)}
    payload={"schema_version":"1.0.0","status":"REFERENCE_RUNTIME_PASS" if all(
             v["status"]=="PASS" for v in results.values()) else "REFERENCE_RUNTIME_PARTIAL",
             "physics_scope":"HYPERISO_UPSTREAM_REFERENCE_ONLY_NOT_ZEE_BR",
             "hyperiso_version":VERSION,"release_commit":PIN,
             "manifest_sha256":sha(manifest),"results":results,
             "zee_operator_matching":"UNKNOWN",
             "zee_two_scalar_injection":"NOT_EVALUATED",
             "misiak_2026_formula_used":False,
             "limitations":["R1/R6 use qmatch=81 GeV, not Misiak 2026 mu0=160 GeV.",
                            "A passing upstream runtime check does not demonstrate Zee matching, two-state injection, or updated 2026 SM prediction."]}
    output_path.parent.mkdir(parents=True,exist_ok=True)
    temp=output_path.with_name(output_path.name+".tmp")
    temp.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n")
    temp.replace(output_path)
    print(payload["status"])
    return 0 if payload["status"]=="REFERENCE_RUNTIME_PASS" else 2

if __name__=="__main__":
    sys.exit(main())
