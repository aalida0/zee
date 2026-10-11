#!/usr/bin/env python3
"""Gate A1O: SM + pure Type-II closure for isolated internal C0w correction.

The A1O patched build is tested against the **same** A1M corrected-NLO
build but without the hidden matching override. This is a consistency
gate only; matching to external NNLO Type-II theory and uncertainty
propagation remain outstanding.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from gateA1n_check_br_candidate import NAMES,parse_output,official_sm

FIXED_MODES=("SM","TYPEII_300","TYPEII_700","TYPEII_1000",
             "TYPEII_2000","ENDPOINT_H1","ENDPOINT_H2")
ALL_ZEE=("ZEE_300_700","ZEE_SAME_WC_ALT_MASS_700",
         "ZEE_REPEAT_MASS_300","ZEE_REPEAT_MASS_700")

def compare(old,patched,sm_reference):
    baseline=parse_output(old)
    bridged=parse_output(patched)
    max_unchanged=0.0
    max_new_zee_mass_difference=0.0
    max_old_zee_mass_difference=0.0
    per_scale=[]
    for scale in range(5):
        for mode in FIXED_MODES:
            value_orig=baseline[scale,mode]["br"]
            value_new=bridged[scale,mode]["br"]
            difference=abs(value_orig-value_new)
            max_unchanged=max(max_unchanged,difference)
            if difference>2e-12:
                raise ValueError(
                    f"Hidden C0w bridge changed single-state or SM rate "
                    f"at scale={scale} mode={mode}: "
                    f"{value_orig} vs {value_new}")
            for op in ("C7prime_re","C7prime_im","C8prime_re",
                       "C8prime_im","cpmax"):
                if abs(baseline[scale,mode][op]-bridged[scale,mode][op])>2e-12:
                    raise ValueError(f"Primed single-state coefficient changed for {mode}")
        for version,rows in (("a1m",baseline),("a1o",bridged)):
            for one,repeat in (("ZEE_300_700","ZEE_REPEAT_MASS_300"),
                               ("ZEE_SAME_WC_ALT_MASS_700","ZEE_REPEAT_MASS_700")):
                if abs(rows[scale,one]["br"]-rows[scale,repeat]["br"])>2e-12:
                    raise ValueError(f"Same-mass replay failure {version} {one}")

        zee=bridged[scale,"ZEE_300_700"]["br"]
        alt=bridged[scale,"ZEE_SAME_WC_ALT_MASS_700"]["br"]
        old_zee=baseline[scale,"ZEE_300_700"]["br"]
        old_alt=baseline[scale,"ZEE_SAME_WC_ALT_MASS_700"]["br"]
        max_new_zee_mass_difference=max(max_new_zee_mass_difference,abs(zee-alt))
        max_old_zee_mass_difference=max(max_old_zee_mass_difference,abs(old_zee-old_alt))
        if abs(zee-alt)>2e-12:
            raise ValueError(
                f"Zee BR still depends on arbitrary mass_H after high-scale "
                f"matching bridge: {zee} vs {alt}, scale={scale}")
        for op in ("C7prime_re","C7prime_im","C8prime_re","C8prime_im","cpmax"):
            if abs(bridged[scale,"ZEE_300_700"][op]-
                   bridged[scale,"ZEE_SAME_WC_ALT_MASS_700"][op])>2e-12:
                raise ValueError(f"Zee primed {op} varies by residual mass_H")
        for mode in FIXED_MODES+ALL_ZEE:
            # Primed coefficient contents must stay invariant across
            # the A1O bsgamma-only extension.
            for op in ("C7prime_re","C7prime_im","C8prime_re","C8prime_im","cpmax"):
                if abs(baseline[scale,mode][op]-bridged[scale,mode][op])>2e-12:
                    raise ValueError(f"Unrelated primed WCs changed for {mode}")

        per_scale.append({
            "scale_index":scale,
            "a1m_single_mass300_candidate":old_zee,
            "a1m_single_mass700_candidate":old_alt,
            "a1o_zee_br_same_for_both_mass_contexts":zee,
            "residual_mass_spread_before":old_zee-old_alt,
            "residual_mass_spread_after":zee-alt,
        })

    if not max_old_zee_mass_difference>1e-8:
        raise ValueError("Control A1M doesn't reproduce original known mass-context effect")
    expected_sm=official_sm(sm_reference)
    if abs(bridged[0,"SM"]["br"]-expected_sm)>1.5e-7:
        raise ValueError("A1O SM baseline does not match official SuperIso")
    for variant,rs in (("a1m",baseline),("a1o",bridged)):
        for scale in range(5):
            for state,end in (("TYPEII_300","ENDPOINT_H1"),
                              ("TYPEII_700","ENDPOINT_H2")):
                if abs(rs[scale,state]["br"]-rs[scale,end]["br"])>2e-12:
                    raise ValueError(f"Type-II endpoint mismatch {variant}/{state}/{scale}")

    return {
        "status":"GATE_A1O_HIDDEN_SINGLE_STATE_REMATCHING_FIXED_CANDIDATE_ONLY",
        "scope":"Isolated SuperIso v5 with A1M NLO diagnostic and C0w[7,8] "
                "internal BR correction, common high-scale Zee matching",
        "nominal":per_scale[0],
        "scale_tests":per_scale,
        "max_SM_TypeII_absolute_rate_change":max_unchanged,
        "max_zee_BR_arbitrary_mass_spread_after":max_new_zee_mass_difference,
        "original_mass_dependence_reproduced":True,
        "SM_official_reference":expected_sm,
        "independent_NLO_NNLO_TypeII_validation":False,
        "full_theory_error_and_experimental_likelihood":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
        "allowed_physics_claim":"Controlled matching-to-BR software consistency; "
                                "not a defensible physical Zee exclusion."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--a1m",type=Path,required=True)
    p.add_argument("--a1o",type=Path,required=True)
    p.add_argument("--official-sm",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        result=compare(args.a1m,args.a1o,args.official_sm)
        code=0
    except ValueError as exc:
        result={
            "status":"GATE_A1O_BLOCKED_VALIDATION_FAILURE",
            "reason":str(exc),
            "Zee_benchmark_allowed":None,
            "Zee_benchmark_excluded":None,
        }
        code=1
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print("Wrote",args.output)
    print("STATUS:",result["status"])
    if "nominal" in result:
        print("nominal:",result["nominal"])
        print("max single state BR change:",result["max_SM_TypeII_absolute_rate_change"])
    if code:
        print("REASON:",result["reason"])
    raise SystemExit(code)

if __name__=="__main__":
    main()
