#!/usr/bin/env python3
"""Zee Priority-1 pipeline entrypoint; no fake model exclusions.

Runs cheap structural/physics bookkeeping over scalar candidates, joins
optional external *actual calculated* source artifacts, and invokes the
real HiggsTools Python bindings only when ALL five-state widths and
hadronic production modes pass completeness contracts.

This is deliberately small. Do not use it as a NNLO or full LFV engine.
"""
from __future__ import annotations
import argparse,collections,json,sys,traceback
from pathlib import Path
from zee_priority1_contracts import (
 REQUIRED,STATUS,hashfile,load_export,read_points,evaluate)
from zee_priority1_higgstools import run as run_higgstools

def save(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True,
                                     allow_nan=False)+"\n")

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--points",type=Path,required=True,
                    help="Original B4 scalar/EWPO candidate CSV, NOT automatically rescreened")
    ap.add_argument("--out",type=Path,required=True,
                    help="New, non-overwriting results directory")
    for stage in REQUIRED:
        ap.add_argument("--"+stage,type=Path,
                        help="Source-generated stage export JSON, schema v1")
    ap.add_argument("--higgsbounds-data",type=Path)
    ap.add_argument("--higgssignals-data",type=Path)
    ap.add_argument("--require-all-inputs",action="store_true")
    ap.add_argument("--dry-run",action="store_true")
    ap.add_argument("--stream-coverage",action="store_true",
                    help="Read millions of CSV/JSONL points sequentially with disk-backed ID checking; no full physics exclusions")
    ap.add_argument("--scalar-physics",action="store_true",
                    help="With --stream-coverage, actually run original GateB4 scalar BFB/unitarity and correlated STU screens")
    a=ap.parse_args(argv)
    if bool(a.higgsbounds_data)!=bool(a.higgssignals_data):
        ap.error("HiggsBounds and HiggsSignals datasets must be specified together")
    if a.stream_coverage:
        if (any(getattr(a,stage) is not None for stage in REQUIRED)
            or a.higgsbounds_data or a.higgssignals_data
            or a.require_all_inputs):
            ap.error("stream-coverage is structural/scalar-only; external physics exports and datasets require the full nonstreaming evaluator")
        from zee_priority1_streaming import scan
        out=a.out.resolve()
        if out.exists():
            ap.error("Output path must be new; never overwrite prior reports")
        if a.dry_run:
            print("P1_STREAM_PLAN",STATUS,"POINTS",str(a.points),
                  "REAL_SCALAR_PHYSICS",a.scalar_physics)
            return 0
        out.mkdir(parents=True,exist_ok=False)
        try:
            summary=scan(a.points,out/"per_candidate.jsonl",
                         scalar_physics=a.scalar_physics)
            save(out/"summary.json",summary)
            save(out/"manifest.json",{
                "status":summary["status"],
                "summary_sha256":hashfile(out/"summary.json"),
                "canonical_driver_SHA256":hashfile(Path(__file__))})
            print("P1_STREAM_STATUS",summary["status"],"POINTS",
                  summary["original_candidate_count"],"EXCLUSIONS",0)
            print("P1_STREAM_REPORT",out/"summary.json")
            return 0
        except Exception as exc:
            save(out/"error.json",{"status":"P1_STREAM_FAIL_CLOSED",
                 "error":repr(exc),"Zee_allowed_or_excluded":None})
            print("P1_STREAM_ERROR",repr(exc),file=sys.stderr)
            return 1
    if a.scalar_physics:
        ap.error("--scalar-physics currently requires --stream-coverage")
    points=read_points(a.points)
    paths={name:getattr(a,name) for name in REQUIRED}
    if a.require_all_inputs and any(x is None for x in paths.values()):
        ap.error("All 5 independent backend inputs are required in strict mode")
    if a.dry_run:
        print("P1_PLAN",STATUS,"POINTS",len(points),
              "BACKENDS",{k:bool(v) for k,v in paths.items()},
              "REAL_HIGGSTOOLS",bool(a.higgsbounds_data))
        return 0
    out=a.out.resolve()
    if out.exists():
        ap.error("Output path must be new; never overwrite prior reports")
    out.mkdir(parents=True,exist_ok=False)
    try:
        exports={};provenance={}
        for stage,path in paths.items():
            if path is None:continue
            data,ref=load_export(path,stage,points)
            exports[stage]=data
            provenance[stage]={"path":str(path.resolve()),
                "sha256":hashfile(path),"reference":ref}
        results=evaluate(points,exports)
        hb_count=0
        if a.higgsbounds_data:
            if not a.higgsbounds_data.is_dir() or not a.higgssignals_data.is_dir():
                raise ValueError("Official HiggsBounds/HiggsSignals dataset directories required")
            # Cache both large dataset classes ONCE, outside the point loop.
            import Higgs.bounds as HB
            import Higgs.signals as HS
            bounds=HB.Bounds(str(a.higgsbounds_data.resolve()))
            signals=HS.Signals(str(a.higgssignals_data.resolve()))
            for z in results:
                key=z["candidate_id"]
                if not(z["stages"]["decays"].startswith("EVALUATED_") and
                       z["stages"]["production"].startswith("EVALUATED_")):
                    z["higgstools"]="BLOCKED_INCOMPLETE_5STATE_PHYSICS"
                    continue
                z["higgstools"]=run_higgstools(
                    points[key],exports["decays"][key],
                    exports["production"][key],bounds,signals)
                hb_count+=1
        else:
            for z in results:z["higgstools"]="NOT_RUN_NO_DATASET_REQUESTED"
        with (out/"per_candidate.jsonl").open("w") as f:
            for row in results:
                f.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
        counts={stage:dict(collections.Counter(r["stages"][stage]
                              for r in results)) for stage in REQUIRED}
        report={
          "status":STATUS,
          "points":len(points),
          "per_candidate_higgstools_API_calls":hb_count,
          "per_component_status_counts":counts,
          "full_Zee_model_allowed_or_excluded":None,
          "unimplemented_physics_gates":[
             "true full NNLO two-charged B->Xs gamma calculation in original model",
             "complete interfering one/two-loop Zee LFV plus nuclear conversion",
             "both-ordering calibrated neutrino global likelihood",
             "model-consistent complete heavy neutral and charged widths",
             "validated five-state hadronic production amplitudes/cross sections",
             "modern likelihood correlations, vacuum and RG matching"],
          "no_automatic_approval_or_exclusion_from_external_flags":True,
          "input_source":{
            "points_path":str(a.points.resolve()),
            "points_sha256":hashfile(a.points),
            "point_is_previously_scalar_EWPO_screened_not_rescreened":True},
          "backend_exports":provenance,
          "HiggsTools_used":bool(a.higgsbounds_data),
          "HiggsTools_dataset_paths":{
            "HB":str(a.higgsbounds_data.resolve()) if a.higgsbounds_data else None,
            "HS":str(a.higgssignals_data.resolve()) if a.higgssignals_data else None},
          "outputs":{"per_candidate_sha256":hashfile(out/"per_candidate.jsonl")},
        }
        save(out/"summary.json",report)
        save(out/"manifest.json",{
             "status":STATUS,"summary_sha256":hashfile(out/"summary.json"),
             "driver_sha256":hashfile(Path(__file__))})
        print("P1_STATUS",STATUS,"POINTS",len(points),
              "HIGGSTOOLS_API_CALLS",hb_count,flush=True)
        for stage in REQUIRED:
            print("P1_GATE",stage,counts[stage],flush=True)
        print("P1_FULL_MODEL_ALLOWED_OR_EXCLUDED",None,flush=True)
        print("P1_REPORT",out/"summary.json",flush=True)
        return 0
    except Exception as exc:
        save(out/"error.json",{
            "status":"P1_FAIL_CLOSED_NOT_MODEL_EXCLUSION",
            "error":repr(exc),"traceback":traceback.format_exc(),
            "Zee_allowed_or_excluded":None})
        print("P1_ERROR",repr(exc),file=sys.stderr,flush=True)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
