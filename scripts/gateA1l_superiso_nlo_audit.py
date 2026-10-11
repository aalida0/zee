#!/usr/bin/env python3
"""Gate A1L: source-level reproducibility audit of SuperIso v5 NLO clipping.

SuperIso v5.0 CW_calculator appears to scale its NLO charged Higgs C7,
C8, C9, C10 against C0w entries initialized to zero and not yet assigned.
This audit identifies *source order*, not model-level perturbative validity.
No source modification or physical BR constraint is produced.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

def assess(source: str):
    init_match = re.search(
        r"for\s*\(\s*ie\s*=\s*1\s*;\s*ie\s*<=\s*10\s*;\s*ie\+\+\s*\)"
        r"\s*C0w\[ie\]\s*=\s*C1w\[ie\]\s*=\s*C2w\[ie\]\s*=\s*0\s*\.",
        source
    )
    source_lines=source.splitlines()
    rows=[]
    for i in (7,8,9,10):
        name=f"C{i}H_1"
        # Match same C0w[i] in test AND multiplicative correction.
        pat=(
            rf"if\s*\(\s*cabs\(\s*{name}\s*\).*?"
            rf"cabs\(\s*C0w\[{i}\]\s*\)\s*\)\s*"
            rf"{name}\s*\*=\s*cabs\(\s*C0w\[{i}\]\s*\)"
        )
        clamp=re.search(pat,source,re.S)
        # Exact C0w[i] assignments (excluding C0w[ie] zero initialization).
        assignments=list(re.finditer(rf"\bC0w\[{i}\]\s*=",source))
        first_pos=min((m.start() for m in assignments),default=None)
        causal=bool(init_match and clamp and first_pos is not None and
                    init_match.start() < clamp.start() < first_pos)
        line=lambda pos:source.count("\n",0,pos)+1 if pos is not None else None
        rows.append({
            "operator":i,
            "nlo_symbol":name,
            "clamp_present":bool(clamp),
            "source_order_forces_zero_before_assignment":causal,
            "array_init_line":line(init_match.start()) if init_match else None,
            "clamp_line":line(clamp.start()) if clamp else None,
            "first_C0w_assignment_line":line(first_pos)
        })
    issue=all(row["source_order_forces_zero_before_assignment"] for row in rows)
    return {
        "status":("VENDOR_V5_NLO_C7_C8_C9_C10_CLIP_TO_ZERO_SOURCE_CONFIRMED" if issue
                  else "SOURCE_PATTERN_INCOMPLETE_CANNOT_CERTIFY_NLO_CLIP"),
        "rows":rows,
        "claimed_physical_B_to_Xs_gamma":False,
        "conclusion":(
            "The selected NLO charged-Higgs C7,C8,C9,C10 terms are set to zero "
            "because C0w indexed entries are still zero. Other NLO contributions "
            "such as C4H_1 and the charged NNLO pieces are not proven zero."
            if issue else
            "Do not extrapolate this source-based conclusion to another vendor revision."
        ),
        "required_next":"Compare unmodified vendor output with a guarded correction "
            "in a separate development copy; independently validate 2HDM limits, "
            "perturbative normalization and renormalization-scale dependence."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--superiso-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("work/gateA1l_nlo_source_audit.json"))
    a=p.parse_args()
    src=a.superiso_dir.expanduser().resolve()/"src"/"wilson.c"
    if not src.is_file():
        p.error(f"No source file: {src}")
    text=src.read_text(errors="replace")
    r=assess(text)
    r["source_path"]=str(src)
    r["sha256"]=hashlib.sha256(src.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+"\n")
    print("Wrote",a.output)
    for d in r["rows"]:
        print(f"C{d['operator']}: init line {d['array_init_line']}; "
              f"clip line {d['clamp_line']}; assignment line "
              f"{d['first_C0w_assignment_line']}; "
              f"zeroed={d['source_order_forces_zero_before_assignment']}")
    print("STATUS:",r["status"])
    return 0 if all(x["source_order_forces_zero_before_assignment"] for x in r["rows"][:2]) else 1

if __name__=="__main__":
    raise SystemExit(main())
