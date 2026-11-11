#!/usr/bin/env python3
"""Stratified Zee scalar-scan accounting with scientifically valid denominators.

The original D14 correlated arms overlap. Estimates from different arms
are therefore NEVER pooled as 'the fraction of Zee parameter space'.
This analyzes source-matched proposal manifest + worker results by arm,
keeps PASS / FAIL / UNKNOWN / ERROR distinct, and quantifies uncertainty
for *source-defined tree-level scalar tests* only.

This is a scan-accounting tool, not a complete Higgs/LFV/B global fit.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


def read_jsonl(path):
    with Path(path).open() as f:
        for n,line in enumerate(f,1):
            if line.strip():
                try:yield json.loads(line)
                except json.JSONDecodeError as e:raise ValueError(f"{path} line {n}: {e}") from e


def wilson(x,n,z=1.959963984540054):
    if not 0<=x<=n: raise ValueError("Out-of-range binomial count")
    if n==0:return None
    p=x/n
    den=1+z*z/n
    mid=(p+z*z/(2*n))/den
    half=z/den*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return [max(0.,mid-half),min(1.,mid+half)]


def audit(config_path:Path,manifest_path:Path,worker_paths:list[Path],require_complete:bool=False):
    config=json.loads(config_path.read_text())
    if config.get("sampling_mode")!="correlated_heavy_v1":
        raise ValueError("Expected original D14 correlated-arm scheme")
    if len(config["arms"])<2:raise ValueError("Need multiple proposal sampling arms")
    total_weight=sum(arm["weight"] for arm in config["arms"])
    if total_weight<=0:raise ValueError("Invalid proposal arm weights")
    arms={a["name"]:a for a in config["arms"]}
    if len(arms)!=len(config["arms"]):raise ValueError("Duplicate proposal arm")
    config_sha=hashlib.sha256(
        json.dumps(config,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    ).hexdigest()
    expected={}
    for line in read_jsonl(manifest_path):
        i=line["id"]
        if i in expected:raise ValueError("Duplicate proposed ID")
        if line["arm"] not in arms:raise ValueError("Unexpected proposed arm")
        if line.get("config_sha256")!=config_sha:
            raise ValueError("Proposal config source hash mismatch")
        source_sha=hashlib.sha256(
            json.dumps(line["scalar"],sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        ).hexdigest()
        if line.get("scalar_sha256")!=source_sha:
            raise ValueError("Scalar proposal SHA does not match source bytes")
        expected[i]=line
    if len(expected)!=config["count"]:
        raise ValueError("Manifest does not have exact configured proposal count")
    # The deterministic arm schedule is a *proposal design*, not a random
    # probability density with a known global phase-space measure.
    for i,item in expected.items():
        slot=i%total_weight
        expected_arm=None
        for arm in config["arms"]:
            if slot<arm["weight"]:
                expected_arm=arm["name"]
                break
            slot-=arm["weight"]
        if item["arm"]!=expected_arm:
            raise ValueError("Arm schedule changed")
    seen={}
    for file in worker_paths:
        for line in read_jsonl(file):
            i=line["id"]
            if i not in expected or i in seen:raise ValueError("Unexpected/duplicate worker ID")
            if line.get("config_sha256")!=config_sha:
                raise ValueError("Worker config source mismatch")
            if line["scalar_sha256"]!=expected[i]["scalar_sha256"]:
                raise ValueError("Worker scalar source SHA not equal to proposal")
            if line["gates"].keys() != {"reconstruction","bfb","unitarity","ewpo","vacuum"}:
                raise ValueError("Changed scalar gate inventory")
            if line.get("global_acceptance") is not None:
                raise ValueError("Worker cannot certify global acceptance from these gates")
            seen[i]=line
    if require_complete and len(seen)!=len(expected):
        raise ValueError("Partial workers: cannot claim completed scalar scan")
    out={}
    for name in arms:
        ids=[i for i,item in expected.items() if item["arm"]==name]
        worked=[seen[i] for i in ids if i in seen]
        statuses=Counter(w["scalar_status"] for w in worked)
        vacuum=Counter(w["gates"]["vacuum"]["assessment"] for w in worked)
        theory=Counter(w["gates"]["reconstruction"]["assessment"] for w in worked)
        labels={k:{"n":statuses[k],"wilson_95_conditional_on_processed":wilson(statuses[k],len(worked))} for k in ("PASS","FAIL","UNKNOWN","ERROR")}
        out[name]={
            "configured_weight":arms[name]["weight"],
            "configured_weight_fraction":arms[name]["weight"]/total_weight,
            "n_proposed":len(ids),"n_processed":len(worked),
            "n_unprocessed":len(ids)-len(worked),
            "scalar_gate_labels":labels,
            "vacuum_gate_status_counts":dict(vacuum),
            "reconstruction_status_counts":dict(theory),
            "n_neutrino_family_evaluations":sum(len(w["neutrino"]) for w in worked if isinstance(w.get("neutrino"),list)),
            "statistical_interpretation":"Within-arm processed proposal fraction only; not allowed fraction of full Zee parameter space",
        }
    result={
        "schema":"zee-stratified-conditional-scalar-proposal-accounting-v1",
        "source_sampling_mode":config["sampling_mode"],
        "proposal_seed":config["seed"],
        "original_config_sha256":config_sha,
        "total_expected":len(expected),
        "total_processed":len(seen),
        "complete_worker_coverage":len(seen)==len(expected),
        "per_arm":out,
        "arms_overlap_in_physical_space":True,
        "global_parameter_space_sampling_density_normalized":False,
        "global_statistical_allowed_fraction":None,
        "full_B_LFV_Higgs_constraints_applied":False,
        "model_globally_allowed":None,
        "selection_warning":"Overlapping targeted and broad arms with different priors; cannot sum pass counts / total to infer a model-wide probability.",
    }
    return result


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--config",type=Path,required=True)
    a.add_argument("--manifest",type=Path,required=True)
    a.add_argument("--worker",type=Path,action="append",required=True)
    a.add_argument("--output",type=Path,required=True)
    a.add_argument("--require-complete",action="store_true")
    args=a.parse_args()
    if args.output.exists():raise FileExistsError("Do not overwrite prior scan receipt")
    report=audit(args.config,args.manifest,args.worker,args.require_complete)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("D14_PAPER_SCALAR_SAMPLING_ACCOUNTED",report["total_processed"],"/",report["total_expected"],
          "GLOBAL_ACCEPTANCE_UNKNOWN",flush=True)
    for name,item in report["per_arm"].items():
        print("ARM",name,"SOURCE_PROCESSED",item["n_processed"],
              "SCALAR_PASS",item["scalar_gate_labels"]["PASS"]["n"],
              "VACUUM",item["vacuum_gate_status_counts"],flush=True)


if __name__=="__main__":
    main()
