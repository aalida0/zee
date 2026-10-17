#!/usr/bin/env python3
"""Gate A1V: fast *legacy* Zee b->s gamma response and flavor-only scan.

This is NOT an experimental-likelihood exclusion or modern 2026 NNLO fit.
It uses the exact source-audited A1U helper interposition, keeping the full
mixed high- and low-scale Wilson vectors consistent at every scan point.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

from gateA1r_run_br_pilot import check_superiso_source
from gateA1u_run_legacy_two_state_br import audit_affine_internal_matching

EXPECTED_K=(-1.,0.,0.5,1.,2.)
FLOAT=r"([-+0-9.eE]+)"
LINE_K=re.compile(rf"^A1V_K k={FLOAT} BR={FLOAT}$")
LINE_INPUT=re.compile(
    rf"^A1V_INPUT mH1={FLOAT} mH2={FLOAT} gamma={FLOAT} "
    rf"tanbeta={FLOAT} muW_factor={FLOAT} mub_factor={FLOAT} "
    rf"muW={FLOAT} mub={FLOAT}$")
LINE_DECOMP=re.compile(
    rf"^A1V_DECOMP SM={FLOAT} LINEAR={FLOAT} QUADRATIC={FLOAT} "
    rf"FULL={FLOAT} RESIDUAL_HALF={FLOAT} RESIDUAL_DOUBLE={FLOAT} "
    rf"INDEPENDENT_SM={FLOAT}$")
STATUS="GATE_A1V_LEGACY_QUADRATIC_RESPONSE_NOT_FLAVOUR_EXCLUSION"
COLUMNS=("mH1","mH2","gamma","tanbeta")


def finite(value):
    x=float(value)
    if not math.isfinite(x):
        raise ValueError("Nonfinite numerical field")
    return x


def validate_inputs(m1,m2,gamma,tanbeta):
    if not (200.<=m1<=m2<=10000. and
            0.<=gamma<=math.pi/2 and
            0.25<=tanbeta<=100.):
        raise ValueError("Invalid charged masses, gamma or tanbeta")


def parse_output(stdout,expected):
    lines=stdout.splitlines()
    if lines.count("STATUS "+STATUS)!=1:
        raise ValueError("Missing A1V physical-completion status")
    def unique(pattern):
        found=[m for line in lines if (m:=pattern.fullmatch(line))]
        if len(found)!=1:
            raise ValueError("Missing/duplicate A1V data line")
        return found[0]
    inp=tuple(finite(x) for x in unique(LINE_INPUT).groups())
    for actual,wanted in zip(inp[:6],expected):
        if not math.isclose(actual,wanted,rel_tol=2.e-13,abs_tol=1.e-12):
            raise ValueError("A1V reported input mismatch")
    values={}
    for line in lines:
        if (match:=LINE_K.fullmatch(line)):
            k,br=(finite(x) for x in match.groups())
            if k not in EXPECTED_K or k in values:
                raise ValueError("Unexpected/duplicate NP-strength probe")
            if not 0.<br<0.01:
                raise ValueError("Unphysical A1V branching ratio")
            values[k]=br
    if set(values)!=set(EXPECTED_K):
        raise ValueError("Missing NP-strength probes")
    d=tuple(finite(x) for x in unique(LINE_DECOMP).groups())
    sm,linear,quad,full,res_half,res_double,refsm=d
    for name,actual,wanted in [
        ("SM",sm,values[0.]),
        ("full",full,values[1.]),
        ("linear",linear,(values[1.]-values[-1.])/2.),
        ("quadratic",quad,(values[1.]+values[-1.])/2.-values[0.]),
    ]:
        if not math.isclose(actual,wanted,rel_tol=2.e-12,abs_tol=2.e-14):
            raise ValueError("A1V %s identity failure" % name)
    if abs(res_half)>5e-11 or abs(res_double)>5e-11 or abs(refsm-sm)>2e-12:
        raise ValueError("A1V independent quadratic/SM closure failure")
    return {
        "input":{"mH1":inp[0],"mH2":inp[1],"gamma":inp[2],
                 "tanbeta":inp[3],"muW_factor":inp[4],"mub_factor":inp[5],
                 "muW":inp[6],"mub":inp[7]},
        "SM_BR":sm,"linear_delta_BR":linear,
        "quadratic_delta_BR":quad,"full_Zee_BR":full,
        "total_NP_shift_BR":full-sm,
        "quadratic_over_total_shift":
            (quad/(full-sm) if abs(full-sm)>1e-15 else None),
        "br_by_np_strength":{str(k):values[k] for k in EXPECTED_K},
        "quadratic_half_residual":res_half,
        "quadratic_double_residual":res_double,
        "independent_SM_BR":refsm,
        "classification":"LEGACY_FLAVOUR_OBSERVABLE_ONLY_NO_EXCLUSION",
    }


def build(root,output):
    lib=root/"src"/"libsuperiso.a"
    source=Path(__file__).with_name("gateA1v_legacy_response.c")
    if not lib.is_file() or not source.is_file():
        raise ValueError("Pinned library or Gate A1V C file unavailable")
    if lib.stat().st_mtime_ns < max(
        (root/"src"/"wilson.c").stat().st_mtime_ns,
        (root/"src"/"bsgamma.c").stat().st_mtime_ns):
        raise ValueError("Stale SuperIso archive; preserve A1M provenance")
    cc=shutil.which("gcc")
    if not cc: raise ValueError("gcc unavailable")
    cmd=[cc,"-O2","-std=gnu99","-Wall","-Wextra",
         "-I"+str(root/"src"),str(source),
         "-Wl,--wrap=CW_calculator",str(lib),"-lm","-o",str(output)]
    p=subprocess.run(cmd,capture_output=True,text=True,check=False,timeout=120)
    if p.returncode:
        raise RuntimeError("Gate A1V compile error: "+p.stderr[-3500:])
    return {
        "cmd":cmd,
        "library_SHA256":hashlib.sha256(lib.read_bytes()).hexdigest(),
        "driver_SHA256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "compile_stderr":p.stderr[-1000:],
    }


def evaluate(exe,m1,m2,gamma,tanbeta,fw=1.,fb=1.):
    inputs=(m1,m2,gamma,tanbeta,fw,fb)
    args=[str(exe.resolve()),*[f"{x:.17g}" for x in inputs],
          "helper_reload"]
    p=subprocess.run(args,capture_output=True,text=True,timeout=180,
                     check=False)
    if p.returncode:
        raise RuntimeError(
            "A1V kernel failure code=%s args=%r\nstdout=%s\nstderr=%s"
            % (p.returncode,args,p.stdout[-1500:],p.stderr[-1500:]))
    return parse_output(p.stdout,inputs),p.stdout


def iter_grid(csv_path,max_points):
    with csv_path.open(newline="") as handle:
        reader=csv.DictReader(handle)
        if reader.fieldnames is None or any(x not in reader.fieldnames
                                            for x in COLUMNS):
            raise ValueError("Scan CSV requires mH1,mH2,gamma,tanbeta columns")
        for i,row in enumerate(reader):
            if i>=max_points:
                raise ValueError("CSV exceeds --max-points; refuse truncation")
            point=tuple(finite(row[x]) for x in COLUMNS)
            validate_inputs(*point)
            yield point


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vendor-root",required=True,type=Path)
    ap.add_argument("--a1m-provenance",required=True,type=Path)
    ap.add_argument("--a1u-result",required=True,type=Path)
    ap.add_argument("--output-dir",required=True,type=Path)
    ap.add_argument("--grid-csv",type=Path,
                    help="Optional Zee charged-sector flavor-only CSV")
    ap.add_argument("--max-points",type=int,default=1000)
    ap.add_argument("--mH1",type=float,default=300.)
    ap.add_argument("--mH2",type=float,default=700.)
    ap.add_argument("--gamma",type=float,default=1.089)
    ap.add_argument("--tanbeta",type=float,default=5.597170833164245)
    ap.add_argument("--skip-scale-diagnostic",action="store_true")
    a=ap.parse_args()
    validate_inputs(a.mH1,a.mH2,a.gamma,a.tanbeta)
    if a.max_points<1: ap.error("max-points must be positive")
    source=check_superiso_source(a.vendor_root,a.a1m_provenance)
    audit=audit_affine_internal_matching(a.vendor_root)
    if audit["internal_CW_mode"]!="helper_reload" or source[
        "bsgamma_internal_CW_reload_detected"]:
        raise ValueError("A1V requires the audited SuperIso v5 nested helper reload")
    legacy=json.loads(a.a1u_result.read_text())
    if legacy.get("status")!=(
        "GATE_A1U_FULL_LEGACY_SUPERISO_TWO_STATE_BR_ENDPOINT_CLOSED_NOT_2026_EXCLUSION"
    ) or not legacy.get("all_A1R_physical_endpoint_checks_pass"):
        raise ValueError("A1V requires genuine successful A1U AF endpoint closure")
    benchmark=legacy["benchmark"]
    for key,val in (("mH1_GeV",a.mH1),("mH2_GeV",a.mH2),
                    ("gamma_rad",a.gamma),("tanbeta",a.tanbeta)):
        if not math.isclose(finite(benchmark[key]),val,
                            rel_tol=1e-12,abs_tol=1e-10):
            raise ValueError("Requested benchmark differs from A1U provenance")

    a.output_dir.mkdir(parents=True,exist_ok=True)
    exe=a.output_dir/"gateA1v_legacy_response"
    built=build(a.vendor_root,exe)
    baseline,raw=evaluate(exe,a.mH1,a.mH2,a.gamma,a.tanbeta)
    if not math.isclose(
        baseline["full_Zee_BR"],finite(benchmark["full_legacy_Zee_BR"]),
        rel_tol=2e-8,abs_tol=4e-11):
        raise ValueError("A1V baseline does not reproduce verified Gate A1U")
    if not math.isclose(baseline["SM_BR"],finite(legacy["SM_BR_legacy"]),
                        rel_tol=2e-8,abs_tol=4e-11):
        raise ValueError("A1V SM differs from verified A1U")

    scale_rows=[]
    scales=(() if a.skip_scale_diagnostic else
            ((0.75,1.),(1.25,1.),(1.,0.75),(1.,1.25)))
    for fw,fb in scales:
        point,_=evaluate(exe,a.mH1,a.mH2,a.gamma,a.tanbeta,fw,fb)
        scale_rows.append(point)
    grid=[]
    if a.grid_csv:
        for m1,m2,g,t in iter_grid(a.grid_csv,a.max_points):
            result,_=evaluate(exe,m1,m2,g,t)
            grid.append(result)
    report={
        "status":"GATE_A1V_LEGACY_RESPONSE_AND_SCAN_PILOT_NOT_EXCLUSION",
        "benchmark":baseline,
        "scale_diagnostic_not_theory_uncertainty":scale_rows,
        "scan_flavour_only":grid,
        "n_scan_points":len(grid),
        "a1u_provenance":str(a.a1u_result),
        "a1m_source_audit":source,
        "nested_helper_audit":audit,
        "build":built,
        "quadratic_interpolation_closure_required":True,
        "modern_2026_full_NNLO_validated":False,
        "theory_uncertainty_calibrated":False,
        "experimental_likelihood_validated":False,
        "Zee_model_allowed":None,
        "Zee_model_excluded":None,
    }
    dest=a.output_dir/"gateA1v_legacy_response.json"
    dest.write_text(json.dumps(report,indent=2)+"\n")
    (a.output_dir/"gateA1v_nominal_raw.log").write_text(raw)
    if grid:
        target=a.output_dir/"scan_flavour_only.csv"
        with target.open("w",newline="") as out:
            cols=[*COLUMNS,"SM_BR","linear_delta_BR","quadratic_delta_BR",
                  "full_Zee_BR","quadratic_over_total_shift","classification"]
            writer=csv.DictWriter(out,fieldnames=cols)
            writer.writeheader()
            for x in grid:
                writer.writerow({**{key:x["input"][key] for key in COLUMNS},
                                 **{key:x[key] for key in cols
                                    if key not in COLUMNS}})
        print("FLAVOUR_ONLY_GRID_CSV",target)
    print("STATUS",report["status"])
    print("LEGACY_ZEE_BR",f"{baseline['full_Zee_BR']:.15g}")
    print("LINEAR_NP_SHIFT",f"{baseline['linear_delta_BR']:.15g}")
    print("QUADRATIC_NP_SHIFT",f"{baseline['quadratic_delta_BR']:.15g}")
    print("NUM_SCALE_DIAGNOSTICS",len(scale_rows))
    print("NUM_FLAVOUR_ONLY_POINTS",len(grid))
    print("2026_NNLO_VALIDATED False")
    print("EXCLUSION_CALCULATED False")
    print("Wrote",dest)


if __name__=="__main__":
    main()
