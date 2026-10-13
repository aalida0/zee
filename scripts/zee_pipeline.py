#!/usr/bin/env python3
"""Single-entry Zee constraint orchestration; NEVER a full-model acceptance.

Runs validated project modules as subprocesses, records inputs, logs and
provenance. It DOES NOT implement physical calculations itself.

Currently wired: B2 algebraic neutrino+partial LFV, B3 general Zee
leptonic widths, B5 mu->3e/tau->3lepton neutral trees and f-only
universality, A1V audited legacy SuperIso and B4C strict results join.
Not wired: full LFV likelihood, 2026 NNLO B->Xs gamma exclusion,
complete Zee HiggsTools prediction adapter, true hadronic cross sections.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

STATUS="ZEE_PIPELINE_PARTIAL_DIAGNOSTICS_ONLY_NOT_ALLOWED"
SOURCE=Path(__file__).resolve().parent
BASE=SOURCE.parent
REQUIRED=("id","mH1","mH2","mh2","ma","alpha","beta",
          "gamma","m12sq","tanbeta")
FOUR=("mH1","mH2","gamma","tanbeta")
STAGES=(
    "neutrino_and_partial_LFV","general_Zee_leptonic_widths",
    "extended_partial_LFV_3lepton_universality",
    "barr_zee_fermion_loop_kernels_NO_amplitudes",
    "SuperIso_legacy_two_charged","joint_provenance_audit")


def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def safe_json(path):
    return json.loads(Path(path).read_text())


def validate_points(path):
    """Input = already scalar/EWPO-screened B1/B4 candidates, not raw draws."""
    with Path(path).open(newline="") as handle:
        reader=csv.DictReader(handle)
        if not reader.fieldnames or any(k not in reader.fieldnames
                                       for k in REQUIRED):
            raise ValueError("Input must be a B1/B4 screened Zee candidate CSV, "
                             "with "+", ".join(REQUIRED))
        ids=set()
        records=[]
        for r in reader:
            ident=r["id"]
            if not ident or ident in ids:
                raise ValueError("Missing/duplicate scalar candidate ID")
            ids.add(ident)
            if "candidate_status" in r and (
                    "NOT_ALLOWED" not in r["candidate_status"]):
                raise ValueError("Input candidates must be explicitly unclassified")
            vals={k:float(r[k]) for k in REQUIRED if k!="id"}
            if not all(math.isfinite(x) for x in vals.values()):
                raise ValueError(f"Nonfinite scalar parameter at {ident}")
            if not (vals["mH1"]>0 and vals["mH2"]>vals["mH1"]
                    and vals["mh2"]>0 and vals["ma"]>0
                    and 0<vals["beta"]<math.pi/2
                    and 0<vals["gamma"]<math.pi/2
                    and vals["tanbeta"]>0):
                raise ValueError(f"Invalid scalar input at {ident}")
            if not math.isclose(vals["tanbeta"],math.tan(vals["beta"]),
                                rel_tol=1e-7,abs_tol=1e-9):
                raise ValueError(f"Inconsistent tanbeta and beta at {ident}")
            records.append(r)
    if not records:raise ValueError("No scalar points")
    return records


def settings(path):
    cfg=safe_json(path)
    if cfg.get("schema_version")!=1:
        raise ValueError("Unknown pipeline settings schema")
    n=cfg.get("neutrino_partial_LFV",{})
    if not isinstance(n,dict):
        raise ValueError("Invalid neutrino stage")
    trials=n.get("trials_per_candidate",100)
    top=n.get("top",5)
    if not (isinstance(trials,int) and 1<=trials<=50000
            and isinstance(top,int) and 1<=top<=1000
            and top<=trials):
        raise ValueError("Invalid neutrino sampling config")
    if cfg.get("higgstools",{}).get("enabled",False):
        raise ValueError(
            "HiggsTools enabled but there is no validated COMPLETE Zee "
            "HiggsPredictions adapter. Fail closed instead of using "
            "partial widths as experimental predictions.")
    if cfg.get("full_LFV",{}).get("enabled",False):
        raise ValueError(
            "Complete LFV requested but only validated partial "
            "one-loop components are implemented. Fail closed.")
    if cfg.get("modern_b_to_s_gamma",{}).get("enabled",False):
        raise ValueError(
            "Modern NNLO-matched two-charged B->Xs gamma "
            "likelihood is not validated. Fail closed.")
    b5=cfg.get("extended_partial_LFV",{})
    if not isinstance(b5,dict) or not isinstance(b5.get("enabled",True),bool):
        raise ValueError("extended_partial_LFV.enabled must be boolean")
    bz=cfg.get("barr_zee_kernel_diagnostic",{})
    if not isinstance(bz,dict) or not isinstance(bz.get("enabled",True),bool):
        raise ValueError("barr_zee_kernel_diagnostic.enabled must be boolean")
    legacy=cfg.get("legacy_superiso",{})
    if not isinstance(legacy,dict):raise ValueError("Invalid legacy SuperIso config")
    if legacy.get("enabled"):
        required=("vendor_root","a1m_provenance","a1u_result")
        if any(not legacy.get(k) for k in required):
            raise ValueError("Legacy SuperIso needs "+", ".join(required))
    return cfg


def absolute(path):
    p=Path(path).expanduser()
    return p if p.is_absolute() else BASE/p


def write_json(path,obj):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")


def run_stage(stage,cmd,expected_output,root,manifest):
    log=root/(stage+".log")
    print("START",stage,"LOG",log,flush=True)
    with log.open("w") as stream:
        proc=subprocess.run(cmd,cwd=BASE,stdout=stream,
                            stderr=subprocess.STDOUT,check=False)
    entry={"status":"ERROR" if proc.returncode else "EXECUTED",
           "log":str(log),"command":cmd,"returncode":proc.returncode,
           "expected_output":str(expected_output)}
    manifest["stages"][stage]=entry
    write_json(root/"manifest.json",manifest)
    if proc.returncode:
        tail=log.read_text(errors="replace").splitlines()[-35:]
        raise RuntimeError(f"{stage} exit {proc.returncode}\n"+
                           "\n".join(tail))
    if not expected_output.exists() or not expected_output.is_file():
        entry["status"]="MISSING_OUTPUT"
        write_json(root/"manifest.json",manifest)
        raise RuntimeError(f"{stage} did not write {expected_output}")
    entry["output_sha256"]=digest(expected_output)
    entry["status"]="DIAGNOSTIC_COMPLETE_NOT_EXCLUSION"
    write_json(root/"manifest.json",manifest)
    print("DONE",stage,"OUTPUT",expected_output,flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--points",type=Path,required=True,
                    help="B1/B4 screened candidate CSV")
    ap.add_argument("--settings",type=Path,
                    default=BASE/"configs/zee_pipeline_partial.json")
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--dry-run",action="store_true")
    a=ap.parse_args()
    points=a.points.resolve()
    settings_path=a.settings.resolve()
    rows=validate_points(points)
    cfg=settings(settings_path)
    out=a.output_dir.resolve()
    legacy=cfg.get("legacy_superiso",{})
    if legacy.get("enabled"):
        for field in ("vendor_root","a1m_provenance","a1u_result"):
            if not absolute(legacy[field]).exists():
                raise FileNotFoundError(
                    f"Missing legacy SuperIso dependency: {field} = "
                    f"{absolute(legacy[field])}")
    if out.exists() and any(out.iterdir()):
        raise ValueError("Use a NEW empty output directory to prevent "
                         "cross-run artifact reuse")
    git=subprocess.run(["git","rev-parse","HEAD"],cwd=BASE,
                       text=True,capture_output=True,check=False)
    code_revision=(git.stdout.strip() if git.returncode==0 else None)
    manifest={
        "status":"RUN_PLAN_PARTIAL_NOT_ALLOWED",
        "zee_code_revision":code_revision,
        "started_utc":datetime.now(timezone.utc).isoformat(),
        "input_candidate_count":len(rows),
        "input_points_path":str(points),"input_sha256":digest(points),
        "settings_path":str(settings_path),
        "settings_sha256":digest(settings_path),
        "python":sys.version.split()[0],
        "stages":{},
        "full_model_allowed_points":None,
        "full_Zee_LFV_likelihood_validated":False,
        "HiggsTools_full_Zee_adapter_validated":False,
        "modern_2026_BtoXs_gamma_exclusion_validated":False,
        "b4_scalar_screen":"INPUT_ONLY_NOT_RECOMPUTED",
    }
    print("STATUS",STATUS)
    print("INPUT_SCALAR_CANDIDATES",len(rows))
    print("HIGGSTOOLS_ZEE_CONSTRAINT blocked_missing_complete_predictions")
    print("COMPLETE_LFV_CONSTRAINT blocked_not_implemented")
    print("MODERN_FLAVOUR_CONSTRAINT blocked_not_validated")
    print("LEGACY_SUPERISO_ENABLED",bool(legacy.get("enabled")))
    print("EXTENDED_PARTIAL_LFV_ENABLED",cfg.get(
        "extended_partial_LFV",{}).get("enabled",True))
    print("BARR_ZEE_LOOP_KERNELS_ONLY_ENABLED",cfg.get(
        "barr_zee_kernel_diagnostic",{}).get("enabled",True))
    if a.dry_run:
        stages=list(STAGES[:2])
        if cfg.get("extended_partial_LFV",{}).get("enabled",True):
            stages.append(STAGES[2])
        if cfg.get("barr_zee_kernel_diagnostic",{}).get("enabled",True):
            stages.append(STAGES[3])
        if legacy.get("enabled"):
            stages+=list(STAGES[4:])
        print("DRY_RUN True")
        print("DRY_RUN_ORDER",",".join(stages))
        return
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/"manifest.json",manifest)
    try:
        b2_dir=out/"B2_neutrino"
        b2_json=b2_dir/"top_neutrino_Yukawa_matrices_NOT_ALLOWED.json"
        n=cfg.get("neutrino_partial_LFV",{})
        trials=n.get("trials_per_candidate",100)
        top=n.get("top",5)
        cmd=[sys.executable,str(SOURCE/"gateB2_zee_neutrino_family_scan.py"),
             "--b1-csv",str(points),"--output-dir",str(b2_dir),
             "--trials-per-candidate",str(trials),"--top",str(top),
             "--seed",str(n.get("random_seed",20261014))]
        run_stage(STAGES[0],cmd,b2_json,out,manifest)
        b2=safe_json(b2_json)
        if set(b2)!={r["id"] for r in rows} or any(
                not b2[i] for i in b2):
            raise ValueError("B2 omitted candidate or returned empty family")
        b3_dir=out/"B3_widths"
        b3_csv=b3_dir/"cascade_width_corrected_NOT_ALLOWED.csv"
        cmd=[sys.executable,str(SOURCE/"gateB3_general_zee_charged_lepton_widths.py"),
             "--b1-csv",str(points),"--b2-json",str(b2_json),
             "--top",str(top),"--output-dir",str(b3_dir)]
        run_stage(STAGES[1],cmd,b3_csv,out,manifest)
        if cfg.get("extended_partial_LFV",{}).get("enabled",True):
            b5_dir=out/"B5_partial_LFV"
            b5_csv=b5_dir/"lfv_partial_3lepton_universality_NOT_ALLOWED.csv"
            cmd=[sys.executable,str(SOURCE/"zee_lfv_backend.py"),
                 "--points",str(points),"--b2-json",str(b2_json),
                 "--output-dir",str(b5_dir)]
            run_stage(STAGES[2],cmd,b5_csv,out,manifest)
        else:
            manifest["stages"][STAGES[2]]={
                "status":"NOT_RUN_DISABLED_BY_CONFIG",
                "not_a_full_lfv_exclusion":True,
            }
        if cfg.get("barr_zee_kernel_diagnostic",{}).get("enabled",True):
            barr_dir=out/"barr_zee_kernel_diagnostics"
            barr_csv=barr_dir/"barr_zee_fermion_photon_kernels_NO_LFV_EXCLUSION.csv"
            cmd=[sys.executable,str(SOURCE/"zee_barr_zee_kernels.py"),
                 "--points",str(points),"--output-dir",str(barr_dir)]
            run_stage(STAGES[3],cmd,barr_csv,out,manifest)
        else:
            manifest["stages"][STAGES[3]]={
                "status":"NOT_RUN_DISABLED_BY_CONFIG",
                "Barr_Zee_dipoles_computed":False,
            }
        if legacy.get("enabled"):
            flavor_inputs=out/"flavour_inputs.csv"
            with flavor_inputs.open("w",newline="") as handle:
                writer=csv.DictWriter(handle,fieldnames=FOUR)
                writer.writeheader()
                writer.writerows({k:row[k] for k in FOUR} for row in rows)
            manifest["flavor_input_sha256"]=digest(flavor_inputs)
            super_dir=out/"A1V_legacy_superiso"
            super_csv=super_dir/"scan_flavour_only.csv"
            cmd=[sys.executable,str(SOURCE/"gateA1v_run_legacy_response.py"),
                 "--vendor-root",str(absolute(legacy["vendor_root"])),
                 "--a1m-provenance",str(absolute(legacy["a1m_provenance"])),
                 "--a1u-result",str(absolute(legacy["a1u_result"])),
                 "--grid-csv",str(flavor_inputs),
                 "--max-points",str(len(rows)),
                 "--skip-scale-diagnostic",
                 "--output-dir",str(super_dir)]
            run_stage(STAGES[4],cmd,super_csv,out,manifest)
            joint_dir=out/"B4C_joint_audit"
            joint_csv=joint_dir/"joint_scalar_neutrino_width_flavour_NOT_ALLOWED.csv"
            cmd=[sys.executable,str(SOURCE/"gateB4c_joined_candidate_audit.py"),
                 "--b4-csv",str(points),"--b2-json",str(b2_json),
                 "--b3-csv",str(b3_csv),"--a1v-csv",str(super_csv),
                 "--output-dir",str(joint_dir)]
            run_stage(STAGES[5],cmd,joint_csv,out,manifest)
            manifest["joint_candidate_table"]=str(joint_csv)
        else:
            for stage in STAGES[4:]:
                manifest["stages"][stage]={
                    "status":"NOT_RUN_MISSING_LEGACY_SUPERISO_CONFIG"}
        manifest["status"]="PARTIAL_DIAGNOSTICS_COMPLETE_NOT_ALLOWED"
    except Exception as exc:
        manifest["status"]="ERROR_FAIL_CLOSED_NOT_ALLOWED"
        manifest["error"]=f"{type(exc).__name__}: {exc}"
        write_json(out/"manifest.json",manifest)
        raise
    write_json(out/"manifest.json",manifest)
    print("PIPELINE_STATUS",manifest["status"])
    print("FULL_ZEE_ALLOWED_POINTS unknown")
    print("MANIFEST",out/"manifest.json")


if __name__=="__main__":
    main()
