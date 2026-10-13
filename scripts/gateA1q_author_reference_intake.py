#!/usr/bin/env python3
"""Gate A1Q: intake of ORIGINAL 2012 NNLO Mathematica reference.

Ref: Hermann, Misiak, Steinhauser, arXiv:1208.2788 (v2), and KIT
TTP12-029 official supplementary README for c2HDM.m.

This gate does NOT evaluate Mathematica or make any BR/exclusion claim.
It records independently verified operator conventions and detects
source inconsistencies, but it is BLOCKED until the ORIGINAL c2HDM.m
source is actually supplied, provenance-pinned and evaluated.

Never substitute HEPfit's or SuperIso's matching source for c2HDM.m.
Never use a generated/reconstructed expression as an original source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from gateA1p_prepare_hepfit_matching import HEPFIT_BLOB,git_blob_sha
from gateA1p_audit_effective_operator_basis import (
    check_superiso_effective_assignments,check_hepfit_nnlo_c8_basis,
)

PUBLICATION="Hermann–Misiak–Steinhauser, arXiv:1208.2788v2, 2012"
PAPER="https://arxiv.org/html/1208.2788"
AUTHOR_README="https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/readme.pdf"
CATALOGUE="https://www.ttp.kit.edu/progdata"
Y=[0,0,-1/3,-4/9,-20/3,-80/9]
Z=[0,0,+1,-1/6,+20,-10/3]

SYMBOLS=("cHeff","cH","cH3uuL","cH3duL",
         "cH3uur0","cH3dur0","cH3uur1m","cH3dur1m")

def original_reference_presence(path,expected_sha256=None):
    """Conservative intake check; syntactic presence is NOT numerical proof."""
    if not path:
        return {"status":"ORIGINAL_C2HDM_M_NOT_SUPPLIED","source_sha256":None,
                "symbol_coverage":None,"originality_verified":False}
    path=Path(path)
    if not path.is_file():
        raise ValueError(f"Original c2HDM.m missing: {path}")
    if path.name!="c2HDM.m":
        raise ValueError("Require extracted original file named c2HDM.m")
    raw=path.read_bytes()
    if len(raw)<500:
        raise ValueError("Original candidate c2HDM.m implausibly short")
    if len(raw)>25_000_000:
        raise ValueError("Original candidate c2HDM.m implausibly large")
    try:
        content=raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Original candidate c2HDM.m not UTF-8 text") from exc
    present={name:bool(re.search(r"\b"+re.escape(name)+r"\b",content))
             for name in SYMBOLS}
    if not all(present.values()):
        raise ValueError(
            "Original Mathematica source symbols incomplete: "+
            ",".join(name for name,found in present.items() if not found))
    digest=hashlib.sha256(raw).hexdigest()
    if expected_sha256 and expected_sha256.lower()!=digest:
        raise ValueError("Original reference expected SHA256 mismatch")
    # A checksum supplied by the user verifies byte identity ONLY.
    # It does not authenticate the source's historical origin. The
    # official KIT Source artifact must be independently retrieved
    # before declaring that this is the authors' original implementation.
    return {"status":("CANDIDATE_SOURCE_BYTES_CHECKSUM_MATCH_NOT_AUTHENTICATED"
                      if expected_sha256 else
                      "AUTHOR_SOURCE_CANDIDATE_NOT_INDEPENDENTLY_PINNED"),
            "source_sha256":digest,"source_size_bytes":len(raw),
            "symbol_coverage":present,
            "expected_hash_matches":bool(expected_sha256),
            "originality_verified":False,
            "Mathematica_expressions_evaluated":False}

def source_conventions(superiso_path,a1m_prov,hepfit_path,hepfit_prov):
    s=Path(superiso_path).read_bytes()
    h=Path(hepfit_path).read_bytes()
    sm=json.loads(Path(a1m_prov).read_text())
    hm=json.loads(Path(hepfit_prov).read_text())
    if hashlib.sha256(s).hexdigest()!=sm.get("patched_wilson_sha256"):
        raise ValueError("A1M SuperIso source not provenance-pinned")
    if git_blob_sha(h)!=HEPFIT_BLOB or hm.get("upstream_git_blob")!=HEPFIT_BLOB:
        raise ValueError("A1P HEPfit source not provenance-pinned")
    si=s.decode()
    hf=h.decode()
    doublet=check_superiso_effective_assignments(si)
    hepfit_c8=check_hepfit_nnlo_c8_basis(hf)
    # Exact source matching-log anchors (the numerical discrepancy
    # was already independently reproduced at 8 points in Gate A1P).
    log_checks={
        "SuperIso_C3_uses_H_mass_in_log":bool(re.search(
            r"C3H_2\s*=\s*G3H\s*\([^;]*Delta3H\s*\([^;]*"
            r"log\s*\(\s*pow\s*\(\s*mu_W\s*/\s*param->mass_H",si,re.S)),
        "SuperIso_C4_uses_H_mass_in_log":bool(re.search(
            r"C4H_2\s*=\s*G4H\s*\([^;]*Delta4H\s*\([^;]*"
            r"log\s*\(\s*pow\s*\(\s*mu_W\s*/\s*param->mass_H",si,re.S)),
        "HEPfit_C3_uses_lstmu":bool(re.search(
            r"CWbsgArrayNNLO\[2\]\s*=\s*\(\s*n32ct\s*\+\s*cd32ct\s*\*\s*lstmu",hf)),
        "HEPfit_C4_uses_lstmu":bool(re.search(
            r"CWbsgArrayNNLO\[3\]\s*=\s*\(\s*n42ct\s*\+\s*cd42ct\s*\*\s*lstmu",hf)),
        "HEPfit_lstmu_log_top":bool(re.search(
            r"double\s+lstmu\s*=\s*2\.\s*\*\s*log\s*\(\s*mu\s*/\s*mt\s*\)",hf)),
    }
    if not all(log_checks.values()):
        raise ValueError("SuperIso/HEPfit source matching-log contracts changed")
    return {
        "status":"EXISTING_IMPLEMENTATION_SOURCE_CONVENTIONS_HASH_PINNED",
        "SuperIso_SHA256":hashlib.sha256(s).hexdigest(),
        "HEPfit_Git_blob":git_blob_sha(h),
        "SuperIso_effective_basis_checks":doublet,
        "HEPfit_NNLO_C8_minus20_C5_in_source":hepfit_c8,
        "SuperIso_standard_C8_z5":+20,
        "HEPfit_implemented_NNLO_C8_z5":-20,
        "original_author_README_standard_C8_z5":+20,
        "source_matching_log_checks":log_checks,
        "warning":"Original paper dipole operator uses inverse g_s powers. "
                  "Do not compare raw operators without perturbative re-normalization."
    }

def make_report(conventions,authors,origin_url):
    return {
        "status":("GATE_A1Q_CANDIDATE_SOURCE_INTAKE_NOT_AUTHENTICATED"
                  if authors["source_sha256"] else
                  "GATE_A1Q_BLOCKED_ORIGINAL_AUTHOR_SOURCE_NOT_SUPPLIED"),
        "publication":PUBLICATION,
        "original_paper":PAPER,
        "official_readme":AUTHOR_README,
        "official_source_listing":CATALOGUE,
        "reference_download_origin_supplied_by_user":origin_url,
        "published_source_author_README_basis":{
            "y_vector":Y,"z_vector":Z,
            "C7_C8_operator_normalization":"4*pi/alpha_s * C7/8 + sum_j y_j/z_j*Cj",
            "top_input":"running mt(mu0)",
            "three_loop_piecewise":"cH3uuL/duL and expansions",
        },
        "existing_independent_source_contract":conventions,
        "authors_Mathematica_source_intake":authors,
        "must_do_before_source_claim":[
            "Obtain original KIT catalogue Source artifact and record URL and checksum",
            "Independently evaluate cH[2,3], cH[2,4] at exact benchmark scales",
            "Evaluate cHeff[2,8] and verify effective z5 sign after conventions",
            "Check original C7/C8 three-loop finite functions at benchmark masses",
            "Verify perturbative normalization between 2012 paper and both libraries",
        ],
        "NNLO_matching_validated":False,
        "physical_BtoXs_gamma_validated":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("superiso-source","a1m-provenance",
                "hepfit-source","hepfit-provenance","output"):
        p.add_argument("--"+key,required=True,type=Path)
    p.add_argument("--authors-source",type=Path)
    p.add_argument("--authors-expected-sha256")
    p.add_argument("--authors-origin-url")
    a=p.parse_args()
    if a.authors_expected_sha256 and not a.authors_source:
        p.error("Expected SHA256 requires the original author source")
    context=source_conventions(a.superiso_source,a.a1m_provenance,
                               a.hepfit_source,a.hepfit_provenance)
    authors=original_reference_presence(
        a.authors_source,a.authors_expected_sha256)
    report=make_report(context,authors,a.authors_origin_url)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n")
    print("STATUS",report["status"])
    print("2012_AUTHOR_SOURCE_INTAKE",authors["status"])
    print("AUTHORS_C8_EFFECTIVE_Z5",report[
        "published_source_author_README_basis"]["z_vector"][4])
    print("HEPFIT_SOURCE_C8_Z5",context["HEPfit_implemented_NNLO_C8_z5"])
    print("DO_NOT_CLAIM_FULL_NNLO_OR_PHYSICAL_BR")
    print("Wrote",a.output)

if __name__=="__main__": main()
