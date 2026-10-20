#!/usr/bin/env python3
"""Gate E4A — ONE large source-pinned high-order matching + Type-II anchor audit.

Run *all together*:
 (1) 27 E3 spectra × 5 physical gamma choices × all 8 LEFT operators
     at QCD orders 0/1/2, against existing A1M isolated SuperIso v5;
 (2) 9 pure-Type-II masses × 2 tanβ = 18 anchors, including 670 GeV;
 (3) source-pinned 2012 original-author A1Q Mathematica 48-value
     NNLO discrepancy/residual audit, without silently editing HEPfit
     or SuperIso;
 (4) numerical E3 2026 Eq.(4) C7,C8 source-pinned LO consistency for
     each of the 27 actual spectra;
 (5) pure-state, intermediate mixing, degenerate-mass and shared
     SM matching checks; all NP vectors superpose before one LEFT rate.

E4A CANNOT produce a publication-level 2026 NNLO inclusive BR: the
2026 full nonperturbative + QCD matrix-element/phase-space kernel,
its covariance and a reproducible complete pure-Type-II 670 GeV
limit have not been supplied. "SM 3.54" and generic Eq.(4) are not that
kernel. Consequently even if ALL matching probes work, E4A must
explicitly report precision_exclusion_readiness=BLOCKED_MISSING_FULL_2026
and NEVER claim an allowed/excluded Zee model or 95% limit.

The large source-integration experiment is a valid progress step:
it establishes whether 2026 LO and old NNLO matching are internally
reproducible for every *actual* selected scalar point, and isolates
basis/order issues for an eventual modern observable replacement.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import subprocess
import sys
import traceback
from pathlib import Path

from gateA1r_run_br_pilot import compile_pilot,check_superiso_source
from gateA1q_audit_numeric_author_residuals import close_numeric_comparison
from gateA1s_run_modern_2026_screen import (
    MODERN_SM,K7,K8,MU0_GEV,linearized_2026
)
from zee_gateC1_joined_uv_pilot import digest
from zee_gateE3_2026_eq4_27_wilson_frontier import (
    STATUS as E3_STATUS,verify_inputs
)

STATUS="GATE_E4A_ALL_ORDERS_COHERENT_MATCHING_COMPLETED_2026_PRECISION_OBSERVABLE_BLOCKED"
FAIL="GATE_E4A_SOURCE_OR_MATCHING_CONSISTENCY_FAILED_NO_EXCLUSION"
TYPEII_MASSES=(300.,450.,550.,600.,650.,670.,700.,800.,1000.)
TANBETA_VALUES=(5.6,50.)
GAMMAS=(0.,.31,.79,1.33,math.pi/2)
OBSERVABLE_STATUS="BLOCKED_MISSING_2026_FULL_NNLO_MATRIX_ELEMENTS_AND_LIKELIHOOD"
HEADER="STATUS E4A_FULL_ORDER_MATCHING_NOT_2026_BR_OR_EXCLUSION"
COEFF=re.compile(
    r"^MATCH order=(\d+) op=(\d+) sm=(\S+) "
    r"delta_light=(\S+) delta_heavy=(\S+) zee=(\S+)$")
INPUT=re.compile(r"^INPUT mH1=(\S+) mH2=(\S+) tanbeta=(\S+) "
                 r"gamma=(\S+) mu0=(\S+) w1=(\S+) w2=(\S+)$")
EXP="PHYSICAL_BR_2026_NOT_IMPLEMENTED true"
TOL=4e-12

def parse_probe(stdout,m1,m2,tanb,gamma):
    lines=stdout.strip().splitlines()
    if lines.count(HEADER)!=1 or lines.count(EXP)!=1 or lines.count(
            "NNLO_MATRIX_ELEMENTS_AND_THEORY_COVARIANCE_MISSING true")!=1:
        raise ValueError("E4A source probe identity/completeness missing")
    inp=[m for line in lines if (m:=INPUT.fullmatch(line))]
    if len(inp)!=1:
        raise ValueError("E4A missing/duplicate matching input")
    vals=list(map(float,inp[0].groups()))
    for given,expected in zip(vals[:4],(m1,m2,tanb,gamma)):
        if not math.isclose(given,expected,rel_tol=1e-12,abs_tol=1e-11):
            raise ValueError("E4A probed wrong mass/tanbeta/gamma")
    if vals[4]!=MU0_GEV or not math.isclose(vals[5]+vals[6],1.,abs_tol=1e-12):
        raise ValueError("E4A mu0 or mixing weight mismatch")
    rows={}
    for line in lines:
        match=COEFF.fullmatch(line)
        if not match:continue
        order,op=map(int,match.groups()[:2])
        numbers=list(map(float,match.groups()[2:]))
        if (order,op) in rows or not all(map(math.isfinite,numbers)):
            raise ValueError("E4A duplicate/nonfinite matching entry")
        rows[order,op]=numbers
    if set(rows)!={(o,i) for o in range(3) for i in range(1,9)}:
        raise ValueError("E4A expected exact 24 source coefficient entries")
    max_mix=0.
    for (order,op),(sm,d1,d2,z) in rows.items():
        expected=sm+vals[5]*d1+vals[6]*d2
        residual=abs(z-expected)
        max_mix=max(max_mix,residual)
        if residual>TOL:
            raise ValueError(f"E4A bad full order matching linearity {order} C{op}")
    return {
        "input":{"mH1":vals[0],"mH2":vals[1],"tanbeta":vals[2],
                 "gamma":vals[3],"mu0":vals[4],"w1":vals[5],"w2":vals[6]},
        "coefficient_rows":rows,
        "max_coherent_Wilson_residual":max_mix
    }

def run_matching(binary,m1,m2,tanb,gamma):
    cmd=[str(Path(binary).resolve()),
         f"{m1:.17g}",f"{m2:.17g}",f"{tanb:.17g}",f"{gamma:.17g}"]
    out=subprocess.run(cmd,capture_output=True,text=True,timeout=90,check=False)
    if out.returncode:
        raise ValueError("E4A pinned source compiled probe returned "
                         +str(out.returncode)+": "+out.stderr[-1000:])
    return parse_probe(out.stdout,m1,m2,tanb,gamma)

def check_e3_source(e3file,e1,e2,a1m,a1u):
    data=json.loads(Path(e3file).read_text())
    if (data.get("status")!=E3_STATUS or data.get("tested")!=27 or
        len(data.get("rows",[]))!=27):
        raise ValueError("E4A completed E3 27-spectrum source unavailable")
    requirements={
        "E1":e1,"E2":e2,"A1M":a1m,"A1U":a1u}
    for key,p in requirements.items():
        if data.get("provenance",{}).get(key)!=digest(p):
            raise ValueError("E4A E3 source ancestry hash mismatch "+key)
    old,new,_,_=verify_inputs(e1,e2,a1m,a1u)
    e3rows={x["candidate_id"]:x for x in data["rows"]}
    if len(e3rows)!=27 or set(e3rows)!=set(old):
        raise ValueError("E4A E1/E2/E3 rows missing or duplicated")
    for key in old:
        e3=e3rows[key]
        if not math.isclose(float(old[key]["gamma"]),
                            float(e3["original_gamma"]),
                            rel_tol=1e-12,abs_tol=1e-12):
            raise ValueError("E4A E3 gamma provenance inconsistency")
    return old,e3rows

def eq4_closure(probe,row,original_gamma):
    rows=probe["coefficient_rows"]
    w1,w2=math.cos(original_gamma)**2,math.sin(original_gamma)**2
    for op in (7,8):
        left=rows[0,op][1]
        right=rows[0,op][2]
        weighted=w1*left+w2*right
        key=f"LO_delta_C{op}_Zee_mu0_160"
        if not math.isclose(weighted,float(row[key]),
                            rel_tol=2e-10,abs_tol=5e-11):
            raise ValueError(f"E4A independent 2026 Eq4 LO C{op} mismatch")
    value=linearized_2026(
        w1*rows[0,7][1]+w2*rows[0,7][2],
        w1*rows[0,8][1]+w2*rows[0,8][2])[
        "linearized_predicted_central_times_1e4"]
    if not math.isclose(value,float(
        row["2026_Eq4_original_LO_linearized_BR_times_1e4"]),
        rel_tol=2e-10,abs_tol=1e-9):
        raise ValueError("E4A 2026 Eq4 original prediction mismatch")
    return value

def gamma_trajectory_checks(probes):
    """Five gamma probes share matching coefficients and reproduce limits."""
    reference=probes[0]
    max_residual=0.
    for row in probes:
        for i in range(3):
            for op in range(1,9):
                coeff=reference["coefficient_rows"][i,op]
                obs=row["coefficient_rows"][i,op]
                for index in (0,1,2):
                    d=abs(coeff[index]-obs[index])
                    max_residual=max(d,max_residual)
                    if d>TOL:
                        raise ValueError("E4A unphysical gamma-dependence of fixed-mass matching")
        if row["input"]["w1"]<1e-15:
            for i in range(3):
                for op in range(1,9):
                    sm,d1,d2,z=row["coefficient_rows"][i,op]
                    if abs(z-(sm+d2))>TOL:
                        raise ValueError("E4A pure heavy endpoint failed")
        if row["input"]["w2"]<1e-15:
            for i in range(3):
                for op in range(1,9):
                    sm,d1,d2,z=row["coefficient_rows"][i,op]
                    if abs(z-(sm+d1))>TOL:
                        raise ValueError("E4A pure light endpoint failed")
    return max_residual

def validate_author_source(comparison):
    data=json.loads(Path(comparison).read_text())
    result=close_numeric_comparison(data)
    if (not result["HEPfit_matches_authors_C3_C6_exact_numerical"] or
        not result["all_eight_effective_residuals_decomposed"] or
        result["full_NNLO_matching_validated"] is not False or
        result["BtoXs_gamma_BR_validated"] is not False):
        raise ValueError("E4A A1Q original author source audit not in known state")
    return {
        "source":result["original_author_sha256"],
        "n_author_reference_rows":len(data["comparison_rows"]),
        "HEPfit_four_quark_exact":True,
        "SuperIso_four_quark_discrepant":result[
            "SuperIso_C3_C6_has_author_discrepancy"],
        "raw_dipole_closure_reproduced":True,
        "full_NNLO_matching_validated":False,
        "physical_BR_validated":False,
        "known_C3_C6_basis_and_matching_discrepancy_UNRESOLVED":True,
    }

def typeII_controls(binary):
    results=[]
    for tanb in TANBETA_VALUES:
        for mass in TYPEII_MASSES:
            # The second mass is set EQUAL so exact mixing independence
            # holds at ALL three QCD orders, including 670 GeV reference.
            combos=[run_matching(binary,mass,mass,tanb,g)
                    for g in (0.,.37,math.pi/2)]
            inv=gamma_trajectory_checks(combos)
            largest=0.
            for ord in range(3):
                for op in range(1,9):
                    first=combos[0]["coefficient_rows"][ord,op][3]
                    for x in combos[1:]:
                        largest=max(largest,abs(first-
                            x["coefficient_rows"][ord,op][3]))
            if largest>TOL:
                raise ValueError("E4A degenerate masses fail gamma-invariance")
            c=combos[0]["coefficient_rows"]
            exp=linearized_2026(c[0,7][1],c[0,8][1])
            if mass>=670. and tanb==50. and not math.isfinite(
                exp["linearized_predicted_central_times_1e4"]):
                raise ValueError("E4A nonfinite published 670 GeV anchor")
            results.append({
                "mH_GeV":mass,"tanbeta":tanb,
                "LO_C7":c[0,7][1],"LO_C8":c[0,8][1],
                "NLO_C7_vendor":c[1,7][1],"NLO_C8_vendor":c[1,8][1],
                "NNLO_C3_vendor":c[2,3][1],
                "NNLO_C4_vendor":c[2,4][1],
                "NNLO_C5_vendor":c[2,5][1],
                "NNLO_C6_vendor":c[2,6][1],
                "NNLO_C7_vendor_not_effective_unless_basis_audited":c[2,7][1],
                "NNLO_C8_vendor_not_effective_unless_basis_audited":c[2,8][1],
                "Eq4_LO_BR_times1e4_NOT_2026_TypeII_NNLO":
                    exp["linearized_predicted_central_times_1e4"],
                "mass_670_2026_95CL_exclusion_reproduced":False,
                "three_gamma_endpoints_checked":True,
                "matched_operators_at_three_orders":24,
                "max_degenerate_residual":largest,
                "max_gamma_independence_residual":inv,
            })
    return results

def run_cohort(binary,e1rows,e3rows):
    summary=[];wide=[]
    for ix,name in enumerate(sorted(e1rows),1):
        row=e1rows[name]
        params=(float(row["mH1"]),float(row["mH2"]),float(row["tanbeta"]))
        gamma=float(row["gamma"])
        gammas=list(GAMMAS)+[gamma]
        tests=[run_matching(binary,*params,g) for g in gammas]
        max_fixed=gamma_trajectory_checks(tests)
        matching=tests[-1]
        linear=eq4_closure(matching,e3rows[name],gamma)
        partial={
            "candidate_id":name,
            "mH1_GeV":params[0],"mH2_GeV":params[1],
            "tanbeta":params[2],"gamma":gamma,
            "2026_Eq4_original_LO_BR_times1e4_reproduced":linear,
            "maximum_fixed_mass_gamma_matching_residual":max_fixed,
            "maximum_source_internal_superposition_residual":max(
                t["max_coherent_Wilson_residual"] for t in tests),
            "source_probe_count":len(tests),
            "matching_rows_verified":24*len(tests),
            "modern_2026_95CL_exclusion":"NOT_IMPLEMENTED",
        }
        summary.append(partial)
        for order in range(3):
            for op in range(1,9):
                sm,d1,d2,total=matching["coefficient_rows"][order,op]
                wide.append({
                    "candidate_id":name,"order":order,"operator":f"C{op}",
                    "source_SM":sm,"light_NP":d1,"heavy_NP":d2,
                    "coherent_Zee_total":total,
                })
        print("E4A_FULLORDER_MODEL",f"{ix}/27",name,
              "C7_LO",matching["coefficient_rows"][0,7][3],
              "C8_LO",matching["coefficient_rows"][0,8][3],
              "C3_NNLO",matching["coefficient_rows"][2,3][3],
              "C4_NNLO",matching["coefficient_rows"][2,4][3],
              "Eq4_LO_times_1e4",linear,
              "full_2026_95CL_BLOCKED",flush=True)
    return summary,wide

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ("e1-summary","e2-summary","e3-summary",
                  "a1m-provenance","a1u-result","a1q-original-comparison",
                  "vendor-root"):
        p.add_argument("--"+field,type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        p.error("Do not overwrite previous source-pinned E4A run")
    args.output_dir.mkdir(parents=True,exist_ok=True)
    result={
        "status":FAIL,"physics_Zee_allowed":None,
        "2026_TypeII_670GeV_95CL_reproduced":False,
        "full_2026_inclusive_NNLO_Zee_BR_implemented":False,
        "matching_source_pinned":False,
        "precision_exclusion_readiness":OBSERVABLE_STATUS,
    }
    try:
        e1,e3=check_e3_source(
            args.e3_summary,args.e1_summary,args.e2_summary,
            args.a1m_provenance,args.a1u_result)
        original=validate_author_source(args.a1q_original_comparison)
        vendor=check_superiso_source(args.vendor_root,args.a1m_provenance)
        probe=Path(__file__).with_name(
            "zee_gateE4a_full_order_matching_probe.c")
        exe=args.output_dir/"gateE4A_source_pinned_multiorder_matching"
        build=compile_pilot(args.vendor_root,exe,probe,False)
        cohort,coefficient_rows=run_cohort(exe,e1,e3)
        typeII=typeII_controls(exe)
        if (len(cohort)!=27 or len(coefficient_rows)!=648 or len(typeII)!=18):
            raise ValueError("E4A full-integrated case count incomplete")
        with (args.output_dir/"E4A_27_Zee_full_order_coefficients.csv").open(
                "w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(coefficient_rows[0]))
            writer.writeheader();writer.writerows(coefficient_rows)
        with (args.output_dir/"E4A_18_pure_TypeII_benchmarks.csv").open(
                "w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(typeII[0]))
            writer.writeheader();writer.writerows(typeII)
        with (args.output_dir/"E4A_27_models_summary.csv").open(
                "w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(cohort[0]))
            writer.writeheader();writer.writerows(cohort)
        # Physics acceptance is deliberately BLOCKED, not a numeric fit.
        count_zee=27*6
        count_typeii=18*3
        summary={
            "unique_27_Zee_spectra":len(cohort),
            "Zee_gamma_source_evaluations":count_zee,
            "typeII_masses":list(TYPEII_MASSES),
            "typeII_tanbeta":list(TANBETA_VALUES),
            "pure_TypeII_mass_tanbeta_benchmarks":len(typeII),
            "pure_TypeII_gamma_source_evaluations":count_typeii,
            "all_source_matched_vendor_calls":count_zee+count_typeii,
            "all_8_operator_3_order_coefficients_inspected":24*(
                count_zee+count_typeii),
            "Zee_original_gamma_coefficients_exported":len(coefficient_rows),
            "A1Q_original_author_independent_NNLO_rows":original[
                "n_author_reference_rows"],
            "max_Zee_source_mixing_roundoff":max(
                x["maximum_source_internal_superposition_residual"]
                for x in cohort),
            "max_Zee_gamma_independence_roundoff":max(
                x["maximum_fixed_mass_gamma_matching_residual"]
                for x in cohort),
            "max_TypeII_equal_mass_gamma_residual":max(
                x["max_degenerate_residual"] for x in typeII),
            "670GeV_pure_TypeII_included":True,
            "full_2026_TypeII_95CL_reproduced":False,
            "modern_2026_precision_Zee_exclusions":None,
            "SOURCE_MATCHING_NUMERICALLY_CHECKED_NOT_FULL_NNLO_BR":True,
            "original_author_NNLO_basis_discrepancy_NOT_RESOLVED":True,
        }
        result.update(
            status=STATUS,model_matching_rows=coefficient_rows,
            Zee_27_results=cohort,pure_TypeII_18_results=typeII,
            A1Q_original_author_NNLO_audit=original,summary=summary,
            vendor_source_metadata=vendor,build_source_metadata=build,
            fingerprints_sha256={
                k:digest(v) for k,v in (
                    ("E1",args.e1_summary),("E2",args.e2_summary),
                    ("E3",args.e3_summary),("A1M",args.a1m_provenance),
                    ("A1U",args.a1u_result),("A1Q",args.a1q_original_comparison),
                    ("E4A_driver",probe))}
        )
        print("E4A_LARGE_INTEGRATED_MATCHING",json.dumps(summary),flush=True)
        print("E4A_P0_FULL_2026_OBSERVABLE",OBSERVABLE_STATUS,flush=True)
        print("E4A_PHYSICAL_ZEE_ALLOWED UNKNOWN",flush=True)
        return 0
    except Exception as exc:
        result.update(error=repr(exc),traceback=traceback.format_exc())
        print("E4A_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        location=args.output_dir/"summary.json"
        location.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("E4A_SUMMARY",location,flush=True)

if __name__=="__main__":
    raise SystemExit(main())
