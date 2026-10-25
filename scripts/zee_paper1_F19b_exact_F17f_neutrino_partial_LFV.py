#!/usr/bin/env python3
"""F19b: exact F17f SLHA/F17 complex Yukawas to neutrino + PARTIAL LFV.

Reconstructs the general Zee Chen-basis f,Y from original full-complex
SARAH cards, independently joins to F17 matrix JSON, checks fixed-NO
neutrino-matrix closure, then coherently evaluates existing validated-
subset one-loop, fermion-gamma and W-gamma Barr-Zee diagrams. Evaluates
tree-only 3-lepton partial rates and f-only universality. Missing
contributions and phase/oscillation likelihood forbid exclusions.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,tarfile
from pathlib import Path
import numpy as np

from zee_paper1_F19_integrated_scalar_EWPO_constraints import (
    CASES,F19_STATUS,F16_FILE,F17F_FILE,F17F_SUBDIR,
    get_bundle_bytes,sha,source_cards,scalar_input)
from zee_paper1_F17_inspect_real_SARAH_UFO import cmat
from gateA1b_hierarchical_no_seed import (
    scalar_kappa,reconstruct_neutrino,target_neutrino_matrix)
from gateA1c_charged_singlet_lfv import CHANNELS
from gateA1e_neutral_one_loop_dipoles import partial_radiative_br
from zee_barr_zee_fermion_dipoles import (
    one_loop_amplitudes,flav_bz_amplitudes)
from zee_gateD4_W_photon_barr_zee_27 import w_photon_amplitudes
from zee_lfv_backend import (
    TREE_CHANNELS,general_neutral_tree_BR,f_only_universality)
from gateB2_zee_neutrino_family_scan import subset_lfv
from zee_gateD2_neutrino_exact_partial_LFV_optimization import amplitude_subset

STATUS="F19B_EXACT_F17F_COMPLEX_NEUTRINO_PARTIAL_LFV_NOT_FULL_EXCLUSION"
F17_JSON="F17_three_F13_exact_complex_matrices_from_F16.json"
OMITTED=(
 "two-loop Barr-Zee charged-scalar, WZ/other electroweak and additional diagrams",
 "full three-charged-lepton photonic non-dipole, Z penguins, boxes/interference",
 "mu-e conversion including full photonic, scalar/vector quark/nuclear matrix elements",
 "charged-doublet Y and interference effects in universality",
 "updated 2026 experimental likelihood/correlations",
 "neutrino NO and IO PMNS/mass phase scan and full oscillation/cosmology likelihood",
 "two-state precise b->s gamma, HiggsTools, nonoblique EW, charge-breaking vacuum",
)
def parse_card_lepton_matrices(raw):
    """Read exact SARAH external complex 3x3 matrices, no defaults for zeros."""
    vals={};block=None
    for rawline in raw.decode("utf8").splitlines():
        line=rawline.split("#",1)[0].strip()
        if not line:continue
        tokens=line.split()
        if tokens[0].upper()=="BLOCK":
            if len(tokens)<2:raise ValueError("SLHA malformed BLOCK")
            block=tokens[1].upper()
            continue
        if tokens[0].upper() in ("DECAY","QNUMBERS"):
            block=None
            continue
        if block not in ("FZEE","IMFZEE","YE","IMYE","YEE2","IMYEE2"):
            continue
        if len(tokens)!=3:raise ValueError("SLHA lepton external row malformed")
        i,j=int(tokens[0]),int(tokens[1])
        if not (1<=i<=3 and 1<=j<=3):
            raise ValueError("SLHA lepton index invalid")
        key=(block,i,j)
        if key in vals:raise ValueError("Duplicate exact source lepton slot")
        val=float(tokens[2].replace("D","E").replace("d","e"))
        if not math.isfinite(val):raise ValueError("Nonfinite exact source lepton slot")
        vals[key]=val
    matrices={}
    for b in ("FZEE","YE","YEE2"):
        if any((t,i,j) not in vals for t in (b,"IM"+b)
               for i in range(1,4) for j in range(1,4)):
            raise ValueError("Incomplete original complex "+b+" SLHA matrix")
        matrices[b]=np.array([[complex(vals[(b,i,j)],vals[("IM"+b,i,j)])
                               for j in range(1,4)] for i in range(1,4)])
    return matrices

def lepton_basis_from_two_sources(original,card,point):
    mats=parse_card_lepton_matrices(card)
    pairs=(("FSARAH","FZEE"),("YeSARAH","YE"),("Ye2SARAH","YEE2"))
    for src,block in pairs:
        reference=np.asarray(cmat(original,src,(3,3)),complex)
        err=float(np.max(abs(reference-mats[block])))
        if err>1e-10:raise ValueError(
            "F17 original complex matrix != F17f SLHA "+src+" "+str(err))
    beta=point["beta"];v=float(original["vev_GeV"])
    ye=mats["YE"];ye2=mats["YEE2"]
    f=mats["FZEE"]/2.
    Y=(-math.sin(beta)*ye+math.cos(beta)*ye2)/math.sqrt(2.)
    y_ref=np.asarray(cmat(original,"YChen",(3,3)),complex)
    if np.max(abs(Y-y_ref))>1e-10:
        raise ValueError("Physical Chen Yukawa basis changed in F17f")
    if np.max(abs(f+f.T))>1e-10:
        raise ValueError("Physical Chen f lost antisymmetry")
    masses=np.asarray(original["lepton_masses_GeV"],float)
    physical=(math.cos(beta)*ye+math.sin(beta)*ye2)*v/math.sqrt(2.)
    if np.max(abs(physical-np.diag(masses)))>1e-8:
        raise ValueError("Source charged lepton mass basis did not close")
    return f,Y,{
      "FSARAH_to_fChen_equals_half_source_card":True,
      "Ye_Ye2_to_YChen_rotation":True,
      "charged_mass_basis_matrix_max_abs_GeV":
          float(np.max(abs(physical-np.diag(masses)))),
      "max_abs_f":float(np.max(abs(f))),
      "max_abs_Y":float(np.max(abs(Y))),
    }

def evaluate_partial_lfv(p,f,Y):
    """Use original full-complex f/Y; NEVER optimize/retune Yukawas here."""
    old_rates,_=subset_lfv(p,f,Y)
    d2check=amplitude_subset(p,f,Y)
    radiative={};ratios=[];one_ratios=[]
    for channel,info in CHANNELS.items():
        ii,jj=info["parent"],info["daughter"]
        a,b=one_loop_amplitudes(p,f,Y,parent=ii,daughter=jj)
        c,d,_=flav_bz_amplitudes(p,Y,parent=ii,daughter=jj)
        e,g,parts=w_photon_amplitudes(p,Y,parent=ii,daughter=jj)
        old=partial_radiative_br(a,b,norm_br=info["norm_br"])
        if not math.isclose(old,float(old_rates[channel]),
                            rel_tol=3e-8,abs_tol=1e-25):
            raise ValueError("Independent one-loop B2 radiative source mismatch "+channel)
        intermediate=partial_radiative_br(a+c,b+d,norm_br=info["norm_br"])
        if not math.isclose(intermediate/info["limit"],d2check[channel],
                            rel_tol=3e-8,abs_tol=1e-16):
            raise ValueError("Original D2 partial amplitude sum changed "+channel)
        final=partial_radiative_br(a+c+e,b+d+g,norm_br=info["norm_br"])
        values=(old,intermediate,final)
        if not all(math.isfinite(z) and z>=0 for z in values):
            raise ValueError("Nonfinite LFV rate "+channel)
        radiative[channel]={
            "experimental_single_channel_limit_reference_NOT_NEW_LIKELIHOOD":float(info["limit"]),
            "one_loop_BR_NOT_FULL":float(old),
            "one_loop_plus_fermion_gamma_BZ_BR_NOT_FULL":float(intermediate),
            "one_loop_plus_fermion_gamma_plus_W_gamma_BR_NOT_FULL":float(final),
            "coherent_partial_ratio_over_reference_limit_NOT_EXCLUSION":
                float(final/info["limit"]),
            "W_gamma_amplitude_C_L_GeV_minus2":[float(e.real),float(e.imag)],
            "W_gamma_amplitude_C_R_GeV_minus2":[float(g.real),float(g.imag)],
            "included_W_photon_diagrams":parts,
        }
        ratios.append(final/info["limit"]);one_ratios.append(old/info["limit"])
    tree={}
    for name,(parent,daughter,spectator,norm,limit) in TREE_CHANNELS.items():
        val,_=general_neutral_tree_BR(
            Y,parent=parent,daughter=daughter,spectator=spectator,
            norm_br=norm,mH=p["mh2"],ma=p["ma"],
            alpha=p["alpha"],beta=p["beta"])
        if not math.isclose(val/limit,d2check[name],rel_tol=3e-8,abs_tol=1e-16):
            raise ValueError("Existing D2 neutral-tree source mismatch "+name)
        tree[name]={
            "neutral_tree_only_BR_NOT_FULL":float(val),
            "ratio_to_historical_limit_NOT_EXCLUSION":float(val/limit),
            "single_channel_limit_reference":float(limit)}
    uni=f_only_universality(f,p["mH1"],p["mH2"],p["gamma"])
    return {
        "radiative_dipoles_PARTIAL":radiative,
        "neutral_tree_three_lepton_PARTIAL":tree,
        "charged_singlet_f_only_universality_PARTIAL":uni,
        "max_one_loop_only_ratio_to_reference_NOT_EXCLUSION":float(max(one_ratios)),
        "max_extended_partial_ratio_to_reference_NOT_EXCLUSION":
            float(max(ratios+[r["ratio_to_historical_limit_NOT_EXCLUSION"]
                              for r in tree.values()])),
        "missing_required_full_Zee_LFV_diagrams":list(OMITTED),
        "complete_radiative_or_threelepton_LFV":False,
        "full_2026_lfv_likelihood":None,
        "full_Zee_excluded_or_allowed":None,
    }

def compute(f19_path,f18_path,bundle_path,out):
    f19_path=Path(f19_path).expanduser().resolve()
    f18_path=Path(f18_path).expanduser().resolve()
    bundle_path=Path(bundle_path).expanduser().resolve()
    out=Path(out).expanduser().resolve()
    if out.exists():raise FileExistsError("Never overwrite a previous F19b study")
    ledger=json.loads(f19_path.read_text())
    f18=json.loads(f18_path.read_text())
    if ledger.get("status")!=F19_STATUS or (
        ledger.get("observational_allowance_or_exclusion") is not None or
        ledger.get("all_three_exact_source_matched") is not True):
        raise ValueError("F19 source-checked baseline missing")
    if (ledger.get("F18_merged_JSON_SHA256")!=sha(f18_path.read_bytes()) or
        ledger.get("F16_original_source_bundle_SHA256")!=sha(bundle_path.read_bytes())):
        raise ValueError("F19 source/actual F18 provenance mismatch")
    if set(x["candidate_id"] for x in ledger["benchmarks"])!=set(CASES):
        raise ValueError("Incorrect actual F19 benchmark cohort")
    if set(x["candidate_id"] for x in f18["benchmarks"])!=set(CASES):
        raise ValueError("Incorrect original F18 benchmark cohort")
    with tarfile.open(bundle_path,"r:gz") as archive:
        raw_f17=get_bundle_bytes(archive,F17_JSON)
        original=json.loads(raw_f17)
    if (original.get("status")!=
          "F17_F16_SOURCE_EXACT_THREE_COMPLEX_MATRICES_NOT_UFO_PARAM_CARD" or
        original.get("full_Zee_param_card_validated") is not False or
        set(original.get("candidate_ids",[]))!=set(CASES) or
        len(original.get("matrices",[]))!=3):
        raise ValueError("F17 original complex source export inconsistent")
    originals={r["candidate_id"]:r for r in original["matrices"]}
    if set(originals)!=set(CASES):
        raise ValueError("F17 original source rows mismatched")
    f16,raw16,rawf17,cards=source_cards(bundle_path)
    if (ledger["F16_reconstructed_scalar_JSON_SHA256"]!=sha(raw16) or
        ledger["F17f_original_report_SHA256"]!=sha(rawf17)):
        raise ValueError("F19 scalar+F17f original source hashes changed")
    by19={r["candidate_id"]:r for r in ledger["benchmarks"]}
    by18={r["candidate_id"]:r for r in f18["benchmarks"]}
    target,masses=target_neutrino_matrix()
    result=[]
    for name in CASES:
        p=scalar_input(name,f16[name],by18[name],cards[name][1])
        if p!=by19[name]["scalar_original_F16_inputs"]:
            raise ValueError("Exact scalar basis not same as F19 "+name)
        f,Y,basis=lepton_basis_from_two_sources(originals[name],cards[name][1],p)
        closure=float(np.max(abs(reconstruct_neutrino(
            f,Y,kappa=scalar_kappa(p["mH1"],p["mH2"],p["gamma"]))-target)))
        if not math.isfinite(closure) or closure>=1e-9:
            raise ValueError("F17f exact general-Zee fixed-NO neutrino reconstruction mismatch "+name+" "+str(closure))
        ext=evaluate_partial_lfv(p,f,Y)
        item={
            "candidate_id":name,
            "F19_original_scalar_STU_screen_flags":by19[name]["constraint_gates"],
            "F18_actual_model_tree_cascade_BR":by19[name]["BR_cascade_tree_MadWidth"],
            "complex_source_basis_verification":basis,
            "neutrino_source_fixed_NO_matrix_closure_max_abs_eV":closure,
            "neutrino_one_loop_kappa_Chen":scalar_kappa(p["mH1"],p["mH2"],p["gamma"]),
            "neutrino_target_masses_eV_fixed_old_central_NO":masses.tolist(),
            "neutrino_full_oscillation_likelihood":None,
            "evaluated_lfv_SUBSET":ext,
            "complete_Zee_constraints_95CL":None,
            "physical_Zee_allowed_or_excluded":None,
        }
        result.append(item)
    out.mkdir(parents=True,exist_ok=False)
    summary={
        "status":STATUS,
        "F19_real_scalar_EWPO_ledger_sha256":sha(f19_path.read_bytes()),
        "F18_exact_merged_sha256":sha(f18_path.read_bytes()),
        "F16_F17f_source_bundle_sha256":sha(bundle_path.read_bytes()),
        "F17_original_complex_matrices_sha256":sha(raw_f17),
        "three_exact_source_matched_cases_recomputed":len(result),
        "missing_full_LFV_and_experimental_components":list(OMITTED),
        "FULL_MODEL_EXPERIMENTALLY_ALLOWED_OR_EXCLUDED":None,
        "results":result}
    path=out/"F19b_exact_complex_neutrino_partial_LFV_NOT_ALLOWED.json"
    path.write_text(json.dumps(summary,sort_keys=True,indent=2,allow_nan=False)+"\n")
    with (out/"F19b_three_exact_Yukawa_partial_LFV_NOT_ALLOWED.csv").open("w",newline="") as dest:
        cols=("candidate_id","BR_cascade_tree_MadWidth","neutrino_closure_eV",
              "max_abs_f","max_abs_Y","max_partial_LFV_ratio_NOT_EXCLUSION",
              "mu_to_e_gamma_partial_BR","mu_to_e_gamma_ratio_NOT_EXCLUSION",
              "full_Zee_allowed")
        w=csv.DictWriter(dest,fieldnames=cols);w.writeheader()
        for item in result:
            d=item["evaluated_lfv_SUBSET"]
            mu=d["radiative_dipoles_PARTIAL"]["mu_to_e_gamma"]
            w.writerow(dict(candidate_id=item["candidate_id"],
                BR_cascade_tree_MadWidth=item["F18_actual_model_tree_cascade_BR"],
                neutrino_closure_eV=item["neutrino_source_fixed_NO_matrix_closure_max_abs_eV"],
                max_abs_f=item["complex_source_basis_verification"]["max_abs_f"],
                max_abs_Y=item["complex_source_basis_verification"]["max_abs_Y"],
                max_partial_LFV_ratio_NOT_EXCLUSION=d["max_extended_partial_ratio_to_reference_NOT_EXCLUSION"],
                mu_to_e_gamma_partial_BR=mu[
                    "one_loop_plus_fermion_gamma_plus_W_gamma_BR_NOT_FULL"],
                mu_to_e_gamma_ratio_NOT_EXCLUSION=mu[
                    "coherent_partial_ratio_over_reference_limit_NOT_EXCLUSION"],
                full_Zee_allowed="UNKNOWN_NOT_EVALUATED"))
    for row in result:
        d=row["evaluated_lfv_SUBSET"]
        print("F19B_CASE",row["candidate_id"],
              "NEUTRINO_CLOSURE_EV",format(row["neutrino_source_fixed_NO_matrix_closure_max_abs_eV"],".6g"),
              "MAX_PARTIAL_LFV_OVER_REF_NOT_EXCLUSION",
              format(d["max_extended_partial_ratio_to_reference_NOT_EXCLUSION"],".8g"),
              "BR_CASCADE",format(row["F18_actual_model_tree_cascade_BR"],".8g"),
              "FULL_ALLOWED","UNKNOWN",flush=True)
    print("F19B_DONE_SOURCE_MATCHED",len(result),"STATUS",STATUS)
    return summary

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--f19-ledger",type=Path,required=True)
    ap.add_argument("--f18-merged",type=Path,required=True)
    ap.add_argument("--f16-source-bundle",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args()
    compute(a.f19_ledger,a.f18_merged,a.f16_source_bundle,a.output_dir)

if __name__=="__main__":main()
