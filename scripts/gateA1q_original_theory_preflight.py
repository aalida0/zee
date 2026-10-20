#!/usr/bin/env python3
"""Gate A1Q: original-author NNLO matching source provenance + static preflight.

The original Hermann/Misiak/Steinhauser c2HDM.m file (2012) MUST be
obtained independently. The published README is not equivalent to the
file: it specifies operator normalization and z5=+20, but cannot
adjudicate C3/C4 finite/logarithmic expressions by itself.

NO automatic claim of NNLO matching correctness is permitted by this
static audit. Full A1Q PASS requires later independent numerical
evaluation of the original source and a physical normalization audit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from gateA1p_prepare_hepfit_matching import HEPFIT_BLOB, git_blob_sha
from gateA1p_audit_effective_operator_basis import (
    check_hepfit_nnlo_c8_basis,
    check_superiso_effective_assignments,
)

PAPER="https://arxiv.org/abs/1208.2788"
AUTHOR_README="https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/readme.pdf"
AUTHOR_PROGRAM_PAGE="https://www.ttp.kit.edu/progdata"

# In the 2012 authors' publication normalization, the original dipole
# Wilson coefficients carry inverse powers of the strong coupling.
# See 2012 paper §2.1 and original c2HDM.m README p. 1.
Y={"C3":-1/3,"C4":-4/9,"C5":-20/3,"C6":-80/9}
Z={"C3":1.,"C4":-1/6,"C5":20.,"C6":-10/3}

def check_reference_sources(superiso_path, si_provenance,
                            hepfit_path, hf_provenance):
    si=superiso_path.read_bytes()
    hf=hepfit_path.read_bytes()
    si_manifest=json.loads(si_provenance.read_text())
    hf_manifest=json.loads(hf_provenance.read_text())
    si_sha=hashlib.sha256(si).hexdigest()
    hf_blob=git_blob_sha(hf)
    if si_sha!=si_manifest.get("patched_wilson_sha256"):
        raise ValueError("A1Q BLOCKED: SuperIso A1M source hash mismatch")
    if hf_blob!=HEPFIT_BLOB or hf_manifest.get("upstream_git_blob")!=HEPFIT_BLOB:
        raise ValueError("A1Q BLOCKED: HEPfit original Git blob mismatch")
    si_basis=check_superiso_effective_assignments(si.decode())
    hf_c8=check_hepfit_nnlo_c8_basis(hf.decode())
    return {
        "status":"ORIGINAL_A1M_AND_HEPFIT_SOURCE_SHA_AND_BASIS_GATES_PASS",
        "A1M_wilson_sha256":si_sha,
        "HEPfit_git_blob_sha1":hf_blob,
        "SuperIso_standard_z5_positive_20":si_basis["SuperIso_RG_effective_C8"],
        "HEPfit_NNLO_z5_negative_20":hf_c8,
        "author_readme_standard_z5":20.,
        "HEPfit_z5_differs_from_author_standard":True,
    }

def inspect_author_mathematica(path):
    """Fingerprint a candidate original source; NEVER trust filename alone."""
    if not path.is_file():
        return {
            "status":"BLOCKED_ORIGINAL_C2HDM_M_NOT_ACQUIRED",
            "details":"Acquire the actual original c2HDM.m from the KIT "
                      "TTP12-029 [Source] entry. The README alone "
                      "cannot validate NNLO C3/C4 logs.",
        }
    raw=path.read_bytes()
    if not (1000<=len(raw)<=20_000_000):
        return {"status":"BLOCKED_UNEXPECTED_SOURCE_SIZE","size_bytes":len(raw)}
    try:
        source=raw.decode("utf-8")
    except UnicodeDecodeError:
        return {"status":"BLOCKED_SOURCE_NOT_UTF8_TEXT"}
    if re.search(r"(?i)<!doctype|<html|<body|404 not found|access denied",source):
        return {"status":"BLOCKED_RETRIEVED_HTML_OR_ERROR_PAGE"}
    # The original README identifies these names; a static symbol check
    # is *not* an evaluation of Mathematica expressions, and is not a
    # proof the file is the authors' unmodified distribution.
    patterns={
        "NNLO_fourquark_cH2":r"\bcH\s*\[\s*2\s*,\s*[3456]\s*\]",
        "NNLO_dipole_cHeff2":r"\bcHeff\s*\[\s*2\s*,\s*[78]\s*\]",
        "three_loop_dipole_piecewise":r"\bc[78]t3L2HDM\b",
        "three_loop_log_symbols":r"\bcH3(?:uu|du)L\s*\[\s*[78]\s*\]",
    }
    matches={k:bool(re.search(rx,source)) for k,rx in patterns.items()}
    if not all(matches.values()):
        return {
            "status":"BLOCKED_SOURCE_SYMBOL_CONTRACT_UNCONFIRMED",
            "size_bytes":len(raw),
            "sha256":hashlib.sha256(raw).hexdigest(),
            "symbols":matches,
            "details":"The candidate source must be manually identified; "
                      "do not treat unrecognized content as c2HDM.m.",
        }
    # Author source byte-for-byte authenticity is NOT established by
    # computing a SHA of a user-provided candidate. Require a published
    # upstream checksum, or a recorded official HTTPS retrieval chain.
    # Even when retrieval verified, source syntax alone cannot decide
    # the nontrivial logarithmic or operator-normalization issue.
    return {
        "status":"ORIGINAL_MATHEMATICA_CANDIDATE_FINGERPRINTED_NOT_EVALUATED",
        "size_bytes":len(raw),
        "candidate_sha256":hashlib.sha256(raw).hexdigest(),
        "symbols":matches,
        "source_authenticity_proven_by_local_sha256":False,
        "analytic_C3_C4_log_comparison_pass":False,
        "dipole_normalization_evaluation_pass":False,
    }

def audit(original,reference):
    original_state=inspect_author_mathematica(original)
    return {
        "status":"GATE_A1Q_BLOCKED_PENDING_ORIGINAL_THEORY_EVALUATION",
        "scope":"Source acquisition/provenance/preflight only",
        "original_paper":PAPER,
        "original_author_readme":AUTHOR_README,
        "original_author_programs_page":AUTHOR_PROGRAM_PAGE,
        "author_standard_effective_basis": {
            "y_C3_to_C6":Y,
            "z_C3_to_C6":Z,
            "dipole_normalization":"C7,8eff=(4*pi/alpha_s)*C7,8 + "
                                   "sum_j basis_j*C_j in authors' "
                                   "operator convention",
        },
        "verified_implementation_sources":reference,
        "original_author_source":original_state,
        "required_next_gate":"Evaluate original c2HDM.m C3/C4 NNLO "
                             "functions at two matching scales and "
                             "C7/C8 raw/effective functions with "
                             "matched normalization before validating",
        "mathematica_source_evaluated":False,
        "NNLO_matching_theoretically_validated":False,
        "full_TypeII_branching_ratio_validated":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ("original-mathematica-source","superiso-source","a1m-provenance",
                 "hepfit-source","hepfit-provenance","output"):
        p.add_argument("--"+flag,type=Path,required=True)
    a=p.parse_args()
    verified=check_reference_sources(a.superiso_source,a.a1m_provenance,
                                     a.hepfit_source,a.hepfit_provenance)
    result=audit(a.original_mathematica_source,verified)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS",result["status"])
    print("AUTHOR_SOURCE",result["original_author_source"]["status"])
    print("HEPFIT_Z5_MINUS20_AND_AUTHOR_Z5_PLUS20_SOURCE_EVIDENCE_CONFIRMED")
    print("STOP: NO FULL NNLO MATCHING / NO BR / NO ZEE EXCLUSION")
    print("Wrote",a.output)

if __name__=="__main__":
    main()
