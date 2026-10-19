#!/usr/bin/env python3
"""One invocation: large Zee candidate discovery + ALL established diagnostic backends.

B4 adaptive scalar/EWPO => B2/B3/B5/Barr-Zee-kernel/A1V/B4C pipeline
=> exact Q4v13 source-pinned C1/C2/C3/C4/C5 => D1 => D2
=> joint candidate/variant evidence table.

This workflow is an EVIDENCE-GATHERING CAMPAIGN, never a globally allowed
Zee scan. There are still NO complete LFV, HiggsTools, complete decay,
global vacuum certificate, or modern NNLO B->Xs-gamma exclusion results.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts"
STATUS = "LARGE_ZEE_EVIDENCE_CAMPAIGN_COMPLETED_NO_ALLOWED_POINT_CLASSIFICATION"
BLOCKED = "LARGE_ZEE_EVIDENCE_CAMPAIGN_BLOCKED_NO_ALLOWED_POINT_CLASSIFICATION"
Q4_SAMPLES = 676
CONFIG = ROOT / "configs/zee_pipeline_partial.json"
DEFAULT_SEEDS = ROOT / "work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv"
DEFAULT_RGE = ROOT / "work/zee_section8_Q4_pyrate_v4/generator_output"
DEFAULT_Q4 = ROOT / "work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json"
UNRESOLVED = {
    "complete_neutrino_oscillation_likelihood": "NOT_VALIDATED",
    "complete_gauge_consistent_CLFV_including_Barr_Zee_mu_e_conversion": "NOT_VALIDATED",
    "model_complete_HiggsTools_predictions_and_direct_searches": "NOT_IMPLEMENTED",
    "matched_modern_two_state_B_to_Xs_gamma_likelihood": "NOT_VALIDATED",
    "full_physical_widths_and_hadronic_cross_sections": "NOT_VALIDATED",
    "mathematical_global_vacuum_certificate": "NOT_ESTABLISHED",
    "full_threshold_matched_RGE_and_quark_flavor_symmetry": "NOT_ESTABLISHED",
}


def digest(path: Path) -> str:
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, indent=2,
                               allow_nan=False)+"\n")


def csv_rows(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        rows=list(csv.DictReader(f))
    if not rows:
        raise ValueError("Empty CSV "+str(path))
    return rows


def unique_ids(rows: list[dict], key: str) -> set:
    ids=[row[key] for row in rows]
    if not all(ids) or len(set(ids))!=len(ids):
        raise ValueError("Missing/duplicated candidate IDs in "+key)
    return set(ids)


def source_preflight(seed: Path, q4report: Path, generator: Path,
                     settings_path: Path) -> dict:
    from gateB4_adaptive_zee_scalar_scan import read_seed_csv
    from zee_gateC1_joined_uv_pilot import find_rges, verify_rge_validation
    from zee_pipeline import settings as verify_settings
    from zee_pipeline import absolute
    from zee_gateF4b_fixed_order_dipole_projector import MASSES
    seeds=read_seed_csv(seed)
    if not seeds:
        raise ValueError("No B1 scalar seeds")
    cfg=verify_settings(settings_path)
    if not cfg["legacy_superiso"]["enabled"]:
        raise ValueError("Large campaign needs A1V legacy diagnostic enabled")
    if cfg["higgstools"]["enabled"] or cfg["full_LFV"]["enabled"] or cfg["modern_b_to_s_gamma"]["enabled"]:
        raise ValueError("Do not enable unvalidated constraints")
    for k in ("vendor_root","a1m_provenance","a1u_result"):
        p=absolute(cfg["legacy_superiso"][k])
        if not p.is_file() and not p.is_dir():
            raise FileNotFoundError("Missing existing A1V source dependency: "+str(p))
    rge=find_rges(generator)
    check=verify_rge_validation(q4report,rge)
    if check.get("Q4v13_numeric_comparisons_passed")!=Q4_SAMPLES:
        raise ValueError("Full complex one-loop RGE source verification missing")
    return {
        "seed_count":len(seeds),"seed_sha256":digest(seed),
        "q4_source":str(rge),"q4_rge_sha256":digest(rge),
        "q4_validation_sha256":digest(q4report),
        "q4_comparisons":Q4_SAMPLES,
        "legacy_A1V_diagnostic_not_modern_likelihood":True,
        "unused_F4b_TypeII_benchmarks_explicitly_not_Zee_constraints":
            list(MASSES),
    }


def build_campaign_settings(src: Path, dst: Path,
                            trials: int, top: int) -> dict:
    s=read_json(src)
    s["neutrino_partial_LFV"]={
        "trials_per_candidate":trials,"top":top,
        "random_seed":20261014}
    # The old optional Barr-Zee subset is still only preliminary. Enable
    # its explicitly diagnostic output but NEVER use it as a veto.
    s["barr_zee_fermion_photon_subset"]["enabled"]=True
    s["higgstools"]["enabled"]=False
    s["full_LFV"]["enabled"]=False
    s["modern_b_to_s_gamma"]["enabled"]=False
    write_json(dst,s)
    from zee_pipeline import settings as check
    check(dst)
    return s


def expect_stage(stage: str, report: dict, cohort: int,
                 roots: int, variants: int) -> dict:
    """Fail closed on wrong status or silently shortened source cohort."""
    spec={
        "B4":("GATE_B4_ADAPTIVE_ZEE_SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED",
              "diverse_shortlist_size",cohort),
        "PIPELINE":("PARTIAL_DIAGNOSTICS_COMPLETE_NOT_ALLOWED",
                    "input_candidate_count",cohort),
        "C1":("GATE_C1_JOINT_ZEE_MODEL_ONE_LOOP_UV_DIAGNOSTIC_NOT_ALLOWED",
              "row_count",cohort),
        "C2":("GATE_C2_PAIRED_ZEE_SCALAR_RESCUE_ONE_LOOP_DIAGNOSTIC_NOT_ALLOWED",
              "tested_interventions",cohort*variants),
        "C3":("GATE_C3_COMPLEX_QUARTIC_RUNNING_BFB_DIAGNOSTIC_NOT_ALLOWED",
              "tested",cohort*2),
        "C4":("GATE_C4_FULL_COMPLEX_55CHANNEL_RUNNING_SCALAR_UNITARITY_NOT_ALLOWED",
              "tested",cohort*2),
        "C5":("GATE_C5_NUMERICAL_FULL_ZEE_CHARGE_BREAKING_VACUUM_NOT_ALLOWED",
              "tested",cohort*2),
        "D1":("GATE_D1_AVAILABLE_B2_JOINT_ZEE_NEUTRINO_LFV_PARTIAL_DIAGNOSTIC_NOT_ALLOWED",
              "B2_total_saved_solutions",cohort*roots),
        "D2":("GATE_D2_NEUTRINO_EXACT_PARTIAL_LFV_OPTIMIZATION_NOT_ALLOWED",
              "tested_spectra",None),
    }
    status,key,expected=spec[stage]
    if report.get("status")!=status:
        raise ValueError(f"{stage} source status unexpected: "+str(report.get("status")))
    if expected is not None and report.get(key)!=expected:
        raise ValueError(f"{stage} {key} expected {expected}, found {report.get(key)}")
    if stage=="D2" and not(1<=report.get(key,0)<=cohort):
        raise ValueError("D2 tested spectra count invalid")
    if stage=="B4" and not(
        report.get("distinct_screened_parameter_bins",0)>=cohort
        and report.get("n_physically_allowed_points") is None):
        raise ValueError("B4 did not supply enough distinct candidates")
    if stage=="PIPELINE":
        if report.get("full_model_allowed_points") is not None:
            raise ValueError("PIPELINE incorrectly classified full-model allowed points")
        required=("neutrino_and_partial_LFV","general_Zee_leptonic_widths",
                  "extended_partial_LFV_3lepton_universality",
                  "barr_zee_fermion_loop_kernels_NO_amplitudes",
                  "barr_zee_fermion_photon_amplitudes_PRELIMINARY",
                  "SuperIso_legacy_two_charged","joint_provenance_audit")
        for k in required:
            if report.get("stages",{}).get(k,{}).get("status")!=(
                    "DIAGNOSTIC_COMPLETE_NOT_EXCLUSION"):
                raise ValueError("Incomplete pipeline stage "+k)
    for k in ("physical_allowed","physical_Zee_allowed",
              "physical_Zee_allowed_points","full_model_allowed_points"):
        if report.get(k,"NOT_LISTED") not in ("NOT_LISTED",None,"UNKNOWN"):
            raise ValueError("Physics acceptance unexpectedly claimed in "+stage)
    return {"status":status,"validated_cohort_count":report.get(key)}


def run_stage(stage, cmd, out, expect, manifest, logroot):
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"{stage}: nonempty output directory, refusing overwrite")
    logfile=logroot/(stage+".log")
    print("LARGE_SCAN_STAGE",stage,"START",flush=True)
    manifest["current_stage"]=stage
    write_json(logroot/"manifest.json",manifest)
    with logfile.open("w") as fh:
        proc=subprocess.run(cmd,cwd=ROOT,stdout=fh,
                            stderr=subprocess.STDOUT,check=False)
    record={"command":cmd,"log":str(logfile),
            "returncode":proc.returncode,
            "expected_report":str(expect)}
    manifest["stages"][stage]=record
    if proc.returncode:
        record["status"]="FAILED"
        write_json(logroot/"manifest.json",manifest)
        tail="\n".join(logfile.read_text(errors="replace").splitlines()[-35:])
        raise RuntimeError(f"{stage} failed with exit {proc.returncode}:\n"+tail)
    if not expect.is_file():
        record["status"]="MISSING_REPORT"
        write_json(logroot/"manifest.json",manifest)
        raise ValueError(stage+" did not create expected report: "+str(expect))
    report=read_json(expect)
    from zee_gateC2_paired_uv_rescue import VARIANTS
    information=expect_stage(stage,report,
                             manifest["cohort_size"],
                             manifest["roots_per_spectrum"],len(VARIANTS))
    record.update(information)
    record["sha256"]=digest(expect)
    record["status"]="VERIFIED_DIAGNOSTIC_NOT_EXCLUSION"
    write_json(logroot/"manifest.json",manifest)
    print("LARGE_SCAN_STAGE",stage,"PASS",information["validated_cohort_count"],
          "NOT_ALLOWED",flush=True)
    return report


def scalar_theory_available(d1: dict) -> int:
    # This is only a diagnostic shortlist: C4 sampled-running checks and
    # absence of an explicit deeper C5 tree vacuum witness.
    model=d1.get("model_variant_status",{})
    n=sum(any(bool(v["scalar_only_candidate_for_further_flavor_work"])
              for v in variants.values()) for variants in model.values())
    return n


def synthesize(root: Path, shortlist: Path, pipe: Path,
               c4: dict, c5: dict, d1: dict, d2: dict | None,
               roots: int) -> dict:
    joined=csv_rows(pipe/"B4C_joint_audit"/
                    "joint_scalar_neutrino_width_flavour_NOT_ALLOWED.csv")
    original=csv_rows(shortlist)
    ids=unique_ids(original,"id")
    if unique_ids(joined,"candidate_id")!=ids or len(ids)!=30:
        raise ValueError("Joined campaign IDs inconsistent with selected B4 shortlist")
    c4rows=c4["cases"]
    c5rows=c5["rows"]
    if not (len(c4rows)==len(c5rows)==60):
        raise ValueError("Expected precisely 60 C4 and C5 case records")
    cases4={(x["candidate_id"],x["variant"]):x for x in c4rows}
    cases5={(x["candidate_id"],x["variant"]):x for x in c5rows}
    if len(cases4)!=60 or set(cases4)!=set(cases5):
        raise ValueError("C4/C5 mismatched candidate or potential-variant cases")
    d2rows={r["candidate_id"]:r for r in (d2 or {}).get("rows",[])}
    if not set(d2rows).issubset(ids):
        raise ValueError("D2 contains unknown candidate")
    byid={r["candidate_id"]:r for r in joined}
    variants=sorted(set(k[1] for k in cases4))
    summaries=[]
    detailed=[]
    for cand in sorted(ids):
        src=byid[cand]
        good=[]
        deeper=0
        for var in variants:
            c4case=cases4[cand,var]
            c5case=cases5[cand,var]
            witness=bool(c5case["C5_deeper_witness"])
            running=bool(c4case["both_running_theory_screens_pass"])
            if witness:deeper+=1
            if running and not witness:good.append(var)
            detailed.append({
                "candidate_id":cand,"variant":var,
                "C4_running_theory_screen_pass":running,
                "C5_explicit_deeper_vacuum_witness":witness,
                "C5_absence_of_witness_is_global_vacuum_proof":False,
                "variant_feasible_for_unvalidated_flavor_followup":
                    running and not witness,
                "Zee_physical_allowed":None})
        rec={
            "candidate_id":cand,
            "mH1_GeV":float(src["mH1"]),
            "mH2_GeV":float(src["mH2"]),
            "gamma":float(src["gamma"]),
            "tanbeta":float(src["tanbeta"]),
            "B4_cascade_upper_proxy_not_cross_section":
                float(src["b4_nonleptonic_cascade_proxy"]),
            "B3_cascade_median_included_LO_channels_only":
                float(src["B3_cascade_proxy_median"]),
            "B3_H2_H1Z_median_included_LO_channels_only":
                float(src["B3_BR_H2_H1Z_median"]),
            "B3_H1_tb_median_included_LO_channels_only":
                float(src["B3_BR_H1_tb_median"]),
            "B2_solutions_saved":int(src["n_B2_flavour_solutions"]),
            "best_partial_LFV_score_NOT_A_LIKELIHOOD":
                float(src["min_partial_LFV_score_NOT_EXCLUSION"]),
            "D2_optimized_partial_score_NOT_A_LIKELIHOOD":
                None if cand not in d2rows else float(
                    d2rows[cand]["new_best_partial_score_NOT_EXCLUSION"]),
            "sampled_RGE_BFB_tree_unitarity_and_no_deeper_witness_variants":
                ";".join(good),
            "num_diagnostic_variants_for_followup":len(good),
            "num_explicit_deeper_tree_vacuum_witness_variants":deeper,
            "legacy_SuperIso_BR_NOT_EXCLUSION":
                float(src["legacy_SuperIso_full_Zee_BR"]),
            "full_Zee_experimental_allowed":None,
            "physical_sigma_pp_tbH2_not_calculated":True,
        }
        if rec["B2_solutions_saved"]!=roots:
            raise ValueError("Per-spectrum B2 roots count mismatch")
        if not all(math.isfinite(v) for v in rec.values()
                   if isinstance(v,float)):
            raise ValueError("Nonfinite joined output")
        summaries.append(rec)
    summaries.sort(key=lambda x:(
        x["num_diagnostic_variants_for_followup"]==0,
        -x["B3_cascade_median_included_LO_channels_only"]))
    summary={
        "status":STATUS,
        "number_scalar_candidates":len(ids),
        "number_paired_running_and_vacuum_cases":len(detailed),
        "number_diagnostic_candidates_for_further_constraints":
            sum(r["num_diagnostic_variants_for_followup"]>0 for r in summaries),
        "number_candidates_with_explicit_deeper_tree_witness_in_all_tested_variants":
            sum(r["num_explicit_deeper_tree_vacuum_witness_variants"]==len(variants)
                for r in summaries),
        "number_physically_allowed_Zee_points":None,
        "number_physically_excluded_Zee_points_by_complete_global_likelihood":None,
        "admissible_hypothesis_test":"NOT_AVAILABLE",
        "selection_is_adaptive_NOT_global_prior":True,
        "C5_no_witness_does_NOT_prove_global_vacuum":True,
        "all_missing_constraints":UNRESOLVED,
        "all_artifacts_are_partial_diagnostics":True,
    }
    a=root/"joined_30_scalar_campaign_prioritization_NOT_ALLOWED.csv"
    with a.open("w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(summaries[0]))
        w.writeheader();w.writerows(summaries)
    b=root/"joint_60_scalar_running_vacuum_variants_NOT_ALLOWED.csv"
    with b.open("w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(detailed[0]))
        w.writeheader();w.writerows(detailed)
    summary["joined_candidate_csv"]=str(a)
    summary["joint_variant_csv"]=str(b)
    summary["joined_candidate_csv_sha256"]=digest(a)
    summary["joint_variant_csv_sha256"]=digest(b)
    write_json(root/"campaign_result.json",summary)
    return summary


def make_parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed-csv",type=Path,default=DEFAULT_SEEDS)
    p.add_argument("--generator-output",type=Path,default=DEFAULT_RGE)
    p.add_argument("--q4v13-report",type=Path,default=DEFAULT_Q4)
    p.add_argument("--settings",type=Path,default=CONFIG)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--steps",type=int,default=20000)
    p.add_argument("--chains",type=int,default=16)
    p.add_argument("--top",type=int,default=30)
    p.add_argument("--neutrino-trials",type=int,default=300)
    p.add_argument("--flavor-top",type=int,default=5)
    p.add_argument("--uv-steps",type=int,default=24)
    p.add_argument("--vacuum-starts",type=int,default=128)
    p.add_argument("--vacuum-maxiter",type=int,default=1000)
    p.add_argument("--d2-max-evals",type=int,default=240)
    p.add_argument("--skip-regression-suite",action="store_true")
    return p


def main() -> int:
    ap=make_parser()
    args=ap.parse_args()
    if (not 1200<=args.steps<=200000 or not 2<=args.chains<=128 or
        args.top!=30 or not 5<=args.flavor_top<=10 or
        args.flavor_top>args.neutrino_trials or
        args.neutrino_trials>50000 or
        not 8<=args.uv_steps<=96 or args.uv_steps%4 or
        not 64<=args.vacuum_starts<=1024 or
        not 200<=args.vacuum_maxiter<=6000 or
        not 80<=args.d2_max_evals<=2000):
        ap.error("Invalid campaign contract; C1/C2/C3/C4/C5/D1 require 30 points")
    if not ROOT.resolve().is_relative_to(Path("/home")):
        ap.error("Execute only from the /home source checkout")
    out=args.output_dir.resolve()
    if not out.is_relative_to(ROOT.resolve()/"work"):
        ap.error("Campaign outputs must be in /home checkout work/")
    if out.exists() and any(out.iterdir()):
        ap.error("Refuse nonempty campaign output. Prior diagnostics are immutable.")
    manifest={
        "status":BLOCKED,"created_utc":datetime.now(timezone.utc).isoformat(),
        "physical_Zee_allowed":None,"unresolved":UNRESOLVED,
        "cohort_size":args.top,"roots_per_spectrum":args.flavor_top,
        "settings":{"steps":args.steps,"chains":args.chains,
                    "neutrino_trials":args.neutrino_trials,
                    "uv_steps":args.uv_steps,
                    "vacuum_starts":args.vacuum_starts},
        "stages":{}}
    out.mkdir(parents=True,exist_ok=True)
    result={"status":BLOCKED,"physical_Zee_allowed":None}
    try:
        for name,path in [("seed_csv",args.seed_csv),
                          ("generator_output",args.generator_output),
                          ("Q4v13_report",args.q4v13_report),
                          ("settings",args.settings)]:
            if not path.exists():
                raise FileNotFoundError(name+": "+str(path))
        seed=args.seed_csv.resolve()
        rge=args.generator_output.resolve()
        q4=args.q4v13_report.resolve()
        cfg_path=args.settings.resolve()
        manifest["preflight"]=source_preflight(seed,q4,rge,cfg_path)
        git=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,
                           check=True,text=True,capture_output=True)
        manifest["zee_git_head"]=git.stdout.strip()
        configs=out/"campaign_partial_constraints_config.json"
        build_campaign_settings(cfg_path,configs,
                                args.neutrino_trials,args.flavor_top)
        manifest["campaign_config_sha256"]=digest(configs)
        write_json(out/"manifest.json",manifest)
        python=sys.executable
        def py(name,*params):
            return [python,str(SCRIPT/name),*[str(x) for x in params]]
        if not args.skip_regression_suite:
            tests=[
                "test_gateB4_adaptive_zee_scalar_scan.py",
                "test_gateB2_zee_neutrino_family_scan.py",
                "test_gateB3_general_zee_charged_lepton_widths.py",
                "test_gateB4c_joined_candidate_audit.py",
                "test_zee_pipeline.py",
                "test_zee_gateC1_joined_uv_pilot.py",
                "test_zee_gateC2_paired_uv_rescue.py",
                "test_zee_gateC3_running_complex_bfb.py",
                "test_zee_gateC4_running_55channel_unitarity.py",
                "test_zee_gateC5_charge_breaking_vacuum_search.py",
                "test_zee_gateD1_joint_300_neutrino_lfv_inventory.py",
                "test_zee_gateD2_neutrino_exact_partial_LFV_optimization.py",
            ]
            log=out/"source_regressions.log"
            with log.open("w") as f:
                for pattern in tests:
                    cmd=[python,"-m","unittest","discover","-s","tests",
                         "-p",pattern,"-v"]
                    p=subprocess.run(cmd,cwd=ROOT,stdout=f,
                                     stderr=subprocess.STDOUT,check=False)
                    f.flush()
                    if p.returncode:
                        raise RuntimeError(f"Regression suite {pattern} failed; see {log}")
            manifest["regressions"]={"status":"PASS",
                                     "tested_modules":tests,"log":str(log),
                                     "sha256":digest(log)}
            write_json(out/"manifest.json",manifest)
        else:
            manifest["regressions"]={"status":"NOT_RUN_EXPLICITLY_SKIPPED"}
            write_json(out/"manifest.json",manifest)
        # 1. Produce 30 fresh scalar/EWPO candidates from a 20,000-proposal
        # adapted B4 exploration. This is biased discovery, not statistical sampling.
        b4=out/"B4_adaptive"
        b4r=run_stage("B4",py("gateB4_adaptive_zee_scalar_scan.py",
            "--seed-csv",seed,"--steps",args.steps,"--chains",args.chains,
            "--top",args.top,"--quadrature-nodes",96,"--adapt-every",200,
            "--random-seed",20261020,"--output-dir",b4),
            b4,b4/"summary.json",manifest,out)
        selected=b4/"diverse_candidates_for_B2_NOT_ALLOWED.csv"
        if len(csv_rows(selected))!=args.top:
            raise ValueError("B4 shortlist not precisely 30 candidates")
        # 2. Single already-integrated neutrino, widths, partial LFV,
        # source-pinned legacy quark-flavor and provenance join.
        pipe=out/"partial_constraint_pipeline"
        pipereport=run_stage("PIPELINE",py("zee_pipeline.py",
            "--points",selected,"--settings",configs,"--output-dir",pipe),
            pipe,pipe/"manifest.json",manifest,out)
        b2=pipe/"B2_neutrino"/"top_neutrino_Yukawa_matrices_NOT_ALLOWED.json"
        b2json=read_json(b2)
        if set(b2json)!=unique_ids(csv_rows(selected),"id"):
            raise ValueError("B2 scalar identifier coverage not complete")
        if any(len(values)!=args.flavor_top for values in b2json.values()):
            raise ValueError("B2 returned fewer than requested Yukawa roots")
        generator=args.generator_output.resolve()
        common=["--b4-csv",selected,"--b2-json",b2]
        rgeargs=["--generator-output",generator,"--q4v13-report",q4]
        c1=out/"C1_model_RGE"
        run_stage("C1",py("zee_gateC1_joined_uv_pilot.py",
            *common,*rgeargs,"--top-candidates",args.top,
            "--solutions-per-candidate",1,"--steps",args.uv_steps,
            "--upper-GeV",10000,"--output-dir",c1),
            c1,c1/"summary.json",manifest,out)
        c2=out/"C2_paired_UV"
        run_stage("C2",py("zee_gateC2_paired_uv_rescue.py",
            *common,*rgeargs,"--c1-cohort-summary",c1/"summary.json",
            "--max-spectra",args.top,"--steps",args.uv_steps,
            "--upper-GeV",10000,"--output-dir",c2),
            c2,c2/"summary.json",manifest,out)
        c3=out/"C3_complex_BFB"
        run_stage("C3",py("zee_gateC3_running_complex_bfb.py",
            *common,*rgeargs,"--c2-summary",c2/"summary.json",
            "--max-spectra",args.top,"--steps",args.uv_steps,
            "--orbit-samples",2048,"--upper-GeV",10000,
            "--output-dir",c3),c3,c3/"summary.json",manifest,out)
        c4=out/"C4_55channel_unitarity"
        c4report=run_stage("C4",py("zee_gateC4_running_55channel_unitarity.py",
            *common,*rgeargs,"--c2-summary",c2/"summary.json",
            "--c3-summary",c3/"summary.json","--max-spectra",args.top,
            "--steps",args.uv_steps,"--orbit-samples",2048,
            "--upper-GeV",10000,"--output-dir",c4),
            c4,c4/"summary.json",manifest,out)
        c5=out/"C5_charge_breaking_vacuum"
        c5report=run_stage("C5",py("zee_gateC5_charge_breaking_vacuum_search.py",
            *common,"--c2-summary",c2/"summary.json",
            "--c3-summary",c3/"summary.json","--c4-summary",c4/"summary.json",
            "--max-spectra",args.top,"--multistart",args.vacuum_starts,
            "--maxiter",args.vacuum_maxiter,"--seed",20261020,
            "--output-dir",c5),c5,c5/"summary.json",manifest,out)
        d1=out/"D1_joint_partial_LFV"
        d1report=run_stage("D1",py("zee_gateD1_joint_300_neutrino_lfv_inventory.py",
            *common,"--c2-summary",c2/"summary.json",
            "--c3-summary",c3/"summary.json","--c4-summary",c4/"summary.json",
            "--c5-summary",c5/"summary.json","--output-dir",d1),
            d1,d1/"summary.json",manifest,out)
        good=scalar_theory_available(d1report)
        if good:
            d2=out/"D2_neutrino_partial_LFV_optimization"
            d2report=run_stage("D2",
                py("zee_gateD2_neutrino_exact_partial_LFV_optimization.py",
                   *common,"--c2-summary",c2/"summary.json",
                   "--c3-summary",c3/"summary.json","--c4-summary",c4/"summary.json",
                   "--c5-summary",c5/"summary.json","--d1-summary",d1/"summary.json",
                   "--max-spectra",min(good,args.top),
                   "--starts-per-spectrum",2,"--max-evals",args.d2_max_evals,
                   "--output-dir",d2),
                d2,d2/"summary.json",manifest,out)
        else:
            d2report=None
            manifest["stages"]["D2"]={
                "status":"NOT_RUN_NO_SCALAR_C4_C5_DIAGNOSTIC_SURVIVORS",
                "physical_allowed":None}
            write_json(out/"manifest.json",manifest)
        result=synthesize(out,selected,pipe,c4report,c5report,
                          d1report,d2report,args.flavor_top)
        result["source_git_head"]=manifest["zee_git_head"]
        result["input_b1_seed_sha256"]=digest(seed)
        result["validated_Q4v13_source_sha256"]=manifest["preflight"]["q4_rge_sha256"]
        write_json(out/"campaign_result.json",result)
        manifest["status"]=STATUS
        manifest["current_stage"]=None
        manifest["campaign_result_sha256"]=digest(out/"campaign_result.json")
        write_json(out/"manifest.json",manifest)
        print("ZEE_LARGE_CAMPAIGN_STATUS",STATUS,flush=True)
        print("ZEE_DIAGNOSTIC_CANDIDATES",
              result["number_diagnostic_candidates_for_further_constraints"],
              "OF",args.top,flush=True)
        print("ZEE_FULL_ALLOWED_POINTS UNKNOWN",flush=True)
        print("ZEE_CAMPAIGN_SUMMARY",out/"campaign_result.json",flush=True)
        return 0
    except Exception as exc:
        manifest["status"]=BLOCKED
        manifest["error"]=repr(exc)
        manifest["error_traceback"]=traceback.format_exc()
        write_json(out/"manifest.json",manifest)
        print("ZEE_LARGE_CAMPAIGN_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
