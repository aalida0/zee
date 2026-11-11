#!/usr/bin/env python3
"""Source-qualified 2026 B->Xs gamma leading-NP constraints on 16 Zee scalars.

Published reference: Misiak et al arXiv:2608.29863v1 Eq.(4):
    1e4 * BR = (3.54 +/- 0.14) - 8.51 DeltaC7 - 2.16 DeltaC8
with mu0=160 GeV. Gaussian pull with 2026 exp (3.49 +/- 0.19)e-4
is an *approximation*, not a calibrated full Zee likelihood.

Use independent native/BMU two-state top-only matching at LO, check against
the existing Module14 linear reference. Compare the NP *shift only*
against public flavio 2.7.1, never pretend old flavio absolute SM baseline
equals the new 2026 SM baseline. A baseline-transferred observable is only
an exploratory method-difference test, not an independent 2026 prediction.

NP NLO and model uncertainty are not established by this script.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import flavio
from flavio.physics.running import running

from research.full_constraints.bsgamma_flavio_2026.bridge_3cards import ordinary,wilson_rate
from module14.conditional_scan.flavor import evaluate as prior_diagnostic
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

ROOT=Path(__file__).resolve().parents[3]
MATCHING_CARD=ROOT/"module14/conditional_scan/matching_card.json"
MISIARK_ARXIV="2608.29863v1"
PUBLISHED_SM=3.54e-4
PUBLISHED_SM_SIGMA=0.14e-4
EXP=3.49e-4
EXP_SIGMA=0.19e-4
COEF_C7=-8.51e-4
COEF_C8=-2.16e-4
Z95=1.959963984540054


def assess_point(p,card,flavio_sm,alpha_s):
    raw=p["input_card"]
    physical=raw["physical"]
    native=ordinary(physical,card["mt_MSbar_GeV"],card["matching_scale_GeV"])
    published=(PUBLISHED_SM+COEF_C7*native["C7_LO"]+COEF_C8*native["C8_LO"])
    legacy=prior_diagnostic(raw,card)
    if legacy["status"]!="DIAGNOSTIC_ONLY":
        raise ArithmeticError("Old C1 scope changed")
    if not math.isclose(legacy["BR_linear_2026"],published,rel_tol=1e-10,abs_tol=5e-12):
        raise ArithmeticError("Native BMU LO source disagrees with published Eq.(4) backend")
    if abs(legacy["DeltaC7_LO"]-native["C7_LO"])>1e-10 or abs(legacy["DeltaC8_LO"]-native["C8_LO"])>1e-10:
        raise ArithmeticError("Two source-matched Wilson coefficients no longer agree")
    mu=card["matching_scale_GeV"]
    raw_lo=wilson_rate(native["C7_LO"],native["C8_LO"],mu)
    a=alpha_s/(4*math.pi)
    raw_dipNLO=wilson_rate(native["C7_LO"]+a*native["C7_NLO_raw"],
                           native["C8_LO"]+a*native["C8_NLO_raw"],mu)
    delta_flavio_lo=raw_lo-flavio_sm
    delta_flavio_dipNLO=raw_dipNLO-flavio_sm
    diagnostic_transfer_lo=PUBLISHED_SM+delta_flavio_lo
    diagnostic_transfer_dipNLO=PUBLISHED_SM+delta_flavio_dipNLO
    denom=math.hypot(PUBLISHED_SM_SIGMA,EXP_SIGMA)
    def pull(rate):return (rate-EXP)/denom
    passes=[abs(pull(x))<Z95 for x in (
        published,diagnostic_transfer_lo,diagnostic_transfer_dipNLO
    )]
    return {
        "scalar_id":p["id"],
        "original_scalar_sha256":p["scalar_sha256"],
        "source_scalar_vacuum_sufficient_certificate":"PASS",
        "model_mH1_GeV":physical["mH1"],
        "model_mH2_GeV":physical["mH2"],
        "model_gamma":physical["gamma"],
        "model_tanbeta":math.tan(physical["beta"]),
        "source_B_LO_C7":native["C7_LO"],
        "source_B_LO_C8":native["C8_LO"],
        "source_B_NLO_C4_raw":native["C4_NLO_raw"],
        "source_B_NLO_C7_raw":native["C7_NLO_raw"],
        "source_B_NLO_C8_raw":native["C8_NLO_raw"],
        "published_2026_Eq4_prediction":published,
        "published_2026_Eq4_pull":pull(published),
        "legacy_2026_diagnostic_pull":legacy["conditional_pull"],
        "flavio_2026_independent_LO_NP_shift":delta_flavio_lo,
        "flavio_dipole_only_NLO_NP_shift":delta_flavio_dipNLO,
        "flavio_original_SM_prediction":flavio_sm,
        "flavio_original_LO_prediction":raw_lo,
        "flavio_original_dipole_only_NLO_prediction":raw_dipNLO,
        "heuristic_SM_baseline_transferred_LO":diagnostic_transfer_lo,
        "heuristic_SM_baseline_transferred_dipole_NLO":diagnostic_transfer_dipNLO,
        "heuristic_transferred_LO_pull":pull(diagnostic_transfer_lo),
        "heuristic_transferred_dipole_NLO_pull":pull(diagnostic_transfer_dipNLO),
        "published_vs_flavio_LO_NP_shift_difference":delta_flavio_lo-(published-PUBLISHED_SM),
        "published_eq4_gaussian_interior":passes[0],
        "all_three_diagnostic_prescriptions_gaussian_interior":all(passes),
        "mixed_prescription_fragility":passes.count(True)!=3,
        "NLO_C4_inserted_in_flavio":False,
        "NP_quadratic_remainder_bound":None,
        "NP_model_theory_uncertainty":None,
        "published_Eq4_theory_uncertainty_is_SM_only":True,
        "physical_B":"UNKNOWN",
        "full_model_exclusion":None,
        "global_acceptance":None,
    }


def run(path):
    if path.exists():
        raise FileExistsError("Never overwrite physical validation receipts")
    if flavio.__version__!="2.7.1":
        raise RuntimeError("Pin flavio 2.7.1")
    card=json.loads(MATCHING_CARD.read_text())
    if card["matching_scale_GeV"]!=160 or card["quark_scheme"]!="MSbar_top_at_matching_scale_real_top_only_ms0":
        raise ValueError("Unexpected source scheme")
    par=flavio.default_parameters.get_central_all()
    alpha_s=float(running.get_alpha(par,160)["alpha_s"])
    flavio_sm=float(flavio.sm_prediction("BR(B->Xsgamma)"))
    points=source_points()
    if len(points)!=16:
        raise ArithmeticError("Original 16-scalar conditional input changed")
    rows=[]
    for p in sorted(points,key=lambda r:r["id"]):
        if (p["gates"]["vacuum"]["assessment"]!="PASS" or
            p["bsg_nominal_classification"]!="APPROX_COMPATIBLE"):
            raise ValueError("Scalar source certification changed")
        z=assess_point(p,card,flavio_sm,alpha_s)
        rows.append(z)
        print("B2026_SCALAR",p["id"],"EQ4",z["published_2026_Eq4_prediction"],
              "EQ4_PULL",z["published_2026_Eq4_pull"],
              "FLAVIO_TRANSFER_LO",z["heuristic_SM_baseline_transferred_LO"],
              "LO_PULL",z["heuristic_transferred_LO_pull"],
              "DIPOLE_NLO_PULL",z["heuristic_transferred_dipole_NLO_pull"],
              "THREE_WAY_INTERIOR",z["all_three_diagnostic_prescriptions_gaussian_interior"],
              "PHYSICAL_B_UNKNOWN",flush=True)
    output={
        "schema":"zee-sixteen-scalar-published-2026-Eq4-flavio-independent-NP-shift-compare-v1",
        "published_source":MISIARK_ARXIV,
        "published_locator":"arXiv:2608.29863v1 page 4 Eq.(4); LO NP C7,8 at mu0=160 GeV",
        "published_2026_SM_branching_fraction":PUBLISHED_SM,
        "published_2026_SM_theory_sigma":PUBLISHED_SM_SIGMA,
        "experimental_snapshot":EXP,"experimental_sigma":EXP_SIGMA,
        "gaussian_two_sided_z":Z95,
        "gaussian_assumptions":"SM and experimental errors independent, no NP theory covariance, Eq4 neglects quadratic DeltaC7,8; only diagnostic interior, not full constraints",
        "coefficient_sources":"BMU top-only real NDR, two charged states summed cos²gamma/sin²gamma with one matching scale",
        "flavio_source_version":flavio.__version__,
        "flavio_SM_baseline_is_historical":True,
        "flavio_baseline_transfer_is_not_updated_rate_prediction":True,
        "n_spectra":len(rows),
        "n_published_Eq4_gaussian_interior":sum(r["published_eq4_gaussian_interior"] for r in rows),
        "n_all_three_diagnostic_prescriptions_gaussian_interior":
            sum(r["all_three_diagnostic_prescriptions_gaussian_interior"] for r in rows),
        "scalars":rows,
        "physical_B":"UNKNOWN","NP_theory_covariance":None,
        "published_2026_95CL_2HDMII_mHplus_min_GeV":670,
        "published_2HDMII_mHplus_bound_is_not_direct_Zee_two_state_cut":True,
        "global_acceptance":None,
    }
    path.write_text(json.dumps(output,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("B2026_TRIANGULATION_DONE",len(rows),
          "EQ4_INTERIOR",output["n_published_Eq4_gaussian_interior"],
          "THREE_WAY_DIAGNOSTIC_INTERIOR",output["n_all_three_diagnostic_prescriptions_gaussian_interior"],
          "PHYSICAL_B UNKNOWN",flush=True)
    return output

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    run(args.output)

if __name__=="__main__":
    main()
