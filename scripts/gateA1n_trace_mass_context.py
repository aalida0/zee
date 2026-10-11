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

LABELS=("ZEE_300_700","ZEE_SAME_WC_ALT_MASS_700",
        "ZEE_REPEAT_MASS_300","ZEE_REPEAT_MASS_700")
RGE=re.compile(
    r"^RGEDETAIL (\S+) i=(\d+) C0re=([+\-0-9.eE]+) "
    r"C0im=([+\-0-9.eE]+) C1re=([+\-0-9.eE]+) "
    r"C1im=([+\-0-9.eE]+) C2re=([+\-0-9.eE]+) "
    r"C2im=([+\-0-9.eE]+) scale=(\d+)$")
MUTATION=re.compile(
    r"^INPUTMUTATION (\\S+) max_abs=([+\\-0-9.eE]+) scale=(\\d+)$")
PRIME=re.compile(
    r"^CPALL (\S+) i=(\d+) re=([+\-0-9.eE]+) "
    r"im=([+\-0-9.eE]+) scale=(\d+)$")


def load_stages(file_path):
    lines=Path(file_path).read_text().splitlines()
    result=parse_output(file_path)
    rge={}
    prime={}
    input_mutations={}
    for line in lines:
        mut=MUTATION.fullmatch(line)
        if mut:
            name,val,scale=mut.groups()
            key=int(scale),name
            if key in input_mutations or name not in LABELS:
                raise ValueError(f"Duplicate/unrecognized input mutation {key}")
            number=float(val)
            if not math.isfinite(number) or number<0:
                raise ValueError(f"Invalid input mutation {key}")
            input_mutations[key]=number
            continue
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
    mutation_expected={(scale,label) for scale in range(5)
                       for label in LABELS}
    if set(input_mutations)!=mutation_expected:
        raise ValueError("Missing high-scale mutation rows")
    if set(rge)!=wanted or set(prime)!=wanted:
        raise ValueError(
            f"Incomplete stage diagnostics: "
            f"RGE missing={len(wanted-set(rge))}; "
            f"prime missing={len(wanted-set(prime))}")
    return result,rge,prime,input_mutations


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
        br,rge,prime,mutation=load_stages(file)
        per_scale=[]
        for scale in range(5):
            diff_entries=[
                (abs(a-b),index,order,part)
                for index in range(1,11)
                for order in range(3)
                for part in range(2)
                for a,b in [(
                    rge[scale,LABELS[0],index][2*order+part],
                    rge[scale,LABELS[1],index][2*order+part]
                )]
            ]
            rg_delta,index_max,order_max,part_max=max(diff_entries)
            primed_delta=max(abs(x-y)
                for index in range(1,11)
                for x,y in zip(prime[scale,LABELS[0],index],
                               prime[scale,LABELS[1],index]))
            repeat_rg_delta=max(
                abs(x-y)
                for index in range(1,11)
                for pair in ((LABELS[0],LABELS[2]),(LABELS[1],LABELS[3]))
                for x,y in zip(rge[scale,pair[0],index],
                               rge[scale,pair[1],index]))
            repeat_primed_delta=max(
                abs(x-y)
                for index in range(1,11)
                for pair in ((LABELS[0],LABELS[2]),(LABELS[1],LABELS[3]))
                for x,y in zip(prime[scale,pair[0],index],
                               prime[scale,pair[1],index]))
            repeat_BR_delta=max(
                abs(br[scale,pair[0]]["br"]-br[scale,pair[1]]["br"])
                for pair in ((LABELS[0],LABELS[2]),(LABELS[1],LABELS[3]))
            )
            b1=br[scale,LABELS[0]]["br"]
            b2=br[scale,LABELS[1]]["br"]
            per_scale.append({
                "scale_index":scale,
                "zee_BR_using_residual_mass300":b1,
                "zee_BR_using_residual_mass700":b2,
                "BR_absolute_difference":b1-b2,
                "BR_fractional_difference":(b1-b2)/b1,
                "maximum_post_RG_WC_difference":rg_delta,
                "post_RG_largest_difference_location":{
                    "operator_index":index_max,"perturbative_order":order_max,
                    "component":("real" if part_max==0 else "imag")
                },
                "maximum_primed_WC_difference":primed_delta,
                "max_high_scale_WC_mutation":max(
                    mutation[scale,label] for label in LABELS),
                "maximum_repeat_same_mass_post_RG_difference":repeat_rg_delta,
                "maximum_repeat_same_mass_primed_difference":repeat_primed_delta,
                "maximum_repeat_same_mass_BR_difference":repeat_BR_delta,
            })
        if any(x["maximum_repeat_same_mass_post_RG_difference"]>1e-13
               or x["maximum_repeat_same_mass_BR_difference"]>2e-12
               for x in per_scale):
            cause="SAME_MASS_REPEAT_IS_NONDETERMINISTIC_CHECK_STATE_OR_MEMORY"
        elif any(x["maximum_post_RG_WC_difference"]>1e-13
                 for x in per_scale):
            cause="POST_RG_DIFFERENCE_BETWEEN_MASS_CONTEXTS_CAUSE_NOT_ESTABLISHED"
        elif any(x["maximum_primed_WC_difference"]>1e-13
                 for x in per_scale):
            cause="PRIMED_WC_DIFFERENCE_BETWEEN_MASS_CONTEXTS"
        elif any(abs(x["BR_absolute_difference"])>2e-12
                 for x in per_scale):
            cause="BR_DIFFERENCE_WITH_IDENTICAL_POST_RG_AND_PRIMED_WCS"
        else:
            cause="NO_RESIDUAL_MASS_DIFFERENCE_DETECTED"
        status[name]={"stage_diagnosis":cause,"scales":per_scale}

    return {
        "status":"GATE_A1N_DIAGNOSTIC_ONLY_RESIDUAL_MASS_CONTEXT",
        "scope":"Unmodified and isolated SuperIso candidate outputs, no physical Zee BR",
        "source_references":source_scan(vendor_root),
        "libraries":status,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
        "next":"Check exact largest post-RG coefficient difference, mutation of "
               "high-scale arrays, and same-mass repetitions. The absence of "
               "direct mass_H tokens inside C_calculator_base1 does not "
               "establish or exclude indirect parameter dependencies. "
               "Do not call the difference a physical mass effect yet.",
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
        print("  largest differing RG entry =",row["post_RG_largest_difference_location"])
        print("  max input mutation =",row["max_high_scale_WC_mutation"])
        print("  max same-mass repeat RG diff =",row["maximum_repeat_same_mass_post_RG_difference"])
        print("  max same-mass repeat BR diff =",row["maximum_repeat_same_mass_BR_difference"])
    for name,entry in result["source_references"].items():
        print("SOURCE",name,"mass_H/THDM refs:",
              entry.get("total_mass_H_or_THDM_references","MISSING"))
    print("STATUS: Diagnostic complete; Zee BR remains unvalidated")


if __name__=="__main__":
    main()
