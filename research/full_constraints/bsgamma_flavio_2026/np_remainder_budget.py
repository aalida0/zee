#!/usr/bin/env python3
"""Decompose the 2026 B->Xs gamma leading-NP approximation at 16 Zee spectra.

1. Published LO-NP linear rate Misiak et al. 2608.29863v1 Eq.(4).
2. Independent *older scheme* flavio 2.7.1 C7/C8 rate split into odd
   (linear) and even (quadratic) Wilson-coefficient components by ± matching.
3. 2026 confidence-interval headroom for an *unmodeled signed shift*, and
   a predeclared ± relative NP-shift sensitivity. Neither is a theory sigma.
4. Recompute a one-state 2HDM Type-II tanbeta=50 M=670 benchmark at the
   same LO-NP matching to explicitly demonstrate the order mismatch with
   the full 2026 NNLO bound. Do not 'calibrate' a Zee confidence interval by
   equating the two different theoretical prescriptions.

Uncertified sources: NP NLO full C4/evolution, NNLO new-physics matching,
nonperturbative NP covariance, finite ms/up-charm and extra Zee EW loops.
Never emit full-model exclusions or a made-up NP uncertainty.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import flavio
from flavio.physics.running import running
from scripts.zee_module5_bmu_nlo import matching
from research.full_constraints.bsgamma_flavio_2026.bridge_3cards import wilson_rate
from research.full_constraints.bsgamma_flavio_2026.published_eq4_triangulation import (
    assess_point, MATCHING_CARD, PUBLISHED_SM, EXP, EXP_SIGMA,
    PUBLISHED_SM_SIGMA, COEF_C7, COEF_C8, Z95
)
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

PROBE_FRACTIONS=(0., 0.05, 0.1, 0.2, 0.3, 0.5, 1.)
SOURCE_2HDM_MASS_GEV=670.
SOURCE_2HDM_TANBETA=50.
SOURCE_2HDM_MASS_BOUND_SIGMA="UNSPECIFIED_NNLO_MODEL_COMPARISON__NOT_LO_NP_EQ4"
OBS="BR(B->Xsgamma)"


def norm_BR(c7,c8):
    return PUBLISHED_SM+COEF_C7*c7+COEF_C8*c8


def split_flavio(rate_function,c7,c8):
    z=rate_function(0.,0.)
    plus=rate_function(c7,c8)
    minus=rate_function(-c7,-c8)
    odd=0.5*(plus-minus)
    even=0.5*(plus+minus)-z
    plus2=rate_function(2*c7,2*c8)
    minus2=rate_function(-2*c7,-2*c8)
    odd2=(plus2-minus2)/2
    even2=(plus2+minus2)/2-z
    if not math.isclose(odd2,2*odd,rel_tol=1e-9,abs_tol=1e-13):
        raise ArithmeticError("Independent WET amplitude fails linearity under doubling")
    if not math.isclose(even2,4*even,rel_tol=1e-8,abs_tol=1e-13):
        raise ArithmeticError("Independent WET amplitude fails quadratic scaling")
    return dict(
        old_backend_SM=z,
        old_backend_full_plus=plus,
        old_backend_full_minus=minus,
        NP_linear_odd=odd,
        NP_quadratic_even=even,
        NP_quadratic_relative_to_linear=even/odd if odd!=0 else None,
        NP_quadratic_ratio_to_published_linear=even/(COEF_C7*c7+COEF_C8*c8),
        NP_quadratic_has_been_transferred_to_2026=False,
        doubled_odd_residual=odd2-2*odd,
        doubled_even_residual=even2-4*even,
        theoretical_scope="Exact Wilson quadratic in flavio's older inclusive-rate prescription; not an order-matched 2026 NNLO NP correction or a rigorous remainder bound",
    )


def one_state_reference(mt):
    def coeff(mass):
        return matching(float(mass),SOURCE_2HDM_TANBETA,mt,mu=160.)
    ref=coeff(SOURCE_2HDM_MASS_GEV)
    predicted=norm_BR(ref["C7_LO"],ref["C8_LO"])
    denom=math.hypot(PUBLISHED_SM_SIGMA,EXP_SIGMA)
    z=(predicted-EXP)/denom
    # One-sided and two-sided Gaussian *LO NP Eq4* roots, neither
    # substitutes the published full two-Higgs-doublet NNLO likelihood.
    roots={}
    for tag,criterion in (("one_sided_1p645",1.6448536269514722),("two_sided_1p960",Z95)):
        lo,hi=350.,1500.
        def zp(m):
            x=coeff(m)
            return (norm_BR(x["C7_LO"],x["C8_LO"])-EXP)/denom
        if not (zp(lo)>criterion>zp(hi)):
            raise ArithmeticError("Unexpected one-state LO NP 95CL bracket")
        for _ in range(55):
            mid=(lo+hi)/2
            if zp(mid)>criterion:lo=mid
            else:hi=mid
        roots[tag]=0.5*(lo+hi)
    return dict(
        source_ref="2608.29863v1 page4, full 2HDMII NNLO M_H+>670 at 95CL",
        mHplus_GeV=SOURCE_2HDM_MASS_GEV,
        tanbeta=SOURCE_2HDM_TANBETA,
        matched_coefficients=ref,
        LO_NP_Eq4_predicted_BR=predicted,
        LO_NP_Eq4_gaussian_pull=z,
        LO_NP_Eq4_roots_GeV=roots,
        published_NNLO_TypeII_mass_bound_GeV=670.,
        source_bound_uses_same_approximate_likelihood=False,
        allowed_to_transfer_published_bound_directly_to_Zee=False,
        conversion_to_theory_sigma=None,
    )


def run(path:Path):
    if path.exists():raise FileExistsError("Refuse overwrite of physics evidence")
    if flavio.__version__!="2.7.1":raise ValueError("Unpinned flavio")
    card=json.loads(MATCHING_CARD.read_text())
    if card["matching_scale_GeV"]!=160:raise ValueError("Unexpected matching scale")
    pp=flavio.default_parameters.get_central_all()
    alpha_s=float(running.get_alpha(pp,160)["alpha_s"])
    sm=float(flavio.sm_prediction(OBS))
    def rate(c7,c8):return wilson_rate(c7,c8,160.)
    points=source_points()
    if len(points)!=16:raise ValueError("Original scalar count changed")
    denom=math.hypot(PUBLISHED_SM_SIGMA,EXP_SIGMA)
    upper=EXP+Z95*denom
    lower=EXP-Z95*denom
    roots=one_state_reference(card["mt_MSbar_GeV"])
    rows=[]
    for p in sorted(points,key=lambda d:d["id"]):
        prior=assess_point(p,card,sm,alpha_s)
        c7=prior["source_B_LO_C7"]
        c8=prior["source_B_LO_C8"]
        split=split_flavio(rate,c7,c8)
        shift=prior["published_2026_Eq4_prediction"]-PUBLISHED_SM
        headroom=upper-prior["published_2026_Eq4_prediction"]
        if shift <= 0 or headroom<=0:
            raise ArithmeticError("Source B diagnostic or upper-bound assumptions changed")
        scenarios={}
        for fraction in PROBE_FRACTIONS:
            # bounded signed remainder relative to *positive* published LO-NP shift
            low=prior["published_2026_Eq4_prediction"]-fraction*shift
            high=prior["published_2026_Eq4_prediction"]+fraction*shift
            scenarios[f"{fraction:.3f}"]={
                "relative_shift_magnitude":fraction,
                "signed_rate_min":low,"signed_rate_max":high,
                "both_signs_inside_95_gaussian_diagnostic":
                    (lower<=low<=upper and lower<=high<=upper),
                "higher_order_remainder_has_known_bound":False
            }
        row=dict(prior)
        row.update({
            "old_scheme_flavio_odd_even_signed_split":split,
            "2026_gaussian_upper_bound_assuming_NP_sigma_zero":upper,
            "2026_gaussian_lower_bound_assuming_NP_sigma_zero":lower,
            "2026_positive_missing_branching_shift_headroom":headroom,
            "2026_relative_positive_shift_headroom_to_LO_NP":headroom/shift,
            "2026_gaussian_reference_combined_SM_exp_sigma":denom,
            "bound_assumes_extra_NP_perturbative_sigma_zero":True,
            "reference_signed_remainder_scenarios":scenarios,
            "NP_remainder_certified_bound":None,
            "NP_theory_sigma":None,
            "published_full_2026_NNLO_rate_executed":False,
            "physical_B":"UNKNOWN",
            "global_acceptance":None,
        })
        rows.append(row)
        print("2026_B_NP_REMAINDER",p["id"],
              "PRED",row["published_2026_Eq4_prediction"],
              "HEADROOM",headroom,
              "HEADROOM_RELATIVE_NP",row["2026_relative_positive_shift_headroom_to_LO_NP"],
              "FLAVIO_QUADRATIC_OLD",split["NP_quadratic_even"],
              "FLAVIO_QUADRATIC_RELATIVE",split["NP_quadratic_relative_to_linear"],
              "FULL_B_UNKNOWN",flush=True)
    output={
        "schema":"zee-2026-published-Bsgamma-LONP-one-state-control-flavio-quadratic-decomposition-v1",
        "flavio_version":flavio.__version__,
        "source_2026":"arXiv:2608.29863v1 Eq.(4), E_gamma>1.6 GeV, mu0=160 GeV",
        "published_SM":PUBLISHED_SM,"published_SM_sigma":PUBLISHED_SM_SIGMA,
        "experimental_central":EXP,"experimental_sigma":EXP_SIGMA,
        "assumed_independent_gaussian_sigma":denom,
        "two_sided_gaussian_95_upper":upper,
        "two_sided_gaussian_95_lower":lower,
        "one_state_670_full_NNLO_vs_LO_NP_control":roots,
        "n_original_certified_scalar_points":len(rows),
        "uncertified_NP_remainder_status":"NO_RIGOROUS_BOUND_OR_COVARIANCE",
        "n_spectra_robust_to_plus_minus_10_percent_of_LO_NP":
            sum(row["reference_signed_remainder_scenarios"]["0.100"]["both_signs_inside_95_gaussian_diagnostic"]
                for row in rows),
        "n_spectra_robust_to_plus_minus_20_percent_of_LO_NP":
            sum(row["reference_signed_remainder_scenarios"]["0.200"]["both_signs_inside_95_gaussian_diagnostic"]
                for row in rows),
        "n_spectra_robust_to_plus_minus_30_percent_of_LO_NP":
            sum(row["reference_signed_remainder_scenarios"]["0.300"]["both_signs_inside_95_gaussian_diagnostic"]
                for row in rows),
        "spectra":rows,
        "full_B_uncertainty_completed":False,
        "physical_B":"UNKNOWN","global_acceptance":None,
        "no_double_counting":"Legacy flavio quadratic term is reported separately and NEVER added to the Misiak 2026 NNLO prediction as a certified higher-order remainder.",
    }
    path.write_text(json.dumps(output,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("2026_B_REMAINDER_STUDY_COMPLETE",len(rows),
          "FULL_B_UNKNOWN",flush=True)
    return output


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    run(args.output)


if __name__=="__main__":main()
