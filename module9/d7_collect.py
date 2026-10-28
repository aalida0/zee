"""Merge exactly four content-verified D7 Condor pilot shards.

No CL, likelihood, vacuum or acceptance. A missing/failed job makes aggregate
INCOMPLETE, never silently changes the denominator. A failed physics gate
is distinct from an infrastructure error.
"""
import argparse
import hashlib
import json
from pathlib import Path

from module2.interface import strict_loads

STATUS="D7_BATCH_PILOT_AGGREGATE_ONLY"


def collect(manifest, shards_folder, results_folder, receipts_folder):
    if (not isinstance(manifest,dict) or manifest.get("schema_version")!="d7-pilot-1.0.0"
        or manifest.get("total_points")!=32 or manifest.get("shard_count")!=4):
        raise ValueError("Unknown D7 manifest")
    expected={p["point_id"]:p for p in manifest["points"]}
    if len(expected)!=32:raise ValueError("Duplicate or missing manifest IDs")
    output=[];missing=[];infra=[]
    for idx,item in enumerate(manifest["shards"]):
        name=item["name"]
        shard=(shards_folder/name)
        if not shard.is_file() or hashlib.sha256(shard.read_bytes()).hexdigest()!=item["sha256"]:
            raise ValueError("Changed/missing original input shard "+name)
        output_path=results_folder/f"result_{idx}.jsonl"
        receipt_path=receipts_folder/f"receipt_{idx}.json"
        if not output_path.is_file() or not receipt_path.is_file():
            missing.append(name)
            continue
        receipt=strict_loads(receipt_path.read_text())
        raw=output_path.read_bytes()
        if (receipt.get("source_shard_sha256")!=item["sha256"] or
            receipt.get("result_bytes_sha256")!=hashlib.sha256(raw).hexdigest() or
            receipt.get("input_count")!=item["points"] or
            receipt.get("output_count")!=item["points"]):
            raise ValueError("Result/receipt/provenance mismatch "+name)
        rows=[strict_loads(line) for line in raw.decode().splitlines()]
        shard_in=[strict_loads(line) for line in shard.read_text().splitlines()]
        if len(rows)!=item["points"] or len(shard_in)!=item["points"]:
            raise ValueError("Unexpected shard cardinality")
        for original,row in zip(shard_in,rows):
            pid=original["point_id"]
            if row.get("point_id")!=pid or row.get("input_sha256")!=original["input_sha256"]:
                raise ValueError("Input/output point mismatch")
            if pid not in expected or row.get("global_zee_acceptance","invalid") is not None:
                raise ValueError("Unknown ID or illegal viability claim")
            if row.get("execution_status")=="EVALUATION_ERROR":infra.append(pid)
            elif row.get("execution_status")!="EVALUATED_SCOPED":
                raise ValueError("Unknown execution status")
            output.append(row)
    if len({x["point_id"] for x in output})!=len(output):
        raise ValueError("Repeated results")
    complete=(not missing and not infra and len(output)==manifest["total_points"])
    return {"schema_version":"d7-summary-1.0.0","status":STATUS,
      "pilot_completion_status":"COMPLETE_SCOPED" if complete else "INCOMPLETE_OR_BLOCKED",
      "point_count_expected":manifest["total_points"],
      "point_count_collected":len(output),
      "missing_shards":missing,"evaluation_errors":infra,
      "scoped_scalar_pass":sum(r.get("scalar_status")=="SCOPED_PASS" for r in output),
      "scoped_scalar_fail_or_unknown":sum(r.get("scalar_status")=="SCOPED_FAIL_OR_UNKNOWN" for r in output),
      "inverse_neutrino_closure_pass":sum(r.get("neutrino_status")=="INVERSE_TARGET_CLOSURE_PASS" for r in output),
      "mass_minmax_GeV":{key:[min(p["physical"][key] for p in manifest["points"]),
                            max(p["physical"][key] for p in manifest["points"])]
                         for key in ("mH1","mH2")},
      "scoped_rows":output,
      "cutflow_representativeness":"DEVELOPMENT_SUPPORT_ONLY_NO_GLOBAL_EFFICIENCY_INFERENCE",
      "full_LFV":"NOT_EVALUATED","nuFIT_joint_likelihood":"NOT_EVALUATED",
      "global_vacuum":"NOT_EVALUATED","physical_bsgamma":"NOT_EVALUATED",
      "collider_rates":"NOT_EVALUATED","global_zee_acceptance":None}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--shards",type=Path,required=True)
    ap.add_argument("--results",type=Path,required=True)
    ap.add_argument("--receipts",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    m=strict_loads(args.manifest.read_text())
    report=collect(m,args.shards,args.results,args.receipts)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=args.output.with_name(args.output.name+".tmp")
    tmp.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    tmp.replace(args.output)
    print(STATUS,report["pilot_completion_status"],report["point_count_collected"])
    return 0 if report["pilot_completion_status"]=="COMPLETE_SCOPED" else 2

if __name__=="__main__":raise SystemExit(main())
