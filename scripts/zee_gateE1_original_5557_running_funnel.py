#!/usr/bin/env python3
"""One LARGE existing-cohort Zee scan: original-potential RGE first.

Read all source-validated 5,557 B4 coarse-binned scalar/EWPO points.
Check physical ORIGINAL scalar quartics against 55-channel matching-scale
unitarity; construct exact-neutrino-closure single representative B2 f,Y;
evaluate source-pinned one-loop complete scalar/quark/lepton running
BFB+55-channel unitarity to 10 TeV (24 steps); double-resolution rerun
(48 steps) for provisional passes; numerical 6-field tree-vacuum search
only for those provisional passes. Preserve all evidence and rank physical
ORIGINAL B4 points only, never C2 counterfactual variants.

This is a guided/biased exploratory funnel. In particular failure of the
one illustrative B2 Yukawa family, 10-TeV perturbativity screening,
finite tree-vacuum multistart, or incomplete LFV does NOT imply an
experimentally excluded Zee spectrum.
"""
from __future__ import annotations
import argparse
import collections
import csv
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import traceback
import numpy as np

BASE=Path(__file__).resolve().parents[1]
STATUS="E1_ORIGINAL_5557_RUNNING_FUNNEL_DIAGNOSTIC_NOT_ALLOWED"
BLOCKED="E1_ORIGINAL_RUNNING_FUNNEL_BLOCKED_NOT_ALLOWED"
DEFAULT_CAMPAIGN=BASE/"work/zee_large_integrated_20261020_v1"
DEFAULT_POSTSCAN=BASE/"work/zee_postscan_original_B4_20261020_v2/result.json"
DEFAULT_GENERATOR=BASE/"work/zee_section8_Q4_pyrate_v4/generator_output"
DEFAULT_Q4_REPORT=BASE/"work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json"
KEYS=("mH1","mH2","mh2","ma","alpha","beta","gamma",
      "m12sq","lc","k1","k2","k12")
EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED=(
 "complete_Zee_neutrino_likelihood_both_orderings",
 "complete_two_loop_CLFV_and_mu_e_conversion",
 "NLO_NNLO_two_charged_B_to_Xs_gamma_likelihood",
 "model_complete_HiggsTools_and_total_widths",
 "hadronic_H2_production_cross_section",
 "mathematically_global_vacuum_certificate",
 "fully_matched_Yukawa_quark_RGE_and_thresholds",
)


def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for batch in iter(lambda:stream.read(1<<20),b""):
            h.update(batch)
    return h.hexdigest()


def parse_rows(path):
    with Path(path).open(newline="") as stream:
        reader=csv.DictReader(stream)
        if not reader.fieldnames or not set(("id","candidate_status",
                                            *KEYS)).issubset(reader.fieldnames):
            raise ValueError("Missing full B4 scalar-proposal schema")
        rows=[]
        seen=set()
        for r in reader:
            tag=r["id"]
            if not tag or tag in seen:
                raise ValueError("Duplicate/empty original scalar B4 ID")
            seen.add(tag)
            if r["candidate_status"]!="SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED":
                raise ValueError("Old B4 candidate mislabeled as physical pass")
            row={"id":tag}
            for k in KEYS:
                z=float(r[k])
                if not math.isfinite(z):
                    raise ValueError("Nonfinite scalar parameter "+k)
                row[k]=z
            for k in ("production_weighted_nonleptonic_cascade_upper_proxy",
                      "chi2_Gfitter","max_unitarity"):
                val=float(r[k])
                if not math.isfinite(val):
                    raise ValueError("Nonfinite scalar screening record "+k)
                row[k]=val
            rows.append(row)
    if not rows:
        raise ValueError("Empty original B4 ensemble")
    return rows


def verify_prior(campaign, postscan, generator, q4):
    from zee_gateC1_joined_uv_pilot import verify_rge_validation
    from zee_section8_Q4_generated_source_limit_probe import find_rges
    m=json.loads((campaign/"manifest.json").read_text())
    prior=json.loads((campaign/"campaign_result.json").read_text())
    post=json.loads(postscan.read_text())
    B4=campaign/"B4_adaptive"/"all_screened_candidates_NOT_ALLOWED.csv"
    B4report=campaign/"B4_adaptive"/"summary.json"
    selected=campaign/"B4_diverse_tree_consistent_30_NOT_ALLOWED.csv"
    if (m.get("status")!=
        "LARGE_ZEE_EVIDENCE_CAMPAIGN_COMPLETED_NO_ALLOWED_POINT_CLASSIFICATION"
        or prior.get("status")!=m["status"]):
        raise ValueError("Incomplete/mismatched original B4 discovery campaign")
    if (m.get("stages",{}).get("B4",{}).get("sha256")!=digest(B4report)
        or digest(selected)!=m.get("C2_variant_tree_preselection",{}).get(
           "selected_csv_sha256")):
        raise ValueError("Original B4 discovery source provenance modified")
    if (post.get("status")!=
        "POSTSCAN_ORIGINAL_B4_AND_OPTIMIZED_YUKAWA_AUDIT_NOT_ALLOWED"
        or post.get("original_B4_spectra_tested")!=30
        or post.get("original_B4_optimized_fY_sampled_RGE_and_no_deeper_tree_witness")!=2
        or post.get("source",{}).get("B4_original_selected_input_sha256")!=digest(selected)):
        raise ValueError("Previous original-potential 30-spectrum postscan not complete")
    source=find_rges(generator)
    if (post.get("source",{}).get("pinned_complex_one_loop_RGE_sha256")!=digest(source)
        or prior.get("validated_Q4v13_source_sha256")!=digest(source)):
        raise ValueError("Q4 one-loop RGE source hash changed")
    verify_rge_validation(q4,source)
    rows=parse_rows(B4)
    original_count=json.loads(B4report.read_text())[
        "distinct_screened_parameter_bins"]
    if len(rows)!=original_count or original_count!=5557:
        raise ValueError("Unexpected B4 full saved coarse-bin population")
    post_anchors={r["candidate_id"]:r for r in post["details"]
                  if r["original_B4_original_fY_diagnostic_candidate"]}
    if set(post_anchors)!={"B4_0006862","B4_0006962"}:
        raise ValueError("Postscan original-potential anchor cohort changed")
    catalog={r["id"]:r for r in rows}
    for k,x in post_anchors.items():
        if k not in catalog or not math.isclose(
                catalog[k]["mH2"],x["mH2_GeV"],rel_tol=0,abs_tol=1e-8):
            raise ValueError("Old original B4 anchors missing/mismatched")
    return rows,source,{
        "discovery_manifest_sha256":digest(campaign/"manifest.json"),
        "full_B4_coarse_bins_sha256":digest(B4),
        "source_RGE_SHA256":digest(source),
        "Q4v13_validation_SHA256":digest(q4),
        "original_B4_v2_postscan_SHA256":digest(postscan),
        "previous_confirmed_10TeV_original_anchors":sorted(post_anchors),
        "num_original_scalar_EWPO_coarse_bins":len(rows),
    }


def rank_pool(rows, limit):
    """Rank completed *post-RGE* records, keyed by candidate_id.

    The original B4 input tables use 'id'; once the funnel builds its
    diagnostic records, the canonical identifier is 'candidate_id'.
    Never infer an alternate key here; malformed records fail closed.
    """
    if not 0 <= limit <= len(rows):
        raise ValueError("Invalid E1 shortlist limit")
    keys=[x["candidate_id"] for x in rows]
    if any(not isinstance(k,str) or not k for k in keys):
        raise ValueError("Empty E1 diagnostic candidate_id")
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate E1 post-RGE candidate_id")
    rows=sorted(rows,key=lambda z:(
        -z["cascade_upper_proxy"],
        z["maximum_unity_ratio_to_8pi_along_run"],
        z["candidate_id"]))
    chosen=[]
    visited=set()
    for item in rows:
        cell=(int(item["mH1_GeV"]//25),int(item["mH2_GeV"]//40),
              int(item["gamma"]/.12))
        if cell in visited:
            continue
        chosen.append(item)
        visited.add(cell)
        if len(chosen)>=limit:
            break
    return chosen


def run(candidates,source,nsteps,orbits,starts,maxiter,seed,
        output,max_followup):
    from zee_section8_Q4_generated_source_limit_probe import load_generated
    from zee_gateC1_joined_uv_pilot import scalar_lagrangian,build_model_state
    from zee_gateC3_running_complex_bfb import quartic_bfb
    from zee_gateC4_running_55channel_unitarity import (
        scattering_limit,full_trajectory)
    from zee_gateC5_charge_breaking_vacuum_search import (
        candidate_starts,evaluate_multistart)
    from gateA1b_hierarchical_no_seed import (
        target_neutrino_matrix,antisymmetric_f_with_null_condition)
    from gateB2_zee_neutrino_family_scan import solve_point

    module=load_generated(source)
    target,_=target_neutrino_matrix()
    f0,_=antisymmetric_f_with_null_condition(target)
    rng=np.random.default_rng(seed)
    ledger=output/"E1_all_5557_original_model_scalar_RGE_diagnostics.jsonl"
    stats=collections.Counter()
    candidates_strict=[]
    candidates_pending=[]
    with ledger.open("w") as target_file:
        for i,point in enumerate(candidates,1):
            id_=point["id"]
            row={
                "candidate_id":id_,
                "mH1_GeV":point["mH1"],
                "mH2_GeV":point["mH2"],
                "gamma":point["gamma"],
                "tanbeta":math.tan(point["beta"]),
                "cascade_upper_proxy":
                    point["production_weighted_nonleptonic_cascade_upper_proxy"],
                "EWPO_scalar_screen":"ALREADY_PASS_SOURCE_B4_NOT_GLOBAL_FIT",
                "matched_scale_full_55channel":None,
                "matched_scale_sufficient_BFB":None,
                "one_neutrino_texture_tested":False,
                "original_1loop_RGE_10TeV_screen":None,
                "global_vacuum_proven":False,
                "full_Zee_experimental_allowed_or_excluded":None,
            }
            quartic,preflight=scalar_lagrangian(point)
            s55=scattering_limit(quartic)
            row["matching_scattering_ratio_to_8pi"]=s55["ratio_to_8pi"]
            row["matched_scale_full_55channel"]=s55["passes_strict_8pi"]
            if not s55["passes_strict_8pi"]:
                row["diagnostic_status"]="FULL_55CHANNEL_MATCHING_UNITARITY_FAILURE"
                stats["matching_55channel_fail"]+=1
            else:
                bfb=quartic_bfb(quartic,orbits)
                row["matching_BFB_verdict"]=bfb["verdict"]
                row["matched_scale_sufficient_BFB"]=(
                    bfb["verdict"]=="BFB_SUFFICIENT_CERTIFIED")
                if bfb["verdict"]!="BFB_SUFFICIENT_CERTIFIED":
                    row["diagnostic_status"]="MATCHING_BFB_UNCERTIFIED_OR_NEGATIVE_WITNESS"
                    stats["matching_BFB_not_sufficient"]+=1
                else:
                    # Generate a deterministic EXACT-neutrino solution for
                    # this scalar source point. It is only one family: no
                    # failure can be interpreted as full model exclusion.
                    try:
                        solution=solve_point(point,target,f0,rng,0.)
                    except (ValueError,ArithmeticError,
                            np.linalg.LinAlgError) as exc:
                        solution=None
                        row["B2_single_texture_error_type"]=type(exc).__name__
                    if solution is None:
                        row["diagnostic_status"]="SINGLE_B2_TEXTURE_UNAVAILABLE_NOT_EXCLUSION"
                        stats["neutrino_texture_unavailable"]+=1
                    else:
                        row["one_neutrino_texture_tested"]=True
                        row["single_B2_partial_LFV_score_NOT_EXCLUSION"]=float(
                            solution["partial_LFV_score_NOT_EXCLUSION"])
                        state,model_checks=build_model_state(point,solution)
                        coarse=full_trajectory(
                            module,state,mu0=point["mH2"],upper=10000.,
                            steps=nsteps,orbits=orbits)
                        row["coarse_1loop_full_source_RGE"]={
                            k:coarse[k] for k in (
                                "status","reached_end_scale",
                                "BFB_sufficient_at_all_sampled_steps",
                                "tree_unitarity_8pi_at_all_sampled_steps",
                                "first_BFB_uncertified_scale_GeV",
                                "first_tree_unitarity_uncertified_scale_GeV",
                                "maximum_scattering_eigenvalue_encountered")}
                        co_ok=bool(coarse["reached_end_scale"] and
                              coarse["BFB_sufficient_at_all_sampled_steps"] and
                              coarse["tree_unitarity_8pi_at_all_sampled_steps"])
                        stats["one_texture_RGE_evaluated"]+=1
                        if not co_ok:
                            row["diagnostic_status"]="ORIGINAL_RGE_COARSE_NOT_10TEV_CERTIFIED"
                            stats["RGE_coarse_not_pass"]+=1
                        else:
                            refined=full_trajectory(
                                module,state,mu0=point["mH2"],
                                upper=10000.,steps=2*nsteps,orbits=orbits)
                            keys=("reached_end_scale",
                                  "BFB_sufficient_at_all_sampled_steps",
                                  "tree_unitarity_8pi_at_all_sampled_steps",
                                  "BFB_negative_witness")
                            concordant=all(
                                bool(coarse[k])==bool(refined[k]) for k in keys)
                            row["RGE_two_resolutions_agree"]=bool(concordant)
                            row["refined_1loop_full_source_RGE"]={
                                k:refined[k] for k in (
                                    "status","reached_end_scale",
                                    "BFB_sufficient_at_all_sampled_steps",
                                    "tree_unitarity_8pi_at_all_sampled_steps",
                                    "first_BFB_uncertified_scale_GeV",
                                    "first_tree_unitarity_uncertified_scale_GeV",
                                    "maximum_scattering_eigenvalue_encountered")}
                            if (not concordant or
                                not refined["reached_end_scale"] or
                                not refined["BFB_sufficient_at_all_sampled_steps"] or
                                not refined["tree_unitarity_8pi_at_all_sampled_steps"]):
                                row["diagnostic_status"]="ORIGINAL_RGE_RESOLUTION_INCONCLUSIVE"
                                stats["RGE_refined_disagreement"]+=1
                            else:
                                row["original_1loop_RGE_10TeV_screen"]=True
                                row["maximum_unity_ratio_to_8pi_along_run"]=max(
                                    coarse["maximum_scattering_eigenvalue_encountered"],
                                    refined["maximum_scattering_eigenvalue_encountered"])/(8.*math.pi)
                                row["diagnostic_status"]="RGE_PASS_VACUUM_NOT_YET_TESTED"
                                row["_original_source_neutrino_solution"]=solution
                                candidates_pending.append(row)
                                stats["RGE_two_resolution_pass"]+=1
            # Compact JSONL ledger preserves every input result, WITHOUT
            # storing O(1000) heavy full step histories for each point.
            target_file.write(json.dumps({
                k:v for k,v in row.items()
                if not k.startswith("_")},allow_nan=False,sort_keys=True)+"\n")
            if i%250==0 or i==len(candidates):
                print("E1_PROGRESS",i,"/",len(candidates),
                      "RGE_PASS",stats["RGE_two_resolution_pass"],
                      "MATCHING_FAIL",stats["matching_55channel_fail"],
                      flush=True)
    # Vacuum work is done only on double-resolution confirmed RGE
    # candidates. NEVER mark an unevaluated point as vacuum acceptable.
    candidates_pending.sort(key=lambda z:-z["cascade_upper_proxy"])
    results=[]
    seen=set()
    for i,row in enumerate(candidates_pending[:max_followup],1):
        point=next(p for p in candidates if p["id"]==row["candidate_id"])
        state,_=build_model_state(point,row["_original_source_neutrino_solution"])
        starts=candidate_starts(starts.shape[0],seed+int.from_bytes(
            hashlib.sha256(row["candidate_id"].encode()).digest()[:4],"big"))
        vac=evaluate_multistart(point,state,starts,maxiter=maxiter)
        witness=bool(vac["most_negative_witness"] is not None)
        if vac["successful_field_evaluations"]<=0:
            raise ValueError("No successful original tree vacuum search "+row["candidate_id"])
        row["original_tree_vacuum_status"]=vac["status"]
        row["vacuum_multistart_no_deeper_witness"]=not witness
        row["C5_explicit_deeper_original_tree_potential_witness"]=witness
        row["C5_min_delta_V_over_v4"]=(
            vac["lowest_point_found"]["difference_from_EW_over_v4"] if
            vac["lowest_point_found"] else None)
        row["diagnostic_status"]=(
            "ORIGINAL_RGE_AND_NO_TREE_DEEPER_WITNESS_DIAGNOSTIC"
            if not witness else "EXPLICIT_DEEPER_TREE_WITNESS")
        if not witness:
            results.append(row)
        stats["original_vacuum_cases_tested"]+=1
        stats["original_vacuum_deeper_witness"]+=int(witness)
        print("E1_ORIGINAL_VACUUM",i,"/",min(len(candidates_pending),max_followup),
              row["candidate_id"],row["diagnostic_status"],flush=True)
    selected=rank_pool(results, min(len(results),100))
    with (output/"E1_vacuum_tested_original_models.json").open("w") as stream:
        json.dump([{k:v for k,v in row.items() if not k.startswith("_")}
                   for row in candidates_pending[:max_followup]],
                  stream,indent=2,allow_nan=False)
    with (output/"E1_source_exact_neutrino_solutions_for_100_ranked_NOT_ALLOWED.json").open("w") as stream:
        json.dump({row["candidate_id"]:row["_original_source_neutrino_solution"]
                   for row in selected},stream,indent=2,allow_nan=False)
    with (output/"E1_100_original_10TeV_RGE_vacuum_diagnostic_shortlist_NOT_ALLOWED.csv").open(
            "w",newline="") as stream:
        fields=("candidate_id","mH1_GeV","mH2_GeV","gamma","tanbeta",
                "cascade_upper_proxy","matching_scattering_ratio_to_8pi",
                "maximum_unity_ratio_to_8pi_along_run","original_tree_vacuum_status",
                "single_B2_partial_LFV_score_NOT_EXCLUSION",
                "diagnostic_status")
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        writer.writerows({k:z[k] for k in fields} for z in selected)
    # The canonical B4 CSV has more than the minimal numeric scan fields.
    # Select exact archived source rows by ID rather than reconstructing
    # missing observables or altering their numeric precision.
    return stats,len(candidates_pending),selected


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-dir",type=Path,default=DEFAULT_CAMPAIGN)
    ap.add_argument("--postscan-result",type=Path,default=DEFAULT_POSTSCAN)
    ap.add_argument("--generator-output",type=Path,default=DEFAULT_GENERATOR)
    ap.add_argument("--q4v13-report",type=Path,default=DEFAULT_Q4_REPORT)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--uv-steps",type=int,default=24)
    ap.add_argument("--orbit-samples",type=int,default=512)
    ap.add_argument("--vacuum-multistarts",type=int,default=128)
    ap.add_argument("--vacuum-maxiter",type=int,default=1000)
    ap.add_argument("--max-vacuum-followup",type=int,default=150)
    ap.add_argument("--random-seed",type=int,default=20261020)
    args=ap.parse_args()
    if (args.uv_steps not in (24,48) or not 256<=args.orbit_samples<=8192
        or not 64<=args.vacuum_multistarts<=1024
        or not 10<=args.max_vacuum_followup<=500
        or not 200<=args.vacuum_maxiter<=6000):
        ap.error("Unsupported source-controlled E1 campaign scale")
    if not BASE.resolve().is_relative_to(Path("/home")):
        ap.error("Source execution must remain under /home")
    out=args.output_dir.resolve()
    if not out.is_relative_to(BASE.resolve()/"work") or (
            out.exists() and any(out.iterdir())):
        ap.error("E1 needs a fresh empty output in the checkout work/")
    out.mkdir(parents=True,exist_ok=True)
    result={"status":BLOCKED,
            "physical_Zee_allowed_or_excluded":None,
            "required_missing_constraints":EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED}
    try:
        from zee_gateC3_running_complex_bfb import orbit_design
        input_rows,source,prov=verify_prior(
            args.campaign_dir.resolve(),args.postscan_result.resolve(),
            args.generator_output.resolve(),args.q4v13_report.resolve())
        orbits=orbit_design(args.orbit_samples)
        starts=np.zeros((args.vacuum_multistarts,6),float) # count-only input
        stats,RGEs_pass,selected=run(
            input_rows,source,args.uv_steps,orbits,starts,
            args.vacuum_maxiter,args.random_seed,out,args.max_vacuum_followup)
        # Preserve source B4 CSV rows exactly for downstream official
        # B2/B3/phenomenology. This is not a regenerated scalar point.
        archive=(args.campaign_dir.resolve()/"B4_adaptive"/
                 "all_screened_candidates_NOT_ALLOWED.csv")
        selected_ids=[r["candidate_id"] for r in selected]
        ids=set(selected_ids)
        selected_source={}
        with archive.open(newline="") as f:
            reader=csv.DictReader(f)
            columns=reader.fieldnames
            for row in reader:
                if row["id"] in ids:
                    if row["id"] in selected_source:
                        raise ValueError("Repeated original B4 ID in archive")
                    selected_source[row["id"]]=row
        if len(selected_source)!=len(ids):
            raise ValueError("Cannot recover all original B4 shortlist records")
        with (out/"E1_100_original_B4_full_source_NOT_ALLOWED.csv").open(
                "w",newline="") as f:
            wr=csv.DictWriter(f,fieldnames=columns)
            wr.writeheader()
            wr.writerows(selected_source[i] for i in selected_ids)
        result={
            "status":STATUS,
            "input_original_B4_scalar_EWPO_points":len(input_rows),
            "RGE_two_resolution_pass_all_before_vacuum":RGEs_pass,
            "vacuum_followup_limit":args.max_vacuum_followup,
            "RGE_screens_passing_but_vacuum_not_evaluated":
                max(0,RGEs_pass-args.max_vacuum_followup),
            "original_B4_10TeV_plus_numerical_vacuum_no_witness_tested":
                stats["original_vacuum_cases_tested"]-
                stats["original_vacuum_deeper_witness"],
            "ranked_original_B4_diagnostic_shortlist_size":
                len(selected),
            "source_provenance":prov,
            "diagnostic_counts":dict(stats),
            "selection_is_biased_not_posterior_or_exclusion":True,
            "only_ONE_neutrino_closed_texture_per_scalar_tested":True,
            "passes_10TeV_is_chosen_theory_validity_scale_not_exclusion":True,
            "no_deeper_tree_vacuum_found_not_global_certificate":True,
            "physical_Zee_allowed_or_excluded":None,
            "required_missing_constraints":EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED,
        }
        result["output_file_SHA256"]={
            p.name:digest(p) for p in out.glob("E1_*")
            if p.is_file()}
        (out/"summary.json").write_text(
            json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
        print("E1_STATUS",STATUS,"DIAGNOSTIC_CANDIDATES",
              len(selected),"ORIGINAL_B4_SCALAR_SCREENED",len(input_rows),
              "FULL_ZEE_ALLOWED_UNKNOWN",flush=True)
        return 0
    except Exception as exc:
        result["error"]=repr(exc)
        result["traceback"]=traceback.format_exc()
        (out/"summary.json").write_text(
            json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("E1_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
