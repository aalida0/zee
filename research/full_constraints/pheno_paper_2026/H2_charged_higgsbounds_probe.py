#!/usr/bin/env python3
"""64 new Zee families: actual 13 TeV LO tbH2 charged-Higgs HiggsBounds subset.

Only the source-validated H2 heavy charged state and its MG5 13 TeV LO
associated tb rate are supplied to HiggsBounds. The **complete native D4
two-body** total width includes the exotic H2 -> H1 Z cascade, so each
SM final state BR has the correct shared denominator. H1 production,
8 TeV, 4FS/NLO and all neutral states are not supplied.

A bounded observed-limit ratio in this restricted production/decay model is
NOT a global Zee exclusion or a guarantee of experimental NWA/shape validity.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

from module14.scan import digest
from module14.decays import DecayCalculation
from module2.interface import evaluate as neutrino_evaluate
from research.full_constraints.pheno_paper_2026.paper_gate import load_sources

TOOL_DECAYS=(
    ("tb","t anti-b"),("cs","c anti-s"),("cb","c anti-b"),
    ("ud","u anti-d"),("us","u anti-s"),("ub","u anti-b"),
    ("cd","c anti-d"),("enu","e nu_all"),("munu","mu nu_all"),
    ("taunu","tau nu_all")
)

def inspect_decay_contract(h2,fresh):
    total=h2["total"]
    if total["status"]!="D4_COMPLETE_TWO_BODY_BR_PASS":
        raise ValueError("Native D4 incomplete charged width")
    gamma=float(total["total_width_GeV"])
    if not math.isfinite(gamma) or gamma<=0:
        raise ValueError("Invalid Zee H2 total width")
    channels={r["channel"]:float(r["width_GeV"]) for r in h2["channels"]}
    if len(channels)!=len(h2["channels"]) or any(not math.isfinite(x) or x<0 for x in channels.values()):
        raise ValueError("Repeated, unphysical or missing charged widths")
    if not math.isclose(math.fsum(channels.values()),gamma,rel_tol=1e-9):
        raise ValueError("H2 total width is not the sum of charged D4 channels")
    if not math.isclose(channels["H1 Z"]/gamma,fresh["D4_BR_H2_H1Z"],rel_tol=2e-8,abs_tol=1e-12):
        raise ValueError("Exotic Zee cascade source BR not retained in D4 total width")
    result={}
    for name,channel in TOOL_DECAYS:
        result[name]=channels[channel]/gamma
    # Other physical two-body decays are never silently discarded from the
    # denominator simply because the HiggsBounds decay enum lacks that mode.
    if sum(result.values())>1+1e-12:
        raise ValueError("HiggsBounds SM channel BRs violate unitarity")
    return {"gamma_GeV":gamma,"input_BRs":result,
            "BR_H2_to_H1_Z":channels["H1 Z"]/gamma,
            "all_two_body_BRs_sum":math.fsum(channels.values())/gamma,
            "H2_decay_channels_total":len(channels)}

def _higgsbounds_entry(entry):
    limit=entry.limit()
    observed=float(entry.obsRatio())
    expected=float(entry.expRatio())
    if not (math.isfinite(observed) and math.isfinite(expected) and observed>=0 and expected>=0):
        raise ValueError("Invalid HiggsBounds charged observed/expected ratio")
    return {"id":int(limit.id()),"process":str(limit),
            "reference":str(limit.reference()),
            "observed_ratio":observed,"expected_ratio":expected,
            "contributing_particles":[str(x) for x in entry.contributingParticles()]}

def evaluate(source:Path,dataset:Path,out:Path):
    if out.exists():raise FileExistsError("Never overwrite charged source-limit evidence")
    if not dataset.is_dir():raise FileNotFoundError("Pinned HiggsBounds dataset missing")
    import Higgs.predictions as HP
    import Higgs.bounds as HB
    data=json.loads(source.read_text())
    if (data.get("new_neutrino_family_count")!=64 or len(data.get("families",[]))!=64
        or data.get("global_acceptance") is not None):
        raise ValueError("Requires 64 source-specific Zee flavor cards")
    _,original,rates,_,_,_,_,_=load_sources()
    scalars={x["scalar_id"]:x for x in data["scalars"]}
    if set(scalars)!=set(original) or set(i for i,energy in rates if energy==13)!=set(original):
        raise ValueError("Original exact 16 scalar/production records not coherent")
    hb=HB.Bounds(str(dataset),HB.LimitOptions(minExpRatio=0.))
    cases=[]
    for f in data["families"]:
        rid=f["id"]
        if f["scalar_sha256"]!=original[rid]["scalar_sha256"]:
            raise ValueError("New Yukawa family scalar hash not original production card")
        scalar=scalars[rid]["scalar_input"]
        if digest(scalar)!=f["scalar_sha256"]:
            raise ValueError("Original certified scalar has changed")
        n=neutrino_evaluate(f["algebraic_texture_input"])
        if n["inverse"]["family_relative_residual"]>=2e-9:
            raise ValueError("Neutrino inverse target does not close")
        fields={k:n[k] for k in ("F","D","Ye","Ye2","Mnu")}
        fields.update(input=f["algebraic_texture_input"],input_sha256=f["algebraic_texture_input_sha256"])
        decay=DecayCalculation(scalar,fields).evaluate(fields)
        if decay["status"]!="PASS" or decay["scalar_sha256"]!=f["scalar_sha256"]:
            raise ValueError("Source native charged D4 decay re-evaluation failed")
        widths=inspect_decay_contract(decay["mothers"]["H2"],f)
        p=scalar["physical"]
        sigma=float(rates[(rid,13)]["sigma_pb"])
        if not math.isfinite(sigma) or sigma<=0:
            raise ValueError("Missing/invalid actual MG5 H2 associated rate")
        pred=HP.Predictions()
        h2=pred.addParticle(HP.ChargedScalar("H2"))
        h2.setMass(p["mH2"])
        h2.setTotalWidth(widths["gamma_GeV"])
        h2.setCxn(HP.Collider.LHC13,HP.Production.Hpmtb,sigma)
        for dec,br in widths["input_BRs"].items():
            h2.setBr(getattr(HP.Decay,dec),br)
        hbresult=hb(pred)
        applied=[_higgsbounds_entry(x) for x in hbresult.appliedLimits]
        selected={str(k):_higgsbounds_entry(x) for k,x in hbresult.selectedLimits.items()}
        cases.append({
            "scalar_id":rid,"ordering":f["ordering"],"seed":f["seed"],
            "source_scalar_sha256":f["scalar_sha256"],
            "H2_mass_GeV":float(p["mH2"]),
            "H2_gamma_over_mass":widths["gamma_GeV"]/float(p["mH2"]),
            "H2_D4_two_body":widths,
            "sigma13_MG5_5FS_LO_pb":sigma,
            "applied_charged_limits":applied,
            "selected_charged_limits":selected,
            "H2_13TeV_LO_model_subset_excluded":bool(applied and not hbresult.allowed),
            "H2_higgsbounds_study_status":"CENTRAL_LO_NWA_SIGNAL_CONTRACT_UNVALIDATED",
            "includes_H1_production":False,"includes_8TeV":False,
            "full_charged_Higgs_exclusion":None,"full_Higgs":"UNKNOWN",
            "global_acceptance":None
        })
        if rid in (15673,15591,2264):
            print("ZEE_H2_ONLY_HB",rid,f["ordering"],f["seed"],
                  "GAMMA_OVER_M",widths["gamma_GeV"]/float(p["mH2"]),
                  "BR_H1Z",widths["BR_H2_to_H1_Z"],
                  "APPLIED",len(applied),
                  "SELECTED_OBS",[round(x["observed_ratio"],6) for x in selected.values()],
                  "NO_GLOBAL_HIGGS",flush=True)
    if len(cases)!=64 or len({(x["scalar_id"],x["ordering"],x["seed"]) for x in cases})!=64:
        raise ValueError("Incomplete or repeated 64-card native H2 charged study")
    result={
        "schema":"zee-64-source-H2-charged-HB-13TeV-LO-bounded-subset-v1",
        "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "n_original_scalar":16,"n_new_neutrino_family":64,
        "n_H2_LO_model_subset_excluded":sum(x["H2_13TeV_LO_model_subset_excluded"] for x in cases),
        "all_16_actual_H2_MG5_13TeV_rates_used":True,
        "H2_total_two_body_width_includes_cascade":True,
        "missing_material_experimental_inputs":["H1 13TeV and 8TeV production",
          "Neutral H/A production and decay competition",
          "4FS versus 5FS and NLO QCD scale/PDF uncertainties",
          "Signal resonance line shape/interference, selection efficiency and reported NWA signal applicability",
          "H2 to H1Z experimental cascade final-state topology"],
        "full_charged_Higgs_exclusion":None,
        "physical_Higgs":"UNKNOWN","global_acceptance":None,
        "cases":cases,
    }
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("ZEE_64_H2_HIGGSBOUNDS_SCOPED",len(cases),
          "SELECTED_LO_EXCLUDED",result["n_H2_LO_model_subset_excluded"],
          "NOT_FULL_MODEL",flush=True)
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True,type=Path)
    ap.add_argument("--dataset",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    evaluate(a.source,a.dataset,a.output)

if __name__=="__main__":main()
