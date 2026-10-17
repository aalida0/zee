#!/usr/bin/env python3
"""Rank ALREADY scalar-theory + oblique-EWPO screened Zee spectra for Paper 2.

Input must be Gate B4's all_screened_candidates_NOT_ALLOWED.csv,
which stores quartic BFB/unitarity and correlated S,T,U screening plus
conditional LO nonleptonic charged-scalar decay fractions. This tool
does NOT perform the B4 physics screening again; it reuses its evidence.

Computes both charge-conjugate Z-only muon collider pair production
in the Yang/Wu alpha,G_F,MZ input scheme independently validated by
MG5 for B4_0000318. Conditional H1H1Z/tb tb Z yields use B4
INCLUDED-PARTIAL-WIDTH ratios and are NOT model-complete BR or
physical signal expectations. No full flavor/HiggsTools/direct bounds,
muon Yukawa t-channel, detector efficiencies, or BIB are included.

This is candidate prioritization, NOT a selection of allowed points.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import median
from zee_muon_mass_mixing_grid import ALPHA_YW,SW2_YW
from zee_muon_asymmetric_pair_pilot import (
    sigma_both_charges_fb,rest_frame_b_momentum,
    BR_Z_EE_MUMU, BR_Z_HADRONS, MZ
)

STATUS="PAPER2_SCALAR_EWPO_SCREENED_ZEE_MUON_REACH_PROXIES_NOT_ALLOWED"
REQUIRED=(
    "id","seed_id","mH1","mH2","mh2","ma","gamma",
    "alpha","beta","m12sq","lc","k1","k2","k12",
    "BR_H2_H1Z_nonleptonic_included_upper_proxy",
    "BR_H1_tb_nonleptonic_included_upper_proxy",
    "max_unitarity","chi2_Gfitter","chi2_PDG","candidate_status"
)
FIELDNAMES=(
    "candidate_id","seed_id","sqrt_s_GeV","luminosity_ab_inverse",
    "mH1_GeV","mH2_GeV","gamma_rad","mheavy_neutral_GeV","mA_GeV",
    "sigma_Z_both_charges_fb","n_produced_pairs",
    "H2_to_H1Z_nonleptonic_included_fraction_NOT_FULL_BR",
    "H1_to_tb_nonleptonic_included_fraction_NOT_FULL_BR",
    "n_tb_tb_Z_included_only_ceiling",
    "n_tb_tb_Z_ee_mumu_included_only_ceiling",
    "n_tb_tb_Z_hadrons_included_only_ceiling",
    "H1_b_rest_momentum_GeV","max_unitarity",
    "chi2_Gfitter","chi2_PDG",
    "model_allowed", "status"
)
SCENARIOS=((1500.,.5),(3000.,1.),(10000.,10.))


def input_candidate(row):
    if any(key not in row for key in REQUIRED):
        raise ValueError("Require original complete B4 scalar/EWPO screened CSV")
    if not row["candidate_status"].startswith("SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"):
        raise ValueError("Not a B4 scalar/EWPO-screened provisional candidate")
    p={"candidate_id":row["id"],"seed_id":row["seed_id"]}
    if not p["candidate_id"]:
        raise ValueError("Missing candidate id")
    for key in REQUIRED:
        if key in ("id","seed_id","candidate_status"):continue
        try:val=float(row[key])
        except (TypeError,ValueError) as exc:
            raise ValueError("Non-numeric B4 "+key) from exc
        if not math.isfinite(val):
            raise ValueError("Nonfinite B4 "+key)
        p[key]=val
    if not (200<=p["mH1"]<p["mH2"] and
            p["mH2"]>p["mH1"]+MZ and
            0<p["gamma"]<math.pi/2 and
            0<=p["BR_H2_H1Z_nonleptonic_included_upper_proxy"]<=1
            and 0<=p["BR_H1_tb_nonleptonic_included_upper_proxy"]<=1):
        raise ValueError("Unphysical B4 kinematic or proxy inputs")
    return p


def evaluate(p,E,L):
    sig=sigma_both_charges_fb(E,p["mH1"],p["mH2"],p["gamma"],
                              alpha=ALPHA_YW,sw2=SW2_YW)
    n=sig*1000*L
    br2=p["BR_H2_H1Z_nonleptonic_included_upper_proxy"]
    br1=p["BR_H1_tb_nonleptonic_included_upper_proxy"]
    cascade=n*br2*br1**2
    return {
        "candidate_id":p["candidate_id"],"seed_id":p["seed_id"],
        "sqrt_s_GeV":E,"luminosity_ab_inverse":L,
        "mH1_GeV":p["mH1"],"mH2_GeV":p["mH2"],
        "gamma_rad":p["gamma"],
        "mheavy_neutral_GeV":p["mh2"],"mA_GeV":p["ma"],
        "sigma_Z_both_charges_fb":sig,
        "n_produced_pairs":n,
        "H2_to_H1Z_nonleptonic_included_fraction_NOT_FULL_BR":br2,
        "H1_to_tb_nonleptonic_included_fraction_NOT_FULL_BR":br1,
        "n_tb_tb_Z_included_only_ceiling":cascade,
        "n_tb_tb_Z_ee_mumu_included_only_ceiling":
            cascade*BR_Z_EE_MUMU,
        "n_tb_tb_Z_hadrons_included_only_ceiling":
            cascade*BR_Z_HADRONS,
        "H1_b_rest_momentum_GeV":rest_frame_b_momentum(p["mH1"]),
        "max_unitarity":p["max_unitarity"],
        "chi2_Gfitter":p["chi2_Gfitter"],
        "chi2_PDG":p["chi2_PDG"],
        "model_allowed":"unknown",
        "status":"SCALAR_EWPO_SCREEN_AND_INCLUDED_WIDTH_CEILING_ONLY_NOT_ALLOWED",
    }


def mass_diverse(rows,n=8):
    """Keep one candidate per 25-GeV H1 and 50-GeV H2 mass cell."""
    seen=set();out=[]
    for r in rows:
        key=(int(r["mH1_GeV"]//25),int(r["mH2_GeV"]//50))
        if key not in seen:
            seen.add(key);out.append(r)
        if len(out)>=n:break
    return out


def read_csv(path):
    with Path(path).open(newline="") as f:
        rd=csv.DictReader(f)
        if not rd.fieldnames or any(k not in rd.fieldnames for k in REQUIRED):
            raise ValueError("B4 CSV header incomplete")
        points=[input_candidate(x) for x in rd]
    if not points or len({p["candidate_id"] for p in points})!=len(points):
        raise ValueError("B4 empty or duplicate IDs")
    return points


def run(input_file,output):
    points=read_csv(input_file)
    rows=[evaluate(p,E,L) for p in points for E,L in SCENARIOS]
    if output.exists() and any(output.iterdir()):
        raise ValueError("Choose empty output directory")
    output.mkdir(parents=True,exist_ok=True)
    path=output/"scalar_EWPO_screened_Z_only_conditional_ceiling_NOT_ALLOWED.csv"
    with path.open("w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=FIELDNAMES)
        wr.writeheader();wr.writerows(rows)
    stats={}
    for E,_ in SCENARIOS:
        subset=[r for r in rows if r["sqrt_s_GeV"]==E]
        subset.sort(key=lambda r:r["n_tb_tb_Z_ee_mumu_included_only_ceiling"],
                    reverse=True)
        key=f"{int(E)}_GeV"
        stats[key]={
            "max_sigma_fb":max(r["sigma_Z_both_charges_fb"] for r in subset),
            "median_sigma_fb":median(r["sigma_Z_both_charges_fb"] for r in subset),
            "mass_diverse_conditional_ceiling_top":mass_diverse(subset),
            "max_truth_ll_ceiling":subset[0][
                "n_tb_tb_Z_ee_mumu_included_only_ceiling"],
        }
    manifest={
        "status":STATUS,
        "n_distinct_B4_spectra":len(points),
        "n_energy_spectrum_rows":len(rows),
        "mH1_range_GeV":[min(p["mH1"] for p in points),
                            max(p["mH1"] for p in points)],
        "mH2_range_GeV":[min(p["mH2"] for p in points),
                            max(p["mH2"] for p in points)],
        "gamma_range_rad":[min(p["gamma"] for p in points),
                            max(p["gamma"] for p in points)],
        "source_B4_csv":str(input_file),
        "YangWu_alpha":ALPHA_YW,"YangWu_sw2":SW2_YW,
        "n_model_allowed_points":None,
        "full_physical_neutrino_LFV_HiggsTools_flavor":False,
        "B4_conditional_included_BR_is_physical":False,
        "muon_neutrino_tchannel_included":False,
        "muon_BIB_detector_or_SM_backgrounds_included":False,
        "selection_for_diversity":"one maximum conditional yield per "
                                  "25-GeV H1 / 50-GeV H2 mass cell",
        "scenarios":stats,
        "output_csv":str(path)}
    (output/"summary.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("STATUS",STATUS)
    print("B4_SPECTRA",len(points),"ENERGY_SPECTRUM_ROWS",len(rows))
    print("SCANNED_MH1_RANGE",manifest["mH1_range_GeV"])
    print("SCANNED_MH2_RANGE",manifest["mH2_range_GeV"])
    print("SCANNED_GAMMA_RANGE",manifest["gamma_range_rad"])
    for E,_ in SCENARIOS:
        key=f"{int(E)}_GeV";x=stats[key]
        print("ENERGY_GEV",E,"MAX_SIGMA_FB",format(x["max_sigma_fb"],".6g"),
              "MAX_TRUTH_Z_TO_LL_INCLUDED_ONLY",format(
                  x["max_truth_ll_ceiling"],".6g"))
        for r in x["mass_diverse_conditional_ceiling_top"][:4]:
            print("  MASS_DIVERSE",r["candidate_id"],
                  "m1",round(r["mH1_GeV"],2),
                  "m2",round(r["mH2_GeV"],2),
                  "gamma",round(r["gamma_rad"],3),
                  "sigma_fb",round(r["sigma_Z_both_charges_fb"],5),
                  "truth_Z_ll_ceiling",round(
                      r["n_tb_tb_Z_ee_mumu_included_only_ceiling"],2))
    print("COMPLETE_EXPERIMENTAL_CONSTRAINTS False")
    print("MODEL_ALLOWED_POINTS unknown")
    print("OUTPUT",path)
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--b4-csv",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    run(a.b4_csv,a.output_dir)


if __name__=="__main__":
    main()
