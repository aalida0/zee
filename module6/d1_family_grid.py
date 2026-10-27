"""D1 deterministic *illustrative* Zee family-grid inputs, not a viable scan.

Generates six individually hash-bound Module3 inverse-neutrino inputs from
one existing source, sampling two charged-scalar spectra and three complex
homogeneous Yukawa directions. Does not compute physical acceptance.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

from module2.interface import canonical_hash, strict_loads, scalar_input, validate_schema as validate2
from module3.interface import validate as validate3

STATUS="D1_INPUTS_GENERATED_NOT_EVALUATED"
# Explicit hand-picked development probes, not a physics prior/distribution.
SPECTRA=(
 ("source_spectrum", {}),
 ("illustrative_second_spectrum", {"mH1":450.0,"mH2":850.0,"gamma":0.95}),
)
FAMILIES=(
 ("source_family",complex(1,0)),
 ("homogeneous_x10",complex(10,0)),
 ("homogeneous_i10",complex(0,10)),
)

def generate(seed):
    if not isinstance(seed,dict):raise ValueError("Seed must be an input object")
    validate3(seed,"input.schema.json")
    m2=seed["module2_input"]
    validate2(m2,"input.schema.json")
    if "module2_output" in seed:
        raise ValueError("Input-only seed required; embedded output would become stale")
    if m2["mode"]!="inverse" or m2["scalar"]["kind"]!="module1_input":
        raise ValueError("Require Module2 inverse mode and SHA-bound full Module1 scalar input")
    scalar_input(m2["scalar"])
    if set(m2["scalar"]["record"].get("search",{}))!={"starts","seeds"}:
        raise ValueError("Explicit vacuum search configuration required")
    if not (m2["benchmark_id"]==seed["benchmark_id"]==m2["scalar"]["record"]["benchmark_id"]):
        raise ValueError("Inconsistent benchmark IDs")
    coeff=m2["homogeneous_coefficients"]
    if not isinstance(coeff,dict) or set(coeff)!={"real","imag"} or any(
        not isinstance(coeff[k],list) or len(coeff[k])!=4 for k in ("real","imag")
    ):raise ValueError("Expected four complex homogeneous coefficients")
    original=[complex(r,i) for r,i in zip(coeff["real"],coeff["imag"])]
    if any(not math.isfinite(z.real) or not math.isfinite(z.imag) for z in original):
        raise ValueError("Nonfinite original homogeneous coefficients")
    results=[]
    manifest=[]
    for spectrum_label,changes in SPECTRA:
        for family_label,factor in FAMILIES:
            record=copy.deepcopy(seed)
            identity=f"d1_{m2['ordering']}_{spectrum_label}_{family_label}"
            record["benchmark_id"]=identity
            record["module2_input"]["benchmark_id"]=identity
            wrapper=record["module2_input"]["scalar"]
            scalar=wrapper["record"]
            scalar["benchmark_id"]=identity
            for name,value in changes.items():
                scalar["physical"][name]=value
            wrapper["sha256"]=canonical_hash(scalar)
            family=record["module2_input"]["homogeneous_coefficients"]
            transformed=[factor*z for z in original]
            family["real"]=[z.real for z in transformed]
            family["imag"]=[z.imag for z in transformed]
            validate3(record,"input.schema.json")
            validate2(record["module2_input"],"input.schema.json")
            verified, _=scalar_input(wrapper)
            if not (0<verified["mH1"]<=verified["mH2"] and abs(verified["gamma"])<=math.pi/2):
                raise ValueError("Invalid derived charged-scalar spectrum")
            results.append(record)
            manifest.append({"benchmark_id":identity,"ordering":m2["ordering"],
                             "spectrum_name":spectrum_label,"family_name":family_label,
                             "homogeneous_multiplier":{"real":factor.real,"imag":factor.imag},
                             "charged_masses_GeV":[verified["mH1"],verified["mH2"]],
                             "beta_rad":verified["beta"],"gamma_rad":verified["gamma"],
                             "bound_scalar_input_sha256":wrapper["sha256"],
                             "module3_input_sha256":canonical_hash(record),
                             "physical_status":"NOT_EVALUATED",
                             "constraints_complete":False,"COMPLETE_LFV":False,
                             "flavor_experimental_comparison":"NOT_EVALUATED",
                             "global_zee_acceptance":None})
    if len({x["benchmark_id"] for x in manifest})!=len(manifest) or len(results)!=6:
        raise ValueError("Incomplete/duplicate illustrative grid")
    return results,manifest

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed",required=True,type=Path)
    ap.add_argument("--output-jsonl",required=True,type=Path)
    ap.add_argument("--manifest",required=True,type=Path)
    args=ap.parse_args()
    if len({p.resolve() for p in (args.seed,args.output_jsonl,args.manifest)})!=3:
        raise ValueError("Distinct seed, manifest and JSONL paths required")
    raw=args.seed.read_bytes()
    seed=strict_loads(raw.decode())
    grid,entries=generate(seed)
    payload={"schema_version":"1.0.0","status":STATUS,
             "source_input_bytes_sha256":hashlib.sha256(raw).hexdigest(),
             "generation_scope":"TWO_ILLUSTRATIVE_SPECTRA_X_THREE_COMPLEX_INVERSE_FAMILIES",
             "points":entries,
             "constraints_complete":False,
             "COMPLETE_LFV":False,"flavor_experimental_comparison":"NOT_EVALUATED",
             "global_zee_acceptance":None}
    dests=[(args.output_jsonl,"".join(json.dumps(r,sort_keys=True,allow_nan=False)+"\n" for r in grid)),
           (args.manifest,json.dumps(payload,sort_keys=True,indent=2,allow_nan=False)+"\n")]
    for p,text in dests:
        p.parent.mkdir(parents=True,exist_ok=True)
        tmp=p.with_name(p.name+".tmp")
        tmp.write_text(text)
        tmp.replace(p)
    print(STATUS,"N",len(grid))

if __name__=="__main__":main()
