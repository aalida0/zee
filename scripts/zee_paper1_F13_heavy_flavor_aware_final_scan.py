#!/usr/bin/env python3
"""F13: final bounded HEAVY charged Zee scalar + 2026 LO B->Xs gamma
flavor-aware exploration followed by exact neutrino and partial LFV fits.

Target mH1 = 550--720GeV and mH2>mH1+MZ, up to 1600GeV;
start from Florentino's P1 Table-2 inspired *rebuilt* scalar seeds.
Every accepted model independently passes B4 scalar BFB/unitarity/EWPO
sufficient screens. The Misiak 2026 Eq4 LO dC7,dC8 flavor response is
evaluated from SOURCE-PINNED SuperIso A1S on each proposed point and
actually enters the Metropolis objective, never after the fact.

The published 2026 Eq4 B->Xs gamma prediction is LINEAR in LO NP.
The diagnostic abs(z)<1.96 is an UNCALIBRATED screen, not a 95% CL.
No full Zee point is labelled allowed; no true hadron cross sections.
The source-pinned E4A three-order matching independently closes A1S LO
on selected priority points. Then optimize exact 3x3 Zee neutrino
mass target with existing D2 coherent PARTIAL-LFV and lepton widths.
This is a FINITE, falsifiable exploratory gate, NOT global exclusion.
"""
from __future__ import annotations
import argparse,csv,json,math,sys,traceback,statistics
from pathlib import Path
import numpy as np

from gateB4_adaptive_zee_scalar_scan import (
   encode,decode,propose,coarse_bin,make_record,scalar_screen,
   ewpo_screen,write_csv,OUTPUT_COLS
)
from gateA1r_run_br_pilot import compile_pilot
from gateA1s_run_modern_2026_screen import (
    combine,linearized_2026,MODERN_SM,PDG_EXP,
)
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import (
    ROOT,digest,writejson,
)
from zee_paper1_F10_six_new_two_charged_legacy_bsgamma import discover_f6
from zee_paper1_F11_six_real_flavio_LO_NP_rate import (
    matching,coeff,close,cross_check_a1s_vs_e4a,
)
from zee_paper1_F12_309_modern_Eq4_Bsgamma_frontier import (
    original_source,build_vendor,source_probe,
)
from zee_paper1_F13_heavy_P1_seeds import (
    validated_p1_seeds,HEAVY_MIN,HEAVY_MAX,H2_MAX,MZ
)
from zee_paper1_florentino_feasibility_scan import (
    optimize_point,scalar_row,complex_payload,MISSING as P1_MISSING,
)
from gateA1b_hierarchical_no_seed import target_neutrino_matrix

STATUS="F13_HEAVY_P1_2026_EQ4_FLAVOR_GUIDED_NEUTRINO_LFV_FEASIBILITY_NOT_ALLOWED"
BLOCKED="F13_BLOCKED_NO_COMPLETE_PHYSICAL_ZEE_OR_FULL_BSGAMMA_LIKELIHOOD"
RNAME="F13_all_heavy_scalar_2026LO_flavor_screen_NOT_ALLOWED.csv"
SELECT="F13_selected_priority_scalar_2026LO_NOT_ALLOWED.csv"
REPORT="F13_ranked_heavy_neutrino_LFV_2026Eq4_NOT_ALLOWED.csv"
STOP_Z=1.96
DEFAULT=ROOT/"work"/"zee_paper1_F13_heavy_flavor_final_pilot"
MISSING=tuple(P1_MISSING)+(
    "2026 Eq4 ignores NP^2, higher-order matching and BSM covariance",
    "search has finite mass/gamma seed and objective coverage only",
    "genuinely quoted signal pb at 13.6/14 TeV remains missing",
)
def floatval(v):
    f=float(v)
    if not math.isfinite(f):raise ValueError("nonfinite physics input")
    return f

def screen_flavor(p,backend,cache):
    """A1S on reconstructed scalar *physical point*, not gamma-only edit."""
    gamma=floatval(p["gamma"])
    t=math.tan(floatval(p["beta"]))
    def point(m):
        key=(floatval(m),t)
        if key not in cache:cache[key]=backend(key[0],key[1])
        return cache[key]
    a,b=point(p["mH1"]),point(p["mH2"])
    ref=point(670.)
    reflo=linearized_2026(ref["delta_C7_LO"],ref["delta_C8_LO"])
    out=combine(a,b,gamma)
    shift=out["linearized_shift_times_1e4"]
    br=out["linearized_predicted_central_times_1e4"]
    sigma=math.hypot(MODERN_SM["sigma_times_1e4"],
                     PDG_EXP["sigma_times_1e4"])
    z=(br-PDG_EXP["central_times_1e4"])/sigma
    ref_shift=reflo["linearized_shift_times_1e4"]
    if not(ref_shift>0 and shift>0):
        raise ValueError("Unexpected nonconstructive TypeII/Zee LO C7C8 dipole")
    return {
      "delta_C7_LO":out["LO_delta_C7_mu0_160"],
      "delta_C8_LO":out["LO_delta_C8_mu0_160"],
      "2026_Eq4_LO_linearized_BRx1e4":br,
      "2026_Eq4_LO_linearized_NP_shift_x1e4":shift,
      "2026_Eq4_same_tanbeta_TypeII670_NP_shift_x1e4":ref_shift,
      "Zee_to_same_tanbeta_TypeII670_2026Eq4_LO_NP_ratio_NOT_CL":
          shift/ref_shift,
      "abs_z_illustrative_NOT_CL":abs(z),
      "signed_z_illustrative_NOT_CL":z,
      "diagnostic_below_1p96_NOT_allowed":abs(z)<STOP_Z,
      "SM_2026_reference_1e4":MODERN_SM["central_times_1e4"],
      "experiment_2026_reference_1e4":PDG_EXP["central_times_1e4"],
      "no_BSM_covariance_and_quadratic_NP_terms":True,
      "modern_2026_full_NNLO_excluded_or_allowed":None,
    }

def fitness(rec):
    """Only a proposal-selection heuristic, never χ²/likelihood/posterior."""
    p=rec["production_weighted_nonleptonic_cascade_upper_proxy"]
    z=rec["abs_z_illustrative_NOT_CL"]
    return float(p)-.55*max(0.,z-STOP_Z)-.10*max(0.,z-2.4)

def domain(p):
    return (p is not None and
      HEAVY_MIN<=p["mH1"]<=HEAVY_MAX and
      p["mH2"]>p["mH1"]+MZ+1. and p["mH2"]<=H2_MAX)

def augment(row,p,backend,cache):
    fl=screen_flavor(p,backend,cache)
    result={**row,**fl}
    result["proposal_objective_NOT_physics_likelihood"]=fitness(result)
    result["fully_allowed_Zee_model"]=None
    return result

def walk(seeds,steps,quad,rng,backend,
         *,temperature=.09,report_every=200,debug=False):
    if steps<0 or quad<40 or temperature<=0:
        raise ValueError("F13 invalid MCMC settings")
    # Restrict proposal states to independent physical scalar screens.
    states=[]
    records=[]
    seen=set()
    cache={}
    for p,rec in seeds:
        if not domain(p):raise ValueError("F13 seed outside heavy domain")
        row=augment(rec,p,backend,cache)
        x=encode(p)
        states.append((x,row))
        cell=coarse_bin(p)
        if cell not in seen:
            records.append(row);seen.add(cell)
    if not states:raise ValueError("No actual scalar-screened heavy seeds")
    counters={"new_proposals":steps,"invalid":0,"theory":0,
              "EWPO":0,"partial_widths":0,"flavor_backend":0,
              "new_screened":len(records),"accepted_Metropolis":0,
              "compared_new_scored":0}
    found=sum(r["diagnostic_below_1p96_NOT_allowed"] and
              r["production_weighted_nonleptonic_cascade_upper_proxy"]>=.10
              for r in records)
    for it in range(1,steps+1):
        j=int(rng.integers(0,len(states)))
        x,old=states[j]
        # Physics-motivated mass+gauge proposals along with B4 local jumps;
        # B4 codec always reconstructs a new scalar potential and quartics.
        proposal=propose(x,rng,.9 if it%4 else 2.6)
        if it%17==0:
            proposal[0]+=rng.normal(0.,17.) # mH1
            proposal[1]+=rng.normal(0.,22.) # mH2
            proposal[6]+=rng.normal(0.,.035) # gamma
        p=decode(proposal)
        if not domain(p):
            counters["invalid"]+=1;continue
        try:
            theory=scalar_screen(p)
            if theory is None:
                counters["theory"]+=1;continue
            ew=ewpo_screen(p,quad)
            if ew is None:
                counters["EWPO"]+=1;continue
            row=make_record(p,theory,ew,it,
                            f"F13_heavy_{it:07d}",
                            old["seed_id"])
        except (ValueError,ArithmeticError,FloatingPointError,
                np.linalg.LinAlgError):
            counters["partial_widths"]+=1;continue
        try:
            newer=augment(row,p,backend,cache)
        except (ValueError,ArithmeticError,FloatingPointError,
                np.linalg.LinAlgError):
            counters["flavor_backend"]+=1
            raise # invalid A1S source must fail CLOSED, not bias model.
        counters["compared_new_scored"]+=1
        newer["candidate_status"]="SCALAR_EWPO_PLUS_2026_EQ4_SCREEN_ONLY_NOT_ALLOWED"
        cell=coarse_bin(p)
        if cell not in seen:
            seen.add(cell)
            records.append(newer)
            counters["new_screened"]+=1
            if (newer["diagnostic_below_1p96_NOT_allowed"] and
                newer["production_weighted_nonleptonic_cascade_upper_proxy"]>=.10):
                found+=1
        current_temp=temperature*(.45+.55*(1-it/max(1,steps)))
        ds=fitness(newer)-fitness(old)
        if ds>=0. or rng.random()<math.exp(max(-700.,ds/current_temp)):
            states[j]=(proposal,newer)
            counters["accepted_Metropolis"]+=1
        if report_every and it%report_every==0:
            print("F13_ITER",it,"/",steps,
                  "HEAVY_THEORY_EWPO",len(records),
                  "EQ4_LT_1p96_AND_PROXY_GTE_0p1",found,
                  "MIN_Z",format(min(v["abs_z_illustrative_NOT_CL"]
                                 for v in records),".5g"),
                  "BEST_PROXY",format(max(v[
                  "production_weighted_nonleptonic_cascade_upper_proxy"]
                  for v in records),".5g"),
                  flush=True)
    return records,{**counters,
        "flavor_benchmark_backend_calls":len(cache),
        "diagnostic_lt1p96_proxy_gte0p1":found,
        "Metropolis_distribution_NOT_unbiased_or_posterior":True}

def pick(rows,count):
    """Diversify along Pareto flavors and geometry: avoid all on one ridge."""
    if count<1:raise ValueError("Need >0 priority rows")
    eligible=[r for r in rows if
        r["diagnostic_below_1p96_NOT_allowed"] and
        r["production_weighted_nonleptonic_cascade_upper_proxy"]>=.10]
    pool=eligible if eligible else rows
    # If no screen-positive rows exist, pick least-bad finite subset,
    # explicitly mark this condition in summary rather than claiming GO.
    ranked=sorted(pool,key=lambda r:
        (-r["production_weighted_nonleptonic_cascade_upper_proxy"]+
         .30*max(0.,r["abs_z_illustrative_NOT_CL"]-STOP_Z),
         r["abs_z_illustrative_NOT_CL"]))
    out=[];bins=set()
    for row in ranked:
        k=(int(row["mH1"]//25),int(row["mH2"]//55),
           int(row["gamma"]/.12))
        if k in bins:continue
        bins.add(k);out.append(row)
        if len(out)>=count:break
    if len(out)<count:
        for r in sorted(rows,key=lambda v:v["abs_z_illustrative_NOT_CL"]):
            if r["id"] not in {x["id"] for x in out}:
                out.append(r)
                if len(out)>=count:break
    return out,bool(eligible)

def source_crosscheck(exe,sample,backend):
    """Compiled E4A independently confirms exact A1S LO matching at H1/H2."""
    p=sample
    t=math.tan(p["beta"])
    obj=matching(exe,p["mH1"],p["mH2"],t,p["gamma"])
    light7,heavy7,mix7=coeff(obj,7)
    light8,heavy8,mix8=coeff(obj,8)
    for mass,d7,d8 in ((p["mH1"],light7,light8),
                       (p["mH2"],heavy7,heavy8)):
        a=backend(mass,t)
        close(a["delta_C7_LO"],d7,"A1S E4A independent C7",atol=3e-12)
        close(a["delta_C8_LO"],d8,"A1S E4A independent C8",atol=3e-12)
    close(p["delta_C7_LO"],mix7,"Zee gamma mixed C7",atol=3e-12)
    close(p["delta_C8_LO"],mix8,"Zee gamma mixed C8",atol=3e-12)
    pure=matching(exe,670.,670.,t,.39)
    l7,h7,d7=coeff(pure,7)
    l8,h8,d8=coeff(pure,8)
    close(l7,h7,"pure TypeII 670GeV equal-mass C7",atol=3e-12)
    close(l8,h8,"pure TypeII 670GeV equal-mass C8",atol=3e-12)
    ref=backend(670.,t)
    close(ref["delta_C7_LO"],d7,"A1S/E4A TypeII670 C7",atol=3e-12)
    close(ref["delta_C8_LO"],d8,"A1S/E4A TypeII670 C8",atol=3e-12)
    return {"matched_A1S_E4A_two_mass_C7_C8":True,
            "E4A_all_orders_input_rows_source_checked":len(obj[
                "coefficient_rows"])==24,
            "same_tanbeta_TypeII670_LO_2026_Eq4_crosscheck":True,
            "crosscheck_status":"SOURCE_CONSISTENT_NOT_FULL_NNLO_RATE"}

def fit_priorities(selected,rng,trials,local_seeds,maxfev):
    target,_=target_neutrino_matrix()
    results={}
    for n,row in enumerate(selected,1):
        # Must pass exactly original scalar solver again, not only trust
        # saved input row. This also rejects malformed "allowed" labels.
        p=scalar_row(row)
        theory=scalar_screen(p)
        if theory is None:raise ValueError("F13 saved scalar failed recheck")
        result=optimize_point(p,target,rng,trials=trials,
             local_seeds=local_seeds,max_evals=maxfev)
        results[row["id"]]=result
        print("F13_NEUTRINO_LFV",n,"/",len(selected),row["id"],
          result["status"],
          "PARTIAL_LFV_MAX_RATIO",result.get("best",{}).get(
              "score_partial_LFV_max_ratio_NOT_Full_CL"),
          "2026_EQ4_Z",round(row["abs_z_illustrative_NOT_CL"],4),
          "PROXY",round(row[
               "production_weighted_nonleptonic_cascade_upper_proxy"],5),
          "NOT_ALLOWED",flush=True)
    return results

def execute(args):
    if (args.seed_attempts<1 or args.seeds<1 or args.steps<0 or
        args.quad<40 or args.max_neutrino<1 or args.trials<1 or
        args.optimize_seeds<1 or args.optimize_evals<0 or
        args.temperature<=0):
        raise ValueError("Bad F13 campaign settings")
    out=args.output.resolve()
    if out.exists():raise FileExistsError("F13 refuse overwrite output")
    if not ROOT.resolve().is_relative_to(Path("/home")) or not out.is_relative_to(
         ROOT/"work"):
        raise ValueError("F13 requires source in /home and outputs in /home work")
    # Original F6 source must close the entire historic vendor manifest.
    if args.f6_dir is None:
        f6,old,meta,exe,pin=discover_f6(ROOT/"work")
    else:
        f6=args.f6_dir.resolve()
        old,meta,vendor,pin=original_source(f6)
    original,meta,vendor,pin=original_source(f6)
    seeds,seedmeta=validated_p1_seeds(
        args.seed_attempts,args.quad,args.seed,max_seeds=args.seeds)
    if not seeds:
        raise ValueError("F13 NO_HEAVY_P1_SCALAR_THEORY_EWPO_SEED: "
                         "finite search failed; not full Zee exclusion")
    out.mkdir(parents=True,exist_ok=False)
    binary,build=build_vendor(vendor,f6,out)
    # A1S is source-validated physical dipole matching at mu0=160 GeV.
    def backend(mass,tanbeta):
        return source_probe(binary,mass,tanbeta)
    rng=np.random.default_rng(args.seed+17)
    seedrows=[]
    for p,row in seeds:
        seedrows.append(row)
    write_csv(out/"F13_heavy_P1_seeds_NOT_ALLOWED.csv",seedrows,OUTPUT_COLS)
    rows,history=walk(seeds,args.steps,args.quad,rng,backend,
                     temperature=args.temperature,
                     report_every=args.report_every)
    ranked,has_good=pick(rows,args.max_neutrino)
    # E4A source source-check before spending time on family fits.
    probe=out/"F13_independent_E4A_matching"
    comp=compile_pilot(vendor,probe,
       ROOT/"scripts"/"zee_gateE4a_full_order_matching_probe.c",False)
    if comp["library_SHA256"]!=build["A1S_original_static_vendor_SHA256"]:
        raise ValueError("A1S/E4A static source vendor library mismatch")
    checks={r["id"]:source_crosscheck(probe,r,backend) for r in ranked}
    write_csv(out/RNAME,rows,
         OUTPUT_COLS+tuple(k for k in rows[0] if k not in OUTPUT_COLS))
    write_csv(out/SELECT,ranked,
         OUTPUT_COLS+tuple(k for k in rows[0] if k not in OUTPUT_COLS))
    flavor=fit_priorities(ranked,rng,args.trials,
                         args.optimize_seeds,args.optimize_evals)
    records=[]
    for i,row in enumerate(ranked,1):
        result=flavor[row["id"]]
        full={"scalar":row,"independent_A1S_E4A_matching":checks[row["id"]],
              "neutrino_and_partial_lfv":result,
              "physically_Zee_allowed":None,
              "modern_bsgamma_95CL":None,
              "hadronic_R_tbZ_pb":None,
              "all_model_constraints_complete":False,
              "missing_physics":MISSING}
        fname=f"F13_priority_{i:02d}_NOT_ALLOWED.json"
        writejson(out/fname,full)
        best=result.get("best",{})
        records.append({
          "candidate_id":row["id"],
          "mH1":row["mH1"],"mH2":row["mH2"],
          "gamma":row["gamma"],"tanbeta":row["tanbeta"],
          "2026_Eq4_LINEARIZED_BRx1e4":row[
              "2026_Eq4_LO_linearized_BRx1e4"],
          "2026_Eq4_Zee_to_same_tanbeta_TypeII670_LO_NP_shift_NOT_CL":
              row["Zee_to_same_tanbeta_TypeII670_2026Eq4_LO_NP_ratio_NOT_CL"],
          "z_UNCALIBRATED_NOT_CL":row["abs_z_illustrative_NOT_CL"],
          "z_below_1p96_diagnostic_ONLY":
              row["diagnostic_below_1p96_NOT_allowed"],
          "scalar_nonleptonic_included_cascade_proxy_NOT_pb":row[
              "production_weighted_nonleptonic_cascade_upper_proxy"],
          "neutrino_closed_fixed_old_NO":
              "best" in result,
          "partial_LFV_score_NOT_full_CL":best.get(
              "score_partial_LFV_max_ratio_NOT_Full_CL"),
          "partial_LFV_subset_below_reference":
              best.get("subset_below_all_implemented_reference_limits"),
          "lepton_included_cascade_proxy_NOT_pb":best.get(
              "charged_included_LO_cascade_proxy_NOT_pb"),
          "actual_hadronic_cross_section_pb":None,
          "2026_NNLO_excluded_or_allowed":None,
          "full_Zee_model_allowed_or_excluded":None,
        })
    with (out/REPORT).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]))
        w.writeheader();w.writerows(records)
    # Finite stopping rule means a diagnostic "screen" success is NOT
    # a final paper GO without the missing complete physics.
    flavor_viable=sum(("best" in flavor[r["id"]] and
          flavor[r["id"]]["best"][
             "subset_below_all_implemented_reference_limits"])
          for r in ranked if r["diagnostic_below_1p96_NOT_allowed"] and
          r["production_weighted_nonleptonic_cascade_upper_proxy"]>=.1)
    if flavor_viable:
        decision="PRELIM_SCREEN_GO_ONLY_CONTINUE_FULL_THEORY_NO_PAPER_GO"
    elif has_good:
        decision="SCALAR_FLAVOR_DIAGNOSTIC_EXISTS_BUT_NEUTRINO_SUBSET_UNRESOLVED"
    else:
        decision="NO_HIGH_CASCADE_BELOW_FLAVOR_DIAGNOSTIC_IN_FINITE_HEAVY_PILOT"
    z=sorted(x["abs_z_illustrative_NOT_CL"] for x in rows)
    summary={
      "status":STATUS,
      "flavor_aware_not_postselection_only":True,
      "seed_source":"P1-INSPIRED_REBUILT_SCALAR_NOT_PUBLISHED_POINT",
      "heavier_H1_search_GeV":[HEAVY_MIN,HEAVY_MAX],
      "heavier_H2_max_GeV":H2_MAX,
      "P1_accepted_seed_scan":seedmeta,
      "flavor_guided_walk":history,
      "unique_heavy_scalar_EWPO_points":len(rows),
      "flavor_diagnostic_lt1p96_in_scalar_cloud":sum(
           r["diagnostic_below_1p96_NOT_allowed"] for r in rows),
      "flavor_diag_z_min_median_max":[z[0],statistics.median(z),z[-1]],
      "max_cascade_proxy_among_diagnostic_below_1p96":
         max((r["production_weighted_nonleptonic_cascade_upper_proxy"]
              for r in rows if r["diagnostic_below_1p96_NOT_allowed"]),
             default=None),
      "selected_for_exact_neutrino_and_partial_lfv":len(ranked),
      "selected_same_vendor_independent_A1S_E4A_matching":len(checks),
      "neutrino_partial_lfv_successes":sum("best" in v for v in flavor.values()),
      "neutrino_plus_partial_lfv_under_reference_plus_eq4_diagnostic":
         flavor_viable,
      "finite_feasibility_decision_NOT_PAPER_GO":decision,
      "2026_complete_NNLO_twocharged_exclusions":None,
      "full_physical_model_allowed_or_excluded":None,
      "physical_hadronic_cascade_rate_pb":None,
      "paper1_publication_GO":None,
      "missing_full_constraints":MISSING,
      "source_provenance":{
         "F13_script_SHA256":digest(Path(__file__)),
         "F13_P1_seed_source_SHA256":digest(ROOT/"scripts"/
                                          "zee_paper1_F13_heavy_P1_seeds.py"),
         "Florentino_P1_region_SHA256":digest(ROOT/"data"/
                          "florentino2021_table2_regions.json"),
         "F6_original_source_summary_SHA256":digest(f6/"summary.json"),
         "original_A1S_build":build,
         "E4A_source_SHA256":digest(ROOT/"scripts"/
                             "zee_gateE4a_full_order_matching_probe.c"),
         "E4A_probe_executable_SHA256":digest(probe)},
      "outputs_SHA256":{name:digest(out/name) for name in (
         "F13_heavy_P1_seeds_NOT_ALLOWED.csv",RNAME,SELECT,REPORT)}
    }
    writejson(out/"summary.json",summary)
    writejson(out/"manifest.json",{
        "status":STATUS,"summary_SHA256":digest(out/"summary.json"),
        "F6_archive":str(f6),
        "full_model_allowed_or_excluded":None})
    print("F13_STATUS",STATUS,"SCALAR",len(rows),
          "EQ4_BELOW_1p96",summary["flavor_diagnostic_lt1p96_in_scalar_cloud"],
          "NEUTRINO_PARTIAL",summary["neutrino_partial_lfv_successes"],
          "SCREEN_GO",flavor_viable,
          "FULL_ALLOWED",None,flush=True)
    print("F13_FINITE_VERDICT",decision,flush=True)
    print("F13_SUMMARY",out/"summary.json",flush=True)
    return 0

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--f6-dir",type=Path)
    p.add_argument("--output",type=Path,default=DEFAULT)
    p.add_argument("--seed-attempts",type=int,default=450)
    p.add_argument("--seeds",type=int,default=6)
    p.add_argument("--steps",type=int,default=3200)
    p.add_argument("--quad",type=int,default=48)
    p.add_argument("--temperature",type=float,default=.10)
    p.add_argument("--max-neutrino",type=int,default=8)
    p.add_argument("--trials",type=int,default=80)
    p.add_argument("--optimize-seeds",type=int,default=2)
    p.add_argument("--optimize-evals",type=int,default=250)
    p.add_argument("--report-every",type=int,default=200)
    p.add_argument("--seed",type=int,default=20261021)
    try:
        return execute(p.parse_args(argv))
    except Exception as e:
        print("F13_FAIL_CLOSED",repr(e),file=sys.stderr,flush=True)
        traceback.print_exc()
        return 1

if __name__=="__main__":raise SystemExit(main())
