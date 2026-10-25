"""Versioned *input contract* for a future Zee LO matching patch in HyperIso.

Never computes a B->Xs gamma branching ratio or applies the 2026 limit.
The external Hamiltonian convention is still UNCERTIFIED.
"""
import argparse
import hashlib
import json
from pathlib import Path
from module5.bsgamma_lo import compute, STATUS

ROOT=Path(__file__).resolve().parents[1]
HYPERISO_SHA="09d26ac6e71d1528922097a896d15693589f636b"
VALIDATED_PARENT="218fe01d893730bc2699c270d10db85a22708616"
INPUT_FIELDS=frozenset(("mH1_GeV","mH2_GeV","beta_rad","gamma_rad",
                        "mt_MSbar_GeV","matching_scale_GeV"))
OUTCOME="PATCH_INPUT_ONLY_EXTERNAL_OPERATOR_CONVENTION_UNCERTIFIED"

def make_contract(data):
    if not isinstance(data,dict) or set(data)!=INPUT_FIELDS:
        raise ValueError("Exactly the six explicit frozen Gate A input fields are required")
    lo=compute(**data)
    if lo["status"]!=STATUS or lo["matching_convention_status"]!="MATCHING_CONVENTION_UNKNOWN":
        raise ValueError("Unexpected production matching scope")
    states=lo["charged_scalars"]
    if len(states)!=2 or {r["scalar"] for r in states}!={"H1_charged","H2_charged"}:
        raise ValueError("Two distinct charged-state entries required")
    source=ROOT/"module5/bsgamma_lo.py"
    values={}
    for coeff in ("C7","C8"):
        key="delta_"+coeff
        parts=[float(r[key]) for r in states]
        total=float(lo["delta_"+coeff+"_LO_at_matching_scale"])
        if abs(sum(parts)-total)>1e-12*max(1e-16,abs(total),sum(abs(x) for x in parts)):
            raise ValueError("Per-state Wilson shifts do not sum to total")
        values[coeff]={"real":total,"imag":0.,"per_state_real":parts}
    return {
        "schema_version":"1.0.0","status":OUTCOME,
        "hyperiso_release_commit":HYPERISO_SHA,
        "zee_source_ancestor":VALIDATED_PARENT,
        "zee_lo_source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "matching_scale_GeV":lo["input"]["matching_scale_GeV"],
        "top_mass_MSbar_at_matching_scale_GeV":lo["input"]["mt_MSbar_GeV"],
        "model":"ZeeTypeII_REAL_QUARK_SECTOR_TWO_CHARGED_STATES",
        "contribution":"BSM","order":"LO_ALPHA_S_0",
        "coefficient_basis":"B_C7_C8_CONDITIONAL_MATCHING_NOT_EXTERNAL_OPERATOR_CERTIFIED",
        "coefficients":values,
        "scalar_rows":states,
        "input":lo["input"],
        "misiak_2026_screen":None,"physical_BR":None,
        "experimental_comparison":"NOT_EVALUATED",
        "global_zee_acceptance":None,
        "limitations":[
          "Not a calibrated or validated external Hamiltonian/operator match.",
          "No actual HyperIso injection has been executed by this pure-Python contract.",
          "The MSbar top mass is explicitly supplied; no mass running or scheme conversion occurs.",
          "Do not add to a native THDM charged-Higgs calculation (double counting).",
          "No NP NLO/NNLO, BR, likelihood, exclusion, or full Zee viability."
        ]
    }

def unique_pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError("Duplicate JSON key: "+k)
        d[k]=v
    return d

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    raw=args.input.read_bytes()
    record=json.loads(raw,object_pairs_hook=unique_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Nonfinite JSON: "+x)))
    out=make_contract(record)
    out["input_sha256"]=hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=args.output.with_name(args.output.name+".tmp")
    tmp.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    tmp.replace(args.output)
    print(OUTCOME)

if __name__=="__main__":
    main()
