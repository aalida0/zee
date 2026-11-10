#!/usr/bin/env python3
"""LFV texture audit of historical 16 vacuum-certified / B-approx-compatible Zee scalars.

Reconstructs ORIGINAL D14C neutrino input bytes via historical correlated
scan seed 20261104, then tests neutrino-preserving homogeneous directions.
No scalar re-sampling. No physical B/LFV/Higgs acceptance claim.
"""
from __future__ import annotations
import argparse
from collections import Counter
import copy
import json
import math
from pathlib import Path

import numpy as np

from module2.interface import canonical_hash,decode,evaluate as neutrino_evaluate
from module14.decays import DecayCalculation
from module14.lfv import evaluate_family as partial_lfv
from module14.scan import digest,neutrino_input,perturbativity
from module14.conditional_scan.workflow import load

ROOT=Path(__file__).resolve().parents[3]
HIST=ROOT/"module14/conditional_scan/candidate_followup.json"
TABLE="CERTIFIED_VACUUM_APPROX_BSG_16"
SCANNER_SEED=20261104
ETA=(1.0,0.01,0.001,0.0001,0.0)
LIMIT=1.5e-13
ORIGINAL_DATASET_SHA="2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9"


def source_points():
    dat=load(HIST)
    if dat["dataset_sha256"]!=ORIGINAL_DATASET_SHA or dat.get("global_acceptance") is not None:
        raise ValueError("Historical 20k/225 frozen source identity changed")
    rows=dat["tables"][TABLE]
    if len(rows)!=16 or len({p["id"] for p in rows})!=16:
        raise ValueError("Source-certified/approx-B compatible original table not 16 unique scalars")
    for p in rows:
        if (p["gates"]["vacuum"]["assessment"]!="PASS"
                or p["bsg_nominal_classification"]!="APPROX_COMPATIBLE"
                or p["global_acceptance"] is not None or p["physical_bsgamma"]!="UNKNOWN"):
            raise ValueError("Historical scalar certification scope changed")
        if canonical_hash(p["input_card"])!=p["scalar_sha256"]:
            raise ValueError("Historical complete scalar card hash mismatch")
        if len(p["families"])!=4:
            raise ValueError("Expected 2 NO+2 IO original full neutrino inverses")
        pairs={(f["ordering"],f["family"]) for f in p["families"]}
        if pairs!={("NO",0),("NO",1),("IO",0),("IO",1)}:
            raise ValueError("Frozen original NO/IO family identities changed")
    return rows


def one_family(point,original,eta,decayer=None):
    if eta not in ETA:raise ValueError("Predeclared eta only")
    row={"id":point["id"],"scalar":point["input_card"],"scalar_sha256":point["scalar_sha256"]}
    seed,spec,input=neutrino_input(row,SCANNER_SEED,original["ordering"],original["family"])
    if seed!=original["seed_sha256"] or digest(input)!=original["input_sha256"]:
        raise ValueError("Original immutable D14C family seed or input changed")
    inp=copy.deepcopy(input)
    for part in ("real","imag"):
        inp["homogeneous_coefficients"][part]=[eta*c for c in inp["homogeneous_coefficients"][part]]
    result=neutrino_evaluate(inp)
    metrics=perturbativity(result)
    if result["inverse"]["family_relative_residual"]>=2e-9:
        raise ArithmeticError("Neutrino mass inversion broke under homogeneous reweight")
    family={k:result[k] for k in ("F","D","Ye","Ye2","Mnu")}
    family.update(input=inp,input_sha256=digest(inp))
    if eta==1.0:
        for key in ("F","D","Ye","Ye2"):
            if canonical_hash(result[key])!=original["yukawa_sha256"][key]:
                raise ValueError("Original D14C Yukawa execution not reproduced: "+key)
    data={
        "id":point["id"],"ordering":original["ordering"],"family":original["family"],
        "eta_homogeneous":eta,"scalar_sha256":point["scalar_sha256"],
        "seed_sha256":seed,
        "neutrino_input_sha256":digest(inp),
        "original_neutrino_input_sha256":original["input_sha256"],
        "neutrino_closure":result["inverse"]["family_relative_residual"],
        "yukawa_max":metrics["overall_max"],
        "vacuum_certificate":"PASS",
        "B_nominal_reference":"APPROX_COMPATIBLE",
        "physical_B":"UNKNOWN","physical_Higgs":"UNKNOWN",
        "physical_LFV":"UNKNOWN","global_acceptance":None,
        "H2_mass_GeV":point["physical"]["mH2"],
        "H1_mass_GeV":point["physical"]["mH1"],
        "original_cascade_BR":original["cascade_BR"],
        "source_original_production_status":original["production_status"],
    }
    if metrics["overall_max"]>=math.sqrt(4*math.pi):
        data.update(status="NONPERTURBATIVE",partial_mu_e_BR=None)
        return data
    l=partial_lfv(family,False)
    if l["status"]!="PARTIAL" or l["complete_lfv"]:
        raise ArithmeticError("Unexpected global LFV promotion")
    br=l["channels"]["mu_to_e_gamma"]["partial_BR"]
    data.update(status="NEUTRINO_PASS_LFV_PARTIAL",
                partial_mu_e_BR=br,partial_to_MEGII_ratio=br/LIMIT,
                partial_below_MEGII=(br<LIMIT),
                retained_dipole_CL=l["channels"]["mu_to_e_gamma"]["C_L"],
                retained_dipole_CR=l["channels"]["mu_to_e_gamma"]["C_R"],
                source_Module4_output_SHA256=l["module4_output_sha256"],
                F_max=metrics["max_abs"]["F"],D_max=metrics["max_abs"]["D"])
    if br < LIMIT:
        # Recalculate all D4 competing two-body widths after changing lepton
        # Yukawas. The old branching ratio is not copied onto a new family.
        if decayer is None:
            decayer=DecayCalculation(point["input_card"],family)
        widths=decayer.evaluate(family)
        if widths["status"]!="PASS":
            raise ArithmeticError("Missing revised D4 decay width")
        data.update(
           new_D4_tree_total_H2_GeV=widths["mothers"]["H2"]["total"]["total_width_GeV"],
           new_D4_tree_cascade_BR=widths["mothers"]["H2"]["br_H1_Z"],
           new_D4_tree_H1_tb_BR=widths["mothers"]["H1"]["br_tb"],
           new_D4_tree_cascade_product=widths["cascade_product"],
           revised_neutrino_input=inp,
           source_D4_widths_sha256=digest(widths["source_sha256"]))
    return data

def run(output:Path):
    if output.exists():raise FileExistsError("No overwriting historical outputs")
    points=source_points()
    out=[]
    for point in points:
        orig_production=point.get("production_status")
        for family in point["families"]:
            for eta in ETA:
                r=one_family(point,family,eta)
                out.append(r)
        successful=[r for r in out if r["id"]==point["id"] and r.get("partial_below_MEGII")]
        print("HISTORICAL_TEXTURE_SCALAR",point["id"],
              "M2",f'{point["physical"]["mH2"]:.3f}',
              "ORIGINAL_PROD",orig_production,
              "MU_E_PARTIAL_SUBLIMIT",len(successful),
              "BEST",f'{min((r["partial_mu_e_BR"] for r in successful),default=float("nan")):.10g}',flush=True)
    summary={}
    for eta in ETA:
        rows=[r for r in out if r["eta_homogeneous"]==eta]
        valid=[r for r in rows if r["status"]=="NEUTRINO_PASS_LFV_PARTIAL"]
        winners=[r for r in valid if r["partial_below_MEGII"]]
        summary[str(eta)]={
            "n_evaluated_family_scenarios":len(rows),
            "n_neutrino_perturbative_and_partial_LFV":len(valid),
            "n_partial_sub_limit":len(winners),
            "n_distinct_scalar_points_with_partial_sub_limit":len({r["id"] for r in winners}),
            "min_partial_BR":min((r["partial_mu_e_BR"] for r in valid),default=None),
            "min_partial_ratio_to_limit":min((r["partial_to_MEGII_ratio"] for r in valid),default=None),
            "ids_with_partial_sub_limit":sorted({r["id"] for r in winners}),
            "winners_with_existing_source_matched_13TeV_original_production_ids":
                sorted({r["id"] for r in winners if r["source_original_production_status"]=="SUPPLIED_DOCUMENTED"}),
        }
        print("HISTORICAL_TEXTURE_ETA_SUMMARY",eta,json.dumps(summary[str(eta)],sort_keys=True),flush=True)
    top=sorted((r for r in out if r.get("partial_below_MEGII")),
               key=lambda r:(-r["new_D4_tree_cascade_product"],r["partial_mu_e_BR"]))
    source_file=load(HIST)
    audit={
       "schema":"zee-historical16-certified-vacuum-approxB-LFV-homogeneous-textures-v1",
       "status":"HISTORICAL_16_CERTIFIED_VACUUM_PLUS_B_REFERENCE_SOURCE_REPLAY",
       "historical_original_dataset_sha256":ORIGINAL_DATASET_SHA,
       "historical_candidate_followup_sha256":__import__("hashlib").sha256(HIST.read_bytes()).hexdigest(),
       "original_scan_seed":SCANNER_SEED,
       "n_original_scalar_points":16,
       "n_original_family_seeds":64,
       "eta_values":ETA,
       "n_scenarios":len(out),
       "targeted_flavor_textures_not_volume_fraction":True,
       "source_note":"Original 225 point selection + historically validated vacuum certificates; conditional B is merely approximate; no new scalar proposal, no 14 TeV rate and no certified global acceptance.",
       "MEGII_90CL_limit":LIMIT,
       "summary_by_eta":summary,
       "candidate_partial_sub_limit_by_cascade_product":top,
       "all_family_scenarios":out,
       "physical_LFV":"UNKNOWN","physical_B":"UNKNOWN",
       "physical_Higgs":"UNKNOWN","global_acceptance":None}
    output.write_text(json.dumps(audit,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("HISTORICAL_TEXTURE_COMPLETE",len(out),"SUBLIMIT",len(top),
          "SCALAR_SUBLIMIT",len({r["id"] for r in top}),
          "GLOBALLY_ALLOWED NONE",flush=True)
    return audit

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args();run(args.output)
if __name__=="__main__":
    main()
