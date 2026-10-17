#!/usr/bin/env python3
"""Reproducible first-octant IO family-Z2 *candidate*, not a NuFIT fit.

Context: 2022 Primulando-Jul io-Uttayarat accepted both theta23
octants. Our prior source-matched 2022 searches optimized only the
published Table1 UPPER octant central value sin2theta23=.575.
They cannot exclude source FIRST-octant solutions.

This module supplies a deterministic independent numerical WITNESS
with theta23 in the first octant and the OTHER FOUR Table 1 (2022) IO
observables inside their marginal 2sigma windows. Its theta23
provisional exploration window [.43,.49] is NOT a quoted 2022
lower-octant 2sigma confidence interval. The formal 2022 historical
first-octant acceptance needs the exact likelihood/profile from the
paper's oscillation dataset. The old Planck+BAO sum <.13 eV
and descriptive 2<=m1/m3<=15 checks are separate from oscillation data.

No global scalar vacuum, high-tanbeta scalar theory, LFV, HiggsTools,
modern cosmology or modern two-state b->s gamma is tested. The
family-Z2 texture's charged-mass conventions are those already
unit-tested in the preceding Zee pilots.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

from scipy.optimize import differential_evolution
from zee_section8_family_z2_neutrino_texture_pilot import (
    candidate_from_unit,forward,mixing_observables
)
from zee_section8_reproduce_2022_IO_table1 import SOURCE

STATUS="FAMILY_Z2_IO_FIRST_OCTANT_DIAGNOSTIC_NOT_SOURCE_LIKELIHOOD_OR_ALLOWED"
FIRST_OCTANT_PROVISIONAL=(.43,.49)
BOUNDS=((-24.,24.),(-24.,24.),(-5.,5.),(-math.pi,math.pi))
WITNESS={"tanbeta":15.,
         "coordinates":[-3.8318906,-8.45647671,-.62476731,-3.1167578],
         "mass_reference":"mH1=300,mH2=700 GeV,gamma=1.089 (shape only)",
         "source":"independent deterministic numerical search; not an experimental fit"}

def source_other_four(obs):
    residuals={}
    for key in ("sin2theta12","sin2theta13","J_CP","mass_ratio"):
        central,down,up=SOURCE[key]
        diff=float(obs[key]-central)
        residuals[key]=diff/(up if diff>0 else down)
    return residuals

def evaluate_coordinates(x,*,tanbeta,mH1=300.,mH2=700.,gamma=1.089):
    par=candidate_from_unit(x)
    p=forward(tanbeta=tanbeta,mH1=mH1,mH2=mH2,
              gamma=gamma,**par)
    obs=mixing_observables(p,ordering="IO")
    residuals=source_other_four(obs)
    m=obs["masses_eV"]
    ratio=float(m[0]/m[2]) if m[2]>0 else math.inf
    if not math.isfinite(ratio):
        raise ValueError("Invalid neutrino mass ratio")
    lower,upper=FIRST_OCTANT_PROVISIONAL
    theta=float(obs["sin2theta23"])
    passes_four=all(abs(z)<=2. for z in residuals.values())
    first_window=bool(lower<=theta<=upper)
    oldcosmo=bool(obs["sum_masses_eV"]<.13)
    paper_ratio=bool(2<=ratio<=15)
    return {
        "status":STATUS,
        "tanbeta":float(tanbeta),"ordering":"IO",
        "mH1_GeV":mH1,"mH2_GeV":mH2,"gamma":gamma,
        "four_2022_upper_octant_table1_other_observables_2sigma":passes_four,
        "four_2022_table1_residuals_in_source_sigma":residuals,
        "theta23_first_octant_exploratory_0p43_to_0p49":first_window,
        "theta23_first_octant_source_likelihood_validated":False,
        "source_2022_full_5observable_2sigma_pass":"NOT_EVALUATED",
        "historical_sum_mnu_lt_0p13_eV":oldcosmo,
        "reported_IO_ratio_2_to_15":paper_ratio,
        "IO_m1_over_m3":ratio,
        "passes_EXPLORATORY_four_plus_theta23_window_and_history":bool(
            passes_four and first_window and oldcosmo and paper_ratio),
        "oscillation_observables":obs,
        "charged_texture_parameters":par,
        "charged_mass_closure_max_GeV":p["charged_mass_closure_max_GeV"],
        "charged_texture_e_minus_mmu_GeV":par["e"]-.1056583755,
        "optimizer_coordinates":list(map(float,x)),
        "full_NuFIT_likelihood":False,
        "full_LFV_likelihood":False,
        "high_tanbeta_scalar_theory_screen":"NOT_EVALUATED",
        "full_Zee_allowed":None,
    }

def exploratory_objective(x,tanbeta):
    try:
        a=evaluate_coordinates(x,tanbeta=tanbeta)
        p=sum(max(0.,abs(v)-2.)**2 for v in a[
            "four_2022_table1_residuals_in_source_sigma"].values())
        theta=a["oscillation_observables"]["sin2theta23"]
        lower,upper=FIRST_OCTANT_PROVISIONAL
        p+=max(0.,(lower-theta)/.018,(theta-upper)/.018)**2
        m=a["oscillation_observables"]["sum_masses_eV"]
        p+=max(0.,(m-.13)/.01)**2
        ratio=a["IO_m1_over_m3"]
        p+=max(0.,2.-ratio)**2 + max(0.,ratio-15.)**2
        return float(p)
    except (ValueError,OverflowError,FloatingPointError,
            ZeroDivisionError):
        return 1e12

def optimize(*,tanbeta,seed,maxiter,popsize):
    r=differential_evolution(
        lambda x:exploratory_objective(x,tanbeta), BOUNDS,
        seed=seed,maxiter=maxiter,popsize=popsize,
        polish=True,updating="immediate",workers=1)
    report=evaluate_coordinates(r.x,tanbeta=tanbeta)
    report["optimizer_seed"]=seed
    report["exploratory_objective_NOT_chi2"]=float(r.fun)
    report["optimizer_success_not_global_proof"]=bool(r.success)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witness-only",action="store_true")
    parser.add_argument("--tanbetas",default="15,20")
    parser.add_argument("--seeds",default="101,102,103")
    parser.add_argument("--maxiter",type=int,default=95)
    parser.add_argument("--popsize",type=int,default=14)
    parser.add_argument("--output",required=True,type=Path)
    a=parser.parse_args()
    if a.output.exists():parser.error("Refusing to overwrite an existing file")
    results=[]
    fixed=evaluate_coordinates(WITNESS["coordinates"],tanbeta=WITNESS["tanbeta"])
    if fixed["charged_mass_closure_max_GeV"]>1e-9:
        raise ValueError("Charged-lepton mass closure failed")
    fixed["origin"]="EXPLICIT_NUMERICAL_WITNESS_NOT_PAPER_BENCHMARK"
    results.append(fixed)
    print("STATUS",STATUS)
    print("FIXED_FIRST_OCTANT_WITNESS",
          json.dumps({
              "passes_exploratory":fixed[
                  "passes_EXPLORATORY_four_plus_theta23_window_and_history"],
              "sin2theta23":fixed["oscillation_observables"]["sin2theta23"],
              "sum_mnu_eV":fixed["oscillation_observables"]["sum_masses_eV"],
              "IO_m1_over_m3":fixed["IO_m1_over_m3"],
              "four_source_residuals":fixed[
                  "four_2022_table1_residuals_in_source_sigma"],
              "charged_mass_closure_GeV":fixed["charged_mass_closure_max_GeV"]
          },sort_keys=True),flush=True)
    if not a.witness_only:
        betas=[float(z) for z in a.tanbetas.split(",")]
        seeds=[int(z) for z in a.seeds.split(",")]
        if not betas or len(set(betas))!=len(betas) or any(
                not math.isfinite(x) or x<=0 for x in betas):
            parser.error("Invalid tanbeta list")
        if not seeds or len(set(seeds))!=len(seeds) or min(seeds)<0:
            parser.error("Invalid seed list")
        if not 1<=a.maxiter<=2000 or not 3<=a.popsize<=100:
            parser.error("Invalid optimizer settings")
        for tb in betas:
            for seed in seeds:
                r=optimize(tanbeta=tb,seed=seed,
                           maxiter=a.maxiter,popsize=a.popsize)
                results.append(r)
                o=r["oscillation_observables"]
                print("FIRST_OCTANT_CASE",tb,seed,
                      "VIOLATION",r["exploratory_objective_NOT_chi2"],
                      "EXPLORATORY_PASS",r[
                          "passes_EXPLORATORY_four_plus_theta23_window_and_history"],
                      "S23SQ",o["sin2theta23"],
                      "SUM_MNU",o["sum_masses_eV"],
                      "M1_OVER_M3",r["IO_m1_over_m3"],flush=True)
    out={
        "status":STATUS,
        "witness_provenance":WITNESS,
        "source_2022":"https://doi.org/10.1140/epjc/s10052-022-10189-0",
        "source_other_four_observables":{
            k:SOURCE[k] for k in
            ("sin2theta12","sin2theta13","J_CP","mass_ratio")
        },
        "theta23_first_octant_provisional_window_NOT_SOURCE_2SIGMA":
            FIRST_OCTANT_PROVISIONAL,
        "paper_first_octant_full_likelihood_reproduced":False,
        "current_NuFIT_6_1_likelihood":False,
        "full_flavor_and_model_allowed":False,
        "results":results
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print("FORMAL_FIRST_OCTANT_SOURCE_FIT False")
    print("FULL_ZEE_ALLOWED False")
    print("OUTPUT",a.output)

if __name__=="__main__":
    main()
