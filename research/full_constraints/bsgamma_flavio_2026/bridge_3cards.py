#!/usr/bin/env python3
"""Independent flavio v2.7.1 WET C7/C8 rate cross-check for two Zee scalar cards.

IMPORTANT: This is not a physical full-model B->X_s gamma exclusion.
Source-matched ordinary BMU NDR top-only real charged-scalar coefficients
are passed to flavio/Wilson in WET/flavio C7_bs and C8_bs. The NLO
case intentionally inserts the *dipole-only* NLO matching improvement;
it cannot reproduce independent C4_NLO, C1..C6 evolution or unprovided
NP nonperturbative/EW uncertainties. A direct 95% CL exclusion is forbidden.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path

import flavio
from wilson import Wilson

from scripts.zee_module5_bmu_nlo import matching
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

ROOT = Path(__file__).resolve().parents[3]
INPUT_CARD = ROOT / "module14/conditional_scan/matching_card.json"
IDS = (15591, 15673, 2264)
ENERGY_SCALE = 160.0
OBS = "BR(B->Xsgamma)"
EXPERIMENT_CENTRAL = 3.49e-4
EXPERIMENT_SIGMA = 0.19e-4
ORDERED_KEYS = ("C7_LO", "C8_LO", "C4_NLO_raw", "C7_NLO_raw", "C8_NLO_raw")


def ordinary(p, mt, mu, gamma=None, mass1=None, mass2=None):
    m1 = p["mH1"] if mass1 is None else mass1
    m2 = p["mH2"] if mass2 is None else mass2
    gg = p["gamma"] if gamma is None else gamma
    tb = math.tan(p["beta"])
    weights = (math.cos(gg)**2, math.sin(gg)**2)
    pieces = [matching(float(m), tb, mt, mu=mu) for m in (m1, m2)]
    return {k: math.fsum(weight * part[k] for weight, part in zip(weights, pieces))
            for k in ORDERED_KEYS}


def wilson_rate(c7, c8, mu):
    wc = Wilson(
        {"C7_bs": float(c7), "C8_bs": float(c8)},
        scale=float(mu), eft="WET", basis="flavio"
    )
    return float(flavio.np_prediction(OBS, wc))


def assess(p, mt, mu, alpha_s_match, sm):
    c = ordinary(p, mt, mu)
    zero = wilson_rate(0.0, 0.0, mu)
    if not math.isclose(zero, sm, rel_tol=1e-10):
        raise ArithmeticError("No-NP WET source fails to reproduce flavio SM")
    lo = wilson_rate(c["C7_LO"], c["C8_LO"], mu)
    a = alpha_s_match / (4 * math.pi)
    approximate_c7 = c["C7_LO"] + a * c["C7_NLO_raw"]
    approximate_c8 = c["C8_LO"] + a * c["C8_NLO_raw"]
    improved = wilson_rate(approximate_c7, approximate_c8, mu)
    for key, val in {"LO":lo, "dipole_NLO_only":improved}.items():
        if val <= 0 or not math.isfinite(val):
            raise ArithmeticError("Invalid flavio "+key+" inclusive rate")
    # Falsify common 2-charged mixing mistakes: gamma endpoints, interchange
    # gamma->gamma+pi/2 and m1<->m2, equal masses mixing independence.
    zero_g = ordinary(p, mt, mu, gamma=0)
    half_g = ordinary(p, mt, mu, gamma=math.pi/2)
    exchange = ordinary(
        p, mt, mu, gamma=p["gamma"]+math.pi/2,
        mass1=p["mH2"], mass2=p["mH1"]
    )
    equal = ordinary(
        p, mt, mu, mass1=p["mH1"], mass2=p["mH1"],
        gamma=0.673
    )
    single1 = matching(p["mH1"], math.tan(p["beta"]), mt, mu)
    single2 = matching(p["mH2"], math.tan(p["beta"]), mt, mu)
    for key in ORDERED_KEYS:
        for q, r in ((zero_g[key],single1[key]),
                     (half_g[key],single2[key]),
                     (exchange[key],c[key]),
                     (equal[key],single1[key])):
            if not math.isclose(q,r,rel_tol=3e-11,abs_tol=1e-12):
                raise ArithmeticError("Two-state BMU matching identity broken: "+key)
    return {
        "ordinary_bmu_matching":c,
        "alpha_s_match":alpha_s_match,
        "alpha_s_over_4pi":a,
        "wilson_C7_LO":c["C7_LO"],
        "wilson_C8_LO":c["C8_LO"],
        "wilson_C7_LO_plus_NLO_dipole_only":approximate_c7,
        "wilson_C8_LO_plus_NLO_dipole_only":approximate_c8,
        "flavio_SM_rate":sm,
        "flavio_lo_C7C8_NP_rate":lo,
        "flavio_LOplusNLO_C7C8_only_rate":improved,
        "difference_NLOdipoleOnly_minus_LO":improved-lo,
        "flavio_LO_rate_minus_experimental_central":lo-EXPERIMENT_CENTRAL,
        "flavio_LO_rate_experimental_only_pull":(lo-EXPERIMENT_CENTRAL)/EXPERIMENT_SIGMA,
        "flavio_dipole_only_rate_experimental_only_pull":
            (improved-EXPERIMENT_CENTRAL)/EXPERIMENT_SIGMA,
        "NLO_C4_ordinary_matching_diagnostic":c["C4_NLO_raw"],
        "NLO_C4_inserted_into_flavio":False,
        "flavio_theory_sigma":None,
        "Zee_NP_theory_sigma":None,
        "B_physical_exclusion":None,
        "basis_bridge_status":"WET_C7C8_LO_BMU_OPERATOR_CONVENTION_CHECKED__NLO_C4_NOT_INCLUDED",
        "source_FF_sector":"top_only_real_NDR_ms0_LO_plus_dipole_NLO_diagnostic",
        "physical_B":"UNKNOWN",
        "global_acceptance":None,
    }


def run(out:Path):
    if out.exists():
        raise FileExistsError("Refuse overwriting evidence")
    if flavio.__version__!="2.7.1":
        raise RuntimeError("Unpinned flavio runtime")
    card=json.loads(INPUT_CARD.read_text())
    if card["matching_scale_GeV"]!=ENERGY_SCALE:
        raise ValueError("Reference matching scale mismatch")
    mt=float(card["mt_MSbar_GeV"])
    par=flavio.default_parameters.get_central_all()
    from flavio.physics.running import running
    alpha_s=float(running.get_alpha(par,ENERGY_SCALE)["alpha_s"])
    if not 0.08<alpha_s<0.14:
        raise ArithmeticError("No matched perturbative alpha_s(160)")
    sm=float(flavio.sm_prediction(OBS))
    if not 3.0e-4<sm<3.9e-4:
        raise ArithmeticError("flavio SM inconsistent with published baseline at 1.6 GeV cut")
    points={z["id"]:z for z in source_points()}
    cases=[]
    for pid in IDS:
        point=points[pid]
        if point["gates"]["vacuum"]["assessment"]!="PASS":
            raise ValueError("Original certified spectrum changed")
        if point["bsg_nominal_classification"]!="APPROX_COMPATIBLE":
            raise ValueError("Reference B diagnostic changed")
        p=point["input_card"]["physical"]
        row=assess(p,mt,ENERGY_SCALE,alpha_s,sm)
        row.update({
            "scalar_id":pid,
            "scalar_sha256":point["scalar_sha256"],
            "mH1_GeV":p["mH1"],"mH2_GeV":p["mH2"],
            "tanbeta":math.tan(p["beta"]), "gamma":p["gamma"],
            "old_2026_linear_diagnostic_pull":point["conditional_pull"],
        })
        cases.append(row)
        print("FLAVIO_INDEPENDENT_ZEE",pid,"SM",sm,
              "LO",row["flavio_lo_C7C8_NP_rate"],
              "DIPOLE_NLO_ONLY",row["flavio_LOplusNLO_C7C8_only_rate"],
              "C4_NLO_NOT_INCLUDED",row["NLO_C4_ordinary_matching_diagnostic"],
              "B_PHYSICAL UNKNOWN",flush=True)
    result={
        "schema":"zee-flavio-v2.7.1-20261111-independent-C7-C8-diagnostic-v1",
        "flavio_version":flavio.__version__,
        "wilson_version_from_metadata":None,
        "python_version":platform.python_version(),
        "matching_scale_GeV":ENERGY_SCALE,
        "matching_mt_MSbar_GeV":mt,
        "alpha_s_flavio_at_160":alpha_s,
        "observable":OBS,
        "photon_cut_GeV":1.6,
        "experiment_2026_snapshot":{"BR":EXPERIMENT_CENTRAL, "sigma_experiment":EXPERIMENT_SIGMA},
        "cases":cases,
        "n_case":len(cases),
        "comparison":"independent public flavio inclusive rate, WET Wilson C7/C8 only",
        "no_complete_NLO_C4_C1toC6":True,
        "no_new_NP_uncertainty":True,
        "full_B_physics":"UNKNOWN",
        "global_acceptance":None,
        "allowed_scalar_point_count":None,
    }
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return result

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    run(args.output)

if __name__=="__main__":
    main()
