#!/usr/bin/env python3
"""Streaming source-aware B4 census + optional *real* scalar/EWPO screen.

This is the integrated replacement for the earlier minimal JSONL coverage
script. It is invoked ONLY via zee_priority1_cli.py --stream-coverage.
It does not read the entire scan into RAM: candidate IDs are verified with
an on-disk SQLite primary key; records are streamed into a temporary file
and atomically published. With --scalar-physics, actual GateB4
scalar_screen and ewpo_screen(64) run on each complete input spectrum.
No point can be declared allowed or experimentally excluded.
"""
from __future__ import annotations
import csv,hashlib,json,math,sqlite3,tempfile
from pathlib import Path
from zee_priority1_contracts import REQUIRED,STATUS,hashfile

SCALAR_FIELDS=("mH1","mH2","mh2","ma","alpha","beta",
               "gamma","m12sq","lc","k1","k2","k12")
SCALAR_STATUS="NOT_RUN_REQUEST_SCALAR_PHYSICS_FOR_FULL_POTENTIAL"
CANONICAL="scripts/zee_priority1_cli.py"
def source_rows(path):
    with Path(path).open(newline="") as f:
        if str(path).endswith(".jsonl"):
            for line in f:
                if line.strip():
                    row=json.loads(line)
                    if not isinstance(row,dict):
                        raise ValueError("JSONL point must be an object")
                    yield row
        elif str(path).endswith(".csv"):
            reader=csv.DictReader(f)
            if not reader.fieldnames or "id" not in reader.fieldnames:
                raise ValueError("B4 CSV requires id header")
            for row in reader:
                yield row
        else:
            raise ValueError("Streaming input must be .jsonl or .csv")
def structural(row,full_scalar):
    name=row.get("id")
    if not isinstance(name,str) or not name or name.strip()!=name:
        raise ValueError("Empty or malformed candidate ID")
    if row.get("candidate_status") and "NOT_ALLOWED" not in row["candidate_status"]:
        raise ValueError("Input cannot be labeled previously allowed")
    if full_scalar:
        from gateB4_adaptive_zee_scalar_scan import scalar_screen,ewpo_screen
        p={k:float(row[k]) for k in SCALAR_FIELDS}
        if not all(math.isfinite(v) for v in p.values()):
            raise ValueError("Nonfinite scalar parameter")
        if not (200<=p["mH1"]<p["mH2"] and 0<p["gamma"]<math.pi/2):
            raise ValueError("Invalid physical charged masses/mixing")
        theory=scalar_screen(p)
        if theory is None:
            status="FAILED_IMPLEMENTED_BFB_OR_TREE_UNITARITY"
        elif ewpo_screen(p,64) is None:
            status="FAILED_IMPLEMENTED_CORRELATED_STU"
        else:
            status="PASSED_IMPLEMENTED_SCALAR_AND_STU_NOT_MODEL_ALLOWED"
    else:
        for k in ("mH1","mH2","gamma"):
            if k in row:
                v=float(row[k])
                if not math.isfinite(v):
                    raise ValueError("Nonfinite "+k)
        status=SCALAR_STATUS
    return {"candidate_id":name,"scalar_EWPO_screen":status,
            "priority1_stage_statuses":{
                x:"BLOCKED_NO_COMPLETE_VALIDATED_BACKEND" for x in REQUIRED},
            "full_Zee_experimentally_allowed_or_excluded":None}
def scan(points,out,scalar_physics=False):
    points=Path(points).resolve();out=Path(out).resolve()
    if points==out or out.exists():
        raise ValueError("Output cannot overwrite input or existing data")
    if not points.is_file():
        raise ValueError("Point source missing")
    out.parent.mkdir(parents=True,exist_ok=True)
    counts={};n=0
    # Durable uniqueness check scales better than a 10-million-key Python set.
    with tempfile.TemporaryDirectory(prefix="p1_scan_",dir=out.parent) as d:
        directory=Path(d)
        db=sqlite3.connect(directory/"ids.sqlite3")
        db.execute("CREATE TABLE ids (id TEXT PRIMARY KEY)")
        with (directory/"rows.jsonl").open("w") as target:
            for row in source_rows(points):
                item=structural(row,scalar_physics)
                db.execute("INSERT INTO ids VALUES (?)",(item["candidate_id"],))
                state=item["scalar_EWPO_screen"]
                counts[state]=counts.get(state,0)+1
                target.write(json.dumps(item,sort_keys=True,allow_nan=False)+"\n")
                n+=1
        if n<1:
            raise ValueError("Cannot report empty cohort")
        db.close()
        # Only publish after the complete scan passes, never partial success.
        (directory/"rows.jsonl").replace(out)
    return {"status":"P1_SOURCE_B4_STREAMING_CENSUS_NOT_ZEE_EXCLUSION",
            "original_candidate_count":n,"scalar_and_EWPO_status_counts":counts,
            "scalar_physics_evaluated":bool(scalar_physics),
            "P1_other_five_scientific_backends_completed":False,
            "full_Zee_allowed_or_excluded":None,
            "input_SHA256":hashfile(points),"output_SHA256":hashfile(out)}
