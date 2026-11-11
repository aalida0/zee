#!/usr/bin/env python3
"""Publication-scoped 2026 Misiak leading-NP B->Xs gamma constraint for Zee Type II.

This is a completed, source-defined LO-new-physics constraint, not a complete
new-physics NNLO rate. The source itself (2608.29863v1 Eq4) recommends LO
NP C7/C8 for generic models near the SM; the rate includes its updated
NNLO SM central and quoted uncertainty. We explicitly compare 2017
confidence-belt conventions and report every required theoretical
remainder margin, without silently inventing an NP sigma or 'full pass'.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from scripts.zee_module5_bmu_nlo import matching
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

ROOT=Path(__file__).resolve().parents[3]
MATCHING=ROOT/"module14/conditional_scan/matching_card.json"
SM=3.54e-4
SM_SIGMA=0.14e-4
EXP=3.49e-4
EXP_SIGMA=0.19e-4
C7_SLOPE=-8.51e-4
C8_SLOPE=-2.16e-4
Z_ONE=1.6448536269514722
Z_TWO=1.959963984540054


def source_rate(row,card):
    p=row["input_card"]["physical"]
    m1,m2=float(p["mH1"]),float(p["mH2"])
    gamma=float(p["gamma"])
    tb=math.tan(p["beta"])
    mt=card["mt_MSbar_GeV"]
    mu=card["matching_scale_GeV"]
    if mu!=160:raise ValueError("2026 source matching scale changed")
    weights=(math.cos(gamma)**2,math.sin(gamma)**2)
    one=[matching(m,tb,mt,mu=mu) for m in (m1,m2)]
    c7=math.fsum(w*z["C7_LO"] for w,z in zip(weights,one))
    c8=math.fsum(w*z["C8_LO"] for w,z in zip(weights,one))
    if c7>=0 or c8>=0:
        raise ValueError("Unexpected Type-II Zee sign or quark matching convention")
    pred=SM+C7_SLOPE*c7+C8_SLOPE*c8
    return pred,c7,c8,weights,one


def classify(row,card):
    pred,c7,c8,weights,one=source_rate(row,card)
    sigma=math.hypot(SM_SIGMA,EXP_SIGMA)
    upper_one=EXP+Z_ONE*sigma
    upper_two=EXP+Z_TWO*sigma
    lower_two=EXP-Z_TWO*sigma
    np_shift=pred-SM
    if np_shift<=0:raise ArithmeticError("The original Type-II relative sign reversed")
    one_sided=pred<=upper_one
    two_sided=lower_two<=pred<=upper_two
    if row["gates"]["vacuum"]["assessment"]!="PASS":
        raise ArithmeticError("Original scalar no longer source-certified vacuum")
    if row["bsg_nominal_classification"]!="APPROX_COMPATIBLE":
        raise ArithmeticError("Original source B classification changed")
    if not math.isclose(pred,SM+(row["conditional_pull"]*sigma+EXP-SM),rel_tol=2e-10,abs_tol=1e-13):
        raise ArithmeticError("Original 2026 B coefficient matching not reproduced")
    return {
        "scalar_id":row["id"],
        "scalar_sha256":row["scalar_sha256"],
        "tree_scalar_vacuum_certificate":"PASS",
        "charged_eigenmass_GeV":[row["input_card"]["physical"]["mH1"],
                                row["input_card"]["physical"]["mH2"]],
        "tanbeta":math.tan(row["input_card"]["physical"]["beta"]),
        "gamma":row["input_card"]["physical"]["gamma"],
        "charged_doublet_fractions_squared":weights,
        "per_state_ordinary_BMU_LO_C7C8":[
            [r["C7_LO"],r["C8_LO"]] for r in one
        ],
        "two_state_ordinary_DeltaC7":c7,
        "two_state_ordinary_DeltaC8":c8,
        "2026_published_Eq4_rate":pred,
        "leading_NP_rate_shift":np_shift,
        "gaussian_screen_pull":(pred-EXP)/sigma,
        "upper_95_one_sided":upper_one,
        "upper_95_two_sided":upper_two,
        "lower_95_two_sided":lower_two,
        "one_sided_95_LO_NP_screen":one_sided,
        "two_sided_95_LO_NP_screen":two_sided,
        "one_sided_positive_absolute_missing_rate_headroom":upper_one-pred,
        "two_sided_positive_absolute_missing_rate_headroom":upper_two-pred,
        "one_sided_positive_missing_rate_fraction_of_LO_NP":
            (upper_one-pred)/np_shift,
        "two_sided_positive_missing_rate_fraction_of_LO_NP":
            (upper_two-pred)/np_shift,
        "gaussian_covariance_assumption":
            "2026 quoted SM theory sigma and current measurement treated independent; no extra NP covariance",
        "published_order_constraint_status":
            "PASS_2026_SOURCE_DECLARED_LO_NP_TWO_SIDED_95"
            if two_sided else "FAIL_2026_SOURCE_DECLARED_LO_NP_TWO_SIDED_95",
        "one_sided_convention_status":
            "PASS_2026_SOURCE_DECLARED_LO_NP_ONE_SIDED_95"
            if one_sided else "FAIL_2026_SOURCE_DECLARED_LO_NP_ONE_SIDED_95",
        "NP_missing_high_order_absolute_remainder_certified_bound":None,
        "physical_full_model_95_cl_exclusion":None,
        "full_NNLO_model_rate_computed":False,
        "global_acceptance":None,
    }


def run(out:Path):
    if out.exists():raise FileExistsError("No overwrite")
    card=json.loads(MATCHING.read_text())
    pts=sorted(source_points(),key=lambda d:d["id"])
    if len(pts)!=16:raise ArithmeticError("Original 16 source scalar spectra altered")
    rows=[classify(row,card) for row in pts]
    if not all(x["two_sided_95_LO_NP_screen"] for x in rows):
        raise ArithmeticError("Frozen 2026 nominal two-sided source gate changed")
    one_pass=sum(x["one_sided_95_LO_NP_screen"] for x in rows)
    if one_pass!=10:
        raise ArithmeticError("Published-order one-sided reference gate changed")
    byid={x["scalar_id"]:x for x in rows}
    if byid[15591]["one_sided_95_LO_NP_screen"] or not byid[15673]["one_sided_95_LO_NP_screen"]:
        raise ArithmeticError("Original three-benchmark order-95 convention changed")
    result={
        "schema":"zee-2026-published-loNP-bsgamma-explicit-two-sided-and-one-sided-confidence-screen-v1",
        "theory_reference":"Misiak et al arXiv:2608.29863v1 Eq(4), author-approved leading BSM approximation",
        "confidence_interval_reference":"Misiak-Steinhauser arXiv:1702.04571 Section 5, distinct one-sided/two-sided/FC placement",
        "source_2026_SM":SM,"source_2026_SM_sigma":SM_SIGMA,
        "source_PDG_experiment":EXP,"source_experiment_sigma":EXP_SIGMA,
        "combined_independent_gaussian_sigma":math.hypot(SM_SIGMA,EXP_SIGMA),
        "95_one_sided_z":Z_ONE,"95_two_sided_z":Z_TWO,
        "source_matching_scale_GeV":160.,
        "n_original_source_certified_scalar_spectra":len(rows),
        "n_LO_NP_95_one_sided_inside":one_pass,
        "n_LO_NP_95_two_sided_inside":sum(x["two_sided_95_LO_NP_screen"] for x in rows),
        "preferred_B_margin_candidate":15673,
        "source_order_2026_LO_NP_constraint_usable_for_phenomenology":True,
        "full_physical_B_NNLO_uncertainty":None,
        "2026_TypeII_one_state_670GeV_limit_directly_inapplicable_to_two_state_Zee":True,
        "statistical_screen_is_published_approximation_not_author_reproduced_FC":True,
        "scalar_rows":rows,
        "physical_full_95CL":"UNKNOWN",
        "global_acceptance":None,
    }
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("SOURCE_2026_LO_NP_B_GATES",len(rows),"ONE_SIDED",one_pass,
          "TWO_SIDED",result["n_LO_NP_95_two_sided_inside"],flush=True)
    for i in (15591,15673,2264):
        x=byid[i]
        print("PREFERRED_B",i,"RATE",x["2026_published_Eq4_rate"],
              "ONE",x["one_sided_95_LO_NP_screen"],
              "TWO",x["two_sided_95_LO_NP_screen"],
              "POSITIVE_HEADROOM_1S",x["one_sided_positive_absolute_missing_rate_headroom"],
              "POSITIVE_HEADROOM_2S",x["two_sided_positive_absolute_missing_rate_headroom"],
              "FULL_B_UNKNOWN",flush=True)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    run(args.output)

if __name__=="__main__":main()
