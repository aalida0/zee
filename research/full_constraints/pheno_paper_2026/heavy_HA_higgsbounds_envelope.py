#!/usr/bin/env python3
"""Heavy Zee H/A 13 TeV HiggsBounds **upper-rate envelope** (not model exclusion).

Inputs are separately CI-executed all-16 original scalar SusHi ggF+bbH
cross sections and all-64 native Zee/HDECAY disjoint partial-width ledgers.
The known-channel positive sum S is NOT a certified physical total width.
Here it is used as an explicitly chosen *LO signal-maximizing denominator*
at fixed known positive partial widths: Gamma_scenario = S(1+extra>=0).
This supplies a useful sensitivity triage, not a physical global 95%-CL
exclusion. Missing widths, omitted production, interference and HiggsTools
analysis applicability are NOT set to zero in the physical model.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

# Channels with explicit source-computed partial rates and familiar
# inclusive HiggsTools experimental final states. Everything else is in
# the denominator, not silently made to vanish from the Zee model.
CHANNEL_MAP={
    "t tbar":"tt","b bbar":"bb","c cbar":"cc","s sbar":"ss",
    "tau tau":"tautau","mu mu":"mumu","gg":"gg",
    "WW":"WW","ZZ":"ZZ",
}
EXTRA_WIDTH_FACTORS=(0.,0.10,0.25)

def prepare_source(width_case,rate,mode):
    if width_case["state"]!=mode or rate["state"]!=mode:
        raise ValueError("H/A source state mismatch")
    if not math.isclose(float(width_case["mass_GeV"]),float(rate["mass_GeV"]),rel_tol=1e-11):
        raise ValueError("Matched H/A mass mismatch")
    total=float(width_case["mixed_order_known_channel_sum_GeV"])
    if (not math.isfinite(total) or total<=0
        or width_case.get("full_physical_total_width_GeV") is not None
        or width_case.get("full_Higgs")!="UNKNOWN"):
        raise ValueError("Missing/invalid mixed-order source or physical width wrongly established")
    channels={k:float(v) for k,v in width_case["channel_widths_GeV"].items()}
    if any(not math.isfinite(v) or v<0 for v in channels.values()):
        raise ValueError("Unphysical H/A source partial width")
    if not math.isclose(math.fsum(channels.values()),total,rel_tol=1e-10,abs_tol=1e-9):
        raise ValueError("Disjoint HDECAY/native Zee source width sum changed")
    br={dst:channels[src]/total for src,dst in CHANNEL_MAP.items() if src in channels}
    if not ("tt" in br and "bb" in br and "tautau" in br and "gg" in br):
        raise ValueError("One of the leading heavy Higgs channels is missing")
    if sum(br.values())>1+1e-10:
        raise ArithmeticError("Source partial widths exceed known sum")
    cross_sections={}
    for mode_name in ("ggF","bbH"):
        v=float(rate["rates"][mode_name]["sigma_pb"])
        if not math.isfinite(v) or v<0:
            raise ValueError("Nonphysical source SusHi LO production")
        cross_sections[mode_name]=v
    return {
        "mass_GeV":float(rate["mass_GeV"]),
        "known_width_GeV":total,
        "source_partial_BR_upper_components":br,
        "source_ggF_bbH_LO13_pb":cross_sections,
        "fraction_omitted_to_HP_input":1.-sum(br.values()),
        "uncomputed_real_total_width":True,
    }

def build_prediction(pair,extra_width_fraction):
    import Higgs.predictions as HP
    if (not isinstance(extra_width_fraction,(float,int))
        or not math.isfinite(extra_width_fraction) or extra_width_fraction<0):
        raise ValueError("Nonnegative added-width sensitivity factor required")
    pred=HP.Predictions()
    for name in ("H","A"):
        q=pair[name]
        neutral=pred.addParticle(HP.BsmParticle(name,"neutral","even" if name=="H" else "odd"))
        neutral.setMass(q["mass_GeV"])
        width=q["known_width_GeV"]*(1+extra_width_fraction)
        neutral.setTotalWidth(width)
        for proc,channel in (("ggF",HP.Production.ggH),("bbH",HP.Production.bbH)):
            neutral.setCxn(HP.Collider.LHC13,channel,q["source_ggF_bbH_LO13_pb"][proc])
        for channel,source_br in q["source_partial_BR_upper_components"].items():
            neutral.setBr(channel,source_br/(1+extra_width_fraction))
    return pred

def evaluate(widths:Path,production:Path,dataset:Path,out:Path):
    if out.exists():raise FileExistsError("Source exclusions cannot be overwritten")
    if not dataset.is_dir():raise FileNotFoundError("Pinned observed HiggsBounds dataset missing")
    import Higgs.bounds as HB
    w=json.loads(widths.read_text())
    p=json.loads(production.read_text())
    if (w.get("count")!=64 or not w.get("partial_widths_only")
        or w.get("global_acceptance") is not None
        or p.get("scalars")!=16 or p.get("executed_neutral_states")!=32
        or p.get("global_acceptance") is not None):
        raise ValueError("Expected exact original 16x4 partial H/A and 16x2 production inputs")
    pl={(r["scalar_id"],r["state"]):r for r in p["cases"]}
    if len(pl)!=32 or len({r["scalar_id"] for r in p["cases"]})!=16:
        raise ValueError("Incomplete/duplicate actual source H/A production rates")
    hb=HB.Bounds(str(dataset),HB.LimitOptions(minExpRatio=0.))
    output=[]
    for row in w["cases"]:
        sid=row["scalar_id"]
        pair={}
        for st in ("H","A"):
            producer=pl[(sid,st)]
            if producer["original_scalar_sha256"]!=row["scalar_sha256"]:
                raise ValueError("H/A production not same scalar as neutrino family")
            pair[st]=prepare_source(row["states"][st],producer,st)
        family={"scalar_id":sid,"ordering":row["ordering"],"seed":row["seed"],
                "lo_upper_envelope_denominator_is_physical_total_width":False,
                "no_full_Zee_Higgs_exclusion":True,"cases":[],"global_acceptance":None}
        for frac in EXTRA_WIDTH_FACTORS:
            pred=build_prediction(pair,frac)
            tested=hb(pred)
            def entry(e):
                limit=e.limit()
                return {"limit_id":int(limit.id()),"reference":str(limit.reference()),
                        "analysis":str(limit),"observed_ratio":float(e.obsRatio()),
                        "expected_ratio":float(e.expRatio()),
                        "particles":[str(x) for x in e.contributingParticles()]}
            applied=[entry(x) for x in tested.appliedLimits]
            selected={str(k):entry(v) for k,v in tested.selectedLimits.items()}
            if any(not math.isfinite(x["observed_ratio"]) or x["observed_ratio"]<0 for x in applied):
                raise ValueError("Nonfinite heavy-HiggsBounds observed ratio")
            family["cases"].append({
                "assumed_additional_positive_width_fraction_of_known":frac,
                "H_width_scenario_GeV":pair["H"]["known_width_GeV"]*(1+frac),
                "A_width_scenario_GeV":pair["A"]["known_width_GeV"]*(1+frac),
                "selected":selected,"n_applied":len(applied),
                "max_all_applied_observed_ratio":max((x["observed_ratio"] for x in applied),default=None),
                "selected_scoped_only_excluded":bool(applied and not tested.allowed),
                "applied":applied,
                "physical_Higgs_95CL_exclusion":None
            })
        output.append(family)
        if sid in (15673,15591,2264):
            a=family["cases"][0]
            print("HEAVY_ZEE_HB_UPPER_RATE_PILOT",sid,row["ordering"],row["seed"],
                  "SELECTED",[(k,round(v["observed_ratio"],5)) for k,v in a["selected"].items()],
                  "MAX_ALL_APPLIED",a["max_all_applied_observed_ratio"],
                  "UNQUALIFIED_HIGGS_MODEL_UNKNOWN",flush=True)
    if len(output)!=64 or len({(x["scalar_id"],x["ordering"],x["seed"]) for x in output})!=64:
        raise ValueError("Incomplete all-64 heavy-Higgs source join")
    report={
        "schema":"zee-H-A-16x4-source-SusHi-HDECAY-HiggsBounds-LO-signals-upper-envelope-v1",
        "HDECAY_64_source_sha256":hashlib.sha256(widths.read_bytes()).hexdigest(),
        "SusHi_16_source_sha256":hashlib.sha256(production.read_bytes()).hexdigest(),
        "source_16_scalar":16,"source_64_family":64,"HiggsBounds_dataset":str(dataset),
        "additional_width_factors":EXTRA_WIDTH_FACTORS,
        "has_full_H_A_physical_total_widths":False,
        "production_scope":"actual-source-SusHi-1.7.0-LO-ggF-bbH-13TeV",
        "not_included":["2026-QCD-PDF-theory-band","validated-total-H-A-widths",
          "full gamma gamma, Zgamma and offshell exotic modes",
          "H/A to hZ, hh, H1W collider cascade analyses",
          "full neutral plus charged HiggsBounds spectrum",
          "wide-resonance ttbar interference/NWA acceptance"],
        "physical_Higgs":"UNKNOWN","global_acceptance":None,
        "cases":output,
    }
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("HEAVY_ZEE_HB_SOURCE_SCOPED_64",len(output),"HEAVY_HIGGS_PHYSICAL_UNKNOWN",flush=True)
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--widths",type=Path,required=True)
    ap.add_argument("--production",type=Path,required=True)
    ap.add_argument("--dataset",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    x=ap.parse_args()
    evaluate(x.widths,x.production,x.dataset,x.output)

if __name__=="__main__":
    main()
