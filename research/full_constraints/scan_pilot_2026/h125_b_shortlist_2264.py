#!/usr/bin/env python3
"""Fresh-source h125 photon widths and B gamma central diagnostic at Zee 2264.

Replays exactly the optimized full neutrino input. Uses already validated
native h->gamma gamma and h->Z gamma functions but does not run new external
LoopTools, HiggsTools, SusHi or a B physics likelihood. No total width/BR
or experimental exclusion claim.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import numpy as np

from module2.interface import evaluate as nu_evaluate, decode
from module14.scan import digest
from module3.core import vertices, neutral_width
from research.full_constraints.higgs import diphoton, zgamma
from research.full_constraints.higgs.sushi_bridge import lo_amplitude
from module14.conditional_scan.flavor import evaluate as b_evaluate
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

ROOT=Path(__file__).resolve().parents[3]
INPUT=Path(__file__).with_name("2264_fresh_8d_reference.json")
MATCHING=ROOT/"module14/conditional_scan/matching_card.json"


def evaluate():
    ref=json.loads(INPUT.read_text())
    inp=ref["optimized_input"]
    if digest(inp)!=ref["optimized_input_sha256"]:
        raise ValueError("Optimized full neutrino input SHA mismatch")
    point=next(row for row in source_points() if row["id"]==2264)
    if inp["scalar"]["sha256"]!=point["scalar_sha256"]:
        raise ValueError("Wrong certified scalar")
    p=inp["scalar"]["record"]["physical"]
    nout=nu_evaluate(inp)
    if nout["inverse"]["family_relative_residual"]>=2e-9:
        raise ArithmeticError("Neutrino closure changed")
    # D7/F13-tested native diphoton implementation, now applied to actual 2264.
    witness={"yukawas":{"D":nout["D"]}}
    hgg= diphoton.benchmark(p,witness)
    hzg= zgamma.amplitude(
        p["mh1"],hgg["kV"],hgg["kappas"],[p["mH1"],p["mH2"]],
        hgg["g_h_charged_GeV"],hgg["Z_current"],v=p["v"])
    smzg=zgamma.amplitude(p["mh1"],1,{f:1 for f in hgg["kappas"]},v=p["v"])
    ratiozg=hzg["width_GeV"]/smzg["width_GeV"]
    ratiogg=hgg["ratio_to_SM"]
    kv=hgg["kV"]
    ku=math.sin(p["alpha"])/math.sin(p["beta"])
    kd=math.cos(p["alpha"])/math.cos(p["beta"])
    if min(kv,ku,kd)<=0:
        raise ArithmeticError("Unexpected h125 sign branch")
    htree=vertices(decode(nout["D"]),p,np.asarray(inp["lepton_masses_GeV"]))["h"][0]
    ml=inp["lepton_masses_GeV"]
    extra_widths={}
    for i,j,label in ((0,1,"e_mu"),(0,2,"e_tau"),(1,2,"mu_tau")):
        extra_widths[label]=2*neutral_width(htree,p["mh1"],i,j,ml)
    card=json.loads(MATCHING.read_text())
    b=b_evaluate(inp["scalar"]["record"],card)
    if b["status"]!="DIAGNOSTIC_ONLY" or b["bsg_exclusion"] is not None:
        raise ArithmeticError("B flavor diagnostic improperly interpreted")
    if b["bsg_nominal_classification"]!=point["bsg_nominal_classification"]:
        raise ArithmeticError("Original B-physics class was not reproduced")
    # Conditional pull uses 2026 experimental 3.49 +/- 0.19 (1e-4 units)
    # and SM 0.14 (1e-4 units), independent, with no NP uncertainty.
    threshold=b["reference_comparison"]["absolute_pull_threshold"]
    sig=math.hypot(0.14,0.19)
    margin=threshold-abs(b["conditional_pull"])
    # No physical likelihood, and no rigorous NP sigma.
    out={
        "schema":"zee-2264-new-family-h125-photon-and-B-central-diagnostic-v1",
        "source":"Original certified scalar and source-hashed fresh optimized 8D neutrino card",
        "optimized_input_sha256":ref["optimized_input_sha256"],
        "scalar_sha256":point["scalar_sha256"],
        "mass_h125_GeV":p["mh1"],
        "h125_coupling_ratios":{"kappa_V":kv,"kappa_u":ku,"kappa_d":kd,
                                 "kappa_diag_leptons":{
            s:{"real":float(z.real),"imag":float(z.imag)}
            for s,z in zip(("e","mu","tau"),
                           np.diag(htree)*p["v"]/np.asarray(ml))
        }},
        "h125_gammagamma":{
            "leading_one_loop_width_GeV":hgg["full"]["width_GeV"],
            "matched_SM_leading_one_loop_width_GeV":hgg["SM"]["width_GeV"],
            "ratio_to_SM":ratiogg,
            "without_physical_H1_H2_charged_scalar_ratio_to_SM":hgg["ratio_without_charged_to_SM"],
            "physical_charged_scalar_G_diagonals_GeV":[float(hgg["g_h_charged_GeV"][k,k]) for k in (0,1)],
            "scope":"leading one loop, no total Higgs width, not a measured mu",
        },
        "h125_Zgamma":{
            "leading_one_loop_width_GeV":hzg["width_GeV"],
            "matched_SM_leading_one_loop_width_GeV":smzg["width_GeV"],
            "ratio_to_SM":ratiozg,
            "scope":"leading one loop including full signed two-charge off-diagonal Z currents, no Higgs total width",
        },
        "h125_width_independent_ratios":{
            "VBF_gammagamma_over_VBF_WW":ratiogg/kv**2,
            "VBF_Zgamma_over_VBF_WW":ratiozg/kv**2,
            "total_h125_width_cancels":True,
        },
        "h125_tree_partial_LFV_widths_both_charge_GeV":extra_widths,
        "h125_total_width":None,
        "h125_observed_signal_strength":None,
        "higgs_direct_search_exclusion":None,
        "B_to_Xs_gamma":{
            "rate_linear_diagnostic":b["BR_linear_2026"],
            "delta_C7_LO":b["DeltaC7_LO"],
            "delta_C8_LO":b["DeltaC8_LO"],
            "conditional_pull":b["conditional_pull"],
            "approx_2026_sigma_times_1e4":sig,
            "distance_to_approx_1p96_pull_boundary_in_sigma":margin,
            "distance_to_approx_boundary_in_BR":margin*sig*1e-4,
            "approx_classification":b["bsg_nominal_classification"],
            "physical_classification":"UNKNOWN",
            "model_NP_uncertainty":None,
            "physical_exclusion":None,
            "scope":"Single top-only nominal linear response; not physical B gamma rate/covariance",
        },
        "production_13TeV_new_job_executed":False,
        "full_higgs":"UNKNOWN","physical_B":"UNKNOWN","global_acceptance":None,
    }
    return out


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    if args.output.exists():raise FileExistsError("No overwrite")
    z=evaluate()
    args.output.write_text(json.dumps(z,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("H125_2264_KAPPAS",z["h125_coupling_ratios"])
    for k in ("h125_gammagamma","h125_Zgamma"):
        print("H125_PHOTON",k,"RATIO_SM",z[k]["ratio_to_SM"],
              "WIDTH",z[k]["leading_one_loop_width_GeV"])
    print("H125_WIDTH_INDEPENDENT",z["h125_width_independent_ratios"])
    print("B_2264",z["B_to_Xs_gamma"])
    print("FULL_HIGGS UNKNOWN PHYSICAL_B UNKNOWN GLOBAL_ACCEPTANCE NONE",flush=True)

if __name__=="__main__":
    main()
