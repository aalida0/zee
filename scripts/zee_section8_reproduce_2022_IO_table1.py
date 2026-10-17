#!/usr/bin/env python3
"""Reproduce Primulando-Julio-Uttayarat 2022 Table 1 *IO upper-octant*
neutrino target using the independently built family-Z2 Zee mass texture.

NOT the NuFIT 6.1 likelihood: Table 1 2022 marginal 1-sigma numbers
do not specify a full covariance. Squared standardized residuals are
a DIAGNOSTIC only, never an experimental chi2/CL.
This explores *lepton texture only*: at tanbeta>5.597 the fixed P2
scalar potential has NOT been re-screened or found viable.

Uses exact charged-lepton mass closures and source Eqs (8,9,13,17,20,21)
from zee_section8_family_z2_neutrino_texture_pilot.py.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution
from zee_section8_family_z2_neutrino_texture_pilot import (
    candidate_from_unit,forward,mixing_observables
)

STATUS="FAMILY_Z2_2022_TABLE1_IO_SOURCE_MATCHED_DIAGNOSTIC_NOT_NUFIT_OR_ALLOWED"
# EPJC 82 (2022) 253, Table 1, inverted ordering, upper θ23 octant.
SOURCE={
    "sin2theta12":(.304,.013,.013),
    "sin2theta23":(.575,.018,.018),
    "sin2theta13":(.02238,.00063,.00063),
    "mass_ratio":(.0297,.0034,.0034),
    # Asymmetric Table 1 IO: -0.0327 +0.0066 -0.0008.
    "J_CP":(-.0327,.0008,.0066),
}
SOURCE_URL="https://doi.org/10.1140/epjc/s10052-022-10189-0"
PARAM_BOUNDS=((-12.,12.),(-12.,12.),(-4.,4.),(-math.pi,math.pi))
FIELDS=("tanbeta","seed","score_standardized_diag_NOT_chi2",
        "sin2theta12","sin2theta13","sin2theta23","J_CP",
        "mass_ratio","sum_masses_eV","m1_eV","m2_eV","m3_eV",
        "IO_m1_over_m3","source_2022_IO_massratio_2_to_15",
        "d_GeV","e_GeV","f_e_tau_over_e_mu_abs_r","f_relative_phase_rad",
        "f_e_mu_to_match_atm_abs","max_charge_mass_error_GeV",
        "optimizer_x","optimizer_y","optimizer_log10r",
        "optimizer_phase","any_free_parameter_at_bounds",
        "NuFIT_6_1_likelihood","complete_LFV","full_Zee_allowed")

def source_distance(obs):
    residuals={}
    for name,(central,sig_low,sig_high) in SOURCE.items():
        shift=float(obs[name]-central)
        sd=sig_low if shift<0 else sig_high
        residuals[name]=shift/sd
    return float(sum(z*z for z in residuals.values())),residuals

def fit_one(*,tanbeta,seed,maxiter,popsize,mH1=300.,mH2=700.,gamma=1.089):
    if not(math.isfinite(tanbeta) and tanbeta>0 and
           isinstance(seed,int) and seed>=0 and
           1<=maxiter<=2000 and 3<=popsize<=100):
        raise ValueError("Bad fit configuration")
    def objective(x):
        try:
            params=candidate_from_unit(x)
            nu=forward(tanbeta=tanbeta,mH1=mH1,mH2=mH2,
                       gamma=gamma,**params)
            obs=mixing_observables(nu,ordering="IO")
            return source_distance(obs)[0]
        except (ValueError,FloatingPointError,np.linalg.LinAlgError,
                OverflowError):
            return 1e12
    opt=differential_evolution(objective,PARAM_BOUNDS,
                               maxiter=maxiter,popsize=popsize,
                               seed=seed,polish=True,
                               updating="immediate",workers=1)
    params=candidate_from_unit(opt.x)
    nu=forward(tanbeta=tanbeta,mH1=mH1,mH2=mH2,
               gamma=gamma,**params)
    obs=mixing_observables(nu,ordering="IO")
    score,z=source_distance(obs)
    masses=obs["masses_eV"]
    if any(not np.isfinite(val) for val in (score,*masses)):
        raise ValueError("Nonfinite neutrino result")
    ratio=masses[0]/masses[2] if masses[2]>0 else math.inf
    # Bounds flag should distinguish persistent edge solutions
    # from genuine 5-observable reproduction.
    near=any(abs(float(p)-lo)<0.02*(hi-lo) or
             abs(float(p)-hi)<0.02*(hi-lo)
             for p,(lo,hi) in zip(opt.x,PARAM_BOUNDS))
    row={
        "tanbeta":tanbeta,"seed":seed,
        "score_standardized_diag_NOT_chi2":score,
        **{k:obs[k] for k in SOURCE},
        "sum_masses_eV":obs["sum_masses_eV"],
        "m1_eV":masses[0],"m2_eV":masses[1],"m3_eV":masses[2],
        "IO_m1_over_m3":ratio,
        "source_2022_IO_massratio_2_to_15":bool(2<=ratio<=15),
        "d_GeV":params["d"],"e_GeV":params["e"],
        "f_e_tau_over_e_mu_abs_r":params["r"],
        "f_relative_phase_rad":params["phase_rad"],
        "f_e_mu_to_match_atm_abs":obs["f_e_mu_to_match_atm_abs"],
        "max_charge_mass_error_GeV":nu["charged_mass_closure_max_GeV"],
        "optimizer_x":float(opt.x[0]),"optimizer_y":float(opt.x[1]),
        "optimizer_log10r":float(opt.x[2]),
        "optimizer_phase":float(opt.x[3]),
        "any_free_parameter_at_bounds":near,
        "NuFIT_6_1_likelihood":False,
        "complete_LFV":False,"full_Zee_allowed":False,
    }
    return row,z

def parse_tanbetas(s):
    out=[float(v.strip()) for v in s.split(",")]
    if not out or not all(math.isfinite(x) and x>0 for x in out) or (
            len(set(out))!=len(out)):
        raise ValueError("Bad/duplicate tanbetas")
    return out

def parse_seeds(s):
    out=[int(v.strip()) for v in s.split(",")]
    if not out or min(out)<0 or len(set(out))!=len(out):
        raise ValueError("Bad/duplicate seeds")
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tanbetas",default="5.597170833164245,10,15,20")
    p.add_argument("--seeds",default="20261018,20261019,20261020")
    p.add_argument("--mH1",type=float,default=300.)
    p.add_argument("--mH2",type=float,default=700.)
    p.add_argument("--gamma",type=float,default=1.089)
    p.add_argument("--maxiter",type=int,default=90)
    p.add_argument("--popsize",type=int,default=12)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    betas=parse_tanbetas(a.tanbetas)
    seeds=parse_seeds(a.seeds)
    if not(0<a.mH1<a.mH2 and 0<a.gamma<math.pi/2):
        p.error("Invalid charged scalar inputs")
    if a.output_dir.exists() and any(a.output_dir.iterdir()):
        p.error("Refuse to overwrite nonempty output directory")
    results=[]
    print("STATUS",STATUS,flush=True)
    print("RUNS",len(betas)*len(seeds),flush=True)
    for tb in betas:
        for seed in seeds:
            row,z=fit_one(tanbeta=tb,seed=seed,
                          maxiter=a.maxiter,popsize=a.popsize,
                          mH1=a.mH1,mH2=a.mH2,gamma=a.gamma)
            results.append((row,z))
            print("SOURCE2022_CASE","tanbeta",tb,"seed",seed,
                  "DIAGNOSTIC_SCORE",round(row[
                      "score_standardized_diag_NOT_chi2"],5),
                  "SIN2THETA23",round(row["sin2theta23"],5),
                  "J_CP",round(row["J_CP"],5),
                  "SUM_MNU_EV",round(row["sum_masses_eV"],5),
                  "IO_M1_OVER_M3",round(row["IO_m1_over_m3"],3),
                  "AT_BOUNDARY",row["any_free_parameter_at_bounds"],
                  flush=True)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    rows=[r for r,_ in results]
    with (a.output_dir/"cases_SOURCE2022_NOT_NUFIT.csv").open(
            "w",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    best={}
    for tb in betas:
        ordered=sorted((x for x in results if x[0]["tanbeta"]==tb),
                       key=lambda x:x[0]["score_standardized_diag_NOT_chi2"])
        row,z=ordered[0]
        best[str(tb)]={"row":row,
                       "residuals_in_2022_table1_1sigma_units":z}
        print("BEST_SOURCE2022_TANBETA",tb,
              "SCORE_DIAG",round(row["score_standardized_diag_NOT_chi2"],5),
              "RESIDUALS",json.dumps(z,sort_keys=True),flush=True)
    summary={"status":STATUS,
             "source_2022":SOURCE_URL,
             "source_2022_IO_upper_octant_independent_1sigma":SOURCE,
             "independent_marginal_error_quadrature_not_chi2":True,
             "source_quasidegenerate_definition_proxy":"2 <= IO m1/m3 <= 15",
             "NuFIT_6_1_likelihood":False,
             "model_constraints_other_than_charged_lepton_mass":"NOT_RUN",
             "full_Zee_allowed":None,
             "high_tanbeta_scalar_sector_rechecked":False,
             "optimizer_bounds":PARAM_BOUNDS,
             "best_by_tanbeta":best}
    (a.output_dir/"summary.json").write_text(json.dumps(
        summary,indent=2)+"\n")
    print("NUFIT_LIKELIHOOD_DONE False")
    print("FULL_MODEL_ALLOWED False")
    print("OUTPUT",a.output_dir/"summary.json")
if __name__=="__main__":
    main()
