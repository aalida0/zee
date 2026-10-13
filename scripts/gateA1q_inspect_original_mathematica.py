#!/usr/bin/env python3
"""Gate A1Q: authenticated, READ-ONLY inspection of the 2012 KIT c2HDM.m.

This tool establishes that the user's AF retrieval matches the byte-for-byte
original KIT artifact observed for TTP12-029 and extracts evidence of how the
original authors *expressed* selected NNLO matching terms. It DOES NOT
evaluate Mathematica, adjudicate the log convention, or validate a BR.

The exact official SHA256 below is the user's successful AF KIT download,
NOT a checksum copied from HEPfit/SuperIso. Keep the source out of git.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

ORIGINAL_KIT_URL = "https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/c2HDM.m"
PINNED_KIT_SHA256 = "cb2d1328bc2542a6324e73efe6f89c43381efdc93db5e3b0ca8348db980645d8"
EXPECTED_MANIFEST_STATUS = "GATE_A1Q_KIT_ORIGINAL_SOURCE_FETCHED_NOT_EVALUATED"
SELECTORS = {
    "C3_NNLO":r"\bcH\s*\[\s*2\s*,\s*3\s*\]",
    "C4_NNLO":r"\bcH\s*\[\s*2\s*,\s*4\s*\]",
    "C7_NNLO_effective":r"\bcHeff\s*\[\s*2\s*,\s*7\s*\]",
    "C8_NNLO_effective":r"\bcHeff\s*\[\s*2\s*,\s*8\s*\]",
    "C8_NNLO_raw":r"\bcH\s*\[\s*3\s*,\s*8\s*\]",
}
TOKENS = ("Log", "mu", "mt", "r", "ubar", "cH3uuL", "cH3duL", "cH3dur0")

def strip_mathematica_comments(text):
    """Replace nested (* ... *) comments and quoted literals with spaces.

    Preserve original character offsets/newlines, including those within
    nested comments. This prevents false definition matches in comments.
    """
    out=list(text)
    depth=0
    quoted=False
    escaped=False
    i=0
    while i<len(text):
        two=text[i:i+2]
        if depth:
            if two=="(*":
                out[i]=out[i+1]=" "; depth+=1; i+=2; continue
            if two=="*)":
                out[i]=out[i+1]=" "; depth-=1; i+=2; continue
            if text[i]!="\n": out[i]=" "
            i+=1
            continue
        if quoted:
            if text[i]!="\n": out[i]=" "
            if escaped: escaped=False
            elif text[i]=="\\": escaped=True
            elif text[i]=='"': quoted=False
            i+=1
            continue
        if two=="(*":
            out[i]=out[i+1]=" "; depth=1; i+=2; continue
        if text[i]=='"':
            out[i]=" "; quoted=True
        i+=1
    if depth or quoted:
        raise ValueError("Unterminated Mathematica comment or string")
    return "".join(out)

def extract_assignments(source,keypattern,max_excerpt=1300):
    """Find active literal cH[...] / cHeff[...] LHS assignments.

    Do not claim full Mathematica parsing: missing definitions can be built
    with replacement rules or delayed definitions. Source location and a
    bounded literal expression excerpt are provided for expert review.
    """
    clean=strip_mathematica_comments(source)
    pattern=re.compile(keypattern+r"\s*(?::=|=(?!=))")
    rows=[]
    for match in pattern.finditer(clean):
        start=match.start()
        line=source.count("\n",0,start)+1
        end=min(len(clean), match.end()+15000)
        depth=[0,0,0] # parentheses, square brackets, braces
        term=end
        for idx in range(match.end(),end):
            ch=clean[idx]
            if ch==";" and all(n==0 for n in depth):
                term=idx+1
                break
            pairs={"(":(0,1),")":(0,-1),"[":(1,1),"]":(1,-1),
                   "{":(2,1),"}":(2,-1)}
            if ch in pairs:
                k,d=pairs[ch]
                depth[k]+=d
                if depth[k]<0:
                    raise ValueError(f"Unbalanced source near line {line}")
        expr=clean[match.end():term]
        hits={tok:len(re.findall(r"\b"+re.escape(tok)+r"\b",expr))
              for tok in TOKENS}
        rows.append({
            "line":line,"span_start":start,"span_end":term,
            "assignment_operator":clean[match.start():match.end()].strip(),
            "terminated_by_semicolon":term<end,
            "expression_length_chars":len(expr),
            "symbol_counts":{k:v for k,v in hits.items() if v},
            "source_excerpt":source[start:min(term,start+max_excerpt)],
            "excerpt_truncated":term-start>max_excerpt,
        })
    return rows

def attest_source(source_path,manifest_path):
    path=Path(source_path)
    manifest_path=Path(manifest_path)
    raw=path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=PINNED_KIT_SHA256:
        raise ValueError("Official KIT c2HDM.m pinned SHA256 does not match")
    manifest=json.loads(manifest_path.read_text())
    if manifest.get("status")!=EXPECTED_MANIFEST_STATUS:
        raise ValueError("KIT download manifest has unrecognized status")
    if manifest.get("resolved_source_url")!=ORIGINAL_KIT_URL:
        raise ValueError("Manifest does not identify exact official KIT source URL")
    if manifest.get("c2HDM_m_sha256")!=sha:
        raise ValueError("Source checksum conflicts with original KIT manifest")
    if manifest.get("original_source_numerically_evaluated") is not False:
        raise ValueError("KIT source manifest incorrectly indicates prior evaluation")
    return raw.decode("utf-8"),sha,manifest

def audit(source,sha,manifest):
    evidence={key:extract_assignments(source,pat)
              for key,pat in SELECTORS.items()}
    # Genuine Mathematica assignment syntax can use rules or general
    # functions; never equate a missing literal assignment to an absence
    # of the corresponding *physics* term.
    return {
        "status":"GATE_A1Q_ORIGINAL_SOURCE_AUTHENTICATED_STATIC_INSPECTION_NO_NNLO_PASS",
        "original_reference_url":ORIGINAL_KIT_URL,
        "original_reference_sha256":sha,
        "catalogue_resolution_route":manifest.get("source_resolution_route"),
        "matching_conventions_from_README":{
            "standard_effective_C8_coefficient_z5":20,
            "perturbative_normalization_check_required":True,
        },
        "symbol_literal_assignment_evidence":evidence,
        "missing_literal_assignment_keys":[k for k,rows in evidence.items()
                                            if not rows],
        "next_step":"Review excerpts, then construct an independently "
                    "evaluated Mathematica numerical reference with exact "
                    "Yukawa and operator-normalization conventions.",
        "Mathematica_expressions_evaluated":False,
        "C3_C4_log_prescription_adjudicated":False,
        "C8_operator_sign_adjudicated":False,
        "full_NNLO_matching_validated":False,
        "full_BR_validated":False,
        "Zee_benchmark_excluded":None,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--authors-source",type=Path,required=True)
    p.add_argument("--kit-provenance",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    source,sha,manifest=attest_source(args.authors_source,args.kit_provenance)
    result=audit(source,sha,manifest)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS",result["status"])
    print("ORIGINAL_KIT_SHA256_CONFIRMED",sha)
    for key,rows in result["symbol_literal_assignment_evidence"].items():
        print("SOURCE_EXPRESSION",key,"found",len(rows),
              "lines",",".join(str(r["line"]) for r in rows[:6]))
        for row in rows[:2]:
            print("  SYMBOL_COUNTS",row["symbol_counts"],
                  "EXCERPT",row["source_excerpt"][:220].replace("\n"," "))
    print("FULL_NNLO_MATCHING_VALIDATED",result["full_NNLO_matching_validated"])
    print("Wrote",args.output)

if __name__=="__main__":
    main()
