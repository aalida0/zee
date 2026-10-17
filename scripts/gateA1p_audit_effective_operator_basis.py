#!/usr/bin/env python3
"""Gate A1P: compare independent Type-II dipole matching in equal bases.

Inputs: existing A1P 44-row match and the provenance-pinned source for
SuperIso A1M and HEPfit. Source shows HEPfit's NNLO setWCbsg[6,7]
contains an effective-operator y/z rotation while SuperIso's source
rotates C2w[7,8] inside C_calculator_base1. An external raw-C7/C8
comparison is therefore NOT intrinsically a common-basis comparison.

This audit displays both direct/non-effective and effective comparisons
without changing any Wilson coefficient or offering a BR/exclusion.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from gateA1p_prepare_hepfit_matching import HEPFIT_BLOB,git_blob_sha

Y={3:-1./3.,4:-4./9.,5:-20./3.,6:-80./9.}
# Author-supplement standard effective-operator coefficients:
# Hermann-Misiak-Steinhauser (2012) c2HDM.m readme, z5 = +20.
Z={3:1.,4:-1./6.,5:20.,6:-10./3.}
# The pinned HEPfit THDMMatching::setWCbsg has -20*C5, not +20*C5
# in its NNLO C8 return expression. Treat that as a CODE/CONVENTION
# discrepancy and undo the ACTUAL code shift, never the assumed one.
HEPFIT_CODE_Z={3:1.,4:-1./6.,5:-20.,6:-10./3.}
MASSES=(300.,700.,1000.,2000.)

# Check the entire effective-operator rotation. Older SuperIso
# releases use 'double'; installed SuperIso v5 uses 'double complex'.
# No coefficient/sign change is acceptable in either representation.
EXPECTED_SUPERISO_EFFECTIVE={
    "C2w7":"C2w[7]-1./3.*C2w[3]-4./9.*C2w[4]"
            "-20./3.*C2w[5]-80./9.*C2w[6]",
    "C2w8":"C2w[8]+C2w[3]-1./6.*C2w[4]"
            "+20.*C2w[5]-10./3.*C2w[6]",
}

def check_superiso_effective_assignments(source):
    """Check all C2w7/C2w8 source terms; ignore C type and whitespace only."""
    found={}
    for name,expected in EXPECTED_SUPERISO_EFFECTIVE.items():
        pattern=rf"\bdouble\s+(?:complex\s+)?{name}\s*=\s*([^;]+);"
        matches=re.findall(pattern,source,re.S)
        if len(matches)!=1:
            raise ValueError(
                f"Expected exactly one SuperIso {name} definition "
                f"(double or double complex), found {len(matches)}")
        actual=re.sub(r"\s+","",matches[0])
        if actual!=expected:
            raise ValueError(
                f"SuperIso {name} effective-basis coefficients/signs differ: "
                f"observed={actual!r} expected={expected!r}")
        found[f"SuperIso_RG_effective_C{name[-1]}"]=True
    return found


def check_hepfit_nnlo_c8_basis(source):
    """Match the active HEPfit NNLO C8 assignment, not debug text.

    Anchor the expression at the beginning of a C++ statement and
    require its right-hand side to start with an opening parenthesis.
    The pinned HEPfit source includes a commented-out std::cout
    containing the text CWbsgArrayNNLO[7] =, which must be ignored.
    Exactly one active assignment must pass all four basis-term checks.
    """
    # Full-line C++ assignment: the real RHS begins "( n82ct ...".
    # The duplicate literal in a commented std::cout begins '" <<'
    # and is not a standalone assignment statement.
    assignments=re.findall(
        r"^[ \t]*CWbsgArrayNNLO\[7\][ \t]*=[ \t]*(\([^;]+);",
        source, re.M)
    if len(assignments)!=1:
        raise ValueError(
            f"Expected one HEPfit NNLO C8 assignment; found {len(assignments)}")
    rhs=re.sub(r"\s+","",assignments[0])
    terms=(
        "+CWbsgArrayNNLO[2]",
        "-1./6.*CWbsgArrayNNLO[3]",
        "-20.*CWbsgArrayNNLO[4]",
        "-10./3.*CWbsgArrayNNLO[5]",
    )
    if not all(term in rhs for term in terms):
        raise ValueError(
            "HEPfit NNLO C8 effective-basis source terms differ "
            "from pinned -20*C5 implementation")
    return True

def assert_source_contract(si_source,si_manifest,hf_source,hf_manifest):
    si=si_source.read_bytes()
    hf=hf_source.read_bytes()
    p=json.loads(si_manifest.read_text())
    q=json.loads(hf_manifest.read_text())
    if hashlib.sha256(si).hexdigest()!=p.get("patched_wilson_sha256"):
        raise ValueError("A1M source hash is not pinned")
    if git_blob_sha(hf)!=HEPFIT_BLOB or q.get("upstream_git_blob")!=HEPFIT_BLOB:
        raise ValueError("HEPfit source is not pinned")
    si_txt=si.decode()
    hf_txt=hf.decode()
    # The exact SuperIso NNLO effective combinations are validated
    # above, accepting the installed version's 'double complex' type.
    # Keep the independent HEPfit basis signatures checked as before.
    checks={
        "HEPfit_NNLO_effective_C7":r"CWbsgArrayNNLO\[6\]\s*=\s*[^;]*-\s*1\./3\.\*CWbsgArrayNNLO\[2\]",
        "HEPfit_NNLO_effective_C8":r"CWbsgArrayNNLO\[7\]\s*=\s*[^;]*\+\s*CWbsgArrayNNLO\[2\]",
    }
    present=check_superiso_effective_assignments(si_txt)
    present.update({
        k:bool(re.search(pattern,hf_txt,re.S))
        for k,pattern in checks.items()
    })
    # The previously published A1P audit implicitly assumed that
    # HEPfit used the standard +20*C5 shift at NNLO. Its pinned source
    # actually uses -20*C5. Check this discrepancy explicitly and
    # reconstruct HEPfit direct coefficients using *its actual code*
    # rather than a convention assumed from the paper.
    present["HEPfit_NNLO_C8_minus20_C5_confirmed"]=(
        check_hepfit_nnlo_c8_basis(hf_txt)
    )
    if not all(present.values()):
        raise ValueError(f"Source-basis check failed: {[k for k,v in present.items() if not v]}")
    return {
        "status":"PINNED_SOURCE_OPERATOR_BASIS_ROTATIONS_PRESENT",
        "SuperIso_A1M_wilson_SHA256":hashlib.sha256(si).hexdigest(),
        "HEPfit_git_blob":git_blob_sha(hf),
        "source_checks":present,
        "HEPfit_actual_NNLO_C8_C5_sign":-1,
        "authors_2012_standard_NNLO_C8_C5_sign":+1,
        "HEPfit_vs_author_z5_sign_disagrees":True,
        "author_reference":"https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/readme.pdf",
    }

def audit(data,contract):
    if data.get("compared_count")!=44 or len(data.get("compared_coefficients",[]))!=44:
        raise ValueError("Require complete A1P 44-row pilot")
    ref={(float(item["mass_GeV"]),int(item["order"]),item["operator"]):item
         for item in data["compared_coefficients"]}
    if len(ref)!=44:
        raise ValueError("Duplicate coefficient rows")
    output=[]
    for mass in MASSES:
        obj={"mass_GeV":mass,"dipole_comparisons":{}}
        for op,standard_weights in ((7,Y),(8,Z)):
            code_weights=Y if op==7 else HEPFIT_CODE_Z
            def get(name,n):
                return float(ref[mass,2,f"C{n}"][name])
            si_raw=get("superiso_isolated_delta",op)
            hf_returned=get("independent_HEPfit_delta",op)
            si_std_shift=sum(w*get("superiso_isolated_delta",i)
                             for i,w in standard_weights.items())
            hf_std_shift=sum(w*get("independent_HEPfit_delta",i)
                             for i,w in standard_weights.items())
            hf_code_shift=sum(w*get("independent_HEPfit_delta",i)
                              for i,w in code_weights.items())
            si_eff=si_raw+si_std_shift
            hf_direct=hf_returned-hf_code_shift
            hf_author_eff=hf_direct+hf_std_shift
            correction=hf_std_shift-hf_code_shift
            direct_difference=si_raw-hf_direct
            effective_difference=si_eff-hf_author_eff
            old_direct=si_raw-(hf_returned-hf_std_shift)
            old_eff=si_eff-hf_returned
            obj["dipole_comparisons"][f"C{op}"]={
                "superiso_raw":si_raw,
                "superiso_standard_fourquark_shift":si_std_shift,
                "superiso_author_standard_effective":si_eff,
                "HEPfit_actual_returned_code_basis":hf_returned,
                "HEPfit_actual_code_fourquark_shift":hf_code_shift,
                "HEPfit_author_standard_fourquark_shift":hf_std_shift,
                "HEPfit_raw_recovered_from_actual_source":hf_direct,
                "HEPfit_author_standard_effective_reconstructed":hf_author_eff,
                "HEPfit_code_to_author_effective_correction":correction,
                "HEPfit_C5_NNLO":get("independent_HEPfit_delta",5),
                "previous_A1P_mixed_raw_vs_code":si_raw-hf_returned,
                "previous_A1P_direct_difference_WITH_WRONG_HEPFIT_Z5":old_direct,
                "previous_A1P_effective_difference_WITH_WRONG_HEPFIT_Z5":old_eff,
                "matched_direct_SuperIso_minus_HEPfit":direct_difference,
                "matched_effective_SuperIso_minus_HEPfit":effective_difference,
                "difference_between_direct_and_effective_discrepancies":
                    effective_difference-direct_difference,
                "fourquark_relative_convention_spread":si_std_shift-hf_std_shift,
            }
            q=obj["dipole_comparisons"][f"C{op}"]
            if abs(q["difference_between_direct_and_effective_discrepancies"]-
                   q["fourquark_relative_convention_spread"])>2e-12:
                raise ValueError(f"Matched direct/effective closure failed for {mass} C{op}")
            if abs(correction-(40.*get("independent_HEPfit_delta",5)
                               if op==8 else 0.))>2e-12:
                raise ValueError(f"Expected isolated HEPfit C8 sign correction not reproduced {mass}")
        output.append(obj)
    return {
        "status":"GATE_A1P_HEPFIT_C8_Z5_SIGN_MISMATCH_AUDITED_NOT_NNLO_PASS",
        "scope":"Dipole basis transformation only; original NNLO disagreements remain",
        "source_contract":contract,
        "reference":"Hermann-Misiak-Steinhauser 2012 ancillary readme defines "
                    "C7eff=C7+y_j Cj and C8eff=C8+z_j Cj",
        "basis_weights_C7":Y,
        "author_standard_basis_weights_C8":Z,
        "HEPfit_actual_code_basis_weights_C8":HEPFIT_CODE_Z,
        "HEPfit_C8_z5_disagrees_with_2012_author_reference":True,
        "HEPfit_source_corrected":False,
        "masses":output,
        "warning":"Previous Gate A1P C8 matched-basis differences were INVALID "
                  "because HEPfit source has z5=-20 whereas the 2012 author "
                  "supplement and SuperIso use z5=+20. The new audit first "
                  "undoes the ACTUAL HEPfit code shift, then reconstructs "
                  "the author-standard effective combination. The resulting "
                  "differences do not certify physical NNLO correctness.",
        "theoretical_NNLO_matching_validated":False,
        "complete_BtoXs_gamma_BR_validated":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("existing-result","superiso-source","a1m-provenance",
                "hepfit-source","hepfit-provenance","output"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    provenance=assert_source_contract(
        a.superiso_source,a.a1m_provenance,
        a.hepfit_source,a.hepfit_provenance)
    result=audit(json.loads(a.existing_result.read_text()),provenance)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS",result["status"])
    for record in result["masses"]:
        for op,coeffs in record["dipole_comparisons"].items():
            print("mH",record["mass_GeV"],op,
                  "direct_difference",coeffs["matched_direct_SuperIso_minus_HEPfit"],
                  "effective_difference",coeffs["matched_effective_SuperIso_minus_HEPfit"],
                  "HEPfit_code_C8_correction",coeffs["HEPfit_code_to_author_effective_correction"])
    print("SOURCE_PROVENANCE_CONFIRMED, NO NNLO OR BR PHYSICS CLAIM")
    print("Wrote",a.output)

if __name__=="__main__": main()
