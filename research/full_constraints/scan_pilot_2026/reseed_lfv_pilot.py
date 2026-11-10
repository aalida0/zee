#!/usr/bin/env python3
"""Fixed-scalar inverse-neutrino/partial-LFV materiality pilot.

This is NOT a full Zee LFV veto and does NOT rescan scalar parameters.
Sample *new neutrino family IDs* using unmodified deterministic Module14
inverse-neutrino sampler and Module4 partial coherent dipoles, recording
original D14 empirical selection bias. Never certify global acceptance.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from module14.scan import evaluate_family as neutrino_family, digest
from module14.lfv import evaluate_family as partial_lfv_family
from research.full_constraints.scan_pilot_2026.vacuum_followup import strict_inputs

MEG_II=1.5e-13
SEED=20261110
FROZEN={
 (284,"NO",0):2.2441172252435806e-7,
 (284,"NO",1):1.8920605790466856e-7,
 (284,"IO",0):1.4424099333567958e-7,
 (284,"IO",1):5.977836994515708e-7,
 (112,"NO",0):1.1357990060807392e-5,
 (112,"NO",1):2.305135321139242e-5,
 (112,"IO",0):1.3430830008085421e-5,
 (112,"IO",1):1.1022233721377952e-5,
}


def evaluate_one(row,ordering,family):
    if ordering not in ("NO","IO") or type(family) is not int or family<0:
        raise ValueError("wrong deterministic family identity")
    raw={"id":row["id"],"scalar":row["scalar"],"scalar_sha256":row["scalar_sha256"]}
    n=neutrino_family(raw,SEED,ordering,family,math.sqrt(4*math.pi))
    out={"id":row["id"],"scalar_sha256":row["scalar_sha256"],
         "ordering":ordering,"family":family,
         "neutrino_status":n["status"],
         "neutrino_closure":n["closure_status"],
         "seed_sha256":n["seed_sha256"],
         "input_sha256":n.get("input_sha256"),
         "target_sha256":n.get("target_sha256"),
         "max_abs_yukawas":n.get("max_abs_yukawas"),
         "original_neutrino_input":n.get("input"),
         "global_acceptance":None,
         "physical_LFV":None,"full_Zee_LFV_complete":False}
    if n["status"]!="PASS" or n["closure_status"]!="PASS":
        out["LFV"]="NOT_EVALUATED"
        out["reason"]="Neutrino family failed perturbativity or closure"
        return out
    l=partial_lfv_family(n,False)
    if l["status"]!="PARTIAL" or l["complete_lfv"]:
        raise ValueError("Unexpected full Zee LFV promotion")
    channel=l["channels"]["mu_to_e_gamma"]
    br=channel["partial_BR"]
    if not math.isfinite(br) or br<0:raise ArithmeticError("Nonfinite or negative partial LFV")
    orig=FROZEN.get((row["id"],ordering,family))
    if orig is not None and not math.isclose(br,orig,rel_tol=1e-10,abs_tol=1e-22):
        raise ArithmeticError(f"Frozen 400-scan LFV mismatch for {row['id']} {ordering} {family}: {br} vs {orig}")
    ratio=br/MEG_II
    out.update(LFV="PARTIAL",
               partial_mu_to_e_gamma_BR=br,
               ratio_to_MEGII_bound=ratio,
               minimum_destructive_missing_amplitude_fraction=max(0.,1-math.sqrt(MEG_II/br)) if br else 0.,
               retained_dipoles={"C_L":channel["C_L"],"C_R":channel["C_R"]},
               source_lfv_input_sha256=l["module4_input_sha256"],
               source_lfv_output_sha256=l["module4_output_sha256"],
               is_partial_sub_limit=br<MEG_II,
               physical_LFV="UNKNOWN")
    return out

def run(output:Path,n284:int=24,n112:int=8):
    if output.exists():raise FileExistsError("Refuse overwrite")
    if type(n284)!=int or type(n112)!=int or not(2<=n284<=160 and 2<=n112<=160):
        raise ValueError("bounded trial family counts invalid")
    points={r["id"]:r for r in strict_inputs()}
    results=[]
    for scalar_id,n in ((284,n284),(112,n112)):
        for ordering in ("NO","IO"):
            for family in range(n):
                out=evaluate_one(points[scalar_id],ordering,family)
                results.append(out)
                if family<2 or family%8==7:
                    print("NEUTRINO_LFV_FAMILY",scalar_id,ordering,family,
                          out["neutrino_status"],out["LFV"],
                          out.get("partial_mu_to_e_gamma_BR"),
                          "ratio",out.get("ratio_to_MEGII_bound"),flush=True)
    summaries={}
    for pid in (284,112):
        rows=[r for r in results if r["id"]==pid]
        successful=[r for r in rows if r["LFV"]=="PARTIAL"]
        sbr=sorted(r["partial_mu_to_e_gamma_BR"] for r in successful)
        best=sorted(successful,key=lambda r:r["partial_mu_to_e_gamma_BR"])[:8]
        summaries[str(pid)]={
            "n_family_proposals":len(rows),
            "n_neutrino_closure_and_perturbativity_pass":len(successful),
            "n_neutrino_incomplete":len(rows)-len(successful),
            "n_partial_BRs_below_MEGII":sum(r["is_partial_sub_limit"] for r in successful),
            "minimum_partial_BR":sbr[0] if sbr else None,
            "median_partial_BR":sbr[len(sbr)//2] if sbr else None,
            "maximum_partial_BR":sbr[-1] if sbr else None,
            "minimum_partial_to_MEGII_ratio":sbr[0]/MEG_II if sbr else None,
            "best_families":[{"ordering":r["ordering"],"family":r["family"],
                              "partial_BR":r["partial_mu_to_e_gamma_BR"],
                              "ratio_to_limit":r["ratio_to_MEGII_bound"],
                              "minimum_missing_cancellation_fraction":r["minimum_destructive_missing_amplitude_fraction"],
                              "input_sha256":r["input_sha256"]} for r in best]
        }
    summary={
        "schema":"zee-d14-reseeded-families-lfv-materiality-v1",
        "status":"FIXED_SCALAR_NEUTRINO_FAMILY_LFV_SAMPLING_COMPLETE",
        "source_sample":"400 original scalar proposals, no new scalar points",
        "sampling_mode":"UNCHANGED_d14-neutrino-v1_hash_seeded_nullcone_and_homogeneous",
        "seed":SEED,"n_original_scalar_points":2,
        "MEGII_limit_90CL":MEG_II,
        "stage":"MODULE2_NEUTRINO_EXACT_CLOSURE_PLUS_MODULE4_PARTIAL_LFV",
        "physics_note":"sub-limit partial rates do not imply physical PASS; above-limit partial rates can interfere with omitted amplitudes; every physical global acceptance UNKNOWN.",
        "summaries":summaries,"rows":results,"physical_LFV":"UNKNOWN",
        "physical_allowed_count":None,"global_acceptance":None}
    output.write_text(json.dumps(summary,sort_keys=True,indent=2,allow_nan=False)+"\n")
    for pid,x in summaries.items():
        print("LFV_FAMILY_SCAN_SUMMARY",pid,json.dumps({k:v for k,v in x.items() if k!="best_families"},sort_keys=True),flush=True)
    print("PHYSICAL_LFV UNKNOWN; NO_MODEL_POINT_ALLOWED_PROVEN",flush=True)
    return summary

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--n284",type=int,default=24)
    parser.add_argument("--n112",type=int,default=8)
    args=parser.parse_args()
    run(args.output,args.n284,args.n112)

if __name__=="__main__":
    main()
