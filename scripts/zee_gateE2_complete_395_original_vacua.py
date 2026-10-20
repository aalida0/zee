#!/usr/bin/env python3
"""E2: finish 245 MISSING original-B4 tree-vacuum searches from E1.

No second B4 scan or 5,557-point RGE evolution. Source/fingerprinted
E1 ledger, 395 RGE passes, and first 150 vacuum results are reused
without mutation; 245 remaining are evaluated using the IDENTICAL
B2 single-texture recipe, original B4 potential, seeds, C5 optimizer
and numerical settings. Checkpoint supports safe --resume.

No-witness is NOT a global vacuum certificate, and no Zee experimental
allowed/excluded label is produced.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import traceback
from pathlib import Path

import numpy as np
from zee_gateE1_original_5557_running_funnel import (
    BASE, DEFAULT_CAMPAIGN, DEFAULT_POSTSCAN, DEFAULT_GENERATOR,
    DEFAULT_Q4_REPORT, STATUS as E1_STATUS, digest, parse_rows,
    rank_pool, verify_prior, EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED,
)

STATUS = "E2_ALL_395_ORIGINAL_B4_VACUA_NUMERICAL_AUDIT_NOT_ALLOWED"
BLOCKED = "E2_MISSING_VACUUM_AUDIT_BLOCKED_NOT_ALLOWED"
EXPECTED_RGE = 395
EXPECTED_OLD = 150
EXPECTED_REMAINING = EXPECTED_RGE - EXPECTED_OLD


def finite(x, label):
    y = float(x)
    if not math.isfinite(y):
        raise ValueError("Nonfinite " + label)
    return y


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    Path(path).write_text(
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def load_e1(campaign, e1, postscan, generator, q4):
    # Reconfirm the ORIGINAL B4/S,T,U discovery data and the exact
    # 676/676 validated PyR@TE Q4 RGE-source provenance.
    source_rows, rge_source, source_provenance = verify_prior(
        campaign, postscan, generator, q4)
    summary_path = e1 / "summary.json"
    summary = read_json(summary_path)
    if (summary.get("status") != E1_STATUS or
        summary.get("input_original_B4_scalar_EWPO_points") != 5557 or
        summary.get("RGE_two_resolution_pass_all_before_vacuum") != EXPECTED_RGE or
        summary.get("RGE_screens_passing_but_vacuum_not_evaluated") != EXPECTED_REMAINING or
        summary.get("vacuum_followup_limit") != EXPECTED_OLD or
        summary.get("original_B4_10TeV_plus_numerical_vacuum_no_witness_tested") != 106):
        raise ValueError("E1 summary is not the finished 395/150/106 campaign")
    if summary.get("source_provenance") != source_provenance:
        raise ValueError("E1 original B4/Q4 source provenance changed")

    paths = {
        "summary": summary_path,
        "ledger": e1 / "E1_all_5557_original_model_scalar_RGE_diagnostics.jsonl",
        "tested": e1 / "E1_vacuum_tested_original_models.json",
        "saved40": e1 / "E1_source_exact_neutrino_solutions_for_100_ranked_NOT_ALLOWED.json",
        "B4": campaign / "B4_adaptive" / "all_screened_candidates_NOT_ALLOWED.csv",
    }
    for key, filepath in paths.items():
        if not filepath.is_file():
            raise FileNotFoundError(f"Missing E1 {key}: {filepath}")
        if key in ("ledger", "tested", "saved40"):
            old = summary["output_file_SHA256"].get(filepath.name)
            if digest(filepath) != old:
                raise ValueError("E1 output SHA mismatch for "+key)

    point_by_id = {r["id"]: r for r in source_rows}
    if len(point_by_id) != 5557:
        raise ValueError("Original B4 population ID duplication")
    ledger = {}
    rg_ok = {}
    with paths["ledger"].open() as stream:
        for line in stream:
            row = json.loads(line)
            name = row["candidate_id"]
            if name not in point_by_id or name in ledger:
                raise ValueError("E1 ledger missing/duplicated original B4 ID")
            if row.get("full_Zee_experimental_allowed_or_excluded") is not None:
                raise ValueError("E1 ledger falsely claims full model acceptance")
            if row.get("original_1loop_RGE_10TeV_screen") is True:
                if row.get("diagnostic_status") != "RGE_PASS_VACUUM_NOT_YET_TESTED":
                    raise ValueError("E1 successful RGE has unexpected status")
                rg_ok[name] = row
            ledger[name] = row
    if len(ledger) != 5557 or len(rg_ok) != EXPECTED_RGE:
        raise ValueError("Incomplete 5,557 / 395 E1 source ledger")

    old = read_json(paths["tested"])
    if not isinstance(old, list) or len(old) != EXPECTED_OLD:
        raise ValueError("E1 first 150 vacuum results missing")
    tested = {}
    for row in old:
        name = row["candidate_id"]
        if name not in rg_ok or name in tested:
            raise ValueError("Duplicate/out-of-cohort E1 vacuum result")
        if (row.get("original_tree_vacuum_status") not in (
            "EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS",
            "NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE")):
            raise ValueError("E1 prior C5 status unrecognized")
        witness = bool(row["C5_explicit_deeper_original_tree_potential_witness"])
        if witness != (row["original_tree_vacuum_status"] ==
                       "EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS"):
            raise ValueError("E1 C5 witness/status disagreement")
        if not math.isclose(
            finite(row["cascade_upper_proxy"], "E1 old cascade"),
            finite(rg_ok[name]["cascade_upper_proxy"], "E1 source cascade"),
            rel_tol=1.e-10, abs_tol=1.e-12):
            raise ValueError("E1 old C5/scalar proxy mismatch")
        tested[name] = row
    if sum(x["C5_explicit_deeper_original_tree_potential_witness"]
           for x in tested.values()) != 44:
        raise ValueError("Expected 44 validated E1 deeper-tree witnesses")

    saved40 = read_json(paths["saved40"])
    if not isinstance(saved40, dict) or len(saved40) != 40:
        raise ValueError("Missing original E1 source solution reference cohort")
    if not set(saved40).issubset(tested):
        raise ValueError("Source-validated 40-neutrino solutions not in E1 old cohort")
    if any(tested[k]["C5_explicit_deeper_original_tree_potential_witness"]
           for k in saved40):
        raise ValueError("Original E1 40-neutrino solutions not from no-witness subset")

    remaining = sorted(
        set(rg_ok) - set(tested),
        key=lambda k: (-rg_ok[k]["cascade_upper_proxy"], k))
    if len(remaining) != EXPECTED_REMAINING:
        raise ValueError("E1 untested RGE cohort not precisely 245")
    # Unbiased with respect to the extra C5 evaluation: ALL residual RGE
    # candidates, not just collider-proxy leaders, receive a C5 search.
    hashes = {k: digest(p) for k,p in paths.items()}
    return {
        "points": point_by_id, "rge_pass": rg_ok,
        "old": tested, "saved40": saved40,
        "remaining": remaining, "paths": paths,
        "hashes": hashes,
        "q4_RGE_source_sha256": digest(rge_source),
        "provenance": source_provenance,
    }


def reproduce_single_B2(point, rng):
    from gateA1b_hierarchical_no_seed import (
        target_neutrino_matrix, antisymmetric_f_with_null_condition)
    from gateB2_zee_neutrino_family_scan import solve_point
    target, _ = target_neutrino_matrix()
    f0, _ = antisymmetric_f_with_null_condition(target)
    solution = solve_point(point, target, f0, rng, 0.)
    if solution is None or solution.get("status") != (
        "NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED"):
        raise ValueError("Cannot reconstruct E1 single-B2-texture solution")
    if solution.get("candidate_id") != point["id"]:
        raise ValueError("Reconstructed B2 scalar ID disagrees")
    return solution


def assert_reproduced(saved, current, label):
    for key in ("f", "Y"):
        x,y = saved[key], current[key]
        for part in ("real", "imag"):
            a=np.asarray(x[part],float)
            b=np.asarray(y[part],float)
            if a.shape != (3,3) or b.shape != (3,3) or not np.allclose(
                    a,b,rtol=1.e-9,atol=1.e-12):
                raise ValueError("E1 B2 f/Y single texture drift: "+label)
    for key in ("partial_LFV_score_NOT_EXCLUSION",
                "neutrino_matrix_closure_eV"):
        if not math.isclose(
            finite(saved[key],"saved B2"),finite(current[key],"regen B2"),
            rel_tol=1.e-8,abs_tol=1.e-17):
            raise ValueError("E1 B2 single-texture scoring drift: "+label)


def check_saved_B2_reference(data):
    # BEFORE launching 245 expensive vacuum searches, check that E1's
    # numerical seed/f/Y texture is reproduced exactly in actual physics
    # code, not just a mock.
    rng=np.random.default_rng(20261020)
    for name, saved in sorted(data["saved40"].items()):
        current = reproduce_single_B2(data["points"][name],rng)
        assert_reproduced(saved,current,name)
        ref = data["rge_pass"][name]
        if not math.isclose(
            current["partial_LFV_score_NOT_EXCLUSION"],
            finite(ref["single_B2_partial_LFV_score_NOT_EXCLUSION"],
                   "E1 saved one-texture LFV"),rel_tol=1.e-8,abs_tol=1.e-12):
            raise ValueError("E1 saved B2 and RGE-pass ledger source drift")
    return len(data["saved40"])


def validate_vacuum_record(entry, name):
    if entry.get("candidate_id") != name:
        raise ValueError("E2 checkpoint candidate mismatch")
    expected = ("EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS",
                "NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE")
    if entry.get("original_tree_vacuum_status") not in expected:
        raise ValueError("E2 invalid vacuum outcome")
    witness = bool(entry.get("C5_explicit_deeper_original_tree_potential_witness"))
    if witness != (entry["original_tree_vacuum_status"]==expected[0]):
        raise ValueError("E2 vacuum witness contradicts status")
    if entry.get("global_vacuum_proven") is not False or (
            entry.get("full_Zee_experimental_allowed_or_excluded") is not None):
        raise ValueError("E2 record contains a prohibited physical pass")
    finite(entry["cascade_upper_proxy"],"E2 cascade")
    return True


def read_checkpoint(path, data):
    rows = {}
    if not path.exists():
        return rows
    with path.open() as stream:
        for line in stream:
            if not line.strip():
                raise ValueError("Malformed E2 checkpoint blank line")
            obj = json.loads(line)
            name = obj["candidate_id"]
            if name in rows or name not in data["remaining"]:
                raise ValueError("Duplicate/out-of-cohort E2 checkpoint record")
            validate_vacuum_record(obj,name)
            rows[name] = obj
    return rows


def eval_remaining(data, output, starts, maxiter, seed, existing):
    from zee_gateC1_joined_uv_pilot import build_model_state
    from zee_gateC5_charge_breaking_vacuum_search import (
        candidate_starts, evaluate_multistart)
    progress=output/"E2_missing_245_original_B4_vacuum_checkpoint.jsonl"
    counts = dict(
        reused_existing_E2=len(existing),
        newly_evaluated=0)
    with progress.open("a") as fh:
        for i,name in enumerate(data["remaining"],1):
            if name in existing:
                continue
            point=data["points"][name]
            sol=reproduce_single_B2(point,np.random.default_rng(seed))
            original=data["rge_pass"][name]
            if not math.isclose(
                sol["partial_LFV_score_NOT_EXCLUSION"],
                original["single_B2_partial_LFV_score_NOT_EXCLUSION"],
                rel_tol=1e-8,abs_tol=1e-12):
                raise ValueError("Reconstructed B2 partial score inconsistent: "+name)
            state,_=build_model_state(point,sol)
            actual_seed = seed + int.from_bytes(
                hashlib.sha256(name.encode()).digest()[:4],"big")
            vac=evaluate_multistart(
                point,state,candidate_starts(starts,actual_seed),
                maxiter=maxiter)
            if vac["successful_field_evaluations"]<1:
                raise ValueError("No successful original vacuum optimization: "+name)
            witness = bool(vac["most_negative_witness"] is not None)
            obj={
                "candidate_id":name,
                "mH1_GeV":point["mH1"],
                "mH2_GeV":point["mH2"],
                "gamma":point["gamma"],
                "tanbeta":math.tan(point["beta"]),
                "cascade_upper_proxy":original["cascade_upper_proxy"],
                "matching_scattering_ratio_to_8pi":
                    original["matching_scattering_ratio_to_8pi"],
                "maximum_unity_ratio_to_8pi_along_run":
                    original["maximum_unity_ratio_to_8pi_along_run"],
                "single_B2_partial_LFV_score_NOT_EXCLUSION":
                    original["single_B2_partial_LFV_score_NOT_EXCLUSION"],
                "original_tree_vacuum_status":vac["status"],
                "C5_explicit_deeper_original_tree_potential_witness":witness,
                "C5_min_delta_V_over_v4":None if not vac["lowest_point_found"]
                    else vac["lowest_point_found"]["difference_from_EW_over_v4"],
                "vacuum_successful_starts":vac["successful_field_evaluations"],
                "vacuum_negative_witness_count":vac["negative_witness_count"],
                "vacuum_search_boundary_hits":vac["boundary_hits"],
                "vacuum_witness":vac["most_negative_witness"],
                "E2_reuses_E1_10TeV_RGE_not_recomputed":True,
                "global_vacuum_proven":False,
                "full_Zee_experimental_allowed_or_excluded":None,
                "diagnostic_status":(
                  "EXPLICIT_DEEPER_TREE_WITNESS" if witness else
                  "ORIGINAL_RGE_AND_NO_TREE_DEEPER_WITNESS_DIAGNOSTIC"),
            }
            validate_vacuum_record(obj,name)
            fh.write(json.dumps(obj,sort_keys=True,allow_nan=False)+"\n")
            fh.flush()
            os.fsync(fh.fileno())
            existing[name]=obj
            counts["newly_evaluated"]+=1
            print("E2_ORIGINAL_VACUUM",i,"/",len(data["remaining"]),name,
                  obj["diagnostic_status"],flush=True)
    return counts


def finalize(data, output, existing, params):
    if set(existing)!=set(data["remaining"]):
        raise ValueError("E2 missing vacuum cases; cannot finalize")
    allcases={**data["old"], **existing}
    if len(allcases)!=EXPECTED_RGE:
        raise ValueError("Expected 395 unique original-potential C5 cases")
    if any(not validate_vacuum_record({
        **row,"global_vacuum_proven":False,
        "full_Zee_experimental_allowed_or_excluded":None},key)
        for key,row in allcases.items()):
        raise ValueError("Invalid E1/E2 vacuum evidence")
    witnesses={key:r for key,r in allcases.items()
               if r["C5_explicit_deeper_original_tree_potential_witness"]}
    no_witness={key:r for key,r in allcases.items() if key not in witnesses}
    # Keep every numeric survivor, then optionally prioritize mass-diverse
    # collider candidates. Do NOT discard unselected cases as excluded.
    records=[dict(data["rge_pass"][key],**{
        "original_tree_vacuum_status":r["original_tree_vacuum_status"],
        "C5_explicit_deeper_original_tree_potential_witness":
            r["C5_explicit_deeper_original_tree_potential_witness"],
        "C5_min_delta_V_over_v4":r.get("C5_min_delta_V_over_v4"),
        "diagnostic_status":(
            "EXPLICIT_DEEPER_TREE_WITNESS" if key in witnesses else
            "ORIGINAL_RGE_AND_NO_TREE_DEEPER_WITNESS_DIAGNOSTIC"),
        "full_Zee_experimental_allowed_or_excluded":None,
        "global_vacuum_proven":False,
    }) for key,r in sorted(allcases.items())]
    out_file=output/"E2_all_395_original_B4_vacuum_evidence.jsonl"
    with out_file.open("w") as fh:
        for row in records:
            fh.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
    chosen=rank_pool(
        [r for r in records if not r["C5_explicit_deeper_original_tree_potential_witness"]],
        min(100,len(no_witness)))
    def source_csv(path, ids):
        archive=data["paths"]["B4"]
        with archive.open(newline="") as source:
            reader=csv.DictReader(source)
            fields=reader.fieldnames
            source_rows={row["id"]:row for row in reader if row["id"] in ids}
        if set(source_rows)!=set(ids):
            raise ValueError("E2 lost original B4 source rows")
        with path.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=fields)
            writer.writeheader()
            writer.writerows(source_rows[k] for k in ids)
    all_ids=sorted(no_witness)
    source_csv(output/"E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv",
               all_ids)
    top_ids=[x["candidate_id"] for x in chosen]
    source_csv(output/"E2_diverse_top100_original_B4_NOT_ALLOWED.csv",top_ids)

    # Same neutrino-exact single (f,Y) family used in E1's running screen.
    # Save only the diverse shortlist to keep the artifact compact.
    fY={}
    for key in top_ids:
        if key in data["saved40"]:
            sol=data["saved40"][key]
        else:
            sol=reproduce_single_B2(
                data["points"][key],np.random.default_rng(params["seed"]))
            if not math.isclose(
                sol["partial_LFV_score_NOT_EXCLUSION"],
                data["rge_pass"][key]["single_B2_partial_LFV_score_NOT_EXCLUSION"],
                rel_tol=1e-8,abs_tol=1e-12):
                raise ValueError("B2 saved-source score drift: "+key)
        fY[key]=sol
    write_json(output/"E2_top100_one_B2_Yukawa_texture_NOT_ALLOWED.json",fY)
    summary={
        "status":STATUS,
        "original_B4_scalar_EWPO_inputs":5557,
        "source_E1_original_10TeV_RGE_pass":EXPECTED_RGE,
        "source_E1_vacuum_cases_reused":EXPECTED_OLD,
        "new_E2_vacuum_cases_completed":EXPECTED_REMAINING,
        "all_RGE_qualified_original_potentials_vacuum_evaluated":len(allcases),
        "explicit_deeper_tree_vacuum_witnesses":len(witnesses),
        "no_deeper_tree_vacuum_witness_found":len(no_witness),
        "top100_mass_diverse_diagnostic_shortlist":len(top_ids),
        "all_survivors_in_source_CSV_not_just_top100":True,
        "single_neutrino_texture_not_full_Zee_scan":True,
        "global_tree_vacuum_certified":False,
        "full_Zee_experimental_allowed_or_excluded":None,
        "remaining_missing_physics":
            list(EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED),
        "E1_source_hashes":data["hashes"],
        "E1_original_RGE_source_SHA256":data["q4_RGE_source_sha256"],
        "C5_optimizer_params":params,
        "output_SHA256":{p.name:digest(p)
                         for p in output.glob("E2_*")
                         if p.is_file()},
    }
    write_json(output/"summary.json",summary)
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--campaign-dir",type=Path,default=DEFAULT_CAMPAIGN)
    p.add_argument("--postscan-result",type=Path,default=DEFAULT_POSTSCAN)
    p.add_argument("--e1-dir",type=Path,required=True)
    p.add_argument("--generator-output",type=Path,default=DEFAULT_GENERATOR)
    p.add_argument("--q4v13-report",type=Path,default=DEFAULT_Q4_REPORT)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--vacuum-multistarts",type=int,default=128)
    p.add_argument("--vacuum-maxiter",type=int,default=1000)
    p.add_argument("--seed",type=int,default=20261020)
    p.add_argument("--resume",action="store_true")
    a=p.parse_args()
    if a.vacuum_multistarts!=128 or a.vacuum_maxiter!=1000 or a.seed!=20261020:
        p.error("E2 must reproduce original E1 C5 vacuum settings exactly")
    if not BASE.resolve().is_relative_to(Path("/home")):
        p.error("Only execute from a /home source checkout")
    out=a.output_dir.resolve()
    if not out.is_relative_to(BASE.resolve()/"work"):
        p.error("E2 output must be inside /home repo work/")
    if not a.resume and out.exists() and any(out.iterdir()):
        p.error("Refusing to overwrite prior output (use --resume or new directory)")
    if a.resume and not (out/"manifest.json").is_file():
        p.error("Cannot resume without original E2 manifest.json")
    out.mkdir(parents=True,exist_ok=True)
    report={"status":BLOCKED,"full_Zee_experimental_allowed_or_excluded":None}
    try:
        data=load_e1(
            a.campaign_dir.resolve(),a.e1_dir.resolve(),
            a.postscan_result.resolve(),
            a.generator_output.resolve(),a.q4v13_report.resolve())
        params={"vacuum_multistarts":a.vacuum_multistarts,
                "vacuum_maxiter":a.vacuum_maxiter,"seed":a.seed}
        manifest={
            "status":"E2_IN_PROGRESS_NOT_ALLOWED",
            "input_SHA256":data["hashes"],
            "E1_RGE_source_sha256":data["q4_RGE_source_sha256"],
            "settings":params,
            "source_git_HEAD":subprocess.run(
                ["git","rev-parse","HEAD"],cwd=BASE,check=True,
                capture_output=True,text=True).stdout.strip(),
            "full_Zee_experimental_allowed_or_excluded":None}
        if a.resume:
            older=read_json(out/"manifest.json")
            for key in ("input_SHA256","E1_RGE_source_sha256","settings"):
                if older.get(key)!=manifest[key]:
                    raise ValueError("E2 resume source/settings changed: "+key)
            if (out/"summary.json").is_file():
                p.error("Completed E2 result cannot be resumed")
        else:
            write_json(out/"manifest.json",manifest)
        reproduced=check_saved_B2_reference(data)
        print("E2_B2_REFERENCE_REPRODUCED",reproduced,"OF",40,flush=True)
        checkpoint=out/"E2_missing_245_original_B4_vacuum_checkpoint.jsonl"
        old=read_checkpoint(checkpoint,data)
        counts=eval_remaining(data,out,a.vacuum_multistarts,
                              a.vacuum_maxiter,a.seed,old)
        summary=finalize(data,out,old,params)
        manifest["status"]=STATUS
        manifest["summary_sha256"]=digest(out/"summary.json")
        manifest["new_evaluations_this_run"]=counts["newly_evaluated"]
        write_json(out/"manifest.json",manifest)
        print("E2_STATUS",STATUS,
              "ALL_VACUUM_CASES",summary[
                  "all_RGE_qualified_original_potentials_vacuum_evaluated"],
              "NO_DEEPER_WITNESS",summary["no_deeper_tree_vacuum_witness_found"],
              "EXPLICIT_DEEPER_WITNESS",
              summary["explicit_deeper_tree_vacuum_witnesses"],
              "FULL_ZEE_ALLOWED_UNKNOWN",flush=True)
        print("E2_RESULT",out/"summary.json",flush=True)
        return 0
    except Exception as exc:
        report["error"]=repr(exc)
        report["traceback"]=traceback.format_exc()
        write_json(out/"error.json",report)
        print("E2_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
