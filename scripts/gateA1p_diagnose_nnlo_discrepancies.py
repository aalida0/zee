#!/usr/bin/env python3
"""Gate A1P: diagnose NNLO matching discrepancies without modifying physics.

Read existing 44 HEPfit-vs-SuperIso rows; verify input provenance; report
independent NNLO differences and the algebraic C3->C5,C6 relations.
Collect exact original formula source excerpts from the installed
isolated SuperIso and pinned HEPfit file for a human source audit.

A pass through a broad pilot numerical tolerance is NOT a physics pass.
No NNLO normalization/convention is silently changed or corrected.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from gateA1p_prepare_hepfit_matching import HEPFIT_BLOB, git_blob_sha

TARGETS=("C3","C4","C5","C6","C7","C8")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def diagnose(data):
    rows=data["compared_coefficients"]
    by={(float(r["mass_GeV"]),int(r["order"]),r["operator"]):r
        for r in rows}
    if len(rows)!=44 or len(by)!=len(rows):
        raise ValueError("Require 44 unique original comparison entries")
    if data.get("source")!="HEPfit THDMMatching::setWCbsg independent of SuperIso":
        raise ValueError("Unexpected independent matching source")
    output=[]
    for mass in (300.,700.,1000.,2000.):
        r={n:by[mass,2,n] for n in TARGETS}
        d={n:r[n]["superiso_minus_hepfit"] for n in TARGETS}
        c5_from_c3=d["C5"]+d["C3"]/10.
        c6_from_c3=d["C6"]+3.*d["C3"]/16.
        # Dipoles receive both direct three-loop pieces and
        # four-quark-basis recombination terms in HEPfit setWCbsg.
        implied_c7=(-d["C3"]/3.-4.*d["C4"]/9.
                    -20.*d["C5"]/3.-80.*d["C6"]/9.)
        implied_c8=(d["C3"]-d["C4"]/6.
                    -20.*d["C5"]-10.*d["C6"]/3.)
        output.append({
            "mass_GeV":mass,
            "delta_superiso_minus_hepfit":{
                n:d[n] for n in TARGETS
            },
            "C5_residual_after_minus_C3_over10_relation":c5_from_c3,
            "C6_residual_after_minus_3C3_over16_relation":c6_from_c3,
            "C7_delta_from_fourquark_recombination":implied_c7,
            "C7_delta_beyond_fourquark_recombination":d["C7"]-implied_c7,
            "C8_delta_from_fourquark_recombination":implied_c8,
            "C8_delta_beyond_fourquark_recombination":d["C8"]-implied_c8,
            "NNLO_C7_relative_difference":r["C7"]["relative_error"],
            "NNLO_C8_relative_difference":r["C8"]["relative_error"],
        })
    if any(abs(x[k])>1e-11 for x in output for k in
           ("C5_residual_after_minus_C3_over10_relation",
            "C6_residual_after_minus_3C3_over16_relation")):
        raise ValueError(
            "The C5/C6 discrepancy is not explained solely by C3; "
            "additional independent source discrepancies require audit")
    if not data.get("NNLO_above_one_percent_relative_count",0):
        raise ValueError("No reported NNLO precision flags; wrong results file?")
    return {
        "status":"GATE_A1P_NNLO_SOURCE_REVIEW_REQUIRED_BLOCKED",
        "scope":"Postprocessing only; not an NNLO or physical BR correction",
        "masses":output,
        "NNLO_precision_flags":data["NNLO_above_one_percent_relative_count"],
        "C5_C6_disagreement_from_C3_alone":True,
        "original_exploratory_tolerance_failed_count":data["failed_count"],
        "original_exploratory_tolerance_pass_is_not_physics_pass":True,
        "pending":["SuperIso-v5 NNLO C3 and C4 analytic source differences",
                   "Direct NNLO dipole C7 and C8 terms/basis relation",
                   "Full independently computed NNLO Type-II branching ratio"],
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
    }

SUPERI_PAT=re.compile(
    r"\b(?:C[3-8][A-Za-z_0-9]*|G1H|E1H|C7H|C8H)\b"
    r".*(?:_2|NNLO|Higgs|THDM|lambda_u)|"
    r"(?:_2|NNLO|Higgs|THDM|lambda_u).*"
    r"\b(?:C[3-8][A-Za-z_0-9]*|G1H|E1H|C7H|C8H)\b",
    re.I)
HEPFIT_PAT=re.compile(
    r"\b(?:n32ct|cd32ct|n42ct|cd42ct|n41ct|"
    r"n72ct|n72fr|n82ct|n82fr|"
    r"CWbsgArrayNNLO\[)")

def excerpts(lines,matcher,min_line,max_line,radius,limit):
    chosen=set()
    for i,line in enumerate(lines):
        if i+1<min_line or i+1>max_line:
            continue
        if matcher.search(line):
            chosen.update(range(max(0,i-radius),min(len(lines),i+radius+1)))
    indices=sorted(chosen)
    if len(indices)>limit:
        # Refuse silent truncation; user can request explicit source slice.
        indices=indices[:limit]
        truncated=True
    else:truncated=False
    excerpt="\n".join(f"{i+1:5d}: {lines[i]}" for i in indices)
    return {
        "matched_context_line_count":len(chosen),
        "printed_line_count":len(indices),
        "truncated":truncated,
        "excerpts":excerpt,
    }

def source_report(superiso_path,hepfit_path,provenance_path,hepfit_manifest_path):
    si_raw=superiso_path.read_bytes()
    hf_raw=hepfit_path.read_bytes()
    si_prov=json.loads(provenance_path.read_text())
    hf_prov=json.loads(hepfit_manifest_path.read_text())
    if digest(si_raw)!=si_prov.get("patched_wilson_sha256"):
        raise ValueError("SuperIso isolated NLO source hash differs from provenance")
    if git_blob_sha(hf_raw)!=HEPFIT_BLOB or hf_prov.get("upstream_git_blob")!=HEPFIT_BLOB:
        raise ValueError("HEPfit independently pinned source revision changed")
    si_lines=si_raw.decode().splitlines()
    hf_lines=hf_raw.decode().splitlines()
    return {
        "SuperIso_v5_A1M_wilson_c":{
            "path":str(superiso_path),"sha256":digest(si_raw),
            "matching_excerpt":excerpts(si_lines,SUPERI_PAT,
                1400,min(2500,len(si_lines)),3,260)
        },
        "HEPfit_THDMMatching_cpp":{
            "path":str(hepfit_path),"git_blob_sha":git_blob_sha(hf_raw),
            "matching_excerpt":excerpts(hf_lines,HEPFIT_PAT,
                160,min(420,len(hf_lines)),3,220)
        },
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--existing-result",type=Path,required=True)
    p.add_argument("--superiso-a1m-source",type=Path,required=True)
    p.add_argument("--a1m-provenance",type=Path,required=True)
    p.add_argument("--hepfit-source",type=Path,required=True)
    p.add_argument("--hepfit-provenance",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--source-excerpts",type=Path,required=True)
    a=p.parse_args()
    diagnosis=diagnose(json.loads(a.existing_result.read_text()))
    mapping=source_report(
        a.superiso_a1m_source,a.hepfit_source,
        a.a1m_provenance,a.hepfit_provenance)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.source_excerpts.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(diagnosis,indent=2)+"\n")
    snippet_lines=[
        "STATUS GATE_A1P_NNLO_EXACT_SOURCE_SLICES_PROVENANCE_VERIFIED",
        "READ_ONLY_SOURCE_EXCERPTS_NOT_VALIDATED_NNLO"
    ]
    for name,info in mapping.items():
        snippet_lines.extend([
            "",f"==== {name} ====",
            f"path: {info['path']}",
            f"hash: {info.get('sha256',info.get('git_blob_sha'))}",
            info["matching_excerpt"]["excerpts"]])
    a.source_excerpts.write_text("\n".join(snippet_lines)+"\n")
    print("STATUS:",diagnosis["status"])
    print("Wrote",a.output,"and",a.source_excerpts)
    for row in diagnosis["masses"]:
        print(
            f"mH={row['mass_GeV']:.0f}",
            f"dC3={row['delta_superiso_minus_hepfit']['C3']:.9g}",
            f"dC4={row['delta_superiso_minus_hepfit']['C4']:.9g}",
            f"dC7={row['delta_superiso_minus_hepfit']['C7']:.9g}",
            f"dC8={row['delta_superiso_minus_hepfit']['C8']:.9g}",
            f"C5/C6 inherited from C3={diagnosis['C5_C6_disagreement_from_C3_alone']}"
        )
    print("NO PHYSICAL BR/EXCLUSION CLAIM")

if __name__=="__main__":
    main()
