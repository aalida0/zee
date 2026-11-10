#!/usr/bin/env python3
"""Fixed Zee scalar + neutrino-target preserving homogeneous-texture deformation.

Original inverse neutrino solution: D = D0 + sum_k c_k H_k, with four
COMPLEX unconstrained homogeneous coefficients c_k. Vary common real
scale eta multiplying only c_k, re-evaluate independent Module2 inverse
and partial Module4 LFV. This is a deliberately non-volume-weighted
flavor-texture study, NOT a probability or full Zee LFV pass.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
from pathlib import Path
from collections import Counter

from module14.scan import neutrino_input,perturbativity,digest
from module14.lfv import evaluate_family as partial_lfv
from module2.interface import evaluate as neutrino_evaluate
from research.full_constraints.scan_pilot_2026.vacuum_followup import strict_inputs
from research.full_constraints.scan_pilot_2026.reseed_lfv_pilot import FROZEN,SEED,MEG_II

ETAS=(1.0,0.3,0.1,0.03,0.01,0.001,0.0)

def evaluate_texture(scalar,ordering,family,eta):
    if eta not in ETAS:raise ValueError("Not a predeclared texture scale")
    seed,spec,inp=neutrino_input({
         "id":scalar["id"],"scalar":scalar["scalar"],"scalar_sha256":scalar["scalar_sha256"]
    },SEED,ordering,family)
    inp=copy.deepcopy(inp)
    old=copy.deepcopy(inp["homogeneous_coefficients"])
    for chir in ("real","imag"):
        inp["homogeneous_coefficients"][chir]=[eta*a for a in old[chir]]
    output={"id":scalar["id"],"ordering":ordering,"family":family,
            "scalar_sha256":scalar["scalar_sha256"],
            "eta_homogeneous":eta,"seed_sha256":seed,
            "nu_input_sha256":digest(inp),
            "nu_input":inp,
            "physical_LFV":"UNKNOWN",
            "global_acceptance":None}
    try:
        n=neutrino_evaluate(inp)
        metrics=perturbativity(n)
        norm=float(metrics["overall_max"])
        if not math.isfinite(norm):raise ArithmeticError("nonfinite Yukawa")
        residual=n["inverse"]["family_relative_residual"]
        if residual>2e-9:raise ArithmeticError("broken neutrino closure")
        output.update(neutrino_closure=residual,
                      yukawa_max_abs=metrics["max_abs"],
                      perturbativity_max=norm)
        if norm>=math.sqrt(4*math.pi):
            output.update(status="NEUTRINO_NONPERTURBATIVE",
                          partial_lfv=None)
            return output
        family_data={k:n[k] for k in ("F","D","Ye","Ye2","Mnu")}
        family_data.update(input=inp,input_sha256=digest(inp))
        l=partial_lfv(family_data,False)
        if l["status"]!="PARTIAL" or l["complete_lfv"]:
            raise ArithmeticError("Partial LFV was unexpectedly promoted to full prediction")
        c=l["channels"]["mu_to_e_gamma"]
        br=float(c["partial_BR"])
        if not math.isfinite(br) or br<0:raise ArithmeticError("invalid LFV")
        if eta==1.0 and (scalar["id"],ordering,family) in FROZEN:
            expected=FROZEN[scalar["id"],ordering,family]
            if not math.isclose(br,expected,rel_tol=1e-10,abs_tol=1e-22):
                raise ArithmeticError("Original 400-pilot LFV not reproduced")
        output.update(status="NEUTRINO_PASS_LFV_PARTIAL",
                      partial_lfv={"mu_to_e_gamma_BR":br,
                                   "partial_to_MEGII_limit":br/MEG_II,
                                   "partial_below_limit":br<MEG_II,
                                   "dipole_CL":c["C_L"],
                                   "dipole_CR":c["C_R"],
                                   "other_partial_radiative_BR":{k:v["partial_BR"]
                                      for k,v in l["channels"].items() if k!="mu_to_e_gamma"},
                                   "missing_contributions":l["missing_contributions"],
                                   "complete_Zee_LFV":False},
                      source_module4_output_sha256=l["module4_output_sha256"])
    except Exception as exc:
        output.update(status="ERROR",error_type=type(exc).__name__,error=str(exc),
                      partial_lfv=None)
    return output

def run(output:Path,n284=24,n112=8):
    if output.exists():raise FileExistsError("No overwrite")
    if type(n284)!=int or type(n112)!=int or not(2<=n284<=80 and 2<=n112<=80):
        raise ValueError("bounded texture sample counts required")
    cards={r["id"]:r for r in strict_inputs()}
    results=[]
    for id,nfamilies in ((284,n284),(112,n112)):
        for ordering in ("NO","IO"):
            for family in range(nfamilies):
                for eta in ETAS:
                    row=evaluate_texture(cards[id],ordering,family,eta)
                    results.append(row)
                if family<2 or family%8==7:
                    subset=[r for r in results if r["id"]==id and r["ordering"]==ordering and r["family"]==family]
                    print("TEXTURE_TRAJECTORY",id,ordering,family,
                          " ".join(f'{r["eta_homogeneous"]}:{r["partial_lfv"]["mu_to_e_gamma_BR"]:.6g}'
                                   if r["partial_lfv"] is not None else
                                   f'{r["eta_homogeneous"]}:{r["status"]}' for r in subset),flush=True)
    summaries={}
    for id in (284,112):
        summaries[str(id)]={}
        for eta in ETAS:
            rows=[r for r in results if r["id"]==id and r["eta_homogeneous"]==eta]
            vals=sorted((r["partial_lfv"]["mu_to_e_gamma_BR"],r)
                        for r in rows if r["partial_lfv"] is not None)
            best=vals[0][1] if vals else None
            summaries[str(id)][str(eta)]={
              "families":len(rows),
              "neutrino_lfv_valid":len(vals),
              "numerical_errors":sum(r["status"]=="ERROR" for r in rows),
              "partial_mu_to_e_gamma_below_limit":sum(r["partial_lfv"]["partial_below_limit"] for r in rows if r["partial_lfv"] is not None),
              "min_partial_BR":vals[0][0] if vals else None,
              "median_partial_BR":vals[len(vals)//2][0] if vals else None,
              "max_partial_BR":vals[-1][0] if vals else None,
              "best_ordering_family":{"ordering":best["ordering"],"family":best["family"],
                    "input_sha256":best["nu_input_sha256"]} if best else None
            }
            print("TEXTURE_ETA_SUMMARY",id,eta,json.dumps(summaries[str(id)][str(eta)],sort_keys=True),flush=True)
    total={
       "schema":"zee-d14-texture-homogeneous-eta-v1",
       "status":"FIXED_SCALAR_HOMOGENEOUS_NEUTRINO_TEXTURE_DEFORMATION_PILOT",
       "sampling_note":"All etas use EXACT same F, neutrino target and original 400 scalar card per family; only arbitrary free 4-complex-dimensional homogeneous solution coefficients are scaled. This is an intentional texture bias, not a model-volume rate.",
       "eta_values":ETAS,"source_scan_seed":SEED,
       "source_400_manifest":"afa92f0e5d8afa56db976ff4158cc9971319419595574ef09be3f6d0d545ed45",
       "limit_MEGII":MEG_II,
       "summaries":summaries,"rows":results,
       "full_Zee_LFV":False,"physical_LFV":"UNKNOWN",
       "globally_allowed":None,"no_global_acceptance_claim":True}
    output.write_text(json.dumps(total,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("TEXTURE_STUDY_COMPLETE",len(results),"total scenarios","PHYSICAL_LFV UNKNOWN",flush=True)
    return total

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--n284",type=int,default=24)
    ap.add_argument("--n112",type=int,default=8)
    args=ap.parse_args()
    run(args.output,args.n284,args.n112)

if __name__=="__main__":
    main()
