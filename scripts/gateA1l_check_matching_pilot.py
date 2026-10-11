#!/usr/bin/env python3
"""Gate A1L numerical closure for external Wilson-matching superposition.

Does NOT calculate/validate a physical inclusive branching ratio.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re

_COEFF=re.compile(
    r"^COEFF order=(\d+) i=(\d+) sm=(\S+) delta1=(\S+) "
    r"delta2=(\S+) zee=(\S+)$"
)
_FLOAT=re.compile(r"\b(w1|w2|muW)=(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?)",re.I)

def parse(path):
    content=Path(path).read_text()
    if "MATCHING_WILSON_PILOT_NO_PHYSICAL_BR" not in content:
        raise ValueError(f"Wrong diagnostic status in {path}")
    entries={}
    for line in content.splitlines():
        m=_COEFF.fullmatch(line)
        if m:
            order,i=map(int,m.group(1,2))
            numbers=tuple(map(float,m.groups()[2:]))
            if (order,i) in entries:
                raise ValueError(f"Duplicate order/index {order}/{i}")
            if not all(math.isfinite(x) for x in numbers):
                raise ValueError(f"Nonfinite {order}/{i}")
            entries[order,i]=numbers
    if len(entries)!=30 or set(entries)!={(o,i) for o in range(3) for i in range(1,11)}:
        raise ValueError(f"Expected 30 matching rows, received {len(entries)}")
    inp=next((x for x in content.splitlines() if x.startswith("INPUT ")),None)
    if inp is None:
        raise ValueError("Missing INPUT line")
    params={k:float(v) for k,v in _FLOAT.findall(inp)}
    if set(params)!={"w1","w2","muW"} or abs(sum(params[x] for x in ("w1","w2"))-1)>1e-12:
        raise ValueError("Bad mixing weights")
    return {"entries":entries, "inputs":params}

def check(g0,g90,benchmark,vendor_audit):
    for name,item in (("gamma0",g0),("gamma90",g90),("benchmark",benchmark)):
        if not all((0<item["inputs"]["muW"]<1000,
                    abs(item["inputs"]["w1"]+item["inputs"]["w2"]-1)<1e-12)):
            raise ValueError(f"Bad {name} inputs")
    if (abs(g0["inputs"]["w1"]-1)>1e-12 or
        abs(g90["inputs"]["w2"]-1)>1e-12):
        raise ValueError("Gamma endpoint weights wrong")
    if not all(d["source_order_forces_zero_before_assignment"]
               for d in vendor_audit["rows"] if d["operator"] in (7,8)):
        raise ValueError("Vendor NLO clip pattern not verified: do not certify")
    largest_residual=0.
    max_sm_diff=0.
    for key,b in benchmark["entries"].items():
        s0,l0,h0,z0=g0["entries"][key]
        s90,l90,h90,z90=g90["entries"][key]
        sm,dL,dH,zee=b
        smdiff=max(abs(sm-s0),abs(sm-s90))
        max_sm_diff=max(max_sm_diff,smdiff)
        # At the two gamma endpoints, the physical arrays must reduce to
        # the underlying single-H+ matching vectors.
        computed0=s0+l0
        computed90=s90+h90
        pieces=(
            (z0,computed0),
            (z90,computed90),
            (dL,l0),
            (dH,h90),
            (zee,sm+benchmark["inputs"]["w1"]*dL+
                       benchmark["inputs"]["w2"]*dH),
        )
        largest_residual=max(largest_residual,
                             max(abs(x-y) for x,y in pieces))
        if smdiff>1e-11 or any(
            not math.isclose(x,y,abs_tol=1e-11,rel_tol=1e-11)
            for x,y in pieces
        ):
            raise ValueError(f"Wilson superposition failed at {key}")
    # Source audit predicts NLO charged-Higgs C7,C8 zero by construction.
    nlo_deltas={
        f"C{i}":{
            "light":benchmark["entries"][1,i][1],
            "heavy":benchmark["entries"][1,i][2],
        } for i in (7,8)
    }
    if any(abs(v)>1e-12 for row in nlo_deltas.values() for v in row.values()):
        raise ValueError("Vendor NLO clipping pattern and compiled results disagree")
    if not abs(g0["entries"][0,7][1])>1e-6:
        raise ValueError("Missing LO charged-Higgs contribution")
    return {
        "status":"MATCHING_SUPERPOSITION_PILOT_PASS_VENDOR_NLO_C7_C8_ZERO_BLOCKS_PHYSICAL_BR",
        "scope":"Three LO/NLO/NNLO matching vectors, unmodified vendor v5 library",
        "weights":{"light":benchmark["inputs"]["w1"],
                   "heavy":benchmark["inputs"]["w2"]},
        "matching_scale_GeV":benchmark["inputs"]["muW"],
        "closure":{"maximum_absolute_residual":largest_residual,
                   "max_SM_difference":max_sm_diff,
                   "gamma0_single_light_limit":True,
                   "gamma_pi_over_2_single_heavy_limit":True},
        "nlo_charged_C7_C8_deltas_effectively_zero":nlo_deltas,
        "selected_benchmark_Wilson":{
            f"order_{order}":{
                f"C{i}":{
                    "SM":benchmark["entries"][order,i][0],
                    "DeltaH1":benchmark["entries"][order,i][1],
                    "DeltaH2":benchmark["entries"][order,i][2],
                    "Zee":benchmark["entries"][order,i][3],
                } for i in (4,7,8)
            } for order in (0,1,2)
        },
        "not_done":[
            "A valid nonzero charged-Higgs NLO matching",
            "Primed Wilson coefficients for both charged states",
            "QCD evolution and physical B->Xs gamma",
            "Comparison with experimentally measured HFLAV and theory uncertainty",
        ],
        "allowed_Zee_benchmark":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for x in ("gamma0","gamma90","benchmark","audit","output"):
        p.add_argument("--"+x,type=Path,required=True)
    a=p.parse_args()
    r=check(parse(a.gamma0),parse(a.gamma90),
            parse(a.benchmark),json.loads(a.audit.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+"\n")
    print("Wrote",a.output)
    print("WILSON MATCHING PILOT CLOSURE:",
          r["closure"]["maximum_absolute_residual"])
    for order in ("order_0","order_1","order_2"):
        for symbol in ("C7","C8"):
            entry=r["selected_benchmark_Wilson"][order][symbol]
            print(order,symbol,"SM",entry["SM"],"H1",entry["DeltaH1"],
                  "H2",entry["DeltaH2"],"Zee",entry["Zee"])
    print("STATUS:",r["status"])

if __name__=="__main__":
    main()
