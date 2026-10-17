#!/usr/bin/env python3
"""Reproducible family-Z2 neutrino TEXTURE diagnostic across NO/IO and tanbeta.

Runs the same exact charged-lepton-mass / source-equation
family-Z2 neutrino-texture pilot at each beta, ordering and
optimizer seed; no changing Yukawa zeros and no claim of an
oscillation global fit. This is a fast qualitative reproduction
of Primulando et al (2022), NOT a NuFIT likelihood.

WARNING: all tanbeta != the original chosen 5.59717 are
LEPTON-SECTOR-ONLY counterfactuals. Holding scalar masses
and gamma in the neutrino loop is okay for a shape diagnostic,
but the corresponding published P2 scalar potential with
the old m12sq is NOT automatically BFB/unitary at higher tanbeta.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import median
from zee_section8_family_z2_neutrino_texture_pilot import exploratory_optimize

STATUS="FAMILY_Z2_NU_TEXTURE_MULTI_SEED_PROXY_GRID_NOT_NUFIT_OR_ALLOWED"
FIELDNAMES=[
    "tanbeta","ordering","seed","proxy_score_NOT_chisquare",
    "sin2theta12","sin2theta13","sin2theta23","J_CP",
    "dm_solar_over_atmospheric","sum_masses_eV","m1_eV",
    "m2_eV","m3_eV","f_e_mu_normalization_abs",
    "charged_mass_closure_GeV",
    "is_quasidegenerate_mlight_over_mheavy_ge_0p5",
    "full_NuFIT_likelihood","physical_Zee_allowed",
]


def parse_float_list(x):
    vals=[float(part.strip()) for part in x.split(",")]
    if not vals or any(not(math.isfinite(v) and v>0) for v in vals):
        raise ValueError("Expected finite positive tanbeta list")
    if len(set(vals))!=len(vals):raise ValueError("Duplicated tanbeta")
    return vals


def parse_seed_list(x):
    vals=[int(part.strip()) for part in x.split(",")]
    if not vals or any(z<0 for z in vals) or len(set(vals))!=len(vals):
        raise ValueError("Expected distinct nonnegative integer seeds")
    return vals


def summarize_run(report,seed):
    obs=report["observables"]
    mass=obs["masses_eV"]
    if not len(mass)==3:raise ValueError("Invalid neutrino mass spectrum")
    low=min(mass);high=max(mass)
    return {
        "tanbeta":report["tanbeta"],
        "ordering":report["ordering"],
        "seed":seed,
        "proxy_score_NOT_chisquare":report["proxy_score_NOT_chisquare"],
        "sin2theta12":obs["sin2theta12"],
        "sin2theta13":obs["sin2theta13"],
        "sin2theta23":obs["sin2theta23"],
        "J_CP":obs["J_CP"],
        "dm_solar_over_atmospheric":obs["mass_ratio"],
        "sum_masses_eV":obs["sum_masses_eV"],
        "m1_eV":mass[0],"m2_eV":mass[1],"m3_eV":mass[2],
        "f_e_mu_normalization_abs":obs["f_e_mu_to_match_atm_abs"],
        "charged_mass_closure_GeV":report[
            "charged_mass_closure_max_GeV"],
        "is_quasidegenerate_mlight_over_mheavy_ge_0p5":low/high>=.5,
        "full_NuFIT_likelihood":False,
        "physical_Zee_allowed":False,
    }


def check_results(rows,betas,orders,seeds):
    n=len(betas)*len(orders)*len(seeds)
    if len(rows)!=n:raise ValueError("Incomplete pilot grid")
    combos={(r["tanbeta"],r["ordering"],r["seed"]) for r in rows}
    if len(combos)!=n:raise ValueError("Duplicate grid entries")
    for r in rows:
        for key in ("proxy_score_NOT_chisquare",
                    "sin2theta12","sin2theta13","sin2theta23",
                    "sum_masses_eV","charged_mass_closure_GeV"):
            if not math.isfinite(float(r[key])):
                raise ValueError("Nonfinite "+key)
        if r["charged_mass_closure_GeV"]>1e-9:
            raise ValueError("Bad charged-lepton mass closure")
        if r["full_NuFIT_likelihood"] or r["physical_Zee_allowed"]:
            raise ValueError("Incorrectly promoted partial texture run")
    return True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tanbetas",default="5.597170833164245,10,15,20")
    parser.add_argument("--orderings",default="NO,IO")
    parser.add_argument("--seeds",default="20261018,20261019,20261020")
    parser.add_argument("--mH1",type=float,default=300.)
    parser.add_argument("--mH2",type=float,default=700.)
    parser.add_argument("--gamma",type=float,default=1.089)
    parser.add_argument("--maxiter",type=int,default=65)
    parser.add_argument("--popsize",type=int,default=10)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    betas=parse_float_list(args.tanbetas)
    seeds=parse_seed_list(args.seeds)
    orders=[s.strip().upper() for s in args.orderings.split(",")]
    if not orders or any(o not in ("NO","IO") for o in orders) or (
            len(set(orders))!=len(orders)):
        parser.error("Orderings must be NO,IO or an individual ordering")
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise ValueError("Output directory not empty")
    if not(0<args.mH1<args.mH2 and 0<args.gamma<math.pi/2):
        raise ValueError("Invalid charged masses or gamma")
    if not(1<=args.maxiter<=2000 and 3<=args.popsize<=100):
        raise ValueError("Invalid optimizer limits")

    rows=[]
    print("STATUS",STATUS,flush=True)
    print("RUNS",len(betas)*len(orders)*len(seeds),flush=True)
    for tanbeta in betas:
        for ordering in orders:
            for seed in seeds:
                report=exploratory_optimize(
                    tanbeta=tanbeta,ordering=ordering,
                    mH1=args.mH1,mH2=args.mH2,gamma=args.gamma,
                    maxiter=args.maxiter,popsize=args.popsize,
                    seed=seed)
                row=summarize_run(report,seed)
                rows.append(row)
                print("TEXTURE_CASE", "tanbeta",tanbeta,
                      "ordering",ordering,"seed",seed,
                      "PROXY_NOT_CHISQ",round(row[
                          "proxy_score_NOT_chisquare"],4),
                      "s23sq",round(row["sin2theta23"],5),
                      "sum_mnu_eV",round(row["sum_masses_eV"],5),
                      "quasidegenerate",row[
                          "is_quasidegenerate_mlight_over_mheavy_ge_0p5"],
                      flush=True)
    check_results(rows,betas,orders,seeds)
    out=args.output_dir;out.mkdir(parents=True,exist_ok=False)
    with (out/"grid_NOT_NUFIT.csv").open("w",newline="") as h:
        w=csv.DictWriter(h,fieldnames=FIELDNAMES)
        w.writeheader();w.writerows(rows)
    best={}
    for t in betas:
        best[str(t)]={}
        for o in orders:
            group=[r for r in rows if r["tanbeta"]==t and r["ordering"]==o]
            group.sort(key=lambda r:r["proxy_score_NOT_chisquare"])
            best[str(t)][o]={
                "best":group[0],
                "median_proxy_score_NOT_chisquare":median(
                    r["proxy_score_NOT_chisquare"] for r in group),
                "multiple_seeds_no_proof_of_global_optimum":True,
            }
            print("BEST_TANBETA_ORDERING",t,o,"seed",group[0]["seed"],
                  "SCORE_NOT_CHISQ",
                  round(group[0]["proxy_score_NOT_chisquare"],5),
                  "S23SQ",round(group[0]["sin2theta23"],5),
                  "SUM_MNU_EV",round(group[0]["sum_masses_eV"],5),
                  flush=True)
    meta={"status":STATUS,
          "sampled_tanbeta":betas,"sampled_ordering":orders,
          "sampled_seeds":seeds,"runs":len(rows),
          "mH1_GeV":args.mH1,"mH2_GeV":args.mH2,
          "gamma":args.gamma,
          "scalar_BFB_at_high_tanbeta":"NOT_TESTED",
          "NuFIT_version_and_correlated_likelihood":"NOT_IMPLEMENTED",
          "cosmological_neutrino_likelihood":"NOT_IMPLEMENTED",
          "complete_LFV":"NOT_IMPLEMENTED",
          "physical_Zee_allowed":None,
          "results_csv":str(out/"grid_NOT_NUFIT.csv"),
          "best_by_tanbeta_ordering":best}
    (out/"summary.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("PHYSICAL_ALLOWED False")
    print("OUTPUT",out/"summary.json")


if __name__=="__main__":
    main()
