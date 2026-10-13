#!/usr/bin/env python3
"""Gate A1Q: original-author static comparison of NNLO C3/C4 and C8eff.

Validate the authenticated KIT c2HDM.m *definitions themselves* against
source-hashed A1M SuperIso and A1P HEPfit. This does not numerically
evaluate the original Mathematica expression or physical BR(B->Xs gamma).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

from gateA1q_inspect_original_mathematica import (
    SELECTORS,attest_source,extract_assignments,strip_mathematica_comments,
    PINNED_KIT_SHA256,ORIGINAL_KIT_URL,
)
from gateA1q_author_reference_intake import source_conventions

EXPECTED_C7=(
    ("-1/3*cH[2,3]",-1/3),
    ("-4/9*cH[2,4]",-4/9),
    ("-20/3*cH[2,5]",-20/3),
    ("-80/9*cH[2,6]",-80/9),
)
EXPECTED_C8=(
    ("+cH[2,3]",+1),
    ("-1/6*cH[2,4]",-1/6),
    ("+20*cH[2,5]",+20),
    ("-10/3*cH[2,6]",-10/3),
)

def expression_for(original,key):
    clean=strip_mathematica_comments(original)
    rows=extract_assignments(original,SELECTORS[key],max_excerpt=2000)
    if len(rows)!=1:
        raise ValueError(
            f"Expected exactly one original {key} assignment, found {len(rows)}")
    row=rows[0]
    if not row["terminated_by_semicolon"]:
        raise ValueError(f"Original {key} expression not fully delimited")
    return re.sub(r"\s+","",clean[row["span_start"]:row["span_end"]]),row["line"]

def adjudicate_author_static(original,source_checks):
    c3,line3=expression_for(original,"C3_NNLO")
    c4,line4=expression_for(original,"C4_NNLO")
    c7,line7=expression_for(original,"C7_NNLO_effective")
    c8,line8=expression_for(original,"C8_NNLO_effective")

    checks={
        "authors_C3_has_log_mu_squared_over_running_mt_squared":
            "Log[mu^2/mt^2]" in c3,
        "authors_C4_has_log_mu_squared_over_running_mt_squared":
            "Log[mu^2/mt^2]" in c4,
        "authors_C7_effective_rotation_exact":
            all(term in c7 for term,_ in EXPECTED_C7) and
            "cH[3,7]" in c7,
        "authors_C8_effective_rotation_exact":
            all(term in c8 for term,_ in EXPECTED_C8) and
            "cH[3,8]" in c8,
        "hepfit_NNLO_C8_uses_negative_20_C5":
            source_checks["HEPfit_NNLO_C8_minus20_C5_in_source"],
        "superiso_C8_standard_uses_positive_20_C5":
            bool(source_checks["SuperIso_effective_basis_checks"][
                "SuperIso_RG_effective_C8"]),
        "pinned_hepfit_C3_log_matches_author_argument":
            source_checks["source_matching_log_checks"][
                "HEPfit_C3_uses_lstmu"] and
            source_checks["source_matching_log_checks"][
                "HEPfit_lstmu_log_top"],
        "pinned_hepfit_C4_log_matches_author_argument":
            source_checks["source_matching_log_checks"][
                "HEPfit_C4_uses_lstmu"] and
            source_checks["source_matching_log_checks"][
                "HEPfit_lstmu_log_top"],
        "pinned_superiso_C3_log_uses_H_mass":
            source_checks["source_matching_log_checks"][
                "SuperIso_C3_uses_H_mass_in_log"],
        "pinned_superiso_C4_log_uses_H_mass":
            source_checks["source_matching_log_checks"][
                "SuperIso_C4_uses_H_mass_in_log"],
    }
    if not all(checks.values()):
        raise ValueError("Original-authors source conventions incomplete/different: "+
                         ", ".join(k for k,v in checks.items() if not v))
    return {
        "status":
            "GATE_A1Q_ORIGINAL_C3_C4_LOG_ARGUMENT_AND_C8_SIGN_STATIC_MATCH_CONFIRMED",
        "original_author_sha256":PINNED_KIT_SHA256,
        "original_author_url":ORIGINAL_KIT_URL,
        "author_definition_lines":{
            "cH[2,3]":line3,"cH[2,4]":line4,
            "cHeff[2,7]":line7,"cHeff[2,8]":line8,
        },
        "checks":checks,
        "original_C3_matching_log_argument":"Log[mu^2/mt^2]",
        "original_C4_matching_log_argument":"Log[mu^2/mt^2]",
        "HEPfit_C3_C4_matching_log_argument":"2*log(mu/mt)",
        "SuperIso_C3_C4_matching_log_argument":"log((mu_W/mass_H)^2)",
        "original_C8_effective_C5_coefficient":20,
        "pinned_SuperIso_C8_effective_C5_coefficient":20,
        "pinned_HEPfit_C8_effective_C5_coefficient":-20,
        "source_level_C8_sign_inconsistency_confirmed":True,
        "sources_mathematica_evaluated":False,
        "full_NNLO_matching_validated":False,
        "physical_BtoXs_gamma_validated":False,
        "Zee_benchmark_excluded":None,
        "next_required":"Numerically evaluate original c2HDM.m with exact Au,Ad,"
                         " r, mt, mu, and its dipole normalization, then compare"
                         " all coefficients with both implementations.",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("authors-source","kit-provenance","superiso-source",
                "a1m-provenance","hepfit-source","hepfit-provenance","output"):
        p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args()
    src,sha,manifest=attest_source(a.authors_source,a.kit_provenance)
    checks=source_conventions(a.superiso_source,a.a1m_provenance,
                              a.hepfit_source,a.hepfit_provenance)
    result=adjudicate_author_static(src,checks)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS",result["status"])
    for name,line in result["author_definition_lines"].items():
        print("AUTHOR_FORMULA",name,"line",line)
    print("ORIGINAL_C3_C4_LOG",result["original_C3_matching_log_argument"])
    print("ORIGINAL_C8_C5_SIGN",result["original_C8_effective_C5_coefficient"])
    print("HEPFIT_C8_C5_SIGN",result["pinned_HEPfit_C8_effective_C5_coefficient"])
    print("NNLO_VALIDATED",result["full_NNLO_matching_validated"])
    print("Wrote",a.output)

if __name__=="__main__":
    main()
