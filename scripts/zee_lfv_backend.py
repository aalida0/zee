#!/usr/bin/env python3
"""Gate B5: extend GENERAL Zee LFV diagnostics to mu->3e and universality.

Uses B2's already coherent one-loop l_i->l_j gamma diagnostics without
rewriting those loop amplitudes. Adds neutral h/H/A tree-level:
  mu->eee, tau->eee, tau->mumu mu, tau->mu ee, tau->e mumu.
Uses Herrero-Garcia et al arXiv:1701.05345 Eqs. (3.8)-(3.9);
sufficient for tree-level subset ONLY, not full 3-body rates.
Adds f-only charged-current universality Eq.(3.29)-(3.33),
also a SUBSET of general Zee scalar effects.

NOT computed: Barr-Zee, dipole + box + Z-penguin contributions to
3-body decays, conversion including gluon/scalar/vector/photonic
operators, full universal charged Y interference, likelihood correlations.

The program NEVER sets an experimental allowed/excluded state.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np
from gateA1d_neutral_tree_lfv import scalar_couplings, GF
from gateA1c_charged_singlet_lfv import singlet_propagator_sum
from gateB3_general_zee_charged_lepton_widths import (
    read_b1,complex_matrix,ensure_neutrino_closure,
)
from gateA1b_hierarchical_no_seed import target_neutrino_matrix

STATUS="GATE_B5_GENERAL_ZEE_PARTIAL_LFV_EXTENSIONS_ONLY_NOT_ALLOWED"
# Experimental 90% upper limits: reference values, not global likelihood.
# Mu3e: SINDRUM 1988, Nucl.Phys.B299:1.
# Tau: Belle II 424 fb-1 tau->3mu 1.9e-8; Belle trileptons
# and HFLAV 2023 historical compilation. Check current measurements
# and avoid treating any tree-only rate as a physical pass.
TREE_CHANNELS={
    "mu_to_3e_tree":(1,0,0,1.0,1.0e-12),
    "tau_to_3e_tree":(2,0,0,.1782,2.7e-8),
    "tau_to_3mu_tree":(2,1,1,.1739,1.9e-8),
    "tau_to_mu_ee_tree":(2,1,0,.1739,1.8e-8),
    "tau_to_e_mumu_tree":(2,0,1,.1782,2.7e-8),
}
DISPLAY_COLS=(
    "candidate_id","b2_solution_rank","mH1","mH2","gamma",
    "max_abs_f","max_abs_Y","neutrino_matrix_closure_eV",
    "mu_to_3e_neutral_tree_only_BR",
    "mu_to_3e_tree_over_exp_limit_NOT_EXCLUSION",
    "tau_to_3e_neutral_tree_only_BR",
    "tau_to_3mu_neutral_tree_only_BR",
    "tau_to_mu_ee_neutral_tree_only_BR",
    "tau_to_e_mumu_neutral_tree_only_BR",
    "mu_to_e_gamma_coherent_ONELOOP_ONLY_BR",
    "one_loop_radiative_max_ratio_NOT_EXCLUSION",
    "tree_3lepton_max_ratio_NOT_EXCLUSION",
    "delta_GF_mu_f_only",
    "delta_g_tau_over_mu_squared_f_only",
    "delta_g_tau_over_e_squared_f_only",
    "delta_g_mu_over_e_squared_f_only",
    "max_partial_ratio_NOT_EXCLUSION",
    "status",
)


def general_neutral_tree_coefficients(Y,*,parent,daughter,spectator,
                                      mh=125.,mH,ma,alpha,beta):
    """Generalize existing A1D Eq.(3.8) to the e+e- spectator.

    Neutral Yukawa matrices defined as
      -S bar(ell)_i [ C_ij P_L+C_ji* P_R ] ell_j.
    The two fermion currents are (daughter,parent) and
    (spectator,spectator). All h,H,A amplitudes interfere.
    """
    if parent not in (1,2) or daughter not in (0,1) or (
            daughter>=parent) or spectator not in (0,1):
        raise ValueError("Invalid flavor indices for 3lepton neutral tree")
    Y=np.asarray(Y,complex)
    if Y.shape!=(3,3) or not np.all(np.isfinite(Y)):
        raise ValueError("Invalid complex lepton Yukawa matrix")
    D={key:0j for key in ("LL","RR","LR","RL")}
    for C,mass in scalar_couplings(
            Y,mh=mh,mH=mH,mA=ma,alpha=alpha,beta=beta):
        if not (math.isfinite(mass) and mass>0):
            raise ValueError("Invalid neutral scalar mass")
        L=C[daughter,parent]
        R=np.conj(C[parent,daughter])
        qL=C[spectator,spectator]
        qR=np.conj(qL)
        factor=-.5/mass**2
        D["LL"]+=factor*L*qL
        D["RR"]+=factor*R*qR
        D["LR"]+=factor*L*qR
        D["RL"]+=factor*R*qL
    return D


def general_neutral_tree_BR(Y,*,parent,daughter,spectator,norm_br,
                            mh=125.,mH,ma,alpha,beta):
    """Herrero 2017 Eq.(3.8), tree component in massless-final limit.

    Normalization is BR(parent -> daughter nu nu). For mu it is 1.
    xi=1/2 for identical daughter/spectator negative leptons,
    xi=1 otherwise.
    """
    D=general_neutral_tree_coefficients(
        Y,parent=parent,daughter=daughter,spectator=spectator,
        mh=mh,mH=mH,ma=ma,alpha=alpha,beta=beta)
    if not (0<norm_br<=1):
        raise ValueError("Invalid normalization BR")
    xi=.5 if daughter==spectator else 1.
    res=norm_br/(32*GF**2)*(
        xi*(abs(D["LL"])**2+abs(D["RR"])**2)
        +abs(D["LR"])**2+abs(D["RL"])**2)
    if not math.isfinite(res) or res<0:
        raise ValueError("Invalid neutral-tree partial branching fraction")
    return float(res),D


def f_only_universality(f,m1,m2,gamma):
    """2017 Herrero Eqs.(3.29)-(3.33), leading charged-singlet f².

    Returns shifts in SQUARED coupling ratios. Not full rates:
    Y^ell charged-doublet scalar amplitudes and SM interference
    are absent; do not use as accepted/rejected observables.
    """
    f=np.asarray(f,complex)
    if f.shape!=(3,3) or not np.all(np.isfinite(f)):
        raise ValueError("Expected finite 3x3 f")
    if np.max(abs(f+f.T))>1e-10:
        raise ValueError("f not antisymmetric")
    k=math.sqrt(2.)/GF*singlet_propagator_sum(
        gamma=gamma,m1=m1,m2=m2)
    e_mu=abs(f[0,1])**2
    e_tau=abs(f[0,2])**2
    mu_tau=abs(f[1,2])**2
    # Herrero Eqs. (3.31)-(3.33) take f_e_mu=0. Our B2 solves
    # GENERAL antisymmetric f, so restore the muon-decay denominator:
    # delta(g_tau/g_mu)^2 = delta(tau->e) - delta(mu->e).
    # delta(g_tau/g_e)^2  = delta(tau->mu) - delta(mu->e).
    return {
        "GF_mu_over_GF_SM_squared_minus1_f_only":float(k*e_mu),
        "g_tau_over_mu_squared_minus1_f_only":float(k*(e_tau-e_mu)),
        "g_tau_over_e_squared_minus1_f_only":float(k*(mu_tau-e_mu)),
        "g_mu_over_e_squared_minus1_f_only":float(k*(mu_tau-e_tau)),
    }


def evaluate_candidate(p,solution):
    """Compute every partial rate from exactly one saved B2 solution."""
    if str(p["id"])!=str(solution["candidate_id"]):
        raise ValueError("B2 / scalar spectrum candidate IDs mismatch")
    for k in ("mH1","mH2","gamma"):
        if not math.isclose(
                float(p[k]),float(solution[k]),rel_tol=1e-11,abs_tol=1e-10):
            raise ValueError("B2 / scalar spectrum mismatch in "+k)
    f=complex_matrix(solution["f"],"f")
    Y=complex_matrix(solution["Y"],"Y")
    target,_=target_neutrino_matrix()
    closure=ensure_neutrino_closure(p,f,Y,target)
    if not math.isclose(closure,
                        float(solution["neutrino_matrix_closure_eV"]),
                        rel_tol=0,abs_tol=1e-9):
        raise ValueError("Neutrino closure exceeds expected precision")
    rates={}
    limits={}
    for name,(parent,daughter,spectator,norm,limit) in TREE_CHANNELS.items():
        br,_=general_neutral_tree_BR(
            Y,parent=parent,daughter=daughter,spectator=spectator,
            norm_br=norm,mH=p["mh2"],ma=p["ma"],
            alpha=p["alpha"],beta=p["beta"])
        rates[name]=br
        limits[name]={"90CL_reference_limit":limit,
                      "tree_only_over_limit_NOT_EXCLUSION":br/limit}
    universal=f_only_universality(
        f,p["mH1"],p["mH2"],p["gamma"])
    radiative=solution["partial_LFV_rates_NOT_FULL"]
    rad_ratios=solution["partial_LFV_ratios_NOT_EXCLUSION"]
    rad_ratios={k:float(v) for k,v in rad_ratios.items()
                if k in ("mu_to_e_gamma","tau_to_mu_gamma",
                         "tau_to_e_gamma")}
    if len(rad_ratios)!=3:
        raise ValueError("B2 lacks three coherent one-loop radiative channels")
    best=max(rad_ratios.values())
    tree_best=max(r["tree_only_over_limit_NOT_EXCLUSION"]
                  for r in limits.values())
    if not all(math.isfinite(x) and x>=0 for x in [best,tree_best]):
        raise ValueError("Invalid LFV diagnostics")
    return {
        "candidate_id":str(p["id"]),
        "mH1":p["mH1"],"mH2":p["mH2"],"gamma":p["gamma"],
        "max_abs_f":solution["max_abs_f"],
        "max_abs_Y":solution["max_abs_Y"],
        "neutrino_matrix_closure_eV":closure,
        "tree_only_3lepton_rates_NOT_PHYSICAL_TOTAL":rates,
        "tree_only_3lepton_ratios_NOT_EXCLUSION":limits,
        "coherent_one_loop_radiative_only_NOT_PHYSICAL_TOTAL":{
            k:float(radiative[k]) for k in rad_ratios},
        "one_loop_radiative_ratios_NOT_EXCLUSION":rad_ratios,
        "f_only_universality_NOT_FULL":universal,
        "max_tree_3lepton_ratio_NOT_EXCLUSION":tree_best,
        "max_radiative_one_loop_ratio_NOT_EXCLUSION":best,
        "max_combined_partial_diagnostic_NOT_EXCLUSION":max(best,tree_best),
        "status":"TREE_3LEPTON_ONELOOP_GAMMA_F_UNIVERSALITY_PARTIAL_ONLY_NOT_ALLOWED",
    }


def output_row(x,rank):
    rate=x["tree_only_3lepton_rates_NOT_PHYSICAL_TOTAL"]
    rr=x["tree_only_3lepton_ratios_NOT_EXCLUSION"]
    univ=x["f_only_universality_NOT_FULL"]
    return {
        "candidate_id":x["candidate_id"],
        "b2_solution_rank":rank,
        **{k:x[k] for k in (
            "mH1","mH2","gamma","max_abs_f","max_abs_Y",
            "neutrino_matrix_closure_eV")},
        **{
            "mu_to_3e_neutral_tree_only_BR":rate["mu_to_3e_tree"],
            "mu_to_3e_tree_over_exp_limit_NOT_EXCLUSION":
            rr["mu_to_3e_tree"]["tree_only_over_limit_NOT_EXCLUSION"],
            "tau_to_3e_neutral_tree_only_BR":rate["tau_to_3e_tree"],
            "tau_to_3mu_neutral_tree_only_BR":rate["tau_to_3mu_tree"],
            "tau_to_mu_ee_neutral_tree_only_BR":rate["tau_to_mu_ee_tree"],
            "tau_to_e_mumu_neutral_tree_only_BR":rate["tau_to_e_mumu_tree"],
        },
        "mu_to_e_gamma_coherent_ONELOOP_ONLY_BR":
            x["coherent_one_loop_radiative_only_NOT_PHYSICAL_TOTAL"][
                "mu_to_e_gamma"],
        "one_loop_radiative_max_ratio_NOT_EXCLUSION":
            x["max_radiative_one_loop_ratio_NOT_EXCLUSION"],
        "tree_3lepton_max_ratio_NOT_EXCLUSION":
            x["max_tree_3lepton_ratio_NOT_EXCLUSION"],
        "delta_GF_mu_f_only":
            univ["GF_mu_over_GF_SM_squared_minus1_f_only"],
        "delta_g_tau_over_mu_squared_f_only":
            univ["g_tau_over_mu_squared_minus1_f_only"],
        "delta_g_tau_over_e_squared_f_only":
            univ["g_tau_over_e_squared_minus1_f_only"],
        "delta_g_mu_over_e_squared_f_only":
            univ["g_mu_over_e_squared_minus1_f_only"],
        "max_partial_ratio_NOT_EXCLUSION":
            x["max_combined_partial_diagnostic_NOT_EXCLUSION"],
        "status":x["status"],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--points",type=Path,required=True)
    ap.add_argument("--b2-json",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args()
    points=read_b1(a.points)
    b2=json.loads(a.b2_json.read_text())
    if set(points)!=set(b2):
        raise ValueError("B2 and scalar candidate sets disagree")
    rows=[];details={}
    for ident,p in points.items():
        solutions=b2[ident]
        if not isinstance(solutions,list) or not solutions:
            raise ValueError("Missing neutrino family "+ident)
        details[ident]=[]
        for rank,sol in enumerate(solutions,1):
            x=evaluate_candidate({**p,"id":ident},sol)
            details[ident].append(x)
            rows.append(output_row(x,rank))
    a.output_dir.mkdir(parents=True,exist_ok=True)
    csv_path=a.output_dir/"lfv_partial_3lepton_universality_NOT_ALLOWED.csv"
    with csv_path.open("w",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=DISPLAY_COLS)
        writer.writeheader()
        writer.writerows(rows)
    (a.output_dir/"all_partial_LFV_details_NOT_ALLOWED.json").write_text(
        json.dumps(details,indent=2)+"\n")
    summary={
        "status":STATUS,
        "n_scalar_points":len(points),
        "n_neutrino_Yukawa_solutions":len(rows),
        "computed_tree_only_3lepton_modes":list(TREE_CHANNELS),
        "computed_one_loop_radiative_only_channels":[
            "mu_to_e_gamma","tau_to_mu_gamma","tau_to_e_gamma"],
        "computed_f_only_leptonic_universality_shifts":True,
        "max_mu3e_neutral_tree_only_BR":
            max(x["mu_to_3e_neutral_tree_only_BR"] for x in rows),
        "max_one_loop_radiative_only_BR_mu_to_e_gamma":
            max(x["mu_to_e_gamma_coherent_ONELOOP_ONLY_BR"] for x in rows),
        "any_physical_LFV_exclusions":None,
        "full_Zee_LFV_likelihood_validated":False,
        "missing_contributions":[
            "two-loop Barr-Zee amplitudes with validated chiral normalization",
            "off-shell photon, Z penguin and box amplitudes and interference "
            "for mu->3e and tau 3-lepton channels",
            "mu-e conversion photon, quark-scalar, vector, gluon operators "
            "and nuclear overlaps for Type-II quark interactions",
            "Y-dependent charged-current universality and muon-decay "
            "normalization with full likelihood",
            "current precision bounds with combined experimental covariance"],
        "output_csv":str(csv_path)}
    (a.output_dir/"summary.json").write_text(
        json.dumps(summary,indent=2)+"\n")
    print("STATUS",STATUS)
    print("SCALAR_CANDIDATES",len(points))
    print("NEUTRINO_YUKAWA_FAMILIES",len(rows))
    print("MU_3E_NEUTRAL_TREE_IMPLEMENTED True")
    print("RADIATIVE_ONELOOP_REUSED True")
    print("F_ONLY_UNIVERSALITY_IMPLEMENTED True")
    print("BARR_ZEE_IMPLEMENTED False")
    print("MU_E_CONVERSION_PHYSICAL_IMPLEMENTED False")
    print("PHYSICAL_LFV_EXCLUSION_CALCULATED False")
    print("OUTPUT",csv_path)


if __name__=="__main__":
    main()
