#!/usr/bin/env python3
"""F4b independent HEPfit Type-II LO/NLO matching at exact F4 inputs.

Eight pure Type-II cases at muW=160 GeV, tanbeta 5.6/50.
Compares C7,C8 LO/NLO and C4 NLO; excludes all NNLO matching/rates.
Uses existing SHA-pinned A1P HEPfit source/binary and the F4b A1M RG
probe. A successful comparison is NOT inclusive NLO validation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import traceback

OK = "F4B_INDEPENDENT_MATCHING_LO_NLO_8_NUMERICALLY_CONSISTENT_NOT_RATE"
BLOCK = "F4B_INDEPENDENT_MATCHING_BLOCKED_NO_RATE"
OPS = ((0,7), (0,8), (1,4), (1,7), (1,8))
SOURCE_BLOB = "8029be52c3e2f83490dfe3199f80e5db484dd23b"


def value(x, name):
    n = float(x)
    if not math.isfinite(n):
        raise ValueError("Nonfinite " + name)
    return n


def load_reference(a1p: Path) -> tuple[Path, dict]:
    from gateA1p_prepare_hepfit_matching import (
        HEPFIT_BLOB, git_blob_sha, extract)
    if SOURCE_BLOB != HEPFIT_BLOB:
        raise ValueError("Independent HEPfit canonical Git blob changed")
    source = a1p / "HEPfit_THDMMatching.cpp"
    cpp = a1p / "hepfit_matching.cpp"
    exe = a1p / "hepfit_matching"
    manifest = json.loads((a1p / "hepfit_provenance.json").read_text())
    original = source.read_bytes()
    if (git_blob_sha(original) != SOURCE_BLOB or
        manifest.get("upstream_git_blob") != SOURCE_BLOB or
        manifest.get("upstream_source_sha256") != hashlib.sha256(original).hexdigest()):
        raise ValueError("HEPfit independent original matching source no longer pinned")
    extracted = extract(original.decode("utf-8"))
    if extracted not in cpp.read_text():
        raise ValueError("Generated HEPfit shim lacks exact upstream function")
    sha = hashlib.sha256(exe.read_bytes()).hexdigest()
    audit = (a1p / "source_binaries_sha256.txt").read_text().splitlines()
    previously = {}
    for line in audit:
        vals = line.split(maxsplit=1)
        if len(vals) == 2:
            previously[Path(vals[1].strip("* ")).name] = vals[0]
    for name,path in (("hepfit_matching",exe),
                      ("hepfit_matching.cpp",cpp),
                      ("HEPfit_THDMMatching.cpp",source)):
        if previously.get(name) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError("Existing A1P recorded source/binary fingerprint changed: "+name)
    return exe, {"original_git_blob": SOURCE_BLOB,
                 "hepfit_binary_sha256":sha,
                 "hepfit_original_source_sha256":hashlib.sha256(original).hexdigest(),
                 "generated_source_sha256":hashlib.sha256(cpp.read_bytes()).hexdigest()}


def prior_run(path: Path) -> tuple[dict, list[tuple[float,float]]]:
    data = json.loads(path.read_text())
    if data.get("status") != (
        "F4B_ORDER_RESOLVED_DIPOLE_PROJECTOR_NOT_FULL_NLO_RATE"):
        raise ValueError("F4b prior source projector did not complete")
    controls = data.get("typeII_results")
    pairs = [(value(r["mass_GeV"], "mass"), value(r["tanbeta"], "tanbeta"))
             for r in controls]
    if (len(pairs) != 8 or len(set(pairs)) != 8
        or set(pairs) != {(m,t) for t in (5.6,50.) for m in (300.,580.,670.,1000.)}):
        raise ValueError("Missing/changed F4b exact Type-II cohort")
    if (data.get("source_running_parameters", {}).get("muW") != 160.0
        or data.get("NLO_operator_scheme_mapping_certified") is not False):
        raise ValueError("F4b source scale/status contract changed")
    return data,pairs


def calc(f4b: dict, pairs: list, a1p: Path, out: Path) -> tuple[list,dict]:
    from zee_gateF3_fullNLO_source_RG_27 import probe
    from gateA1p_compare_hepfit_matching import read_hepfit
    exe, evidence = load_reference(a1p)
    probe_exe = Path(f4b["source_rg_probe_build"]["compiler_command"][-1]).resolve()
    # F4b's actual executable comes from its *own* audited work directory,
    # not from a build guessed from GitHub. It is source-linked and hashed.
    if not probe_exe.is_file():
        raise ValueError("F4b pinned RG probe absent on AF")
    expected_hash = f4b.get("source_rg_probe_executable_sha256")
    if not expected_hash or hashlib.sha256(probe_exe.read_bytes()).hexdigest() != expected_hash:
        raise ValueError("F4b RG executable fingerprint changed")
    env = os.environ.copy()
    paths = a1p / "hepfit_runtime_library_paths.txt"
    if paths.is_file():
        lines = paths.read_text().splitlines()
        candidates = [line[len("LD_LIBRARY_PATH="):]
                      for line in lines if line.startswith("LD_LIBRARY_PATH=")]
        if len(candidates) != 1:
            raise ValueError("Invalid A1P runtime library path provenance")
        from_prior = candidates[0].split(":")
        if any(not Path(s).is_absolute() or Path(s).is_relative_to(Path("/data"))
               for s in from_prior if s):
            raise ValueError("Unsafe or relative runtime path in prior HEPfit environment")
        env["LD_LIBRARY_PATH"] = candidates[0] + (
            ":"+env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    check = subprocess.run(["ldd",str(exe)], capture_output=True, text=True,
                           env=env, timeout=30, check=True)
    if "not found" in check.stdout:
        raise RuntimeError("Pinned HEPfit loader missing dependencies: "+
                           check.stdout[-1200:])
    muw = f4b["source_running_parameters"]["muW"]
    top = f4b["source_running_parameters"]["mt_running_muW"]
    out_rows = []
    for mass,tanb in pairs:
        source = probe(probe_exe, mass, mass, tanb, 0.)
        cmd = [str(exe), f"{tanb:.17g}", f"{top:.17g}",
               f"{muw:.17g}", f"{mass:.17g}"]
        run = subprocess.run(cmd, capture_output=True, text=True, cwd=a1p,
                             env=env, timeout=120, check=True)
        name = out / f"HEPfit_m{mass:.0f}_tb{str(tanb).replace('.','p')}.txt"
        name.write_text(run.stdout)
        inp,reference=read_hepfit(name)
        if (abs(inp["mass"]-mass)>1e-10 or
            abs(inp["tanbeta"]-tanb)>1e-10 or
            abs(inp["mt_muW"]-top)>1e-10 or
            abs(inp["muW"]-muw)>1e-10):
            raise ValueError("HEPfit independently evaluated different matching inputs")
        for order,op in OPS:
            si = value(source[0 if order==0 else 2,op][
                "high_LO" if order==0 else "high_NLO"], "SuperIso high matching")
            hf = value(reference[order,op], "HEPfit independent high matching")
            absres = abs(si-hf)
            # Relative 2e-5; small absolute floor only for zero-like WCs.
            tolerance = 2.e-10 + 2.e-5*max(abs(si),abs(hf))
            out_rows.append({
                "mass_GeV":mass, "tanbeta":tanb, "muW_GeV":muw,
                "mt_running_muW_GeV":top,
                "order":order,"operator":f"C{op}",
                "SuperIso_delta":si,"HEPfit_delta":hf,
                "absolute_residual":absres,
                "relative_residual":absres/max(abs(si),abs(hf),1.e-15),
                "diagnostic_tolerance":tolerance,
                "matching_pass":absres<=tolerance,
                "NLO_full_observable_validated":False,
            })
    if len(out_rows) != 40:
        raise ValueError("Expected exactly 8x5 high matching comparisons")
    return out_rows,evidence


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--f4b-summary",type=Path,required=True)
    ap.add_argument("--a1p-existing-dir",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    cwd=Path.cwd().resolve()
    out=args.output_dir.resolve()
    if not cwd.is_relative_to(Path("/home")) or not out.is_relative_to(cwd/"work"):
        ap.error("Execute from the AF repo /home; write only to its work/")
    if out.exists() and any(out.iterdir()):
        ap.error("Refuse to overwrite previous results")
    out.mkdir(parents=True,exist_ok=True)
    report={"status":BLOCK,"Zee_allowed_or_excluded":None}
    status=1
    try:
        source,pairs=prior_run(args.f4b_summary)
        rows,evidence=calc(source,pairs,args.a1p_existing_dir.resolve(),out)
        with (out/"F4b_independent_TypeII_LO_NLO_matching_40.csv").open(
             "w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
        bad=[r for r in rows if not r["matching_pass"]]
        report={
            "status":OK if not bad else BLOCK,
            "tested_rows":len(rows),"matching_disagreements":len(bad),
            "worst_relative_residual":max(r["relative_residual"] for r in rows),
            "max_abs_residual":max(r["absolute_residual"] for r in rows),
            "source_provenance":evidence,
            "prior_F4b_summary_sha256":
                hashlib.sha256(args.f4b_summary.read_bytes()).hexdigest(),
            "rows":rows,
            "operator_basis_and_NLO_finite_scheme_certified":False,
            "full_inclusive_NLO_rate_validated":False,
            "paper_ready_Zee_95CL_exclusions":False,
            "Zee_allowed_or_excluded":None}
        status=0 if not bad else 1
    except Exception as exc:
        report={"status":BLOCK,"error":repr(exc),
                "traceback":traceback.format_exc(),
                "Zee_allowed_or_excluded":None}
        print("F4B_HEPFIT_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
    finally:
        (out/"summary.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print("F4B_HEPFIT_STATUS", report["status"],
              "F4B_HEPFIT_SUMMARY",out/"summary.json",flush=True)
    return status


if __name__=="__main__":
    raise SystemExit(main())
