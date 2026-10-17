#!/usr/bin/env python3
"""Paper 2: systematic mixed charged-Higgs mass/mixing GAUGE-only scan.

Analytic mu+mu- -> H1+ H2- + H1- H2+ via off-shell Z at LO.
Reuses zee_muon_asymmetric_pair_pilot.sigma_both_charges_fb,
previously numerically matched to MG5 on benchmark B4_0000318.

This is a KINEMATIC mass-grid scan, not a scalar-potential scan.
Arbitrary mH1,mH2,gamma combinations may violate theoretical
conditions, flavor limits, Higgs constraints, or neutrino masses.
Do not multiply in B3 BRs calculated at DIFFERENT benchmarks;
reported yields are produced stable H1,H2 pairs, before decays.

The additional muon-specific neutrino-exchange amplitude is absent.
No BIB, ISR, beam spread, acceptance, backgrounds or significance.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

from zee_muon_asymmetric_pair_pilot import (
    sigma_both_charges_fb,beta_pair,rest_frame_b_momentum,MT,MB,MZ,
    ALPHA_EM,SW2
)

STATUS="PAPER2_ZEE_MUON_MASS_MIXING_GRID_GAUGE_ONLY_NOT_ALLOWED"
DEFAULT_M1="200,250,300,400,600,800"
DEFAULT_M2="500,700,1000,1200,1500,2000"
DEFAULT_GAMMAS="0.4,0.7853981633974483,1.1845311184933986"
DEFAULT_ENERGIES="1500,3000,10000"
DEFAULT_LUMINOSITY="0.5,1,10"
FIELDS=(
    "mH1_GeV","mH2_GeV","gamma_rad","sqrt_s_GeV",
    "luminosity_ab_inverse","kinematically_open",
    "cascade_H2_to_H1Z_open","H1_to_tb_open",
    "beta_pair","sigma_Z_both_charges_fb","produced_pairs_before_decay",
    "H1_rest_b_momentum_GeV",
    "experimental_and_scalar_constraints_evaluated",
    "neutrino_t_channel_evaluated","status"
)


def numbers(spec,what):
    if not isinstance(spec,str) or not spec.strip():
        raise ValueError("Empty "+what)
    try:
        arr=[float(s.strip()) for s in spec.split(",")]
    except ValueError as exc:
        raise ValueError("Bad "+what+" list") from exc
    if (len(arr)!=len(set(arr))
            or any(not math.isfinite(x) or x<=0 for x in arr)):
        raise ValueError("Invalid or duplicate "+what)
    return arr


def point(m1,m2,gamma,E,L):
    vals=(m1,m2,gamma,E,L)
    if not all(math.isfinite(x) for x in vals):
        raise ValueError("Nonfinite grid point")
    if not (m1>0 and m2>m1 and 0<=gamma<=math.pi/2
            and E>0 and L>0):
        raise ValueError("Invalid grid point")
    open_pair=(E>m1+m2)
    sigma=sigma_both_charges_fb(E,m1,m2,gamma)
    # Avoid floating-point artifacts around exactly zero.
    if sigma<0 or not math.isfinite(sigma):
        raise ArithmeticError("Invalid analytical cross section")
    return {
        "mH1_GeV":m1,"mH2_GeV":m2,"gamma_rad":gamma,
        "sqrt_s_GeV":E,"luminosity_ab_inverse":L,
        "kinematically_open":open_pair,
        "cascade_H2_to_H1Z_open":m2>m1+MZ,
        "H1_to_tb_open":m1>MT+MB,
        "beta_pair":beta_pair(E,m1,m2),
        "sigma_Z_both_charges_fb":sigma,
        "produced_pairs_before_decay":sigma*1000*L,
        "H1_rest_b_momentum_GeV":rest_frame_b_momentum(m1),
        "experimental_and_scalar_constraints_evaluated":False,
        "neutrino_t_channel_evaluated":False,
        "status":"KINEMATIC_GAUGE_ONLY_MASS_GRID_NOT_ALLOWED",
    }


def generate(m1s,m2s,gs,Es,Ls):
    if len(Es)!=len(Ls):
        raise ValueError("Energy and luminosity lists must have same length")
    if any(not 0<=g<=math.pi/2 for g in gs):
        raise ValueError("gamma outside charged mixing range")
    rows=[]
    for m1 in m1s:
        for m2 in m2s:
            if m2<=m1:
                continue
            for g in gs:
                for E,L in zip(Es,Ls):
                    rows.append(point(m1,m2,g,E,L))
    if not rows:
        raise ValueError("No valid mass pairs")
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mH1-GeV",default=DEFAULT_M1)
    p.add_argument("--mH2-GeV",default=DEFAULT_M2)
    p.add_argument("--gamma-rad",default=DEFAULT_GAMMAS)
    p.add_argument("--energies-GeV",default=DEFAULT_ENERGIES)
    p.add_argument("--luminosities-ab-inverse",default=DEFAULT_LUMINOSITY)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    m1s=numbers(args.mH1_GeV,"mH1")
    m2s=numbers(args.mH2_GeV,"mH2")
    gs=numbers(args.gamma_rad,"gamma")
    Es=numbers(args.energies_GeV,"energy")
    Ls=numbers(args.luminosities_ab_inverse,"luminosity")
    rows=generate(m1s,m2s,gs,Es,Ls)
    root=args.output_dir
    if root.exists() and any(root.iterdir()):
        raise ValueError("Use a new empty output folder")
    root.mkdir(parents=True,exist_ok=True)
    out=root/"mixed_pair_Z_only_mass_mixing_grid_NOT_ALLOWED.csv"
    with out.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    results={}
    for E in Es:
        subset=[r for r in rows if r["sqrt_s_GeV"]==E
                and r["cascade_H2_to_H1Z_open"]
                and r["H1_to_tb_open"]
                and r["kinematically_open"]]
        ranked=sorted(subset,key=lambda r:r["sigma_Z_both_charges_fb"],
                      reverse=True)
        results[str(E)+"_GeV"]={
            "candidate_rows_with_pair_and_cascade_and_tb_open":len(ranked),
            "top_five_BY_GAUGE_PRODUCTION_ONLY":[{
                k:r[k] for k in ("mH1_GeV","mH2_GeV","gamma_rad",
                                 "sigma_Z_both_charges_fb",
                                 "produced_pairs_before_decay",
                                 "H1_rest_b_momentum_GeV")}
                for r in ranked[:5]],
        }
    report={
        "status":STATUS,"points":len(rows),
        "input_mass_1_GeV":m1s,"input_mass_2_GeV":m2s,
        "input_charged_mixings_rad":gs,
        "input_energies_GeV":Es,"input_luminosities_ab_inverse":Ls,
        "alpha_fixed":ALPHA_EM,"sin2thetaW_fixed":SW2,
        "same_EW_scheme_as_prior_one_benchmark_analytic":True,
        "independent_MG5_validation_all_grid_points":False,
        "t_channel_muon_yukawa_contribution":False,
        "model_complete_scalar_or_flavor_consistency_tested":False,
        "H1H2_branching_fractions_used":False,
        "detector_significance_computed":False,
        "results_by_energy":results,
        "output_csv":str(out),
    }
    (root/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print("STATUS",STATUS)
    print("GRID_ROWS",len(rows))
    for key,v in results.items():
        print("ENERGY",key,"OPEN_MASS_MIXING_ROWS",
              v["candidate_rows_with_pair_and_cascade_and_tb_open"])
        for r in v["top_five_BY_GAUGE_PRODUCTION_ONLY"][:3]:
            print("  GAUGE_TOP",r["mH1_GeV"],r["mH2_GeV"],
                  "GAMMA",format(r["gamma_rad"],".5g"),
                  "SIGMA_FB",format(r["sigma_Z_both_charges_fb"],".6g"))
    print("PHYSICAL_ZEE_ALLOWED_BENCHMARKS_CALCULATED False")
    print("OUTPUT",out)


if __name__=="__main__":
    main()
