#!/usr/bin/env python3
"""Bounded eight-case Zee fresh-neutrino benchmark comparison.

Two historically certified scalar cards (15591/15673), two neutrino
orderings, two fresh inverse-family deterministic seeds. Reuse original
eight-real-parameter *partial* LFV optimizer; recompute native neutrino,
radiative partial LFV, D4 widths, and leading h125 photon loops for every
new flavor family. This is a conditional benchmark study, not a global
scalar scan or experimentally allowed point count.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from module14.scan import digest, neutrino_input, perturbativity
from module2.interface import evaluate as neutrino_evaluate
from research.full_constraints.scan_pilot_2026 import fresh_8d_lfv_pilot as opt
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.higgs import diphoton, zgamma

IDS=(15591,15673)
SEEDS=(20261111,20261112)
ORDERINGS=("NO","IO")
LIMIT=opt.MEGII_BOUND


def one(point, ordering, seed, max_nfev):
    assert point["id"] in IDS
    if point["gates"]["vacuum"]["assessment"]!="PASS" or point["bsg_nominal_classification"]!="APPROX_COMPATIBLE":
        raise ValueError("Original scalar identity not certified/conditionally compatible")
    raw={
        "id":point["id"],
        "scalar":point["input_card"],
        "scalar_sha256":point["scalar_sha256"],
    }
    seed_hash,spec,inp=neutrino_input(raw,seed,ordering,1)
    if seed_hash!=digest(["d14-neutrino-v1",seed,point["id"],ordering,1]):
        raise ArithmeticError("Independent deterministic family identity mismatch")
    (x,mini),optlogs,calls,scale=opt.optimize_family(inp,max_nfev)
    full=opt.evaluate(inp,x,with_d4=True)
    nu=neutrino_evaluate(full["input"])
    if digest(full["input"])!=full["input_sha256"] or nu["inverse"]["family_relative_residual"]>=2e-9:
        raise ArithmeticError("New original family and optimized inverse source changed")
    pp=point["input_card"]["physical"]
    photon=diphoton.benchmark(pp,{"yukawas":{"D":nu["D"]}})
    zg=zgamma.amplitude(pp["mh1"],photon["kV"],photon["kappas"],
                        [pp["mH1"],pp["mH2"]],
                        photon["g_h_charged_GeV"],photon["Z_current"],v=pp["v"])
    smz=zgamma.amplitude(pp["mh1"],1,
                         {f:1 for f in photon["kappas"]},v=pp["v"])
    if min(zg["width_GeV"],smz["width_GeV"],photon["full"]["width_GeV"])<=0:
        raise ArithmeticError("Nonphysical photon width")
    rates={f:point["families"][0]["production"] for f in ("original",)}
    p13=rates["original"]
    if p13.get("sigma_pb") is None or p13.get("energy_TeV")!=13:
        raise ValueError("Same scalar original 13TeV process receipt unavailable")
    production=float(p13["sigma_pb"])
    proxy_fb=production*1000*full["cascade_tree_BR_product"]
    b_pull=float(point["conditional_pull"])
    return {
        "scalar_id":point["id"],
        "original_scalar_sha256":point["scalar_sha256"],
        "vacuum_sufficient_certificate":"PASS",
        "original_nominal_B_reference_classification":point["bsg_nominal_classification"],
        "original_conditional_B_pull":b_pull,
        "original_physical_B":"UNKNOWN",
        "neutrino_ordering":ordering,
        "fresh_seed":seed,
        "fresh_family_id":1,
        "fresh_neutrino_seed_hash":seed_hash,
        "fresh_neutrino_spec":spec,
        "fresh_original_input":inp,
        "fresh_original_input_sha256":digest(inp),
        "fresh_optimized_input":full["input"],
        "fresh_optimized_input_sha256":full["input_sha256"],
        "optimized_eight_real_coefficients_in_1e_minus4":x.tolist(),
        "optimized_neutrino_closure":full["neutrino_relative_closure"],
        "max_abs_yukawa":full["max_abs_yukawa"],
        "partial_mu_to_e_gamma_BR":full["partial_BR"],
        "partial_sub_MEGII":full["partial_BR"]<LIMIT,
        "other_partial_radiative_BR":full["other_partial_radiative_BR"],
        "tree_mu_to_3e_BR":full["partial_mu3e_tree_BR"],
        "D4_BR_H2_H1Z":full["H2_to_H1Z_tree_BR"],
        "D4_BR_H1_tb":full["H1_to_tb_tree_BR"],
        "D4_tree_cascade_product":full["cascade_tree_BR_product"],
        "original_13TeV_LO_quark_sigma_pb":production,
        "13TeV_LO_cascade_proxy_fb_if_quark_sigma_unchanged":proxy_fb,
        "13TeV_physics_rate_original_revalidated_for_new_full_family":False,
        "H125_leading_gammagamma_ratio_to_SM":photon["ratio_to_SM"],
        "H125_leading_Zgamma_ratio_to_SM":zg["width_GeV"]/smz["width_GeV"],
        "H125_kappa_V":photon["kV"],
        "full_Higgs":"UNKNOWN",
        "physical_LFV":"UNKNOWN",
        "global_acceptance":None,
        "optimizer_log":optlogs,
        "optimizer_source_evaluations":calls,
        "scope":"Full new neutrino input frozen; D4 charged on-shell two-body; partial radiative LFV, leading h125 photon, original 13 TeV LO quark-only rate proxy; no global accepted signal",
    }


def run(output:Path,max_nfev=32):
    if output.exists():raise FileExistsError("Refuse to overwrite run evidence")
    if type(max_nfev)!=int or not 4<=max_nfev<=50:
        raise ValueError("Only bounded optimization allowed")
    source={p["id"]:p for p in source_points()}
    if not set(IDS)<=set(source):
        raise ValueError("Original D14 certified candidate missing")
    results=[]
    for id in IDS:
        point=source[id]
        for ordering in ORDERINGS:
            for seed in SEEDS:
                x=one(point,ordering,seed,max_nfev)
                results.append(x)
                print("CROSS_SCALAR_8D",id,ordering,seed,"PARTIAL_BR",x["partial_mu_to_e_gamma_BR"],
                      "CASCADE",x["D4_tree_cascade_product"],
                      "LO13_CASCADE_FB",x["13TeV_LO_cascade_proxy_fb_if_quark_sigma_unchanged"],
                      "H125_R_GAMMAGAMMA",x["H125_leading_gammagamma_ratio_to_SM"],
                      "H125_R_ZGAMMA",x["H125_leading_Zgamma_ratio_to_SM"],
                      "NEUTRINO_CLOSURE",x["optimized_neutrino_closure"],
                      "FULL_PHYSICS_UNKNOWN",flush=True)
    rows={}
    for id in IDS:
        sub=[x for x in results if x["scalar_id"]==id]
        rows[str(id)]={
            "n_new_family_scenarios":len(sub),
            "n_retained_mu_e_gamma_sub_limit":sum(x["partial_sub_MEGII"] for x in sub),
            "min_partial_mu_e_gamma_BR":min(x["partial_mu_to_e_gamma_BR"] for x in sub),
            "max_partial_mu_e_gamma_BR":max(x["partial_mu_to_e_gamma_BR"] for x in sub),
            "min_cascade_tree_BR_product":min(x["D4_tree_cascade_product"] for x in sub),
            "max_cascade_tree_BR_product":max(x["D4_tree_cascade_product"] for x in sub),
            "min_13TeV_proxy_fb":min(x["13TeV_LO_cascade_proxy_fb_if_quark_sigma_unchanged"] for x in sub),
            "max_13TeV_proxy_fb":max(x["13TeV_LO_cascade_proxy_fb_if_quark_sigma_unchanged"] for x in sub),
            "B_nominal_pull":sub[0]["original_conditional_B_pull"],
        }
        print("CROSS_SCALAR_SUMMARY",id,json.dumps(rows[str(id)],sort_keys=True),flush=True)
    out={
        "schema":"zee-historical-16-two-scalar-eight-fresh-flavor-benchmark-study-1",
        "status":"BOUNDED_TWO_SCALAR_FRESH_FAMILY_PARTIAL_LFV_AND_HIGGS_PILOT",
        "source_existing_20k_scalar_ids":IDS,
        "fresh_seed_schedule":SEEDS,
        "neutrino_orderings":ORDERINGS,
        "n_scenarios":len(results),
        "limit_mu_e_gamma_BR_snapshot":LIMIT,
        "source_sampling_note":"Two known certified scalar spectra, two new seeds per neutrino ordering; exact Module2 inverse and actual Module4 coherent partial dipole, reused D4 plus h125 leading photon. Not a random allowed-volume sample.",
        "scalar_summaries":rows,
        "scenarios":results,
        "full_Zee_LFV":False,"physical_B":"UNKNOWN","physical_Higgs":"UNKNOWN",
        "globally_allowed":None,
        "14TeV_cross_section":None,
        "no_new_MG5_or_detector_run":True,
    }
    output.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("NEW_SCALAR_FAMILY_STUDY_COMPLETE",len(results),"GLOBAL_ACCEPTANCE UNKNOWN",flush=True)
    return out


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True,type=Path)
    a.add_argument("--max-nfev",type=int,default=32)
    v=a.parse_args()
    run(v.output,v.max_nfev)


if __name__=="__main__":
    main()
