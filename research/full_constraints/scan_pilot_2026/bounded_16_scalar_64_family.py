#!/usr/bin/env python3
"""Small, explicitly constructed 16 x 2 x 2 Zee benchmark texture ensemble.

Fixed 16 original D14 scalar cards with source-certified D10 tree-vacuum
sufficient witness and nominal B->Xs gamma compatibility. Fresh complex
inverse neutrino cards are generated for NO/IO and two seeds and the two
direct e-mu neutral Yukawas are solved *algebraically* with the pseudoinverse.

Every actual resulting point is checked with Module2 full neutrino mass,
Module4 selected radiative LFV, D4 charged tree decay inventory, and native
h125 leading one-loop gamma/Zgamma. 2026 Misiak Eq.4 and independent
flavio v2.7.1 NP shifts are checked on each fixed SCALAR only.

No random scalar scan or detector run; no global acceptance. Missing 13
TeV production of 13/16 scalar points remains null (never zero). Results
are a deliberately constructed benchmark ensemble, not an allowed volume.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import flavio
from flavio.physics.running import running

from research.full_constraints.bsgamma_flavio_2026.published_eq4_triangulation import (
    assess_point, MATCHING_CARD
)
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.scan_pilot_2026.analytic_direct_lfv_textures import build

SEEDS=(20261111, 20261112)
ORDERINGS=("NO","IO")
BR_LIMIT=1.5e-13


def run(out:Path):
    if out.exists():raise FileExistsError("No overwrite of physics evidence")
    cards=sorted(source_points(),key=lambda p:p["id"])
    if len(cards)!=16 or len({p["id"] for p in cards})!=16:
        raise ArithmeticError("Original certified scalar source count changed")
    if flavio.__version__!="2.7.1":
        raise RuntimeError("flavio runtime not pinned")
    allowed_ids=tuple(p["id"] for p in cards)
    card=json.loads(MATCHING_CARD.read_text())
    par=flavio.default_parameters.get_central_all()
    a_s=float(running.get_alpha(par,160)["alpha_s"])
    flavio_sm=float(flavio.sm_prediction("BR(B->Xsgamma)"))
    if not 3e-4 < flavio_sm < 3.9e-4:raise ArithmeticError("SM reference missing")
    scalar=[]
    families=[]
    for p in cards:
        if (p["gates"]["vacuum"]["assessment"]!="PASS" or
            p["bsg_nominal_classification"]!="APPROX_COMPATIBLE"):
            raise ArithmeticError("Original scalar not 16-candidate certified")
        b=assess_point(p,card,flavio_sm,a_s)
        result={
            "scalar_id":p["id"],
            "scalar_sha256":p["scalar_sha256"],
            "scalar_input":p["input_card"],
            "tree_vacuum_D10_sufficient":"PASS",
            "published_2026_Eq4_B_pull":b["published_2026_Eq4_pull"],
            "published_Eq4_nominal_gaussian_inside":b["published_eq4_gaussian_interior"],
            "all_three_B_prescription_diagnostics_inside":b["all_three_diagnostic_prescriptions_gaussian_interior"],
            "2026_Eq4_B_pred":b["published_2026_Eq4_prediction"],
            "flavio_transferred_LO_B_pull_is_not_physical":b["heuristic_transferred_LO_pull"],
            "physical_B":"UNKNOWN",
            "global_acceptance":None,
        }
        scalar.append(result)
        print("BOUNDED_SCALAR_B",p["id"],
              "EQ4_PULL",result["published_2026_Eq4_B_pull"],
              "TRIPLE_INSIDE",result["all_three_B_prescription_diagnostics_inside"],
              flush=True)
        for ordering in ORDERINGS:
            for seed in SEEDS:
                f=build(p,ordering,seed,allowed_ids=allowed_ids)
                if f["linear_constraint_rank_complex"]!=2:
                    raise ArithmeticError("Neutrino inverse rank closure not met")
                if f["neutrino_closure"]>=2e-9:
                    raise ArithmeticError("Neutrino mass target closure lost")
                f["source_scalar_B_classification_2026_nominal"]=result["published_Eq4_nominal_gaussian_inside"]
                f["source_scalar_B_method_triage"]=result["all_three_B_prescription_diagnostics_inside"]
                f["published_2026_linear_B_pull"]=result["published_2026_Eq4_B_pull"]
                if f["perturbativity_status"]=="NEUTRINO_PERTURBATIVE":
                    if f["partial_mu_to_e_gamma_BR"] is None:
                        raise ArithmeticError("Missing actual partial radiative rate")
                else:
                    if f["partial_mu_to_e_gamma_BR"] is not None:
                        raise ArithmeticError("Nonperturbative family improperly evaluated")
                f["full_physical_B"]="UNKNOWN"
                f["full_physical_LFV"]="UNKNOWN"
                f["full_physical_Higgs"]="UNKNOWN"
                f["paper_global_acceptance"]=None
                families.append(f)
                print("BOUNDED_TEXTURE",p["id"],ordering,seed,
                      "YMAX",f["max_abs_yukawa"],
                      "CL",f["neutrino_closure"],
                      "PARTIAL_MUEG",f.get("partial_mu_to_e_gamma_BR"),
                      "CASCADE",f.get("D4_cascade_product"),
                      "PRODUCTION_FB",f.get("13TeV_LO_quark_invariant_cascade_proxy_fb"),
                      "GLOBAL_UNKNOWN",flush=True)
    by={}
    for p in scalar:
        sub=[r for r in families if r["id"]==p["scalar_id"]]
        val=[r for r in sub if r["perturbativity_status"]=="NEUTRINO_PERTURBATIVE"]
        good=[r for r in val if r["partial_mu_to_e_gamma_BR"]<BR_LIMIT]
        by[str(p["scalar_id"])]={
            "n_constructed":len(sub),
            "n_perturbative":len(val),
            "n_retained_mu_to_e_gamma_below_MEGl":len(good),
            "min_retained_mu_to_e_gamma":min((r["partial_mu_to_e_gamma_BR"] for r in val),default=None),
            "max_retained_mu_to_e_gamma":max((r["partial_mu_to_e_gamma_BR"] for r in val),default=None),
            "cascade_product_range":[
                min((r["D4_cascade_product"] for r in val),default=None),
                max((r["D4_cascade_product"] for r in val),default=None)
            ],
            "actual_13TeV_production_available":bool(
                val and val[0]["original_13TeV_LO_quark_sigma_pb"] is not None
            ),
            "2026_published_Eq4_pull":p["published_2026_Eq4_B_pull"],
            "flavio_prescription_crosscheck_interior":p["all_three_B_prescription_diagnostics_inside"],
            "globally_allowed_count":None,
        }
        print("SCALAR_ENSEMBLE_SUMMARY",p["scalar_id"],
              json.dumps(by[str(p["scalar_id"])],sort_keys=True),flush=True)
    result={
        "schema":"zee-16-scalar-64-purpose-constructed-neutrino-textures-sourced-2026-v1",
        "source_16_certified_original_scalar_IDs":allowed_ids,
        "new_neutrino_family_count":len(families),
        "source_B_arxiv":"2608.29863v1 Eq.4",
        "algebraic_flavor_solution":"complex two-row pseudoinverse in 4 complex homogeneous dimensions",
        "two_neutrino_orderings":ORDERINGS,
        "two_fresh_seeds":SEEDS,
        "experimental_referenced_mu_e_gamma_limit":BR_LIMIT,
        "n_source_B_Eq4_gaussian_inside":sum(p["published_Eq4_nominal_gaussian_inside"] for p in scalar),
        "n_scalar_B_diagnostic_method_stable":sum(p["all_three_B_prescription_diagnostics_inside"] for p in scalar),
        "n_perturbative_neutrino_families":sum(r["perturbativity_status"]=="NEUTRINO_PERTURBATIVE" for r in families),
        "n_retained_mu_e_gamma_below_limit":sum(
            r["perturbativity_status"]=="NEUTRINO_PERTURBATIVE"
            and r["partial_mu_to_e_gamma_BR"]<BR_LIMIT for r in families),
        "n_original_actual_13TeV_production_rates_available":sum(v["actual_13TeV_production_available"] for v in by.values()),
        "scalar_summaries":by,
        "scalars":scalar,"families":families,
        "selection_not_random_volume_sample":True,
        "physical_LFV":"UNKNOWN","physical_B":"UNKNOWN",
        "physical_Higgs":"UNKNOWN","global_acceptance":None,
        "full_scan_authorized":False,
        "strict_interpretation":"Construction exists at original fixed scalar spectra with retained LFV loop order and published leading B reference. No complete 3body/conversion, Higgs limits/widths, calibrated two-state B uncertainties, or model-wide exclusion is implied."
    }
    if len(families)!=64:
        raise ArithmeticError("Expected exactly 16*2*2 new neutrino families")
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("ENSEMBLE_DONE",len(scalar),"SCALARS",len(families),"FAMILIES",
          "PERTURBATIVE",result["n_perturbative_neutrino_families"],
          "RETAINED_BELOW",result["n_retained_mu_e_gamma_below_limit"],
          "PRODUCTION_RATES",result["n_original_actual_13TeV_production_rates_available"],
          "NO_GLOBAL_ACCEPTANCE",flush=True)
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    run(args.output)

if __name__=="__main__":
    main()
