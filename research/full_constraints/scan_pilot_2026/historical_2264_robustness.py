#!/usr/bin/env python3
"""Source-replayed Zee historical 2264 partial-LFV local-eta robustness.

Determines the two roots of the original partial mu->e gamma rate with
respect to eta along one fixed 8D direction of homogeneous Yukawas.
Other LFV channels recomputed but partial. Uses exact D14C original 20k
manifest scalar/neutrino inputs and provenance. No global acceptance.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from scipy.optimize import brentq

from module14.scan import neutrino_input,digest
from module2.interface import evaluate as neutrino_evaluate
from module14.lfv import evaluate_family
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points,SCANNER_SEED
from research.full_constraints.scan_pilot_2026.historical_eta_minimum import amplitudes,minimize_ray,LIMIT

EXPECTED_ETA=0.0003254613882564927
EXPECTED_BR=9.544105595286678e-14
EXPECTED_CASCADE=0.3675784859358721
PARENT_SIGMA_PB=0.0050014
PARENT_SIGMA_STAT_PB=0.0000088007

def run(output:Path):
    if output.exists():raise FileExistsError("No overwrite")
    source=next(p for p in source_points() if p["id"]==2264)
    original=next(f for f in source["families"] if f["ordering"]=="IO" and f["family"]==1)
    r=minimize_ray(source,original)
    best=r["best"]
    if not (math.isclose(best["eta"],EXPECTED_ETA,rel_tol=1e-8)
            and math.isclose(best["partial_mu_e_gamma_BR"],EXPECTED_BR,rel_tol=1e-10)
            and math.isclose(best["D4_cascade_product"],EXPECTED_CASCADE,rel_tol=1e-9)):
        raise ArithmeticError("Original prior run source result was not reproduced")
    eta=best["eta"]
    def rate(x):return amplitudes(source,original,x)["partial_mu_e_gamma_BR"]
    lower=brentq(lambda x:rate(x)-LIMIT,0,eta,xtol=2e-13,rtol=1e-12)
    upper=brentq(lambda x:rate(x)-LIMIT,eta,0.001,xtol=2e-13,rtol=1e-12)
    # Independent source-rate points just inside/outside each crossing.
    width=upper-lower
    check={
      "lower_outside":rate(lower-.05*width),
      "lower_inside":rate(lower+.05*width),
      "upper_inside":rate(upper-.05*width),
      "upper_outside":rate(upper+.05*width)}
    if not(check["lower_outside"]>LIMIT
           and check["lower_inside"]<LIMIT
           and check["upper_inside"]<LIMIT
           and check["upper_outside"]>LIMIT):
        raise ArithmeticError("Source rate contradicts local safe interval")
    # Recompute original Module4 diagnostic on the chosen source exact input.
    from copy import deepcopy
    row={"id":2264,"scalar":source["input_card"],"scalar_sha256":source["scalar_sha256"]}
    seed,spec,inp=neutrino_input(row,SCANNER_SEED,"IO",1)
    if seed!=original["seed_sha256"] or digest(inp)!=original["input_sha256"]:
        raise ValueError("Original 20k inverse-family input not source-matched")
    inp=deepcopy(inp)
    for part in ("real","imag"):
        inp["homogeneous_coefficients"][part]=[eta*x for x in inp["homogeneous_coefficients"][part]]
    nu=neutrino_evaluate(inp)
    family={k:nu[k] for k in ("F","D","Ye","Ye2","Mnu")}
    family.update(input=inp,input_sha256=digest(inp))
    all_lfv=evaluate_family(family,True)
    if all_lfv["status"]!="PARTIAL" or all_lfv["complete_lfv"]:
        raise ArithmeticError("Incorrect full LFV interpretation")
    results={k:{"partial_BR":v["partial_BR"],
                "upper_limit":v["comparison"]["limit"]["upper_limit"] if v["comparison"]["limit"] else None,
                "diagnostic_only":v["comparison"]["status"]=="DIAGNOSTIC_ONLY"}
             for k,v in all_lfv["channels"].items()}
    if not math.isclose(results["mu_to_e_gamma"]["partial_BR"],best["partial_mu_e_gamma_BR"],
                        rel_tol=1e-12,abs_tol=1e-24):
        raise ArithmeticError("Independent complex LFV replay failed")
    # Reuse published scalar-level 13 TeV LO 5FS sigma only as a distinctly
    # qualified quark-hard-process proxy: actual original LHA receipt binds
    # previous full lepton Yukawa family and is not revalidated for this one.
    # The 5FS gb hard amplitude is quark-only at fixed scalar mixing, but no
    # new point source run/uncertainty is performed.
    production_proxy=PARENT_SIGMA_PB*best["D4_cascade_product"]
    out={
      "schema":"zee-2264-historical-local-homogeneous-robustness-1",
      "status":"ORIGINAL_2264_PARTIAL_MU_E_LFV_LOCAL_RAY_INTERVAL_VALIDATED",
      "source_20k_seed":SCANNER_SEED,
      "original_scan_neutrino_input_sha256":original["input_sha256"],
      "new_neutrino_input_sha256":best["modified_neutrino_input_sha256"],
      "scalar_sha256":source["scalar_sha256"],
      "charged_scalar_masses_GeV":[source["physical"]["mH1"],source["physical"]["mH2"]],
      "tanbeta":source["tanbeta"],"gamma_rad":source["physical"]["gamma"],
      "neutrino_ordering":"IO","family":1,
      "eta_min":eta,
      "eta_below_retained_mu_e_gamma_limit_interval":[lower,upper],
      "interval_width":width,
      "selected_eta_vs_original_eta_sampling_scale":eta,
      "retained_mu_e_gamma_partial_BR":best["partial_mu_e_gamma_BR"],
      "MEGII_upper_limit":LIMIT,
      "retained_partial_BRs_other_radiative":results,
      "mu3e_neutral_tree_partial_BR":best["partial_mu3e_tree_BR"],
      "source_interval_verification":check,
      "original_scalar_vacuum_D10":"PASS",
      "original_nominal_B_class":"APPROX_COMPATIBLE",
      "original_physical_B":"UNKNOWN",
      "branching_H2_H1Z_tree":best["D4_BR_H2_H1Z"],
      "branching_H1_tb_tree":best["D4_BR_H1_tb"],
      "tree_cascade_product":best["D4_cascade_product"],
      "original_13TeV_LO_5FS_quark_sigma_pb":PARENT_SIGMA_PB,
      "original_13TeV_LO_5FS_sigma_integration_error_pb":PARENT_SIGMA_STAT_PB,
      "13TeV_LO_quark_process_assumed_invariant_under_pure_lepton_homogeneous_change":True,
      "13TeV_LO_cascade_proxy_pb_if_quark_rate_unchanged":production_proxy,
      "13TeV_LO_cascade_proxy_fb_if_quark_rate_unchanged":1000*production_proxy,
      "13TeV_LO_cascade_proxy_statistical_integration_error_pb":PARENT_SIGMA_STAT_PB*best["D4_cascade_product"],
      "original_production_artifact_full_yukawa_source_binding_revalidated":False,
      "new_MG5_generation_executed":False,
      "14TeV_cross_section_pb":None,
      "13TeV_no_detector_preselection_yield_at_3000fb_inv_if_unchanged":production_proxy*1000*3000,
      "missing":"Full Zee LFV/gauge 2loop, mu3e non-tree, mu-e conversion, B physical uncertainties, Higgs exclusion, production PDF/scale and acceptance.",
      "physics_global_acceptance":None,
      "physical_LFV":"UNKNOWN",
      "claim":"Only an 1D partial LFV interval in an eight-real-dimensional family space, not physical/global viability or scan acceptance."
    }
    output.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("ROBUST_2264_ETA",f'{eta:.12g}',"INTERVAL",f'[{lower:.12g},{upper:.12g}]',
          "WIDTH",f'{width:.12g}',"BR",f'{best["partial_mu_e_gamma_BR"]:.12g}',
          "13TEV_LO_CASCADE_IF_UNCHANGED_FB",f'{1000*production_proxy:.8g}',flush=True)
    for k,v in results.items():
        print("OTHER_RETAINED_RADIATIVE",k,f'{v["partial_BR"]:.11e}',
              "LIMIT",v["upper_limit"],flush=True)
    print("GLOBAL_ACCEPTANCE UNKNOWN / PHYSICAL_B UNKNOWN / PHYSICAL_LFV UNKNOWN",flush=True)
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args();run(a.output)
if __name__=="__main__":main()
