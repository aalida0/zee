#!/usr/bin/env python3
"""Gate A1N: map hidden internal electroweak matching in SuperIso bsgamma.

The bsgamma() API takes evolved Wilson coefficients, but older versions
recalculate high-scale C0w inside bsgamma() for N(E0), P_em(E0).
Search the EXACT installed v5 source without editing the vendor library.

Reports line-numbered excerpts and SHA256. Status is SOURCE AUDIT
ONLY, not a validated Zee branching ratio/exclusion.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import re

PATTERNS=[
    ("internal_matching",re.compile(r"\bCW_calculator\s*\(")),
    ("internal_C0w",re.compile(r"\bC0w\s*\[")),
    ("internal_C1w",re.compile(r"\bC1w\s*\[")),
    ("internal_C2w",re.compile(r"\bC2w\s*\[")),
    ("nonperturbative_N",re.compile(r"\bN_E0\b")),
    ("electromagnetic_P",re.compile(r"\bP_em\b")),
    ("top_charm_interference",re.compile(r"\bKt0\b")),
    ("electromagnetic_C",re.compile(r"\bCem\s*\[")),
    ("charged_mass_direct",re.compile(r"\bmass_H\b")),
    ("function_bsgamma",re.compile(r"\bbsgamma\s*\(")),
]

def audit(src,context=3):
    lines=src.splitlines()
    matches=[]
    for kind,pattern in PATTERNS:
        hits=[i for i,line in enumerate(lines) if pattern.search(line)]
        matches.append((kind,hits))
    significant=set()
    for kind,hits in matches:
        for i in hits:
            significant.update(range(max(0,i-context),
                                     min(len(lines),i+context+1)))
    spans=[]
    for i in sorted(significant):
        if not spans or i>spans[-1][-1]+1:
            spans.append([i])
        else:
            spans[-1].append(i)
    hits={k:[i+1 for i in indexes] for k,indexes in matches}
    out=[]
    out.append("STATUS: SOURCE_MAP_ONLY_NOT_ZEE_BR")
    out.append("OBSERVATION: check whether internal CW_calculator re-evaluates "
               "single-state C0w inside bsgamma and feeds N_E0/P_em.")
    for kind,nums in hits.items():
        out.append(f"{kind}: {nums if nums else 'not found'}")
    out.append("")
    for span in spans:
        out.append(f"===== source lines {span[0]+1}–{span[-1]+1} =====")
        out.extend(f"{i+1:5d}: {lines[i]}" for i in span)
        out.append("")
    if hits["internal_matching"] and hits["internal_C0w"]:
        out.append("SOURCE_FINDING: bsgamma.c contains internal matching and C0w "
                   "references; inspect dataflow before generalizing two-state model.")
    else:
        out.append("SOURCE_FINDING: older-version internal matching pattern not "
                   "observed; trace other hidden helper dependencies instead.")
    out.append("PHYSICAL_BR_EVALUATED: false")
    return "\n".join(out)+"\n"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--superiso-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,
                   default=Path("work/gateA1n_bsgamma_hidden_matching_audit.txt"))
    p.add_argument("--context",type=int,default=4)
    a=p.parse_args()
    if not 0<=a.context<=20:
        p.error("Require context between 0 and 20 source lines")
    path=a.superiso_dir.expanduser().resolve()/"src"/"bsgamma.c"
    if not path.is_file():
        p.error(f"SuperIso bsgamma source missing: {path}")
    raw=path.read_bytes()
    report=(f"SOURCE: {path}\n"
            f"SHA256: {hashlib.sha256(raw).hexdigest()}\n"
            f"TOTAL_LINES: {len(raw.splitlines())}\n\n"
            +audit(raw.decode("utf-8",errors="replace"),a.context))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(report)
    print("Wrote",a.output)
    for line in report.splitlines():
        if line.startswith(("internal_matching:", "internal_C0w:",
                            "nonperturbative_N:", "electromagnetic_P:",
                            "SOURCE_FINDING:", "STATUS:")):
            print(line)

if __name__=="__main__":
    main()
