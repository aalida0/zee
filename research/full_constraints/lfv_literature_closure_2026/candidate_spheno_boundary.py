"""Create an ISOLATED, UNVALIDATED low-scale Zee Yukawa boundary candidate.

Never modifies the source file or compiled binary. This addresses the
observed SPheno FZEEIN insensitivity/Ye2IN cross-dependence as a hypothesis,
not a confirmed model fix. Do not use candidate rates without full validation.

Usage:
  python -m research.full_constraints.lfv_literature_closure_2026.candidate_spheno_boundary \
    --original /path/to/original/ZeeTypeII/SPheno.m \
    --output /tmp/ZeeTypeII_SPheno_yukawa_LHInput_CANDIDATE.m
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

REQUIRED=("OnlyLowEnergySPheno", "BoundaryLowScaleInput")
BOUNDARY=re.compile(r"(BoundaryLowScaleInput\s*=\s*\{)(.*?)(\}\s*;)",re.DOTALL)
ASSIGNMENT=re.compile(r"\{\s*(fzee|Ye2)\s*,",re.IGNORECASE)

def generate(source: str):
    if not all(token in source for token in REQUIRED):
        raise ValueError("Original low-scale model controls not recognized")
    matches=list(BOUNDARY.finditer(source))
    if len(matches)!=1:
        raise ValueError("Expected exactly one original BoundaryLowScaleInput")
    match=matches[0]
    body=match.group(2)
    already=set(z.lower() for z in ASSIGNMENT.findall(body))
    if already:
        raise ValueError("Existing fzee/Ye2 boundary assignments require manual audit: "+str(already))
    insert=("\n  (* RESEARCH CANDIDATE: enforce exact native LHInput matrix bindings *)\n"
            "  {fzee, LHInput[fzee]},\n"
            "  {Ye2, LHInput[Ye2]},\n")
    # Existing original boundary entries follow inserted entries; not affected.
    new=source[:match.start(2)]+insert+source[match.start(2):]
    if new.replace(insert,"",1)!=source:
        raise AssertionError("Unrelated Mathematica model text changed")
    return new

def run(original:Path, output:Path):
    if output.exists():
        raise FileExistsError("Never overwrite a model definition")
    raw=original.read_bytes()
    source=raw.decode("utf-8")
    candidate=generate(source)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(candidate.encode("utf-8"))
    provenance={
        "status":"UNVALIDATED_CANDIDATE_ONLY_NOT_REGENERATED_NOT_COMPILED",
        "original_model_path":str(original),
        "original_SHA256":hashlib.sha256(raw).hexdigest(),
        "candidate_model_path":str(output),
        "candidate_SHA256":hashlib.sha256(output.read_bytes()).hexdigest(),
        "candidate_boundary_entries":["{fzee, LHInput[fzee]}", "{Ye2, LHInput[Ye2]}"],
        "physics_LFV":None,
        "do_not_replace_original":True,
        "validity_requires":["generated Fortran contains both LHInput boundary bindings",
            "source-verified actual model rebuild",
            "SLHA input-response F and Ye2 pass",
            "native 3x3 complex Yukawas and antisymmetry pass",
            "scalar masses and neutrino loop reconstruction pass",
            "recompute actual 64 one-loop operators and conversion"],
    }
    receipt=output.with_suffix(output.suffix+".audit.json")
    if receipt.exists():raise FileExistsError("Existing prior candidate provenance")
    receipt.write_text(json.dumps(provenance,indent=2)+"\n")
    return provenance

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=run(a.original.expanduser(),a.output.expanduser())
    print(r["status"],"CANDIDATE",r["candidate_model_path"])
    print("DO_NOT_USE_FOR_PHYSICS_UNTIL_REGENERATED_AND_VALIDATED")
if __name__=="__main__":main()
