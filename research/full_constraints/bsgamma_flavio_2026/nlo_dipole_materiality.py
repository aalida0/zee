#!/usr/bin/env python3
"""Explicit NLO matching insertion *diagnostic* for the 2026 Misiak Eq.(4).

Published Eq4 is a LO-new-physics Wilson-coefficient formula, NOT a
renormalization-scheme-independent NNLO rate functional. Inserting
C7=C7^(0)+alpha_s(mu0)/(4pi) C7^(1) and similarly C8 quantifies a
specific subset of NLO matching, but MUST NOT be advertised as a
complete NLO/NNLO Zee branching ratio. Missing C4^1 and hard P_ij
interference/evolution, nonperturbative nuisance and NP covariance.

We also repeat the paper's one-state Type-II tanbeta=50 670GeV
reference with the SAME scheme, so any accidental root agreement can
be diagnosed instead of declaring calibration.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import flavio
from flavio.physics.running import running

from research.full_constraints.bsgamma_flavio_2026.np_remainder_budget import (
    one_state_reference, SOURCE_2HDM_TANBETA, SOURCE_2HDM_MASS_GEV
)
from research.full_constraints.bsgamma_flavio_2026.published_eq4_triangulation import (
    assess_point, MATCHING_CARD, PUBLISHED_SM, EXP, EXP_SIGMA,
    PUBLISHED_SM_SIGMA, COEF_C7, COEF_C8, Z95
)
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from scripts.zee_module5_bmu_nlo import matching

def rate(c7,c8):
    return PUBLISHED_SM+COEF_C7*c7+COEF_C8*c8

def one_state_curve(mt, a):
    def prediction(m):
        wc=matching(m,SOURCE_2HDM_TANBETA,mt,mu=160)
        lo=rate(wc["C7_LO"],wc["C8_LO"])
        partial_nlo=rate(
            wc["C7_LO"]+a*wc["C7_NLO_raw"],
            wc["C8_LO"]+a*wc["C8_NLO_raw"],
        )
        return {"mass_GeV":m, "LO_NP_Eq4":lo,
                "NLO_dipole_matching_inserted_into_Eq4":partial_nlo,
                "NLO_matching_dipole_delta":partial_nlo-lo,
                "C4_NLO_raw_omitted":wc["C4_NLO_raw"]}
    p670=prediction(670.)
    denom=math.hypot(EXP_SIGMA,PUBLISHED_SM_SIGMA)
    roots={}
    for tag,z in (("one_sided_95",1.6448536269514722),("two_sided_95",Z95)):
        xlo,xhi=350.,1500.
        def pull(m):
            return (prediction(m)["NLO_dipole_matching_inserted_into_Eq4"]-EXP)/denom
        if not pull(xlo)>z>pull(xhi):
            raise ArithmeticError("NLO-only 2HDM reference does not bracket chosen sensitivity root")
        for _ in range(55):
            mid=(xlo+xhi)/2
            if pull(mid)>z:xlo=mid
            else:xhi=mid
        roots[tag]=0.5*(xlo+xhi)
    return {"one_state_at_published_mass":p670,
            "source_full_order_published_bound_GeV":670.,
            "NLO_dipole_only_Eq4_gaussian_roots_GeV":roots,
            "NLO_dipole_only_not_full_NNLO":True,
            "one_state_NLO_only_does_not_calibrate_NP_uncertainty":True}

def run(path:Path):
    if path.exists():raise FileExistsError("No overwrite")
    if flavio.__version__!="2.7.1":raise RuntimeError("Need pinned flavio")
    card=json.loads(MATCHING_CARD.read_text())
    if card["matching_scale_GeV"]!=160:raise ValueError("Reference scale changed")
    pars=flavio.default_parameters.get_central_all()
    a_s=float(running.get_alpha(pars,160)["alpha_s"])
    a=a_s/(4*math.pi)
    if not 0.005<a<0.012:raise ArithmeticError("Unexpected alpha_s/(4pi)")
    flavio_sm=float(flavio.sm_prediction("BR(B->Xsgamma)"))
    p670=one_state_curve(card["mt_MSbar_GeV"],a)
    rows=[]
    zdenom=math.hypot(PUBLISHED_SM_SIGMA,EXP_SIGMA)
    for p in sorted(source_points(),key=lambda p:p["id"]):
        old=assess_point(p,card,flavio_sm,a_s)
        lo=old["published_2026_Eq4_prediction"]
        d7n=a*old["source_B_NLO_C7_raw"]
        d8n=a*old["source_B_NLO_C8_raw"]
        nlo=rate(old["source_B_LO_C7"]+d7n,old["source_B_LO_C8"]+d8n)
        if not math.isclose(nlo-lo,COEF_C7*d7n+COEF_C8*d8n,rel_tol=1e-10,abs_tol=1e-15):
            raise ArithmeticError("Linear coefficient expansion failed")
        row={
            "scalar_id":p["id"],
            "original_scalar_sha256":p["scalar_sha256"],
            "LO_NP_2026_Eq4_rate":lo,
            "matching_C7_NLO_ordinary_raw":old["source_B_NLO_C7_raw"],
            "matching_C8_NLO_ordinary_raw":old["source_B_NLO_C8_raw"],
            "matching_C4_NLO_ordinary_raw_UNINJECTED":old["source_B_NLO_C4_raw"],
            "alpha_s_160":a_s,
            "alpha_s_over_4pi":a,
            "NLO_dipole_matching_only_BR":nlo,
            "signed_NLO_dipole_matching_only_shift":nlo-lo,
            "relative_to_2026_LO_NP_shift":(nlo-lo)/(lo-PUBLISHED_SM),
            "NLO_dipole_only_gaussian_pull_NOT_FULL_MODEL":(nlo-EXP)/zdenom,
            "NLO_C4_included":False,
            "NLO_matrix_elements_consistently_updated":False,
            "NNLO_2026_implementation":False,
            "NP_uncertainty_sigma":None,
            "physical_B":"UNKNOWN",
            "global_acceptance":None,
        }
        rows.append(row)
        print("TWO_STATE_B_NLO_DIP_ONLY",p["id"],
              "LO",lo,"NLO_DIP_ONLY",nlo,
              "SHIFTONLY",row["signed_NLO_dipole_matching_only_shift"],
              "PULL",row["NLO_dipole_only_gaussian_pull_NOT_FULL_MODEL"],
              "PHYSICAL_UNKNOWN",flush=True)
    output={
        "schema":"zee-2026-Eq4-NLO-matching-dipoles-only-16-scalar-materiality-v1",
        "published_source":"arXiv:2608.29863v1 Eq4 assumes LO NP only",
        "source_quark_matching":"BMU ordinary real top-only MSbar 160GeV two-state NLO",
        "alpha_s_over_4pi_flavio_160":a,
        "one_state_670_reference":p670,
        "two_state_spectra":rows,
        "n_spectra":len(rows),
        "NLO_C4_included":False,
        "NLO_matrix_elements_included":False,
        "physical_B":"UNKNOWN",
        "full_model_exclusion":None,
        "global_acceptance":None,
        "claimed_theory_error":None,
        "interpretation":"NLO charged-scalar dipole matching materiality only. Using LO published coefficients as a high-order physical-rate functional is NOT a matched NLO calculation.",
    }
    path.write_text(json.dumps(output,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("B_NLO_DIPOLE_MATCHING_ONLY_DONE",len(rows),
          "FULL_B_UNKNOWN",flush=True)
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    run(args.output)

if __name__=="__main__":main()
