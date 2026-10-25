#!/usr/bin/env python3
"""F19c source-matched six-dimensional Zee tree vacuum witness search.

Joins the exact three F18 full-MadWidth scalar points with F19 scalar/EWPO
and F19b exact F17f complex-neutrino/partial-LFV ledgers by SHA256.
Calls the existing analytic C5 full Zee scalar *dimensionful* potential
and six-real-field charge/CP-breaking minimizer, not the quartic-only
BFB surrogate. A deeper potential value is a negative witness; failure
to find one is NOT a global stability proof, especially at loop level.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
from zee_paper1_F19_integrated_scalar_EWPO_constraints import CASES,F19_STATUS,sha
from zee_paper1_F19b_exact_F17f_neutrino_partial_LFV import STATUS as F19B_STATUS
from zee_gateC1_joined_uv_pilot import scalar_lagrangian
from zee_gateC5_charge_breaking_vacuum_search import (
    candidate_starts,evaluate_multistart,WITNESS_MARGIN)

STATUS="F19C_EXACT_F18_F19B_TREE_CHARGE_BREAKING_VACUUM_WITNESS_SCREEN_NOT_GLOBAL"
def check_inputs(f18_file,f19_file,f19b_file):
    f18=json.loads(Path(f18_file).read_text())
    f19=json.loads(Path(f19_file).read_text())
    f19b=json.loads(Path(f19b_file).read_text())
    if (f18.get("status")!="F18_THREE_CASES_CONDOR_OR_LOCAL_MERGED_TREE_LO_NOT_ALLOWED"
        or not f18.get("three_original_benchmarks_LO_MadWidth_completed")
        or f18.get("physical_Zee_model_allowed_or_excluded") is not None):
        raise ValueError("F19c requires real original F18 tree source")
    if (f19.get("status")!=F19_STATUS or
        f19.get("F18_merged_JSON_SHA256")!=sha(Path(f18_file).read_bytes()) or
        f19.get("observational_allowance_or_exclusion") is not None):
        raise ValueError("F19c predecessor actual F19 scalar/EWPO source mismatch")
    if (f19b.get("status")!=F19B_STATUS or
        f19b.get("F19_real_scalar_EWPO_ledger_sha256")!=sha(Path(f19_file).read_bytes()) or
        f19b.get("F18_exact_merged_sha256")!=sha(Path(f18_file).read_bytes()) or
        f19b.get("FULL_MODEL_EXPERIMENTALLY_ALLOWED_OR_EXCLUDED") is not None):
        raise ValueError("F19c predecessor exact-complex F19b source mismatch")
    if (f19b.get("F16_F17f_source_bundle_sha256")!=f19.get(
        "F16_original_source_bundle_SHA256")):
        raise ValueError("F19b original F16/F17f source hash mismatch")
    by18={x["candidate_id"]:x for x in f18["benchmarks"]}
    by19={x["candidate_id"]:x for x in f19["benchmarks"]}
    by19b={x["candidate_id"]:x for x in f19b["results"]}
    for name,mapping in (("F18",by18),("F19",by19),("F19b",by19b)):
        if set(mapping)!=set(CASES) or len(mapping)!=3:
            raise ValueError("F19c original 3-case "+name+" cohort not exact")
    for name in CASES:
        if by19b[name].get("physical_Zee_allowed_or_excluded") is not None:
            raise ValueError("F19b prematurely labels full model allowed")
        if not math.isclose(
                float(by19b[name]["F18_actual_model_tree_cascade_BR"]),
                float(by18[name]["cascade_BR_product_model_LO_2plus3"]),
                rel_tol=1e-12,abs_tol=1e-13):
            raise ValueError("F18/F19b charged cascade physics mismatch "+name)
        gates=by19[name]["constraint_gates"]
        if (gates.get("Zee_tree_BFB_sufficient_not_necessary")!="SCREEN_PASS"
            or gates.get("Zee_scalar_2to2_tree_unitarity_8pi")!="SCREEN_PASS"):
            raise ValueError("F19c assumes BFB/uni screen passing origin "+name)
        err=float(by19b[name]["neutrino_source_fixed_NO_matrix_closure_max_abs_eV"])
        if not math.isfinite(err) or not 0<=err<1e-9:
            raise ValueError("F19c requires actually reconstructed neutrino masses")
    return by18,by19,by19b

def run(f18_file,f19_file,f19b_file,out_dir,*,multistart=128,maxiter=650,seed=20261024):
    f18_file=Path(f18_file).expanduser().resolve()
    f19_file=Path(f19_file).expanduser().resolve()
    f19b_file=Path(f19b_file).expanduser().resolve()
    out_dir=Path(out_dir).expanduser().resolve()
    if out_dir.exists():raise FileExistsError("F19c must not overwrite previous run")
    if not(64<=multistart<=1024 and 200<=maxiter<=6000 and
           0<=seed<=2**31-1):
        raise ValueError("C5 computational audit settings outside validated domain")
    by18,by19,by19b=check_inputs(f18_file,f19_file,f19b_file)
    rows=[]
    for i,name in enumerate(CASES,1):
        point=dict(by19[name]["scalar_original_F16_inputs"])
        point["id"]=name
        state,scalar_checks=scalar_lagrangian(point)
        if any(not math.isfinite(float(state[k])) for k in
               ("m1","m2","m12","mchi","muZee")):
            raise ValueError("Invalid exact dimensionful Zee state "+name)
        # C5 deterministic candidate search has a stable per-case seed
        # independent of arbitrary Python process hash randomization.
        offset=int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],"big")
        starts=candidate_starts(multistart,(seed+offset)%(2**32))
        result=evaluate_multistart(point,state,starts,maxiter=maxiter)
        if (not result["search_is_not_a_global_minimization_certificate"] or
            result["starts_requested"]!=multistart+2):
            raise ValueError("C5 finite numerical search completeness flag lost")
        deeper=result["most_negative_witness"]
        if (deeper is not None and not
            float(deeper["difference_from_EW_over_v4"]) < -WITNESS_MARGIN):
            raise ValueError("C5 deeper witness lacks independent value margin")
        row={
           "candidate_id":name,
           "BR_cascade_tree_MadWidth":float(
               by18[name]["cascade_BR_product_model_LO_2plus3"]),
           "original_neutrino_closure_eV":float(by19b[name][
               "neutrino_source_fixed_NO_matrix_closure_max_abs_eV"]),
           "tree_charge_breaking_vacuum_status":result["status"],
           "found_deeper_tree_potential_witness":bool(deeper is not None),
           "deepest_witness_type":None if deeper is None else deeper["kind"],
           "deepest_potential_gap_over_v4":None if deeper is None
             else deeper["difference_from_EW_over_v4"],
           "lowest_observed_V_minus_VEW_over_v4":None if
             result["lowest_point_found"] is None else
             result["lowest_point_found"]["difference_from_EW_over_v4"],
           "gauge_fixed_field_witness_over_v":None if deeper is None
             else deeper["gauge_fixed_fields_over_v"],
           "starts_requested":result["starts_requested"],
           "successful_field_evaluations":result["successful_field_evaluations"],
           "failed_optimizer_field_evaluations":result["optimizer_failures"],
           "artificial_bound_hits":result["boundary_hits"],
           "ew_stationarity_residual_over_v3":result["ew"][
               "stationarity_max_gradient_over_v3"],
           "ew_hessian_mass_spectrum_rel_err":result["ew"][
               "physical_plus_goldstone_spectrum_relmax"],
           "EW_tree_global_minimum_certified":False,
           "Zee_model_allowed_or_excluded":None,
           "dimensionful_Zee_potential":{k:float(state[k]) for k in
                ("m1","m2","m12","mchi","muZee")},
           "quartic_and_mass_source_checks":scalar_checks,
           "optimizer_diagnostics":result,
        }
        rows.append(row)
        print("F19C_CASE",i,"/",len(CASES),name,
              "TREE_WITNESS",bool(deeper),
              "TYPE",row["deepest_witness_type"],
              "DELTA_V_OVER_V4",row["lowest_observed_V_minus_VEW_over_v4"],
              "EW_MASS_HESSIAN_REL",row["ew_hessian_mass_spectrum_rel_err"],
              "STARTS",result["starts_requested"],
              "FULL_MODEL_ALLOWED","UNKNOWN",flush=True)
    report={
       "status":STATUS,
       "original_F18_SHA256":sha(f18_file.read_bytes()),
       "original_F19_SHA256":sha(f19_file.read_bytes()),
       "original_F19b_SHA256":sha(f19b_file.read_bytes()),
       "real_three_cases_source_matched":len(rows)==3,
       "C5_witness_threshold_in_VEV4_units":WITNESS_MARGIN,
       "boundedness_globally_proven":False,
       "absence_of_witness_proves_global_tree_vacuum":False,
       "loop_effective_potential_or_metastability_computed":False,
       "full_Zee_theory_and_experimental_allowed":None,
       "cases":rows,
    }
    out_dir.mkdir(parents=True,exist_ok=False)
    (out_dir/"F19c_three_vacuum_witnesses_NOT_GLOBAL.json").write_text(
        json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    with (out_dir/"F19c_three_vacuum_witness_summary.csv").open("w",newline="") as handle:
        cols=("candidate_id","BR_cascade_tree_MadWidth",
              "original_neutrino_closure_eV",
              "tree_charge_breaking_vacuum_status",
              "found_deeper_tree_potential_witness",
              "deepest_witness_type","deepest_potential_gap_over_v4",
              "lowest_observed_V_minus_VEW_over_v4",
              "starts_requested","successful_field_evaluations",
              "failed_optimizer_field_evaluations","artificial_bound_hits",
              "ew_stationarity_residual_over_v3",
              "ew_hessian_mass_spectrum_rel_err",
              "EW_tree_global_minimum_certified","Zee_model_allowed_or_excluded")
        writer=csv.DictWriter(handle,fieldnames=cols)
        writer.writeheader()
        writer.writerows({k:row.get(k) for k in cols} for row in rows)
    print("F19C_RESULT",STATUS,"COMPLETE",len(rows),"TREE_GLOBAL_PROOF",False)
    print("F19C_OUTPUT",out_dir)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--f18",type=Path,required=True)
    p.add_argument("--f19",type=Path,required=True)
    p.add_argument("--f19b",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--multistart",type=int,default=128)
    p.add_argument("--maxiter",type=int,default=650)
    p.add_argument("--seed",type=int,default=20261024)
    a=p.parse_args()
    run(a.f18,a.f19,a.f19b,a.output_dir,
        multistart=a.multistart,maxiter=a.maxiter,seed=a.seed)
if __name__=="__main__":main()
