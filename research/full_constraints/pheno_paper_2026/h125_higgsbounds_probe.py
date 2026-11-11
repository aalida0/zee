#!/usr/bin/env python3
"""Source-pinned, h125-only HiggsBounds screening for the 64 constructed Zee cards.

This intentionally evaluates ONLY the 125 GeV resonance. Heavy H/A, H1/H2,
nonresonant processes, the complete Zee width and the full experimental
acceptance are NOT represented. Never treat a nonexclusion here as a global
Zee Higgs PASS.  Applied limits and selected analyses are saved individually.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

from research.full_constraints.pheno_paper_2026.h125_higgssignals_probe import build_zee_h125_prediction

ROOT=Path(__file__).resolve().parents[3]
SM_LEDGER=ROOT/"research/full_constraints/higgs/H125_SIGNAL_STRENGTH_EVIDENCE.json"

def _applied(entry):
    limit=entry.limit()
    observed=float(entry.obsRatio())
    expected=float(entry.expRatio())
    if not (math.isfinite(observed) and math.isfinite(expected) and observed>=0 and expected>=0):
        raise ValueError("Unphysical HiggsBounds ratio or dataset")
    return {
        "id":int(limit.id()),
        "analysis":str(limit),
        "reference":str(limit.reference()),
        "observed_ratio":observed,
        "expected_ratio":expected,
        "contributing_particles":[str(x) for x in entry.contributingParticles()],
    }

def evaluate(source:Path,dataset:Path,out:Path):
    if out.exists():
        raise FileExistsError("No overwrite of original 64-card HiggsBounds evidence")
    if not dataset.is_dir():
        raise FileNotFoundError("Pinned HiggsBounds dataset required")
    import Higgs.bounds as HB
    data=json.loads(source.read_text())
    rows=data.get("families",[])
    if data.get("n_evaluated")!=64 or len(rows)!=64 or data.get("global_acceptance") is not None:
        raise ValueError("Original source is not a complete 64-card undecided Zee set")
    sm_ledger=json.loads(SM_LEDGER.read_text())["matched_SM_ledger_GeV"]
    hb=HB.Bounds(str(dataset),HB.LimitOptions(minExpRatio=0.))
    n_loaded=len(hb.limits())
    if n_loaded<100:
        raise ValueError("Incomplete HiggsBounds observed limit dataset")
    cards=[]
    for row in rows:
        h=row["h125"]
        if h["full_model_total_width_GeV"] is not None:
            raise ValueError("Source h125 full width must still be unknown")
        pred,wr=build_zee_h125_prediction(h,sm_ledger)
        result=hb(pred)
        selected={str(key):_applied(val) for key,val in result.selectedLimits.items()}
        applied=[_applied(x) for x in result.appliedLimits]
        maxratio=max((x["observed_ratio"] for x in applied),default=None)
        observed_exclusion=bool(applied and not result.allowed)
        # Any rejection is only within the declared h125 effective-coupling
        # prescription. The omitted H/A/H1/H2 may lead to additional failures.
        cards.append({
            "scalar_id":row["scalar_id"],"ordering":row["ordering"],"seed":row["seed"],
            "h125_effective_width_input":wr,
            "n_applied_h125_only":len(applied),
            "selected_limits":selected,
            "applied_limits":applied,
            "max_h125_only_observed_ratio":maxratio,
            "h125_only_approx_excluded":observed_exclusion,
            "includes_heavy_neutral_or_charged":False,
            "physical_full_higgs_allowed":None,"global_acceptance":None,
        })
        if row["scalar_id"] in (15673,15591,2264):
            print("H125_HB_ONLY",row["scalar_id"],row["ordering"],row["seed"],
                  "N_APPLIED",len(applied),"MAX_OBS_RATIO",maxratio,
                  "SCOPED_APPROX_EXCLUDED",observed_exclusion,
                  "FULL_HIGGS_UNKNOWN",flush=True)
    if len({(x["scalar_id"],x["ordering"],x["seed"]) for x in cards})!=64:
        raise ValueError("Duplicate original 64-card family detected")
    report={
        "schema":"zee-2026-h125-only-HiggsBounds-screen-v1",
        "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "hbdataset":str(dataset),"n_loaded_limits":n_loaded,
        "n_h125_source_cases":len(cards),
        "source_specific_h125_width_prescription":"SM_reference_effective_couplings_plus_native_Zee_LFV_modes",
        "n_h125_only_approx_excluded":sum(x["h125_only_approx_excluded"] for x in cards),
        "h125_observed_limits_consulted":True,
        "heavy_H_A_and_H1_H2_observed_limits_applied":False,
        "full_physical_higgs":"UNKNOWN","global_acceptance":None,
        "interpretation":"HiggsBounds evaluated 125 GeV only, with effective-coupling reference widths, explicit Zee photon/gg couplings and native LFV. This is not the full scalar-sector experimental constraint.",
        "cases":cards,
    }
    out.write_text(json.dumps(report,allow_nan=False,sort_keys=True,indent=2)+"\n")
    print("H125_HB_SOURCE_64_DONE",len(cards),"SCOPED_EXCLUDED",report["n_h125_only_approx_excluded"],
          "MODEL_FULL_HIGGS_UNKNOWN",flush=True)
    return report

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--dataset",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    x=a.parse_args()
    evaluate(x.source,x.dataset,x.output)

if __name__=="__main__":
    main()
