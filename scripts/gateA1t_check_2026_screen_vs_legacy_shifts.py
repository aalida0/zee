#!/usr/bin/env python3
"""Gate A1T: cross-check modern 2026 linearized NP shifts vs legacy v5 BR.

Reads USER-EXECUTED A1R and A1S JSON files. This diagnostic does NOT
equate the 2026 Eq.4 linearized LO NP correction with a higher-order
legacy SuperIso NP correction. It quantifies their difference and
keeps all 95% CL/allowed/excluded claims unset. No new AF physics run.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

MASSES=(300,700,1000,2000)
SM2026=3.54
EXP2026=3.49
SIGMA2026=0.14
SIGMAEXP=0.19

def finite(v):
    x=float(v)
    if not math.isfinite(x):
        raise ValueError("Nonfinite original BR/matching value")
    return x

def assess(legacy,modern):
    if legacy.get("status")!=(
        "GATE_A1R_SINGLE_TYPEII_OBSERVABLE_BR_PILOT_"
        "AWAITING_INDEPENDENT_ERROR_BUDGET"
    ):
        raise ValueError("Wrong Gate A1R status")
    if modern.get("status")!=(
        "GATE_A1S_2026_MODERN_EQ4_LO_LINEARIZED_ZEE_SCREEN_NOT_EXCLUSION"
    ):
        raise ValueError("Wrong Gate A1S status")
    eq4=modern.get("Eq4_coefficients",{})
    if not (finite(eq4.get("matching_scale_GeV"))==160. and
            finite(eq4.get("coefficient_delta_C7"))==-8.51 and
            finite(eq4.get("coefficient_delta_C8"))==-2.16 and
            finite(eq4.get("constant"))==SM2026):
        raise ValueError("Modern Eq4 scale/coefficients changed")
    if finite(modern["SM_2026"]["central_times_1e4"])!=SM2026:
        raise ValueError("Modern SM reference was changed")
    if finite(modern["experimental_PDG_2026"]["central_times_1e4"])!=EXP2026:
        raise ValueError("2026 experimental reference changed")
    legacy_sm=finite(legacy["SM_model_BR"])*1e4
    if not 2.5<legacy_sm<4.5:
        raise ValueError("Wrong legacy SM reference")
    new_rows=modern["source_pinned_LO_coefficients"]
    old_rows=legacy["TypeII_control_points"]
    pairs=[]
    for m in MASSES:
        key=str(float(m))
        # A1S saves keys from Python floats ("300.0", etc.)
        if key not in new_rows:
            raise ValueError(f"Missing A1S mass {m} GeV")
        new=new_rows[key]
        vendor=old_rows.get(f"TypeII{m}")
        if not isinstance(vendor,dict):
            raise ValueError(f"Missing A1R mass {m} GeV")
        if abs(finite(new["mass_GeV"])-m)>1e-9:
            raise ValueError("Wrong A1S mass")
        if abs(finite(vendor["mH_GeV"])-m)>1e-9:
            raise ValueError("Wrong A1R mass")
        if not math.isclose(finite(vendor["tanbeta"]),
                            finite(new["tanbeta"]),rel_tol=1e-12,
                            abs_tol=1e-12):
            raise ValueError("A1R and A1S Yukawa tanbeta differ")
        if finite(new["matching_scale_GeV"])!=160.:
            raise ValueError("A1S masses are not evaluated at 160 GeV")
        delta7=finite(new["delta_C7_LO"])
        delta8=finite(new["delta_C8_LO"])
        new_shift=(-8.51*delta7-2.16*delta8)
        old_shift=finite(vendor["BR_B_to_Xs_gamma"])*1e4-legacy_sm
        if old_shift<=0 or new_shift<=0:
            raise ValueError("Unexpected charged-scalar effect sign")
        pairs.append({
            "mass_GeV":m,
            "A1R_legacy_BR_shift_times_1e4":old_shift,
            "A1S_2026_linearized_LO_BR_shift_times_1e4":new_shift,
            "linearized_minus_legacy_shift_times_1e4":new_shift-old_shift,
            "fractional_linearized_vs_legacy_shift_difference":
                new_shift/old_shift-1.,
            "schemes_and_order_not_matched":True,
            "not_theory_error_estimate":True,
        })
    z=modern["selected_Zee_scalar_sector_benchmark"]
    w1=finite(z["w_light_cos2"])
    w2=finite(z["w_heavy_sin2"])
    if not math.isclose(w1+w2,1.,abs_tol=1e-13):
        raise ValueError("Zee charged-Higgs mixing weights do not close")
    mz1=finite(z["mH1_GeV"])
    mz2=finite(z["mH2_GeV"])
    if mz1 not in [float(k) for k in MASSES] or mz2 not in [float(k) for k in MASSES]:
        raise ValueError("Zee mass points must have matching A1R controls")
    if mz1>=mz2:
        raise ValueError("Ordered two-state charged masses required")
    bymass={item["mass_GeV"]:item for item in pairs}
    vendor_linear_weighted_shift=(
        w1*bymass[int(mz1)]["A1R_legacy_BR_shift_times_1e4"]+
        w2*bymass[int(mz2)]["A1R_legacy_BR_shift_times_1e4"]
    )
    # This is NOT the legacy two-state BR: that requires propagating the
    # TWO combined Wilson arrays through the full observable including
    # interference/quadratic NP terms.
    modern_shift=finite(z["linearized_shift_times_1e4"])
    ref_modern=sum(w*bymass[int(m)]["A1S_2026_linearized_LO_BR_shift_times_1e4"]
                   for w,m in ((w1,mz1),(w2,mz2)))
    if abs(ref_modern-modern_shift)>1e-8:
        raise ValueError("A1S Zee mixing does not close in LO Eq4")
    eq4_prediction=SM2026+modern_shift
    if abs(eq4_prediction-finite(z["linearized_predicted_central_times_1e4"]))>1e-9:
        raise ValueError("A1S Eq4 Zee prediction changed")
    naive_sigma=math.hypot(SIGMA2026,SIGMAEXP)
    return {
        "status":"GATE_A1T_LO_VS_LEGACY_NP_SHIFT_DIAGNOSTIC_NOT_PRECISION_OR_EXCLUSION",
        "references":{"2026_arxiv":"2608.29863","2026_mu0_GeV":160.,
                      "SM2026_times_1e4":SM2026,
                      "experimental2026_times_1e4":EXP2026,
                      "legacy_SuperIso_v5_SM_times_1e4":legacy_sm},
        "single_state_diagnostics":pairs,
        "Zee_screen":{
            "mH1_GeV":mz1,"mH2_GeV":mz2,"w_light":w1,"w_heavy":w2,
            "2026_Eq4_LO_shift_times_1e4":modern_shift,
            "2026_Eq4_LO_BR_times_1e4":eq4_prediction,
            "legacy_single_state_BR_shift_weighted_diagnostic_times_1e4":
                vendor_linear_weighted_shift,
            "linearized_2026_minus_weighted_legacy_shift_times_1e4":
                modern_shift-vendor_linear_weighted_shift,
            "illustrative_naive_uncorrelated_pull_sigma":
                (eq4_prediction-EXP2026)/naive_sigma,
            "pull_not_a_95CL_exclusion_significance":True,
            "weighted_legacy_shift_NOT_a_physical_two_state_BR":True,
        },
        "A1R_actual_full_single_state_BR_measured":True,
        "A1S_2026_LO_Eq4_two_state_screen_measured":True,
        "mixed_state_full_2026_NNLO_BR_measured":False,
        "model_specific_theory_uncertainty_quantified":False,
        "experimental_likelihood_validated":False,
        "Zee_allowed":None,
        "Zee_excluded":None,
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-A1R",required=True,type=Path)
    parser.add_argument("--modern-A1S",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    data=assess(json.loads(args.legacy_A1R.read_text()),
                json.loads(args.modern_A1S.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+"\n")
    print("STATUS",data["status"])
    for row in data["single_state_diagnostics"]:
        print("mH",row["mass_GeV"],
              "legacy_NP_shift_1e4",
              f"{row['A1R_legacy_BR_shift_times_1e4']:.10g}",
              "2026_Eq4_NP_shift_1e4",
              f"{row['A1S_2026_linearized_LO_BR_shift_times_1e4']:.10g}",
              "relative_shift_difference_percent",
              f"{100.*row['fractional_linearized_vs_legacy_shift_difference']:.5g}")
    zee=data["Zee_screen"]
    print("ZEE_NOMINAL_NAIVE_PULL_NOT_EXCLUSION",
          f"{zee['illustrative_naive_uncorrelated_pull_sigma']:.9g}")
    print("2026_TWO_STATE_NNLO_BR_VALIDATED",False)
    print("ZEE_EXCLUSION_CALCULATED",False)
    print("Wrote",args.output)

if __name__=="__main__":
    main()
