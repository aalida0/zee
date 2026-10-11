#!/usr/bin/env python3
"""Compare MadWidth two-body decay table against independent Gate-6 LO formulas.

Diagnose only: Yang/Wu + Type-II quark/lepton source patch, f_ab=0,
no neutrino-mass fit, no EW/flavor/exclusion constraints, no NLO.
No claims of a *physical* Zee BR. Preserve parent run/card artifacts.
"""
import argparse
import json
import math
import re
from pathlib import Path
from gate6_width_inventory import inventory

DECAY_HEADER = re.compile(
    r"^\s*DECAY\s+([+-]?\d+)\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EDed][+-]?\d+)?)\b",
    re.I,
)


def _float(token):
    return float(token.replace("D", "E").replace("d", "e"))


def read_widths(card):
    result={}
    current=None
    for raw in card.splitlines():
        line=raw.split("#",1)[0].strip()
        if not line:
            continue
        hdr=DECAY_HEADER.match(line)
        if hdr:
            pdg=int(hdr.group(1))
            result[pdg]={"width_GeV":_float(hdr.group(2)),"channels":{}}
            current=pdg
            continue
        if re.match(r"^(?:BLOCK|QNUMBERS)\b",line,re.I):
            current=None
            continue
        if current is None:
            continue
        parts=line.split()
        if len(parts)<4:
            continue
        try:
            br=_float(parts[0]);nda=int(parts[1])
            if len(parts)!=nda+2 or nda<2 or nda>4:
                continue
            pdgs=tuple(sorted(int(n) for n in parts[2:]))
        except ValueError:
            continue
        if pdgs in result[current]["channels"]:
            raise ValueError(f"Duplicate decay table channel for PDG {current}: {pdgs}")
        result[current]["channels"][pdgs]=br
    return result


def compare(card, beta=1.394,mH1=300.,mH2=700.,rel_tolerance=0.20):
    info=read_widths(card)
    for pdg in (227,228):
        if pdg not in info:
            raise ValueError(f"Missing DECAY table {pdg}")
        if info[pdg]["width_GeV"]<=0:
            raise ValueError(f"Nonpositive computed total width PDG {pdg}")
        if not info[pdg]["channels"]:
            raise ValueError(f"No MadWidth branching table entries for PDG {pdg}")
        if sum(info[pdg]["channels"].values())>1.05:
            raise ValueError(f"Decay branching ratios sum to >1 for PDG {pdg}")
    expected=inventory(beta,mH1,mH2)
    check={
        "H2_to_H1_Z":(227,(23,228),expected["partial_widths_GeV"]["H2"]["H1_Z"]),
        "H2_to_tb":(227,(-5,6),expected["partial_widths_GeV"]["H2"]["tb"]),
        "H2_to_W_hheavy":(227,(24,225),expected["partial_widths_GeV"]["H2"]["W_hheavy"]),
        "H2_to_H1_h125":(227,(25,228),expected["partial_widths_GeV"]["H2"]["H1_h125"]),
        "H1_to_tb":(228,(-5,6),expected["partial_widths_GeV"]["H1"]["tb"]),
    }
    comparisons={}
    for label,(parent,daughters,ref) in check.items():
        br=info[parent]["channels"].get(tuple(sorted(daughters)))
        calculated=None if br is None else info[parent]["width_GeV"]*br
        rel=None if calculated is None else (calculated-ref)/ref
        comparisons[label]={
            "parent_pdg":parent,"daughter_pdgs":list(daughters),
            "Gate6_LO_reference_width_GeV":ref,
            "MadWidth_partial_width_GeV":calculated,
            "MadWidth_branching_fraction_unphysical_lepton_limit":br,
            "relative_difference_to_Gate6":rel,
            "passes_lo_20pct_screen":calculated is not None and abs(rel)<rel_tolerance,
        }
    output={
        "status":"LO_DECAY_DIAGNOSTIC_ONLY_NOT_A_PHYSICAL_ZEE_BR",
        "beta":beta,"mH1":mH1,"mH2":mH2,
        "computed_total_widths_GeV":{str(k):info[k]["width_GeV"] for k in (227,228)},
        "sum_decay_table_branching_fractions":{
            str(k):sum(info[k]["channels"].values()) for k in (227,228)},
        "comparisons":comparisons,
        "all_five_partial_width_screens_pass":all(
            v["passes_lo_20pct_screen"] for v in comparisons.values()),
        "relative_tolerance":rel_tolerance,
        "warnings":[
          "The f_ab=0 benchmark has no radiative Zee neutrino masses.",
          "Absolute decay partial widths are more meaningful than model-unstable BR.",
          "Even agreement here does not check gauge invariance or physical constraints.",
          "20% tolerance is diagnostic, not a precision theory uncertainty.",
        ],
    }
    return output


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--card",required=True,type=Path)
    ap.add_argument("--output",type=Path)
    ap.add_argument("--beta",type=float,default=1.394)
    ap.add_argument("--mH1",type=float,default=300.)
    ap.add_argument("--mH2",type=float,default=700.)
    ap.add_argument("--relative-tolerance",type=float,default=.20)
    a=ap.parse_args()
    out=compare(a.card.read_text(),a.beta,a.mH1,a.mH2,a.relative_tolerance)
    text=json.dumps(out,indent=2)+"\n"
    print(text,end="")
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(text)
    if not out["all_five_partial_width_screens_pass"]:
        raise SystemExit("LO DECAY DIAGNOSTIC FAILED: inspect widths/normalizations before physics claims.")


if __name__=="__main__":
    main()
