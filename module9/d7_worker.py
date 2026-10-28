"""D7 HTCondor worker: scoped scalar + NO inverse closure, no acceptance claims.

Each point is treated independently. Scalar hard FAIL is a scientific screen
result, not a batch failure. A computational exception is EVALUATION_ERROR
and MUST NOT be counted as a rejected physics point. Vacuum, LFV, true NuFIT,
quark-flavor physical filter and collider production are NOT executed.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import importlib.metadata
import importlib.util
from datetime import datetime, timezone
import sys
import time

import numpy as np
from module1.scalar_constraints import validate_input, reconstruct, check_bfb, unitarity, ewpo
from module2.interface import canonical_hash, scalar_input, evaluate as neutrino_evaluate, strict_loads
from module9.d7_inputs import validate_point, VARIED

STATUS="D7_SCOPED_EVALUATION_ONLY_GLOBAL_UNKNOWN"
SCALAR_GATES=("reconstruction","bfb","unitarity","ewpo")


def evaluate_one(rec):
    if not isinstance(rec,dict) or set(rec)!={"point_id","arm","input_sha256","input"}:
        raise ValueError("Unrecognized D7 input row schema")
    point=rec["input"]
    if not isinstance(point, dict) or not isinstance(rec["arm"], str) or not rec["arm"]:
        raise ValueError("Malformed point input or arm")
    if rec["point_id"]!=point.get("benchmark_id") or rec["input_sha256"]!=canonical_hash(point):
        raise ValueError("Modified input or mismatched benchmark")
    validate_point(point)
    wrapper=point["module2_input"]["scalar"]
    physical,_=scalar_input(wrapper)
    scalar=wrapper["record"]
    _,ew,_,_=validate_input(scalar)
    p,inherited,recon=reconstruct(physical)
    gates={"reconstruction":recon,"bfb":check_bfb(p),
           "unitarity":unitarity(p,inherited),"ewpo":ewpo(physical,ew,scalar["ew_fit"])}
    choices={name:{"assessment":gates[name]["assessment"],
                    "status":gates[name]["status"]} for name in SCALAR_GATES}
    scientific_pass=all(x["assessment"]=="PASS" for x in choices.values())
    result={"point_id":rec["point_id"],"arm":rec["arm"],
       "input_sha256":rec["input_sha256"],"scalar_sha256":wrapper["sha256"],
       "physical":{k:physical[k] for k in ("mH1","mH2","mh2","ma","beta","gamma","alpha","m12sq")},
       "gates":choices,
       "selected_STU":gates["ewpo"]["STU"],
       "reconstruction_residuals":{k:recon[k] for k in (
           "tadpole_max_over_v3", "spectrum_max_relative_residual", "mixing_max_residual_GeV2")},
       "ewpo_chi2":gates["ewpo"]["alternative_fits_not_combined"][scalar["ew_fit"]]["chi2_relative_to_fit_minimum"],
       "unitarity_max_abs_eigenvalue":gates["unitarity"]["max_abs_eigenvalue"],
       "scalar_status":"SCOPED_PASS" if scientific_pass else "SCOPED_FAIL_OR_UNKNOWN",
       "neutrino_status":"NOT_EVALUATED",
       "neutrino_inverse_relative_residual":None,
       "vacuum":"NOT_EVALUATED","COMPLETE_LFV":False,
       "physical_bsgamma":"NOT_EVALUATED",
       "collider_rate":"NOT_EVALUATED","global_zee_acceptance":None, "constraints_complete":False}
    if scientific_pass:
        out=neutrino_evaluate(point["module2_input"])
        if out["benchmark_id"]!=rec["point_id"] or out["status"]!="NEUTRINO_COMPUTED":
            raise ValueError("Inverse neutrino returned an incoherent status")
        inv=out["inverse"]
        err=inv["family_relative_residual"]
        if isinstance(err,bool) or not isinstance(err,(float,int)) or not math.isfinite(err) or not 0 <= err <= 2e-9:
            raise ValueError("Invalid inverse-family neutrino closure")
        result["neutrino_status"]="INVERSE_TARGET_CLOSURE_PASS"
        result["neutrino_inverse_relative_residual"]=float(err)
        # No NuFIT likelihood is implied by reproducing a generated target.
    return result


def run(shard_bytes):
    started=time.monotonic()
    lines=shard_bytes.decode("utf-8").splitlines()
    if not lines or len(lines)>1000:
        raise ValueError("Empty or excessive shard")
    output=[];seen=set();blocked=0
    for line in lines:
        item=strict_loads(line)
        if not isinstance(item,dict) or not isinstance(item.get("point_id"),str):
            raise ValueError("Malformed point identity in shard")
        pid=item["point_id"]
        if pid in seen:raise ValueError("Duplicate point identity within shard")
        seen.add(pid)
        start=time.monotonic()
        try:
            row=evaluate_one(item)
            row["execution_status"]="EVALUATED_SCOPED"
            json.dumps(row, allow_nan=False)
        except (ValueError,TypeError,ArithmeticError,KeyError,np.linalg.LinAlgError) as exc:
            blocked+=1
            row={"point_id":pid,"input_sha256":item.get("input_sha256"),
                 "execution_status":"EVALUATION_ERROR",
                 "scalar_status":"UNKNOWN",
                 "error_type":type(exc).__name__,"error":str(exc)[:500],
                 "global_zee_acceptance":None, "constraints_complete":False}
        row["elapsed_seconds"]=time.monotonic()-start
        output.append(row)
    receipt={"schema_version":"d7-worker-1.0.0","status":STATUS,
      "source_shard_sha256":hashlib.sha256(shard_bytes).hexdigest(),
      "input_count":len(lines),"output_count":len(output),
      "scoped_pass":sum(x.get("scalar_status")=="SCOPED_PASS" for x in output),
      "scoped_fail_or_unknown":sum(x.get("scalar_status")=="SCOPED_FAIL_OR_UNKNOWN" for x in output),
      "evaluation_error":blocked,
      "worker_exit_code":2 if blocked else 0,
      "execution_mode":os.environ.get("ZEE_D7_EXECUTION_MODE", "LOCAL_SIMULATION"),
      "condor_cluster_id":os.environ.get("ZEE_D7_CLUSTER_ID"),
      "condor_proc_id":os.environ.get("ZEE_D7_PROC_ID"),
      "completed_utc":datetime.now(timezone.utc).isoformat(),
      "elapsed_seconds":time.monotonic()-started,
      "peak_rss_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      "platform":platform.platform(),
      "machine":platform.machine(),
      "python_executable":sys.executable,
      "python_executable_sha256":hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
      "environment_setup_sha256":hashlib.sha256((Path(__file__).parent/"condor/environment.sh").read_bytes()).hexdigest(),
      "installed_distribution_inventory_sha256":canonical_hash(sorted(
          (d.metadata["Name"], d.version) for d in importlib.metadata.distributions())),
      "pip_version":importlib.metadata.version("pip") if importlib.util.find_spec("pip") else "UNAVAILABLE",
      "library_versions":{name:importlib.metadata.version(name) for name in ("numpy","scipy","jsonschema","mpmath")},
      "python_version":sys.version.split()[0],
      "numpy_version":np.__version__,
      "execution_host":platform.node(),
      "environment_cvmfs_selected":os.environ.get("ZEE_D7_ENV_ID","NOT_SET"),
      "source_commit":os.environ.get("ZEE_D7_SOURCE_COMMIT","LOCAL_TEST_UNPINNED"),
      "source_bundle_sha256":os.environ.get("ZEE_D7_BUNDLE_SHA256","LOCAL_TEST_UNPINNED"),
      "global_zee_acceptance":None,
      "constraints_complete":False}
    return output,receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--receipt",type=Path,required=True)
    args=parser.parse_args()
    if len({x.resolve() for x in (args.shard,args.output,args.receipt)})!=3:
        raise ValueError("Input/output/receipt paths must differ")
    if args.output.exists() or args.receipt.exists():
        raise ValueError("Refuse existing worker output or receipt")
    raw=args.shard.read_bytes()
    rows,receipt=run(raw)
    result="".join(json.dumps(x,sort_keys=True,allow_nan=False)+"\n" for x in rows)
    receipt["result_bytes_sha256"]=hashlib.sha256(result.encode()).hexdigest()
    for target,body in ((args.output,result),
                        (args.receipt,json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+"\n")):
        target.parent.mkdir(parents=True,exist_ok=True)
        tmp=target.with_name(target.name+".tmp")
        tmp.write_text(body)
        tmp.replace(target)
    print(STATUS,"completed",len(rows),"failed_evaluation",receipt["evaluation_error"])
    return 2 if receipt["evaluation_error"] else 0

if __name__=="__main__":raise SystemExit(main())
