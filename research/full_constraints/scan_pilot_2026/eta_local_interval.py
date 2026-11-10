#!/usr/bin/env python3
"""Local one-dimensional LFV-safe homogeneous-texture intervals at fixed Zee points.

Only an explicit ray c_k -> eta c_k through the 8-dimensional real
homogeneous coefficient space is analyzed. 'Below partial dipole limit'
does not imply full physical LFV acceptance, statistical model-space
weight or robustness under orthogonal texture perturbations.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
from pathlib import Path

from scipy.optimize import brentq
from module14.scan import neutrino_input,perturbativity,digest
from module14.lfv import evaluate_family as partial_lfv
from module2.interface import evaluate as neutrino_evaluate
from research.full_constraints.scan_pilot_2026.vacuum_followup import strict_inputs
from research.full_constraints.scan_pilot_2026.homogeneous_texture_lfv import MEG_II,SEED
from research.full_constraints.scan_pilot_2026.detailed_texture_benchmarks import CASES

SCAN_POSITIVE=(0.000125,0.00025,0.0005,0.00075,0.001,0.0015,0.002,0.003,0.005,0.01,0.02,0.04)

def partial_BR(scalar,ordering,family,eta):
    if not math.isfinite(eta) or abs(eta)>1:
        raise ValueError("finite eta in original homogeneous parameter ray required")
    seed,spec,input=neutrino_input({
        "id":scalar["id"],"scalar":scalar["scalar"],"scalar_sha256":scalar["scalar_sha256"]
    },SEED,ordering,family)
    input=copy.deepcopy(input)
    for z in ("real","imag"):
        input["homogeneous_coefficients"][z]=[eta*a for a in input["homogeneous_coefficients"][z]]
    nu=neutrino_evaluate(input)
    metrics=perturbativity(nu)
    if metrics["overall_max"]>=math.sqrt(4*math.pi):
        raise ArithmeticError("Nonperturbative Yukawa on ray")
    if nu["inverse"]["family_relative_residual"]>2e-9:
        raise ArithmeticError("Neutrino closure broken")
    fields={k:nu[k] for k in ("F","D","Ye","Ye2","Mnu")}
    fields.update(input=input,input_sha256=digest(input))
    l=partial_lfv(fields,False)
    if l["status"]!="PARTIAL" or l["complete_lfv"]:
        raise ArithmeticError("Unexpected LFV full-physics promotion")
    br=l["channels"]["mu_to_e_gamma"]["partial_BR"]
    if not math.isfinite(br) or br<0:
        raise ArithmeticError("Nonfinite partial branching ratio")
    return float(br)

def interval(scalar,ordering,family):
    cache={}
    def val(eta):
        key=float(eta)
        if key not in cache:
            cache[key]=partial_BR(scalar,ordering,family,key)
        return cache[key]
    zero=val(0.)
    if zero>=MEG_II:
        raise ValueError("Selected source benchmark has no partial sub-limit eta=0")
    edges={}
    for sign,name in ((1.,"positive"),(-1.,"negative")):
        lo=0.
        upper=None
        for step in SCAN_POSITIVE:
            br=val(sign*step)
            if br>=MEG_II:
                upper=step
                break
            lo=step
        if upper is None:
            edges[name]={"status":"NO_CROSSING_WITHIN_PREDEFINED_GRID",
                         "last_eta":sign*lo,"last_rate":val(sign*lo)}
            continue
        root=brentq(lambda x:val(sign*x)-MEG_II,lo,upper,
                    xtol=1e-11,rtol=2e-12,maxiter=80)
        # The interval being reported is local along exactly one ray.
        # Verify the inner side and outer side with the actual source amplitude.
        inner=max(0.,root-5e-7)
        outer=root+5e-7
        if val(sign*inner)>MEG_II*(1+1e-6) or val(sign*outer)<MEG_II*(1-1e-6):
            raise ArithmeticError("Failed independent crossing-direction validation")
        edges[name]={"status":"LOCALLY_BRACKETED",
                     "eta_threshold":sign*root,
                     "br_at_root":val(sign*root),
                     "inner_eta":sign*inner,"inner_BR":val(sign*inner),
                     "outer_eta":sign*outer,"outer_BR":val(sign*outer)}
    return {"scalar_id":scalar["id"],"ordering":ordering,"family":family,
            "BR_partial_at_zero":zero,
            "MEGII_bound":MEG_II,"crossings":edges,
            "evaluations":len(cache),
            "vacuum_and_physical_B_unchanged_by_texture":True,
            "physical_LFV":"UNKNOWN",
            "global_acceptance":None,
            "interpretation":"Local 1D ray in 8-real-dimensional free homogeneous neutrino solution; not an 8D permitted-volume fraction or total LFV constraint."}

def run(output:Path):
    if output.exists():raise FileExistsError("No overwrites")
    scalars={r["id"]:r for r in strict_inputs()}
    results=[]
    for id,ordering,family,eta in CASES:
        x=interval(scalars[id],ordering,family)
        results.append(x)
        print("LOCAL_LFV_ETA_INTERVAL",id,ordering,family,
              "BR0",x["BR_partial_at_zero"],
              "NEG",x["crossings"]["negative"].get("eta_threshold"),
              "POS",x["crossings"]["positive"].get("eta_threshold"),
              "CALLS",x["evaluations"],flush=True)
    payload={"schema":"zee-d14-homogeneous-one-dimensional-partial-LFV-safe-interval-v1",
        "status":"LOCAL_SOURCE_MATCHED_PARTIAL_LFV_TEXTURE_RAY_CROSSINGS",
        "source":"Original scalar 400 manifest; unchanged neutrino null-cone/target; original Module2 and Module4",
        "cases":results,"physical_LFV":"UNKNOWN","global_acceptance":None}
    output.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return payload

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    run(args.output)

if __name__=="__main__":
    main()
