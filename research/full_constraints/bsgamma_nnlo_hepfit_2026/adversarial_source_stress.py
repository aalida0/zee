#!/usr/bin/env python3
"""Stress-test the 2026 published-order Zee B->Xs gamma screening gate.

Three *different schemes/orders* are NEVER combined into a physical rate or a
statistically calibrated BSM uncertainty. This executable asks only the
conditional question: even if each of three known diagnostic differences
were adversarially aligned, does the published-LO-NP source-defined screen
still have positive rate headroom?

Diagnostic absolute stress components:
(1) |SuperIso-v5 NLO source NP shift - Misiak-2026 Eq4 LO NP shift|
(2) |HEPfit source-matched three-loop Wilson C7,C8 insertion into LO Eq4 slope|
(3) |flavio-2.7.1 historical-rate quadratic Wilson C7,C8 term|

These are *NOT independent nuisance sigmas*, include order/scheme mismatch,
and may overlap. The envelope is not a bound on unknown amplitudes; a pass
means only survival under this explicitly enumerated stress scenario.
"""
from __future__ import annotations

import argparse,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
INPUT=ROOT/"research/full_constraints/bsgamma_nnlo_hepfit_2026/16_scalar_three_loop_source_matched_evidence.json"

# Audited original SuperIso source run 43091722057 + original independent
# flavio ±C7/C8 curvature run 43089287057, both generated on 2026-11-11.
# Order-scheme ambiguity is intentional: these numbers are NEVER added
# as formal perturbative corrections or probabilistic nuisance errors.
DIAGNOSTIC_LEGACY={
    2264: (3.157461513254861e-05, 1.3571821916076739e-06),
    2616: (2.211693579678547e-05, 7.1803055114600658e-07),
    3693: (2.837260819755496e-05, 1.126908802654336e-06),
    4611: (2.4238260256673953e-05, 8.5084684450770611e-07),
    8294: (2.571568831371201e-05, 9.4252494259127297e-07),
    8850: (2.7111694803665142e-05, 1.0309708132845885e-06),
    9454: (3.1075853460117069e-05, 1.3361774234892597e-06),
    11016: (1.6304436191781342e-05, 4.1455338753670868e-07),
    13345: (2.7970034345917323e-05, 1.1010928863062195e-06),
    14074: (1.5341871718682956e-05, 3.697178907511949e-07),
    14187: (2.4998054281631904e-05, 8.966792936927607e-07),
    14555: (2.827308364858794e-05, 1.1328045864102349e-06),
    14984: (2.330866647042571e-05, 7.886865631822758e-07),
    15591: (2.8085183020264051e-05, 1.0999309591115149e-06),
    15673: (1.9407607011497259e-05, 5.6562979197752631e-07),
    16385: (2.4896627706411534e-05, 8.9201572158994135e-07),
}
LO2026_SM=3.54e-4

def run(out:Path):
    if out.exists(): raise FileExistsError("No overwrites of physics receipts")
    data=json.loads(INPUT.read_text())
    if (data["n_scalar_16"]!=16 or
        data["source_git_blob"]!="8029be52c3e2f83490dfe3199f80e5db484dd23b"):
        raise ArithmeticError("Original HEPfit three-loop source provenance changed")
    if set(DIAGNOSTIC_LEGACY)!={int(c["id"]) for c in data["cases"]}:
        raise ArithmeticError("Prior-source scalar set changed")
    cases=[]
    for z in data["cases"]:
        id=z["id"]
        si,fl=DIAGNOSTIC_LEGACY[id]
        shift=z["LO_NP_Misiak2026_rate"]-LO2026_SM
        if shift<=0:
            raise ArithmeticError("Type-II constructive NP shift changed")
        delta1=abs(si-shift)
        delta2=abs(z["UNMATCHED_diagnostic_2026_LO_rate_shift_if_inserting_NNLO_dipoles"])
        delta3=abs(fl)
        stress=sum((delta1,delta2,delta3))
        margin1=z["positive_headroom_one_sided"]
        margin2=z["positive_headroom_two_sided"]
        row={
            "scalar_id":id,"scalar_sha256":z["scalar_sha256"],
            "LO_NP_shift_published_2026":shift,
            "source_SuperIso_old_scheme_full_vector_NLO_NP_shift":si,
            "old_scheme_flavio_quadratic":fl,
            "absolute_NLO_minus_LO_different_scheme":delta1,
            "absolute_source_three_loop_matching_only_unmatched_rate_probe":delta2,
            "absolute_old_flavio_quadratic":delta3,
            "worst_signed_sum_heuristic_stress":stress,
            "stress_fraction_of_published_LO_NP_shift":stress/shift,
            "published_one_sided_positive_headroom":margin1,
            "published_two_sided_positive_headroom":margin2,
            "one_sided_stress_screen_survives":margin1>stress,
            "two_sided_stress_screen_survives":margin2>stress,
            "one_sided_stress_remaining_margin":margin1-stress,
            "two_sided_stress_remaining_margin":margin2-stress,
            "uncalibrated_theory_sigma":None,
            "physical_2026_NNLO_B":"UNKNOWN",
            "global_acceptance":None,
        }
        cases.append(row)
        print("B_DIAGNOSTIC_STRESS",id,"SUM",stress,
              "ONE_SIDED_SURVIVES",row["one_sided_stress_screen_survives"],
              "TWO_SIDED_SURVIVES",row["two_sided_stress_screen_survives"],
              "FULL_PHYSICAL_UNKNOWN",flush=True)
    original={x["scalar_id"]:x for x in cases}
    if not original[15673]["one_sided_stress_screen_survives"]:
        raise ArithmeticError("Primary 15673 no longer survives declared stress scenario")
    if original[15591]["one_sided_stress_screen_survives"]:
        raise ArithmeticError("15591 was outside one-sided published leading screen")
    output={
        "schema":"zee-2026-three-independent-bsgamma-source-differences-adversarial-stress-only-v1",
        "original_superiso_source_run":"https://github.com/aalida0/zee/actions/runs/43091722057",
        "original_flavio_quadratic_run":"https://github.com/aalida0/zee/actions/runs/43089287057",
        "2026_source":"arXiv:2608.29863v1 Eq4",
        "status":"HEURISTIC_STRESS_TEST_NOT_MODEL_NP_THEORY_BOUND",
        "n_original_scalar_spectra":16,
        "n_one_sided_stress_surviving":sum(x["one_sided_stress_screen_survives"] for x in cases),
        "n_two_sided_stress_surviving":sum(x["two_sided_stress_screen_survives"] for x in cases),
        "source_Hepfit_matching_only_not_updated_rate":True,
        "historical_backend_order_differences_not_additive_physical_corrections":True,
        "no_model_NP_uncertainty_inferred":True,
        "physical_2026_NNLO_B":"UNKNOWN",
        "global_acceptance":None,
        "cases":cases
    }
    out.write_text(json.dumps(output,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("B_DIAGNOSTIC_STRESS_DONE",len(cases),"1S",output["n_one_sided_stress_surviving"],
          "2S",output["n_two_sided_stress_surviving"],flush=True)
    return output

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",type=Path,required=True)
    z=a.parse_args()
    run(z.output)

if __name__=="__main__":main()
