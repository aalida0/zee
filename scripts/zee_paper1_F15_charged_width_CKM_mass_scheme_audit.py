#!/usr/bin/env python3
"""F15: source-closed charged Zee width audit and CKM/light-quark additions.

This audits the original F13 complex f/Y at exactly the original scalar
point, reconstructs B3 charged inclusive width inventory, and joins the
original F14 13-TeV cross sections. Adds all 3x3 CKM Type-II-like H+ -> u d
two-body fermionic modes at LO, REPLACING the prior Vtb=1, mb=4.7 GeV tb
channel, NOT double counting it. Compares fixed bottom-mass proxy vs two
running-mass-inspired sensitivity scenarios (not a QCD theory error).

No NNLO flavor, loop, three-body, QCD-corrected widths, validated UFO,
MadWidth or "full" physical total is inferred. In particular this is an
on-shell tree-level TWO-BODY SUBSET check, NOT the promised complete
two/three-body 5-state decay calculation.

Branching fractions with missing positive modes decrease for fixed
numerator/inputs, but there is NO rigorous physical upper bound once QCD
corrections, parameter running, possible loop amplitudes or 3-body
interference are varied.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from pathlib import Path
import numpy as np
from gateA1b_hierarchical_no_seed import target_neutrino_matrix
from gateB3_general_zee_charged_lepton_widths import (
    evaluate as b3_evaluate, complex_matrix)
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import (
    ROOT,digest,writejson)
from zee_paper1_F14_LHCHXSWG_13TeV_physical_unit_cascade import (
    ORIGINAL as F13_DIR, STATUS as F14_STATUS,OUTNAME as F14_CSV,
    read_f13
)
from zee_paper1_F13_heavy_flavor_aware_final_scan import STATUS as F13_STATUS

STATUS="F15_EXACT_F13_COMPLEX_YUKAWA_CHARGED_2BODY_LO_CKM_MASS_STRESS_NOT_FULL_WIDTH"
TARGETS=("F13_heavy_0001330","F13_heavy_0000981","F13_heavy_0001003")
OUTCSV="F15_three_real_Zee_CKM_mass_stress_13TeV_NOT_COMPLETE.csv"
FCCCSV="F15_85_100TeV_required_TypeII_production_NOT_a_prediction.csv"
CONTROL="F15_8_light_quark_missing_modes_and_widths_NOT_COMPLETE.csv"
UP=("u","c","t")
DOWN=("d","s","b")
# Fixed mass proxies used for SOURCE-CONVENTION diagnostics, not claims
# of correct running masses in a 2026 precision scheme.
MUP={"u":.0022,"c":1.27,"t":172.}
MDN={"d":.0047,"s":.093,"b":4.7}
GF=1.1663787e-5
VABS=np.array([
    [.97401,.22650,.00361],
    [.22636,.97320,.04053],
    [.00854,.03978,.999172],
],float)
# These are NOT confidence-level intervals on mb; just a first direct
# sensitivity test for replacing a "pole-ish" mb with running mb.
BOTTOM_VARIANTS={"fixed_b4p7":4.7,
                 "lower_b3p0_stress":3.0,
                 "lower_b2p5_stress":2.5}
MISSING=(
    "complete neutral and charged model tree-level 2/3-body inventory from physically matched UFO",
    "on-shell 2-body subset misses three-body virtual W/Z/H and loop decays",
    "NLO QCD-corrected tb/cs/cb widths with consistent running masses/schemes",
    "finite-width overlapping-resonance/interference and continuum effects",
    "source-consistent full 2026 B->Xs gamma two-scalar NNLO prediction",
    "complete one-/two-loop Zee LFV and 2026 neutrino likelihood",
    "HiggsTools, quark alignment and FCNC, charge-breaking/global vacuum",
    "13.6/14TeV updated matched production and detector-level simulation",
    "FCC-hh 85/100TeV independent validated hadronic production and backgrounds",
)
def finite(v,label):
    if isinstance(v,bool):raise ValueError("Boolean "+label)
    x=float(v)
    if not math.isfinite(x):raise ValueError("Nonfinite "+label)
    return x
def close(a,b,label,rtol=3e-9,atol=1e-11):
    if not math.isclose(finite(a,label),finite(b,label),rel_tol=rtol,
                        abs_tol=atol):
        raise ValueError("Source mismatch "+label+" "+str(a)+" != "+str(b))
def validate_ckm():
    if VABS.shape!=(3,3) or not (VABS>=0).all() or not (VABS<=1).all():
        raise ValueError("Invalid CKM")
    rows=np.sum(VABS**2,axis=1)
    cols=np.sum(VABS**2,axis=0)
    if max(abs(rows-1))>.005 or max(abs(cols-1))>.005:
        raise ValueError("CKM magnitudes inconsistent with approximate unitarity")
    return {"row_sum_squares":rows.tolist(),
            "column_sum_squares":cols.tolist(),
            "ckm_is_external_approximate_not_fit":True}

def charged_quark_width(mass,up,down,tanbeta,doublet2,mb=4.7):
    """Type-II charged H+ -> u_i anti-d_j one charge, exact LO 2-body spin
    trace with finite masses and CKM. Formula matches Gate6 tb at |Vtb|=1.
    """
    mass=finite(mass,"charged mass")
    t=finite(tanbeta,"tanbeta")
    db=finite(doublet2,"doublet fraction")
    mb=finite(mb,"mb scenario")
    if mass<=0 or t<=0 or not 0<=db<=1 or mb<=0:
        raise ValueError("Nonphysical quark width inputs")
    if up not in UP or down not in DOWN:
        raise ValueError("Invalid quark flavor")
    a=MUP[up];b=mb if down=="b" else MDN[down]
    if mass<=a+b:return 0.
    ru=(a/mass)**2;rd=(b/mass)**2
    triangle=max(0.,(1-ru-rd)**2-4*ru*rd)
    part=(a*a/(t*t)+b*b*t*t)*(1-ru-rd)-4*a*a*b*b/mass**2
    value=(3*GF*mass/(4*math.sqrt(2)*math.pi)*db*
           math.sqrt(triangle)*max(0.,part)*
           float(VABS[UP.index(up),DOWN.index(down)]**2))
    if not math.isfinite(value) or value<0:
        raise ValueError("Invalid quark partial width")
    return value

def quark_inventory(mass,tanbeta,doublet2,mb):
    out={up+dn:charged_quark_width(
        mass,up,dn,tanbeta,doublet2,mb) for up in UP for dn in DOWN}
    if len(out)!=9 or not all(math.isfinite(v) and v>=0 for v in out.values()):
        raise ValueError("Incomplete charged quark two-body inventory")
    return out

def join_origins(f13dir,f14dir):
    folder=Path(f13dir).resolve()
    f14dir=Path(f14dir).resolve()
    f13s,selected,ranked,allrows,proof=read_f13(folder)
    f14s=json.loads((f14dir/"summary.json").read_text())
    f14m=json.loads((f14dir/"manifest.json").read_text())
    if (f14s.get("status")!=F14_STATUS or
        f14m.get("status")!=F14_STATUS or
        f14m.get("summary_SHA256")!=digest(f14dir/"summary.json") or
        f14s.get("source_F13",{}).get("F13_summary_SHA256")!=proof[
            "F13_summary_SHA256"] or
        f14s.get("eight_same_scalar_neutrino_lepton_widths_evaluated")!=8 or
        not f14s.get("none_are_complete_physical_Zee_rates")):
        raise ValueError("F14 source or exact F13 source provenance mismatch")
    if f14s.get("outputs_SHA256",{}).get(F14_CSV)!=digest(f14dir/F14_CSV):
        raise ValueError("F14 eight benchmark CSV corrupted")
    with (f14dir/F14_CSV).open(newline="") as stream:
        production=list(csv.DictReader(stream))
    if len(production)!=8 or set(x["candidate_id"] for x in production)!=set(
        x["candidate_id"] for x in ranked):
        raise ValueError("F13/F14 model identities incompatible")
    by_id={r["candidate_id"]:r for r in ranked}
    prod={r["candidate_id"]:r for r in production}
    for name,row in by_id.items():
        v=prod[name]
        for a,b in (("mH1","mH1_GeV"),("mH2","mH2_GeV"),
                    ("tanbeta","tanbeta"),("gamma","gamma_rad")):
            close(row[a],v[b],name+" "+a)
        close(float(v["13TeV_TypeII_sigma_times_included_cascade_proxy_pb"]),
              float(v["TypeII_Santander_NLO13TeV_sigma_pb"])*
              float(row["lepton_included_cascade_proxy_NOT_pb"]),
              name+" F14 production no-double-weight")
    return by_id,prod,{
        **proof,
        "F14_summary_SHA256":digest(f14dir/"summary.json"),
        "F14_manifest_SHA256":digest(f14dir/"manifest.json"),
        "F14_8_csv_SHA256":digest(f14dir/F14_CSV),
    }

def source_b3(f13dir,name,ranked_row):
    f13dir=Path(f13dir)
    matched=None
    for candidate in sorted(f13dir.glob("F13_priority_*_NOT_ALLOWED.json")):
        data=json.loads(candidate.read_text())
        if data["scalar"]["id"]!=name:continue
        if matched is not None:raise ValueError("Duplicate F13 priority ID")
        matched=data
    if matched is None:raise ValueError("Missing exact original F13 complex f/Y model "+name)
    scalar=matched["scalar"]
    if matched.get("physically_Zee_allowed") is not None:
        raise ValueError("Source F13 mislabeled full physical allowance")
    original=matched["neutrino_and_partial_lfv"]
    if original.get("status")!=(
         "NEUTRINO_EXACT_WITH_PARTIAL_LFV_AND_INCLUDED_CASCADE_ONLY"):
        raise ValueError("F13 original did not have exact solved neutrino and subset LFV")
    best=original["best"]
    for key in ("mH1","mH2","gamma","tanbeta"):
        close(scalar[key],ranked_row[key],name+" scalar solution "+key)
    f=complex_matrix(best["optimized_f"],"f")
    Y=complex_matrix(best["optimized_Y"],"Y")
    neutrino,_=target_neutrino_matrix()
    result=b3_evaluate(scalar,f,Y,neutrino)
    if result["candidate_id"]!=name or (
        result["status"]!=
        "GENERAL_ZEE_LEPTON_WIDTHS_LO_INCLUDED_ONLY_NOT_ALLOWED"):
        raise ValueError("B3 returned wrong or unsupported physical output")
    close(result["BR_H2_H1Z_included_general_Zee"],
          best["BR_H2_H1Z_included_channels_ONLY"],
          name+" original H2 H1 Z width fraction",rtol=5e-9,atol=5e-11)
    close(result["BR_H1_tb_included_general_Zee"],
          best["BR_H1_tb_included_channels_ONLY"],
          name+" original H1 tb width fraction",rtol=5e-9,atol=5e-11)
    close(result["production_weighted_partial_cascade_proxy"],
          best["charged_included_LO_cascade_proxy_NOT_pb"],
          name+" F13 saved B3 proxy",rtol=6e-9,atol=3e-10)
    close(result["production_weighted_partial_cascade_proxy"],
          ranked_row["lepton_included_cascade_proxy_NOT_pb"],
          name+" F13 ranked B3 proxy",rtol=6e-9,atol=3e-10)
    if result["neutrino_matrix_closure_eV"]>=1e-9:
        raise ValueError("F13 Yukawas no longer reconstruct neutrino target")
    return result,scalar,{
        "priority_record_SHA256":digest(candidate),
        "neutrino_matrix_closure_eV":result["neutrino_matrix_closure_eV"],
        "partial_lfv_score_NOT_full_CL":
            best["score_partial_LFV_max_ratio_NOT_Full_CL"],
        "complex_Y_and_f_recomputed_without_dropping_phases":True,
    }

def scenario(widths,scalar,xsec_typeii,mb):
    tb=math.tan(scalar["beta"])
    gamma=scalar["gamma"]
    doublet={"H1":math.cos(gamma)**2,"H2":math.sin(gamma)**2}
    # In a two-charged-state CP-conserving potential, a mixed
    # H2 -> H1 A coupling may be allowed. Old Gate6 omits it.
    # Do not silently accept a kinematically open unknown 2-body width.
    mixed_pseudoscalar_open=bool(
        scalar["mH2"] > scalar["mH1"]+scalar["ma"])
    results={}
    for state in ("H1","H2"):
        original=widths["partial_widths_included_GeV"][state]
        M=scalar["mH1"] if state=="H1" else scalar["mH2"]
        qq=quark_inventory(M,tb,doublet[state],mb)
        old_tb=original["tb"]
        if state=="H1" and mb==4.7:
            # Gate6 m_t, m_b, G_F and LO spin trace must match exactly
            # apart from Vtb^2. The new CKM table is not unitarity-exact.
            close(qq["tb"],old_tb*VABS[2,2]**2,
                  "H1 tb Gate6 normalization",rtol=1e-11,atol=1e-9)
        if state=="H2" and mb==4.7:
            close(qq["tb"],old_tb*VABS[2,2]**2,
                  "H2 tb Gate6 normalization",rtol=1e-11,atol=1e-9)
        rest=sum(v for k,v in original.items() if k!="tb")
        total=rest+sum(qq.values())
        if total<=0:raise ValueError("Bad charged width scenario")
        results[state]={
            "M_GeV":M,
            "old_tree_tb_width_Vtb_eq1_GeV":old_tb,
            "CKM_corrected_tb_width_GeV":qq["tb"],
            "CKM_other_8_quark_modes_GeV":sum(v for k,v in qq.items() if k!="tb"),
            "all_9_quark_widths_tree_LO_GeV":qq,
            "source_included_non_tb_width_GeV":rest,
            "new_2body_subset_total_GeV":total,
            "source_included_total_GeV":widths["totals_included_GeV"][state],
            "one_state_other_8_quark_fraction_of_new_total":
                sum(v for k,v in qq.items() if k!="tb")/total,
            "modified_subset_tb_fraction":qq["tb"]/total,
            "no_claim_QCD_or_all_3body_complete":True,
        }
    old=widths["production_weighted_partial_cascade_proxy"]
    high=results["H2"]
    low=results["H1"]
    numhigh=widths["partial_widths_included_GeV"]["H2"]["H1_Z"]
    newproxy=(math.sin(gamma)**2 *
              numhigh/high["new_2body_subset_total_GeV"] *
              low["CKM_corrected_tb_width_GeV"]/low["new_2body_subset_total_GeV"])
    if not 0<newproxy<1:raise ValueError("Nonphysical CKM subset cascade")
    return {
        "mb_in_quark_LO_width_GeV":mb,
        "source_B3_cascade_proxy_before_CKM":old,
        "modified_2body_subset_cascade_proxy_with_CKM":newproxy,
        "relative_new_over_original_B3_proxy":newproxy/old,
        "approximate_sigma13_product_pb":xsec_typeii*newproxy,
        "approximate_sigma13_Z_ee_mumu_product_pb":
            xsec_typeii*newproxy*.0673,
        "H1":low,"H2":high,
        "H2_to_H1_A_pseudoscalar_potentially_open_and_NOT_calculated":
            mixed_pseudoscalar_open,
        "H2_minus_H1_minus_A_threshold_GeV":
            scalar["mH2"]-scalar["mH1"]-scalar["ma"],
        "uncalculated_decays_can_only_reduce_ratio_AT_fixed_numerators":
            True,
        "actual_physical_signal_rate_pb":None,
        "physical_total_charged_widths_GeV":None,
    }

def calc_all(f13dir,f14dir):
    originals,prod,provenance=join_origins(f13dir,f14dir)
    validate_ckm()
    results=[]
    for name in TARGETS:
        b3,scalar,record=source_b3(f13dir,name,originals[name])
        xsec=finite(prod[name]["TypeII_Santander_NLO13TeV_sigma_pb"],
                    "xsec source")
        variants={label:scenario(b3,scalar,xsec,mb)
                  for label,mb in BOTTOM_VARIANTS.items()}
        # Must retain source F14 rate at precisely the same fixed B3
        # scalar/F/Y solution. No mixing factor is multiplied again.
        close(xsec*b3["production_weighted_partial_cascade_proxy"],
              prod[name]["13TeV_TypeII_sigma_times_included_cascade_proxy_pb"],
              name+" source 13TeV normalization",rtol=5e-9,atol=1e-11)
        results.append({
            "candidate_id":name,
            "source":record,
            "spectrum":{k:scalar[k] for k in
                        ("mH1","mH2","beta","gamma","mh2","ma","alpha","k12")},
            "source_F14_13TeV_included_only_estimate_pb":
                xsec*b3["production_weighted_partial_cascade_proxy"],
            "source_F14_TypeII13TeV_sigma_pb":xsec,
            "mb_input_stress_scenarios_NOT_an_NLO_uncertainty":variants,
            "full_Zee_model_allowed_or_excluded":None,
            "physical_inclusive_signal_pb":None,
        })
    return results,provenance

def fcc_production_thresholds(records, *,
    scenarios=(("FCC_HH_FSR_2025_85TeV",85000,20000),
               ("FCC_HH_CDR_100TeV",100000,30000)),
    n_events=(10,25,100),efficiencies=(.01,.05,.10)):
    """Only algebraic required production baseline, NEVER an 85/100TeV XS.

    N = L_fb * sigma_TypeII_fb * P_included_CKM * BR(Z->ee,mumu)
        * epsilon_full_selection.

    Actual detector efficiency, backgrounds, 85/100TeV TypeII/NLO
    rates and complete widths are UNKNOWN. Counts are illustrative.
    """
    output=[]
    for rec in records:
        gamma=finite(rec["spectrum"]["gamma"],"gamma")
        weight=math.sin(gamma)**2
        proxy=rec["mb_input_stress_scenarios_NOT_an_NLO_uncertainty"][
            "fixed_b4p7"]["modified_2body_subset_cascade_proxy_with_CKM"]
        if not 0<proxy<=weight<=1+1e-10:
            raise ValueError("FCC source did not preserve one doublet weight")
        for name,energy,Lfb in scenarios:
            if energy<=14000 or Lfb<=0:
                raise ValueError("FCC comparison requires credible pp design inputs")
            for count in n_events:
                if count<=0:raise ValueError("Events must be positive")
                for efficiency in efficiencies:
                    if not 0<efficiency<=1:
                        raise ValueError("Selection efficiency out of range")
                    min_typeii=count/(Lfb*.0673*efficiency*proxy)
                    output.append({
                        "candidate_id":rec["candidate_id"],
                        "design_scenario":name,
                        "proton_proton_sqrt_s_GeV":energy,
                        "design_integrated_luminosity_fb_inv":Lfb,
                        "event_count_target_NOT_significance":count,
                        "selection_efficiency_ASSUMED_NOT_simulated":efficiency,
                        "Z_to_ee_mumu_BR_approx":.0673,
                        "CKM_LO_included_channel_cascade_proxy_NOT_full_BR":
                            proxy,
                        "required_TypeII_like_baseline_sigma_at_this_energy_fb":
                            min_typeii,
                        "required_Zee_H2_associated_sigma_at_this_energy_fb":
                            min_typeii*weight,
                        "FCC_85_or_100TeV_actual_production_sigma_fb":None,
                        "complete_Zee_widths_and_observability_certified":False,
                    })
    return output

def run(args):
    out=Path(args.output).resolve()
    if out.exists():raise FileExistsError("No overwrite of previous F15 results")
    records,src=calc_all(args.f13_dir,args.f14_dir)
    out.mkdir(parents=True,exist_ok=False)
    simple=[]
    for record in records:
        source=record["source"]
        variants=record["mb_input_stress_scenarios_NOT_an_NLO_uncertainty"]
        row={"candidate_id":record["candidate_id"],
             "mH1_GeV":record["spectrum"]["mH1"],
             "mH2_GeV":record["spectrum"]["mH2"],
             "13TeV_source_F14_included_proxy_pb":
                record["source_F14_13TeV_included_only_estimate_pb"],
             "original_B3_neutrino_closure_eV":
                source["neutrino_matrix_closure_eV"],
             "original_B3_partial_LFV_max_ratio_NOT_full":
                source["partial_lfv_score_NOT_full_CL"],
             "physical_Zee_R_tbZ_pb":None,
             "fully_Zee_allowed":None}
        for label,v in variants.items():
            row[label+"_13TeV_included_2body_CKM_estimate_pb"]=v[
                 "approximate_sigma13_product_pb"]
            row[label+"_ratio_vs_F14"]=v[
                 "relative_new_over_original_B3_proxy"]
            row[label+"_H1_total_partial_GeV"]=v["H1"][
                 "new_2body_subset_total_GeV"]
            row[label+"_H2_total_partial_GeV"]=v["H2"][
                 "new_2body_subset_total_GeV"]
            row[label+"_H1_other_quark_width_GeV"]=v["H1"][
                 "CKM_other_8_quark_modes_GeV"]
            row[label+"_H2_other_quark_width_GeV"]=v["H2"][
                 "CKM_other_8_quark_modes_GeV"]
        simple.append(row)
        writejson(out/(record["candidate_id"]+"_all_LO_quark_channels_NOT_FULL.json"),
                  record)
    thresholds=fcc_production_thresholds(records)
    with (out/FCCCSV).open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(thresholds[0]))
        writer.writeheader();writer.writerows(thresholds)
    with (out/OUTCSV).open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(simple[0]))
        writer.writeheader();writer.writerows(simple)
    report={
      "status":STATUS,"source":src,
      "candidate_ids":list(TARGETS),
      "exact_F13_F14_compatible_source_and_complex_fY":True,
      "source_included_B3_totals_physically_complete":False,
      "tree_LO_CKM_3x3_quark_channels_counted_in_each_charge_state":9,
      "typeII_9_quark_channels_tree_LO_new":True,
      "mixed_pseudoscalar_H2_H1_A_open_in_any_selected":any(
           v["mb_input_stress_scenarios_NOT_an_NLO_uncertainty"][
             "fixed_b4p7"][
               "H2_to_H1_A_pseudoscalar_potentially_open_and_NOT_calculated"]
           for v in records),
      "bottom_mass_scenarios_NOT_theory_errors":BOTTOM_VARIANTS,
      "CKM_input_and_approximate_unitarity":validate_ckm(),
      "13TeV_typeII_matched_production_only":True,
      "approximate_signal_rates_NOT_complete_Zee_model":simple,
      "FCC_hh_85_or_100TeV_cross_sections_not_computed":True,
      "FCC_85_100_event_thresholds_only_not_cross_sections":True,
      "FCC_2025_85TeV_20ab_versus_CDR_100TeV_30ab_cases":True,
      "FCC_threshold_scenarios":len(thresholds),
      "full_two_three_body_complete":False,
      "precision_QCD_corrected_fermion_widths_computed":False,
      "independent_validated_physical_complex_Zee_UFO_used":False,
      "full_Zee_model_allowed_or_excluded":None,
      "paper1_GO_or_NOGO":None,
      "missing_critical_physics":MISSING,
      "script_SHA256":digest(Path(__file__)),
      "outputs_SHA256":{OUTCSV:digest(out/OUTCSV),
                        FCCCSV:digest(out/FCCCSV)},
    }
    writejson(out/"summary.json",report)
    writejson(out/"manifest.json",{
      "status":STATUS,"summary_SHA256":digest(out/"summary.json"),
      "full_model_allowed_or_excluded":None})
    for x in simple:
        print("F15_WIDTH_SENSITIVITY",x["candidate_id"],
              "F14_fb",round(x["13TeV_source_F14_included_proxy_pb"]*1000,7),
              "CKM_b4p7_fb",round(x[
                 "fixed_b4p7_13TeV_included_2body_CKM_estimate_pb"]*1000,7),
              "b3p0_STRESS_fb",round(x[
                 "lower_b3p0_stress_13TeV_included_2body_CKM_estimate_pb"]*1000,7),
              "b2p5_STRESS_fb",round(x[
                 "lower_b2p5_stress_13TeV_included_2body_CKM_estimate_pb"]*1000,7),
              "NOT_FULL_WIDTHS",flush=True)
    print("F15_STATUS",STATUS,"N",len(records),"COMPLETE_WIDTHS",False,
          "FCC_85_100TEV_XSEC",None,flush=True)
    print("F15_SUMMARY",out/"summary.json",flush=True)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--f13-dir",type=Path,default=F13_DIR)
    parser.add_argument("--f14-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    run(parser.parse_args())
if __name__=="__main__":
    main()
