#!/usr/bin/env python3
"""Join source-pinned real 64-case Zee HiggsTools/HDECAY/SusHi diagnostics.

OUTPUT is intentionally a *declared-order diagnostic constraint ledger*.
It does not convert a reduced HiggsSignals Delta-chi2 into a 95% confidence
test, an omitted HiggsBounds process into zero, or an incomplete heavy-Higgs
width into a physical one. This prepares the parameter-space scan cutflow,
without claiming physical allowed-space coverage.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path

def load(path,expected_count,field):
    raw=path.read_bytes()
    d=json.loads(raw)
    if d.get("global_acceptance") is not None or d.get(field)!=expected_count:
        raise ValueError(f"Unqualified or incomplete source evidence: {path}")
    if len(d.get("cases",[]))!=expected_count:
        raise ValueError("Source case count mismatch")
    return d,hashlib.sha256(raw).hexdigest()

def keyed(cases,tag):
    d={}
    for x in cases:
        key=(int(x["scalar_id"]),str(x["ordering"]),int(x["seed"]))
        if key in d:raise ValueError(f"Repeated source card in {tag}: {key}")
        d[key]=x
    if len(d)!=64 or len({k[0] for k in d})!=16:
        raise ValueError(f"Not complete original 16x4 source in {tag}")
    return d

def finite(x,name):
    if not isinstance(x,(int,float)) or not math.isfinite(x):
        raise ValueError(f"Missing/nonfinite source observable {name}")
    return float(x)

def selected_max(rows,field):
    if not isinstance(rows,dict) or not rows:
        raise ValueError("Expected source observed-limit selection is missing")
    return max(finite(v[field],field) for v in rows.values())

def join(hs_path:Path,hb125_path:Path,charged_path:Path,heavy_path:Path,output:Path):
    if output.exists():raise FileExistsError("Do not overwrite published constraint ledger")
    sources={}
    for name,path,n,field in (
        ("h125_higgssignals",hs_path,64,"n_h125_cases"),
        ("h125_higgsbounds",hb125_path,64,"n_h125_source_cases"),
        ("both_charged_higgsbounds",charged_path,64,"source_families"),
        ("heavy_HA_higgsbounds",heavy_path,64,"source_64_family"),
    ):
        d,digest=load(path,n,field)
        sources[name]={"data":d,"sha256":digest,"path":str(path)}
    keyed_sources={name:keyed(v["data"]["cases"],name) for name,v in sources.items()}
    reference=set(next(iter(keyed_sources.values())))
    if any(set(v)!=reference for v in keyed_sources.values()):
        raise ValueError("Higgs sectors use different scalar/neutrino/seed cards")
    results=[]
    for key in sorted(reference):
        h=keyed_sources["h125_higgssignals"][key]
        hb=keyed_sources["h125_higgsbounds"][key]
        charged=keyed_sources["both_charged_higgsbounds"][key]
        heavy=keyed_sources["heavy_HA_higgsbounds"][key]
        if any(q.get("global_acceptance") is not None for q in (h,hb,charged,heavy)):
            raise ValueError("Individual source case promoted to full model status")
        delta=finite(h["delta_chi2_h125_restricted"],"h125 Delta chi2")
        if delta < -300:raise ValueError("Gross HiggsSignals source inconsistency")
        if heavy.get("full_Higgs") not in ("UNKNOWN",None):
            raise ValueError("Heavy width provisional envelope was promoted")
        h125_ex=bool(hb["h125_only_approx_excluded"])
        charged_ex=bool(charged["scoped_13TeV_public_model_excluded"])
        heavy0=heavy["cases"][0]
        if not math.isclose(heavy0["assumed_additional_positive_width_fraction_of_known"],0,abs_tol=1e-14):
            raise ValueError("Heavy neutral baseline is not known-width sum")
        heavy_ex=bool(heavy0["selected_scoped_only_excluded"])
        row={
            "scalar_id":key[0],"ordering":key[1],"seed":key[2],
            "h125_HiggsSignals_delta_chi2_vs_same_dataset_SM":delta,
            "h125_HiggsSignals_formal_95CL":None,
            "h125_HiggsBounds_selected_observed_max":selected_max(hb["selected_limits"],"observed_ratio"),
            "H1_H2_matched_13TeV_HiggsBounds_selected_observed_max":selected_max(charged["selected_limits"],"observed_ratio"),
            "heavy_HA_LO_known_width_optimistic_HiggsBounds_selected_observed_max":selected_max(heavy0["selected"],"observed_ratio"),
            "heavy_HA_width_factor_tests":[float(z["assumed_additional_positive_width_fraction_of_known"]) for z in heavy["cases"]],
            "direct_search_h125_restricted_excluded":h125_ex,
            "direct_search_charged_matched_restricted_excluded":charged_ex,
            "direct_search_HA_optimistic_LO_restricted_excluded":heavy_ex,
            "all_evaluated_direct_search_subsets_below_selected_limits":not (h125_ex or charged_ex or heavy_ex),
            "h125_fit_diagnostic_delta_chi2_above_9":delta>9.0,
            "h125_fit_diagnostic_threshold_is_statistical_exclusion":False,
            "missing_nonstandard_heavy_searches":True,
            "physical_HiggsSignals_95CL":None,
            "full_HiggsBounds_observed_exclusion":None,
            "global_acceptance":None
        }
        for name in ("h125_HiggsBounds_selected_observed_max",
                     "H1_H2_matched_13TeV_HiggsBounds_selected_observed_max",
                     "heavy_HA_LO_known_width_optimistic_HiggsBounds_selected_observed_max"):
            if row[name]<0:raise ValueError("Negative observed ratio")
        results.append(row)
    if len(results)!=64:
        raise ValueError("Incomplete source cases")
    srcsummary={name:{"sha256":s["sha256"],"path":s["path"]} for name,s in sources.items()}
    counts={
        "n_source_cases":64,
        "n_scalar_spectra":16,
        "n_all_evaluated_direct_search_subsets_below_selected_limits":
          sum(r["all_evaluated_direct_search_subsets_below_selected_limits"] for r in results),
        "n_h125_delta_chi2_greater_than_9_DIAGNOSTIC_ONLY":
          sum(r["h125_fit_diagnostic_delta_chi2_above_9"] for r in results),
        "n_globally_allowed_Zee_cases":None,
    }
    report={
      "schema":"zee-pheno-16x4-public-Higgs-diagnostic-not-physical-global-constraint-v1",
      "sources":srcsummary,"summary":counts,"cases":results,
      "model_scope":"General Zee lepton Yukawas, Type-II quark sector, two charged mass eigenstates",
      "caveat":"All evaluated observed-search subsets are source-conditional; h125 DeltaChi2 is diagnostic without a declared test-statistic distribution. Heavy-H/A known widths are incomplete. Missing charged, H/A exotic, offshell, finite-width, interference and experiment applicability remain unresolved.",
      "physical_Higgs":"UNKNOWN","full_Higgs_exclusion":None,"global_acceptance":None,
    }
    output.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("ZEE_HIGGS_CONSTRAINT_JOIN_64",counts,
          "PHYSICAL_HIGGS_UNKNOWN",flush=True)
    for sid in (15673,15591,2264,14555):
        q=[r for r in results if r["scalar_id"]==sid]
        print("ZEE_HIGGS_SCOPED",sid,
              "DELTA_CHI2_RANGE",[min(x["h125_HiggsSignals_delta_chi2_vs_same_dataset_SM"] for x in q),max(x["h125_HiggsSignals_delta_chi2_vs_same_dataset_SM"] for x in q)],
              "MAX_CHARGED_OBS",max(x["H1_H2_matched_13TeV_HiggsBounds_selected_observed_max"] for x in q),
              "MAX_HEAVY_OBS",max(x["heavy_HA_LO_known_width_optimistic_HiggsBounds_selected_observed_max"] for x in q),
              "GLOBAL_UNKNOWN",flush=True)
    return report

def main():
    p=argparse.ArgumentParser()
    for name in ("hs","hb125","charged","heavy","output"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    join(a.hs,a.hb125,a.charged,a.heavy,a.output)

if __name__=="__main__":
    main()
