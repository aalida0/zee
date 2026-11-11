#!/usr/bin/env python3
"""Algebraic LFV texture construction in the native exact Zee inverse.

For each source-certified scalar and newly deterministic neutrino input,
solve the TWO complex linear constraints D[e,mu]=D[mu,e]=0 by complex
Moore-Penrose pseudoinverse in the four-complex-dimensional homogeneous
solution. No arbitrary ±5e-5 box; no dipole cancellation objective.
The remaining two complex kernel coordinates are left at minimum norm.

Checks actual Module2 target/perturbativity, full retained Module4 LFV,
D4 charged tree widths and h125 leading photon BR ratios. This is a
flavor-texture diagnostic, not physical all-operator acceptance.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
import numpy as np

from module14.scan import digest, neutrino_input, perturbativity
from module14.lfv import evaluate_family as partial_lfv
from module14.decays import DecayCalculation
from module2.interface import evaluate as evaluate_neutrino, decode, encode
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.higgs import diphoton, zgamma
from research.full_constraints.scan_pilot_2026.two_scalar_flavor_benchmark import (
    IDS,SEEDS,ORDERINGS,LIMIT
)

RANK_TOLERANCE=1e-9
CLOSURE_MAX=2e-9


def build(row,ordering,seed):
    if row["id"] not in IDS or row["gates"]["vacuum"]["assessment"]!="PASS":
        raise ValueError("Not one of the source-certified two scalar cards")
    source={"id":row["id"],"scalar":row["input_card"],
            "scalar_sha256":row["scalar_sha256"]}
    seedsha,spec,original=neutrino_input(source,seed,ordering,1)
    if seedsha!=digest(["d14-neutrino-v1",seed,row["id"],ordering,1]):
        raise ArithmeticError("New family seed mismatch")
    baseline=copy.deepcopy(original)
    baseline["homogeneous_coefficients"]={
        "real":[0.0]*4,"imag":[0.0]*4
    }
    nbase=evaluate_neutrino(baseline)
    D0=decode(nbase["inverse"]["D0"])
    H=decode(nbase["inverse"]["homogeneous"],(4,3,3))
    A=np.asarray([H[:,0,1],H[:,1,0]],dtype=complex)
    b=-np.asarray([D0[0,1],D0[1,0]],dtype=complex)
    if np.linalg.matrix_rank(A,tol=RANK_TOLERANCE)!=2:
        raise ArithmeticError("Direct two-complex-Yukawa constraint lacks rank")
    z,residuals,rank,singular=np.linalg.lstsq(A,b,rcond=None)
    err=np.linalg.norm(A@z-b)
    if err>1e-10*max(1.0,np.linalg.norm(b)):
        raise ArithmeticError("Exact analytic neutral LFV texture algebra failed")
    # Rank-2 complex map from four complex homogeneous coefficients leaves
    # exactly TWO complex null directions in the direct-Yukawa constraints.
    U,S,Vh=np.linalg.svd(A,full_matrices=True)
    null=Vh[2:].conj().T
    if np.linalg.norm(A@null)>1e-10*max(1.0,np.linalg.norm(A)):
        raise ArithmeticError("Nullspace construction failed")
    changed=copy.deepcopy(original)
    changed["homogeneous_coefficients"]=encode(np.asarray(z,dtype=complex))
    nout=evaluate_neutrino(changed)
    actualD=decode(nout["D"])
    direct=[abs(actualD[0,1]),abs(actualD[1,0])]
    if max(direct)>=1e-10:
        raise ArithmeticError("Actual source D direct entries not suppressed")
    closure=nout["inverse"]["family_relative_residual"]
    if closure>=CLOSURE_MAX:
        raise ArithmeticError("Exact neutrino target closure lost")
    perturb=perturbativity(nout)
    status="NEUTRINO_PERTURBATIVE" if perturb["overall_max"]<math.sqrt(4*math.pi) else "NONPERTURBATIVE"
    result={
        "id":row["id"],"ordering":ordering,"seed":seed,"family":1,
        "scalar_sha256":row["scalar_sha256"],
        "original_neutrino_seed_hash":seedsha,
        "original_input_sha256":digest(original),
        "original_input":original,
        "algebraic_texture_input":changed,
        "algebraic_texture_input_sha256":digest(changed),
        "homogeneous_coefficients_minimum_norm":changed["homogeneous_coefficients"],
        "max_homogeneous_coefficient_abs":float(np.max(np.abs(z))),
        "original_homogeneous_max_abs":float(np.max(np.abs(
            decode(original["homogeneous_coefficients"],(4,))))),
        "direct_D_e_mu":direct[0],"direct_D_mu_e":direct[1],
        "linear_constraint_singular_values":singular.tolist(),
        "linear_constraint_rank_complex":int(rank),
        "residual_complex_direct_D":float(err),
        "remaining_direct_Yukawa_nullity_complex":2,
        "neutrino_closure":closure,"max_abs_yukawa":perturb["overall_max"],
        "perturbativity_status":status,
        "physical_LFV":"UNKNOWN","physical_Higgs":"UNKNOWN",
        "physical_B":"UNKNOWN","global_acceptance":None,
    }
    if status!="NEUTRINO_PERTURBATIVE":
        result.update(partial_mu_to_e_gamma_BR=None,D4_cascade_product=None,
                      h125_gamma_ratios=None)
        return result
    fields={k:nout[k] for k in ("F","D","Ye","Ye2","Mnu")}
    fields.update(input=changed,input_sha256=digest(changed))
    lf=partial_lfv(fields,True)
    if lf["status"]!="PARTIAL" or lf["complete_lfv"]:
        raise ArithmeticError("Unexpected full LFV status promotion")
    widths=DecayCalculation(row["input_card"],fields).evaluate(fields)
    if widths["status"]!="PASS":
        raise ArithmeticError("D4 charged tree widths incomplete")
    p=row["input_card"]["physical"]
    hgg=diphoton.benchmark(p,{"yukawas":{"D":nout["D"]}})
    hzg=zgamma.amplitude(p["mh1"],hgg["kV"],hgg["kappas"],
                        [p["mH1"],p["mH2"]],
                        hgg["g_h_charged_GeV"],hgg["Z_current"],v=p["v"])
    smzg=zgamma.amplitude(p["mh1"],1,{f:1 for f in hgg["kappas"]},v=p["v"])
    production=row["families"][0]["production"]
    if production["energy_TeV"]!=13 or production.get("sigma_pb") is None:
        raise ArithmeticError("Original quark hard rate missing")
    br=float(lf["channels"]["mu_to_e_gamma"]["partial_BR"])
    result.update({
        "partial_mu_to_e_gamma_BR":br,
        "partial_mu_to_e_gamma_below_retained_limit":br<LIMIT,
        "other_partial_radiative_BR":{
            k:v["partial_BR"] for k,v in lf["channels"].items()
            if k!="mu_to_e_gamma"
        },
        "mu_to_3e_tree_partial_BR":lf["mu_to_3e"]["tree_subset_BR"],
        "D4_cascade_product":widths["cascade_product"],
        "D4_BR_H2_H1Z":widths["mothers"]["H2"]["br_H1_Z"],
        "D4_BR_H1_tb":widths["mothers"]["H1"]["br_tb"],
        "original_13TeV_LO_quark_sigma_pb":production["sigma_pb"],
        "13TeV_LO_quark_invariant_cascade_proxy_fb":1000*production["sigma_pb"]*widths["cascade_product"],
        "original_production_full_family_input_revalidated":False,
        "h125_gamma_ratios":{
            "gammagamma_to_SM":hgg["ratio_to_SM"],
            "Zgamma_to_SM":hzg["width_GeV"]/smzg["width_GeV"],
            "kappa_V":hgg["kV"],
            "total_Higgs_width":None,
        },
    })
    return result


def run(path):
    if path.exists():raise FileExistsError("No overwrites")
    mp={p["id"]:p for p in source_points()}
    out=[]
    for id in IDS:
        for ordering in ORDERINGS:
            for seed in SEEDS:
                r=build(mp[id],ordering,seed)
                out.append(r)
                print("ALGEBRAIC_LFV_TEXTURE",id,ordering,seed,
                      "YMAX",r["max_abs_yukawa"],
                      "MAX_C",r["max_homogeneous_coefficient_abs"],
                      "DIR_E_MU",r["direct_D_e_mu"],r["direct_D_mu_e"],
                      "BR_MU_E",r.get("partial_mu_to_e_gamma_BR"),
                      "SUB_LIMIT",r.get("partial_mu_to_e_gamma_below_retained_limit"),
                      "CASCADE",r.get("D4_cascade_product"),flush=True)
    stats={}
    for id in IDS:
        rows=[r for r in out if r["id"]==id]
        good=[r for r in rows if r["perturbativity_status"]=="NEUTRINO_PERTURBATIVE"]
        stats[str(id)]={
            "n_fresh_family_proposals":len(rows),
            "n_neutrino_perturbative":len(good),
            "n_partial_below_limit":sum(z["partial_mu_to_e_gamma_below_retained_limit"] for z in good),
            "min_partial_BR":min((z["partial_mu_to_e_gamma_BR"] for z in good),default=None),
            "max_direct_e_mu":max(z["direct_D_e_mu"] for z in rows),
            "max_direct_mu_e":max(z["direct_D_mu_e"] for z in rows),
            "max_abs_homogeneous_coefficient":max(z["max_homogeneous_coefficient_abs"] for z in rows),
            "min_tree_cascade_product":min((z["D4_cascade_product"] for z in good),default=None),
        }
        print("ALGEBRAIC_SCALAR_SUMMARY",id,json.dumps(stats[str(id)],sort_keys=True),flush=True)
    payload={
        "schema":"zee-historical-two-scalar-complex-pseudoinverse-zero-direct-e-mu-textures-v1",
        "status":"ALGEBRAIC_DIRECT_LFV_TEXTURE_CONSTRUCTION_NOT_FULL_LFV",
        "method":"Exact minimum-Euclidean-norm complex linear solution for D[e,mu]=D[mu,e]=0 in 4-complex dimensional homogeneous neutrino family; independent from 8D dipole optimizer",
        "same_frozen_scalar_ids":IDS,"same_seed_schedule":SEEDS,"orderings":ORDERINGS,
        "n_scenarios":len(out),
        "summary":stats,"scenarios":out,
        "physical_LFV":"UNKNOWN","physical_B":"UNKNOWN","physical_Higgs":"UNKNOWN",
        "global_acceptance":None,
        "volume_statistic":None,
        "caveat":"Tree direct neutral e-mu Yukawas suppressed; F†F, charged doublet and neutral loops remain and are explicitly reevaluated. Other mu3e and Type-II conversion Wilsons not computed. No physical exclusion claim.",
    }
    path.write_text(json.dumps(payload,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("ALGEBRAIC_TEXTURE_STUDY_DONE",len(out),"PHYSICAL_LFV UNKNOWN",flush=True)
    return payload


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    run(args.output)


if __name__=="__main__":
    main()
