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
Z={3:1.,4:-1./6.,5:20.,6:-10./3.}
MASSES=(300.,700.,1000.,2000.)

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
    # Guard the exact two distinct locations of the effective
    # transformation; regex checks are structure, not full proof.
    checks={
        "SuperIso_RG_effective_C7":r"double\s+C2w7\s*=\s*C2w\[7\]\s*-\s*1\./3\.\*C2w\[3\]",
        "SuperIso_RG_effective_C8":r"double\s+C2w8\s*=\s*C2w\[8\]\s*\+\s*C2w\[3\]",
        "HEPfit_NNLO_effective_C7":r"CWbsgArrayNNLO\[6\]\s*=\s*[^;]*-\s*1\./3\.\*CWbsgArrayNNLO\[2\]",
        "HEPfit_NNLO_effective_C8":r"CWbsgArrayNNLO\[7\]\s*=\s*[^;]*\+\s*CWbsgArrayNNLO\[2\]",
    }
    present={
        k:bool(re.search(pattern,si_txt if k.startswith("SuperIso") else hf_txt,re.S))
        for k,pattern in checks.items()
    }
    if not all(present.values()):
        raise ValueError(f"Source-basis check failed: {[k for k,v in present.items() if not v]}")
    return {
        "status":"PINNED_SOURCE_OPERATOR_BASIS_ROTATIONS_PRESENT",
        "SuperIso_A1M_wilson_SHA256":hashlib.sha256(si).hexdigest(),
        "HEPfit_git_blob":git_blob_sha(hf),
        "source_checks":present
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
        for op,weights in ((7,Y),(8,Z)):
            def get(name,n):
                return float(ref[mass,2,f"C{n}"][name])
            si_raw=get("superiso_isolated_delta",op)
            hf_eff=get("independent_HEPfit_delta",op)
            si_4q=sum(w*get("superiso_isolated_delta",i)
                      for i,w in weights.items())
            hf_4q=sum(w*get("independent_HEPfit_delta",i)
                      for i,w in weights.items())
            si_eff=si_raw+si_4q
            hf_direct=hf_eff-hf_4q
            obj["dipole_comparisons"][f"C{op}"]={
                "superiso_raw":si_raw,
                "superiso_fourquark_basis_shift":si_4q,
                "superiso_effective":si_eff,
                "HEPfit_effective":hf_eff,
                "HEPfit_fourquark_basis_shift":hf_4q,
                "HEPfit_direct":hf_direct,
                "SuperIso_raw_minus_HEPfit_effective_INVALID_MIXED_BASIS":si_raw-hf_eff,
                "matched_direct_SuperIso_minus_HEPfit":si_raw-hf_direct,
                "matched_effective_SuperIso_minus_HEPfit":si_eff-hf_eff,
                "difference_between_direct_and_effective_discrepancies":
                    (si_eff-hf_eff)-(si_raw-hf_direct),
                "fourquark_relative_convention_spread":si_4q-hf_4q,
            }
            # Algebraic closure, including for any deviations already
            # traced to NNLO C3/C4 scale logarithms.
            q=obj["dipole_comparisons"][f"C{op}"]
            assert abs(q["difference_between_direct_and_effective_discrepancies"]-
                       q["fourquark_relative_convention_spread"])<2e-12
        output.append(obj)
    return {
        "status":"GATE_A1P_EFFECTIVE_OPERATOR_BASIS_CONSISTENCY_AUDIT_NOT_NNLO_PASS",
        "scope":"Dipole basis transformation only; original NNLO disagreements remain",
        "source_contract":contract,
        "reference":"Hermann-Misiak-Steinhauser 2012 ancillary readme defines "
                    "C7eff=C7+y_j Cj and C8eff=C8+z_j Cj",
        "basis_weights_C7":Y,"basis_weights_C8":Z,
        "masses":output,
        "warning":"Do not compare SuperIso raw C7/C8 with HEPfit effective "
                  "C7/C8; display matched direct and matched effective "
                  "differences separately. Basis transformations do not "
                  "fix the known C3/C4 matching-log prescription mismatch.",
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
                  "effective_difference",coeffs["matched_effective_SuperIso_minus_HEPfit"])
    print("SOURCE_PROVENANCE_CONFIRMED, NO NNLO OR BR PHYSICS CLAIM")
    print("Wrote",a.output)

if __name__=="__main__": main()
