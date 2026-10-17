#!/usr/bin/env python3
"""Gate B1: reproducible Zee scalar/EWPO/neutrino screening and cascade ranking.

NOT a global experimental scan. In particular, HiggsTools, two-state
B->Xs gamma likelihood, full LFV including Barr-Zee, vacuum globality,
and full charged-scalar widths remain unimplemented. Never use the
output as a physically allowed Zee parameter-point catalogue.

ScannerS/2HDMC cover the 2HDM subsector but do not represent a mixed
charged SU(2) singlet. Primary model engine here is the existing
independent exact tree-level Zee scalar reconstruction (Gate 6).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

from gate6_benchmark import benchmark
from gate6_width_inventory import inventory, MZ
from gateA1h_correlated_stu_ewpo import report as stu_report
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,
    antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,
    reconstruct_neutrino,
    scalar_kappa,
)
from gateA1d_neutral_tree_lfv import tau_tree_br
from gateA1c_charged_singlet_lfv import CHANNELS, dipole_coefficient_f_only
from gateA1e_neutral_one_loop_dipoles import (
    total_neutral_dipoles, partial_radiative_br,
)
from gateA1f_charged_doublet_y_dipoles import charged_doublet_y_dipole

STATUS="GATE_B1_ZEE_SCALAR_EWPO_NEUTRINO_CANDIDATES_NOT_GLOBAL_ALLOWED"
SEED={
    "beta":1.394, "alpha":1.398, "gamma":1.089,
    "mH1":300., "mH2":700., "mh2":580.7, "ma":633.7,
    "m12sq":57700., "lc":4.473, "k1":1.082,
    "k2":0.00398, "k12":-0.001266,
}
COLUMNS=("mH1","mH2","gamma","tanbeta")
CSV_COLS=("id","mH1","mH2","mh2","ma","beta","alpha","gamma",
          "tanbeta","m12sq","lambda1","lambda2","lambda3",
          "lambda4","lambda5","max_unitarity","S","T","U",
          "chi2_Gfitter","chi2_PDG","kappa","max_abs_f",
          "max_abs_Y","neutrino_closure_eV","BR_H2_H1Z_included_only",
          "BR_H1_tb_included_only","production_mixing_weight",
          "cascade_signal_proxy_included_only",
          "mu_to_e_gamma_one_loop_only_over_limit",
          "candidate_status")
REQUIRED_MISSING=(
    "full Zee neutrino and LFV global likelihood including Barr-Zee, "
    "charged-scalar leptonic widths, universality and mu-e conversion",
    "HiggsTools/HiggsBounds/HiggsSignals with full Zee production and widths",
    "two-state b->s gamma calibrated theory+experimental likelihood",
    "charge-breaking/global-vacuum and electroweak observables beyond STU",
    "complete two-state charged-Higgs widths and collider production rates",
)

def make_point(rng,index):
    """Narrow multi-dimensional seed exploration; NOT exhaustive."""
    if index==0: return dict(SEED)
    p=dict(SEED)
    p["beta"]=float(np.clip(rng.normal(1.394,0.004),1.375,1.409))
    p["gamma"]=float(np.clip(rng.normal(1.089,0.20),0.30,1.50))
    p["mH1"]=float(np.clip(rng.normal(300.,75.),200.,570.))
    p["mH2"]=float(np.clip(rng.normal(700.,100.),
                             p["mH1"]+MZ+4.,1100.))
    p["mh2"]=float(np.clip(rng.normal(580.7,65.),300.,950.))
    p["ma"]=float(np.clip(rng.normal(633.7,65.),300.,950.))
    p["alpha"]=float(p["beta"]+rng.normal(0.,0.025))
    p["m12sq"]=float(np.clip(rng.normal(57700.,11000.),15000.,100000.))
    # Keep quartics involving the singlet near the published-inspired seed
    # in this first pilot. A later comprehensive scan must vary them.
    return p


def physical_point_spectrum(p):
    return benchmark(
        beta=p["beta"],mH1=p["mH1"],mH2=p["mH2"],
        alpha=p["alpha"],gamma=p["gamma"],
        m12sq=p["m12sq"],mh2=p["mh2"],ma=p["ma"],
        lc=p["lc"],k1=p["k1"],k2=p["k2"],k12=p["k12"])


def neutrino_at_point(p,*,target=None,f=None):
    """One selected algebraic neutrino solution, NOT full LFV fit."""
    if target is None:
        target,_=target_neutrino_matrix()
    if f is None:
        f,_=antisymmetric_f_with_null_condition(target)
    kappa=scalar_kappa(p["mH1"],p["mH2"],p["gamma"])
    Y,rank,_=solve_lepton_yukawa(f,target,kappa=kappa)
    calc=reconstruct_neutrino(f,Y,kappa=kappa)
    closure=float(np.max(abs(calc-target)))
    if rank!=5 or closure>1.e-9 or not np.all(np.isfinite(Y)):
        raise ValueError("Neutrino rank/complex-mass-matrix closure failed")
    return Y,{
        "kappa":kappa, "max_abs_f":float(np.max(abs(f))),
        "max_abs_Y":float(np.max(abs(Y))),
        "rank":rank,"neutrino_closure_eV":closure,
        "sum_nu_m_eV":float(np.sum(np.linalg.svd(target,compute_uv=False))),
        "neutrino_solution_not_global_fit":True,
    }


def one_loop_lfv_diagnostics(p,f,Y):
    """Coherent subset for informative ranking; NEVER a full LFV pass."""
    out={}
    for name,v in CHANNELS.items():
        parent,daughter=v["parent"],v["daughter"]
        cln,crn,_=total_neutral_dipoles(
            Y,parent=parent,daughter=daughter,
            mH=p["mh2"],mA=p["ma"],alpha=p["alpha"],beta=p["beta"])
        cly,cry=charged_doublet_y_dipole(
            Y,parent=parent,daughter=daughter,
            m1=p["mH1"],m2=p["mH2"],gamma=p["gamma"])
        crf=dipole_coefficient_f_only(
            f,parent,daughter,m1=p["mH1"],m2=p["mH2"],gamma=p["gamma"])
        subset=partial_radiative_br(
            cln+cly,crn+cry+crf,norm_br=v["norm_br"])
        out[name]={
            "coherent_selected_one_loop_BR_NOT_PHYSICAL":subset,
            "reference_experimental_upper_limit":v["limit"],
            "one_loop_subset_over_limit_NOT_PASS_FAIL":subset/v["limit"],
        }
    for name,daughter in (("tau_to_3mu",1),("tau_to_e_mumu",0)):
        val,_=tau_tree_br(
            Y,daughter=daughter,mH=p["mh2"],mA=p["ma"],
            alpha=p["alpha"],beta=p["beta"])
        out[name]={"neutral_scalar_tree_subset_BR":val,
                   "not_full_physical_LFV":True}
    return out


def evaluate(p,*,n_quad=96,target=None,f=None):
    """Return candidate ONLY after all *implemented* scalar/EWPO gates."""
    theory=physical_point_spectrum(p)
    if not (theory["sufficient_global_quartic_BFB"] and
            theory["tree_unitarity_pass"]):
        return None,"scalar_theory"
    sw=stu_report(
        m1=p["mH1"],m2=p["mH2"],mh=125.,
        mH=p["mh2"],mA=p["ma"],alpha=p["alpha"],
        beta=p["beta"],gamma=p["gamma"],n=n_quad)
    fits=sw["correlated_fit_screens"]
    if not all(v["inside_95percent_3D_gaussian_ellipsoid"]
               for v in fits.values()):
        return None,"oblique_gaussian"
    Y,nu=neutrino_at_point(p,target=target,f=f)
    part=inventory(
        beta=p["beta"],mH1=p["mH1"],mH2=p["mH2"],
        alpha=p["alpha"],gamma=p["gamma"],
        m12sq=p["m12sq"],mh2=p["mh2"],ma=p["ma"],
        lc=p["lc"],k1=p["k1"],k2=p["k2"],k12=p["k12"])
    br2=part["conditional_fractions_included_channels_only"]["H2"]["H1_Z"]
    br1=part["conditional_fractions_included_channels_only"]["H1"]["tb"]
    mix=math.sin(p["gamma"])**2
    lfv=one_loop_lfv_diagnostics(
        p,f if f is not None else antisymmetric_f_with_null_condition(
            target_neutrino_matrix()[0])[0],Y)
    return {
        "scalar_inputs":p,
        "tanbeta":theory["tanbeta"],
        "quartics":theory["quartics"],
        "max_unitarity":theory["max_abs_unitarity_eigenvalue"],
        "S_T_U":sw["scalar_STU"],
        "EWPO_correlated_fits":fits,
        "neutrino_seed":nu,
        "LFV_subset_NOT_complete":lfv,
        "partial_width_inventory":part,
        "BR_H2_H1Z_included_only":br2,
        "BR_H1_tb_included_only":br1,
        "production_mixing_weight":mix,
        "cascade_signal_proxy_included_only":mix*br2*br1,
        "status":"SCALAR_EWPO_PASS_NEUTRINO_ALGEBRA_CLOSED_ONLY_NOT_ALLOWED",
        "constraints_NOT_IMPLEMENTED":REQUIRED_MISSING,
    },"candidate"


def flatten(res,index):
    p=res["scalar_inputs"];q=res["quartics"]
    st=res["S_T_U"];v=res["neutrino_seed"]
    fits=res["EWPO_correlated_fits"]
    return {
        "id":index,
        **{k:p[k] for k in ("mH1","mH2","mh2","ma",
                             "beta","alpha","gamma","m12sq")},
        "tanbeta":res["tanbeta"],
        **{"lambda"+str(i):q["lambda"+str(i)] for i in range(1,6)},
        "max_unitarity":res["max_unitarity"],
        **st,
        "chi2_Gfitter":fits["Gfitter_2026_U_floating"]
                         ["chi2_relative_to_fit_minimum"],
        "chi2_PDG":fits["PDG_2025_U_floating"]
                     ["chi2_relative_to_fit_minimum"],
        "kappa":v["kappa"],
        "max_abs_f":v["max_abs_f"],
        "max_abs_Y":v["max_abs_Y"],
        "neutrino_closure_eV":v["neutrino_closure_eV"],
        "BR_H2_H1Z_included_only":res["BR_H2_H1Z_included_only"],
        "BR_H1_tb_included_only":res["BR_H1_tb_included_only"],
        "production_mixing_weight":res["production_mixing_weight"],
        "cascade_signal_proxy_included_only":res["cascade_signal_proxy_included_only"],
        "mu_to_e_gamma_one_loop_only_over_limit":res[
            "LFV_subset_NOT_complete"]["mu_to_e_gamma"]
            ["one_loop_subset_over_limit_NOT_PASS_FAIL"],
        "candidate_status":res["status"],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--points",type=int,default=300)
    ap.add_argument("--seed",type=int,default=20261013)
    ap.add_argument("--quadrature-nodes",type=int,default=96)
    ap.add_argument("--top",type=int,default=20)
    ap.add_argument("--output-dir",type=Path,
                    default=Path("work/gateB1_zee_seed_scan"))
    a=ap.parse_args()
    if not (1<=a.points<=500000 and 40<=a.quadrature_nodes<=320 and
            1<=a.top<=1000):
        ap.error("Invalid point count, quadrature nodes or top count")
    a.output_dir.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(a.seed)
    target,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(target)
    counts={"scalar_theory":0,"oblique_gaussian":0,
            "candidate":0,"failed_numerics":0}
    candidates=[]
    for i in range(a.points):
        p=make_point(rng,i)
        try:
            result,reason=evaluate(p,n_quad=a.quadrature_nodes,target=target,f=f)
        except (FloatingPointError,ArithmeticError,ValueError,
                np.linalg.LinAlgError) as exc:
            counts["failed_numerics"]+=1
            if counts["failed_numerics"]<=5:
                print("POINT_NUMERIC_FAILURE index=%d %s"%(i,exc))
            continue
        counts[reason]+=1
        if result is not None:
            candidates.append(flatten(result,i))
    candidates.sort(key=lambda p:(p["BR_H2_H1Z_included_only"],
                                  p["cascade_signal_proxy_included_only"]),
                    reverse=True)
    ranked=candidates[:a.top]
    dest=a.output_dir/"ranked_screened_candidates_NOT_ALLOWED.csv"
    with dest.open("w",newline="") as fcsv:
        w=csv.DictWriter(fcsv,fieldnames=CSV_COLS,extrasaction="ignore")
        w.writeheader();w.writerows(ranked)
    full=a.output_dir/"all_screened_candidates_NOT_ALLOWED.csv"
    with full.open("w",newline="") as fcsv:
        w=csv.DictWriter(fcsv,fieldnames=CSV_COLS,extrasaction="ignore")
        w.writeheader();w.writerows(candidates)
    flavor=a.output_dir/"candidate_flavor_inputs.csv"
    with flavor.open("w",newline="") as fcsv:
        w=csv.DictWriter(fcsv,fieldnames=COLUMNS)
        w.writeheader()
        for p in candidates:
            w.writerow({k:p[k] for k in COLUMNS})
    # A 2HDMC cross-check can use the same 2HDM quartics and soft
    # mixing, but the *unmixed doublet* charged-mass parameter is NOT
    # either physical Zee charged-Higgs mass. Never use 2HDMC's
    # single-charged-Higgs signal predictions as a Zee exclusion.
    sub=a.output_dir/"doublet_subsector_2HDMC_INPUT_ONLY.csv"
    subcols=("id","tanbeta","m12sq","lambda1","lambda2","lambda3",
             "lambda4","lambda5","lambda6","lambda7",
             "mHD_unmixed_GeV","meaning")
    with sub.open("w",newline="") as ff:
        ww=csv.DictWriter(ff,fieldnames=subcols)
        ww.writeheader()
        for row in candidates:
            g=row["gamma"]
            md=(row["mH1"]**2*math.cos(g)**2+
                row["mH2"]**2*math.sin(g)**2)**0.5
            ww.writerow({
                **{k:row[k] for k in
                   ("id","tanbeta","m12sq","lambda1","lambda2",
                    "lambda3","lambda4","lambda5")},
                "lambda6":0.,"lambda7":0.,
                "mHD_unmixed_GeV":md,
                "meaning":"2HDM_DOUBLETS_ONLY_NOT_PHYSICAL_ZEE_HCHARGED",
            })
    summary={
        "status":STATUS, "seed":a.seed,
        "attempted":a.points,"counts":counts,
        "top":len(ranked),
        "ranking_criterion":"BR(H2->H1Z) among INCLUDED leading-order "
                            "widths only; NOT the total Zee branching fraction",
        "secondary_objective":"sin^2(gamma)*BR_included(H2->H1Z)"
                              "*BR_included(H1->tb): NOT hadron-level rate",
        "neutrino_scope":"Exact one-loop mass-matrix algebraic seed for ONE "
                         "chosen antisymmetric texture and minimal-norm "
                         "Yukawa solution; no likelihood fit or general "
                         "null-space Yukawa scan",
        "failed_to_test":REQUIRED_MISSING,
        "n_physically_allowed_points":None,
        "higgstools_applied":False,
        "scanners_or_2hdmc_full_zee_model_applied":False,
        "flavour_exclusion_applied":False,
        "quadrature_nodes":a.quadrature_nodes,
        "paths":{
            "ranked_candidates":str(dest),
            "all_candidates":str(full),
            "flavour_inputs_for_A1V":str(flavor),
            "2hdmc_doublet_subsector_only":str(sub)},
    }
    (a.output_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("STATUS",STATUS)
    print("COUNTS",counts)
    print("RANKED_CANDIDATE_ROWS",len(ranked))
    print("PHYSICALLY_ALLOWED_POINTS unknown")
    print("HIGGSTOOLS_NOT_YET_RUN True")
    print("MISSING_FLAVOUR_AND_NEUTRINO_LIKELIHOOD True")
    print("OUTPUT",dest)


if __name__=="__main__":
    main()
