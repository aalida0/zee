#!/usr/bin/env python3
"""Gate A1N — independent sanity checks for SuperIso inclusive BR candidates.

One must reproduce the verified official v5 SM baseline, stay invariant
under isolated NLO-only source patch for SM, reproduce mixing endpoints,
and report Type-II controls/scale dependences. These are NECESSARY
conditions, NOT sufficient for a physical Zee exclusion.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re

RESULT=re.compile(
    r"^RESULT (\S+) ([0-9]+(?:\.[0-9]*)?(?:[eE][+-]?[0-9]+)?) "
    r"muW=([0-9.eE+-]+) mub=([0-9.eE+-]+) "
    r"cpmax=([0-9.eE+-]+) scale=(\d+)$")
NAMES={
    "SM","TYPEII_300","TYPEII_700","TYPEII_1000","TYPEII_2000",
    "ZEE_300_700","ENDPOINT_H1","ENDPOINT_H2"
}

def parse_output(path):
    lines=Path(path).read_text().splitlines()
    if "STATUS GATE_A1N_BR_CANDIDATE_NOT_VALIDATED_FOR_EXCLUSION" not in lines:
        raise ValueError(f"Missing candidate-only status in {path}")
    if "STATUS_END GATE_A1N_BR_CANDIDATE_NO_EXCLUSION" not in lines:
        raise ValueError(f"Missing completion footer in {path}")
    observations={}
    for line in lines:
        m=RESULT.fullmatch(line)
        if not m:
            continue
        name,br,muW,mub,cp,scale=m.groups()
        key=int(scale),name
        if key in observations:
            raise ValueError(f"Duplicate row {key}")
        vals=dict(br=float(br),muW=float(muW),mub=float(mub),
                  cpmax=float(cp))
        if name not in NAMES or not all(math.isfinite(x) for x in vals.values()):
            raise ValueError(f"Invalid row: {line}")
        if not (0<vals["br"]<1 and vals["cpmax"]<=1e-8):
            raise ValueError(f"Nonphysical or unexpected primed coefficients: {line}")
        observations[key]=vals
    expected={(scale,name) for scale in range(5) for name in NAMES}
    if set(observations)!=expected:
        raise ValueError(f"Incomplete modes/scales: missing={sorted(expected-set(observations))}")
    for scale in range(5):
        rows=[observations[scale,n] for n in NAMES]
        if len({x["muW"] for x in rows})!=1 or len({x["mub"] for x in rows})!=1:
            raise ValueError(f"Coefficient scale mismatch at scan {scale}")
    return observations

def official_sm(log):
    output=Path(log).read_text()
    m=re.search(r"(?m)^BR\(b->s gamma\)\s+([0-9.]+(?:[eE][+-]?[0-9]+)?)\s*$",output)
    if not m:
        raise ValueError("Official Gate A1J SuperIso SM prediction missing")
    value=float(m.group(1))
    if not math.isfinite(value) or not 1e-4 < value < 6e-4:
        raise ValueError("Official SM reference is out of range")
    return value

def verify(original,patched,reference):
    details={}
    for label,rs in (("vendor",original),("isolated",patched)):
        base=rs[0,"SM"]["br"]
        if abs(base-reference)>1.5e-7:
            raise ValueError(
                f"{label} SM {base:.12g} does not reproduce "
                f"official sm.x output {reference:.12g}; do not trust downstream BR")
        max_endpoints=0.
        for scale in range(5):
            for state,end in (("TYPEII_300","ENDPOINT_H1"),("TYPEII_700","ENDPOINT_H2")):
                diff=abs(rs[scale,state]["br"]-rs[scale,end]["br"])
                max_endpoints=max(max_endpoints,diff)
                if diff>2e-12:
                    raise ValueError(f"{label}: {state} matching endpoint BR failed at scan {scale}")
        b300=rs[0,"TYPEII_300"]["br"]
        b700=rs[0,"TYPEII_700"]["br"]
        b1000=rs[0,"TYPEII_1000"]["br"]
        b2000=rs[0,"TYPEII_2000"]["br"]
        details[label]={
            "sm_br":base,
            "typeII_300_br":b300,"typeII_700_br":b700,
            "typeII_1000_br":b1000,"typeII_2000_br":b2000,
            "zee_br_candidate":rs[0,"ZEE_300_700"]["br"],
            "zee_to_sm_ratio":rs[0,"ZEE_300_700"]["br"]/base,
            "typeII_2000_closer_to_sm_than_1000":
                abs(b2000-base)<abs(b1000-base),
            "endpoint_br_max_abs_difference":max_endpoints,
            "muW_variation":{
                "half":rs[1,"ZEE_300_700"]["br"],
                "double":rs[2,"ZEE_300_700"]["br"]},
            "mub_variation":{
                "half":rs[3,"ZEE_300_700"]["br"],
                "double":rs[4,"ZEE_300_700"]["br"]},
        }
    for scale in range(5):
        if abs(original[scale,"SM"]["br"]-patched[scale,"SM"]["br"])>5e-13:
            raise ValueError("Isolated NLO-only patch changed the SM inclusive BR")
    for mode in ("TYPEII_300","TYPEII_700","ZEE_300_700"):
        if abs(original[0,mode]["br"]-patched[0,mode]["br"])<1e-10:
            raise ValueError(f"NLO repair has no impact on {mode} BR; inspect code")
    return {
        "status":"BR_CANDIDATE_SM_AND_ENDPOINT_CONTROLS_PASS_NOT_EXCLUSION",
        "scope":"SuperIso v5 inclusive BR (Egamma>1.6 GeV), "
                "common-scale two-charged matching and native vs isolated variant",
        "official_sm_reference":reference,
        "per_library":details,
        "native_minus_isolated_zee_br":
            original[0,"ZEE_300_700"]["br"]-patched[0,"ZEE_300_700"]["br"],
        "SM_native_vs_isolated_same_all_scales":True,
        "Egamma_cut_GeV":1.6,
        "cautions":[
            "Original v5 has NLO charged C7/C8 clipping bug",
            "Isolated variant removes four limiters but analytic NLO/NNLO matching "
            "and independent Type-II calculation are not yet validated",
            "No full experimental-theory covariance, scale or perturbative "
            "uncertainty assigned",
            "Stock THDM ignores flavour-violating Zee Yukawas beyond chosen "
            "Type-II quark projection and checks no new chirality-flipped terms",
            "Does not establish exclusion or permission to publish the benchmark"
        ],
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("vendor","isolated","reference_sm","output"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    result=verify(parse_output(a.vendor),parse_output(a.isolated),
                  official_sm(a.reference_sm))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("Wrote",a.output)
    for name in ("vendor","isolated"):
        print(name,":",result["per_library"][name])
    print("STATUS:",result["status"])
    print("NO PHYSICAL ZEE VIABILITY OR EXCLUSION DECISION")
if __name__=="__main__":
    main()
