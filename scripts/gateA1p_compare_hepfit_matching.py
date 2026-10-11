#!/usr/bin/env python3
"""Compare independent HEPfit Type-II matching with isolated SuperIso v5.

HEPfit source-derived C_i^(0,1,2) vectors are compared with A1M
(single-charge Type-II, NLO clipping removed) for identical mH/tanbeta,
matching muW and input running mt(muW). This does NOT establish
independent physical inclusive BR accuracy or a Zee exclusion.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re
from gateA1l_check_matching_pilot import parse as parse_superiso

HEPFIT=re.compile(
    r"^HEPFIT order=(\d+) op=(\d+) delta=(\S+) mass=(\S+)$")
INPUT=re.compile(
    r"^INPUT mass=(\S+) tanbeta=(\S+) mt_muW=(\S+) muW=(\S+)$")
TOLERANCES={
    0:{"atol":1.0e-7,"rtol":1.0e-6},
    1:{"atol":2.0e-3,"rtol":5.0e-3},
    2:{"atol":3.5e-1,"rtol":3.0e-2},
}
PRIMARY=(7,8)
SECONDARY={1: (4,), 2: (3,4,5,6)}

def read_hepfit(path):
    content=Path(path).read_text()
    if "HEPFIT_SOURCE_ONLY_NOT_PHYSICAL_BR" not in content:
        raise ValueError("HEPfit independence marker absent")
    inp={}
    rows={}
    for line in content.splitlines():
        m=INPUT.fullmatch(line)
        if m:
            if inp:
                raise ValueError("Duplicate input in HEPfit reference")
            inp=dict(zip(("mass","tanbeta","mt_muW","muW"),
                         map(float,m.groups())))
        m=HEPFIT.fullmatch(line)
        if m:
            order,op=int(m.group(1)),int(m.group(2))
            val,mass=map(float,m.group(3,4))
            if (order,op) in rows or not all(map(math.isfinite,(val,mass))):
                raise ValueError("Invalid or duplicate independent matching row")
            rows[order,op]=(val,mass)
    expected={(order,op) for order in range(3) for op in range(1,9)}
    if set(rows)!=expected or not inp:
        raise ValueError(f"Missing reference rows, got {len(rows)}")
    if not all(math.isfinite(v) and v>0 for v in inp.values()):
        raise ValueError("Invalid HEPfit mass/scale input")
    if any(abs(mass-inp["mass"])>1e-9 for val,mass in rows.values()):
        raise ValueError("HEPfit reference mass changed within file")
    return inp,{k:v for k,(v,mass) in rows.items()}

def compare_mass(superiso_file,hepfit_file,expected_mass,beta):
    reference_input,reference=read_hepfit(hepfit_file)
    si=parse_superiso(superiso_file)
    if abs(reference_input["mass"]-expected_mass)>1e-7:
        raise ValueError("Reference mass mismatch")
    if abs(reference_input["muW"]-si["inputs"]["muW"])>1e-9:
        raise ValueError("High-scale matching muW mismatch")
    if abs(reference_input["tanbeta"]-math.tan(beta))>1e-9:
        raise ValueError("Reference tanbeta mismatch")
    if abs(si["inputs"]["w1"]-1)>1e-12:
        raise ValueError("The control must be pure single-charged-Higgs")
    rows=[]
    for order in (0,1,2):
        ops=sorted(set(PRIMARY)|set(SECONDARY.get(order,())))
        for op in ops:
            expected=reference[order,op]
            sm,observed,_other,zee=si["entries"][order,op]
            if not math.isclose(zee,sm+observed,abs_tol=1e-10,rel_tol=1e-10):
                raise ValueError(f"SuperIso gamma=0 matching closure failed "
                                 f"order={order} op={op}")
            diff=observed-expected
            t=TOLERANCES[order]
            tolerance=t["atol"]+t["rtol"]*max(abs(expected),abs(observed))
            rows.append({
                "mass_GeV":expected_mass,"order":order,"operator":f"C{op}",
                "superiso_isolated_delta":observed,
                "independent_HEPfit_delta":expected,
                "superiso_minus_hepfit":diff,
                "absolute_error":abs(diff),"relative_error":(
                    abs(diff)/max(abs(expected),abs(observed))
                    if max(abs(expected),abs(observed))>1e-15 else 0.),
                "pilot_tolerance":tolerance,
                "numerically_consistent":abs(diff)<=tolerance,
            })
    return rows,reference_input

def report(pairs,beta,source_manifest):
    manifest=json.loads(Path(source_manifest).read_text())
    if manifest.get("upstream_git_blob")!="8029be52c3e2f83490dfe3199f80e5db484dd23b":
        raise ValueError("Reference uses unknown HEPfit source revision")
    rows=[]
    refs=[]
    for mass,si,hepf in pairs:
        sub,ref=compare_mass(si,hepf,mass,beta)
        rows.extend(sub);refs.append(ref)
    if not pairs or len({round(x[0],7) for x in pairs})!=len(pairs):
        raise ValueError("Empty/duplicate mass controls")
    mtset={round(item["mt_muW"],8) for item in refs}
    if len(mtset)!=1:
        raise ValueError("HEPfit running-top input changed between points")
    failed=[r for r in rows if not r["numerically_consistent"]]
    maxerr=max(r["absolute_error"] for r in rows)
    primary_fail=[r for r in failed if r["operator"] in ("C7","C8")]
    # A broad coefficient-level NNLO pilot tolerance is not an
    # accuracy assessment. Surface residuals >1% even when they fit
    # inside the exploratory absolute tolerance.
    precision_flags=[
        r for r in rows if r["order"]==2
        and max(abs(r["independent_HEPfit_delta"]),
                abs(r["superiso_isolated_delta"]))>1e-3
        and r["relative_error"]>0.01
    ]
    if failed:
        stage="INDEPENDENT_HEPFIT_MATCHING_DISCREPANCY_REQUIRES_CONVENTION_AUDIT"
    elif precision_flags:
        stage="INDEPENDENT_HEPFIT_MATCHING_PILOT_WITH_NNLO_PRECISION_FLAGS"
    else:
        stage="INDEPENDENT_HEPFIT_TYPEII_MATCHING_PILOT_CONSISTENT"
    return {
        "status":stage,
        "source":"HEPfit THDMMatching::setWCbsg independent of SuperIso",
        "upstream_git_blob":manifest["upstream_git_blob"],
        "masses_GeV":[x[0] for x in pairs],
        "muW_GeV":refs[0]["muW"],
        "running_mt_muW_GeV":refs[0]["mt_muW"],
        "mt_input_provenance":"Derived once from matching-level LO consistency; "
                              "must be checked independently against SuperIso running_mass",
        "tanbeta":math.tan(beta),
        "model":"One physical Type-II charged Higgs in each control",
        "basis":"HEPfit Misiak basis op i maps to SuperIso Ci via i+1; "
                "equivalence remains subject to explicit source convention audit",
        "tolerances":"Exploratory numerical tolerances, broadest for NNLO "
                     "interpolation/expansion; passing does not certify NNLO accuracy",
        "compared_coefficients":rows,
        "compared_count":len(rows),
        "failed_count":len(failed),
        "failed_primary_C7_C8_count":len(primary_fail),
        "largest_absolute_residual":maxerr,
        "largest_relative_residual":max(r["relative_error"] for r in rows),
        "NNLO_above_one_percent_relative_count":len(precision_flags),
        "NNLO_precision_review_flags":precision_flags,
        "NNLO_publication_precision_validated":False,
        "mismatches":failed,
        "full_bsgamma_independently_validated":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pair",action="append",nargs=3,metavar=("MASS","SUPERISO_TXT","HEPFIT_TXT"),
                    required=True)
    ap.add_argument("--beta",type=float,default=1.394)
    ap.add_argument("--hepfit-provenance",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    pairs=[(float(m),Path(si),Path(hf)) for m,si,hf in a.pair]
    try:
        result=report(pairs,a.beta,a.hepfit_provenance)
        status=0 if result["failed_count"]==0 else 1
    except (ValueError,KeyError) as exc:
        result={
            "status":"INDEPENDENT_HEPFIT_COMPARISON_BLOCKED_INVALID_INPUT",
            "reason":str(exc),
            "full_bsgamma_independently_validated":False,
            "Zee_benchmark_allowed":None,
            "Zee_benchmark_excluded":None,
        }
        status=1
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("Wrote",a.output,"STATUS:",result["status"])
    if "compared_count" in result:
        print("Rows",result["compared_count"],"failures",result["failed_count"])
        for row in result["NNLO_precision_review_flags"][:15]:
            print("NNLO PRECISION REVIEW",row["mass_GeV"],row["operator"],
                  "relative_error=",row["relative_error"])
        for row in result["mismatches"][:15]:
            print("MISMATCH",row["mass_GeV"],row["order"],
                  row["operator"],"SuperIso=",row["superiso_isolated_delta"],
                  "HEPfit=",row["independent_HEPfit_delta"])
    else:
        print("INPUT ERROR:",result["reason"])
    raise SystemExit(status)

if __name__=="__main__":
    main()
