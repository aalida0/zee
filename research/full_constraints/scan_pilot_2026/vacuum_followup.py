#!/usr/bin/env python3
"""Independent bounded tree-level Zee vacuum follow-up on five frozen pilot IDs.

Uses original Module1 reconstructed CP-conserving ten-field Zee potential,
exact D10 sufficient certificate, complete Gram-orbit five-variable SLSQP
search, and 80-digit independent polynomial verification of credible deeper
stationary witnesses. Finite search never certifies global vacuum stability.
No scans, new scalar draws, collider simulation or physical B veto.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

from module1.scalar_constraints import reconstruct, validate_input
from module1.d10_certificate import attempt_certificate
from module1.d10_search import constrained_search, polish_high_precision
from module14.scan import digest

HERE=Path(__file__).resolve().parent
PIN=HERE/"selected_five_vacuum_inputs_400.json"
IDS=(31,112,284,320,394)
OLD={31:"UNKNOWN",112:"PASS",284:"UNKNOWN",320:"UNKNOWN",394:"UNKNOWN"}
EXPECTED_MANIFEST_SHA="afa92f0e5d8afa56db976ff4158cc9971319419595574ef09be3f6d0d545ed45"
EXPECTED_DATASET_SHA="52bfe78aecf28bc7c4dc299bc49a74c77e1cf7a0c51c54746d541ac6794b7639"
EXPECTED_COMMIT="c194bb9018801b1a6881f22134e0650b1fdccae7"

def strict_inputs(path=PIN):
    evidence=json.loads(Path(path).read_text())
    if (evidence["executed_scan_commit"]!=EXPECTED_COMMIT
            or evidence["original_manifest_sha256"]!=EXPECTED_MANIFEST_SHA
            or evidence["original_dataset_sha256"]!=EXPECTED_DATASET_SHA):
        raise ValueError("Source 400-pilot provenance mismatch")
    rows=evidence["cards"]
    if tuple(c["id"] for c in rows)!=IDS:
        raise ValueError("Frozen candidate list changed")
    for row in rows:
        x,_,_,_=validate_input(row["scalar"])
        if digest(row["scalar"])!=row["scalar_sha256"]:
            raise ValueError("Original scan card SHA-256 mismatch for "+str(row["id"]))
        if row["scalar"]["benchmark_id"]!=f'd14_{row["id"]:08d}':
            raise ValueError("Original scalar id mismatch")
    return rows

def evaluate_one(row,starts:int,second_seed_starts:int):
    if not(16<=starts<=192 and 0<=second_seed_starts<=192 and
           (second_seed_starts==0 or second_seed_starts>=16)):
        raise ValueError("Bounded search starts not in documented range")
    x=row["scalar"]["physical"]
    p,_,reconstruction=reconstruct(x)
    if reconstruction["assessment"]!="PASS":
        raise RuntimeError("Original scalar reconstruction failed on copied card")
    cert=attempt_certificate(p,x)
    if row["id"]==112 and not cert["certified"]:
        raise RuntimeError("Previously exact-D10-certified point lost certificate")
    if row["id"]!=112 and cert["certified"]:
        raise RuntimeError("Previously uncertified point changed original certificate")
    # The seeds are explicit, unrelated to the generation seed. This is
    # a finite diagnostic with fixed boundary starts, not global proof.
    seeds=[(20261110+row["id"],starts)]
    if second_seed_starts:seeds.append((31415926+row["id"],second_seed_starts))
    searches=[]
    witnesses=[]
    for seed,n in seeds:
        search=constrained_search(p,x,seed=seed,starts=n)
        searches.append(search)
        best=search["lowest_credible_minimum"]
        if best is not None and best["delta_over_v4"]< -1e-6:
            try:
                polished=polish_high_precision(best,p,x)
            except Exception as exc:
                witnesses.append({"assessment":"UNCONFIRMED","seed":seed,
                                  "reason":str(exc),"pre_polish_candidate":best})
            else:
                witnesses.append({"assessment":"FAIL_VERIFIED_DEEPER_MINIMUM",
                                  "seed":seed,"witness":polished})
    confirmed=[z for z in witnesses if z["assessment"]=="FAIL_VERIFIED_DEEPER_MINIMUM"]
    if confirmed and cert["certified"]:
        raise ArithmeticError("Exact global certificate contradicts verified deeper minimum")
    assessment="FAIL" if confirmed else "PASS" if cert["certified"] else "UNKNOWN"
    return {
        "id":row["id"],"scalar_sha256":row["scalar_sha256"],
        "previous_vacuum_assessment":OLD[row["id"]],
        "new_vacuum_assessment":assessment,
        "tree_reconstruction":"PASS",
        "exact_sufficient_certificate":cert,
        "two_charged_Higgs_masses_GeV":[x["mH1"],x["mH2"]],
        "searches":searches,
        "minimum_credible_delta_over_v4":min(
            (r["lowest_credible_minimum"]["delta_over_v4"]
             for r in searches if r["lowest_credible_minimum"] is not None),
             default=None),
        "verified_deeper_stationary_witnesses":confirmed,
        "unconfirmed_deeper_witnesses":[z for z in witnesses if z["assessment"]=="UNCONFIRMED"],
        "finite_search_proves_global":False,
        "vacuum_lifetime":None,
        "physical_B":None,"physical_LFV":None,"physical_Higgs":None,
        "globally_allowed":None
    }

def run(output:Path,starts_main:int=192,starts_other:int=48,second_seed_starts:int=96):
    if output.exists():raise FileExistsError("Refuse overwrite of previous vacuum evidence")
    rows=strict_inputs()
    data=[]
    for row in rows:
        # Use a reproducible detailed two-seed search for ID 284,
        # bounded single-seed checks for other candidate IDs.
        primary=starts_main if row["id"]==284 else starts_other
        secondary=second_seed_starts if row["id"]==284 else 0
        result=evaluate_one(row,primary,secondary)
        data.append(result)
        print("VACUUM_FOLLOWUP",row["id"],result["new_vacuum_assessment"],
              "runs",sum(len(x["runs"]) for x in result["searches"]),
              "best_delta",result["minimum_credible_delta_over_v4"],
              "verified_deeper",len(result["verified_deeper_stationary_witnesses"]),
              "D10",result["exact_sufficient_certificate"]["certified"],flush=True)
    summary={
        "schema":"zee-400-pilot-vacuum-followup-1",
        "source_card_file_sha256":hashlib.sha256(PIN.read_bytes()).hexdigest(),
        "original_scan_commit":EXPECTED_COMMIT,
        "original_scan_manifest_sha256":EXPECTED_MANIFEST_SHA,
        "original_dataset_sha256":EXPECTED_DATASET_SHA,
        "status":"BOUNDED_TREE_VACUUM_DIAGNOSTICS_COMPLETE",
        "method":"D10 exact sufficient square completion + finite full Gram-orbit search and independent high-precision witness confirmation",
        "n_original_candidates":len(data),"n_new_scalar_proposals":0,
        "n_certified_by_exact_D10":sum(x["new_vacuum_assessment"]=="PASS" for x in data),
        "n_verified_deeper":sum(x["new_vacuum_assessment"]=="FAIL" for x in data),
        "n_global_unknown":sum(x["new_vacuum_assessment"]=="UNKNOWN" for x in data),
        "notes":"Finite multi-start optimizer non-discovery is not proof of global stability; no radiative vacuum, lifetime or experimental global acceptance.",
        "cards":data,
        "global_acceptance":None,"physical_allowed_count":None,
    }
    output.write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("BOUNDED_VACUUM_COMPLETE",summary["n_certified_by_exact_D10"],
          summary["n_verified_deeper"],summary["n_global_unknown"],flush=True)
    return summary

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--output",type=Path,required=True)
    a.add_argument("--starts-main",type=int,default=192)
    a.add_argument("--starts-other",type=int,default=48)
    a.add_argument("--second-seed-starts",type=int,default=96)
    x=a.parse_args()
    run(x.output,x.starts_main,x.starts_other,x.second_seed_starts)

if __name__=="__main__":
    main()
