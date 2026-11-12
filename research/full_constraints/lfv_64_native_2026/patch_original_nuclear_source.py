#!/usr/bin/env python3
"""Minimal audited nuclear proton/neutron scalar-sign repair for Zee FlavorKit.

The model-specific original SPheno FlavorKit_Observables_ZeeTypeII.f90
contains
    Lcont=(Z+N)(g0LV+g0LS)+(Z-N)(g1LV-g1LS)
but the scalar current is physically Z*gSp+N*gSn, not N*gSp+Z*gSn.
Only the isovector scalar signs in Calculate_MuEconversion must change.

Copies to a NEW path; refuses to touch original source, reuse output, patch
an unexpected version or alter anything besides the two known assignments.
Must compile an independent model-specific SPheno binary from the copy;
merely writing this file does NOT repair an existing executable.
"""
from __future__ import annotations
import argparse,hashlib,re
from pathlib import Path

EXPECTED_ORIGINAL="b179e6fea1fe3afe08e34e6d481380b7d4b669ffb904898ac6ee6f8555aa3784"
PATTERN=re.compile(
    r"(?im)^\s*(?P<side>Lcont|Rcont)\s*=\s*"
    r"\(Znuc\+Nnuc\)\s*\*\s*\(g0(?P<chir>LV|RV)\+g0(?P<sca>LS|RS)\)"
    r"\s*\+\s*\(Znuc-Nnuc\)\s*\*\s*\(g1(?P=chir)-g1(?P=sca)\)\s*$"
)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def patch_text(source):
    if source.count("Subroutine Calculate_MuEconversion")!=2:
        # One declaration, one END SUBROUTINE line.
        raise ValueError("Expected exact native source observable declaration/end")
    begin=re.search(r"(?im)^\s*Subroutine\s+Calculate_MuEconversion\b",source)
    end=re.search(r"(?im)^\s*End\s+Subroutine\s+Calculate_MuEconversion\b",source)
    if not begin or not end or end.start()<=begin.end():
        raise ValueError("Cannot isolate original model nuclear observable safely")
    before,body,after=source[:begin.end()],source[begin.end():end.start()],source[end.start():]
    found=[]
    def fix(m):
        side=m.group("side").lower()
        chir,sca=m.group("chir"),m.group("sca")
        if (side=="lcont" and (chir,sca)!=("LV","LS")) or (
            side=="rcont" and (chir,sca)!=("RV","RS")):
            raise ValueError("Unexpected charged scalar/nuclear chirality")
        found.append(side)
        # Preserve original external vector currents exactly, change only
        # the nuclear isovector SCALAR sign.
        return m.group(0).replace("g1"+chir+"-g1"+sca,
                                  "g1"+chir+"+g1"+sca)
    changed,n=PATTERN.subn(fix,body)
    if n!=2 or sorted(found)!=["lcont","rcont"] or changed==body:
        raise ValueError("Original full ZeeTypeII scalar isovector convention not found exactly twice")
    result=before+changed+after
    if result.replace("(g1LV+g1LS)","(g1LV-g1LS)").replace("(g1RV+g1RS)","(g1RV-g1RS)")!=source:
        raise ArithmeticError("Nuclear repair modified anything beyond two scalar signs")
    return result

def patch(original:Path,output:Path):
    if output.exists() or output.resolve()==original.resolve():
        raise FileExistsError("Never overwrite original SPheno/FlavorKit source")
    raw=original.read_bytes()
    if digest(raw)!=EXPECTED_ORIGINAL:
        raise ValueError("Not the known original exact ZeeTypeII generated observable source")
    fixed=patch_text(raw.decode("utf-8")).encode("utf-8")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(fixed)
    return {"input_file":str(original),"original_sha256":digest(raw),
            "copy":str(output),"corrected_sha256":digest(fixed),
            "isovector_scalar_signs_corrected":2,
            "native_executable_recompiled":False,
            "model_specific_conversion_physically_uncertainty_qualified":False}

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--original",required=True,type=Path)
    pa.add_argument("--output",required=True,type=Path)
    args=pa.parse_args()
    print(patch(args.original,args.output))
if __name__=="__main__":
    main()
