#!/usr/bin/env python3
"""Gate A1N diagnostic: isolate residual single-Higgs mass dependence.

Consumes the already-computed candidate outputs (not as physics BRs)
and compares the complete post-RG Wilson vector, full primed Wilson
vector, and finally BR for IDENTICAL high-scale Zee matching inputs
at two arbitrary residual mass_H values.

Never bypasses or relaxes the physical-candidate consistency guard.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from gateA1n_check_br_candidate import parse_output

LABELS=("ZEE_300_700","ZEE_SAME_WC_ALT_MASS_700")
RGE=re.compile(
    r"^RGEDETAIL (\S+) i=(\d+) C0re=([+\-0-9.eE]+) "
    r"C0im=([+\-0-9.eE]+) C1re=([+\-0-9.eE]+) "
    r"C1im=([+\-0-9.eE]+) C2re=([+\-0-9.eE]+) "
    r"C2im=([+\-0-9.eE]+) scale=(\d+)$")
PRIME=re.compile(
    r"^CPALL (\S+) i=(\d+) re=([+\-0-9.eE]+) "
    r"im=([+\-0-9.eE]+) scale=(\d+)$")


def load_stages(file_path):
    lines=Path(file_path).read_text().splitlines()
    result=parse_output(file_path)
    rge={}
    prime={}
    for line in lines:
        match=RGE.fullmatch(line)
        if match:
            label,index,*rest=match.groups()
            if label not in LABELS:
                raise ValueError(f"Unexpected RGE label: {label}")
            vals=tuple(float(x) for x in rest[:6])
            key=(int(rest[6]),label,int(index))
            if key in rge or not all(math.isfinite(x) for x in vals):
                raise ValueError(f"Invalid/duplicate RGE row {key}")
            rge[key]=vals
            continue
        match=PRIME.fullmatch(line)
        if match:
            label,index,reval,imval,scale=match.groups()
            if label not in LABELS:
                raise ValueError(f"Unexpected Cprime label: {label}")
            key=(int(scale),label,int(index))
            vals=float(reval),float(imval)
            if key in prime or not all(math.isfinite(x) for x in vals):
                raise ValueError(f"Invalid/duplicate Cprime row {key}")
            prime[key]=vals

    wanted={(scale,label,index) for scale in range(5)
            for label in LABELS for index in range(1,11)}
    if set(rge)!=wanted or set(prime)!=wanted:
        raise ValueError(
            f"Incomplete stage diagnostics: "
            f"RGE missing={len(wanted-set(rge))}; "
            f"prime missing={len(wanted-set(prime))}")
    return result,rge,prime


def source_scan(root):
    root=Path(root).expanduser().resolve()
    findings={}
    for name in ("src/bsgamma.c","src/wilson.c"):
        path=root/name
        if not path.is_file():
            findings[name]={"present":False}
            continue
        lines=path.read_text(errors="replace").splitlines()
        pattern=re.compile(r"\b(?:mass_H|THDM_model)\b")
        hits=[{"line":i+1,"text":line.strip()[:320]}
              for i,line in enumerate(lines) if pattern.search(line)]
        findings[name]={
            "present":True,
            "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "total_mass_H_or_THDM_references":len(hits),
            "first_references":hits[:90],
        }
    return findings


def diagnostic(vendor_file,isolated_file,vendor_root):
    status={}
    for name,file in (("vendor",vendor_file),("isolated",isolated_file)):
        br,rge,prime=load_stages(file)
        per_scale=[]
        for scale in range(5):
            rg_delta=max(abs(x-y)
                for index in range(1,11)
                for x,y in zip(rge[scale,LABELS[0],index],
                               rge[scale,LABELS[1],index]))
            primed_delta=max(abs(x-y)
                for index in range(1,11)
                for x,y in zip(prime[scale,LABELS[0],index],
                               prime[scale,LABELS[1],index]))
            b1=br[scale,LABELS[0]]["br"]
            b2=br[scale,LABELS[1]]["br"]
            per_scale.append({
                "scale_index":scale,
                "zee_BR_using_residual_mass300":b1,
                "zee_BR_using_residual_mass700":b2,
                "BR_absolute_difference":b1-b2,
                "BR_fractional_difference":(b1-b2)/b1,
                "maximum_post_RG_WC_difference":rg_delta,
                "maximum_primed_WC_difference":primed_delta,
            })
        if any(x["maximum_post_RG_WC_difference"]>1e-13
               for x in per_scale):
            cause="RESIDUAL_MASS_DEPENDENCE_ALREADY_IN_RG"
        elif any(x["maximum_primed_WC_difference"]>1e-13
                 for x in per_scale):
            cause="RESIDUAL_MASS_DEPENDENCE_IN_CPRIME"
        elif any(abs(x["BR_absolute_difference"])>2e-12
                 for x in per_scale):
            cause="IDENTICAL_POST_RG_AND_PRIMED_WCS_BUT_BSGAMMA_USES_MASS_CONTEXT"
        else:
            cause="NO_RESIDUAL_MASS_DEPENDENCE_DETECTED"
        status[name]={"stage_diagnosis":cause,"scales":per_scale}

    return {
        "status":"GATE_A1N_DIAGNOSTIC_ONLY_RESIDUAL_MASS_CONTEXT",
        "scope":"Unmodified and isolated SuperIso candidate outputs, no physical Zee BR",
        "source_references":source_scan(vendor_root),
        "libraries":status,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
        "next":"If the full evolved and primed WCs agree, inspect mass_H "
               "references and direct model dependence inside src/bsgamma.c; "
               "do not arbitrarily choose an effective charged mass.",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vendor-log",type=Path,required=True)
    p.add_argument("--isolated-log",type=Path,required=True)
    p.add_argument("--vendor-source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=diagnostic(a.vendor_log,a.isolated_log,a.vendor_source)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("Wrote",a.output)
    for name,detail in result["libraries"].items():
        row=detail["scales"][0]
        print(name,"stage:",detail["stage_diagnosis"])
        print("  nominal delta BR =",row["BR_absolute_difference"])
        print("  max RG WC difference =",row["maximum_post_RG_WC_difference"])
        print("  max primed WC difference =",row["maximum_primed_WC_difference"])
    for name,entry in result["source_references"].items():
        print("SOURCE",name,"mass_H/THDM refs:",
              entry.get("total_mass_H_or_THDM_references","MISSING"))
    print("STATUS: Diagnostic complete; Zee BR remains unvalidated")


if __name__=="__main__":
    main()
