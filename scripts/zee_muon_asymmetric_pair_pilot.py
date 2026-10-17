#!/usr/bin/env python3
"""Zee asymmetric H1+ H2- muon-collider analytical GAUGE-ONLY pilot.

Cross section for mu+mu- -> H1+H2- AND its charge conjugate via Z*.
Tree-level unpolarized massless initial muons, no neutrino t-channel,
ISR, EW Sudakov, beams, detector acceptance, or beam-induced background.
The nonresonant process is equally available in e+e- at equal s under
these approximations; it is NOT intrinsically muon specific.

Coupling: g(ZH1H2) = e sin(2 gamma)/(4 sW cW) [up to sign],
Florentino, Romao, Silva, EPJC 81 (2021) 1148, App. B Eqs.(B.2),(B.3).
Cross section obtained from the exact scalar-pair angular distribution
d sigma/d cos(theta) proportional (1-cos(theta)^2) lambda_bar^(3/2).

Inputs: *already screened* B4C joined CSV including B3 included-only
BRs. Output event counts use those CONDITIONAL branching fractions,
not model-complete physical widths and not experimental limits.

This is a fail-closed FEASIBILITY diagnostic, not a physical
discovery sensitivity, full UFO calculation, or viable Zee benchmark.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import median

STATUS="ZEE_MUON_COLLIDER_GAUGE_ONLY_PRELIMINARY_NOT_PHYSICAL_REACH"
GEV_MINUS2_TO_FB=3.893793656e11
MZ=91.1876
SW2=0.23122
ALPHA_EM=1/128.0     # fixed tree-level benchmark scheme
MT=172.5
MB=4.18
BR_Z_EE_MUMU=0.0673  # 2 charged light-lepton channels combined
BR_Z_HADRONS=0.6991
FIELDS=(
    "candidate_id","seed_id","energy_TeV","luminosity_ab_inverse",
    "mH1_GeV","mH2_GeV","gamma",
    "charge_sum_sigma_Z_only_fb",
    "one_charge_sigma_Z_only_fb",
    "beta_pair","endpoint_tb_rest_b_momentum_GeV",
    "B3_included_BR_H2_H1Z_NOT_PHYSICAL",
    "B3_included_BR_H1_tb_NOT_PHYSICAL",
    "produced_pairs",
    "produced_H1H1Z_tb_tb_included_only",
    "truth_Z_ee_mumu_tb_tb_included_only",
    "truth_Z_hadrons_tb_tb_included_only",
    "discovery_or_exclusion_calculated","status"
)
SCENARIOS=((1.5,0.5),(3.0,1.0),(10.0,10.0))


def finite(x,name):
    try:v=float(x)
    except (TypeError,ValueError) as exc:
        raise ValueError("Invalid "+name) from exc
    if not math.isfinite(v):raise ValueError("Nonfinite "+name)
    return v


def beta_pair(E,m1,m2):
    """2-body unequal-mass beta=lambda^(1/2)/s, not simple sqrt(1-4m²/s)."""
    for name,v in (("E",E),("m1",m1),("m2",m2)):
        if not math.isfinite(v) or v<=0:
            raise ValueError("Invalid "+name)
    if E<=m1+m2:return 0.
    s=E*E
    lam=(1.-(m1+m2)**2/s)*(1.-(m1-m2)**2/s)
    if lam<0:return 0.
    return math.sqrt(lam)


def sigma_one_charge_fb(E,m1,m2,gamma,*,alpha=ALPHA_EM,sw2=SW2):
    """Unpolarized s-channel Z* differential integral, one charge ordering.

    sigma_one = (pi alpha^2 / 3s) * beta_pair^3 * R_Z
    R_Z=sin²(2gamma) * [(-1/2+sW²)²+(sW²)²] /
        [32 (sW² cW²)²] * |s/(s-MZ²)|².
    This is *relative* to the scalar-pair photon Q=+1 result,
    sigma_gamma=pi alpha² beta³/(3s).
    """
    if not (0<sw2<1 and 0<alpha<1 and math.isfinite(gamma)):
        raise ValueError("Invalid EW couplings/mixing")
    beta=beta_pair(E,m1,m2)
    if beta==0:return 0.
    s=E*E
    if abs(s-MZ*MZ)<1:
        raise ValueError("Need finite Z-width near resonance")
    gL=-.5+sw2
    gR=sw2
    ratio=(math.sin(2*gamma)**2*(gL*gL+gR*gR)/
           (32.*(sw2*(1-sw2))**2)*(s/(s-MZ*MZ))**2)
    return (math.pi*alpha**2/(3*s))*beta**3*ratio*GEV_MINUS2_TO_FB


def sigma_both_charges_fb(E,m1,m2,gamma,**kwargs):
    return 2.*sigma_one_charge_fb(E,m1,m2,gamma,**kwargs)


def rest_frame_b_momentum(m1,mt=MT,mb=MB):
    """Momentum of b from H1+->t bbar in the H1 rest frame."""
    if not all(math.isfinite(x) and x>=0 for x in (m1,mt,mb)):
        raise ValueError("Invalid mass")
    if m1<=mt+mb:return 0.
    return math.sqrt(
        (m1*m1-(mt+mb)**2)*(m1*m1-(mt-mb)**2))/(2*m1)


def to_candidate(row):
    needed=("candidate_id","seed_id","mH1","mH2","gamma",
            "B3_BR_H2_H1Z_median","B3_BR_H1_tb_median")
    if any(k not in row for k in needed):
        raise ValueError("Require validated B4C joined CSV with "+", ".join(needed))
    p={"candidate_id":row["candidate_id"],"seed_id":row["seed_id"]}
    if not p["candidate_id"]:raise ValueError("Missing candidate ID")
    for key in needed[2:]:
        p[key]=finite(row[key],key)
    if not (p["mH1"]<p["mH2"] and
            0<=p["B3_BR_H2_H1Z_median"]<=1 and
            0<=p["B3_BR_H1_tb_median"]<=1):
        raise ValueError("Invalid masses/conditional BRs")
    if "candidate_status" in row and "NOT_ALLOWED" not in row["candidate_status"]:
        raise ValueError("Do not import physical-allowed candidate labels")
    return p


def evaluate(p,energy_tev,luminosity_ab):
    if not math.isfinite(luminosity_ab) or luminosity_ab<=0:
        raise ValueError("Require positive luminosity")
    E=energy_tev*1000.
    one=sigma_one_charge_fb(E,p["mH1"],p["mH2"],p["gamma"])
    both=2*one
    prod=both*luminosity_ab*1000.
    br2=p["B3_BR_H2_H1Z_median"]
    br1=p["B3_BR_H1_tb_median"]
    cascade=prod*br2*br1**2
    return {
        "candidate_id":p["candidate_id"],"seed_id":p["seed_id"],
        "energy_TeV":energy_tev,"luminosity_ab_inverse":luminosity_ab,
        "mH1_GeV":p["mH1"],"mH2_GeV":p["mH2"],"gamma":p["gamma"],
        "charge_sum_sigma_Z_only_fb":both,"one_charge_sigma_Z_only_fb":one,
        "beta_pair":beta_pair(E,p["mH1"],p["mH2"]),
        "endpoint_tb_rest_b_momentum_GeV":
            rest_frame_b_momentum(p["mH1"]),
        "B3_included_BR_H2_H1Z_NOT_PHYSICAL":br2,
        "B3_included_BR_H1_tb_NOT_PHYSICAL":br1,
        "produced_pairs":prod,
        "produced_H1H1Z_tb_tb_included_only":cascade,
        "truth_Z_ee_mumu_tb_tb_included_only":cascade*BR_Z_EE_MUMU,
        "truth_Z_hadrons_tb_tb_included_only":cascade*BR_Z_HADRONS,
        "discovery_or_exclusion_calculated":False,
        "status":"GAUGE_ONLY_LO_TRUTH_COUNTS_INCLUDED_BRS_NOT_ALLOWED"
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--joined-csv",type=Path,required=True,
                    help="B4C joined table with B3 width-corrected conditional BR")
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args()
    with a.joined_csv.open(newline="") as fh:
        rd=csv.DictReader(fh)
        if not rd.fieldnames:raise ValueError("Missing header")
        points=[to_candidate(row) for row in rd]
    if not points or len(set(p["candidate_id"] for p in points))!=len(points):
        raise ValueError("Empty or duplicate benchmark list")
    rows=[evaluate(p,E,L) for p in points for E,L in SCENARIOS]
    a.output_dir.mkdir(parents=True,exist_ok=True)
    path=a.output_dir/"charge_sum_gauge_only_kinematic_pilot_NOT_ALLOWED.csv"
    with path.open("w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    stats={}
    for energy,_ in SCENARIOS:
        sub=[r for r in rows if r["energy_TeV"]==energy]
        stats[str(energy)+"_TeV"]={
            "max_gauge_sigma_both_fb":
                max(r["charge_sum_sigma_Z_only_fb"] for r in sub),
            "median_gauge_sigma_both_fb":
                median(r["charge_sum_sigma_Z_only_fb"] for r in sub),
            "max_truth_Z_ee_mumu_tb_tb_included_only":
                max(r["truth_Z_ee_mumu_tb_tb_included_only"] for r in sub),
        }
    details={
        "status":STATUS,"points":len(points),
        "scenarios_energy_TeV_luminosity_ab_inverse":SCENARIOS,
        "alpha_fixed":ALPHA_EM,"sin2thetaW_fixed":SW2,
        "Z_ee_mumu_BR_fixed":BR_Z_EE_MUMU,
        "Z_hadronic_BR_fixed":BR_Z_HADRONS,
        "source":"Florentino Romao Silva EPJC 81 (2021) 1148 Appendix B.3b",
        "cross_section_spin_averaged":True,
        "both_charge_conjugates_included":True,
        "s_channel_Z_only":True,"muon_specific_vs_electron_gauge_only":False,
        "t_channel_neutrino_fermion_yukawas_included":False,
        "ISR_and_beam_energy_spread_included":False,
        "muon_collider_BIB_detector_response_included":False,
        "full_Zee_physical_branching_ratios_validated":False,
        "full_Zee_experimental_constraints_applied":False,
        "validated_UFO_vs_analytic_cross_section":False,
        "statistically_valid_discovery_or_exclusion":False,
        "statistics":stats,
        "output_csv":str(path)}
    (a.output_dir/"summary.json").write_text(
        json.dumps(details,indent=2)+"\n")
    print("STATUS",STATUS)
    print("SCALAR_POINTS",len(points))
    for e,l in SCENARIOS:
        x=stats[str(e)+"_TeV"]
        print("ENERGY_TEV",e,"L_AB_INV",l,
              "MAX_SIGMA_BOTH_FB",format(x["max_gauge_sigma_both_fb"],".6g"),
              "MAX_Z_EE_MUMU_TRUTH",format(
                  x["max_truth_Z_ee_mumu_tb_tb_included_only"],".6g"))
    print("T_CHANNEL_NEUTRINO_INCLUDED False")
    print("PHYSICAL_REACH_CALCULATED False")
    print("OUTPUT",path)


if __name__=="__main__":
    main()
