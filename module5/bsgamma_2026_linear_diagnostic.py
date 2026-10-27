"""Misiak et al. 2026 Eq.(4): linearized LO shift diagnostic.

Direct LEFT high-scale coefficient-to-BR formula. No HyperIso Wilson patch
is used. The retained real, top-only LO operator bridge is documented in
BSGAMMA_2026_CONVENTION.md; this is never a full Zee BR or constraint.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from module5.hyperiso_patch_contract import INPUT_FIELDS, make_contract, unique_pairs

SOURCE="arXiv:2608.29863v1"
SOURCE_URL="https://arxiv.org/html/2608.29863v1"
STATUS="2026_EQ4_LO_LINEARIZED_DIAGNOSTIC_NOT_A_CONSTRAINT"
CONVENTION_STATUS="EXTERNAL_CONVENTION_PASS"
MATCHING_GEV=160.0
SM_CENTRAL=3.54
SM_SIGMA=0.14
EXPERIMENT_CENTRAL=3.49
EXPERIMENT_SIGMA=0.19
COEF_C7=-8.51
COEF_C8=-2.16
PHOTON_CUT_GEV=1.6

def finite_real(x, name):
    if isinstance(x,bool) or not isinstance(x,(int,float)):
        raise ValueError(name+": finite real required")
    try:
        value=float(x)
    except OverflowError as exc:
        raise ValueError(name+": finite real required") from exc
    if not math.isfinite(value):
        raise ValueError(name+": finite real required")
    return value

def eq4_conditional(delta_c7,delta_c8):
    a,b=finite_real(delta_c7,"DeltaC7"),finite_real(delta_c8,"DeltaC8")
    pieces=(COEF_C7*a,COEF_C8*b)
    val=math.fsum((SM_CENTRAL,*pieces))
    if not math.isfinite(val):
        raise ValueError("Nonfinite Eq4 output")
    # For large NP the linearized formula could become unphysical; do not
    # clip or call the result a physical BR.
    return {"delta_B_times_1e4":math.fsum(pieces),
            "C7_linear_term_times_1e4":pieces[0],
            "C8_linear_term_times_1e4":pieces[1],
            "conditional_B_times_1e4":val}

def run_contract(contract, source_input_bytes=None):
    if not isinstance(contract,dict):
        raise ValueError("Expected object")
    input_data=contract.get("input")
    if not isinstance(input_data,dict):
        raise ValueError("Missing contract input")
    if not INPUT_FIELDS <= input_data.keys():
        raise ValueError("Missing explicit matching input (including MSbar top mass)")
    expected=make_contract({k:input_data[k] for k in INPUT_FIELDS})
    extras=set(contract)-set(expected)
    if extras-{"input_sha256"}:
        raise ValueError("Unexpected input contract fields")
    # Dict equality would accept False == 0.0 in coefficients and metadata.
    actual=json.dumps({k:v for k,v in contract.items() if k!="input_sha256"},
                      sort_keys=True,allow_nan=False)
    if actual!=json.dumps(expected,sort_keys=True,allow_nan=False):
        raise ValueError("Input contract is not reproduced by frozen Zee LO code")
    input_hash=contract.get("input_sha256")
    if "input_sha256" in contract and (not isinstance(input_hash,str) or
            len(input_hash)!=64 or any(c not in "0123456789abcdef" for c in input_hash)):
        raise ValueError("Malformed source input SHA256")
    if source_input_bytes is not None:
        if hashlib.sha256(source_input_bytes).hexdigest()!=input_hash:
            raise ValueError("Source input SHA256 mismatch")
        source=json.loads(source_input_bytes,object_pairs_hook=unique_pairs,
                          parse_constant=lambda x: finite_real(float(x),"source JSON"))
        if make_contract(source)!=expected:
            raise ValueError("Source input does not reproduce contract")
    if expected["matching_scale_GeV"]!=MATCHING_GEV:
        raise ValueError("Eq4 requires high-scale coefficients at 160 GeV")
    if expected["coefficients"]["C7"]["imag"]!=0.0 or expected["coefficients"]["C8"]["imag"]!=0.0:
        raise ValueError("Complex Wilson coefficients require distinct analysis")
    d7,d8=(expected["coefficients"][k]["real"] for k in ("C7","C8"))
    for k,d in (("C7",d7),("C8",d8)):
        parts=expected["coefficients"][k]["per_state_real"]
        if len(parts)!=2 or not math.isclose(math.fsum(parts),d,abs_tol=2e-15,rel_tol=3e-14):
            raise ValueError("Incoherent two-state "+k+" components")
    return {
        "schema_version":"1.0.0",
        "status":STATUS,"paper":SOURCE,"paper_url":SOURCE_URL,
        "source_equation":"Eq.(4)","operator_basis":"Eq.(2)",
        "external_convention_status":CONVENTION_STATUS,
        "convention_audit":"module5/BSGAMMA_2026_CONVENTION.md",
        "convention_scope":"Real top-only charged-scalar LO dipoles, ms=0; no full Zee matching claim",
        "source_input_sha256":input_hash,
        "source_input_hash_verification":("VERIFIED" if source_input_bytes is not None
                                          else "NOT_VERIFIED_ORIGINAL_BYTES_NOT_PROVIDED"),
        "matching_input":expected["input"],
        "energy_cut_Egamma_GeV":PHOTON_CUT_GEV,
        "matching_scale_GeV":MATCHING_GEV,
        "coefficient_order":"ALPHA_S_0",
        "shift_input":{"DeltaC7":d7,"DeltaC8":d8},
        "linearized":eq4_conditional(d7,d8),
        "published_values_in_units_1e-4":{
            "SM_central":SM_CENTRAL,"SM_reported_sigma":SM_SIGMA,
            "experimental_central":EXPERIMENT_CENTRAL,"experimental_reported_sigma":EXPERIMENT_SIGMA},
        "experiment_comparison":"NOT_EVALUATED",
        "zee_likelihood":None,
        "zee_exclusion":None,
        "global_zee_acceptance":None,
        "hyperiso_injection":"NOT_USED_SM_BSM_PATCH_DROPPED",
        "limitations":[
            "Operator bridge passes only for the retained real top-only LO dipoles; frozen upstream contract metadata is historical.",
            "The explicit MSbar top mass is an input; this diagnostic performs no running, conversion or calibration.",
            "Quadratic new-physics Wilson terms, additional operators, NP NLO/NNLO and finite-ms effects are omitted.",
            "SM 0.14e-4 error is NOT a derived Zee BSM theory uncertainty.",
            "No covariance or justified scan-point exclusion/acceptance; not a physical BR prediction.",
            "Do not impose the single-state Type-II 2HDM 670 GeV lower mass bound separately on Zee charged scalars."
        ]
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",type=Path,required=True,help="Frozen module5.hyperiso_patch_contract JSON")
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--source-input",type=Path,
                    help="Original six-field input bytes, to verify the contract's embedded SHA256")
    args=ap.parse_args()
    raw=args.input.read_bytes()
    c=json.loads(raw,object_pairs_hook=unique_pairs,
                 parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Invalid JSON: "+x)))
    result=run_contract(c,args.source_input.read_bytes() if args.source_input else None)
    result["input_contract_sha256"]=hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=args.output.with_name(args.output.name+".tmp")
    tmp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    tmp.replace(args.output)
    print(STATUS)

if __name__=="__main__":main()
