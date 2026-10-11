#!/usr/bin/env python3
"""Source audit: inspect actual SuperIso definition of mass_top_muW.

At A1P the provisional mt=163.107096456575 was inferred from LO C7.
That number is not a certified running-top input without checking the
actual SuperIso formula and parameters at muW. A text-only source audit
identifies the relevant statements without changing vendor source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

PAT=re.compile(r"\bmass_top_muW\b|\brunning_mass\s*\(|\bmass_top_pole\b")

def audit(path,expected_sha=None):
    raw=path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if expected_sha is not None and sha!=expected_sha:
        raise ValueError(f"Unexpected source revision: {sha}")
    lines=raw.decode("utf-8").splitlines()
    hits=[]
    for idx,line in enumerate(lines):
        if PAT.search(line):
            hits.append({"line":idx+1,"text":line.strip()[:500]})
    if not any("mass_top_muW" in x["text"] for x in hits):
        raise ValueError("No mass_top_muW symbol in Wilson source")
    return {
        "status":"SUPERISO_RUNNING_TOP_SOURCE_AUDIT_NOT_INDEPENDENT_NUMERIC_VALUE",
        "source_file":str(path.resolve()),"sha256":sha,
        "hits":hits,
        "mt_muW_used_in_A1P_GeV":163.10709645657502,
        "mt_muW_source_value_directly_evaluated":False,
        "requires":"Independently evaluate top-running-mass function "
                   "at muW=160.7384 with this exact vendor parameter struct; "
                   "record scheme and scale before promoting matching pass.",
    }

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    result=audit(args.source,expected_sha=
      "b3679eec2244917bf062420e69730f91e2bb32a679febd5d0d28db6af5b707bd")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print("Wrote",args.output)
    for entry in result["hits"][:22]:
        print(entry["line"],entry["text"])

if __name__=="__main__":
    main()
