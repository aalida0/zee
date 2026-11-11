#!/usr/bin/env python3
"""Scan-ready *declared-order* Higgs/LFV coverage for the reconstructed 16x4 Zee families.

Purpose: evaluate actual source-specific LO tree 3-body decays, LO neutral
H/A positive partial width floors, known-channel h125 widths, dipole-dominance
diagnostics, and a fail-closed experimental status for uncomputed observables.

Crucial: a lower bound on Gamma_total gives only an UPPER bound on BR.
A partial BR below an observed limit is not automatically an exclusion test
unless production/acceptance match the experimental signal hypothesis.

Public phenomenology sources:
- Herrero-Garcia et al JHEP04(2017)130 section 3.3, neutral 3-body and
  dipole LFV; incomplete non-dipole amplitudes not set to zero.
- Kitano, Koike, Okada PRD66(2002)096002 conversion overlap framework.
- Florentino, Romao, Silva EPJC81(2021)1148 for charged-state scalar gauge
  vertices and previous cascade phenomenology.
- HDECAY/SM ledger and native Zee modules pinned in this repository.

A 2017 dipole-dominance mu->3e factor is useful as a *diagnostic*:
alpha/(3 pi)*(ln(m_mu^2/m_e^2)-11/4).
For Al the common dipole-dominance conversion estimate is
CR(Al)=BR(mu->e gamma)/389, again NOT a full model prediction.
"""

from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np

from module2.interface import decode, evaluate as neutrino_evaluate
from module3.core import vertices, neutral_width
from module3 import tree
from module4.couplings import quarks
from module7.d4_inputs import SM, yukawa_masses
from module7.d4_tree_kernels import scalar_vector, scalar_fermions, scalar_scalar
from research.full_constraints.higgs.decays_bridge import neutral_hhh
from research.full_constraints.higgs.sushi_bridge import lo_amplitude
from research.full_constraints.pheno_paper_2026.heavy_HA_tree_widths import heavy_tree_channels

ROOT=Path(__file__).resolve().parents[3]
SM_H125=ROOT/"research/full_constraints/higgs/H125_SIGNAL_STRENGTH_EVIDENCE.json"
SOURCE_CARDS=ROOT/"module14/conditional_scan/candidate_followup.json"
ALPHA_0=1/137.035999084
GF=1.1663787e-5
MUON_MASS=0.1056583755
ELECTRON_MASS=0.00051099895
TAU_WIDTH=6.582119569e-25/(290.3e-15) # hbar in GeV*s over tau lifetime
MU3E_DIP_FACTOR=ALPHA_0/(3*math.pi)*(math.log((MUON_MASS/ELECTRON_MASS)**2)-11/4)
AL_CONVERSION_DIP_FACTOR=1/389.0


def _finite_positive(value,label):
    if not isinstance(value,(float,int)) or not math.isfinite(value) or value<0:
        raise ValueError(f"Invalid {label}: {value}")
    return float(value)


def _mass_fermion_width(mother, mf_yuk, mf_kin, c, pseudoscalar=False, color=3):
    # For pseudoscalar +i*g, PL and PR have opposite signs; scalar they
    # are identical. Explicit spin-summed matrix element from D4 kernel.
    a=complex(c)
    b=-a if pseudoscalar else a.conjugate()
    return scalar_fermions(mother,mf_kin,mf_kin,a,b,color)


def _higgs_kinematics(p,D,ml,state):
    source=vertices(D,p,ml)
    c,M=source[state]
    out={}
    if state not in ("H","A"):
        raise ValueError("Heavy neutral state H or A expected")
    for i,flav in enumerate(("e","mu","tau")):
        for j in range(i,3):
            other=("e","mu","tau")[j]
            width=(2 if i!=j else 1)*neutral_width(c,M,i,j,ml)
            out["ll_"+flav+"_"+other]=_finite_positive(width,"neutral lepton width")

    # Quark Yukawas are Type II only in the quark sector. Running masses
    # in Yukawa vertices, physical masses in phase space, both source D4.
    yq=yukawa_masses(M)
    if isinstance(yq,dict):
        raise ValueError("Native D4 yukawa_masses return changed unexpectedly")
    QNAMES=("u","c","t","d","s","b")
    MREF=dict(zip(QNAMES,SM["kinematic_masses"]))
    yref=dict(zip(QNAMES,yq))
    for q in QNAMES:
        coupl=quarks(yref[q],"top" if q in ("u","c","t") else "bottom",p)[state]
        out["qq_"+q]=_finite_positive(_mass_fermion_width(
            M,yref[q],MREF[q],coupl,pseudoscalar=(state=="A")), "quark width")

    # Native Zee H/A -> charged mass eigenstate + W, both charge conjugates
    # from independently D4 checked gauge current, according to 2021 model.
    for k in (1,2):
        cW=SM["EW"]["mW"]/p["v"]*(math.cos(p["gamma"]) if k==1 else -math.sin(p["gamma"]))
        if state=="H":cW*=math.cos(p["beta"]-p["alpha"])
        out[f"H{k}_W_both_charges"]=2*scalar_vector(M,p[f"mH{k}"],SM["EW"]["mW"],cW)

    if state=="A":
        out["A_h_Z"]=scalar_vector(
            M,p["mh1"],SM["EW"]["mZ"],
            SM["EW"]["mZ"]/p["v"]*math.sin(p["beta"]-p["alpha"])
        )
    else:
        out["H_h_h"]=scalar_scalar(M,p["mh1"],p["mh1"],neutral_hhh(p))/2
        # Do not insert off-shell VV or other scalar modes as zero.

    floor=math.fsum(out.values())
    if not math.isfinite(floor) or floor<=0:
        raise ArithmeticError("Nonpositive heavy neutral known-channel floor")
    ratio_tau=out["ll_tau_tau"]/floor
    return {"state":state,"mass_GeV":M,
            "positive_known_disjoint_partial_widths_GeV":out,
            "known_channel_positive_sum_GeV":floor,
            "BR_tautau_upper_bound_from_positive_channels":ratio_tau,
            "full_total_width_GeV":None,
            "full_BR_tautau":None,
            "exclusion_from_HiggsBounds":None,
            "missing_groups":[
                "Higgs complex electroweak multi-body WW/ZZ offshell and gamma/Zgamma loops",
                "All open H/A neutral-to-neutral and charged-scalar-pair channels not listed",
                "Finite-width off-shell charged-W and scalar channels at thresholds",
                "Required production ggF/bbH reference incl QCD and PDF uncertainties for this exact scalar",
                "Source-qualified observed tau tau, ZZ, WW and cascade search likelihoods"
            ],
            "status":"POSITIVE_LO_CHANNEL_FLOOR_NOT_TOTAL_WIDTH"}


def _model_known_h125(p,D,ml,ratios,sm):
    ch=vertices(D,p,ml)["h"][0]
    # Native quarks(mass=1) returns the physical Yukawa vertex in 1/GeV.
    # Convert back to the dimensionless SM-normalized modifier kappa.
    ku=p["v"]*quarks(1.0,"top",p)["h"]
    kd=p["v"]*quarks(1.0,"bottom",p)["h"]
    if not (0.2<abs(ku)<4 and 0.2<abs(kd)<4):
        raise ArithmeticError("Unphysical source coupling-to-kappa normalization")
    kv=math.cos(p["beta"]-p["alpha"])
    gg,ggsm=lo_amplitude(125.,"even",ku,kd),lo_amplitude(125.,"even",1.,1.)
    # lo_amplitude returns (complex amplitude, metadata), do NOT treat
    # the complete tuple as a scalar amplitude.
    gg_ratio=abs(gg[0]/ggsm[0])**2
    out={}
    for flav in ("bb","ss","dd"):
        out[flav]=sm[flav]*kd**2
    for flav in ("cc","uu"):
        out[flav]=sm[flav]*ku**2
    out["gg"]=sm["gg"]*gg_ratio
    for f in ("WW","ZZ"):
        out[f]=sm[f]*kv**2
    out["gammagamma"]=sm["gammagamma"]*ratios["gammagamma_to_SM"]
    out["Zgamma"]=sm["Zgamma"]*ratios["Zgamma_to_SM"]
    for i,fa in enumerate(("e","mu","tau")):
        for j in range(i,3):
            fb=("e","mu","tau")[j]
            out[f"ll_{fa}_{fb}"]=(2 if i!=j else 1)*neutral_width(ch,125.,i,j,ml)
    # Reuse directly computed QCD-improved SM reference ledger only if
    # all channel names are matched; do not assert complete total width.
    floor=math.fsum(out.values())
    gb=out["bb"]
    return {"matched_known_channel_sum_GeV":floor,
            "matched_independent_quark_lo_gg_ratio":gg_ratio,
            "kappaV":kv,"kappa_top":ku,"kappa_bottom":kd,
            "known_partial_widths_GeV":out,
            "BR_mue_over_Gamma_bb_upper_bound":out["ll_e_mu"]/gb,
            "BR_mutau_over_Gamma_bb_upper_bound":out["ll_mu_tau"]/gb,
            "BR_etau_over_Gamma_bb_upper_bound":out["ll_e_tau"]/gb,
            "full_model_total_width_GeV":None,
            "HiggsSignals_chi2":None,
            "physical_95CL_exclusion":None,
            "status":"KNOWN_CHANNEL_PARTIAL_WIDTH_FLOOR"}


def _source_map():
    orig=json.loads(SOURCE_CARDS.read_text())["tables"]["CERTIFIED_VACUUM_APPROX_BSG_16"]
    return {x["id"]:x for x in orig}


def _lfv_dipole_and_tree(f,p,D,F,ml):
    from module3.core import dipole_ledger,combine,radiative_width
    from module14.lfv import evaluate_family as retained
    nout=neutrino_evaluate(f["algebraic_texture_input"])
    fields={k:nout[k] for k in ("F","D","Ye","Ye2","Mnu")}
    fields.update(input=f["algebraic_texture_input"],input_sha256=f["algebraic_texture_input_sha256"])
    source=retained(fields,True)
    if source["status"]!="PARTIAL" or source["complete_lfv"]:
        raise ArithmeticError("Unexpected full-LFV claim in original backend")
    rad={}
    for name, channel in source["channels"].items():
        rad[name]={"selected_partial_BR":channel["partial_BR"],
                   "full_physical_rate":None,
                   "excluded_at_source_declared_order":None}
    if not math.isclose(rad["mu_to_e_gamma"]["selected_partial_BR"],
                        f["partial_mu_to_e_gamma_BR"],
                        rel_tol=2e-8,abs_tol=1e-27):
        raise ArithmeticError("Saved direct physical LFV rate not reproduced")
    states=vertices(D,p,ml)
    tree3e=tree.width(states,1,0,0,ml,order=6,contact=True)
    mu3e_tree_BR=tree3e/(GF*GF*MUON_MASS**5/(192*math.pi**3))
    source_mu3e=f["mu_to_3e_tree_partial_BR"]
    if not math.isclose(mu3e_tree_BR,source_mu3e,rel_tol=2e-3,abs_tol=1e-38):
        raise ArithmeticError("Coherent three-body tree replay mismatches source")
    tau3mu=tree.width(states,2,1,1,ml,order=6,contact=True)/TAU_WIDTH
    tau3e=tree.width(states,2,0,0,ml,order=6,contact=True)/TAU_WIDTH
    dipmu3e=MU3E_DIP_FACTOR*rad["mu_to_e_gamma"]["selected_partial_BR"]
    # Cauchy (L2) triangle for coherent SUM of only these two *source*
    # amplitudes. Does not constrain non-dipole loop/box contributions.
    coherent_max=(math.sqrt(mu3e_tree_BR)+math.sqrt(dipmu3e))**2
    Al=AL_CONVERSION_DIP_FACTOR*rad["mu_to_e_gamma"]["selected_partial_BR"]
    return {"source_radiative":rad,
        "mu3e_tree_coherent_contact_BR":mu3e_tree_BR,
        "mu3e_dipole_only_BR":dipmu3e,
        "mu3e_tree_plus_dipole_kinematic_Cauchy_upper":coherent_max,
        "mu3e_full_rate":None,
        "tau_to_3mu_neutral_tree_contact_BR":tau3mu,
        "tau_to_3e_neutral_tree_contact_BR":tau3e,
        "tau_to_3mu_full_rate":None,"tau_to_3e_full_rate":None,
        "mu_e_conversion_Al_dipole_dominance_only":Al,
        "mu_e_conversion_Al_full_rate":None,
        "mu_e_conversion_Au_full_rate":None,
        "mu_e_conversion_tree_semileptonic_mu_e_scalar_status":
            "D_e_mu_D_mu_e_ZERO_BY_ALGEBRA_WITHIN_FLOAT_TOL_ONLY",
        "full_physical_LFV":"UNKNOWN",
        "explicit_missing_terms":[
            "mu3e: offshell photon monopole K1, Z penguin and full box operator vector and interference",
            "mu-e Al/Au: nonphotonic vector/scalar/gluon Wilsons and nuclear coherent matching",
            "Zee W/Goldstone and mixed charged-singlet F-D gauge-complete two-loop dipoles"
        ]}


def execute(source_path:Path,out:Path,limit:int|None=None):
    if out.exists():raise FileExistsError("Refuse to overwrite physics receipts")
    original=json.loads(source_path.read_text())
    if (len(original["families"])!=64 or
        original["new_neutrino_family_count"]!=64):
        raise ValueError("Require full 16 x 4 constructed family source")
    smledger=json.loads(SM_H125.read_text())["matched_SM_ledger_GeV"]
    mp=_source_map()
    families=[]
    for f in original["families"][:limit]:
        rid=f["id"]
        if f["scalar_sha256"] != mp[rid]["scalar_sha256"]:
            raise ValueError("Scalar provenance changed")
        p=mp[rid]["input_card"]["physical"]
        n=neutrino_evaluate(f["algebraic_texture_input"])
        D=decode(n["D"]);F=decode(n["F"]);ml=SM["lepton_masses"]
        if (max(abs(D[0,1]),abs(D[1,0]))>1e-10
            or n["inverse"]["family_relative_residual"]>=2e-9):
            raise ArithmeticError("Original inverse neutrino closure lost")
        h=_model_known_h125(p,D,ml,f["h125_gamma_ratios"],smledger)
        heavy={x:heavy_tree_channels(p,D,x) for x in ("H","A")}
        if not 0.003<h["matched_known_channel_sum_GeV"]<0.006:
            raise ArithmeticError("h125 SM-matched channel ledger out of physical MeV range")
        lfv=_lfv_dipole_and_tree(f,p,D,F,ml)
        row={"scalar_id":rid,"scalar_sha256":f["scalar_sha256"],
             "ordering":f["ordering"],"seed":f["seed"],
             "h125":h,"heavy_neutral":heavy,"lfv":lfv,
             "full_Higgs":"UNKNOWN","full_LFV":"UNKNOWN",
             "global_acceptance":None}
        families.append(row)
        print("PAPER_LO_HIGGS_LFV",rid,f["ordering"],f["seed"],
              "hwidth_floor",h["matched_known_channel_sum_GeV"],
              "Hwidth_floor",heavy["H"]["known_tree_disjoint_sum_GeV"],
              "Awidth_floor",heavy["A"]["known_tree_disjoint_sum_GeV"],
              "mu3e_subset_max",lfv["mu3e_tree_plus_dipole_kinematic_Cauchy_upper"],
              "Al_dipole_only",lfv["mu_e_conversion_Al_dipole_dominance_only"],
              "full_H_LFV_unknown",flush=True)
    report={"schema":"zee-16-scalar-64-flavor-leading-channel-Higgs-LFV-explicit-coverage-v1",
            "n_evaluated":len(families),
            "n_input":len(original["families"]),
            "calculation_accuracy":"native Zee tree channels, matched-SM h125 restricted loop partial widths, source selected radiative dipoles, tau/mu 3-lepton tree contact and dipole dominance only",
            "not_full_neutral_widths":True,
            "mu_e_conversion_al_dipole_dominance_only":True,
            "full_Higgs":"UNKNOWN",
            "full_LFV":"UNKNOWN",
            "global_acceptance":None,
            "families":families}
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--limit",type=int)
    a=p.parse_args()
    execute(a.input,a.output,a.limit)


if __name__=="__main__":main()
