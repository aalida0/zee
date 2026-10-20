#!/usr/bin/env python3
"""One-shot postcampaign PHYSICS DIAGNOSTIC on ORIGINAL B4 potentials.

Reuses complete previously run 20,000-proposal campaign (no repeat B4).
For all 30 ORIGINAL B4 potentials, do a fresh Q4-source-pinned full
11-quartic running BFB + 55-channel tree unitarity audit and a 6-field
charge-breaking-inclusive numerical tree-vacuum search; re-run full
one-loop RGEs with all 22 D2 optimized f,Y solutions. Independently
recompute and compare D1 and D2 SAME-OBJECTIVE partial LFV scores.

No finite multistart search proves a global minimum. Q4 is one-loop,
no matched thresholds; D1/D2 LFV are incomplete, B to Xs gamma,
HiggsTools, complete physical widths and cross sections remain pending.
Therefore the only defensible labels are diagnostic/UNKNOWN.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import traceback

import numpy as np

BASE=Path(__file__).resolve().parents[1]
STATUS="POSTSCAN_ORIGINAL_B4_AND_OPTIMIZED_YUKAWA_AUDIT_NOT_ALLOWED"
BLOCKED="POSTSCAN_BLOCKED_NOT_ALLOWED"
MISSING={
 "full_neutrino_mass_global_likelihood":"NOT_VALIDATED",
 "complete_LFV_Barr_Zee_and_conversion":"NOT_VALIDATED",
 "matched_modern_two_charged_B_to_Xs_gamma_likelihood":"NOT_VALIDATED",
 "complete_Zee_HiggsTools_adapter":"NOT_IMPLEMENTED",
 "complete_widths_and_hadronic_production":"NOT_VALIDATED",
 "global_vacuum_proof":"NOT_ESTABLISHED",
 "threshold_matched_quark_yukawa_RGE":"NOT_ESTABLISHED",
}


def digest(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()


def read_json(p):
    return json.loads(Path(p).read_text())


def write_json(p,x):
    Path(p).write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+"\n")


def finite(v,label):
    x=float(v)
    if not math.isfinite(x):
        raise ValueError("Nonfinite "+label)
    return x


def compare_same_objective(d1_scores,d2_rows):
    """Never compare B2 one-loop-only with D2 joint fermion-BZ/tree score."""
    ids={z["candidate_id"] for z in d2_rows}
    if len(ids)!=len(d2_rows):
        raise ValueError("Duplicate D2 candidate ID")
    ans={}
    for row in d2_rows:
        name=row["candidate_id"]
        if name not in d1_scores:
            raise ValueError("D2 optimized candidate absent from D1")
        before=finite(row["original_D1_best_partial_score_NOT_EXCLUSION"],
                      "D2 recorded starting D1 objective")
        independent=finite(d1_scores[name],"D1 original joint objective")
        after=finite(row["new_best_partial_score_NOT_EXCLUSION"],
                     "D2 optimized joint objective")
        if before<=0 or independent<=0 or after<0:
            raise ValueError("Invalid positive partial LFV objectives")
        if not math.isclose(before,independent,rel_tol=2e-8,abs_tol=1e-12):
            raise ValueError("D1/D2 baseline objective mismatch for "+name)
        if after>before*(1+1e-8):
            raise ValueError("D2 worsened matched D1 objective at "+name)
        ans[name]={
           "same_objective_D1_start":before,
           "same_objective_D2_optimized":after,
           "D1_over_D2_partial_score_improvement_factor":
               before/max(after,1e-100),
           "both_scores_are_INCOMPLETE_LFV_NOT_a_likelihood":True,
        }
    return ans


def running_result(source,mod,state,mass,steps,orbits):
    from zee_gateC4_running_55channel_unitarity import full_trajectory
    coarse=full_trajectory(mod,state,mu0=mass,upper=10000.,
                           steps=steps,orbits=orbits)
    refined=full_trajectory(mod,state,mu0=mass,upper=10000.,
                            steps=2*steps,orbits=orbits)
    # Two resolutions MUST agree on boolean reachability, sampled
    # BFB sufficiency and tree unitarity to be considered numerically
    # controlled. A disagreement is INCONCLUSIVE, never a physical fail.
    keys=("reached_end_scale","BFB_sufficient_at_all_sampled_steps",
          "tree_unitarity_8pi_at_all_sampled_steps",
          "BFB_negative_witness")
    stable=all(bool(coarse[k])==bool(refined[k]) for k in keys)
    sufficient=(stable and coarse["reached_end_scale"] and
                coarse["BFB_sufficient_at_all_sampled_steps"] and
                coarse["tree_unitarity_8pi_at_all_sampled_steps"])
    return {
        "status":"NUMERICALLY_STABLE_DIAGNOSTIC" if stable
                 else "COARSE_REFINED_DISAGREEMENT_INCONCLUSIVE",
        "passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV":
            bool(sufficient),
        "negative_running_quartic_witness":
            bool(coarse["BFB_negative_witness"] or
                 refined["BFB_negative_witness"]),
        "coarse_path_status":coarse["status"],
        "refined_path_status":refined["status"],
        "coarse_reached_target":bool(coarse["reached_end_scale"]),
        "refined_reached_target":bool(refined["reached_end_scale"]),
        "first_uncertified_BFB_GeV":
            coarse["first_BFB_uncertified_scale_GeV"],
        "first_uncertified_tree_unitarity_GeV":
            coarse["first_tree_unitarity_uncertified_scale_GeV"],
        "largest_55channel_eigenvalue_coarse":
            finite(coarse["maximum_scattering_eigenvalue_encountered"],
                   "largest C4 eigenvalue"),
        "Q4_one_loop_no_threshold_matching":True,
    }


def verify_saved_campaign(root,rg_source,q4report):
    from zee_gateC1_joined_uv_pilot import verify_rge_validation
    from zee_gateD2_neutrino_exact_partial_LFV_optimization import verify_d1
    from zee_gateC2_paired_uv_rescue import load_cohort
    old=read_json(root/"campaign_result.json")
    manifest=read_json(root/"manifest.json")
    if (old.get("status")!=
        "LARGE_ZEE_EVIDENCE_CAMPAIGN_COMPLETED_NO_ALLOWED_POINT_CLASSIFICATION"
        or manifest.get("status")!=old["status"]):
        raise ValueError("Prior full campaign has no completed diagnostic status")
    if (manifest.get("cohort_size")!=30 or
        manifest.get("roots_per_spectrum")!=5 or
        old.get("number_scalar_candidates")!=30 or
        old.get("number_paired_running_and_vacuum_cases")!=60 or
        old.get("number_diagnostic_candidates_for_further_constraints")!=22):
        raise ValueError("Expected complete attached 2026-10-20 30/60/22 cohort")
    if (old.get("validated_Q4v13_source_sha256")!=digest(rg_source)
        or manifest.get("preflight",{}).get("q4_rge_sha256")!=digest(rg_source)):
        raise ValueError("PyR@TE full complex Zee RGE source SHA drift")
    verify_rge_validation(q4report,rg_source)
    selected=root/"B4_diverse_tree_consistent_30_NOT_ALLOWED.csv"
    if digest(selected)!=manifest["C2_variant_tree_preselection"]["selected_csv_sha256"]:
        raise ValueError("B4 selected physical-input table has changed")
    stage_files={
       "C2":root/"C2_paired_UV"/"summary.json",
       "C3":root/"C3_complex_BFB"/"summary.json",
       "C4":root/"C4_55channel_unitarity"/"summary.json",
       "C5":root/"C5_charge_breaking_vacuum"/"summary.json",
       "D1":root/"D1_joint_partial_LFV"/"summary.json",
       "D2":root/"D2_neutrino_partial_LFV_optimization"/"summary.json"}
    for name,path in stage_files.items():
        saved=manifest["stages"].get(name,{})
        if saved.get("status")!="VERIFIED_DIAGNOSTIC_NOT_EXCLUSION":
            raise ValueError("Previous "+name+" stage not certified completed")
        if saved.get("sha256")!=digest(path):
            raise ValueError("Previous "+name+" report source hash changed")
    b2=root/"partial_constraint_pipeline"/"B2_neutrino"/(
        "top_neutrino_Yukawa_matrices_NOT_ALLOWED.json")
    result=verify_d1(stage_files["D1"],selected,b2,
              stage_files["C2"],stage_files["C3"],
              stage_files["C4"],stage_files["C5"])
    d1,mapping=result
    d2=read_json(stage_files["D2"])
    if (d2.get("status")!=
        "GATE_D2_NEUTRINO_EXACT_PARTIAL_LFV_OPTIMIZATION_NOT_ALLOWED"
        or d2.get("tested_spectra")!=22 or len(d2.get("rows",[]))!=22):
        raise ValueError("D2 optimized 22-point cohort not complete")
    if any(d2.get("inputs_SHA256",{}).get(k)!=digest(path)
           for k,path in (
              ("B4",selected),("B2",b2),
              ("C2",stage_files["C2"]),("C3",stage_files["C3"]),
              ("C4",stage_files["C4"]),("C5",stage_files["C5"]),
              ("D1",stage_files["D1"]))):
        raise ValueError("D2 source provenance does not match original")
    points,solutions,_=load_cohort(selected,b2,30)
    if len(points)!=30 or any(len(v)!=5 for v in solutions.values()):
        raise ValueError("B4/B2 cohort length/root consistency failed")
    if set(points)!=set(d1["B2_saved_solution_count_per_candidate"]):
        raise ValueError("D1 does not cover all B4 scalar spectra")
    return {
        "points":points,"B2":solutions,"D1":d1,"D2":d2,
        "B4":selected,"B2_path":b2,
        "previous_manifest_SHA256":digest(root/"manifest.json"),
        "previous_result_SHA256":digest(root/"campaign_result.json")
    }


def audit(inp,mod,*,nstarts,steps,maxiter,orbits,seed):
    from zee_gateC1_joined_uv_pilot import build_model_state
    from zee_gateC5_charge_breaking_vacuum_search import (
        candidate_starts,evaluate_multistart)
    from gateB3_general_zee_charged_lepton_widths import complex_matrix
    from zee_gateD2_neutrino_exact_partial_LFV_optimization import (
        final_solution,optimize_kernels_cache)
    d1=inp["D1"]
    old_scores={}
    for item in d1["all_available_incomplete_LFV_details"]:
        name=item["candidate_id"]
        score=finite(item["joint_incomplete_LFV_score_NOT_EXCLUSION"],
                     "D1 matched objective")
        old_scores[name]=min(old_scores.get(name,math.inf),score)
    d2=inp["D2"]
    comparison=compare_same_objective(old_scores,d2["rows"])
    roots=d2["optimized_full_f_Y_and_partial_flavor_provenance"]
    if set(roots)!=set(comparison):
        raise ValueError("Optimized f/Y source solutions do not match D2 rows")
    optimize_kernels_cache()
    detailed=[]
    nstable=0
    n_joint=0
    improved=[]
    for index,name in enumerate(sorted(inp["points"]),1):
        point=inp["points"][name]
        first=inp["B2"][name][0]
        base_state,preflight=build_model_state(point,first)
        baseline=running_result("B2_rank1",mod,base_state,
                                float(point["mH2"]),steps,orbits)
        starts=candidate_starts(
            nstarts,seed+int.from_bytes(hashlib.sha256(
                ("original/"+name).encode()).digest()[:4],"big"))
        vac=evaluate_multistart(point,base_state,starts,maxiter=maxiter)
        witness=bool(vac["most_negative_witness"] is not None)
        if vac["successful_field_evaluations"]<1:
            raise ValueError("No original B4 vacuum search evaluations for "+name)
        optimized=None
        recomputed_joint=None
        if name in comparison:
            selected=roots[name]["chosen"]["solution"]
            if str(selected["candidate_id"])!=name:
                raise ValueError("D2 optimized f/Y candidate ID mismatch")
            ff=complex_matrix(selected["f"],"f")
            Y=complex_matrix(selected["Y"],"Y")
            _,recomputed,_=final_solution(point,selected,ff,Y)
            recomputed_joint=finite(
                recomputed["joint_incomplete_LFV_score_NOT_EXCLUSION"],
                "recomputed original B4 optimized LFV")
            if not math.isclose(
                recomputed_joint,
                comparison[name]["same_objective_D2_optimized"],
                rel_tol=2e-8,abs_tol=1e-12):
                raise ValueError("D2 original-source LFV recomputation disagrees at "+name)
            new_state,new_preflight=build_model_state(point,selected)
            optimized=running_result("optimized_fY",mod,new_state,
                                      float(point["mH2"]),steps,orbits)
            if new_preflight["neutrino_matrix_closure_eV"]>=1e-9:
                raise ValueError("Optimized solution neutrino closure failed")
            improved.append(comparison[name]["D1_over_D2_partial_score_improvement_factor"])
        baseline_use=(baseline[
            "passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV"]
            and not witness)
        opt_use=(bool(optimized and optimized[
            "passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV"])
            and not witness)
        nstable+=int(baseline_use)
        n_joint+=int(opt_use)
        record={
          "candidate_id":name,
          "mH1_GeV":finite(point["mH1"],"mass"),
          "mH2_GeV":finite(point["mH2"],"mass"),
          "gamma":finite(point["gamma"],"gamma"),
          "tanbeta":math.tan(finite(point["beta"],"beta")),
          "original_B4_rank1_RGE":baseline,
          "original_B4_tree_vacuum_status":vac["status"],
          "original_B4_tree_explicit_deeper_witness":witness,
          "original_B4_lowest_tree_potential_gap_over_v4":
              None if vac["lowest_point_found"] is None else vac[
                  "lowest_point_found"]["difference_from_EW_over_v4"],
          "original_B4_witness_kind":
              None if not witness else vac["most_negative_witness"]["kind"],
          "original_B4_witness_fields_over_v":
              None if not witness else vac["most_negative_witness"]["gauge_fixed_fields_over_v"],
          "original_B4_original_fY_diagnostic_candidate":bool(baseline_use),
          "same_objective_partial_LFV_comparison":
              comparison.get(name),
          "optimized_fY_current_RGE":optimized,
          "optimized_fY_recomputed_partial_LFV_score":
              recomputed_joint,
          "original_B4_optimized_fY_diagnostic_candidate":bool(opt_use),
          "globally_stable_tree_vacuum_proven":False,
          "full_model_allowed_or_excluded":None,
          "full_Zee_likelihood_validated":False,
        }
        detailed.append(record)
        print("POSTSCAN_ORIGINAL_B4",index,"/30",name,
              "base_RGE",baseline["passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV"],
              "deeper_witness",witness,
              "optimized_RGE",None if optimized is None else optimized[
                 "passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV"],
              "joint_diagnostic_survivor",opt_use,flush=True)
    summary={
        "status":STATUS,
        "original_B4_spectra_tested":len(detailed),
        "optimized_D2_spectra_RGE_retested":len(comparison),
        "original_B4_B2rank1_sampled_RGE_and_no_deeper_tree_witness":nstable,
        "original_B4_optimized_fY_sampled_RGE_and_no_deeper_tree_witness":n_joint,
        "original_B4_explicit_deeper_tree_witnesses":
            sum(z["original_B4_tree_explicit_deeper_witness"] for z in detailed),
        "D1_vs_D2_same_objective_comparison_count":len(improved),
        "D1_D2_same_objective_min_improvement_factor":
            min(improved) if improved else None,
        "D1_D2_same_objective_median_improvement_factor":
            float(np.median(improved)) if improved else None,
        "D1_D2_same_objective_max_improvement_factor":
            max(improved) if improved else None,
        "nonuniform_30_selected_spectra_NOT_parameter_space_coverage":True,
        "original_scalar_potential_not_counterfactual":True,
        "RGE_original_and_optimized_Yukawas_not_interchangeable":True,
        "finite_vacuum_search_not_global_minimum_proof":True,
        "full_experimental_Zee_allowed_points":None,
        "unresolved":MISSING,
        "details":detailed,
    }
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-dir",type=Path,required=True)
    ap.add_argument("--generator-output",type=Path,
        default=BASE/"work/zee_section8_Q4_pyrate_v4/generator_output")
    ap.add_argument("--q4v13-report",type=Path,
        default=BASE/"work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json")
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--uv-steps",type=int,default=24)
    ap.add_argument("--orbit-samples",type=int,default=2048)
    ap.add_argument("--vacuum-multistarts",type=int,default=128)
    ap.add_argument("--vacuum-maxiter",type=int,default=1000)
    ap.add_argument("--seed",type=int,default=20261020)
    args=ap.parse_args()
    if (args.uv_steps not in (24,48,72,96)
        or args.orbit_samples<256 or args.orbit_samples>32768
        or not 64<=args.vacuum_multistarts<=1024
        or not 200<=args.vacuum_maxiter<=6000):
        ap.error("Invalid source-controlled diagnostic numerical settings")
    if not BASE.resolve().is_relative_to(Path("/home")):
        ap.error("Only execute under /home source tree")
    output=args.output_dir.resolve()
    if (not output.is_relative_to(BASE.resolve()/"work")
        or (output.exists() and any(output.iterdir()))):
        ap.error("Use a new empty /home/aalida/zee/work/ output directory")
    output.mkdir(parents=True,exist_ok=True)
    report={"status":BLOCKED,"full_experimental_Zee_allowed_points":None}
    try:
        from zee_section8_Q4_generated_source_limit_probe import (
            find_rges,load_generated)
        from zee_gateC3_running_complex_bfb import orbit_design
        rg_src=find_rges(args.generator_output)
        pre=verify_saved_campaign(
            args.campaign_dir.resolve(),rg_src,
            args.q4v13_report.resolve())
        module=load_generated(rg_src)
        orbits=orbit_design(args.orbit_samples)
        report=audit(pre,module,nstarts=args.vacuum_multistarts,
                     steps=args.uv_steps,maxiter=args.vacuum_maxiter,
                     orbits=orbits,seed=args.seed)
        report["source"]= {
            "previous_campaign_manifest_sha256":pre["previous_manifest_SHA256"],
            "previous_campaign_result_sha256":pre["previous_result_SHA256"],
            "q4_676_validation_sha256":digest(args.q4v13_report),
            "pinned_complex_one_loop_RGE_sha256":digest(rg_src),
            "B4_original_selected_input_sha256":digest(pre["B4"]),
            "B2_Yukawa_solutions_sha256":digest(pre["B2_path"]),
            "vacuum_multistarts":args.vacuum_multistarts,
            "running_55_channel_steps":args.uv_steps,
            "running_refined_steps":2*args.uv_steps,
            "sampled_scalar_orbits":len(orbits)}
        columns=[
          "candidate_id","mH1_GeV","mH2_GeV","gamma","tanbeta",
          "original_B4_B2rank1_RGE_screen","original_B4_vacuum_witness",
          "D1_joint_partial_LFV","D2_joint_partial_LFV",
          "D1_over_D2_improvement_same_objective",
          "original_B4_optimized_fY_RGE_screen",
          "original_B4_original_fY_diagnostic_followup",
          "original_B4_optimized_fY_diagnostic_followup",
          "full_Zee_experimental_allowed"]
        flat=[]
        for item in report["details"]:
            comp=item["same_objective_partial_LFV_comparison"] or {}
            opt=item["optimized_fY_current_RGE"]
            flat.append({
                "candidate_id":item["candidate_id"],
                "mH1_GeV":item["mH1_GeV"],
                "mH2_GeV":item["mH2_GeV"],
                "gamma":item["gamma"],
                "tanbeta":item["tanbeta"],
                "original_B4_B2rank1_RGE_screen":item["original_B4_rank1_RGE"][
                    "passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV"],
                "original_B4_vacuum_witness":item[
                    "original_B4_tree_explicit_deeper_witness"],
                "D1_joint_partial_LFV":comp.get("same_objective_D1_start"),
                "D2_joint_partial_LFV":comp.get("same_objective_D2_optimized"),
                "D1_over_D2_improvement_same_objective":comp.get(
                    "D1_over_D2_partial_score_improvement_factor"),
                "original_B4_optimized_fY_RGE_screen":None if not opt else opt[
                    "passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV"],
                "original_B4_original_fY_diagnostic_followup":item[
                    "original_B4_original_fY_diagnostic_candidate"],
                "original_B4_optimized_fY_diagnostic_followup":item[
                    "original_B4_optimized_fY_diagnostic_candidate"],
                "full_Zee_experimental_allowed":None,
            })
        csv_path=output/"original_B4_30_and_optimized_fY_22_NOT_ALLOWED.csv"
        with csv_path.open("w",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=columns)
            writer.writeheader();writer.writerows(flat)
        report["results_csv"]=str(csv_path)
        report["results_csv_sha256"]=digest(csv_path)
        (output/"result.json").write_text(
            json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
        print("POSTSCAN_STATUS",STATUS)
        print("POSTSCAN_ORIGINAL_B4_WITH_NO_WITNESS_AND_RUNNING_SCREEN",
              report["original_B4_B2rank1_sampled_RGE_and_no_deeper_tree_witness"])
        print("POSTSCAN_OPTIMIZED_FY_WITH_NO_WITNESS_AND_RUNNING_SCREEN",
              report["original_B4_optimized_fY_sampled_RGE_and_no_deeper_tree_witness"])
        print("POSTSCAN_FULL_ALLOWED_POINTS UNKNOWN")
        print("POSTSCAN_RESULT",output/"result.json")
        return 0
    except Exception as exc:
        report={"status":BLOCKED,"error":repr(exc),
                "traceback":traceback.format_exc(),
                "full_experimental_Zee_allowed_points":None}
        (output/"result.json").write_text(
            json.dumps(report,sort_keys=True,indent=2)+"\n")
        print("POSTSCAN_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
