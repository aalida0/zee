#!/usr/bin/env python3
"""F20: one large AF-independent Zee phenomenology campaign shard.

Runs ACTUAL broad B4 scalar EWPO proposal exploration, 2026 published
linearized analytic LO C7,C8 screening at each surviving scalar point,
exact fixed-NO complex f/Y neutrino+coherent PARTIAL LFV optimization
at diverse frontier points, B3 included-channel charged BRs, and full
dimensionful C5 six-dimensional tree vacuum witness search for selected
points. Four independently seeded shards are intended for HTCondor.

Authenticates the real original F18/F19/F19b/F19c/F19d anchor cohort by
SHA and uses their original F19 scalar parameters as three seed chains.
New scan points DO NOT have SARAH-UFO/MadWidth or HiggsTools full decay
predictions. No CL or fully allowed point can result from this script.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,traceback
from collections import Counter
from pathlib import Path
import numpy as np

from zee_paper1_F19d_AF_independent_analytic_LO_bsgamma import (
    STATUS as F19D_STATUS,checked_cohort,model,CASES,sha)
from gateB4_adaptive_zee_scalar_scan import (
    scan as scalar_scan,encode,decode,scalar_screen,ewpo_screen,
    nonleptonic_proxy)
from zee_paper1_florentino_feasibility_scan import (
    scalar_row,optimize_point)
from gateA1b_hierarchical_no_seed import target_neutrino_matrix
from zee_gateD2_neutrino_exact_partial_LFV_optimization import optimize_kernels_cache
from zee_gateC1_joined_uv_pilot import scalar_lagrangian
from zee_gateC5_charge_breaking_vacuum_search import (
    candidate_starts,evaluate_multistart)

STATUS="F20_AF_INDEPENDENT_LARGE_SCALAR_NEUTRINO_PARTIAL_LFV_LO_FLAVOR_VACUUM_SCAN_NOT_ALLOWED"
GAPS=[
    "Complete 2026 two-charged NNLO B->Xs gamma and scheme/calibrated covariance",
    "Complete Zee LFV including remaining two loops, mu-e conversion, boxes and penguins",
    "NuFIT orderings, PMNS phases and errors; fixed NO central target only",
    "Complete 5-state HiggsTools rate/decay inputs and direct charged searches",
    "Full-QCD physical hadron rates and full MadWidth every scan point",
    "Numerically global/loop-corrected EW vacuum certification",
    "All relevant quark FCNCs, CKM/RGE precision alignment and non-oblique EW precision",
]
COLS=["candidate_id","shard","mH1","mH2","mh2","ma","beta","gamma",
      "tanbeta","max_unitarity","chi2_Gfitter","chi2_PDG",
      "cascade_included_nonleptonic_proxy_NOT_F18_MadWidth",
      "LO_C7_mu160_mt163","LO_C8_mu160_mt163",
      "LO_Bsgamma_linearized_x1e4_NOT_CL",
      "LO_Zee_over_670_shift_NOT_CL","LO_Bsgamma_shift_x1e4_NOT_CL",
      "ranked_for_LFV_fit"]
def dump(path,object):
    Path(path).write_text(json.dumps(object,sort_keys=True,
             indent=2,allow_nan=False)+"\n")
def save_csv(path,rows,columns):
    with Path(path).open("w",newline="") as fd:
        w=csv.DictWriter(fd,fieldnames=columns,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
def frontier(rows):
    # Direction: maximize included-channel cascade PROXY and minimize
    # diagnostic LO B->Xs gamma shift; NO experiment exclusion is implied.
    ordered=sorted(rows,key=lambda r:(
        r["LO_Bsgamma_shift_x1e4_NOT_CL"],
        -r["cascade_included_nonleptonic_proxy_NOT_F18_MadWidth"],
        r["candidate_id"]))
    best=-math.inf
    pareto=[]
    for r in ordered:
        proxy=r["cascade_included_nonleptonic_proxy_NOT_F18_MadWidth"]
        if proxy>best+1e-15:
            pareto.append(r)
            best=proxy
    return pareto
def diverse_selection(allrows,limit):
    # Union of strong cascade proxy and low analytic flavor shift.
    # Sampled B4 walk is NOT unbiased allowed-volume/posterior inference.
    sorted_proxy=sorted(allrows,key=lambda r:
       -r["cascade_included_nonleptonic_proxy_NOT_F18_MadWidth"])
    sorted_flavor=sorted(allrows,key=lambda r:
        r["LO_Bsgamma_shift_x1e4_NOT_CL"])
    order=[]
    for i in range(max(len(sorted_proxy),len(sorted_flavor))):
        if i<len(sorted_proxy):order.append(sorted_proxy[i])
        if i<len(sorted_flavor):order.append(sorted_flavor[i])
    selected=[];seen=set()
    for r in order:
        cell=(int(r["mH1"]//20),int(r["mH2"]//35),
              int(r["gamma"]/.08),int(r["beta"]/.008))
        if cell in seen:continue
        seen.add(cell);selected.append(r)
        if len(selected)==limit:break
    return selected
def seeds_from_real_f19(by19):
    out=[]
    for name in CASES:
        p=dict(by19[name]["scalar_original_F16_inputs"])
        x=decode(encode(p))
        if x is None:raise ValueError("Real F19 source point outside scanner domain")
        # Preserve exact seed source and run same B4 scalar+EWPO screen.
        if scalar_screen(x) is None:
            raise ValueError("F19 original benchmark fails B4 scalar replay "+name)
        out.append({"seed_id":name,**x})
    return out
def verify(f18,f19,f19b,f19c,f19d):
    files,objs,cohort=checked_cohort(f18,f19,f19b,f19c)
    d=json.loads(Path(f19d).read_text())
    if (d.get("status")!=F19D_STATUS
        or d.get("original_three_cases_matched") is not True
        or d.get("full_Zee_model_experimentally_allowed_or_excluded") is not None):
        raise ValueError("F19d original analytical real-point cohort invalid")
    manifest=d.get("actual_CERN_F18_F19_F19b_F19c_source_SHA256",{})
    for label,source in zip(("F18","F19","F19b","F19c"),files):
        if manifest.get(label)!=sha(source):
            raise ValueError("F19d source anchor SHA mismatch "+label)
    rows=d.get("rows",[])
    if len(rows)!=9 or set(x["candidate_id"] for x in rows)!=set(CASES):
        raise ValueError("F19d source original 9-row mt scenario mismatched")
    return files,objs,cohort
def execute(args):
    if not (0<=args.shard<=63 and 200<=args.steps<=100000 and
        1<=args.fits<=500 and 10<=args.trials<=2000 and
        0<=args.opt_evals<=2500 and 1<=args.optimize_seeds<=8 and
        0<=args.vacuum<=args.fits and 64<=args.vacuum_starts<=512 and
        40<=args.quad<=320):
        raise ValueError("F20 campaign resource settings invalid")
    out=Path(args.output).expanduser().resolve()
    if out.exists():raise FileExistsError("Never overwrite an F20 shard")
    files,src,by=verify(args.f18,args.f19,args.f19b,args.f19c,args.f19d)
    by18,by19,_,_=by
    s=args.seed+args.shard*100003
    rng=np.random.default_rng(s)
    seeds=seeds_from_real_f19(by19)
    out.mkdir(parents=True,exist_ok=False)
    manifest={
      "status":"F20_RUNNING_PARTIAL_NO_ACCEPTANCE",
      "original_source_SHA256":{k:sha(p) for k,p in zip(
        ("F18","F19","F19b","F19c","F19d"),
        (args.f18,args.f19,args.f19b,args.f19c,args.f19d))},
      "original_three_verified_F18_benchmarks":list(CASES),
      "shard":args.shard,"random_seed":s,
      "steps":args.steps,"requested_LFV_fits":args.fits,
      "requested_vacuum_searches":args.vacuum,
      "full_Zee_allowed_or_excluded":None,
    }
    dump(out/"manifest_started.json",manifest)
    print("F20_BROAD_SCALAR_START","SHARD",args.shard,"STEPS",args.steps,flush=True)
    screened,summary=scalar_scan(
       seeds,steps=args.steps,chains=max(3,args.chains),
       quad=args.quad,adaptive_block=200,rng=rng,
       report_every=max(250,args.steps//8))
    if not screened:raise ValueError("No scalar/EWPO accepted points")
    evaluated=[]
    for item in screened:
        p={k:item[k] for k in ("mH1","mH2","beta","gamma")}
        flav=model(p["mH1"],p["mH2"],p["beta"],p["gamma"],163.)
        vals={
           "candidate_id":item["id"],"shard":args.shard,
           "cascade_included_nonleptonic_proxy_NOT_F18_MadWidth":item[
              "production_weighted_nonleptonic_cascade_upper_proxy"],
           "LO_C7_mu160_mt163":flav["delta_C7_LO_analytic"],
           "LO_C8_mu160_mt163":flav["delta_C8_LO_analytic"],
           "LO_Bsgamma_linearized_x1e4_NOT_CL":flav[
              "linearized_2026_central_BR_x1e4"],
           "LO_Bsgamma_shift_x1e4_NOT_CL":flav[
              "linearized_2026_shift_x1e4"],
           "LO_Zee_over_670_shift_NOT_CL":flav[
              "Zee_shift_over_TypeII670_shift_LO_NOT_CL"],
           "ranked_for_LFV_fit":False,
        }
        evaluated.append({**item,**vals})
    proposed_frontier=frontier(evaluated)
    chosen=diverse_selection(evaluated,args.fits)
    if not chosen:raise ValueError("No points for the exact neutrino+partial LFV fit")
    ranked_ids=set(x["candidate_id"] for x in chosen)
    for r in evaluated:r["ranked_for_LFV_fit"]=r["candidate_id"] in ranked_ids
    save_csv(out/"F20_all_scalar_LO_flavor_NOT_EXCLUSION.csv",evaluated,COLS)
    save_csv(out/"F20_pareto_cascade_vs_LO_flavor_NOT_EXCLUSION.csv",
             proposed_frontier,COLS)
    save_csv(out/"F20_selected_complex_neutrino_fits_NOT_ALLOWED.csv",chosen,COLS)
    dump(out/"scalar_stage_summary.json",{"status":"F20_SCALAR_LO_DIAGNOSTIC_NOT_ALLOWED",
         "scan_summary":summary,"frontier_count":len(proposed_frontier),
         "full_model_allowed":None})
    print("F20_SCALAR_READY","SHARD",args.shard,"DISTINCT",len(evaluated),
          "PARETO",len(proposed_frontier),"LFV_SELECTED",len(chosen),flush=True)
    target,_=target_neutrino_matrix()
    optimize_kernels_cache()
    fits=[];failures=Counter()
    for i,r in enumerate(chosen,1):
        p=scalar_row(r)
        try:
            sol=optimize_point(p,target,rng,trials=args.trials,
                       local_seeds=args.optimize_seeds,
                       max_evals=args.opt_evals)
            if sol["status"]!="NEUTRINO_EXACT_WITH_PARTIAL_LFV_AND_INCLUDED_CASCADE_ONLY":
                failures[sol["status"]]+=1
            entry={"candidate_id":r["candidate_id"],
                   "scalar":{k:p[k] for k in p},
                   "LO_flavor_screen_analytic_not_CL":{
                       k:r[k] for k in ("LO_Bsgamma_linearized_x1e4_NOT_CL",
                         "LO_Zee_over_670_shift_NOT_CL")},
                   "LO_included_cascade_not_full_MadWidth":r[
                       "cascade_included_nonleptonic_proxy_NOT_F18_MadWidth"],
                   "fixed_NO_complex_neutrino_and_partial_LFV":sol,
                   "F20_all_model_allowed":None}
        except (ValueError,ArithmeticError,OverflowError,
                np.linalg.LinAlgError) as exc:
            failures[type(exc).__name__]+=1
            entry={"candidate_id":r["candidate_id"],
                   "error":repr(exc),"F20_all_model_allowed":None}
        fits.append(entry)
        dump(out/("point_"+str(i).zfill(3)+"_NOT_ALLOWED.json"),entry)
        print("F20_COMPLEX_FIT",args.shard,i,"/",len(chosen),r["candidate_id"],
              "SCORE",entry.get("fixed_NO_complex_neutrino_and_partial_LFV",{})
              .get("best",{}).get("score_partial_LFV_max_ratio_NOT_Full_CL"),
              flush=True)
    valid=[r for r in fits
      if "best" in r.get("fixed_NO_complex_neutrino_and_partial_LFV",{})]
    # Vacuum subset covers the strongest combined proxy and partial LFV fits.
    # A full vacuum certificate would require a different mathematical method.
    prioritized=sorted(valid,key=lambda r:(
       -r["LO_included_cascade_not_full_MadWidth"],
       r["fixed_NO_complex_neutrino_and_partial_LFV"]["best"][
        "score_partial_LFV_max_ratio_NOT_Full_CL"]))
    vacuums=[];vacuum_errors=Counter()
    for i,fit in enumerate(prioritized[:args.vacuum],1):
        p=fit["scalar"]
        try:
            state,_=scalar_lagrangian(p)
            sub_seed=s+int.from_bytes(hashlib.sha256(
                  fit["candidate_id"].encode()).digest()[:4],"big")
            starts=candidate_starts(args.vacuum_starts,sub_seed%(2**32))
            vac=evaluate_multistart(p,state,starts,maxiter=args.vacuum_iters)
            if vac["search_is_not_a_global_minimization_certificate"] is not True:
                raise ValueError("C5 global certificate semantics changed")
            value={
              "candidate_id":fit["candidate_id"],
              "C5_tree_vacuum_witness":vac["status"],
              "deeper_witness_found":vac["most_negative_witness"] is not None,
              "vacuum_search":vac,
              "full_model_allowed":None,
            }
        except (ValueError,ArithmeticError,OverflowError,
                np.linalg.LinAlgError) as exc:
            vacuum_errors[type(exc).__name__]+=1
            value={"candidate_id":fit["candidate_id"],"error":repr(exc),
                   "full_model_allowed":None}
        vacuums.append(value)
        dump(out/("vacuum_"+str(i).zfill(3)+"_NOT_GLOBAL.json"),value)
        print("F20_VACUUM",args.shard,i,"/",min(args.vacuum,len(prioritized)),
           fit["candidate_id"],value.get("C5_tree_vacuum_witness"),
           flush=True)
    tab=[]
    vacuum_map={x["candidate_id"]:x for x in vacuums}
    for r in fits:
        name=r["candidate_id"]
        sol=r.get("fixed_NO_complex_neutrino_and_partial_LFV",{})
        best=sol.get("best",{})
        v=vacuum_map.get(name,{})
        tab.append({
            "candidate_id":name,
            "mH1_GeV":r.get("scalar",{}).get("mH1"),
            "mH2_GeV":r.get("scalar",{}).get("mH2"),
            "gamma_rad":r.get("scalar",{}).get("gamma"),
            "cascade_included_LO_proxy_NOT_MadWidth":r.get(
               "LO_included_cascade_not_full_MadWidth"),
            "LO_flavor_BR_x1e4_NOT_CL":r.get("LO_flavor_screen_analytic_not_CL",{}).get(
               "LO_Bsgamma_linearized_x1e4_NOT_CL"),
            "LFV_partial_score_NOT_EXCLUSION":best.get(
               "score_partial_LFV_max_ratio_NOT_Full_CL"),
            "fixed_NO_neutrino_closure_eV":best.get("neutrino_matrix_closure_eV"),
            "vacuum_no_deeper_witness_found_NOT_PROOF":v.get(
               "C5_tree_vacuum_witness")==
               "NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE" if v else None,
            "full_model_allowed":"UNKNOWN_NOT_EVALUATED",
        })
    tab.sort(key=lambda r:(
      r["LFV_partial_score_NOT_EXCLUSION"] is None,
      -(r["cascade_included_LO_proxy_NOT_MadWidth"] or 0.)))
    save_csv(out/"F20_paper_scan_shortlist_NOT_ALLOWED.csv",tab,list(tab[0]))
    final={"status":STATUS,
          **manifest,
          "completed_new_scalar_bins":len(evaluated),
          "passed_scalar_EWPO_proposals":summary["EWPO_screen_pass_proposals"],
          "analytic_LO_two_charged_flavor_evaluated_points":len(evaluated),
          "neutrino_partial_LFV_attempted":len(chosen),
          "neutrino_partial_LFV_completed":len(valid),
          "vacuum_multistart_evaluated":len(vacuums),
          "LFV_fit_failures":dict(failures),
          "vacuum_errors":dict(vacuum_errors),
          "theoretical_95pct_Zee_exclusion":None,
          "model_fully_allowed_or_excluded":None,
          "missing_for_publishable_complete_model":GAPS,
          "largest_spectrum_still_not_source_validated_in_UFO":True,
          "F18_MadWidth_is_original_3_points_only":True,
          "B4_acceptance_is_not_allowed_volume_or_posterior":True,
          "F20_outputs_SHA256":{p.name:sha(p) for p in out.glob("*.csv")},
          }
    final["status"]=STATUS
    dump(out/"F20_shard_complete_summary.json",final)
    print("F20_SHARD_COMPLETE",args.shard,"SCALAR",len(evaluated),
          "NEUTRINO_SOLVES",len(valid),"VACUUM",len(vacuums),
          "FULL_MODEL_ALLOWED",None,flush=True)
    return final
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("f18","f19","f19b","f19c","f19d","output"):
        p.add_argument("--"+key,required=True,type=Path)
    p.add_argument("--shard",type=int,required=True)
    p.add_argument("--seed",type=int,default=20261024)
    p.add_argument("--steps",type=int,default=5000)
    p.add_argument("--chains",type=int,default=8)
    p.add_argument("--quad",type=int,default=64)
    p.add_argument("--fits",type=int,default=30)
    p.add_argument("--trials",type=int,default=90)
    p.add_argument("--optimize-seeds",type=int,default=2)
    p.add_argument("--opt-evals",type=int,default=180)
    p.add_argument("--vacuum",type=int,default=12)
    p.add_argument("--vacuum-starts",type=int,default=64)
    p.add_argument("--vacuum-iters",type=int,default=350)
    args=p.parse_args()
    execute(args)
if __name__=="__main__":main()
