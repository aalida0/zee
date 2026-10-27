"""D2 deterministic LOW-COST scalar prefilter near the D0 benchmark.

Evaluates frozen reconstruction, tree BFB, 55-state unitarity, scalar STU.
It deliberately does NOT run vacuum searches, neutrino inversion, LFV,
collider rates, or B->Xs gamma. Passing this scoped filter is NOT physical
or global Zee acceptance. The candidate neighborhood is not a scan prior.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import numpy as np

from module1.scalar_constraints import (
    validate_input, reconstruct, check_bfb, unitarity, ewpo
)
from module2.interface import scalar_input, canonical_hash, strict_loads, validate_schema as validate2
from module3.interface import validate as validate3

STATUS = "D2_SCOPED_SCALAR_PREFILTER_NO_VACUUM"
FIELDS = ("mH1", "mH2", "mh2", "ma", "gamma")
# Source-centred DEVELOPMENT perturbations, not physical prior or confidence set.
STEP = {
    "mH1": (10., 25., 50.),
    "mH2": (15., 30., 60.),
    "gamma": (0.02, 0.05, 0.09),
    "mh2": (15., 35.),
    "ma": (15., 35.),
}
CORRELATED = (
    {"mH1": 10., "mH2": 15.},
    {"mH1": -10., "mH2": -15.},
    {"mH1": 25., "mH2": 30.},
    {"mH1": -25., "mH2": -30.},
    {"mh2": 15., "ma": 15.},
    {"mh2": -15., "ma": -15.},
    {"mH2": 15., "ma": 15.},
    {"mH2": -15., "ma": -15.},
)

def neighborhood():
    specs = [("source", {})]
    for key in FIELDS:
        for d in STEP[key]:
            for sign in (-1, 1):
                specs.append((f"{key}_{'m' if sign<0 else 'p'}{str(d).replace('.', 'p')}",
                              {key: sign*d}))
    specs.extend((f"correlated_{i:02d}", d) for i,d in enumerate(CORRELATED))
    if len({name for name,_ in specs})!=len(specs) or len(specs)>64:
        raise ValueError("Duplicate or excessive scalar development probes")
    return specs

def candidate(seed, name, offsets):
    validate3(seed, "input.schema.json")
    validate2(seed["module2_input"], "input.schema.json")
    if "module2_output" in seed:
        raise ValueError("Input-only seed required")
    if seed["module2_input"]["mode"]!="inverse" or seed["module2_input"]["scalar"]["kind"]!="module1_input":
        raise ValueError("Require complete inverse input with bound Module1 scalar")
    scalar_input(seed["module2_input"]["scalar"])
    if not (seed["module2_input"]["benchmark_id"]==seed["benchmark_id"]
            ==seed["module2_input"]["scalar"]["record"]["benchmark_id"]):
        raise ValueError("Incoherent seed benchmark IDs")
    if set(seed["module2_input"]["scalar"]["record"].get("search", {})) != {"starts", "seeds"}:
        raise ValueError("Explicit vacuum search configuration required")
    if not isinstance(offsets,dict) or not set(offsets)<=set(STEP):
        raise ValueError("Unsupported spectrum perturbations")
    out=copy.deepcopy(seed)
    tag=f"d2_{out['module2_input']['ordering']}_{name}"
    out["benchmark_id"]=tag
    out["module2_input"]["benchmark_id"]=tag
    wrapper=out["module2_input"]["scalar"]
    row=wrapper["record"];row["benchmark_id"]=tag
    for key,d in offsets.items():
        if not isinstance(d,(int,float)) or isinstance(d,bool) or not math.isfinite(d):
            raise ValueError("Nonfinite spectrum offset")
        row["physical"][key]=float(row["physical"][key]+d)
    wrapper["sha256"]=canonical_hash(row)
    validate3(out,"input.schema.json")
    validate2(out["module2_input"],"input.schema.json")
    physical,_=scalar_input(wrapper)
    validate_input(row)
    return out,physical

def prefilter(seed):
    specs=neighborhood()
    outputs=[]
    for name,deltas in specs:
        c=None
        gates={}
        try:
            c,x=candidate(seed,name,deltas)
            scalar=c["module2_input"]["scalar"]["record"]
            _, ew, _, _=validate_input(scalar)
            p, inherited, reconstruction=reconstruct(x)
            gates["reconstruction"]=reconstruction
            gates["bfb"]=check_bfb(p)
            gates["unitarity"]=unitarity(p,inherited)
            gates["ewpo"]=ewpo(x,ew,scalar["ew_fit"])
            valid=all(g.get("assessment")=="PASS" for g in gates.values())
            status="PASSES_SCOPED_TREE_AND_EWPO" if valid else "HAS_SCOPED_FAIL_OR_UNKNOWN"
            error=None
        except (ValueError, TypeError, ArithmeticError, KeyError, np.linalg.LinAlgError) as exc:
            status="SCREEN_EVALUATION_BLOCKED"
            error=f"{type(exc).__name__}: {exc}"
            valid=False
        outputs.append({
            "name":name,"offsets":deltas,
            "benchmark_id":c["benchmark_id"] if c is not None else None,
            "scalar_sha256":c["module2_input"]["scalar"]["sha256"] if c is not None else None,
            "physical":{k:x[k] for k in ("mH1","mH2","mh2","ma","gamma","beta")} if c is not None else None,
            "status":status,
            "passes_scoped_tree_and_EWPO":valid,
            "gates":{k:{"status":v.get("status"),"assessment":v.get("assessment"),
                         "STU":v.get("STU"),
                         "chi2":v.get("alternative_fits_not_combined",{}).get(v.get("selected_fit"),{}).get("chi2_relative_to_fit_minimum")}
                     for k,v in gates.items()},
            "vacuum":"NOT_EVALUATED",
            "neutrino":"NOT_EVALUATED",
            "LFV":"NOT_EVALUATED",
            "B_to_Xs_gamma":"NOT_EVALUATED",
            "global_zee_acceptance":None,
            "error":error,
        })
    return {
        "schema_version":"1.0.0","status":STATUS,
        "source_input_sha256":canonical_hash(seed),
        "point_count":len(outputs),
        "scoped_pass_count":sum(x["passes_scoped_tree_and_EWPO"] for x in outputs),
        "scoped_fail_count":sum(x["status"]=="HAS_SCOPED_FAIL_OR_UNKNOWN" for x in outputs),
        "computation_blocked_count":sum(x["status"]=="SCREEN_EVALUATION_BLOCKED" for x in outputs),
        "points":outputs,
        "sampling_scope":"DETERMINISTIC_SMALL_NEIGHBORHOOD_NOT_PRIOR",
        "vacuum":"NOT_EVALUATED",
        "global_zee_acceptance":None,
        "constraints_complete":False,
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.seed.resolve()==args.output.resolve():
        raise ValueError("Input and output paths must differ")
    raw=args.seed.read_bytes()
    inp=strict_loads(raw.decode())
    result=prefilter(inp)
    result["seed_bytes_sha256"]=hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=args.output.with_name(args.output.name+".tmp")
    tmp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    tmp.replace(args.output)
    print(STATUS,result["scoped_pass_count"],"/",result["point_count"])

if __name__=="__main__":
    main()
