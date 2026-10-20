#!/usr/bin/env python3
"""Reproduce the 2022 family-Z2 IO neutrino acceptance, NOT a modern fit.

The paper (Primulando/Julio/Uttayarat EPJC 82 (2022) 253, Sec 3)
accepts five oscillation observables individually within 2 standard
deviations and then imposes Sum(m_nu)<0.13 eV (Planck+BAO, historical).
For the *upper-octant IO* reference use their Table 1 central values.

Crucial fixes relative to the old 2022 Table1 diagnostic:
- Optimize 2-sigma VIOLATIONS, not central-value squared deviations.
- Expand the transformed charged-mass coordinates from [-12,12] to
  [-22,22]; physical solutions can require e very close to m_tau.
- Require a separate historical cosmology cut and report the paper's
  mass ratio 2 <= m1/m3 <= 15. Ratio window is a SOURCE-observed
  property, not an independent experimental exclusion.
- Check numerical stability near e~m_tau using charged-mass closure.
- Keep every physical-model constraint explicitly NOT_EVALUATED.

This is still a lepton-only diagnostic, no modern NuFIT covariance,
no full LFV, no modern cosmology, no global scalar vacuum.
Do not call physical_Zee_allowed = True based on this program.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from scipy.optimize import differential_evolution

from zee_section8_family_z2_neutrino_texture_pilot import (
    ME,MMU,MTAU,candidate_from_unit,forward,mixing_observables
)
from zee_section8_reproduce_2022_IO_table1 import SOURCE,source_distance

STATUS="FAMILY_Z2_2022_IO_HISTORICAL_2SIGMA_ACCEPTANCE_ONLY_NOT_NUFIT_OR_ALLOWED"
# This includes relatively extreme m_tau proximity, which the old
# +/-12 logistic coordinate excluded. Reproducibility over >1 seed
# and SVD closure are essential.
DEFAULT_BOUNDS=((-22.,22.),(-22.,22.),(-5.,5.),(-math.pi,math.pi))


def source_acceptance(obs):
    score, z = source_distance(obs)
    violations={k:max(0.,abs(float(v))-2.) for k,v in z.items()}
    oscillation_pass=all(v<=1e-10 for v in violations.values())
    masses=obs["masses_eV"]
    ratio=float(masses[0]/masses[2]) if masses[2]>0 else math.inf
    mass_range=bool(2.<=ratio<=15.)
    historical_cosmo=bool(obs["sum_masses_eV"]<.13)
    # Bounded target for an initial exploratory optimizer. This is
    # NOT an experimental chi2 or a statistical likelihood.
    violation_objective=sum(v*v for v in violations.values())
    violation_objective+=max(0.,2.-ratio)**2
    violation_objective+=max(0.,ratio-15.)**2
    violation_objective+=(max(0.,obs["sum_masses_eV"]-.13)/.01)**2
    return {
        "source_2022_standardized_residuals_NOT_chi2":z,
        "source_2022_independent_2sigma_excess":violations,
        "oscillation_5of5_2sigma":oscillation_pass,
        "source_reported_IO_m1_over_m3":ratio,
        "source_reported_2_to_15":mass_range,
        "historical_Planck_BAO_sum_lt_0p13_eV":historical_cosmo,
        "source_style_all_three_conditions":bool(
            oscillation_pass and mass_range and historical_cosmo),
        "source_acceptance_proxy_objective_NOT_chi2":float(
            violation_objective),
    }


def one_run(*,tanbeta,seed,maxiter,popsize,
            mH1=300.,mH2=700.,gamma=1.089,bounds=DEFAULT_BOUNDS):
    if not(math.isfinite(tanbeta) and tanbeta>0 and
           isinstance(seed,int) and seed>=0 and
           1<=maxiter<=2000 and 3<=popsize<=100):
        raise ValueError("Invalid optimizer settings")
    def evaluate_params(x):
        params=candidate_from_unit(x)
        nu=forward(tanbeta=tanbeta,mH1=mH1,mH2=mH2,
                   gamma=gamma,**params)
        o=mixing_observables(nu,"IO")
        accept=source_acceptance(o)
        return params,nu,o,accept
    def objective(x):
        try:
            return evaluate_params(x)[-1][
                "source_acceptance_proxy_objective_NOT_chi2"]
        except (ValueError,FloatingPointError,OverflowError,
                ZeroDivisionError):
            return 1.e12
    result=differential_evolution(
        objective,bounds,maxiter=maxiter,popsize=popsize,
        seed=seed,polish=True,tol=.0001,workers=1,updating="immediate")
    pars,nu,obs,accept=evaluate_params(result.x)
    closure=nu["charged_mass_closure_max_GeV"]
    if closure>1e-9:
        raise ValueError("Charged-lepton physical masses did not close")
    # Boundary warnings must include physical proximity to the mu/tau
    # physical masses, not just optimization-box edge.
    edge=any((float(x)-lo)<.02*(hi-lo) or (hi-float(x))<.02*(hi-lo)
             for x,(lo,hi) in zip(result.x,bounds))
    out={
        "status":STATUS,
        "benchmark_context":"LEPTON_TEXTURE_ONLY; HIGH_TANBETA_SCALAR_NOT_RESCREENED",
        "tanbeta":tanbeta,"seed":seed,
        "charged_masses_GeV":[ME,MMU,MTAU],
        "charged_mass_closure_max_GeV":closure,
        "charged_texture_parameters":pars,
        "charged_texture_near_tau_e_gap_GeV":float(MTAU-pars["e"]),
        "optimizer_coordinates":result.x.tolist(),
        "optimizer_at_2pct_box_boundary":edge,
        "optimizer_polish_success_not_global_proof":bool(result.success),
        "oscillation_observables":obs,
        **accept,
        "model_scalar_BFB_at_requested_tanbeta":"NOT_EVALUATED",
        "current_NuFIT_correlated_likelihood":"NOT_EVALUATED",
        "full_LFV":"NOT_EVALUATED",
        "modern_cosmology":"NOT_EVALUATED",
        "global_vee_minimum":"NOT_EVALUATED",
        "physical_Zee_allowed":None,
        "source_Florentino_P2_scalar_BFB_not_transferred_to_high_tanbeta":True,
    }
    return out


def parse_floats(s):
    seq=[float(x) for x in s.split(",")]
    if not seq or any(not math.isfinite(x) or x<=0 for x in seq) or (
            len(seq)!=len(set(seq))):
        raise ValueError("Invalid tanbeta list")
    return seq


def parse_seeds(s):
    seq=[int(x) for x in s.split(",")]
    if not seq or any(x<0 for x in seq) or len(seq)!=len(set(seq)):
        raise ValueError("Invalid optimizer seed list")
    return seq


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tanbetas",default="10,15,20")
    p.add_argument("--seeds",default="20261018,20261019,20261020")
    p.add_argument("--mH1",type=float,default=300.)
    p.add_argument("--mH2",type=float,default=700.)
    p.add_argument("--gamma",type=float,default=1.089)
    p.add_argument("--maxiter",type=int,default=145)
    p.add_argument("--popsize",type=int,default=18)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    betas=parse_floats(a.tanbetas)
    seeds=parse_seeds(a.seeds)
    if not(0<a.mH1<a.mH2 and 0<a.gamma<math.pi/2):
        p.error("Invalid scalar mass inputs")
    if a.output_dir.exists() and any(a.output_dir.iterdir()):
        p.error("Refusing to overwrite existing pilot")
    records=[]
    print("STATUS",STATUS,flush=True)
    print("N_JOBS",len(betas)*len(seeds),flush=True)
    for tb in betas:
        for sd in seeds:
            row=one_run(tanbeta=tb,seed=sd,
                        maxiter=a.maxiter,popsize=a.popsize,
                        mH1=a.mH1,mH2=a.mH2,gamma=a.gamma)
            records.append(row)
            print("SOURCE2022_2SIGMA_CASE","tanbeta",tb,
                  "seed",sd,"VIOLATION",round(row[
                      "source_acceptance_proxy_objective_NOT_chi2"],8),
                  "OSC_2SIGMA",row["oscillation_5of5_2sigma"],
                  "SUM_Ev",round(row[
                      "oscillation_observables"]["sum_masses_eV"],6),
                  "IO_M1_OVER_M3",round(row[
                      "source_reported_IO_m1_over_m3"],5),
                  "HIST_0p13",row[
                      "historical_Planck_BAO_sum_lt_0p13_eV"],
                  "FULL_SOURCE_STYLE",row["source_style_all_three_conditions"],
                  "TAU_GAP_GEV",row["charged_texture_near_tau_e_gap_GeV"],
                  flush=True)
    best=[]
    for tb in betas:
        same=[r for r in records if r["tanbeta"]==tb]
        chosen=min(same,key=lambda r:r[
            "source_acceptance_proxy_objective_NOT_chi2"])
        best.append(chosen)
        print("BEST_TB",tb,"SCORE",chosen[
            "source_acceptance_proxy_objective_NOT_chi2"],
            "OBSERVABLES",json.dumps(
                chosen["oscillation_observables"],sort_keys=True),
            "RESIDUALS",json.dumps(chosen[
                "source_2022_standardized_residuals_NOT_chi2"],
                sort_keys=True),flush=True)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    dest=a.output_dir/"results_SOURCE_2022_ACCEPTANCE_NOT_ALLOWED.json"
    dest.write_text(json.dumps({
        "status":STATUS,
        "source_paper":"https://doi.org/10.1140/epjc/s10052-022-10189-0",
        "source_table1_IO_upper_octant":SOURCE,
        "objective":"five independent 2022 marginal +/- 2sigma windows, "+
            "plus descriptive m1/m3 2-15 range and historical "+
            "sum(mnu)<0.13 eV: NOT a NuFIT correlated likelihood",
        "optimizer_bounds":DEFAULT_BOUNDS,
        "high_tanbeta_Florentino_P2_scalar_untested":True,
        "physical_Zee_allowed":None,
        "results":records,
        "best_by_tanbeta":best},indent=2)+"\n")
    print("HISTORICAL_SOURCE_STYLE_FOUND",
          any(r["source_style_all_three_conditions"] for r in records))
    print("CURRENT_NUFIT_LIKELIHOOD_DONE False")
    print("PHYSICAL_ZEE_ALLOWED False")
    print("OUTPUT",dest)


if __name__=="__main__":
    main()
