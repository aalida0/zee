#!/usr/bin/env python3
"""Gate A1K: read-only SuperIso 5.0 Type-II and Wilson-matching source audit.

Inspects the ACTUAL installed version, not an inferred external API.
No source modification, execution, parameter-point calculation, or
claim of two-charged-state NNLO support. It produces source locations
and bounded excerpts for subsequent scientific code review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

INPUTS = {
    "Makefile": (
        r"(?i)\bthdm\b", r"(?i)\b2HDMC\b", r"(?i)\bscan_coeffs\b",
        r"(?i)\bpredict\b",
    ),
    "thdm.c": (
        r"(?i)\b2HDMC\b", r"(?i)\bTHDM\b", r"(?i)\btype\b",
        r"(?i)\bbsgamma\s*\(",
        r"\bCW_calculator\s*\(", r"\bC_calculator\s*\(",
    ),
    "src/2hdmc.c": (
        r"(?i)\b2HDMC\b", r"(?i)\bTHDM\b",
        r"(?i)\bparam\b", r"(?i)\bYukawa\b",
    ),
    "src/wilson.c": (
        r"\bCW_calculator\s*\(", r"\bC_calculator(?:_base[12])?\s*\(",
        r"\bCprime_calculator\s*\(", r"(?i)\bTHDM\b",
        r"(?i)\bcharged\b.{0,20}\bHiggs\b",
        r"(?i)\bHiggs\b.{0,20}\bcharged\b",
        r"\bC7\b", r"\bC8\b",
    ),
    "src/bsgamma.c": (
        r"\bbsgamma\s*\(", r"\bCW_calculator\s*\(",
        r"\bC_calculator\s*\(", r"\bC7\b", r"\bC8\b",
    ),
    "src/include.h": (
        r"\bstruct\s+parameters\b", r"(?i)\bTHDM\b",
        r"(?i)\b2hdm\b", r"(?i)\bcharged\b",
    ),
    "scan_coeffs.c": (
        r"\bmain\s*\(", r"(?i)\bWilson\b", r"\bC7\b", r"\bC8\b",
        r"\bbsgamma\s*\(", r"\bC_calculator\s*\(",
    ),
    "predict.c": (
        r"\bmain\s*\(", r"(?i)\bWilson\b", r"\bC7\b", r"\bC8\b",
        r"\bbsgamma\s*\(",
    ),
}

# Inspect locations rather than inferring whether matching is supported.
KEYWORDS = {
    "src/wilson.c": ("CW_calculator", "C_calculator_base1",
                     "C_calculator_base2", "Cprime_calculator"),
    "src/bsgamma.c": ("bsgamma",),
    "src/2hdmc.c": ("thdmc",),
    "thdm.c": ("main",),
    "scan_coeffs.c": ("main",),
    "predict.c": ("main",),
}

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as reader:
        for block in iter(lambda: reader.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()

def inspect_file(root, relative, patterns, *, max_hits=12, context=2):
    path = root / relative
    if not path.is_file():
        return {"present":False,"relative_path":relative,"matches":[],
                "matching_signatures":{}, "sha256":None}
    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    signature_locations = {
        name:[index+1 for index,line in enumerate(lines)
              if re.search(r"\b"+re.escape(name)+r"\s*\(",line)]
        for name in KEYWORDS.get(relative, ())
    }
    matches = []
    for key in patterns:
        matched_lines = [i for i,line in enumerate(lines) if re.search(key,line)]
        displayed = matched_lines[:max_hits]
        matches.append({
            "pattern":key, "count_total":len(matched_lines),
            "line_numbers_first": [i+1 for i in displayed],
            "excerpts":[
                {"start_line":max(1,i-context+1),
                 "lines":[{"line":j+1,"text":lines[j][:260]}
                          for j in range(max(0,i-context),
                                         min(len(lines),i+context+1))]}
                for i in displayed
            ],
        })
    return {
        "present":True, "relative_path":relative,
        "sha256":sha256(path), "line_count":len(lines),
        "matching_signatures":signature_locations,
        "matches":matches,
    }

def audit(root, max_hits=8, context=2):
    root=Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"SuperIso source directory not found: {root}")
    if not (root/"Makefile").is_file() or not (root/"src").is_dir():
        raise ValueError("Require vendor Makefile and src/ directory")
    files={name:inspect_file(root,name,expressions,max_hits=max_hits,
                             context=context)
           for name,expressions in INPUTS.items()}
    missing=[name for name,d in files.items() if not d["present"]]
    mandatory=["Makefile","src/wilson.c","src/bsgamma.c","src/include.h"]
    critical_missing=[name for name in mandatory if name in missing]
    return {
        "status":("SOURCE_AUDIT_INCOMPLETE_MANDATORY_FILES_MISSING" if
                  critical_missing else
                  "SOURCE_MAP_CAPTURED_NOT_TWO_CHARGED_MATCHING_CERTIFIED"),
        "vendor_root":str(root),"critical_missing":critical_missing,
        "other_missing":sorted(set(missing)-set(critical_missing)),
        "files":files,
        "observations":{
            "thdm_driver_present":files["thdm.c"]["present"],
            "2hdmc_bridge_present":files["src/2hdmc.c"]["present"],
            "scan_coeffs_source_present":files["scan_coeffs.c"]["present"],
            "predict_source_present":files["predict.c"]["present"],
            "two_charged_state_Zee_implementation_verified":False,
            "typeII_2HDM_control_calculated":False,
            "physical_B_to_Xs_gamma_Zee_calculated":False,
        },
        "next":[
            "Review exact THDM input/yukawa-type parameter handling in thdm.c",
            "Trace charged-Higgs matching in src/wilson.c and src/include.h",
            "Find LO/NLO/NNLO C7/C8 matching and RG call boundaries",
            "Document model convention and SM/2HDM coefficient normalization",
            "Validate pure Type-II one-H+ controls prior to two-state patch",
        ],
    }

def make_text_report(report):
    output = [
        "# Gate A1K — installed SuperIso v5 source-map excerpts",
        f"STATUS: {report['status']}",
        f"Source root: {report['vendor_root']}",
        "NO ZEE b->s gamma physical prediction has been calculated.",
        "All snippets are read from the installed vendor source, "
        "not from an assumed v5 API.",
    ]
    for path,desc in report["files"].items():
        output.append(f"\n## {path}: "+("PRESENT" if desc["present"] else "MISSING"))
        if not desc["present"]:
            continue
        output.append(f"SHA256: {desc['sha256']}; lines={desc['line_count']}")
        for sig,locs in desc["matching_signatures"].items():
            output.append(f"SYMBOL {sig} occurrences at {locs[:24]}")
        for match in desc["matches"]:
            output.append(f"PATTERN {match['pattern']}: "
                          f"{match['count_total']} total; "
                          f"first {match['line_numbers_first']}")
            for excerpt in match["excerpts"]:
                for line in excerpt["lines"]:
                    output.append(f"  L{line['line']:>6}: {line['text']}")
    return "\n".join(output)+"\n"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--superiso-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path(
        "work/gateA1k_superiso_source_audit.json"))
    p.add_argument("--text-report",type=Path,default=Path(
        "work/gateA1k_superiso_source_audit.txt"))
    p.add_argument("--max-hits",type=int,default=8)
    a=p.parse_args()
    if not 1<=a.max_hits<=40:
        p.error("--max-hits must be from 1 to 40")
    r=audit(a.superiso_dir,max_hits=a.max_hits)
    for path,content in (
        (a.output,json.dumps(r,indent=2)+"\n"),
        (a.text_report,make_text_report(r))
    ):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content)
        print("Wrote",path)
    for name in INPUTS:
        d=r["files"][name]
        print(f"{name}: "+("found" if d["present"] else "MISSING"))
        for symbol,locs in d["matching_signatures"].items():
            if locs:
                print(f"  {symbol}: line(s) {locs[:8]}")
    print("STATUS:",r["status"])
    assert not r["observations"]["two_charged_state_Zee_implementation_verified"]
    return 1 if r["critical_missing"] else 0

if __name__=="__main__":
    raise SystemExit(main())
