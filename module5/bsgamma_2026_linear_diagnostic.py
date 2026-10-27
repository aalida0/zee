"""Misiak et al. 2026 Eq.(4): *conditional* linearized LO shift diagnostic.

Direct LEFT high-scale coefficient-to-BR formula. No HyperIso Wilson patch
is used. External full operator convention is not yet independently certified;
this script NEVER performs a Zee exclusion, chi2 or likelihood calculation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from module5.hyperiso_patch_contract import INPUT_FIELDS, make_contract, unique_pairs

SOURCE="arXiv:2608.29863v1"
SOURCE_URL="https://arxiv.org/html/2608.29863v1"
STATUS="2026_EQ4_CONDITIONAL_DIAGNOSTIC_OPERATOR_MAPPING_UNCERTIFIED"
MATCHING_GEV=160.0
SM_CENTRAL=3.54
SM_SIGMA=0.14
EXPERIMENT_CENTRAL=3.49
EXPERIMENT_SIGMA=0.19
COEF_C7=-8.51
COEF_C8=-2.16
PHOTON_CUT_GEV=1.6

def finite_real(x, name):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):
        raise ValueError(name+": finite real required")
    return float(x)

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

def run_contract(contract):
    if not isinstance(contract,dict):
        raise ValueError("Expected object")
    input_data=contract.get("input")
    if not isinstance(input_data,dict):
        raise ValueError("Missing contract input")
    expected=make_contract({k:input_data[k] for k in INPUT_FIELDS})
    extras=set(contract)-set(expected)
    if extras-{"input_sha256"}:
        raise ValueError("Unexpected input contract fields")
    if {k:v for k,v in contract.items() if k!="input_sha256"}!=expected:
        raise ValueError("Input contract is not reproduced by frozen Zee LO code")
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
        "source_equation":"Eq.(4)","operator_basis":"Eq.(2)_CONVENTION_NOT_YET_EXTERNALLY_CLOSED",
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
            "Conditional algebra only: the external Misiak/HyperIso operator convention bridge remains UNKNOWN.",
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
    args=ap.parse_args()
    raw=args.input.read_bytes()
    c=json.loads(raw,object_pairs_hook=unique_pairs,
                 parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Invalid JSON: "+x)))
    result=run_contract(c)
    result["input_contract_sha256"]=hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=args.output.with_name(args.output.name+".tmp")
    tmp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    tmp.replace(args.output)
    print(STATUS)

if __name__=="__main__":main()
