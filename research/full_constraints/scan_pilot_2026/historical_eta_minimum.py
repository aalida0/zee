#!/usr/bin/env python3
"""Source-locked local LFV homogeneous-ray minimisation at old D14 scalar points.

NEVER a full Zee LFV acceptance. Iterate only positive/negative homogeneous
real eta while retaining exact scalar, F, 2x Majorana phase, neutrino target,
RGE convention, and full original D14 source identity. Re-evaluate actual
module4 complex LFV dipoles; naive rate interpolation is not physics output.

Use original all-family source SHA and per-Yukawa checks at eta=1 first.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from module14.scan import neutrino_input,perturbativity,digest
from module14.decays import DecayCalculation
from module14.lfv import evaluate_family as evaluate_lfv
from module2.interface import evaluate as evaluate_nu, decode,canonical_hash
from research.full_constraints.scan_pilot_2026.historical_certified_texture import (
    source_points, SCANNER_SEED, LIMIT
)

FOCUS=((2264,"IO",1),(15673,"NO",1),(14555,"IO",1),(8850,"IO",1))
EXPECTED={
 (2264,"IO",1):{0.0:2.3841238931139983e-13,1e-4:1.640521548094087e-13,.001:7.095757634809949e-13},
 (15673,"NO",1):{0.0:1.7880830770170269e-13,1e-4:1.8665724642547337e-13,.001:3.501209573552915e-13},
 (14555,"IO",1):{0.0:5.329585417356353e-13,1e-4:5.14525985000526e-13,.001:4.425774048814667e-13},
 (8850,"IO",1):{0.0:7.465282170131716e-13,1e-4:5.67395174290697e-13,.001:7.163969652783424e-13}
}

def amplitudes(point,original,eta,with_d4=False):
    if not(-.003<=eta<=.003 and math.isfinite(eta)):raise ValueError("eta outside predeclared local scan")
    row={"id":point["id"],"scalar":point["input_card"],"scalar_sha256":point["scalar_sha256"]}
    seed,spec,source=neutrino_input(row,SCANNER_SEED,original["ordering"],original["family"])
    if seed!=original["seed_sha256"] or digest(source)!=original["input_sha256"]:
        raise ValueError(f"Historical seed/input mismatch for {point['id']} {original['ordering']} {original['family']}: current seed={seed}, expected seed={original['seed_sha256']}, current input={digest(source)}, expected input={original['input_sha256']}")
    input=copy.deepcopy(source)
    for key in ("real","imag"):
        input["homogeneous_coefficients"][key]=[eta*v for v in input["homogeneous_coefficients"][key]]
    nu=evaluate_nu(input)
    if nu["inverse"]["family_relative_residual"]>=2e-9:
        raise ArithmeticError("Inverse neutrino target changed")
    metrics=perturbativity(nu)
    if metrics["overall_max"]>=math.sqrt(4*math.pi):
        raise ArithmeticError("Nonperturbative texture")
    if eta==1.:
        for key in ("F","D","Ye","Ye2"):
            if canonical_hash(nu[key])!=original["yukawa_sha256"][key]:
                raise ArithmeticError("Frozen original Yukawa does not match historical hash")
    family={k:nu[k] for k in ("F","D","Ye","Ye2","Mnu")}
    family.update(input=input,input_sha256=digest(input))
    l=evaluate_lfv(family,with_d4)
    if l["status"]!="PARTIAL" or l["complete_lfv"]:
        raise ArithmeticError("Unvalidated total LFV promotion")
    br=float(l["channels"]["mu_to_e_gamma"]["partial_BR"])
    if not math.isfinite(br) or br<0:raise ArithmeticError("Invalid partial dipole rate")
    row={
        "id":point["id"],"ordering":original["ordering"],"family":original["family"],"eta":eta,
        "partial_mu_e_gamma_BR":br,"ratio_to_limit":br/LIMIT,
        "partial_sub_limit":br<LIMIT,"physical_LFV":"UNKNOWN","global_acceptance":None,
        "scalar_sha256":point["scalar_sha256"],
        "original_neutrino_family_input_sha256":original["input_sha256"],
        "modified_neutrino_input_sha256":digest(input),
        "neutrino_target_sha256":digest(input["target_eV"]),
        "neutrino_relative_closure":nu["inverse"]["family_relative_residual"],
        "max_perturbative_Yukawa":metrics["overall_max"],
        "dipole_C_L":l["channels"]["mu_to_e_gamma"]["C_L"],
        "dipole_C_R":l["channels"]["mu_to_e_gamma"]["C_R"],
        "module4_source_output_sha256":l["module4_output_sha256"],
        "physical_B":"UNKNOWN","physical_Higgs":"UNKNOWN",
        "vacuum_sufficient_certificate":"PASS",
        "nominal_B_reference":"APPROX_COMPATIBLE",
        "source_13TeV_production_status":point["production_status"]
    }
    if with_d4:
        tree=l["mu_to_3e"]
        dec=DecayCalculation(point["input_card"],family).evaluate(family)
        if dec["status"]!="PASS":raise ArithmeticError("Missing full two-body charged decay table")
        row.update({
            "partial_mu3e_tree_BR":tree["tree_subset_BR"],
            "mu3e_tree_quadrature_change":tree["quadrature_relative_change"],
            "D4_H2_total_width_GeV":dec["mothers"]["H2"]["total"]["total_width_GeV"],
            "D4_H1_total_width_GeV":dec["mothers"]["H1"]["total"]["total_width_GeV"],
            "D4_BR_H2_H1Z":dec["mothers"]["H2"]["br_H1_Z"],
            "D4_BR_H1_tb":dec["mothers"]["H1"]["br_tb"],
            "D4_cascade_product":dec["cascade_product"],
            "scalar_quark_production_original_receipt_revalidated_for_reweighted_family":False,
            "same_point_13TeV_hard_process_rate_recomputed":False})
    return row

def minimize_ray(point,original):
    key=(point["id"],original["ordering"],original["family"])
    checks={}
    for eta,expect in EXPECTED[key].items():
        result=amplitudes(point,original,eta)
        if not math.isclose(result["partial_mu_e_gamma_BR"],expect,rel_tol=4e-10,abs_tol=1e-24):
            raise ArithmeticError(f"historical BR mismatch {key} eta={eta}")
        checks[str(eta)]=result["partial_mu_e_gamma_BR"]
    # Coarse scan catches non-convexity and finite branches.
    grid=np.linspace(-.003,.003,31)
    computed={}
    def calc(eta):
        k=float(eta)
        if k not in computed:computed[k]=amplitudes(point,original,k)["partial_mu_e_gamma_BR"]
        return computed[k]
    for eta in grid:calc(eta)
    # Start with the two lowest local intervals and the full interval.
    ordered=sorted((calc(x),i) for i,x in enumerate(grid))[:3]
    minima=[]
    for _,i in ordered:
        a=float(grid[max(0,i-1)]);b=float(grid[min(len(grid)-1,i+1)])
        res=minimize_scalar(lambda x:calc(x),bounds=(a,b),method="bounded",
                            options={"xatol":1e-12,"maxiter":120})
        if not res.success:raise ArithmeticError("One-dimensional minimization failed")
        minima.append((res.fun,float(res.x)))
    minimum=min([*minima,*((calc(x),float(x)) for x in grid)])
    eta=minimum[1]
    row=amplitudes(point,original,eta,with_d4=minimum[0]<LIMIT)
    if not math.isclose(row["partial_mu_e_gamma_BR"],minimum[0],rel_tol=1e-13,abs_tol=1e-26):
        raise ArithmeticError("Independent minimum replay failed")
    return {"original_identity":key,"baselines":checks,
            "grid_evaluations":len(grid),"num_source_evaluations":len(computed),
            "eta_minimum":eta,"best":row,
            "negative_endpoint_BR":calc(-.003),"positive_endpoint_BR":calc(.003),
            "physical_lfv":"UNKNOWN","globally_allowed":None}

def run(path:Path):
    if path.exists():raise FileExistsError("Refuse overwriting results")
    pointmap={p["id"]:p for p in source_points()}
    out=[]
    for key in FOCUS:
        p=pointmap[key[0]]
        original=next(f for f in p["families"] if (f["ordering"],f["family"])==key[1:])
        res=minimize_ray(p,original)
        out.append(res)
        v=res["best"]
        print("HISTORICAL_LOCAL_LFV_MIN",*key,
              "ETA",f'{v["eta"]:.12g}',
              "PARTIAL_BR",f'{v["partial_mu_e_gamma_BR"]:.12g}',
              "RATIO",f'{v["ratio_to_limit"]:.9g}',
              "SUBLIMIT",v["partial_sub_limit"],
              "TREE_CASCADE",v.get("D4_cascade_product"),
              "TREE_MU3E",v.get("partial_mu3e_tree_BR"),flush=True)
    summary={"schema":"zee-20k-historical-certified-4-case-source-locked-local-ray-lfv-minimization-v1",
        "status":"SOURCE_LOCKED_BOUNDED_ONE_RAY_MINIMA_NOT_GLOBAL_LFV",
        "scope":"Four original certified vacuum and approx B compatible scalar points, four frozen neutrino families, eta in [-0.003,0.003]; not full 8D free texture minimization.",
        "no_new_scalar_points":True,"source_seed":SCANNER_SEED,
        "source_20k_dataset_sha256":"2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9",
        "MEGII_limit_90CL":LIMIT,"cases":out,
        "n_partial_sublimit":sum(x["best"]["partial_sub_limit"] for x in out),
        "n_full_zee_accepted":None,"physical_LFV":"UNKNOWN","global_acceptance":None}
    path.write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return summary

def main():
    a=argparse.ArgumentParser();a.add_argument("--output",required=True,type=Path);v=a.parse_args()
    run(v.output)

if __name__=="__main__":main()
