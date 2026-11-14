"""One-point native SPheno input-sensitivity experiment.

No physics parameter changes to original file or repository. Starting with
a saved failed native Zee case, vary FZEEIN and YEE2IN *separately* in
byte-preserving copies of the original SLHA input, run the source-attested
SPheno binary in fresh isolated directories, and compare matrix outputs.

If the output is invariant even after multiplying original input entries,
the native generated model is not propagating those inputs, or a boundary
condition overrides them. This does not identify the exact Fortran statement
until InputOutput_ZeeTypeII and SugraRuns_ZeeTypeII are inspected.

python -m research.full_constraints.lfv_literature_closure_2026.probe_native_yukawa_binding \
  --case /path/to/EDM3ZERO_SOURCE64_.../native-source-64-results/Zee_... \
  --work ~/zee-lfv64-serial-20261112-094549 \
  --output-root /tmp/zee-binding-probe-001
"""
from __future__ import annotations
import argparse,hashlib,json,math,re
from pathlib import Path
import numpy as np
from research.full_constraints.lfv_64_native_2026.spheno_64_source_gate import (
    split_slha,matrix_from_native,attest_compiled_nuclear_correction,
    EXPECTED_SOURCES,check_source_bundle)
from .run_repaired64_native_source import run_native_isolated
from .diagnose_native_yukawas import inspect_case,_comparison

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def scaled_matrix_entries(raw:str,stem:str,factor:float,keys:tuple[tuple[int,int],...]):
    """Multiply selected real AND imaginary entries of an original matrix.

    Keep all other control and physical input bytes, especially SPHENOINPUT
    and SMINPUTS, unaltered; only generated COPY is a nonphysical probe.
    """
    if not math.isfinite(factor) or factor<=0 or factor==1:
        raise ValueError("Need a meaningful finite positive scale factor")
    sections=re.compile(r"(?im)^\s*BLOCK\s+([A-Za-z0-9_]+)\b")
    matches=list(sections.finditer(raw))
    if not matches:raise ValueError("No SLHA blocks")
    wanted={stem.upper(),"IM"+stem.upper()}
    found=set();counts={k:0 for k in wanted}
    rebuilt=[]
    cursor=0
    for i,m in enumerate(matches):
        end=matches[i+1].start() if i+1<len(matches) else len(raw)
        rebuilt.append(raw[cursor:m.start()])
        name=m.group(1).upper()
        piece=raw[m.start():end]
        if name in wanted:
            if name in found:raise ValueError("Duplicate matrix block")
            found.add(name)
            lines=piece.splitlines(keepends=True)
            for j in range(1,len(lines)):
                text=lines[j]
                body=text.rstrip("\r\n")
                newline=text[len(body):]
                match=re.match(r"^(\s*)([1-3])\s+([1-3])\s+([+-]?(?:\d*\.)?\d+(?:[EeDd][+-]?\d+)?)(.*)$",body)
                if match and (int(match.group(2)),int(match.group(3))) in keys:
                    old=float(match.group(4).replace("D","E").replace("d","e"))
                    new=old*factor
                    if not math.isfinite(new):raise ValueError("Scaled matrix nonfinite")
                    lines[j]=(match.group(1)+match.group(2)+" "+match.group(3)+
                              f" {new:.17e}"+match.group(5)+newline)
                    counts[name]+=1
            piece="".join(lines)
        rebuilt.append(piece);cursor=end
    rebuilt.append(raw[cursor:])
    if found!=wanted or any(counts[k]!=len(keys) for k in wanted):
        raise ValueError(f"Original Yukawa input blocks incomplete: {found} {counts}")
    result="".join(rebuilt)
    # Other blocks and every non-selected matrix entry must remain unchanged.
    original=split_slha(raw,allowed_repeated=("SPHENOINPUT",))
    modified=split_slha(result,allowed_repeated=("SPHENOINPUT",))
    for name in original:
        if name not in wanted and original[name]!=modified[name]:
            raise ValueError("Probe edited unrelated native SLHA block: "+name)
    return result

def source_audit(model_dir:Path|None):
    if model_dir is None:return {"status":"NOT_REQUESTED"}
    files=("InputOutput_ZeeTypeII.f90","SugraRuns_ZeeTypeII.f90",
           "Model_Data_ZeeTypeII.f90","SPhenoZeeTypeII.f90")
    findings={}
    for name in files:
        p=model_dir/name
        if not p.is_file():
            findings[name]={"exists":False}
            continue
        lines=p.read_text(errors="replace").splitlines()
        terms=("fzeein","ye2in","fzee","ye2","lhinput")
        hits=[{"line":i+1,"source":v.strip()[:260]}
               for i,v in enumerate(lines) if any(w in v.lower() for w in terms)]
        findings[name]={"exists":True,"SHA256":digest(p),"matches":hits[:100],
                        "hits_total":len(hits),"truncated":len(hits)>100}
    return findings

def probe(case:Path,work:Path,output_root:Path,model_dir=None):
    original=inspect_case(case)
    orig_in=case/"input.in"
    orig_out=(case/"output.spc" if (case/"output.spc").is_file()
              else case/"SPheno.spc.ZeeTypeII")
    if output_root.exists():raise FileExistsError("Refuse overwrite previous probe")
    exe=work/"SPheno-4.0.5/bin/SPhenoZeeTypeII"
    receipt=work/"model-rebuild-attestation.json"
    if not exe.is_file() or not receipt.is_file():
        raise FileNotFoundError("Original precompiled verified SPheno build missing")
    att=json.loads(receipt.read_text())
    if not attest_compiled_nuclear_correction(att,exe):
        raise ValueError("Source-corrected SPheno binary attestation failed")
    original_five={k:work/"original-five"/k for k in EXPECTED_SOURCES}
    if check_source_bundle(original_five)!=EXPECTED_SOURCES:
        raise ValueError("Original ZeeTypeII Fortran sources drifted")
    output_root.mkdir(parents=True)
    result_dir=output_root/"runs"
    result_dir.mkdir()
    expected_blocks=split_slha(orig_in.read_text(),allowed_repeated=("SPHENOINPUT",))
    if "FZEEIN" not in expected_blocks or "YEE2IN" not in expected_blocks:
        raise ValueError("Only the genuine native FZEEIN/YEE2IN input schema is probed")
    baseline=split_slha(orig_out.read_text())
    f0=matrix_from_native(baseline,"FZEE");y0=matrix_from_native(baseline,"YEE2")
    probes=(
        ("FZEEIN",((1,2),(2,1)),2.0),
        ("YEE2IN",((3,3),),2.0),
    )
    rows=[]
    for stem,keys,factor in probes:
        content=scaled_matrix_entries(orig_in.read_text(),stem,factor,keys)
        inp=output_root/(stem+".in")
        inp.write_text(content)
        spc,log,metadata=run_native_isolated(exe,inp,result_dir)
        blocks=split_slha(spc.read_text())
        f=matrix_from_native(blocks,"FZEE")
        y=matrix_from_native(blocks,"YEE2")
        denominator_F=max(np.max(abs(f0)),1e-12)
        denominator_Y=max(np.max(abs(y0)),1e-12)
        relf=float(np.max(abs(f-f0))/denominator_F)
        rely=float(np.max(abs(y-y0))/denominator_Y)
        rows.append({
            "changed_input":stem,"factor":factor,"indices":keys,
            "unchanged_source_case":str(case),
            "probe_input_sha256":digest(inp),
            "native_spectrum_sha256":digest(spc),
            "delta_native_F_relative_to_baseline":relf,
            "delta_native_Ye2_relative_to_baseline":rely,
            "F_output_vs_original":_comparison(f0,f),
            "Y_output_vs_original":_comparison(y0,y),
            "spheno_execution":metadata,
            "model_parameter_input_propagation_proven":relf>1e-8 or rely>1e-8,
            "full_physical_LFV":None
        })
    result={"status":"NATIVE_BOUNDARY_INPUT_PROBE_NOT_PHYSICS","source_case":str(case),
        "source_case_input_SHA256":digest(orig_in),
        "source_case_spectrum_SHA256":digest(orig_out),
        "pinned_native_binary_SHA256":digest(exe),
        "source_generated_fortran_inspection":source_audit(model_dir),
        "original_mismatch":original,
        "probes":rows,"global_acceptance":None,"full_physical_LFV":None}
    report=output_root/"ZEE_NATIVE_YUKAWA_INPUT_BINDING_PROBE.json"
    report.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print("SOURCE_CASE",case)
    for r in rows:
        print("PROBE",r["changed_input"],"native_delta_F",r["delta_native_F_relative_to_baseline"],
            "native_delta_YEE2",r["delta_native_Ye2_relative_to_baseline"],
            "propagation",r["model_parameter_input_propagation_proven"])
    # These experiments identify sensitivity, not the mathematical origin
    # of any mismatch or a valid model-specific Yukawa boundary prescription.
    insensitive=[r["changed_input"] for r in rows
                 if not r["model_parameter_input_propagation_proven"]]
    print("INSENSITIVE_INPUT_BLOCKS",insensitive)
    for path,info in result["source_generated_fortran_inspection"].items():
        if not info.get("exists"):
            print("GENERATED_FORTRAN_MISSING",path)
        else:
            print("GENERATED_FORTRAN_HITS",path,info["hits_total"])
            for hit in info["matches"][:7]:
                print("    ",hit["line"],hit["source"])
    print("AUDIT",report)
    print("NATIVE_LFV_UNVALIDATED")
    return result

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--case",required=True,type=Path)
    a.add_argument("--work",type=Path,default=Path("~/zee-lfv64-serial-20261112-094549").expanduser())
    a.add_argument("--model-dir",type=Path,default=None,
                   help="Private SARAH generated SPheno model directory, optional")
    a.add_argument("--output-root",required=True,type=Path)
    args=a.parse_args()
    work=args.work.expanduser()
    generated=args.model_dir.expanduser() if args.model_dir else work/"SPheno-4.0.5/ZeeTypeII"
    probe(args.case.expanduser(),work,args.output_root.expanduser(),
          generated if generated.is_dir() else None)

if __name__=="__main__":main()
