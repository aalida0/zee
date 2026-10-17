#!/usr/bin/env python3
"""Gate A1R: source-pinned SM and single-Type-II inclusive BR pilot.

Computes actual BR via the isolated, compiled SuperIso v5 physics kernel
bsgamma() and C_calculator_base1(), with E_gamma > 1.6 GeV.
Runs SM, vendor Type-II, and Type-II with only source-authenticated
original NNLO C3-C6/raw C7-C8 matching substituted. No patches to
SuperIso, and no extraction of excluded or allowed Zee points.

Requires previously produced original Mathematica output with 48 records.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

from gateA1q_inspect_original_mathematica import (
    PINNED_KIT_SHA256,attest_source,
)
from gateA1q_compare_original_mathematica import (
    read_authors_values,make_inputs,MASSES,
)

SOURCE_STATUS="A1R_SUPERISO_V5_BR_PILOT_NOT_FLAVOUR_EXCLUSION"
INPUT_PATTERN=re.compile(
    r"^INPUT mode=([SVA]) mass_H=([.eE0-9+-]+) "
    r"tanbeta=([.eE0-9+-]+) muW=([.eE0-9+-]+) "
    r"mu_b=([.eE0-9+-]+) mt_muW=([.eE0-9+-]+) E0_GeV=1\.6$")
BR_PATTERN=re.compile(r"^BR_B_TO_XS_GAMMA=([.eE0-9+-]+)$")
MODELS={
    "SM":("S",2000.0),
    "TypeII300":("V",300.0),
    "TypeII580":("V",580.0),
    "TypeII700":("V",700.0),
    "TypeII1000":("V",1000.0),
    "TypeII2000":("V",2000.0),
    "Original300":("A",300.0),
    "Original700":("A",700.0),
    "Original1000":("A",1000.0),
    "Original2000":("A",2000.0),
}
REFERENCE_SM={"source":"Misiak, Rehman, Steinhauser 2020, arXiv:2002.01548",
              "B_SM":3.40e-4,"sigma_theory":0.17e-4,
              "photon_cut_GeV":1.6}
HISTORICAL_BOUND={
    "source":"Misiak and Steinhauser EPJC77 (2017) 201",
    "type_II_mass_limit_range_GeV_95CL":[570,800],
    "warning":"Historical statistical bounds, NOT a calibration target or new exclusion",
}

def finite(x):
    n=float(x)
    if not math.isfinite(n): raise ValueError("Nonfinite BR input")
    return n

def make_author_reference_control(directory,values,inp):
    directory.mkdir(parents=True,exist_ok=True)
    files={}
    for m in MASSES:
        content=(
            "A1R_AUTHOR_NNLO 1\n"
            f"SHA256 {PINNED_KIT_SHA256}\n"
            f"MASS {m}\n"
            f"MUW {inp['mu_GeV']:.17g}\n"
            f"MT {inp['mt_GeV']:.17g}\n"
            f"TANBETA {inp['tanbeta']:.17g}\n"
            "C2 "+
            " ".join(f"{values[m,ord,op]:.17g}"
                     for ord,op in ((2,3),(2,4),(2,5),(2,6),
                                    (3,7),(3,8)))+"\n"
        )
        p=directory/f"author_c2_m{m}.txt"
        p.write_text(content)
        files[m]=p
    return files

def check_superiso_source(root,source_manifest):
    root=Path(root)
    manifest=json.loads(Path(source_manifest).read_text())
    target=root/"src"/"wilson.c"
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    if digest!=manifest.get("patched_wilson_sha256"):
        raise ValueError("SuperIso A1M Wilson source hash changed")
    bsg=root/"src"/"bsgamma.c"
    code=bsg.read_text()
    if not re.search(r"double\s+E0\s*=\s*1\.6\s*;",code):
        raise ValueError("SuperIso photon energy cut changed from 1.6GeV")
    if not re.search(r"double\s+bsgamma\s*\(",code):
        raise ValueError("Unrecognized SuperIso physical observable source")
    # A fixed-argument source regex incorrectly rejects valid vendor
    # versions. Detect any REAL CW_calculator() call inside bsgamma()
    # (not its wrapper), and record whether it is present. For this
    # *single charged-Higgs* comparison the actual Wilson vectors are
    # passed explicitly to bsgamma(), so an absent internal reload is
    # not grounds for failing the observable pilot. The two-state Zee
    # implementation must audit any internal Kt0 dependence separately.
    clean=re.sub(r'/\*.*?\*/|//[^\n]*', ' ', code, flags=re.S)
    start=re.search(r'\bdouble\s+bsgamma\s*\(',clean)
    end=re.search(r'\bdouble\s+bsgamma_calculator\s*\(',clean)
    if start is None or end is None or end.start()<=start.start():
        raise ValueError("Cannot delimit pinned SuperIso bsgamma() body")
    observable_body=clean[start.end():end.start()]
    internal_reload=bool(re.search(r'\bCW_calculator\s*\(',observable_body))
    return {
        "A1M_patched_wilson_SHA256":digest,
        "SuperIso_bsgamma_c_SHA256":
            hashlib.sha256(bsg.read_bytes()).hexdigest(),
        "Egamma_cut_GeV":1.6,
        "uses_unmodified_bsgamma_kernel":True,
        "bsgamma_internal_CW_reload_detected":internal_reload,
        "warning_internal_CW_reload":(
            "CW_calculator() call found inside bsgamma(); its LO "
            "single-charged-Higgs matching must remain consistent, "
            "and two-state Zee mode requires a separate Kt0 audit."
            if internal_reload else
            "No CW_calculator() call found inside bsgamma(); do not "
            "assume a matching reload, and explicitly audit the "
            "nonperturbative part before two-state Zee mode."
        ),
    }

def compile_pilot(root,output,driver_source,make_if_missing=False):
    root=Path(root)
    # SuperIso v5 uses src/libsuperiso.a (not the old SuperIso
    # v3-era root/libisospin.a). Gate A1P already compiled/runs
    # against this exact isolated A1M archive.
    lib=root/"src"/"libsuperiso.a"
    if not lib.is_file() and make_if_missing:
        vendor_makefile=root/"src"/"Makefile"
        if vendor_makefile.is_file():
            try:
                subprocess.run(["make","-C",str(root/"src"),"libsuperiso.a"],
                               check=True,timeout=180)
            except subprocess.CalledProcessError as exc:
                raise ValueError(
                    "The isolated A1M SuperIso v5 src/Makefile could not "
                    "rebuild src/libsuperiso.a; preserve the existing "
                    "pinned A1M library and inspect the build error"
                ) from exc
    if not lib.is_file():
        raise ValueError(
            f"SuperIso v5 isolated A1M library absent: {lib}. "
            "A1P uses src/libsuperiso.a; verify the existing A1M build "
            "instead of substituting a different SuperIso version.")
    # The archive hash is recorded, and obvious stale builds are
    # rejected before linking. An archive SHA alone is not a proof that
    # it was rebuilt from the pinned current source.
    newest_source=max((root/"src"/"wilson.c").stat().st_mtime_ns,
                      (root/"src"/"bsgamma.c").stat().st_mtime_ns)
    if lib.stat().st_mtime_ns < newest_source:
        raise ValueError(
            "SuperIso libisospin.a is older than pinned Wilson/BR source; "
            "rebuild the pinned isolated A1M src/libsuperiso.a first using its original src/Makefile")
    cc=shutil.which("gcc")
    if cc is None:
        raise ValueError("C compiler gcc unavailable")
    output.parent.mkdir(parents=True,exist_ok=True)
    # Link the EXACT checked archive rather than relying on the
    # linker's shared-vs-static -lisospin selection.
    cmd=[cc,"-O2","-std=gnu99","-Wall","-Wextra",
         "-I"+str(root/"src"),str(driver_source),
         str(lib),"-lm","-o",str(output)]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=90,
                        check=False)
    if proc.returncode:
        raise ValueError("Gate A1R C observable-driver compilation failed "
                         f"stdout={proc.stdout[-1500:]} stderr={proc.stderr[-3500:]}")
    return {
        "library_SHA256":hashlib.sha256(lib.read_bytes()).hexdigest(),
        "driver_SHA256":
            hashlib.sha256(Path(driver_source).read_bytes()).hexdigest(),
        "compiler_command":cmd,
        "compiler_stdout_stderr_excerpt":(proc.stdout+proc.stderr)[-2500:],
    }

def read_br_output(raw,mode,m,tan):
    lines=raw.splitlines()
    if lines.count("STATUS "+SOURCE_STATUS)!=1:
        raise ValueError("Missing SuperIso BR driver authenticity marker")
    infos=[INPUT_PATTERN.fullmatch(line) for line in lines]
    infos=[m for m in infos if m is not None]
    brs=[BR_PATTERN.fullmatch(line) for line in lines]
    brs=[m for m in brs if m is not None]
    if len(infos)!=1 or len(brs)!=1:
        raise ValueError("Missing/duplicated SuperIso BR or input line")
    entry=infos[0]
    if entry[1]!=mode or not math.isclose(float(entry[2]),m,abs_tol=1e-7) \
       or not math.isclose(float(entry[3]),tan,abs_tol=1e-12,rel_tol=1e-12):
        raise ValueError("Output mode/mass/tanbeta mismatch")
    value=finite(brs[0][1])
    if value<=0 or value>0.01:
        raise ValueError("SuperIso physical BR is outside sanity range")
    return {"mode":mode,"mH_GeV":m,"tanbeta":tan,
            "muW_GeV":finite(entry[4]),
            "mu_b_GeV":finite(entry[5]),
            "mt_muW_GeV":finite(entry[6]),
            "Egamma_cut_GeV":1.6,
            "BR_B_to_Xs_gamma":value}

def audit_points(data,reference,provenance,logfile):
    if set(data)!=set(MODELS):
        raise ValueError("Missing SuperIso SM or TypeII pilot controls")
    sm=data["SM"]["BR_B_to_Xs_gamma"]
    if not 2.5e-4<sm<4.5e-4:
        raise ValueError(
            "SuperIso SM result far from published NNLO SM band; "
            "do not proceed to flavour exclusions")
    vals={}
    for key,(mode,mass) in MODELS.items():
        x=data[key]
        if not math.isclose(x["mH_GeV"],mass,rel_tol=1e-12):
            raise ValueError("Changed pilot charged-Higgs mass")
        vals[key]=x["BR_B_to_Xs_gamma"]
    # Always compare the vendor and author-matched full BR at the
    # same mass BEFORE considering any experimental interval.
    deltas={str(int(m)): {
        "vendor_BR":vals[f"TypeII{int(m)}"],
        "original_NNLO_matched_BR":vals[f"Original{int(m)}"],
        "original_minus_vendor":vals[f"Original{int(m)}"]-
                                 vals[f"TypeII{int(m)}"],
        "relative_delta":(vals[f"Original{int(m)}"]-
                          vals[f"TypeII{int(m)}"])/
                          vals[f"TypeII{int(m)}"],
    } for m in MASSES}
    return {
        "status":"GATE_A1R_SINGLE_TYPEII_OBSERVABLE_BR_PILOT_"
                 "AWAITING_INDEPENDENT_ERROR_BUDGET",
        "scope":"Actual SuperIso-v5 inclusive BR with isolated A1M C kernel",
        "published_SM_control":REFERENCE_SM,
        "historical_TypeII_bound_reference":HISTORICAL_BOUND,
        "SM_model_BR":sm,
        "SM_minus_published_reference":sm-REFERENCE_SM["B_SM"],
        "SM_published_theory_sigmas":
             (sm-REFERENCE_SM["B_SM"])/REFERENCE_SM["sigma_theory"],
        "SM_reasonable_magnitude_only":True,
        "TypeII_control_points":data,
        "source_author_vs_vendor_BR_differences":deltas,
        "source_provenance":provenance,
        "raw_logs_path":str(logfile),
        "full_NNLO_B_to_Xs_gamma_precision_validated":False,
        "experimental_likelihood_calibrated":False,
        "Zee_two_state_BR_calculated":False,
        "Zee_model_allowed_or_excluded":None,
        "notes":[
            "Published 2017 charged-Higgs bound is methodological reference; "
            "do not infer exclusion by scanning crosses of central BR alone.",
            "Our original source-pinned NNLO coefficient cross-check "
            "is not a published independent full NNLO BR implementation.",
            "Fixed SuperIso E_gamma=1.6GeV and legacy SM input scheme "
            "remain subject to quantitative systematic-error audit.",
            "Leptonic full-Zee neutrino/LFV constraints are not included.",
        ],
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vendor-root",required=True,type=Path)
    ap.add_argument("--a1m-provenance",required=True,type=Path)
    ap.add_argument("--authors-source",required=True,type=Path)
    ap.add_argument("--kit-provenance",required=True,type=Path)
    ap.add_argument("--authors-values",required=True,type=Path)
    ap.add_argument("--existing-result",required=True,type=Path)
    ap.add_argument("--output-dir",required=True,type=Path)
    ap.add_argument("--make-if-missing",action="store_true")
    ap.add_argument("--prepare-only",action="store_true")
    a=ap.parse_args()
    _,sha,_=attest_source(a.authors_source,a.kit_provenance)
    original=read_authors_values(a.authors_values)
    reference=json.loads(a.existing_result.read_text())
    inp=make_inputs(reference)
    source_checks=check_superiso_source(a.vendor_root,a.a1m_provenance)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    controls=make_author_reference_control(
        a.output_dir/"reference",original,inp)
    summary={
        "source_checks":source_checks,
        "original_kit_sha256":sha,
        "author_control_files":{
            str(int(m)):str(f) for m,f in controls.items()},
        "status":"GATE_A1R_ORIGINAL_MATCHING_INPUTS_PREPARED_NOT_OBSERVABLE_VALIDATED",
    }
    driver=Path(__file__).with_name("gateA1r_superiso_br_pilot.c")
    binary=a.output_dir/"gateA1r_br_pilot"
    if a.prepare_only:
        (a.output_dir/"pilot_preflight.json").write_text(
            json.dumps(summary,indent=2)+"\n")
        print("STATUS",summary["status"])
        print("A1M_SUPERISO_SHA256",source_checks["A1M_patched_wilson_SHA256"])
        print("REFERENCE_KIT_SHA256",sha)
        print("AUTHOR_CONTROLS_WRITTEN",len(controls))
        print("OBSERVABLE_CALCULATED False")
        return
    provenance=compile_pilot(a.vendor_root,binary,driver,a.make_if_missing)
    summary["compiled_binary_provenance"]=provenance
    out={}
    logs=[]
    for key,(mode,m) in MODELS.items():
        command=[str(binary.resolve()),mode,str(int(m)),
                 f"{inp['tanbeta']:.17g}"]
        if mode=="A":
            command.append(str(controls[m].resolve()))
        proc=subprocess.run(command,text=True,capture_output=True,
                            timeout=90,check=False)
        if proc.returncode:
            raise ValueError(f"BR driver failed case={key} "
                             f"code={proc.returncode} "
                             f"stdout={proc.stdout[-1700:]} "
                             f"stderr={proc.stderr[-1700:]}")
        out[key]=read_br_output(proc.stdout,mode,m,inp["tanbeta"])
        logs.append("CASE "+key+"\n"+proc.stdout)
        if proc.stderr:
            logs.append("STDERR "+key+"\n"+proc.stderr)
    log=a.output_dir/"br_raw_driver_output.log"
    log.write_text("\n".join(logs))
    report=audit_points(out,reference,summary,log)
    target=a.output_dir/"gateA1r_br_pilot.json"
    target.write_text(json.dumps(report,indent=2)+"\n")
    print("STATUS",report["status"])
    print("SM_BR",f"{report['SM_model_BR']:.11g}",
          "published_SM_2020",REFERENCE_SM["B_SM"])
    for key,vals in report["source_author_vs_vendor_BR_differences"].items():
        print("MASS",key,"vendor_BR",f"{vals['vendor_BR']:.11g}",
              "original_C2_BR",f"{vals['original_NNLO_matched_BR']:.11g}",
              "original_minus_vendor",f"{vals['original_minus_vendor']:.11g}")
    print("FULL_NNLO_PRECISION_VALIDATED",False)
    print("ZEE_EXCLUSION_CALCULATED",False)
    print("Wrote",target)

if __name__=="__main__":
    main()
