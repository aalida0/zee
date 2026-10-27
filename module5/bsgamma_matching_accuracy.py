"""Gate C2: assess NLO matching sensitivity, NOT a Zee BR or scan exclusion.

Input contains externally RUN, source-pinned HyperIso per-state matching
coefficients in the expansion C=C^(0)+alpha_s/(4*pi)*C^(1)+... .
NLO effects on the *2026 LO-only linear Eq.(4)* are an informal dipole
sensitivity diagnostic, NOT the complete O(alpha_s) correction to BR:
C4 and other operator effects require their proper matrix elements/running.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from module5.bsgamma_lo import compute
from module5.hyperiso_patch_contract import INPUT_FIELDS, unique_pairs

EXPECTED_UPSTREAM = "09d26ac6e71d1528922097a896d15693589f636b"
STATUS = "NLO_MATCHING_SENSITIVITY_ONLY_NOT_SCAN_FILTER"
COEFFICIENT_CONVENTION = "C_0_PLUS_ALPHA_S_OVER_4PI_TIMES_C_1"
MATCHING_BASIS = "BMU_ORDINARY_P4_P7_P8"
SHA_LEN=64

def real(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value,(float,int)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite real")
    if positive and value<=0: raise ValueError(f"{name} must be positive")
    return float(value)

def valid_sha(value):
    return isinstance(value,str) and len(value)==SHA_LEN and all(ch in "0123456789abcdef" for ch in value)

def evaluate(contract, witness):
    if not isinstance(contract,dict) or not isinstance(witness,dict):
        raise ValueError("Both contract and witness must be JSON objects")
    inputs=contract.get("input")
    if not isinstance(inputs,dict) or set(INPUT_FIELDS)-set(inputs):
        raise ValueError("Six-field physical input required")
    if contract.get("status")!="PATCH_INPUT_ONLY_EXTERNAL_OPERATOR_CONVENTION_UNCERTIFIED":
        raise ValueError("Unrecognized pinned Zee LO contract")
    # Reconstruct the SOURCE instead of trusting its cached sums.
    from module5.hyperiso_patch_contract import make_contract
    reference=make_contract({k:inputs[k] for k in INPUT_FIELDS})
    if json.dumps({k:v for k,v in contract.items() if k!="input_sha256"},sort_keys=True,allow_nan=False)!=json.dumps(reference,sort_keys=True,allow_nan=False):
        raise ValueError("Tampered LO contract")
    if reference["matching_scale_GeV"]!=160:
        raise ValueError("Need common scale mu0=160 GeV")
    if witness.get("upstream_commit")!=EXPECTED_UPSTREAM or witness.get("schema_version")!="1.0.0" or witness.get("normalization")!=COEFFICIENT_CONVENTION:
        raise ValueError("Unpinned or unrecognized external matching witness")
    if witness.get("source_status")!="EXECUTED_HYPERISO_UNMODIFIED":
        raise ValueError("NLO witness must originate in an actual pinned HyperIso run")
    if not all(valid_sha(witness.get(k)) for k in ("binary_sha256","source_LHA_sha256","runtime_log_sha256")):
        raise ValueError("Missing external provenance SHA256")
    if witness.get("matching_basis")!=MATCHING_BASIS:
        raise ValueError("Need explicit ordinary BMU matching basis, not effective dipoles")
    q=real(witness.get("qmatch_GeV"),"qmatch",positive=True)
    mt=real(witness.get("mt_MSbar_at_qmatch_GeV"),"top MSbar",positive=True)
    tanb=real(witness.get("tan_beta"),"tanbeta",positive=True)
    alphas=real(witness.get("alpha_s_at_qmatch"),"alpha_s",positive=True)
    if q!=160. or alphas>=1. or abs(mt-reference["top_mass_MSbar_at_matching_scale_GeV"])>2e-11 or abs(tanb-math.tan(reference["input"]["beta_rad"]))>1e-10:
        raise ValueError("Mismatched matching scale, scheme, top mass or tanbeta")
    states=witness.get("unweighted_native_states")
    if not isinstance(states,list) or len(states)!=2:
        raise ValueError("Need exactly two native one-Higgs matching evaluations")
    gamma=reference["input"]["gamma_rad"]
    weights=(math.cos(gamma)**2,math.sin(gamma)**2)
    raw=[]
    for idx,state in enumerate(states):
        if not isinstance(state,dict) or set(state)!={"mH_GeV","C4_NLO_raw","C7_LO","C8_LO","C7_NLO_raw","C8_NLO_raw","C1_to_C6_LO_zero"}:
            raise ValueError("Incomplete per-mass NLO witness")
        mass=real(state["mH_GeV"],"mass",positive=True)
        if abs(mass-reference["input"][f"mH{idx+1}_GeV"])>1e-9 or state["C1_to_C6_LO_zero"] is not True:
            raise ValueError("Mass mismatch or unexpected LO four-quark contributions")
        native={k:real(state[k],k) for k in ("C4_NLO_raw","C7_LO","C8_LO","C7_NLO_raw","C8_NLO_raw")}
        ref_single=compute(mass,mass,reference["input"]["beta_rad"],0.,mt,160.)
        for coeff in ("C7","C8"):
            target=ref_single[f"delta_{coeff}_LO_at_matching_scale"]
            if abs(native[f"{coeff}_LO"]-target)>2e-12*max(1e-8,abs(target)):
                raise ValueError("Native HyperIso LO disagrees with frozen one-state Zee source")
        raw.append(native)
    if abs(sum(weights)-1.)>4e-15:raise ValueError("Bad scalar admixtures")
    ratio=alphas/(4*math.pi)
    weighted={}
    for coef,order in (("C4","NLO_raw"),("C7","LO"),("C8","LO"),("C7","NLO_raw"),("C8","NLO_raw")):
        weighted[f"{coef}_{order}"]=math.fsum(weights[i]*raw[i][f"{coef}_{order}"] for i in (0,1))
    for coeff in ("C7","C8"):
        if abs(weighted[f"{coeff}_LO"]-reference["coefficients"][coeff]["real"])>2e-13:
            raise ValueError("Two-state LO recombination fails")
    nlo_c7=ratio*weighted["C7_NLO_raw"]
    nlo_c8=ratio*weighted["C8_NLO_raw"]
    lo_c7=weighted["C7_LO"];lo_c8=weighted["C8_LO"]
    # Eq.(4) slopes act on C7,C8 only; use as a perturbative sensitivity probe.
    lo_shift=math.fsum((-8.51*lo_c7,-2.16*lo_c8))
    higher_shift=math.fsum((-8.51*nlo_c7,-2.16*nlo_c8))
    return {
        "schema_version":"1.0.0","status":STATUS,
        "model":"ZeeTypeII_two_charged_scalar_real_quark_sector",
        "upstream_commit":EXPECTED_UPSTREAM,
        "matching_basis":MATCHING_BASIS,
        "sensitivity_status":"NLO_MATCHING_DIPOLE_ONLY_SENSITIVITY",
        "matching_scale_GeV":q,"alpha_s_160":alphas,"alpha_s_over_4pi":ratio,
        "weights":list(weights),"matching_coefficients":{
          "LO":{"DeltaC7":lo_c7,"DeltaC8":lo_c8},
          "NLO_raw_unmultiplied":{"DeltaC4":weighted["C4_NLO_raw"],
                                  "DeltaC7":weighted["C7_NLO_raw"],"DeltaC8":weighted["C8_NLO_raw"]},
          "NLO_shift_times_alpha_s_over_4pi":{"DeltaC4":ratio*weighted["C4_NLO_raw"],
                                               "DeltaC7":nlo_c7,"DeltaC8":nlo_c8},
          "LO_plus_NLO_dipole_only":{"DeltaC7":lo_c7+nlo_c7,"DeltaC8":lo_c8+nlo_c8}},
        "2026_Eq4_matching_dipole_sensitivity_in_units_1e_minus4":{
           "LO_NP_dipole_linear_shift":lo_shift,
           "NLO_matching_dipole_only_increment":higher_shift,
           "NLO_increment_over_LO_shift":higher_shift/lo_shift if lo_shift else None},
        "provenance":{k:witness[k] for k in ("binary_sha256","source_LHA_sha256","runtime_log_sha256")},
        "external_convention_status":"PASS_FOR_RETAINED_REAL_TOP_LO_ONLY",
        "nonlinear_BSM_curvature":"NOT_EVALUATED",
        "omitted_NLO_fourquark_effects":"NOT_EVALUATED",
        "full_NP_NLO_rate":"NOT_EVALUATED",
        "NP_theory_uncertainty":"NOT_QUANTIFIED",
        "experimental_comparison":"NOT_EVALUATED",
        "physical_BR":None,"global_zee_acceptance":None,
        "limitations":[
          "This is a source-pinned matching sensitivity test, NOT a direct 2026 higher-order BR.",
          "C4 NLO and other operators are NOT propagated into the 2026 Eq4 formula.",
          "NLO increment is not a calibrated theory uncertainty.",
          "Quadratic NP terms and matching-scale, mass-input and perturbative uncertainties remain open.",
          "One-state 670 GeV Type-II limit cannot be applied to either Zee charged state."
        ]
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract",type=Path,required=True)
    ap.add_argument("--witness",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    def read(p):
        content=p.read_bytes()
        return json.loads(content,object_pairs_hook=unique_pairs,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Nonfinite JSON: "+x))),hashlib.sha256(content).hexdigest()
    contract,contract_hash=read(args.contract)
    witness,witness_hash=read(args.witness)
    result=evaluate(contract,witness)
    result["contract_sha256"]=contract_hash;result["witness_sha256"]=witness_hash
    args.output.parent.mkdir(parents=True,exist_ok=True)
    temp=args.output.with_name(args.output.name+".tmp")
    temp.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    temp.replace(args.output)
    print(STATUS)

if __name__=="__main__": main()
