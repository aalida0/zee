#!/usr/bin/env python3
"""Bounded local Zee scalar-viability neighborhood around *original* witnesses.

A continuity/materiality test, NOT an unbiased or exhaustive model scan.
The centers are original D10 tree-vacuum-certified scalar spectra. Vary
physical masses, charged mixing, tanbeta, alignment, cubic/quartic terms
in explicitly retained small ranges, apply the exact original scalar
reconstruction/BFB/unitarity/EWPO/D10-sufficient-vacuum gates, and use
the 2026 LO-NP B formula only if the input passes model validation.

Do not interpolate MG5 production to new scalar cards. Do not automatically
reuse the 64 neutrino textures on changed scalar cards or call them allowed.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
import random
from pathlib import Path

from module14.scan import scalar_gates,digest,scalar_status
from module14.conditional_scan.flavor import evaluate as flavor_diagnostic
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

ROOT=Path(__file__).resolve().parents[3]
CARD=ROOT/"module14/conditional_scan/matching_card.json"
CENTERS=(15673,15591,14074)
VARIATIONS_PER_CENTER=16

# Fractions w.r.t. the source physical input. CP-conserving potential is
# kept in exactly the previous parameterization. All variation variables
# are deterministic uniform proposal coordinates, NOT global model priors.
REL_MASS=0.01
REL_M12=0.02
REL_TANBETA=0.03
DELTA_GAMMA=0.025
DELTA_ALIGNMENT=0.012
REL_SCALAR_DIMENSIONLESS=0.02
ONE_SIDED_Z=1.6448536269514722


def perturbed_point(source,center_id,j):
    card=copy.deepcopy(source)
    if j==0:return card,{"variation_type":"exact_original_scalar_source"}
    rng=random.Random(int(digest(["zee-local-scalar-source-v1",center_id,j]),16))
    p=card["physical"]
    base=source["physical"]
    perturbations={}
    for name in ("mH1","mH2","mh2","ma"):
        fac=1+rng.uniform(-REL_MASS,REL_MASS)
        p[name]=base[name]*fac
        perturbations[name+"_fraction"]=fac-1
    factor=1+rng.uniform(-REL_TANBETA,REL_TANBETA)
    p["beta"]=math.atan(math.tan(base["beta"])*factor)
    perturbations["tanbeta_fraction"]=factor-1
    dgamma=rng.uniform(-DELTA_GAMMA,DELTA_GAMMA)
    p["gamma"]=base["gamma"]+dgamma
    perturbations["gamma_delta_rad"]=dgamma
    # The native h125 alignment is cos(alpha-beta), so vary that angle
    # independently of shifts to beta.
    ddelta=rng.uniform(-DELTA_ALIGNMENT,DELTA_ALIGNMENT)
    p["alpha"]=p["beta"]+(base["alpha"]-base["beta"])+ddelta
    perturbations["alpha_minus_beta_delta_rad"]=ddelta
    for name in ("m12sq",):
        fac=1+rng.uniform(-REL_M12,REL_M12)
        p[name]=base[name]*fac
        perturbations[name+"_fraction"]=fac-1
    for name in ("lc","k1","k2","k12"):
        d=rng.uniform(-REL_SCALAR_DIMENSIONLESS,REL_SCALAR_DIMENSIONLESS)
        # Perturb multiplicatively for nonzero components; 0 remains exact.
        p[name]=base[name]*(1+d)
        perturbations[name+"_fraction"]=d
    if not p["mH2"]>p["mH1"]+card["electroweak"]["mZ"]+20:
        raise ValueError("Local proposal closed charged Z cascade unexpectedly")
    return card,{"variation_type":"bounded_source_centered_uniform","deltas":perturbations}


def calculate(center,original,matching_card):
    outputs=[]
    for j in range(VARIATIONS_PER_CENTER+1):
        card,policy=perturbed_point(original,center,j)
        ident=f"local_{center}_{j:02d}"
        srcsha=digest(card)
        gates=scalar_gates({"id":ident,"scalar":card,"scalar_sha256":srcsha})
        status=scalar_status(gates)
        if status=="ERROR":
            # Keep errors as explicit reported failures. Do not continue
            # using a malformed scalar card.
            b=None
        elif gates["reconstruction"]["assessment"]=="PASS":
            try:
                b=flavor_diagnostic(card,matching_card)
            except ValueError:
                b=None
        else:
            b=None
        if b is not None and (b["status"]!="DIAGNOSTIC_ONLY" or b["bsg_physical_classification"]!="UNKNOWN"):
            raise ArithmeticError("Approximate B status promoted to physical pass")
        passed=b is not None and b["conditional_pull"]<=ONE_SIDED_Z and b["conditional_pull"]>=-ONE_SIDED_Z
        row={
            "center_scalar_id":center,"local_index":j,
            "is_original_exact_source":j==0,
            "source_scalar_sha256":srcsha,
            "physical":card["physical"],
            "perturbation":policy,
            "scalar_tree_status":status,
            "source_scalar_gate_status":{k:v["assessment"] for k,v in gates.items()},
            "source_2026_approximate_B_rate":b["BR_linear_2026"] if b is not None else None,
            "source_2026_approximate_B_pull":b["conditional_pull"] if b is not None else None,
            "B_one_sided_source_LO_NP_Gaussian_screen":passed if b is not None else None,
            "tree_and_B_screen_conditional":status=="PASS" and passed,
            "source_theoretical_gates_completed":True,
            "new_neutrino_flavor_recomputed":False,
            "H_A_H125_HiggsTools":None,
            "full_LFV":None,
            "MG5_13TeV_production_new_scalar":None,
            "MG5_14TeV_production_new_scalar":None,
            "physical_global_acceptance":None,
        }
        outputs.append(row)
        print("LOCAL_ZEE_SCALAR",center,j,"TREE",status,
              "B_PULL",row["source_2026_approximate_B_pull"],
              "B_SCREEN",row["B_one_sided_source_LO_NP_Gaussian_screen"],
              "GLOBAL_UNKNOWN",flush=True)
    if outputs[0]["scalar_tree_status"]!="PASS":
        raise ArithmeticError("Original D10 vacuum-certified scalar no longer passes gates")
    if not outputs[0]["tree_and_B_screen_conditional"] and center in (15673,14074):
        raise ArithmeticError("Original primary B-compatible source center lost one-sided screening")
    return outputs


def run(path):
    if path.exists():raise FileExistsError("Refuse overwrite of genuine neighborhood evidence")
    points={p["id"]:p for p in source_points()}
    if not set(CENTERS)<=set(points):
        raise ValueError("Original 16 source certification missing")
    bcard=json.loads(CARD.read_text())
    outputs=[]
    for center in CENTERS:
        row=points[center]
        if (row["gates"]["vacuum"]["assessment"]!="PASS"
            or row["scalar_sha256"]!=digest(row["input_card"])):
            raise ValueError("Original source witness changed")
        outputs.extend(calculate(center,row["input_card"],bcard))
    by={}
    for center in CENTERS:
        rows=[x for x in outputs if x["center_scalar_id"]==center]
        by[str(center)]={
            "n_nearby_proposals":len(rows),
            "tree_scalar_PASS":sum(x["scalar_tree_status"]=="PASS" for x in rows),
            "tree_scalar_UNKNOWN":sum(x["scalar_tree_status"]=="UNKNOWN" for x in rows),
            "tree_scalar_FAIL":sum(x["scalar_tree_status"]=="FAIL" for x in rows),
            "tree_scalar_ERROR":sum(x["scalar_tree_status"]=="ERROR" for x in rows),
            "tree_and_one_sided_B_screen":sum(x["tree_and_B_screen_conditional"] for x in rows),
            "neutrino_and_LFV_and_Higgs_experimental_coverage":"NOT_EVALUATED",
            "sampling_region":"Local ±1% masses, ±3% tanβ, ±0.025 gamma and ±0.012 alignment, centered on preselected certified points, not global parameter prior",
        }
        print("LOCAL_SCALAR_SUMMARY",center,json.dumps(by[str(center)],sort_keys=True),flush=True)
    data={
        "schema":"zee-source-certified-three-local-neighborhoods-16-perturbations-each-scalar-and-Bscreen-v1",
        "centers":CENTERS,"perturbations_per_center":VARIATIONS_PER_CENTER,
        "total_source_centered_points":len(outputs),
        "source_input_derived_from_original_certified_D10_cards":True,
        "full_neutrino_family_recomputed":False,
        "genuine_new_MG5_production":False,
        "statistical_distribution_is_not_global":True,
        "physical_Higgs_and_LFV":"UNKNOWN",
        "global_acceptance":None,
        "source_sums":by,"rows":outputs,
    }
    path.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("LOCAL_NEIGHBORHOOD_SCAN_DONE",len(outputs),"NOT_GLOBAL_ALLOWED",flush=True)
    return data


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    run(args.output)


if __name__=="__main__":
    main()
