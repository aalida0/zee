#!/usr/bin/env python3
"""E3: all E2 no-witness ORIGINAL Zee spectra, multi-root exact-neutrino LFV.

Single resumable campaign:
  - provenance-locked 309 B4 original potentials, 395/395 prior vacuum checks
  - 300 B2 neutrino-closure f/Y trials per original scalar spectrum
  - top 5 B2 by one-loop subset => independent D1 coherent one-loop +
    fermion-photon Barr-Zee and neutral-tree 3-lepton amplitudes
  - optimize the best 2 under exact-neutrino closure using existing D2
  - recompute D4 W-photon dipoles and rank the two with THAT extended score
  - rerun original full model one-loop RGE+BFB+55-channel tree unitarity
    with the actual chosen optimized f/Y using 24 and 48 RK4 steps.
Outputs source-linked JSONL checkpoint, full rows and original B4 CSV.
NEVER claims complete LFV, global vacuum certificate or allowed Zee points.
"""
from __future__ import annotations
import argparse
import collections
import csv
import functools
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import traceback
from pathlib import Path

import numpy as np

from zee_gateE1_original_5557_running_funnel import (
    BASE,DEFAULT_CAMPAIGN,DEFAULT_GENERATOR,DEFAULT_Q4_REPORT,digest,
    EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED)
from zee_gateE2_complete_395_original_vacua import STATUS as E2_STATUS
from gateB2_zee_neutrino_family_scan import (
    solve_point, f_from_null_parameter)
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix, antisymmetric_f_with_null_condition)
from zee_gateD1_joint_300_neutrino_lfv_inventory import candidate_flavor
from zee_gateD2_neutrino_exact_partial_LFV_optimization import (
    optimize_start, optimize_kernels_cache)
from zee_gateD4_W_photon_barr_zee_27 import (
    compare_partial)
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_gateC1_joined_uv_pilot import (
    build_model_state,verify_rge_validation)
from zee_gateC4_running_55channel_unitarity import full_trajectory
from zee_gateC3_running_complex_bfb import orbit_design
from zee_section8_Q4_generated_source_limit_probe import (
    find_rges,load_generated)

STATUS="E3_309_ORIGINAL_MULTIROOT_D1_D2_D4_OPTIMIZED_RGE_PARTIAL_NOT_ALLOWED"
BLOCKED="E3_BLOCKED_NOT_FULL_ZEE_ALLOWED"
REQUIRED=309
MISSING=[
    *EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED,
    "W_photon_Barr_Zee_is_partial_and_independent_validation_pending",
    "other_two_loop_CLFV_Z_penguin_box_and_mu_e_conversion",
    "uncertainties_on_neutrino_observables_and_inverted_ordering",
]


def finite(x,name):
    y=float(x)
    if not math.isfinite(y):
        raise ValueError("Nonfinite "+name)
    return y


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path,obj):
    Path(path).write_text(
        json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+"\n")


def load_inputs(e2, generator, q4):
    report=read_json(e2/"summary.json")
    if (report.get("status")!=E2_STATUS or
        report.get("source_E1_original_10TeV_RGE_pass")!=395 or
        report.get("all_RGE_qualified_original_potentials_vacuum_evaluated")!=395 or
        report.get("no_deeper_tree_vacuum_witness_found")!=309 or
        report.get("explicit_deeper_tree_vacuum_witnesses")!=86 or
        report.get("global_tree_vacuum_certified") is not False or
        report.get("full_Zee_experimental_allowed_or_excluded") is not None):
        raise ValueError("E2 must be finished and have only numerical, nonphysical labels")
    names=(
        "E2_all_395_original_B4_vacuum_evidence.jsonl",
        "E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv",
        "E2_diverse_top100_original_B4_NOT_ALLOWED.csv",
        "E2_top100_one_B2_Yukawa_texture_NOT_ALLOWED.json")
    for name in names:
        path=e2/name
        if not path.is_file() or digest(path)!=report.get("output_SHA256",{}).get(name):
            raise ValueError("E2 output hash missing or changed: "+name)
    src=find_rges(generator)
    if digest(src)!=report.get("E1_original_RGE_source_SHA256"):
        raise ValueError("Generated Q4 one-loop source differs from E2")
    verify_rge_validation(q4,src)
    path=e2/names[1]
    with path.open(newline="") as f:
        reader=csv.DictReader(f)
        records=list(reader)
        fields=reader.fieldnames
    if len(records)!=REQUIRED or not fields:
        raise ValueError("E2 no-witness B4 cohort must have exactly 309 spectra")
    byid={}
    for r in records:
        name=r["id"]
        if not name or name in byid or r.get("candidate_status")!=(
            "SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"):
            raise ValueError("E2 original B4 CSV has duplicate or misclassified point")
        byid[name]=r
    archive=e2/names[0]
    rg,allowed={},set()
    with archive.open() as f:
        for line in f:
            row=json.loads(line)
            name=row["candidate_id"]
            if name in rg:
                raise ValueError("Duplicate original E2 vacuum evidence ID")
            rg[name]=row
            if row.get("original_1loop_RGE_10TeV_screen") is not True:
                raise ValueError("E2 original RGE-passing cohort drift")
            if row.get("C5_explicit_deeper_original_tree_potential_witness") is False:
                allowed.add(name) # ONLY 'no tree witness found' nomenclature
    if len(rg)!=395 or len(allowed)!=309 or allowed!=set(byid):
        raise ValueError("E2 source/RGE/vacuum sample partition inconsistent")
    if any(row.get("full_Zee_experimental_allowed_or_excluded") is not None
           for row in rg.values()):
        raise ValueError("E2 evidence contains false full Zee acceptance")
    return {
        "records":records,"B4_fields":fields,"byid":byid,
        "RG_evidence":rg,"module":load_generated(src),
        "source_RGE_SHA256":digest(src),
        "E2_summary_SHA256":digest(e2/"summary.json"),
        "E2_inputs_sha256":{name:digest(e2/name) for name in names},
        "Q4v13_validation_SHA256":digest(q4),
    }


def try_B2_family(p,rng,target,fseed,n_trials,top):
    output=[]
    failures=collections.Counter()
    anchor_score=None
    for j in range(n_trials):
        try:
            if j==0:
                f=fseed
                strength=0.
            else:
                t=complex(rng.uniform(-1.5,1.5),
                          rng.uniform(-1.5,1.5))
                f=f_from_null_parameter(
                    target,t,10**rng.uniform(-5,-2),
                    int(rng.integers(0,2)))
                strength=float(10**rng.uniform(-1.5,1.))
            z=solve_point(p,target,f,rng,strength)
            if z is None:
                failures["nonperturbative_or_unsolved"]+=1
            else:
                if z["candidate_id"]!=p["id"] or z.get("status")!=(
                    "NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED"):
                    raise ValueError("B2 unexpected allowed label or wrong scalar ID")
                if finite(z["neutrino_matrix_closure_eV"],"neutrino closure")>=1e-9:
                    raise ValueError("B2 neutrino closure lost")
                if j==0:
                    anchor_score=finite(z["partial_LFV_score_NOT_EXCLUSION"],
                                        "E1 anchor score")
                output.append(z)
        except (ValueError,ArithmeticError,np.linalg.LinAlgError,OverflowError) as exc:
            if j==0:
                raise ValueError("Original B2 seed texture unexpectedly unavailable") from exc
            failures[type(exc).__name__]+=1
    if anchor_score is None:
        raise ValueError("Original B2 seed not saved")
    output.sort(key=lambda x:finite(x["partial_LFV_score_NOT_EXCLUSION"],"B2 subset score"))
    return output[:top], {
        "attempted":n_trials,"closed_and_perturbative":n_trials-sum(failures.values()),
        "saved":min(top,len(output)),
        "discarded_or_failed":sum(failures.values()),
        "failure_categories":dict(failures),
        "original_E1_rank1_partial_score":anchor_score,
    }


def original_yukawa_RGE(mod,p,solution,orbits,steps):
    state,pre=build_model_state(p,solution)
    if finite(pre["neutrino_matrix_closure_eV"],"optimized closure")>=1e-9:
        raise ValueError("Optimized state does not reproduce neutrino mass")
    coarse=full_trajectory(mod,state,mu0=p["mH2"],upper=10000.,
                           steps=steps,orbits=orbits)
    refined=full_trajectory(mod,state,mu0=p["mH2"],upper=10000.,
                            steps=2*steps,orbits=orbits)
    fields=("reached_end_scale","BFB_sufficient_at_all_sampled_steps",
            "tree_unitarity_8pi_at_all_sampled_steps","BFB_negative_witness")
    same=all(bool(coarse[k])==bool(refined[k]) for k in fields)
    pass_two=bool(same and coarse["reached_end_scale"] and
                  coarse["BFB_sufficient_at_all_sampled_steps"] and
                  coarse["tree_unitarity_8pi_at_all_sampled_steps"])
    return {
        "original_potential_rge_recomputed_with_optimized_Yukawas":True,
        "run_to_GeV":10000.,"coarse_steps":steps,"refined_steps":steps*2,
        "two_resolution_status_agreement":same,
        "sampled_BFB_and_55channel_unitarity_pass_to_10TeV":pass_two,
        "original_RGE_failure_DOES_NOT_imply_experimentally_excluded":True,
        "maximum_eigenvalue_encountered_coarse":finite(
            coarse["maximum_scattering_eigenvalue_encountered"],"C4 eigen"),
        "maximum_eigenvalue_encountered_refined":finite(
            refined["maximum_scattering_eigenvalue_encountered"],"C4 eigen"),
        "coarse_outcome":coarse["status"],
        "refined_outcome":refined["status"],
        "first_failed_unitarity_scale_coarse":
            coarse["first_tree_unitarity_uncertified_scale_GeV"],
        "first_failed_unitarity_scale_refined":
            refined["first_tree_unitarity_uncertified_scale_GeV"],
    }


def analyze(p,evidence,module,target,fseed,rng,n_trials,top,
            opt_starts,maxeval,orbits,steps):
    saved,trial=try_B2_family(p,rng,target,fseed,n_trials,top)
    old=finite(evidence["single_B2_partial_LFV_score_NOT_EXCLUSION"],
               "E1 one-B2-rank score")
    if not math.isclose(trial["original_E1_rank1_partial_score"],old,
                        rel_tol=1e-8,abs_tol=1e-12):
        raise ValueError("E1 initial exact-neutrino B2 family drift")
    if len(saved)!=top:
        # A spectrum with fewer than five exact-neutrino textures is
        # NOT physically excluded; preserve that in the record.
        return {
            "candidate_id":p["id"],
            "diagnostic_status":"INSUFFICIENT_SAVED_B2_FAMILIES_NOT_PHYSICAL_EXCLUSION",
            "B2":trial,"D1":None,"D2":None,"D4":None,
            "optimized_original_potential_RGE":None,
            "full_Zee_allowed_or_excluded":None}
    details=[candidate_flavor(p,sol,i+1) for i,sol in enumerate(saved)]
    if len(details)!=top or any(z["candidate_id"]!=p["id"] for z in details):
        raise ValueError("D1 source mismatched B2")
    ranked=sorted(range(top),
        key=lambda k:finite(details[k]["joint_incomplete_LFV_score_NOT_EXCLUSION"],
                            "D1 joint LFV"))
    candidates=[]
    for index in ranked[:opt_starts]:
        opt=optimize_start(p,saved[index],details[index],max_evals=maxeval)
        if not math.isclose(
            finite(opt["seed_original_score"],"D2 source score"),
            details[index]["joint_incomplete_LFV_score_NOT_EXCLUSION"],
            rel_tol=2e-8,abs_tol=1e-11):
            raise ValueError("D2/D1 same-objective reference mismatch")
        f=complex_matrix(opt["solution"]["f"],"f")
        Y=complex_matrix(opt["solution"]["Y"],"Y")
        updated=compare_partial(p,f,Y,opt)
        new=finite(updated["new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION"],
                   "D4 W gamma score")
        candidates.append((new,index,opt,updated))
    chosen=min(candidates,key=lambda t:t[0])
    new,index,opt,w=chosen
    rge=original_yukawa_RGE(module,p,opt["solution"],orbits,steps)
    return {
        "candidate_id":p["id"],
        "diagnostic_status":"MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED",
        "B2":trial,"B2_top_five_exact_neutrino_Yukawas":saved,
        "D1": {
            "saved_rank_1_to_5_partial_joint_scores":[
                v["joint_incomplete_LFV_score_NOT_EXCLUSION"] for v in details],
            "best_partial_joint_score":min(
                x["joint_incomplete_LFV_score_NOT_EXCLUSION"] for x in details),
            "best_D1_rank":ranked[0]+1,
        },
        "D2":{
            "number_optimized_family_starts":len(candidates),
            "parent_B2_rank_chosen":index+1,
            "chosen_optimized_source":opt,
            "optimization_is_local_not_global":True,
            "best_D2_score_before_D4":
                min(x[2]["best_score"] for x in candidates),
        },
        "D4_W_photon":w,
        "selected_D4_extended_partial_LFV_score_NOT_EXCLUSION":new,
        "D4_partial_score_below_one_NOT_ALLOWED":bool(new<1.),
        "optimized_original_potential_RGE":rge,
        "E2_no_deeper_tree_vacuum_witness_global_proof":False,
        "complete_neutrino_LFV_likelihood_available":False,
        "full_Zee_allowed_or_excluded":None,
    }


def load_checkpoint(path,valid):
    result={}
    if path.is_file():
        with path.open() as f:
            for line in f:
                rec=json.loads(line)
                key=rec["candidate_id"]
                if key in result or key not in valid or (
                    rec.get("full_Zee_allowed_or_excluded") is not None):
                    raise ValueError("Duplicated/unknown E3 checkpoint result")
                result[key]=rec
    return result


def finalize(output,allrows,results,data,settings):
    if set(results)!=set(data["byid"]) or len(results)!=REQUIRED:
        raise ValueError("Cannot finalize E3 without every original no-witness spectrum")
    if any(r["full_Zee_allowed_or_excluded"] is not None
           for r in results.values()):
        raise ValueError("E3 attempted to assign experimental acceptance")
    records=[results[k] for k in sorted(results)]
    with (output/"E3_all_309_multi_neutrino_partial_LFV_diagnostics.jsonl").open("w") as h:
        for rec in records:
            h.write(json.dumps(rec,sort_keys=True,allow_nan=False)+"\n")
    ranked=[]
    for rec in records:
        if rec["diagnostic_status"]!=(
            "MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED"):
            continue
        p=data["byid"][rec["candidate_id"]]
        rge=rec["optimized_original_potential_RGE"]
        ranked.append({
            "candidate_id":rec["candidate_id"],
            "mH1_GeV":float(p["mH1"]),"mH2_GeV":float(p["mH2"]),
            "gamma":float(p["gamma"]),"tanbeta":math.tan(float(p["beta"])),
            "cascade_upper_proxy":
                float(p["production_weighted_nonleptonic_cascade_upper_proxy"]),
            "best_D1_partial_ratio":rec["D1"]["best_partial_joint_score"],
            "best_D2_partial_ratio_before_D4":
                rec["D2"]["best_D2_score_before_D4"],
            "chosen_D4_extended_partial_ratio_NOT_EXCLUSION":
                rec["selected_D4_extended_partial_LFV_score_NOT_EXCLUSION"],
            "D4_partial_below_one_NOT_ALLOWED":
                rec["D4_partial_score_below_one_NOT_ALLOWED"],
            "optimized_Yukawa_two_resolution_10TeV_screen_pass":
                rge["sampled_BFB_and_55channel_unitarity_pass_to_10TeV"],
            "tree_vacuum_global_minimum_proven":False,
            "full_experimental_Zee_allowed":None,
        })
    ranked.sort(key=lambda r:(
        not r["optimized_Yukawa_two_resolution_10TeV_screen_pass"],
        r["chosen_D4_extended_partial_ratio_NOT_EXCLUSION"],
        -r["cascade_upper_proxy"]))
    output_csv=output/"E3_ranked_309_original_flavor_RGE_NOT_ALLOWED.csv"
    fields=("candidate_id","mH1_GeV","mH2_GeV","gamma","tanbeta",
            "cascade_upper_proxy","best_D1_partial_ratio",
            "best_D2_partial_ratio_before_D4",
            "chosen_D4_extended_partial_ratio_NOT_EXCLUSION",
            "D4_partial_below_one_NOT_ALLOWED",
            "optimized_Yukawa_two_resolution_10TeV_screen_pass",
            "tree_vacuum_global_minimum_proven",
            "full_experimental_Zee_allowed")
    with output_csv.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(ranked)
    def n(p):
        return sum(bool(p(row)) for row in ranked)
    summary={
        "status":STATUS,"E2_original_no_deeper_witness_cohort":REQUIRED,
        "multi_root_D1_D2_D4_evaluated_spectra":len(ranked),
        "B2_insufficient_family_spectra":REQUIRED-len(ranked),
        "optimized_Yukawas_rechecked_original_RGE":len(ranked),
        "optimized_Yukawa_10TeV_running_screen_pass":
            n(lambda r:r["optimized_Yukawa_two_resolution_10TeV_screen_pass"]),
        "D4_extended_partial_ratio_below_one_NOT_FULL_LFV_PASS":
            n(lambda r:r["D4_partial_below_one_NOT_ALLOWED"]),
        "both_RGE_screen_and_partial_D4_below_one_NOT_FULL_ZEE_ALLOWED":
            n(lambda r:r["optimized_Yukawa_two_resolution_10TeV_screen_pass"]
              and r["D4_partial_below_one_NOT_ALLOWED"]),
        "one_selected_optimized_family_per_spectrum_not_full_Yukawa_space":True,
        "NO_complete_experimental_Zee_allowed_or_excluded":None,
        "theory_to_10TeV_is_chosen_scale_not_exclusion":True,
        "E2_no_deeper_vacuum_witness_NOT_global_proof":True,
        "remaining_missing_physics":MISSING,
        "E2_provenance":{k:v for k,v in data.items()
                          if "SHA256" in k or k=="E2_inputs_sha256"},
        "settings":settings,
        "csv_sha256":digest(output_csv),
        "evidence_SHA256":digest(
            output/"E3_all_309_multi_neutrino_partial_LFV_diagnostics.jsonl"),
    }
    write_json(output/"summary.json",summary)
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--e2-dir",type=Path,required=True)
    ap.add_argument("--generator-output",type=Path,default=DEFAULT_GENERATOR)
    ap.add_argument("--q4v13-report",type=Path,default=DEFAULT_Q4_REPORT)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--neutrino-trials",type=int,default=300)
    ap.add_argument("--B2-top",type=int,default=5)
    ap.add_argument("--optimize-starts",type=int,default=2)
    ap.add_argument("--optimizer-maxeval",type=int,default=240)
    ap.add_argument("--uv-steps",type=int,default=24)
    ap.add_argument("--orbits",type=int,default=2048)
    ap.add_argument("--seed",type=int,default=20261014)
    ap.add_argument("--resume",action="store_true")
    a=ap.parse_args()
    if (a.neutrino_trials!=300 or a.B2_top!=5 or
        a.optimize_starts!=2 or a.optimizer_maxeval!=240 or
        a.uv_steps!=24 or a.orbits!=2048 or a.seed!=20261014):
        ap.error("Use source-pinned E3 full 309-scan research settings")
    if not BASE.resolve().is_relative_to(Path("/home")):
        ap.error("E3 must execute from /home code")
    out=a.output_dir.resolve()
    if not out.is_relative_to(BASE.resolve()/"work"):
        ap.error("E3 output must be inside original /home repo work tree")
    if out.exists() and any(out.iterdir()) and not a.resume:
        ap.error("Refuse overwriting prior E3 work; use --resume or fresh path")
    if a.resume and not (out/"manifest.json").is_file():
        ap.error("Cannot resume without original E3 manifest")
    out.mkdir(parents=True,exist_ok=True)
    try:
        inputs=load_inputs(a.e2_dir.resolve(),
                           a.generator_output.resolve(),
                           a.q4v13_report.resolve())
        git=subprocess.run(["git","rev-parse","HEAD"],cwd=BASE,
                           capture_output=True,text=True,check=True)
        settings={
            "neutrino_trials":300,"B2_top":5,"optimize_starts":2,
            "optimizer_maxeval":240,"uv_steps":24,
            "orbits":2048,"seed":20261014,
        }
        manifest={
            "status":"E3_RUNNING_NOT_ALLOWED",
            "settings":settings,
            "E2_summary_SHA256":inputs["E2_summary_SHA256"],
            "source_RGE_SHA256":inputs["source_RGE_SHA256"],
            "Q4v13_validation_SHA256":inputs["Q4v13_validation_SHA256"],
            "script_SHA256":digest(Path(__file__)),
            "source_git_head":git.stdout.strip(),
            "full_Zee_allowed_or_excluded":None,
        }
        if a.resume:
            old=read_json(out/"manifest.json")
            for key in ("settings","E2_summary_SHA256",
                        "source_RGE_SHA256","Q4v13_validation_SHA256",
                        "script_SHA256"):
                if old.get(key)!=manifest[key]:
                    raise ValueError("E3 resume source/settings mismatch: "+key)
            if (out/"summary.json").is_file():
                raise ValueError("Cannot resume completed E3 campaign")
        else:
            write_json(out/"manifest.json",manifest)
        optimize_kernels_cache()
        # Caching original expensive W-photon loop integrals is safe:
        # they depend only on the physical scalar/W masses.
        import zee_gateD4_W_photon_barr_zee_27 as d4
        if not hasattr(d4.photon_W_kernel,"cache_info"):
            d4.photon_W_kernel=functools.lru_cache(maxsize=4096)(
                d4.photon_W_kernel)
        M,_=target_neutrino_matrix()
        fseed,_=antisymmetric_f_with_null_condition(M)
        orbits=orbit_design(a.orbits)
        checkpoint=out/"E3_309_spectrum_checkpoint.jsonl"
        completed=load_checkpoint(checkpoint,inputs["byid"])
        print("E3_ALREADY_COMPLETED",len(completed),flush=True)
        with checkpoint.open("a") as handle:
            for i,name in enumerate(sorted(inputs["byid"]),1):
                if name in completed:
                    continue
                p={k:float(v) if k!="id" else v
                   for k,v in inputs["byid"][name].items()
                   if k in ("id","mH1","mH2","mh2","ma","alpha",
                            "beta","gamma","m12sq","lc","k1","k2","k12",
                            "production_weighted_nonleptonic_cascade_upper_proxy")}
                # One deterministic RNG per spectrum; job restart cannot
                # perturb the nullspace-root random stream of later spectra.
                seed=int.from_bytes(hashlib.sha256(
                    name.encode()).digest()[:8],"big")^a.seed
                row=analyze(p,inputs["RG_evidence"][name],
                            inputs["module"],M,fseed,
                            np.random.default_rng(seed),
                            a.neutrino_trials,a.B2_top,
                            a.optimize_starts,a.optimizer_maxeval,
                            orbits,a.uv_steps)
                if row["candidate_id"]!=name or row[
                        "full_Zee_allowed_or_excluded"] is not None:
                    raise ValueError("E3 checkpoint identity or physics label invalid")
                handle.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
                handle.flush()
                os.fsync(handle.fileno())
                completed[name]=row
                print("E3_SPECTRUM",i,"/",len(inputs["byid"]),
                      name,row["diagnostic_status"],
                      "D4_PARTIAL",row.get(
                         "selected_D4_extended_partial_LFV_score_NOT_EXCLUSION"),
                      "ORIGINAL_OPTIMIZED_RGE_10TEV",(
                          (row.get("optimized_original_potential_RGE") or {})
                           .get("sampled_BFB_and_55channel_unitarity_pass_to_10TeV")),
                      "NOT_ALLOWED",flush=True)
        summary=finalize(out,inputs["records"],completed,inputs,settings)
        manifest["status"]=STATUS
        manifest["summary_SHA256"]=digest(out/"summary.json")
        write_json(out/"manifest.json",manifest)
        print("E3_STATUS",STATUS,"MODELS",summary[
            "multi_root_D1_D2_D4_evaluated_spectra"],
            "RGE_OPTIMIZED_PASS",summary[
                "optimized_Yukawa_10TeV_running_screen_pass"],
            "FULL_ZEE_ALLOWED_UNKNOWN",flush=True)
        return 0
    except Exception as exc:
        write_json(out/"error.json",{
            "status":BLOCKED,"error":repr(exc),
            "traceback":traceback.format_exc(),
            "full_Zee_allowed_or_excluded":None})
        print("E3_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
