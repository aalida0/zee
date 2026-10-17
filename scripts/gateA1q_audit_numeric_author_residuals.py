#!/usr/bin/env python3
"""Gate A1Q: evaluate numerical residual closure against original c2HDM.m.

Reads the prior ORIGINAL Mathematica comparison JSON (48 rows).
Reconstructs each SuperIso / HEPfit standard-effective NNLO
dipole residual from the *direct* original dipole residual plus
the weighted C3-C6 differences. This validates the numerical
bookkeeping without changing any Wilson coefficient.

NO full NNLO matching/physical BR/Zee exclusion is claimed.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

from gateA1p_audit_effective_operator_basis import Y,Z
from gateA1q_inspect_original_mathematica import PINNED_KIT_SHA256

MASSES=(300,700,1000,2000)

def close_numeric_comparison(data):
    if data.get("original_author_source_sha256")!=PINNED_KIT_SHA256:
        raise ValueError("Original-author checksum is not the KIT-pinned c2HDM.m")
    rows=data.get("comparison_rows")
    if not isinstance(rows,list) or len(rows)!=48:
        raise ValueError("Require 48 independent Mathematica coefficient rows")
    expected={(m,k,op)
              for m in MASSES for k,ops in
              {0:(7,8),1:(7,8),2:(3,4,5,6,7,8),3:(7,8)}.items()
              for op in ops}
    ref={}
    for row in rows:
        key=(int(row["mass_GeV"]),int(row["author_order"]),
             int(row["operator"].removeprefix("C")))
        if key in ref:
            raise ValueError("Duplicate original-source coefficient row")
        ref[key]=row
        for name in ("original_author","SuperIso_in_author_basis",
                     "HEPfit_in_author_basis"):
            if not math.isfinite(float(row[name])):
                raise ValueError(f"Nonfinite comparison entry {key}:{name}")
    if set(ref)!=expected:
        raise ValueError("Missing/extra Mathematica comparison rows")
    out=[]
    max_hf_fourq_abs=0.
    for m in MASSES:
        q={i:ref[m,2,i] for i in (3,4,5,6)}
        hf_fourq=max(abs(float(v["HEPfit_minus_author"])) for v in q.values())
        si_fourq=max(abs(float(v["SuperIso_minus_author"])) for v in q.values())
        max_hf_fourq_abs=max(max_hf_fourq_abs,hf_fourq)
        for op,weights in ((7,Y),(8,Z)):
            effective=ref[m,2,op]
            direct=ref[m,3,op]
            comparisons={}
            for label in ("SuperIso","HEPfit"):
                eff_delta=float(effective[label+"_minus_author"])
                raw_delta=float(direct[label+"_minus_author"])
                shift=sum(float(q[i][label+"_minus_author"])*weight
                          for i,weight in weights.items())
                closure=eff_delta-(raw_delta+shift)
                if abs(closure)>1.e-8:
                    raise ValueError(f"Author effective-basis closure FAILED "
                                     f"mass={m} op=C{op} implementation={label}: "
                                     f"closure={closure:g}")
                comparisons[label]={
                    "effective_residual":eff_delta,
                    "raw_dipole_residual":raw_delta,
                    "four_quark_effective_shift_residual":shift,
                    "effective_closure_residual":closure,
                    "raw_relative_to_author":abs(raw_delta)/
                         max(1.e-30,abs(float(direct["original_author"]))),
                    "relative_effective_residual":abs(eff_delta)/
                         max(1.e-30,abs(float(effective["original_author"]))),
                }
            out.append({
                "mass_GeV":m,"operator":f"C{op}",
                "SuperIso":comparisons["SuperIso"],
                "HEPfit":comparisons["HEPfit"],
                "SuperIso_raw_closer_than_HEPfit":
                    abs(comparisons["SuperIso"]["raw_dipole_residual"]) <
                    abs(comparisons["HEPfit"]["raw_dipole_residual"]),
            })
        out.append({
            "mass_GeV":m,"operator":"C3-C6",
            "HEPfit_max_absolute_four_quark_residual":hf_fourq,
            "SuperIso_max_absolute_four_quark_residual":si_fourq,
            "HEPfit_matches_authors_to_1e_10":hf_fourq<1.e-10,
            "SuperIso_matches_authors_to_1e_10":si_fourq<1.e-10,
        })
    fourq=[x for x in out if x["operator"]=="C3-C6"]
    dipoles=[x for x in out if x["operator"]!="C3-C6"]
    hf_exact=all(x["HEPfit_matches_authors_to_1e_10"] for x in fourq)
    si_fourq_diff=any(not x["SuperIso_matches_authors_to_1e_10"] for x in fourq)
    si_raw_preferred=all(x["SuperIso_raw_closer_than_HEPfit"] for x in dipoles)
    classification=(
        "GATE_A1Q_AUTHOR_NUMERIC_FOURQUARK_HEPFIT_CLOSES_"
        "SUPERISO_DISCREPANT_RAW_DIPOLES_SUPERISO_CLOSER_NOT_BR_VALIDATED"
        if hf_exact and si_fourq_diff and si_raw_preferred else
        "GATE_A1Q_AUTHOR_NUMERIC_RESIDUAL_CLOSURE_REQUIRES_REVIEW"
    )
    return {
        "status":classification,
        "original_author_sha256":PINNED_KIT_SHA256,
        "masses_GeV":list(MASSES),
        "four_quark_max_HEPfit_absolute":max_hf_fourq_abs,
        "HEPfit_matches_authors_C3_C6_exact_numerical":hf_exact,
        "SuperIso_C3_C6_has_author_discrepancy":si_fourq_diff,
        "SuperIso_raw_C7_C8_closer_to_authors_all_8":si_raw_preferred,
        "rows":out,
        "all_eight_effective_residuals_decomposed":True,
        "full_NNLO_matching_validated":False,
        "BtoXs_gamma_BR_validated":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-comparison",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    data=json.loads(a.original_comparison.read_text())
    result=close_numeric_comparison(data)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS",result["status"])
    for row in result["rows"]:
        if row["operator"]=="C3-C6":
            print(f"mH={row['mass_GeV']} C3-C6",
                  "max_abs_HEPfit_minus_author=",
                  f"{row['HEPfit_max_absolute_four_quark_residual']:.6g}",
                  "max_abs_SI_minus_author=",
                  f"{row['SuperIso_max_absolute_four_quark_residual']:.6g}")
        else:
            print(f"mH={row['mass_GeV']} {row['operator']}",
                  "SI_raw=",f"{row['SuperIso']['raw_dipole_residual']:.9g}",
                  "SI_fourquark=",f"{row['SuperIso']['four_quark_effective_shift_residual']:.9g}",
                  "SI_effective=",f"{row['SuperIso']['effective_residual']:.9g}",
                  "HF_raw=",f"{row['HEPfit']['raw_dipole_residual']:.9g}",
                  "closure_max=",f"{max(abs(row['SuperIso']['effective_closure_residual']),abs(row['HEPfit']['effective_closure_residual'])):.3g}")
    print("FULL_NNLO_MATCHING_VALIDATED",result["full_NNLO_matching_validated"])
    print("BR_VALIDATED",result["BtoXs_gamma_BR_validated"])
    print("Wrote",a.output)

if __name__=="__main__":
    main()
