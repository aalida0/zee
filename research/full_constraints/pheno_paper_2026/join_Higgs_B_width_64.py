#!/usr/bin/env python3
"""Merge all-64 public Higgs, B-leading-source and threshold evidence for scan triage.

This is a deterministic *prioritization overlay*, NOT a frequentist 95% CL
global model acceptance. The source 64 lepton textures were algebraically
engineered; counts are therefore not parameter-volume survival fractions.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

H125_MATERIALITY_DELTA_CHI2_DIAGNOSTIC=9.0

def join_case(f,h,t,scalar):
    key=(f["id"],f["ordering"],f["seed"])
    if key!=(h["scalar_id"],h["ordering"],h["seed"]) or key!=(t["scalar_id"],t["ordering"],t["seed"]):
        raise ValueError("Cross-source exact scalar and neutrino family identity mismatch")
    if f["scalar_sha256"]!=scalar["scalar_sha256"]:
        raise ValueError("Scalar hash changed between source and scan")
    if h.get("global_acceptance") is not None or t.get("global_acceptance") is not None:
        raise ValueError("A partial Higgs-screen source declared full acceptance")
    if h.get("full_HiggsBounds_observed_exclusion") is not None or h.get("physical_HiggsSignals_95CL") is not None:
        raise ValueError("Partial Higgs experimental result promoted to physical exclusion")
    if t.get("actual_resonance_shape_validation") is not None or t.get("metrics",{}).get("inferred_narrow_width_allowed") is not None:
        raise ValueError("Unknown width/shape validity wrongly certified")
    m=t["metrics"]
    bsource=scalar["published_Eq4_nominal_gaussian_inside"]
    if not isinstance(bsource,bool):raise ValueError("Missing declared leading source B screen")
    direct=h["all_evaluated_direct_search_subsets_below_selected_limits"]
    if not isinstance(direct,bool):raise ValueError("Missing scoped HiggsBounds comparison")
    far=m["all_open_H1W_and_H2H1Z_far_five_widths"]
    if not isinstance(far,bool):raise ValueError("Unknown source cascade threshold domain")
    widths=[float(v) for v in m["source_width_floor_over_mass"].values()]
    if any(not math.isfinite(v) or v<=0 for v in widths):
        raise ValueError("Invalid source Higgs width floor")
    chi=float(h["h125_HiggsSignals_delta_chi2_vs_same_dataset_SM"])
    if not math.isfinite(chi):raise ValueError("Invalid source h125 HiggsSignals delta chi2")
    relative_small=chi<=H125_MATERIALITY_DELTA_CHI2_DIAGNOSTIC
    # This is a conservative, practical followup choice; B=LO-NP Gaussian,
    # h125=declared diagnostic (not calibrated CL), thresholds=5 source widths
    # (not physical NWA), HB only named experimentally covered channels.
    # No one of these is an unqualified physical PASS.
    tier0=bool(bsource and direct)
    tier1=bool(tier0 and far)
    tier2=bool(tier1 and relative_small)
    return {
        "scalar_id":key[0],"ordering":key[1],"seed":key[2],
        "source_scalar_sha256":f["scalar_sha256"],
        "source_B_published_2026_LO_NP_one_sided_Gaussian":bsource,
        "B_full_theory_uncertainty_and_NNLO_physical_rate":None,
        "named_higgs_direct_13TeV_HB_subsets_below_selected_limits":direct,
        "h125_restricted_effective_HS_delta_chi2":chi,
        "h125_relative_penalty_below9_is_diagnostic_not_95CL":relative_small,
        "five_source_widths_cascade_buffer":far,
        "source_width_floor_over_mass":m["source_width_floor_over_mass"],
        "complete_neutral_width_nwa_and_tt_interference":None,
        "source_B_plus_named_direct_scoped_screen":tier0,
        "source_B_plus_direct_and_threshold_well_separated":tier1,
        "source_B_direct_threshold_and_h125_small_penalty_for_followup":tier2,
        "full_LFV":None,"physical_Higgs":None,
        "global_acceptance":None,
    }

def run(fresh:Path,higgs:Path,thresholds:Path,out:Path):
    if out.exists():raise FileExistsError("No overwrite of incomplete-source triage")
    s=json.loads(fresh.read_text())
    h=json.loads(higgs.read_text())
    t=json.loads(thresholds.read_text())
    if (s.get("new_neutrino_family_count")!=64 or h.get("global_acceptance") is not None
        or t.get("n_case")!=64 or t.get("global_acceptance") is not None):
        raise ValueError("Original 64 family source/combined public Higgs/threshold evidence incomplete")
    fcases={(r["id"],r["ordering"],r["seed"]):r for r in s["families"]}
    hcases={(r["scalar_id"],r["ordering"],r["seed"]):r for r in h["cases"]}
    tcases={(r["scalar_id"],r["ordering"],r["seed"]):r for r in t["cases"]}
    originals={r["scalar_id"]:r for r in s["scalars"]}
    if not(len(fcases)==len(hcases)==len(tcases)==64 and set(fcases)==set(hcases)==set(tcases)):
        raise ValueError("B, Higgs, width provenance case keys do not join exactly")
    cases=[join_case(fcases[k],hcases[k],tcases[k],originals[k[0]]) for k in sorted(fcases)]
    summary={
        "n_new_engineered_lepton_models":len(cases),
        "n_source_B_LO_NP_one_sided_Gaussian":sum(c["source_B_published_2026_LO_NP_one_sided_Gaussian"] for c in cases),
        "n_named_HiggsBounds_selected_below1":sum(c["named_higgs_direct_13TeV_HB_subsets_below_selected_limits"] for c in cases),
        "n_cascade_threshold_far_five_source_widths":sum(c["five_source_widths_cascade_buffer"] for c in cases),
        "n_h125_small_relative_chi2_diagnostic":sum(c["h125_relative_penalty_below9_is_diagnostic_not_95CL"] for c in cases),
        "n_B_and_named_Higgs_direct":sum(c["source_B_plus_named_direct_scoped_screen"] for c in cases),
        "n_B_direct_and_well_separated_threshold":sum(c["source_B_plus_direct_and_threshold_well_separated"] for c in cases),
        "n_B_direct_threshold_h125_small_relative_diagnostic":sum(c["source_B_direct_threshold_and_h125_small_penalty_for_followup"] for c in cases),
        "followup_scalar_ids":sorted({c["scalar_id"] for c in cases if c["source_B_direct_threshold_and_h125_small_penalty_for_followup"]}),
        "source_selected_families_not_statistical_sampling":True,
        "physical_global_acceptance":None,
    }
    report={
        "schema":"zee-2026-64-source-B-Higgs-width-scoped-followup-prioritization-not-physical-acceptance-v1",
        "source_sha256":{k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in
                  (("fresh",fresh),("higgs",higgs),("thresholds",thresholds))},
        "n_cases":len(cases),"h125_diagnostic_relative_delta_chi2_cut":H125_MATERIALITY_DELTA_CHI2_DIAGNOSTIC,
        "model_scope":"16 preselected scalar cards x 4 algebraically LFV-suppressed Yukawa cases, not an unbiased scan",
        "do_not_interpret_counts_as_allowed_volume":True,
        "limitations":[
          "Physical two-state NNLO B uncertainty missing (published 2026 LO-NP central only)",
          "Full one-loop mu->3e and mu-e conversion plus two-loop Zee lepton flavor coverage missing",
          "HiggsSignals delta chi2 is a named relative tension diagnostic, not calibrated exclusion",
          "Heavy H/A Zgamma and finite-width/nonresonant/interference effects not validated",
          "HiggsBounds lists only included 13 TeV direct channels; exotic cascades and 8 TeV gaps remain",
        ],
        "physical_Higgs":"UNKNOWN","full_LFV":"UNKNOWN",
        "global_acceptance":None,"summary":summary,"cases":cases}
    out.write_text(json.dumps(report,allow_nan=False,sort_keys=True,indent=2)+"\n")
    print("ZEE_LO_SCOPED_FOLLOWUP_64",json.dumps(summary,sort_keys=True),"GLOBAL_UNKNOWN",flush=True)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fresh",type=Path,required=True)
    p.add_argument("--higgs",type=Path,required=True)
    p.add_argument("--thresholds",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    run(args.fresh,args.higgs,args.thresholds,args.output)
if __name__=="__main__":main()
