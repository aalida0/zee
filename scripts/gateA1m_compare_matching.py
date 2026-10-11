#!/usr/bin/env python3
"""Compare full matching vectors from unmodified vs isolated SuperIso v5.

This is a diagnostic perturbative-order comparison only. No physical
B->Xs gamma calculation or model exclusion is supported here.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

from gateA1l_check_matching_pilot import parse

def close(a,b):
    return math.isclose(a,b,rel_tol=5e-10,abs_tol=5e-10)

def compare(native, patched, provenance):
    a,b=parse(native),parse(patched)
    if not (close(a["inputs"]["w1"],b["inputs"]["w1"]) and
            close(a["inputs"]["w2"],b["inputs"]["w2"]) and
            close(a["inputs"]["muW"],b["inputs"]["muW"])):
        raise ValueError("Mismatched mass/mixing or matching scale")
    if provenance["changed_statement_count"] != 4:
        raise ValueError("Expected exactly four isolated source line changes")
    if set(provenance["changed_symbols"]) != {"C7H_1","C8H_1","C9H_1","C10H_1"}:
        raise ValueError("Unexpected altered source symbols")
    max_unaffected_abs_difference=0.
    changed={}
    for key in sorted(a["entries"]):
        order,i=key
        orig=a["entries"][key]
        new=b["entries"][key]
        # tuple (SM,DeltaH1,DeltaH2,Zee)
        for j in range(4):
            if j==0 or order != 1 or i not in (7,8,9,10):
                delta=abs(orig[j]-new[j])
                max_unaffected_abs_difference=max(max_unaffected_abs_difference,delta)
                if not close(orig[j],new[j]):
                    raise ValueError(f"Changed unaffected coefficient {key}, column {j}: {orig[j]}->{new[j]}")
        if order==1 and i in (7,8,9,10):
            changed[f"C{i}"]={
                "native_single_light":orig[1], "native_single_heavy":orig[2],
                "patched_single_light":new[1],"patched_single_heavy":new[2],
                "native_zee":orig[3], "patched_zee":new[3]
            }
    # The vendor compiled NLO charged C7 and C8 must vanish at both masses.
    for i in (7,8):
        row=changed[f"C{i}"]
        if not close(row["native_single_light"],0.) or not close(row["native_single_heavy"],0.):
            raise ValueError(f"Vendor C{i} NLO is not clipped to zero; source behavior changed")
        for mode in ("light","heavy"):
            if not abs(row[f"patched_single_{mode}"])>1e-8:
                raise ValueError(f"Patched C{i} NLO {mode} is zero: check patch/build")
    # Validate interpolation also for repaired NLO values.
    w1,w2=b["inputs"]["w1"],b["inputs"]["w2"]
    for i in (7,8,9,10):
        sm,light,heavy,zee=b["entries"][1,i]
        if not close(zee,sm+w1*light+w2*heavy):
            raise ValueError(f"Patched NLO C{i} superposition failed")
    return {
        "status":"ISOLATED_NLO_C7_C8_RESTORED_DIAGNOSTIC_NOT_PHYSICAL_BR",
        "scope":"Direct match-point comparison; vendor library unmodified; no RGE or BR",
        "max_unchanged_entry_abs_difference":max_unaffected_abs_difference,
        "nlo_charged_coefficient_changes":changed,
        "matched_perturbative_orders":"LO/NLO/NNLO C1..C10",
        "full_2HDM_typeII_BR_control_passed":False,
        "Zee_physical_B_to_Xs_gamma_evaluated":False,
        "Zee_benchmark_accepted_or_excluded":False,
        "remaining_validation":[
            "Verify NLO Type-II coefficients against independent formulas",
            "Investigate NNLO basis and mass/renormalization conventions",
            "Validate native vs isolated SM and Type-II branching-ratio controls",
            "Audit primed matching and run complete RG evolution and inclusive BR",
            "Systematic muW/mub scale and parameter/theory uncertainties"
        ]
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--patched",type=Path,required=True)
    p.add_argument("--provenance",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    r=compare(args.native,args.patched,json.loads(args.provenance.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2)+"\n")
    print("Wrote",args.output)
    for i in (7,8):
        print("NLO",f"C{i}",r["nlo_charged_coefficient_changes"][f"C{i}"])
    print("STATUS:",r["status"])
if __name__=="__main__":
    main()
