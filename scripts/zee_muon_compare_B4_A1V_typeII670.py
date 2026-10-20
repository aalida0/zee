#!/usr/bin/env python3
"""Paper2: same-implementation 670-GeV Type-II comparison for B4 spectra.

Input: Gate B4 scalar/EWPO-screened candidate CSV; completed A1V
scan_flavour_only.csv from precisely the same rows; its audited compiled
A1V helper executable. For each original tanbeta, evaluate the *same
A1V code* at mH1=670,mH2=700,gamma=0. (The second scalar is singlet,
so this is one Type-II-coupled 670-GeV charged state.)

Strictly validate row identity, SM baseline closure and linear-plus-
quadratic Wilson response; fail closed on zero/negative reference NP shift.
Compute the independently MG5-validated LO Z-only muon pair rate.

The ratio of legacy BR shifts is a screening/ordering metric ONLY,
NOT a formal application of Misiak 2026 95%-CL Type-II mass bound
to a two-charged-state Zee model. No actual LFV, HiggsTools,
muon BIB, acceptance, or physical full BRs are evaluated.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import median
from gateA1v_run_legacy_response import evaluate as a1v_evaluate
from zee_muon_mass_mixing_grid import ALPHA_YW,SW2_YW
from zee_muon_asymmetric_pair_pilot import sigma_both_charges_fb,BR_Z_EE_MUMU

STATUS="PAPER2_B4_SAME_A1V_TYPEII670_COMPARISON_NOT_MODEL_EXCLUSION"
NEEDED=("mH1","mH2","gamma","tanbeta")
WIDTHS=("BR_H2_H1Z_nonleptonic_included_upper_proxy",
        "BR_H1_tb_nonleptonic_included_upper_proxy")
FIELDS=(
    "id","mH1","mH2","gamma","tanbeta",
    "SM_BR_legacy","Zee_BR_legacy","Zee_delta_BR_legacy",
    "TypeII670_BR_legacy","TypeII670_delta_BR_legacy",
    "R_legacy_Zee_over_TypeII670",
    "sigma_Z_both_charges_1500_fb","sigma_Z_both_charges_3000_fb",
    "produced_pairs_1500_0p5ab",
    "Zll_tb_tb_included_channel_truth_ceiling_1500_0p5ab",
    "ratio_below_1_not_physical_acceptance","status",
)


def read_data(path,required):
    with Path(path).open(newline="") as handle:
        r=csv.DictReader(handle)
        if not r.fieldnames or any(k not in r.fieldnames for k in required):
            raise ValueError("CSV missing required fields: "+str(path))
        rows=list(r)
    if not rows:raise ValueError("Empty CSV "+str(path))
    return rows


def num(row,key):
    x=float(row[key])
    if not math.isfinite(x):raise ValueError("Nonfinite "+key)
    return x


def identity(p,f):
    for k in NEEDED:
        x,y=num(p,k),num(f,k)
        if not math.isclose(x,y,rel_tol=3e-12,abs_tol=1e-9):
            raise ValueError("A1V/B4 row identity mismatch: "+k)
    if not p.get("id") or p.get("candidate_status")!=(
            "SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"):
        raise ValueError("Invalid B4 screened provenance")
    return True


def combine(p,f,reference):
    """One B4 point and its A1V same-scheme single-670 reference."""
    identity(p,f)
    sm=num(f,"SM_BR")
    zee=num(f,"full_Zee_BR")
    delta=zee-sm
    linear=num(f,"linear_delta_BR")
    quadratic=num(f,"quadratic_delta_BR")
    if abs(delta-linear-quadratic)>1e-11:
        raise ValueError("A1V decomposition not closed")
    if not math.isclose(sm,float(reference["SM_BR"]),
                        rel_tol=0,abs_tol=1e-11):
        raise ValueError("A1V SM baseline mismatch")
    ref_delta=float(reference["full_Zee_BR"])-float(reference["SM_BR"])
    if not(math.isfinite(ref_delta) and ref_delta>0):
        raise ValueError("Invalid 670-GeV Type-II legacy NP shift")
    ratio=delta/ref_delta
    m1,m2,g,t=(num(p,k) for k in NEEDED)
    b2=num(p,WIDTHS[0])
    b1=num(p,WIDTHS[1])
    if not(200<=m1<m2 and 0<=g<=math.pi/2
            and .25<=t<=100 and 0<=b2<=1 and 0<=b1<=1):
        raise ValueError("Invalid B4 scalar/width inputs")
    s15=sigma_both_charges_fb(1500.,m1,m2,g,
                              alpha=ALPHA_YW,sw2=SW2_YW)
    s30=sigma_both_charges_fb(3000.,m1,m2,g,
                              alpha=ALPHA_YW,sw2=SW2_YW)
    pairs=s15*500.
    return {
        "id":p["id"],"mH1":m1,"mH2":m2,"gamma":g,"tanbeta":t,
        "SM_BR_legacy":sm,"Zee_BR_legacy":zee,
        "Zee_delta_BR_legacy":delta,
        "TypeII670_BR_legacy":reference["full_Zee_BR"],
        "TypeII670_delta_BR_legacy":ref_delta,
        "R_legacy_Zee_over_TypeII670":ratio,
        "sigma_Z_both_charges_1500_fb":s15,
        "sigma_Z_both_charges_3000_fb":s30,
        "produced_pairs_1500_0p5ab":pairs,
        "Zll_tb_tb_included_channel_truth_ceiling_1500_0p5ab":
            pairs*b2*b1*b1*BR_Z_EE_MUMU,
        "ratio_below_1_not_physical_acceptance":ratio<1.,
        "status":"LEGACY_FLAVOR_ORDERING_AND_INCLUDED_WIDTH_ONLY_NOT_ALLOWED",
    }


def compare(points,flavor,reference_function,progress_every=25):
    if len(points)!=len(flavor):
        raise ValueError("A1V and B4 number of rows differ")
    ids=[row.get("id") for row in points]
    if len(ids)!=len(set(ids)):
        raise ValueError("Missing or duplicated B4 candidate IDs")
    rows=[]
    for j,(p,f) in enumerate(zip(points,flavor),1):
        identity(p,f)
        t=num(p,"tanbeta")
        ref=reference_function(t)
        rows.append(combine(p,f,ref))
        if progress_every>0 and j%progress_every==0:
            print("CHECKED",j,"OF",len(points),flush=True)
    return rows


def summarize(rows):
    ratios=[r["R_legacy_Zee_over_TypeII670"] for r in rows]
    below=sorted((r for r in rows if r[
        "ratio_below_1_not_physical_acceptance"]),
        key=lambda r:r["sigma_Z_both_charges_1500_fb"],
        reverse=True)
    above=sorted((r for r in rows if not r[
        "ratio_below_1_not_physical_acceptance"]),
        key=lambda r:r["R_legacy_Zee_over_TypeII670"])
    return {
        "status":STATUS,"n_spectra":len(rows),
        "all_same_scheme_SM_reference_checked":True,
        "n_ratio_below_1_NOT_allowed_count":len(below),
        "n_ratio_at_or_above_1_NOT_excluded_count":len(rows)-len(below),
        "ratio_min":min(ratios),
        "ratio_median":median(ratios),
        "ratio_max":max(ratios),
        "best_sigma_among_below_1_NOT_allowed":below[:10],
        "smallest_ratio_among_at_or_above_1_NOT_excluded":above[:5],
        "single_TypeII_670_bound_not_direct_Zee_exclusion":True,
        "full_neutrino_LFV_HiggsTools_modern_NNLO_completed":False,
        "complete_charged_widths_BRs_computed":False,
        "muon_detector_backgrounds_computed":False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--b4-csv",type=Path,required=True)
    ap.add_argument("--a1v-csv",type=Path,required=True)
    ap.add_argument("--a1v-executable",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    points=read_data(args.b4_csv,("id","candidate_status",*NEEDED,*WIDTHS))
    flavor=read_data(args.a1v_csv,(*NEEDED,"SM_BR","full_Zee_BR",
                                   "linear_delta_BR","quadratic_delta_BR"))
    executable=args.a1v_executable.resolve()
    if not executable.is_file():
        raise FileNotFoundError("Missing audited A1V executable "+str(executable))
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise ValueError("Choose a new empty output dir")
    print("STATUS",STATUS,flush=True)
    print("B4_ROWS",len(points),"RUN_EXISTING_A1V_SINGLE_TYPEII_670",flush=True)
    def ref(t):
        result,_=a1v_evaluate(executable,670.,700.,0.,t)
        return result
    results=compare(points,flavor,ref)
    info=summarize(results)
    out=args.output_dir
    out.mkdir(parents=True,exist_ok=True)
    path=out/"B4_same_A1V_typeII670_ratios_NOT_EXCLUSIONS.csv"
    with path.open("w",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=FIELDS)
        writer.writeheader();writer.writerows(results)
    info["results_csv"]=str(path)
    (out/"summary.json").write_text(json.dumps(info,indent=2)+"\n")
    print("SM_BASELINE_MATCH True")
    print("RATIO_SUMMARY_MIN_MEDIAN_MAX",
          format(info["ratio_min"],".8g"),
          format(info["ratio_median"],".8g"),
          format(info["ratio_max"],".8g"))
    print("NUM_R_LESS_1",info["n_ratio_below_1_NOT_allowed_count"],
          "OF",len(results))
    for r in info["best_sigma_among_below_1_NOT_allowed"][:8]:
        print("CANDIDATE_R_BELOW_1_NOT_ALLOWED",r["id"],
              "m1",round(r["mH1"],2),"m2",round(r["mH2"],2),
              "gamma",round(r["gamma"],4),
              "R",round(r["R_legacy_Zee_over_TypeII670"],4),
              "sigma1500_fb",round(r["sigma_Z_both_charges_1500_fb"],5),
              "conditional_Zll",round(
                  r["Zll_tb_tb_included_channel_truth_ceiling_1500_0p5ab"],2))
    if not info["best_sigma_among_below_1_NOT_allowed"]:
        for r in info["smallest_ratio_among_at_or_above_1_NOT_excluded"]:
            print("CLOSEST_ABOVE_R1_NOT_EXCLUDED",r["id"],
                  "R",round(r["R_legacy_Zee_over_TypeII670"],5),
                  "sigma1500_fb",round(r["sigma_Z_both_charges_1500_fb"],5))
    print("PHYSICAL_95CL_EXCLUSION_COMPUTED False")
    print("OUTPUT",path)


if __name__=="__main__":
    main()
