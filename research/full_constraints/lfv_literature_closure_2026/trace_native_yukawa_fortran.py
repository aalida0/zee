"""Read-only forensic trace of the actual compiled ZeeTypeII Yukawa path.

No local SPheno rerun, no model edits, no tolerance changes. Inspects the
exact generated model tree used by the verified binary, extracting context
around FZEEIN/Ye2IN input reading, low-scale matching, boundary code,
spectrum callbacks and output serialisation.

Usage:
  python -m research.full_constraints.lfv_literature_closure_2026.trace_native_yukawa_fortran \\
    --model-dir ~/zee-lfv64-serial-20261112-094549/SPheno-4.0.5/ZeeTypeII \\
    --output ~/zee_yukawa_fortran_trace_20261114.txt
"""
from __future__ import annotations
import argparse
import hashlib
import re
from pathlib import Path

FILES_AND_RANGES={
    "InputOutput_ZeeTypeII.f90": ((135,220),),
    "SPhenoZeeTypeII.f90": ((200,292),(545,610)),
    "Boundaries_ZeeTypeII.f90": ((1445,1502),(1705,1758)),
    "LoopMasses_ZeeTypeII.f90": ((217,273),),
    "Model_Data_ZeeTypeII.f90": ((1923,1985),),
    "RunSM_ZeeTypeII.f90": ((24,95),),
    "Observables/LowEnergy_ZeeTypeII.f90": ((1725,1795),),
}
CALL_PATTERNS=(re.compile(r"\bsubroutine\s+SetMatchingConditions\b", re.I),
               re.compile(r"\bsubroutine\s+CalculateSpectrum\b",re.I),
               re.compile(r"\bsubroutine\s+Boundary(?:Conditions|SUSY|EWSB)\b", re.I))

def contextual(lines,start,end):
    lo=max(1,start);hi=min(len(lines),end)
    return "\n".join(f"{i:5d} {lines[i-1]}" for i in range(lo,hi+1))

def find_subroutine_definitions(model_dir):
    sections=[]
    for p in sorted(model_dir.glob("*.f90")):
        lines=p.read_text(errors="replace").splitlines()
        for i,line in enumerate(lines):
            if any(pat.search(line) for pat in CALL_PATTERNS):
                if line.lstrip().startswith("!"): continue
                if line.strip().lower().startswith("end subroutine"):continue
                if "call " in line.lower():continue
                sections.append((p,lines,i))
    return sections

def inspect(model_dir):
    model_dir=Path(model_dir)
    if not model_dir.is_dir():raise FileNotFoundError(model_dir)
    output=[]
    observed=set()
    output.append("TRACE_STATUS SOURCE_ONLY_NO_NATIVE_PHYSICS_EXECUTED")
    for rel,regions in FILES_AND_RANGES.items():
        p=model_dir/rel
        if not p.is_file():
            output.append("MISSING GENERATED SOURCE "+rel)
            continue
        raw=p.read_bytes()
        lines=raw.decode("utf-8",errors="replace").splitlines()
        output.append("\n===== "+rel+" SHA256 "+hashlib.sha256(raw).hexdigest()+" =====")
        for a,b in regions:
            output.append("--- lines %d-%d ---"%(a,b))
            output.append(contextual(lines,a,b))
        if rel.endswith("Boundaries_ZeeTypeII.f90"):
            for key in ("fzee = fzeeIN","Ye2 = Ye2IN"):
                if any(key.lower() in line.lower() for line in lines):
                    observed.add(key.lower())
    output.append("\n===== EXACT GENERATED SUBROUTINE ENTRY POINTS =====")
    matches=find_subroutine_definitions(model_dir)
    for path,lines,idx in matches:
        output.append("--- "+path.name+":"+str(idx+1)+" ---")
        output.append(contextual(lines,idx+1,min(idx+80,len(lines))))
    output.append("BOUNDARY_LOW_SCALE_F_FROM_INPUT_PRESENT "+str("fzee = fzeein" in observed))
    output.append("BOUNDARY_LOW_SCALE_YE2_FROM_INPUT_PRESENT "+str("ye2 = ye2in" in observed))
    output.append("NEXT ACTION: inspect ReadMatrixC and where the spectrum solver changes the arrays")
    output.append("NO_ORIGINAL_FORTRAN_WAS_MODIFIED; FULL_ZEE_LFV_UNKNOWN")
    return "\n".join(output)+"\n"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-dir",type=Path,default=Path(
        "~/zee-lfv64-serial-20261112-094549/SPheno-4.0.5/ZeeTypeII").expanduser())
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("Do not overwrite forensic trace")
    report=inspect(a.model_dir.expanduser())
    a.output.write_text(report)
    print("WRITTEN",a.output,"BYTES",len(report))
    for token in ("BOUNDARY_LOW_SCALE_F_FROM_INPUT_PRESENT",
                  "BOUNDARY_LOW_SCALE_YE2_FROM_INPUT_PRESENT"):
        match=next((x for x in report.splitlines() if x.startswith(token)),"missing")
        print(match)
    print("FULL_ZEE_LFV_UNKNOWN")

if __name__=="__main__": main()
