#!/usr/bin/env python3
"""64-case heavy Zee H/A 13-TeV source-pinned HiggsBounds *rate-envelope* scan.

Inputs:
- 32 real SusHi 1.7.0 LO ggF/bbH rates for 16 original scalar spectra;
- 64 source-matched actual AnyHdecay 6.60 transferable quark/neutral partial
  widths combined with native Zee general lepton/exotic charged-W channels;
- one precise pinned HiggsBounds 1.1.3 observed-limit dataset.

The denominator of every BR is the sum of known, disjoint, source-calculated
partial widths: it is a *declared optimistic rate upper envelope* under
the assumption that missing positive-width channels only add decay rate.
It is NOT a physical total width, a physical BR, or a demonstrated exclusion.
Signal interpretation requires QCD/PDF, width/interference, efficiency and
all missing channel assessments. Do not declare model-wide PASS or FAIL.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

SUSHI_SHA="e896b5a5cb07bfcb3acedbb40f68f6b266d8cc27be97e5f16db817dfb0753faf"
HDECAY_SHA="c02622cb7d9eb6bbe74a8e435b5e9f0e85513cd2160cee48376003f5db83b32d"

HEAVY_DECAYS=(
    ("bb","b bbar"),("cc","c cbar"),("ss","s sbar"),
    ("tt","t tbar"),("tautau","tau tau"),("mumu","mu mu"),
    ("WW","WW"),("ZZ","ZZ"),
)

def checked_inputs(sushi:Path,widths:Path):
    files=((sushi,SUSHI_SHA),(widths,HDECAY_SHA))
    for path,expected in files:
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=expected:
            raise ValueError("Frozen native source dataset changed without independent revalidation: "+str(path))
    s=json.loads(sushi.read_text())
    w=json.loads(widths.read_text())
    if (s.get("scalars")!=16 or s.get("executed_neutral_states")!=32 or
        s.get("QCD_order")!="LO_5FS" or s.get("energy_TeV")!=13 or
        s.get("global_acceptance") is not None):
        raise ValueError("Expected exactly 16x2 independently executed SusHi 13 TeV")
    if (w.get("count")!=64 or not w.get("partial_widths_only") or
        w.get("global_acceptance") is not None or w.get("full_physical_Higgs")!="UNKNOWN"):
        raise ValueError("64 native Zee/HDECAY partial-channel source not validated")
    prod={}
    for row in s["cases"]:
        key=(row["scalar_id"],row["state"])
        if key in prod or row["state"] not in ("H","A"):
            raise ValueError("Duplicated SusHi H/A original scalar")
        prod[key]=row
    if len(prod)!=32 or len({k[0] for k in prod})!=16:
        raise ValueError("Not 32 distinct SusHi H/A production input cards")
    cases=w["cases"]
    if len(cases)!=64 or len({(r["scalar_id"],r["ordering"],r["seed"]) for r in cases})!=64:
        raise ValueError("Missing or duplicated source neutrino families")
    return prod,cases

def positive(x,label,allowzero=True):
    x=float(x)
    if not math.isfinite(x) or x<0 or (not allowzero and x<=0):
        raise ValueError("Invalid source "+label)
    return x

def source_rates(prod,row,state):
    p=prod[(row["scalar_id"],state)]
    w=row["states"][state]
    if p["original_scalar_sha256"]!=row["scalar_sha256"]:
        raise ValueError("Production/decay original scalar SHA mismatch")
    if not math.isclose(p["mass_GeV"],w["mass_GeV"],rel_tol=1e-12):
        raise ValueError("Production and decay physical resonance mass mismatch")
    if p["QCD_order"]!="LO" or p["energy_TeV"]!=13 or p["PDF"]!="MMHT2014lo68cl":
        raise ValueError("SusHi energy, order or PDF provenance changed")
    gg=positive(p["rates"]["ggF"]["sigma_pb"],"ggF source")
    bb=positive(p["rates"]["bbH"]["sigma_pb"],"bbH source")
    known=positive(w["mixed_order_known_channel_sum_GeV"],"known disjoint width",False)
    channels=w["channel_widths_GeV"]
    for k,v in channels.items():
        positive(v,"partial channel "+k)
    if not math.isclose(math.fsum(channels.values()),known,rel_tol=5e-11):
        raise ValueError("H/A native Zee/HDECAY disjoint width accounting failed")
    if w["full_physical_total_width_GeV"] is not None or w["normalized_physical_branching_fractions"] is not None:
        raise ValueError("Source unexpectedly promoted partial sum to physical width")
    if w["source_uncomputed_on_shell"]:
        raise ValueError("Missing open on-shell Zee decay channel: not even optimistic channel-complete")
    missing=tuple(w.get("additional_missing_groups",()))+tuple(w.get("source_uncomputed_channel_groups",()))
    return {"mass_GeV":p["mass_GeV"],"sigma13_ggF_LO_pb":gg,
            "sigma13_bbH_LO_pb":bb,"known_Gamma_sum_GeV":known,
            "known_Gamma_over_M":known/p["mass_GeV"],
            "channels":channels,"missing":missing}

def _applied(entry):
    lim=entry.limit()
    obs=float(entry.obsRatio());exp=float(entry.expRatio())
    if not (math.isfinite(obs) and math.isfinite(exp)):
        raise ValueError("Invalid observed/expected HiggsBounds data")
    return {"analysis_id":int(lim.id()),"analysis":str(lim),
            "reference":str(lim.reference()),"observed_ratio":obs,
            "expected_ratio":exp,
            "contributing_particles":[str(x) for x in entry.contributingParticles()]}

def scan(sushi:Path,widths:Path,dataset:Path,out:Path):
    if out.exists():raise FileExistsError("Refuse overwrite of original source Higgs results")
    if not dataset.is_dir():raise FileNotFoundError("Pinned HiggsBounds experimental dataset missing")
    import Higgs.predictions as HP
    import Higgs.bounds as HB
    prods,cases=checked_inputs(sushi,widths)
    bounds=HB.Bounds(str(dataset),HB.LimitOptions(minExpRatio=0.))
    if len(bounds.limits())<100:raise ValueError("Observed HiggsBounds dataset incomplete")
    experiments=[]
    for case in cases:
        row={"scalar_id":case["scalar_id"],"scalar_sha256":case["scalar_sha256"],
             "ordering":case["ordering"],"seed":case["seed"]}
        for name in ("H","A"):
            row[name]=source_rates(prods,case,name)
        stresses=[]
        # The actual unknown physical total is not substituted. Multiply
        # all source known denominators by a fixed factor to quantify how
        # the observed search comparison depends on additional decays.
        # 1.0 is an optimistic upper-rate envelope for fixed source widths.
        for excess in (1.0,1.10,1.25,1.50):
            pred=HP.Predictions()
            for state in ("H","A"):
                d=row[state]
                particle=pred.addParticle(HP.BsmParticle(state,"neutral","even" if state=="H" else "odd"))
                particle.setMass(d["mass_GeV"])
                particle.setTotalWidth(excess*d["known_Gamma_sum_GeV"])
                particle.setCxn(HP.Collider.LHC13,HP.Production.ggH,d["sigma13_ggF_LO_pb"])
                particle.setCxn(HP.Collider.LHC13,HP.Production.bbH,d["sigma13_bbH_LO_pb"])
                for dmode,k in HEAVY_DECAYS:
                    particle.setBr(getattr(HP.Decay,dmode),positive(d["channels"][k],k)/(excess*d["known_Gamma_sum_GeV"]))
            result=bounds(pred)
            selected={str(k):_applied(v) for k,v in result.selectedLimits.items()}
            applied=[_applied(v) for v in result.appliedLimits]
            stresses.append({"denominator_known_sum_multiplier":excess,
                  "selected_limits":selected,"n_applied":len(applied),
                  "applied_limits":applied,
                  "selected_excluded_under_provisional_LO_model":bool(applied and not result.allowed),
                  "actual_physical_Zee_exclusion":None})
        row["stress_tests"]=stresses
        row["optimistic_known_width_sum_is_a_physical_total"]=False
        row["optimistic_limit_decision_requires_signal_shape_and_missing_processes"]=True
        row["full_Higgs"]="UNKNOWN"
        experiments.append(row)
        if case["scalar_id"] in (15673,15591,2264) and case["ordering"]=="NO" and case["seed"]==20261111:
            sel=stresses[0]["selected_limits"]
            print("ZEE_HA_HEAVY_HB",case["scalar_id"],"ORDERING",case["ordering"],
                "N_APPLIED",stresses[0]["n_applied"],
                "SELECTED",[(v["analysis_id"],round(v["observed_ratio"],5)) for v in sel.values()],
                "UPPER_DENOM_ONLY",True,"FULL_HIGGS_UNKNOWN",flush=True)
    report={
      "schema":"zee-16x4-H-A-HiggsBounds-optimistic-partial-sum-LO-rate-envelope-v1",
      "n_cases":len(experiments),"n_spectra":16,"n_both_states":32,
      "SusHi_source_file_sha256":SUSHI_SHA,"native_HDECAY_source_file_sha256":HDECAY_SHA,
      "width_multipliers":[1.0,1.10,1.25,1.50],
      "optimistic_known_widths_are_full_Zee_total_widths":False,
      "observable_scope":"Only LHC13 ggF/bbH direct H/A->bb,cc,ss,tt,tautau,mumu,WW,ZZ channels",
      "missing_channels_and_model_comparisons":[
          "H/A->hh,hZ,H_iW and H_iH_j cascade searches (not supplied)",
          "H/A->gamma gamma and Z gamma (Zee specific loops incomplete)",
          "Neutral VBF/VH/ttH and 8 TeV production where physically relevant",
          "Full QCD/EW theory uncertainty including missing total-width channels",
          "On-shell gg->H/A->tt interference and finite-width signal shape",
          "h125 and H1/H2 simultaneous multi-particle HiggsBounds consistency",
      ],
      "physical_Higgs_exclusion":None,"global_acceptance":None,
      "cases":experiments
    }
    out.write_text(json.dumps(report,allow_nan=False,sort_keys=True,indent=2)+"\n")
    print("ZEE_HA_HEAVY_64_SCOPED_COMPLETE",len(experiments),
          "N_OPTIMISTIC_MODEL_EXCLUDED",sum(x["stress_tests"][0]["selected_excluded_under_provisional_LO_model"] for x in experiments),
          "FULL_PHYSICAL_HIGGS_UNKNOWN",flush=True)
    return report

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--sushi",type=Path,required=True)
    a.add_argument("--widths",type=Path,required=True)
    a.add_argument("--dataset",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    x=a.parse_args()
    scan(x.sushi,x.widths,x.dataset,x.output)

if __name__=="__main__":main()
