#!/usr/bin/env python3
"""Source-locked 400-point *conditional* Zee pilot (never full acceptance).

Reuses the original module14 correlated sampler and actual scalar/neutrino/
D4 and diagnostic LFV workers. No external SPheno, MG5, HB/HS, B-veto, nor
unknown physics gate is silently applied. Publishes a complete manifest,
shard outputs, independent collection audit, and conditional dataset.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys

from module14 import scan
from module14.conditional_scan.workflow import join, load


ROOT=Path(__file__).resolve().parents[3]
PLAN=ROOT/"module14/conditional_scan/next20k_proposal.json"
CARD=ROOT/"module14/conditional_scan/matching_card.json"
EXPECTED_ARMS=("sub_TeV","production_window_1000_1350","broad_control")


def sha256(path:Path)->str:
    return scan.file_sha(path)


def strict_new_config(count:int,seed:int,shard_size:int)->dict:
    if any(type(x)!=int for x in (count,seed,shard_size)):
        raise ValueError("Counts and seeds must be integers")
    if count<1 or seed<0 or shard_size<1 or count%shard_size:
        raise ValueError("Require positive count, nonnegative seed and exact shard division")
    config=load(PLAN)
    if tuple(a["name"] for a in config["arms"])!=EXPECTED_ARMS:
        raise ValueError("Existing original scan-arm identities changed")
    if tuple(a["weight"] for a in config["arms"])!=(3,5,2):
        raise ValueError("Original arm weights changed")
    config.update(version="d14-conditional-cascade-1",count=count,
                  seed=seed,shard_size=shard_size)
    if config["sampling_mode"]!="correlated_heavy_v1":
        raise ValueError("Original correlated sampler changed")
    return config


def run(root:Path, count:int=400, seed:int=20261110, shard_size:int=40)->dict:
    root=Path(root)
    root.mkdir(parents=True,exist_ok=False)
    config=strict_new_config(count,seed,shard_size)
    source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    if len(source_commit)!=40:
        raise ValueError("Full source commit required")
    # This is a Git checkout, not an attested Condor bundle; do not claim one.
    os.environ["ZEE_D14_SOURCE_COMMIT"]=source_commit
    os.environ["ZEE_D14_BUNDLE_SHA256"]="LOCAL_UNSPECIFIED"
    (root/"config.json").write_text(json.dumps(config,indent=2,sort_keys=True)+"\n")
    scan.generate(config,root/"scan")
    scan.generate(config,root/"generation_repeat")
    manifest=root/"scan/manifest.jsonl"
    if manifest.read_bytes()!=(root/"generation_repeat/manifest.jsonl").read_bytes():
        raise RuntimeError("Repeated proposal generation is not byte-deterministic")
    root.joinpath("outputs").mkdir()
    triples=[]
    shard_counts={}
    for shard in sorted(root.joinpath("scan").glob("shard_*.jsonl")):
        output=root/"outputs"/(shard.stem+".output.jsonl")
        receipt=root/"outputs"/(shard.stem+".receipt.json")
        result=scan.run(shard,output,receipt,config,lfv=True,lfv_tree=False,
                        bsgamma=False,higgs=False)
        triples.append((shard,output,receipt))
        shard_counts[shard.name]={
            "input_sha256":sha256(shard),"output_sha256":sha256(output),
            "receipt_sha256":sha256(receipt),
            "summary":{k:v for k,v in result.items()
                       if k in ("count","counts","source_commit","source_bundle_sha256")}
        }
    if len(triples)!=count//shard_size:
        raise RuntimeError("Missing original shard triple")
    card=load(CARD)
    dataset=join(manifest,config,triples,card,source_commit,
                 "LOCAL_UNSPECIFIED",families=2,production_dir=None)
    if dataset["status"]!="CONDITIONAL_DATASET" or len(dataset["rows"])<count:
        raise RuntimeError("Collection/conditional join incomplete")
    armcounts=Counter()
    gates=defaultdict(Counter)
    neutrinos=Counter()
    statuses=Counter()
    conditional_flavor=Counter()
    candidates=[]
    for r in dataset["rows"]:
        if (r["globally_allowed"] is not None or r["bsg_exclusion"] is not None
                or r["np_theory_sigma"] is not None or r["rank"] is not None
                or r["yield_proxy_pb"] is not None):
            raise RuntimeError("An unsupported global/production claim escaped into pilot")
        if r["flavor"]["bsg_physical_classification"]!="UNKNOWN":
            raise RuntimeError("Approximate B-physics was promoted to physical")
        statuses[r["scalar_status"]]+=1
        for k,v in r["gates"].items():
            gates[k][v["assessment"]]+=1
        if isinstance(r["neutrino"],dict):
            n=r["neutrino"]
            neutrinos[n["ordering"]+":"+n["status"]]+=1
        label=r["flavor"]["bsg_nominal_classification"]
        conditional_flavor[label]+=1
        c=r["cascade"]
        if (isinstance(c,dict) and c.get("br_status")=="PASS"
                and c.get("BR_H2_H1Z") is not None
                and isinstance(r["neutrino"],dict)
                and r["neutrino"]["status"]=="PASS"):
            p=r["input_card"]["physical"]
            candidates.append({
                "id":r["id"],"arm":r["arm"],
                "ordering":r["neutrino"]["ordering"],
                "family":r["neutrino"]["family"],
                "mH1_GeV":p["mH1"],"mH2_GeV":p["mH2"],
                "tanbeta":math.tan(p["beta"]),"gamma_rad":p["gamma"],
                "BR_H2_to_H1Z_tree":c["BR_H2_H1Z"],
                "BR_H1_to_tb_tree":c["BR_H1_tb"],
                "cascade_product_tree":c["cascade_product"],
                "vacuum_certificate":r["gates"]["vacuum"]["assessment"],
                "approx_B_class":label,"physical_bsg":"UNKNOWN",
                "global_acceptance":None
            })
        armcounts[r["arm"]]+=1
    # Arm counts over *unique scalar proposals* rather than all family rows.
    proposals=Counter()
    for line in manifest.read_text().splitlines():
        x=json.loads(line)
        proposals[x["arm"]]+=1
    if sum(proposals.values())!=count:
        raise RuntimeError("Missing proposals")
    for arm in EXPECTED_ARMS:
        if proposals[arm] != count*next(a["weight"] for a in config["arms"] if a["name"]==arm)/10:
            raise RuntimeError("Arm slot schedule changed")
    candidates.sort(key=lambda c:(-c["cascade_product_tree"],c["id"],c["ordering"],c["family"]))
    dataset_path=root/"conditional_dataset.json.gz"
    with gzip.open(dataset_path,"wt",encoding="utf-8",compresslevel=6) as handle:
        json.dump(dataset,handle,sort_keys=True,allow_nan=False,separators=(",",":"))
    summary={
        "status":"TECHNICAL_CONDITIONAL_PILOT_COMPLETE",
        "date":"2026-11-10",
        "source_commit":source_commit,"plan_path":str(PLAN.relative_to(ROOT)),
        "plan_sha256":sha256(PLAN),"matching_card_sha256":sha256(CARD),
        "python":sys.version,"platform":platform.platform(),
        "config":config,"config_sha256":scan.digest(config),
        "manifest_sha256":sha256(manifest),
        "dataset_sha256":sha256(dataset_path),
        "count_proposals":count,"count_family_rows":len(dataset["rows"]),
        "shards":shard_counts,"by_arm_proposals":dict(sorted(proposals.items())),
        "by_arm_original_workflow":dataset["by_arm"],
        "scalar_gate_counts_OVER_FAMILY_ROWS":{k:dict(v) for k,v in gates.items()},
        "scalar_status_counts_OVER_FAMILY_ROWS":dict(statuses),
        "neutrino_status_counts_OVER_FAMILY_ROWS":dict(neutrinos),
        "approx_B_class_counts_OVER_FAMILY_ROWS":dict(conditional_flavor),
        "candidate_family_rows":len(candidates),
        "top_conditional_candidates":candidates[:25],
        "full_candidate_list":candidates,
        "collection":{
            k:v for k,v in dataset["collection"].items()
            if k in ("status","missing_points","computational_errors","point_count","family_count","shard_count","assessment_counts")
        },
        "physical_LFV":"UNKNOWN","physical_B":"UNKNOWN","physical_Higgs":"UNKNOWN",
        "global_acceptance":None,"physical_allowed_count":None,
        "production_integration":"NOT_RUN","LHC_event_sensitivity":"NOT_EVALUATED",
        "SPheno_full_loop":"NOT_OPERATIVE",
        "physics_scope":"Scalar/BFB/unitarity/EWPO + sufficient vacuum certificates + neutrino; other stages diagnostics; physical global veto incomplete",
        "is_final_full_constraints_scan":False,
        "source_bundle":"NO_ATTESTED_BUNDLE_GITHUB_RUN",
    }
    if summary["collection"]["status"]!="COMPLETE":
        raise RuntimeError("Collector not COMPLETE")
    (root/"pilot_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("PILOT_PASS",source_commit,"PROPOSALS",count,
          "FAMILY_ROWS",len(dataset["rows"]),
          "CANDIDATE_FAMILIES",len(candidates),
          "CANDIDATE_POINTS",len(set(x["id"] for x in candidates)),
          "SCALAR_BY_ARM",dict(sorted(proposals.items())),flush=True)
    print("GATES",json.dumps({k:dict(v) for k,v in gates.items()},sort_keys=True),flush=True)
    print("NEUTRINOS",dict(neutrinos),"FLAVOR_REF",dict(conditional_flavor),flush=True)
    for c in candidates[:10]:
        print("CANDIDATE_CONDITIONAL",json.dumps(c,sort_keys=True),flush=True)
    print("PHYSICAL_ACCEPTANCE UNKNOWN; ORIGINAL WORKER RECEIPTS/PRODUCTION NOT FULLY CERTIFIED",flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--count",type=int,default=400)
    parser.add_argument("--seed",type=int,default=20261110)
    parser.add_argument("--shard-size",type=int,default=40)
    args=parser.parse_args()
    run(args.output,args.count,args.seed,args.shard_size)

if __name__=="__main__":
    main()
