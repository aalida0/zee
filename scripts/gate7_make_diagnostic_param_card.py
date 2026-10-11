#!/usr/bin/env python3
"""Create a *diagnostic* Yang/Wu Zee-Type-II LO param card from Gate-6 scalar point.

Lepton treatment: Type-II charged leptons, antisymmetric Zee couplings f_ab=0.
THIS MAKES NEUTRINOS MASSLESS and is NOT a physical neutrino/LFV Zee fit.
This card must not be used for exclusion/discovery statements or BR claims.
Charged scalar DECAY widths in existing template are LEFT UNTOUCHED and STALE.
"""
from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from gate7_map_p2_to_yangwu import map_point

BLOCK_RE=re.compile(r"^\s*block\s+([A-Za-z0-9_]+)(?:\s|$)",re.I)
VALUE_RE=re.compile(r"^(\s*)(\d+)(\s+)([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?)(.*)$")

def replacements(beta=1.394,mH1=300.,mH2=700.):
    p=map_point(beta,mH1,mH2)
    values={(name,int(code)):float(value) for name,block in p["map"].items()
            for code,value in block.items()}
    z=p["input_Gate6"]; tb=math.tan(beta); vev=z["v"]
    for idx in (1,2,3):
        values[("ZEEYUKAWAF",idx)]=0.
    # Yang/Wu charged-lepton Yukawa: - yl Lbar H_v eR - ylz Lbar H_H eR.
    # Type-II charged leptons require ylz = -tanbeta * yl.
    ml={1:0.000511,2:0.10566,3:1.777}
    for i in range(3):
        for j in range(3):
            values[("ZEEYUKAWAY",3*i+j+1)]=(
                -tb*math.sqrt(2)*ml[i+1]/vev if i==j else 0.
            )
    return values

def render_card(template:str,values:dict):
    lines=template.splitlines(keepends=True)
    seen=set();block=None;result=[]
    for line in lines:
        match=BLOCK_RE.match(line)
        if match:
            block=match.group(1).upper()
            result.append(line);continue
        if re.match(r"^\s*(decay|qnumbers)\b",line,re.I):
            block=None
            result.append(line);continue
        # Important: regex '

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--beta",type=float,default=1.394)
    ap.add_argument("--mH1",type=float,default=300.)
    ap.add_argument("--mH2",type=float,default=700.)
    ap.add_argument("--acknowledge-unfitted-neutrino-sector",
        action="store_true",required=True,
        help="Required acknowledgment: f_ab=0 yields massless neutrinos")
    args=ap.parse_args()
    if args.template.resolve()==args.output.resolve():
        ap.error("Refuse to overwrite original parameter card")
    if args.output.exists():
        ap.error("Output exists: refuse overwrite")
    vals=replacements(args.beta,args.mH1,args.mH2)
    content=render_card(args.template.read_text(),vals)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(content)
    # Independent physical readback before advertising successful write.
    validate_card_values(args.output.read_text(),vals)
    print("PASS: independent SLHA readback verified all required entries including MASS[225]")
    print("Wrote diagnostic card:",args.output)
    print("Mapped scalar parameters:",len(vals)-12,
          "; leptonic Yukawas: Type-II y_e,y_mu,y_tau; f_ab=0.")
    print("CAUTION: DECAY widths remain STALE. Do NOT use for physical BRs.")
    print("CAUTION: Zee neutrino masses and LFV NOT fitted; not a physical benchmark.")


if __name__=="__main__":
    main()
 matches BEFORE the final newline; the captured
        # comment/suffix does not include it. Keep the original EOL explicitly.
        # The old writer dropped EOLs and joined MASS entries after '#' comments.
        linebody = line.rstrip("\r\n")
        eol = line[len(linebody):]
        candidate=VALUE_RE.match(linebody) if block else None
        if candidate:
            a,code,ws,num,end=candidate.groups()
            key=(block,int(code))
            if key in values:
                if key in seen:raise ValueError(f"Duplicate LHA parameter {key}")
                line=f"{a}{code}{ws}{values[key]:.12e}{end}{eol}"
                seen.add(key)
        result.append(line)
    missing=set(values).difference(seen)
    if missing:
        raise ValueError("Template does not define required entries: "+repr(sorted(missing)))
    result="".join(result)
    if len(result.splitlines()) != len(template.splitlines()):
        raise ValueError("Refusing malformed parameter card: physical line count changed")
    validate_card_values(result,values)
    # Don't modify DECAY widths: they must be recomputed independently.
    return result


def parse_card_values(card:str)->dict:
    """Strict 1-index SLHA card parser for values this writer is responsible for."""
    out={}
    block=None
    for line in card.splitlines():
        match=BLOCK_RE.match(line)
        if match:
            block=match.group(1).upper()
            continue
        if re.match(r"^\s*(?:decay|qnumbers)\b",line,re.I):
            block=None
            continue
        # Strip SLHA inline comments before parsing numerical entries.
        clean=line.split("#",1)[0]
        if block not in ONE_INDEX_BLOCKS:
            continue
        match=VALUE_RE.match(clean)
        if not match:
            if clean.strip():
                raise ValueError(f"Malformed scalar SLHA data in {block}: {line!r}")
            continue
        if match.group(5).strip():
            raise ValueError(f"Unexpected trailing numerical tokens in {block}: {line!r}")
        key=(block,int(match.group(2)))
        if key in out:
            raise ValueError(f"Duplicate parsed SLHA entry {key}")
        out[key]=float(match.group(4).replace("D","E").replace("d","e"))
    return out


def validate_card_values(card:str,expected:dict):
    values=parse_card_values(card)
    for key,value in expected.items():
        if key not in values:
            raise ValueError(f"Malformed SLHA card: missing {key}")
        if not math.isclose(values[key],value,rel_tol=3e-12,abs_tol=1e-12):
            raise ValueError(f"Malformed SLHA card: wrong {key}: {values[key]} != {value}")
    for pdg in (25,225,226,227,228):
        if ("MASS",pdg) not in values:
            raise ValueError(f"Malformed SLHA card: MASS[{pdg}] missing")
    return True

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--beta",type=float,default=1.394)
    ap.add_argument("--mH1",type=float,default=300.)
    ap.add_argument("--mH2",type=float,default=700.)
    ap.add_argument("--acknowledge-unfitted-neutrino-sector",
        action="store_true",required=True,
        help="Required acknowledgment: f_ab=0 yields massless neutrinos")
    args=ap.parse_args()
    if args.template.resolve()==args.output.resolve():
        ap.error("Refuse to overwrite original parameter card")
    if args.output.exists():
        ap.error("Output exists: refuse overwrite")
    vals=replacements(args.beta,args.mH1,args.mH2)
    content=render_card(args.template.read_text(),vals)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(content)
    print("Wrote diagnostic card:",args.output)
    print("Mapped scalar parameters:",len(vals)-12,
          "; leptonic Yukawas: Type-II y_e,y_mu,y_tau; f_ab=0.")
    print("CAUTION: DECAY widths remain STALE. Do NOT use for physical BRs.")
    print("CAUTION: Zee neutrino masses and LFV NOT fitted; not a physical benchmark.")


if __name__=="__main__":
    main()
