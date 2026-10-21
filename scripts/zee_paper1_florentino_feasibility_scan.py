#!/usr/bin/env python3
"""A single ACTUAL Zee scalar + complex-neutrino + partial-LFV feasibility scan.

Runs a new correlated scalar/EWPO B4 Markov proposal campaign; for
diverse scalar points constructs exact complex Zee neutrino solutions,
explores different f null-directions and all four complex homogeneous
Yukawa directions, locally optimizes the IMPLEMENTED coherent LFV
subset including fermion-photon Barr--Zee, and recalculates general
Zee charged-lepton widths in the same physical scalar point.

It is neither a full Zee experimental scan nor a paper discovery:
 - neutrino TARGET is a fixed, old central NO matrix, not 2026 NuFIT
   likelihood or IO scan;
 - the LFV amplitudes lack several two-loop/box/conversion classes;
 - new optimized scalar and Yukawas have NOT been evolved together in
   the complete RGE/charge-breaking or quark-alignment/FCNC systems;
 - no 2026 matched inclusive two-charged B->Xs gamma likelihood;
 - no complete 5-state widths, HiggsTools or real pp production rates.
All outputs explicitly record those gaps. NO point is labelled ALLOWED.
One command will LAUNCH a real physics screening scan, not fabricate a
publication-grade full-model exclusion.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import traceback
from datetime import datetime,timezone

import numpy as np
from scipy.optimize import minimize

from gateB4_adaptive_zee_scalar_scan import (
    read_seed_csv,scan as scalar_scan,shortlist as scalar_shortlist,
    write_csv as b4_write_csv,OUTPUT_COLS,scalar_screen,ewpo_screen,
    make_record,
)
from gateB2_zee_neutrino_family_scan import (
    solve_point,f_from_null_parameter,
)
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    reconstruct_neutrino,scalar_kappa,
)
from gateB3_general_zee_charged_lepton_widths import (
    evaluate as evaluate_charged_widths,complex_matrix,
)
from zee_gateD2_neutrino_exact_partial_LFV_optimization import (
    neutrino_family,make_yukawas,objective,amplitude_subset,
    optimize_kernels_cache,PERT,
)
from zee_priority1_contracts import hashfile

ROOT=Path(__file__).resolve().parents[1]
STATUS="PAPER1_ACTUAL_SCALAR_NEUTRINO_PARTIAL_LFV_CASCADE_PILOT_NOT_ALLOWED"
MISSING=(
 "independently validated 2026 NO+IO oscillation likelihood and phases",
 "complete LFV including remaining two-loop W/Z/charged-scalar terms, "
 "box/penguin modes and nuclear mu-e conversion",
 "complete physically matched modern two-charged B->Xs gamma likelihood",
 "finite full Zee quark alignment RGE+mass-basis FCNC/meson bounds",
 "fully revalidated 26 RGE scalar/flavor trajectories and global vacuum",
 "complete 5-state scalar widths and HiggsTools input and evaluation",
 "validated 4FS/5FS pp->t(b)H2 production cross sections and errors",
 "full physical production times branching ratio in pb",
)
SPECTRUM_FIELDS=("mH1","mH2","mh2","ma","alpha","beta","gamma",
                 "m12sq","lc","k1","k2","k12")
DEFAULT_OUT=ROOT/"work"/"zee_paper1_florentino_feasibility_scan_20261021_v1"
E2_NAME="E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv"

def dump(path,value):
    path=Path(path)
    path.write_text(json.dumps(value,indent=2,sort_keys=True,
                               allow_nan=False)+"\n")

def finite(value,label):
    if isinstance(value,bool):raise ValueError(label+": boolean input")
    val=float(value)
    if not math.isfinite(val):raise ValueError(label+": non-finite")
    return val

def scalar_row(src):
    p={key:finite(src[key],key) for key in SPECTRUM_FIELDS}
    if not (0<p["gamma"]<math.pi/2 and
            0<p["beta"]<math.pi/2 and
            p["mH2"]>p["mH1"]+91.1876):
        raise ValueError("Invalid charged spectrum/mixing")
    p["id"]=str(src["id"])
    if not p["id"]:raise ValueError("Empty candidate id")
    return p

def locate_seed_csv(work,explicit=None):
    """Prefer audited original 309, fall back to a documented P2 seed."""
    if explicit is not None:
        p=Path(explicit).resolve()
        if not p.is_file():raise FileNotFoundError(p)
        return p,"USER_SUPPLIED_SCALAR_CSV"
    hits=sorted(Path(work).glob("**/"+E2_NAME))
    if hits:
        by_hash={hashfile(x) for x in hits}
        if len(by_hash)!=1:
            raise ValueError("Multiple DIFFERENT E2 scalar cohort archives; "
                             "specify --seed-csv explicitly")
        # Check that the parent is a genuine published-output directory.
        proof=json.loads((hits[0].parent/"summary.json").read_text())
        if (proof.get("output_SHA256",{}).get(E2_NAME)!=hashfile(hits[0])
            or proof.get("no_deeper_tree_vacuum_witness_found")!=309
            or proof.get("full_Zee_experimental_allowed_or_excluded") is not None):
            raise ValueError("E2 source/provenance validation failed")
        return hits[0],"SOURCE_HASHED_E2_309_NO_DEEPER_WITNESS"
    return None,"NEW_P2_TABLE2_INSPIRED_SCALAR_START_NOT_PUBLISHED_SINGLE_POINT"

def p2_seed():
    from zee_reproduce_florentino_2021_regions import load_regions,build_inputs
    # Published P2 table region; beta=1.394 is OUR representative
    # in the 1%-wide interval; k12=0 is a NEW quartic boundary,
    # not the published value. See Section 8 documentation.
    region=load_regions()["benchmarks"]["P2"]
    inputs=build_inputs(region,mH1=300.,mH2=700.,beta=1.394,k12=0.)
    original={"id":"P2_INSPIRED_BETA1394_K120","mH1":300.,
              "mH2":700.,"mh2":inputs["mh2"],"ma":inputs["ma"],
              "beta":inputs["beta"],"alpha":inputs["alpha"],
              "gamma":inputs["gamma"],"m12sq":inputs["m12sq"],
              "lc":inputs["lc"],"k1":inputs["k1"],"k2":inputs["k2"],
              "k12":inputs["k12"]}
    return {**original,"seed_id":original["id"]}

def seeds_from_csv(path,count):
    """Start with high included-channel proxy, but preserve diversity."""
    raw=read_seed_csv(path)
    keep={k:v for k,v in enumerate(raw)} # do not mutate archive records
    # B4 read_seed_csv provides scalar source IDs and all quartics.
    # Use existing B4 proxy where available, otherwise physical geometry.
    def merit(p):
        return (math.sin(float(p["gamma"]))**2*
                math.sin(2*float(p["gamma"]))**2)
    chosen=[]
    bins=set()
    for p in sorted(keep.values(),key=merit,reverse=True):
        cell=(int(p["mH1"]//45),int(p["mH2"]//65),
              int(p["gamma"]/.15))
        if cell in bins:continue
        bins.add(cell);chosen.append(p)
        if len(chosen)==count:break
    if not chosen:raise ValueError("No diverse original B4 seeds")
    return chosen

def choose_best(rows,n):
    """Mass/mixing diversity, not posterior or allowed volume."""
    selected=scalar_shortlist(rows,n)
    if not selected:raise ValueError("B4 found no scalar candidates")
    return selected

def complex_payload(z):
    z=np.asarray(z,complex)
    if z.shape!=(3,3) or not np.isfinite(z).all():
        raise ValueError("Nonfinite/invalid complex 3x3 Yukawa")
    return {"real":z.real.tolist(),"imag":z.imag.tolist()}

def build_trial(point,target,rng,index,f_default):
    """Use rank-5 exact neutrino solver; vary f orientation and null-Y."""
    if index==0:
        f=f_default.copy()
        strength=0.
    else:
        t=complex(rng.uniform(-1.5,1.5),
                  rng.uniform(-1.5,1.5))
        f=f_from_null_parameter(target,t,10**rng.uniform(-6,-2),
                                 int(rng.integers(0,2)))
        strength=float(10**rng.uniform(-2,1))
    return solve_point(point,target,f,rng,strength)

def local_optimize(point,target,trial,max_evals):
    """Local optimize only the LFV subset, never global fitness/CL."""
    family=neutrino_family(point,trial)
    x0=np.asarray(family["starting_coords"],float)
    if x0.shape!=(9,):raise ValueError("D2 complex nullspace shape")
    original=float(max(amplitude_subset(
        point,complex_matrix(trial["f"],"f"),
        complex_matrix(trial["Y"],"Y")).values()))
    limit=math.log(30.)
    bounds=[(-limit,limit)]+[
        (float(v-3),float(v+3)) for v in x0[1:]]
    if max_evals:
        outcome=minimize(lambda x:objective(family,x),x0,
                         method="Powell",bounds=bounds,
                         options={"maxfev":max_evals,"maxiter":max_evals,
                                  "xtol":5e-4,"ftol":3e-4})
        configs=[("seed",x0)]
        if np.isfinite(outcome.fun):
            configs.append(("Powell_subset_optimized",
                            np.asarray(outcome.x,float)))
    else:
        outcome=None
        configs=[("seed",x0)]
    valid=[]
    for name,x in configs:
        f,Y=make_yukawas(family,x)
        if not np.isfinite(f).all() or not np.isfinite(Y).all():
            continue
        if max(float(np.max(abs(f))),float(np.max(abs(Y))))>=PERT:
            continue
        err=float(np.max(abs(
            reconstruct_neutrino(f,Y,kappa=scalar_kappa(
                point["mH1"],point["mH2"],point["gamma"]))-target)))
        if err>=1e-9 or not math.isfinite(err):
            continue
        ratios=amplitude_subset(point,f,Y)
        score=max(ratios.values())
        width=evaluate_charged_widths(point,f,Y,target)
        if (width["status"]!=
            "GENERAL_ZEE_LEPTON_WIDTHS_LO_INCLUDED_ONLY_NOT_ALLOWED"):
            raise ValueError("Unexpected charged width status")
        valid.append((score,name,f,Y,ratios,width,err))
    if not valid:raise ValueError("No valid local LFV minimum")
    best=min(valid,key=lambda p:p[0])
    if best[0]>original*(1+1e-7):
        raise ValueError("Optimization worsened its own physical seed")
    score,name,f,Y,ratios,width,err=best
    return {
       "score_partial_LFV_max_ratio_NOT_Full_CL":float(score),
       "prior_partial_LFV_max_ratio":float(original),
       "subset_below_all_implemented_reference_limits":bool(score<1),
       "optimization_source":name,
       "optimizer_nfev":int(outcome.nfev) if outcome is not None else 0,
       "optimized_f":complex_payload(f),
       "optimized_Y":complex_payload(Y),
       "max_abs_f":float(np.max(abs(f))),
       "max_abs_Y":float(np.max(abs(Y))),
       "neutrino_matrix_closure_eV":err,
       "fixed_NO_target_not_modern_likelihood":True,
       "implemented_partial_LFV_channel_ratios":ratios,
       "charged_included_channel_widths_GeV":
           width["partial_widths_included_GeV"],
       "BR_H2_H1Z_included_channels_ONLY":
           width["BR_H2_H1Z_included_general_Zee"],
       "BR_H1_tb_included_channels_ONLY":
           width["BR_H1_tb_included_general_Zee"],
       "charged_included_LO_cascade_proxy_NOT_pb":
           width["production_weighted_partial_cascade_proxy"],
       "full_physical_decay_BRs":None,
       "hadronic_production_sigma_pb":None,
       "physical_signal_R_tbZ_pb":None,
       "fully_Zee_allowed_or_excluded":None,
    }

def optimize_point(point,target,rng,*,trials,local_seeds,max_evals):
    default,_=antisymmetric_f_with_null_condition(target)
    candidates=[]
    errors={}
    for i in range(trials):
        try:
            t=build_trial(point,target,rng,i,default)
            if t is not None:
                candidates.append(t)
            else:errors["nonperturbative"] = errors.get("nonperturbative",0)+1
        except (ValueError,ArithmeticError,FloatingPointError,
                np.linalg.LinAlgError) as e:
            key=type(e).__name__
            errors[key]=errors.get(key,0)+1
    if not candidates:
        return {"status":"NO_NEUTRINO_CLOSED_TRIALS_FOUND_NOT_EXCLUSION",
                "trials":trials,"trial_errors":errors,
                "model_allowed_or_excluded":None}
    candidates.sort(key=lambda x:x["partial_LFV_score_NOT_EXCLUSION"])
    best=[]
    # Always include first f orientation, when available; distinct null roots
    # are independent initial solutions, not statistical sample weights.
    for trial in candidates[:local_seeds]:
        try:
            best.append(local_optimize(point,target,trial,max_evals))
        except (ValueError,ArithmeticError,FloatingPointError,
                OverflowError,np.linalg.LinAlgError) as e:
            name="optimization_"+type(e).__name__
            errors[name]=errors.get(name,0)+1
    if not best:
        return {"status":"ALL_LOCAL_OPTIMIZATIONS_INVALID_NOT_EXCLUSION",
                "trials":trials,"neutrino_closed_trials":len(candidates),
                "trial_errors":errors,"model_allowed_or_excluded":None}
    best.sort(key=lambda q:q["score_partial_LFV_max_ratio_NOT_Full_CL"])
    return {
        "status":"NEUTRINO_EXACT_WITH_PARTIAL_LFV_AND_INCLUDED_CASCADE_ONLY",
        "trials":trials,
        "neutrino_closed_trials":len(candidates),
        "local_optima_checked":len(best),
        "trial_errors":errors,
        "best":best[0],
        "other_local_optimizations":[{
            "score_partial_LFV_max_ratio_NOT_Full_CL":
                 z["score_partial_LFV_max_ratio_NOT_Full_CL"],
            "charged_included_LO_cascade_proxy_NOT_pb":
                 z["charged_included_LO_cascade_proxy_NOT_pb"],
        } for z in best[1:]],
        "model_allowed_or_excluded":None,
    }

def execute(args):
    if args.max_spectra<1 or args.scalar_steps<0 or args.trials<1 or (
      args.optimize_seeds<1 or args.optimize_evals<0 or
      args.quadrature_nodes<40 or args.chains<1):
        raise ValueError("Invalid scan parameters")
    output=Path(args.output).resolve()
    if output.exists():raise FileExistsError(
        "Existing output; specify a distinct --output folder")
    seed_csv,kind=locate_seed_csv(ROOT/"work",args.seed_csv)
    seeds=seeds_from_csv(seed_csv,args.seed_count) if seed_csv else [p2_seed()]
    # Require all initial seeds to satisfy the same B4 screening as
    # proposals. Never transport a failed historical label.
    valid=[]
    for seed in seeds:
        try:
            p={k:seed[k] for k in SPECTRUM_FIELDS}
            th=scalar_screen(p)
            if th is None:continue
            if ewpo_screen(p,args.quadrature_nodes) is None:continue
            valid.append(seed)
        except (ValueError,ArithmeticError,FloatingPointError,
                np.linalg.LinAlgError):
            continue
    if not valid:
        raise ValueError("No scalar/EWPO seeds survive the tested B4 "
                         "domain; do not generate false benchmark")
    output.mkdir(parents=True,exist_ok=False)
    provenance={
        "repo_script_sha256":hashfile(Path(__file__)),
        "source_seed_csv":str(seed_csv) if seed_csv else None,
        "source_seed_SHA256":hashfile(seed_csv) if seed_csv else None,
        "seed_type":kind,
        "local_seed_count":len(valid),
        "B4_backend_SHA256":hashfile(ROOT/"scripts"/
                                    "gateB4_adaptive_zee_scalar_scan.py"),
        "B2_backend_SHA256":hashfile(ROOT/"scripts"/
                                    "gateB2_zee_neutrino_family_scan.py"),
        "D2_backend_SHA256":hashfile(ROOT/"scripts"/
                            "zee_gateD2_neutrino_exact_partial_LFV_optimization.py"),
        "B3_backend_SHA256":hashfile(ROOT/"scripts"/
                                    "gateB3_general_zee_charged_lepton_widths.py"),
        "random_seed":args.seed,
    }
    dump(output/"manifest_start.json",{
        "status":"SCAN_LAUNCHED","UTC":datetime.now(timezone.utc).isoformat(),
        "provenance":provenance,"full_Zee_allowed_or_excluded":None})
    print("PAPER1_SCAN_STARTED",output,kind,
          "SCALAR_PROPOSALS",args.scalar_steps,flush=True)
    rng=np.random.default_rng(args.seed)
    records,scalar_summary=scalar_scan(
        valid,steps=args.scalar_steps,
        chains=args.chains,quad=args.quadrature_nodes,
        adaptive_block=max(20,min(200,max(20,args.scalar_steps))),
        rng=rng,report_every=max(1,args.scalar_steps//5) if args.scalar_steps else 0)
    if not records:raise ValueError("No scalar-screened records")
    b4_write_csv(output/"new_B4_scalar_EWPO_NOT_ALLOWED.csv",
                 records,OUTPUT_COLS)
    chosen=choose_best(records,args.max_spectra)
    b4_write_csv(output/"selected_scalar_spectra_NOT_ALLOWED.csv",
                 chosen,OUTPUT_COLS)
    total={}
    target,_=target_neutrino_matrix()
    optimize_kernels_cache()
    for i,row in enumerate(chosen,1):
        p=scalar_row(row)
        result=optimize_point(p,target,rng,trials=args.trials,
                              local_seeds=args.optimize_seeds,
                              max_evals=args.optimize_evals)
        key=p["id"]
        if key in total:raise ValueError("Repeated scalar ID")
        total[key]={"scalar":{k:p[k] for k in p},
                    "scalar_screen_status":
                      "B4_THEORY_EWPO_SCREEN_ONLY_NOT_ALLOWED",
                    "source_B4_included_no_leptons_cascade_proxy_NOT_pb":
                      row["production_weighted_nonleptonic_cascade_upper_proxy"],
                    "flavor":result,"missing_full_constraints":list(MISSING),
                    "full_Zee_allowed_or_excluded":None}
        dump(output/(f"point_{i:02d}_NOT_ALLOWED.json"),total[key])
        print("PAPER1_SCAN_POINT",i,"/",len(chosen),key,
              result["status"],
              "BEST_SUBSET_RATIO",result.get("best",{}).get(
                  "score_partial_LFV_max_ratio_NOT_Full_CL"),
              flush=True)
    completed=[q["flavor"]["best"] for q in total.values()
               if "best" in q["flavor"]]
    rows=[]
    for k,v in total.items():
        b=v["flavor"].get("best",{})
        rows.append({
            "candidate_id":k,"mH1_GeV":v["scalar"]["mH1"],
            "mH2_GeV":v["scalar"]["mH2"],
            "gamma":v["scalar"]["gamma"],
            "scalar_EWPO_screen_only":True,
            "neutrino_exact_fixed_NO":bool(b),
            "neutrino_closure_eV":b.get("neutrino_matrix_closure_eV"),
            "partial_LFV_max_ratio_NOT_CL":
                b.get("score_partial_LFV_max_ratio_NOT_Full_CL"),
            "partial_LFV_subset_below_reference":
                b.get("subset_below_all_implemented_reference_limits"),
            "nonleptonic_cascade_proxy_NOT_pb":
              v["source_B4_included_no_leptons_cascade_proxy_NOT_pb"],
            "flavor_corrected_included_cascade_proxy_NOT_pb":
                b.get("charged_included_LO_cascade_proxy_NOT_pb"),
            "R_tbZ_physical_pb":None,
            "fully_allowed":None,
        })
    with (output/"ranked_florentino_injection_NOT_ALLOWED.csv").open(
            "w",newline="") as f:
        fields=list(rows[0])
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(sorted(rows,key=lambda r:(
            r["partial_LFV_max_ratio_NOT_CL"] is None,
            r["partial_LFV_max_ratio_NOT_CL"]
            if r["partial_LFV_max_ratio_NOT_CL"] is not None else 1e99)))
    summary={
        "status":STATUS,
        "scan_executed_on_AF":None,
        "execution_environment":os.uname().nodename,
        "original_scalar_seed_classification":kind,
        "new_scalar_proposals_attempted":args.scalar_steps,
        "scalar_summary":scalar_summary,
        "selected_spectra":len(chosen),
        "exact_neutrino_and_partial_LFV_solves":len(completed),
        "partial_LFV_subset_below_limits":sum(
            x["subset_below_all_implemented_reference_limits"]
            for x in completed),
        "scientific_novelty_or_physical_allowed_established":False,
        "modern_model_complete_constraints_passed":None,
        "physical_collider_production_rate_pb":None,
        "paper1_GO_or_NOGO":None,
        "candidate_ids":list(total),
        "missing_full_constraints":list(MISSING),
        "source":provenance,
        "candidate_file_SHA256":{
          filename:hashfile(output/filename) for filename in
          ("new_B4_scalar_EWPO_NOT_ALLOWED.csv",
           "selected_scalar_spectra_NOT_ALLOWED.csv",
           "ranked_florentino_injection_NOT_ALLOWED.csv")},
    }
    dump(output/"summary.json",summary)
    dump(output/"manifest.json",{
        "status":STATUS,"summary_SHA256":hashfile(output/"summary.json"),
        "source":provenance,
        "full_Zee_allowed_or_excluded":None})
    print("PAPER1_SCAN_STATUS",STATUS,
          "SCALAR",len(records),"SOLVED",len(completed),
          "FULLY_ALLOWED",None,flush=True)
    print("PAPER1_SCAN_SUMMARY",output/"summary.json",flush=True)
    return summary

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed-csv",type=Path,
        help="Optional prior B4/E2 scalar source. Default autodiscovers "
             "SHA-validated E2 cohort; if absent uses a new P2-inspired point.")
    p.add_argument("--output",type=Path,default=DEFAULT_OUT)
    p.add_argument("--seed-count",type=int,default=6)
    p.add_argument("--max-spectra",type=int,default=6)
    p.add_argument("--scalar-steps",type=int,default=240)
    p.add_argument("--chains",type=int,default=6)
    p.add_argument("--quadrature-nodes",type=int,default=64)
    p.add_argument("--trials",type=int,default=50)
    p.add_argument("--optimize-seeds",type=int,default=2)
    p.add_argument("--optimize-evals",type=int,default=240)
    p.add_argument("--seed",type=int,default=20261021)
    a=p.parse_args(argv)
    try:
        execute(a)
        return 0
    except Exception as err:
        print("PAPER1_SCAN_FAIL_CLOSED",repr(err),file=sys.stderr)
        traceback.print_exc()
        return 1

if __name__=="__main__":
    raise SystemExit(main())
