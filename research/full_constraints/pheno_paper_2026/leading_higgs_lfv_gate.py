#!/usr/bin/env python3
"""Publication-safe leading-order Higgs/LFV cutflow for 64 Zee flavor families.

INPUT is the reproducible native per-family calculation emitted by
leading_higgs_lfv_64.py; the original 16 scalar cards are not random
global Zee draws. This records *actual numerical upper limits on named
partial contributions* separately from physical LFV/Higgs acceptance.

The following named processes are computed at declared order:
- h125->mutau and etau: Gamma(partial)/Gamma_bb positive-width *upper*
  envelope; experimental BR measurements use production assumptions.
- mu->e gamma: source retained scalar one-loop + named Barr-Zee terms.
- mu->3e: neutral tree contact and **dipole-dominance-only** estimate,
  Cauchy upper for sum of just those two amplitudes, NOT full one-loop.
- tau->3mu: neutral tree contact only.
- Al conversion: dipole dominance only, not the full one-loop
  vector/monopole, scalar quark, nuclear operators.
- H and A: source independent all on-shell two-body tree partial widths
  at each particular scalar, NOT QCD/loop-complete HiggsWidths/B/HS.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

THRESHOLDS={
    "MEGII_mu_to_e_gamma_90CL":1.5e-13,
    "SINDRUM_mu_to_3e_90CL":1.0e-12,
    "BelleII_tau_to_3mu_90CL":1.9e-8,
    "ATLAS_h125_to_mutau_95CL":0.0018,
    "ATLAS_h125_to_etau_95CL":0.0020,
}
REFERENCES={
    "MEGII_mu_to_e_gamma_90CL":"MEG II EPJC 85 (2025) 7, BR<1.5e-13",
    "SINDRUM_mu_to_3e_90CL":"SINDRUM Collaboration Nucl.Phys.B299(1988)1-6, 90CL 1e-12; no Mu3e projection treated as exclusion",
    "BelleII_tau_to_3mu_90CL":"Belle II 424 fb-1 2024 90CL 1.9e-8; see BELLE2-CONF-PROC-2024-013",
    "ATLAS_h125_to_mutau_95CL":"ATLAS JHEP07(2023)166, arXiv:2302.05225 observed BR<0.18%",
    "ATLAS_h125_to_etau_95CL":"ATLAS JHEP07(2023)166, arXiv:2302.05225 observed BR<0.20%",
}


def evaluate(source:Path,out:Path):
    if out.exists(): raise FileExistsError("Refuse overwriting a coverage receipt")
    raw=source.read_bytes();d=json.loads(raw)
    if (d.get("n_evaluated")!=64 or len(d.get("families",[]))!=64
        or d.get("full_LFV")!="UNKNOWN" or d.get("full_Higgs")!="UNKNOWN"
        or d.get("global_acceptance") is not None):
        raise ArithmeticError("Original 64 source card quantity or physics scope changed")
    summary={}
    cases=[]
    for x in d["families"]:
        h=x["h125"];lf=x["lfv"];heavy=x["heavy_neutral"]
        if (x["full_LFV"]!="UNKNOWN" or x["full_Higgs"]!="UNKNOWN"
            or x["global_acceptance"] is not None):
            raise ArithmeticError("Unjustified global acceptance in source")
        for name,q in (("h",h),("H",heavy["H"]),("A",heavy["A"])):
            total=q.get("full_model_total_width_GeV",q.get("physical_total_width_GeV"))
            if total is not None:raise ArithmeticError("Incomplete source total width accidentally treated as full")
        observations={
            "mu_to_e_gamma_retained":lf["source_radiative"]["mu_to_e_gamma"]["selected_partial_BR"],
            "mu_to_3e_tree_plus_photon_dipole_kinematic_Cauchy":lf["mu3e_tree_plus_dipole_kinematic_Cauchy_upper"],
            "tau_to_3mu_tree_neutral_only":lf["tau_to_3mu_neutral_tree_contact_BR"],
            "h125_mu_tau_over_Gamma_bb_upper":h["BR_mutau_over_Gamma_bb_upper_bound"],
            "h125_e_tau_over_Gamma_bb_upper":h["BR_etau_over_Gamma_bb_upper_bound"],
            "Al_conversion_dipole_only":lf["mu_e_conversion_Al_dipole_dominance_only"],
        }
        if any(z is None or not math.isfinite(z) or z<0 for z in observations.values()):
            raise ArithmeticError("Unphysical or missing source leading observable")
        screens={
            "mu_to_e_gamma_retained":observations["mu_to_e_gamma_retained"]<THRESHOLDS["MEGII_mu_to_e_gamma_90CL"],
            "mu_to_3e_tree_and_dipole_subset":observations["mu_to_3e_tree_plus_photon_dipole_kinematic_Cauchy"]<THRESHOLDS["SINDRUM_mu_to_3e_90CL"],
            "tau_to_3mu_tree_subset":observations["tau_to_3mu_tree_neutral_only"]<THRESHOLDS["BelleII_tau_to_3mu_90CL"],
            "h125_mu_tau_partial_ratio_upper_screen":observations["h125_mu_tau_over_Gamma_bb_upper"]<THRESHOLDS["ATLAS_h125_to_mutau_95CL"],
            "h125_e_tau_partial_ratio_upper_screen":observations["h125_e_tau_over_Gamma_bb_upper"]<THRESHOLDS["ATLAS_h125_to_etau_95CL"],
        }
        if not all(screens.values()):
            raise ArithmeticError("At least one constructed family violates the predeclared partial-rate screen")
        row={
            "scalar_id":x["scalar_id"],"ordering":x["ordering"],"seed":x["seed"],
            "observable_values":observations,
            "source_subset_screens":screens,
            "H_mass_GeV":heavy["H"]["mass_GeV"],"A_mass_GeV":heavy["A"]["mass_GeV"],
            "H_onshell_tree_width_sum_GeV":heavy["H"]["known_tree_disjoint_sum_GeV"],
            "A_onshell_tree_width_sum_GeV":heavy["A"]["known_tree_disjoint_sum_GeV"],
            "H_missing_open_2body_tree_count":len(heavy["H"]["on_shell_missing"]),
            "A_missing_open_2body_tree_count":len(heavy["A"]["on_shell_missing"]),
            "h125_known_channel_sum_GeV":h["matched_known_channel_sum_GeV"],
            "h125_lepton_diagonal_complex_kappas":h["Zee_lepton_diagonal_kappas_complex"],
            "h125_HiggsSignals_full_model_fit":None,
            "heavy_HA_HiggsBounds_observed_search":None,
            "mu_to_3e_full_one_loop":None,
            "Al_conversion_full_one_loop":None,
            "Au_conversion_full_one_loop":None,
            "gauge_complete_two_loop_LFV":None,
            "physical_Higgs":"UNKNOWN","physical_LFV":"UNKNOWN","global_acceptance":None
        }
        cases.append(row)
    if len({(r["scalar_id"],r["ordering"],r["seed"]) for r in cases})!=64:
        raise ArithmeticError("Repeated or missing flavor cards")
    ids=sorted({r["scalar_id"] for r in cases})
    if len(ids)!=16:
        raise ArithmeticError("Scalar source count changed")
    for id in ids:
        subset=[r for r in cases if r["scalar_id"]==id]
        if len(subset)!=4:raise ValueError("Each scalar must have 2x2 neutrino families")
        summary[str(id)]={
            "n_families":len(subset),
            "h125_known_GeV_range":[min(r["h125_known_channel_sum_GeV"] for r in subset),
                                    max(r["h125_known_channel_sum_GeV"] for r in subset)],
            "max_retained_mu_e_gamma_BR":max(r["observable_values"]["mu_to_e_gamma_retained"] for r in subset),
            "max_mu3e_tree_and_dipole_subset_BR":max(r["observable_values"]["mu_to_3e_tree_plus_photon_dipole_kinematic_Cauchy"] for r in subset),
            "max_tau_to_3mu_neutral_tree_BR":max(r["observable_values"]["tau_to_3mu_tree_neutral_only"] for r in subset),
            "H_A_all_onshell_tree_channels_computed":
                all(r["H_missing_open_2body_tree_count"]==0 and r["A_missing_open_2body_tree_count"]==0 for r in subset),
            "physical_Higgs":"UNKNOWN","physical_LFV":"UNKNOWN","globally_allowed_count":None
        }
    report={
        "schema":"zee-2026-16-scalar-64-leading-Higgs-LFV-scoped-screens-v1",
        "source_sha256":hashlib.sha256(raw).hexdigest(),
        "n_original_selected_scalar_spectra":16,
        "n_algebraically_constructed_flavor_families":64,
        "experimental_limits":THRESHOLDS,
        "experimental_references":REFERENCES,
        "n_source_partial_subset_screen_pass_all":sum(all(r["source_subset_screens"].values()) for r in cases),
        "full_Higgs_signals_or_search_consumer_executed":False,
        "full_mu3e_one_loop_executed":False,
        "full_mu_e_conversion_executed":False,
        "full_Zee_mixed_two_loop_LFV_executed":False,
        "model_wide_allowed_region_established":False,
        "physical_Higgs":"UNKNOWN","physical_LFV":"UNKNOWN","global_acceptance":None,
        "interpretation":"Every PASS is a named partial / selected perturbative-order materiality test. Total one-loop LFV and observed Higgs search vetos are unavailable; zero full-acceptance claims.",
        "by_scalar":summary,
        "cases":cases
    }
    out.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("SOURCE_64_LEADING_HIGGS_LFV_GATES",len(cases),
          "PARTIAL_SCREEN_PASS",report["n_source_partial_subset_screen_pass_all"],
          "HIGGS_FULL_UNKNOWN LFV_FULL_UNKNOWN",flush=True)
    for id in (15673,15591,14074):
        s=summary[str(id)]
        print("MAIN_PHENO_CANDIDATE",id,
            "H125_GEV",s["h125_known_GeV_range"],
            "MAX_MU_E_GAM",s["max_retained_mu_e_gamma_BR"],
            "MAX_MU3E_SUB",s["max_mu3e_tree_and_dipole_subset_BR"],
            "MAX_TAU3MU_TREE",s["max_tau_to_3mu_neutral_tree_BR"],
            "H_A_ONSHELL_TREE_COMPLETE",s["H_A_all_onshell_tree_channels_computed"],
            "FULL_UNKNOWN",flush=True)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    evaluate(args.input,args.output)

if __name__=="__main__":main()
