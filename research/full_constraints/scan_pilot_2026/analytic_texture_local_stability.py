#!/usr/bin/env python3
"""Local sensitivity of algebraic Zee D_e_mu=D_mu_e=0 textures.

No statistical allowed volume, no full physical LFV pass. Perturb the
eight REAL homogeneous coefficients in Euclidean units, keeping F, scalar,
neutrino mass target and family seed unchanged, and re-evaluate *actual*
native Module2 and coherent partial Module4 mu->e gamma amplitudes.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path

import numpy as np

from module2.interface import evaluate as nu_evaluate,decode,encode
from module14.scan import digest,perturbativity
from module14.lfv import evaluate_family as lfv_evaluate
from research.full_constraints.scan_pilot_2026.analytic_direct_lfv_textures import build
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

BENCHMARKS=((15591,"NO",20261111),(15673,"IO",20261111))
RADII=(1e-7,1e-6,1e-5,1e-4)
LIMIT=1.5e-13


def rate(original, z):
    inp=copy.deepcopy(original)
    inp["homogeneous_coefficients"]=encode(np.asarray(z,dtype=complex))
    nu=nu_evaluate(inp)
    if nu["inverse"]["family_relative_residual"]>=2e-9:
        raise ArithmeticError("Neutrino target broken under deformation")
    vmax=perturbativity(nu)["overall_max"]
    if vmax>=math.sqrt(4*math.pi):
        return {"status":"NONPERTURBATIVE","partial_BR":None,
                "max_yukawa":vmax,"physical_LFV":"UNKNOWN","global_acceptance":None}
    obj={k:nu[k] for k in ("F","D","Ye","Ye2","Mnu")}
    obj.update(input=inp,input_sha256=digest(inp))
    l=lfv_evaluate(obj,False)
    if l["status"]!="PARTIAL" or l["complete_lfv"]:
        raise ArithmeticError("Physical LFV erroneously promoted")
    return {"status":"PARTIAL","partial_BR":l["channels"]["mu_to_e_gamma"]["partial_BR"],
            "max_yukawa":vmax,"direct_D_max":max(
                abs(decode(nu["D"])[0,1]),abs(decode(nu["D"])[1,0])),
            "physical_LFV":"UNKNOWN","global_acceptance":None}


def run(output):
    if output.exists():raise FileExistsError("No overwrite")
    points={p["id"]:p for p in source_points()}
    cases=[]
    for scalar_id,ordering,seed in BENCHMARKS:
        ref=build(points[scalar_id],ordering,seed)
        if ref["partial_mu_to_e_gamma_BR"] is None:
            raise ValueError("Baseline texture nonperturbative")
        seedz=decode(ref["algebraic_texture_input"]["homogeneous_coefficients"],(4,))
        baseline=rate(ref["algebraic_texture_input"],seedz)
        if not math.isclose(baseline["partial_BR"],ref["partial_mu_to_e_gamma_BR"],rel_tol=1e-10,abs_tol=1e-25):
            raise ArithmeticError("Algebraic baseline changed")
        rng=np.random.default_rng(15000+scalar_id)
        vals=[]
        for radius in RADII:
            # Signed axes + 24 reproducible isotropic directions in R^8.
            directions=list(np.eye(8))+list(-np.eye(8))
            directions.extend([v/np.linalg.norm(v) for v in rng.normal(size=(24,8))])
            trials=[]
            for d in directions:
                d=np.asarray(d,dtype=float)
                shift=radius*(d[:4]+1j*d[4:])
                val=rate(ref["algebraic_texture_input"],seedz+shift)
                trials.append(val)
            valid=[v for v in trials if v["status"]=="PARTIAL"]
            brs=sorted(v["partial_BR"] for v in valid)
            item={
                "radius_in_homogeneous_complex_coefficients":radius,
                "directions":"16 signed real axes + 24 reproducible isotropic directions",
                "n_trials":len(trials),"n_perturbative":len(valid),
                "n_retained_partial_below_limit":sum(v["partial_BR"]<LIMIT for v in valid),
                "min_partial_BR":min(brs,default=None),
                "median_partial_BR":float(np.median(brs)) if brs else None,
                "max_partial_BR":max(brs,default=None),
                "max_direct_D_e_mu_or_mu_e":max((v["direct_D_max"] for v in valid),default=None),
                "not_volume_fraction":True,
            }
            vals.append(item)
            print("ALGEBRAIC_LOCAL",scalar_id,ordering,seed,
                  "RADIUS",radius,"RETAINED_SUB",item["n_retained_partial_below_limit"],
                  "OF",item["n_trials"],"MAXBR",item["max_partial_BR"],flush=True)
        cases.append({
            "scalar_id":scalar_id,"ordering":ordering,"seed":seed,
            "original_scalar_sha256":ref["scalar_sha256"],
            "baseline_partial_BR":baseline["partial_BR"],
            "baseline_input_sha256":ref["algebraic_texture_input_sha256"],
            "baseline_direct_D_max":baseline["direct_D_max"],
            "baseline_homogeneous_coefficients":ref["algebraic_texture_input"]["homogeneous_coefficients"],
            "local_direction_tests":vals,
            "physical_LFV":"UNKNOWN","global_acceptance":None,
        })
    data={
        "schema":"zee-two-algebraic-LFV-8D-local-perturbation-robustness-v1",
        "status":"SOURCE_MATCHED_DIRECTIONAL_PARTIAL_LFV_STABILITY_NOT_GLOBAL",
        "cases":cases,"reference_limit_BR":LIMIT,
        "n_original_scalar_points":2,"n_perturbation_tests_per_scalar":40*len(RADII),
        "scope":"Two source-certified scalar spectra and two specific new family seeds. Source neutrino target and full scalar unchanged, only homogeneous coefficients perturbed.",
        "physical_LFV":"UNKNOWN","global_acceptance":None,
        "allowed_8d_volume":None,
    }
    output.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("ALGEBRAIC_LOCAL_STABILITY_COMPLETE",len(cases),
          "PHYSICAL_LFV UNKNOWN NO_VOLUME_CLAIM",flush=True)
    return data


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    run(args.output)


if __name__=="__main__":
    main()
