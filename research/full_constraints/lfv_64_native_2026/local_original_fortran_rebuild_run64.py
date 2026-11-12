#!/usr/bin/env python3
"""Run all 64 original ZeeTypeII one-loop LFV rates in an isolated local SPheno.

REQUIRES USER'S ALREADY INSTALLED, EXACT SARAH-GENERATED FULL MODEL AND
SPheno 4.0.5.  The five verified Fortran files alone cannot compile a
standalone model. The entire original SPheno installation is copied into
a fresh work directory, then a two-sign scalar proton/neutron correction
is inserted into a COPY of the original generated model code.

The source is forced-rebuilt before any physical observable is accepted.
Source and binary SHA-256 provenance is retained in private local output.
No original code or binary is committed to GitHub.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from zipfile import ZipFile
from .spheno_64_source_gate import (
    EXPECTED_SOURCES,PRIOR_COMPILED_EXE_SHA,compile_cards,evaluate_cards,
    check_source_bundle,attest_compiled_nuclear_correction,
)
from .patch_original_nuclear_source import patch_text
from .classify_native_64_source_1loop import PATCHED_OBSERVABLE_SHA,evaluate as classify

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_orig_zip(path):
    with ZipFile(path) as z:
        names=z.namelist()
        if set(EXPECTED_SOURCES)-set(names):
            raise ValueError("Uploaded original archive is missing generated model files")
        result={}
        for name,h in EXPECTED_SOURCES.items():
            data=z.read(name)
            if sha(data)!=h:raise ValueError("Archive original model SHA changed: "+name)
            result[name]=data
        return result

def verify_generated_model_tree(model_dir,source):
    paths={
        "FlavorKit_LFV_ZeeTypeII.f90":model_dir/"Observables"/"FlavorKit_LFV_ZeeTypeII.f90",
        "FlavorKit_Observables_ZeeTypeII.f90":model_dir/"Observables"/"FlavorKit_Observables_ZeeTypeII.f90",
        "LowEnergy_ZeeTypeII.f90":model_dir/"Observables"/"LowEnergy_ZeeTypeII.f90",
        "Couplings_ZeeTypeII.f90":model_dir/"Couplings_ZeeTypeII.f90",
    }
    for name,p in paths.items():
        if not p.is_file() or sha(p.read_bytes())!=sha(source[name]):
            raise ValueError("Generated full ZeeTypeII source does NOT match original five-file archive: "+str(p))
    essentials=["Makefile","InputOutput_ZeeTypeII.f90","Model_Data_ZeeTypeII.f90",
                "SPhenoZeeTypeII.f90"]
    absent=[x for x in essentials if not (model_dir/x).exists()]
    if absent:
        raise ValueError("Original full SARAH-generated model directory incomplete: "+str(absent))
    return paths

def prepare_isolated_tree(original_spheno,generated_model,source,work):
    if work.exists():raise FileExistsError("Refuse overwrite of model private source-run directory")
    if not (original_spheno/"src"/"LoopFunctions.f90").is_file():
        raise FileNotFoundError("Need complete original SPheno-4.0.5 source tree")
    if sha((original_spheno/"src"/"LoopFunctions.f90").read_bytes())!=sha(source["LoopFunctions.f90"]):
        raise ValueError("SPheno 4.0.5 LoopFunctions differs from original compiled model source")
    original=verify_generated_model_tree(generated_model,source)
    work.mkdir(parents=True)
    target=work/"SPheno-4.0.5"
    shutil.copytree(original_spheno,target,symlinks=False)
    model=target/"ZeeTypeII"
    shutil.copytree(generated_model,model,dirs_exist_ok=True)
    copies=verify_generated_model_tree(model,source)
    obs=copies["FlavorKit_Observables_ZeeTypeII.f90"]
    corrected=patch_text(obs.read_text()).encode("utf-8")
    if sha(corrected)!=PATCHED_OBSERVABLE_SHA:
        raise ValueError("Patched observable source SHA does not match independently verified correction")
    obs.write_bytes(corrected)
    if sha(obs.read_bytes())!=PATCHED_OBSERVABLE_SHA:
        raise ArithmeticError("Corrected native source not written or changed on disk")
    private=work/"original-five"
    private.mkdir()
    paths={}
    for name,raw in source.items():
        path=private/name
        path.write_bytes(raw)
        paths[name]=path
    return target,paths

def native_build_command(jobs):
    """Build serially: SPheno 4.0.5 make recipes share one nonlocked .a.

    Caller-requested parallelism must NEVER propagate into recursive make,
    because concurrent `ar -ruc ../lib/libSPheno.a` commands truncate the
    shared archive. The public model code is not safe for parallel make.
    """
    if not isinstance(jobs,int) or not 1<=jobs<=32:
        raise ValueError("Native SPheno build jobs must be between 1 and 32")
    return ["make","-B","-j1","Model=ZeeTypeII","F90=gfortran"]

def rebuild_and_evaluate(source_json,template,source_zip,original_spheno,
                         generated_model,work,jobs=1):
    source=read_orig_zip(source_zip)
    # Reject the CI synthetic reference template. The original tree-scheme
    # SPheno input must use the original scheme and CKM/SMINPUTS convention.
    # The CI's synthetic template is NOT an experimentally or model-calibrated
    # input. Reject by its *exact original digest*, not a generic SLHA header,
    # since a valid native reference may legitimately start with MODSEL.
    if sha(template.read_bytes())=="936c146f2c1d11246a93b0f9271dbf76818ef7e68358bc744047fd89f1b2eca1":
        raise ValueError("Synthetic CI-only template cannot be used for physics; supply the validated ZeeTypeII native input")
    target,paths=prepare_isolated_tree(original_spheno,generated_model,source,work)
    build=work/"force-rebuild.log"
    # The original SPheno 4.0.5 top-level Makefile defaults to Intel
    # ifort; on Ubuntu the available compiler is GNU Fortran.  Pass
    # F90=gfortran on the *make command line* so recursive make inherits
    # the compiler choice and its matching -J (not Intel -module) flags.
    if shutil.which("gfortran") is None:
        raise FileNotFoundError("GNU Fortran gfortran required for isolated ZeeTypeII build")
    # Only the COPIED work tree is modified. A pre-existing shared archive
    # may contain stale objects from the previous compiler or interrupted
    # parallel runs; do not reuse it in the forced serial rebuild.
    archive=target/"lib"/"libSPheno.a"
    if archive.exists():
        archive.unlink()
    cmd=native_build_command(jobs)
    with build.open("w") as f:
        run=subprocess.run(cmd,cwd=target,stdout=f,stderr=subprocess.STDOUT,check=False)
    if run.returncode:
        tail="\n".join(build.read_text(errors="replace").splitlines()[-45:])
        raise RuntimeError(f"Full isolated GNU Fortran rebuild failed (exit {run.returncode}): {build}\n{tail}")
    executable=target/"bin"/"SPhenoZeeTypeII"
    if not executable.is_file():raise FileNotFoundError("Forced build did not create SPhenoZeeTypeII")
    exe_sha=sha(executable.read_bytes())
    if exe_sha==PRIOR_COMPILED_EXE_SHA:
        raise ValueError("Compiler produced identical pre-correction executable; source change not linked")
    receipt={
        "schema":"zee-2026-SPheno-original-forced-rebuild-scalar-nuclear-corrected-v1",
        "original_five_sha256":EXPECTED_SOURCES,
        "original_observable_sha256":EXPECTED_SOURCES["FlavorKit_Observables_ZeeTypeII.f90"],
        "patched_observable_sha256":sha((target/"ZeeTypeII"/"Observables"/
                                     "FlavorKit_Observables_ZeeTypeII.f90").read_bytes()),
        "binary_sha256":exe_sha,"original_binary_sha256":PRIOR_COMPILED_EXE_SHA,
        "source_zip_sha256":sha(source_zip.read_bytes()),
        "build_log_sha256":sha(build.read_bytes()),
        "force_complete_rebuild":True,"build_exit_code":run.returncode,
        "original_SPheno_installation_mutated":False,
        "original_generated_model_mutated":False,
        "historical_nuclear_scalar_proton_neutron_interchange_fixed":True,
        "modern_nuclear_matrix_elements_and_LEFT_QCD_missing":True
    }
    (work/"model-rebuild-attestation.json").write_text(
        json.dumps(receipt,allow_nan=False,sort_keys=True,indent=2)+"\n")
    cards=work/"new64-source-cards"
    compile_cards(source_json,template,cards)
    results=work/"new64-native-results"
    raw=evaluate_cards(source_json,template,cards,executable,paths,results,
                       corrected_nuclear_attestation=receipt)
    summary=classify(raw,receipt)
    out=work/"source-1loop-64-mu3e-conversion-90CL-SCOPED.json"
    out.write_text(json.dumps(summary,allow_nan=False,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_ZEETYPEII_GENERATED_LFV_64_EXECUTION_COMPLETED")
    print("MU3E_ONELOOP_90CL_BELOW",summary["n_mu3e_one_loop_below_bound"],"/64")
    print("MU_E_AU_HISTORICAL_NUCLEAR_90CL_BELOW",
          summary["n_Au_one_loop_historical_nuclear_below_bound"],"/64")
    print("FULL_PHYSICAL_LFV_UNKNOWN")
    print("PRIVATE_RESULT",out)
    return out

def resume_verified_build(source_json,template,source_zip,work):
    """Resume the already successfully compiled corrected model without make.

    Strictly verify original 5 sources, compiled binary, corrected source,
    forced-build receipt, and original build log before touching any cards.
    Never reuse an incomplete or unrelated SPheno executable.
    """
    if not work.is_dir():
        raise FileNotFoundError("No prebuilt isolated SPheno work directory: "+str(work))
    source=read_orig_zip(source_zip)
    target=work/"SPheno-4.0.5"
    executable=target/"bin"/"SPhenoZeeTypeII"
    receipt_path=work/"model-rebuild-attestation.json"
    if not receipt_path.is_file() or not executable.is_file():
        raise ValueError("No completed source-corrected SPheno build receipt and executable")
    receipt=json.loads(receipt_path.read_text())
    if receipt.get("source_zip_sha256")!=sha(source_zip.read_bytes()):
        raise ValueError("Original source archive differs from successful native build")
    buildlog=work/"force-rebuild.log"
    if not buildlog.is_file() or receipt.get("build_log_sha256")!=sha(buildlog.read_bytes()):
        raise ValueError("Original successful SPheno build log changed")
    if not attest_compiled_nuclear_correction(receipt,executable):
        raise ValueError("Native binary not compiled with verified source nuclear correction")
    corrected=target/"ZeeTypeII"/"Observables"/"FlavorKit_Observables_ZeeTypeII.f90"
    if not corrected.is_file() or sha(corrected.read_bytes())!=PATCHED_OBSERVABLE_SHA:
        raise ValueError("Native executable source tree missing exact corrected observable")
    if sha((target/"src"/"LoopFunctions.f90").read_bytes())!=EXPECTED_SOURCES["LoopFunctions.f90"]:
        raise ValueError("Native compiled SPheno Fortran loop functions not source-matched")
    unchanged={
        "FlavorKit_LFV_ZeeTypeII.f90":target/"ZeeTypeII"/"Observables"/"FlavorKit_LFV_ZeeTypeII.f90",
        "LowEnergy_ZeeTypeII.f90":target/"ZeeTypeII"/"Observables"/"LowEnergy_ZeeTypeII.f90",
        "Couplings_ZeeTypeII.f90":target/"ZeeTypeII"/"Couplings_ZeeTypeII.f90",
    }
    for name,path in unchanged.items():
        if not path.is_file() or sha(path.read_bytes())!=EXPECTED_SOURCES[name]:
            raise ValueError("Compiled model source no longer matches original: "+name)
    originals={name:work/"original-five"/name for name in EXPECTED_SOURCES}
    check_source_bundle(originals)
    for name,path in originals.items():
        if path.read_bytes()!=source[name]:
            raise ValueError("Private source copy differs from original user archive: "+name)
    # No deletion or overwrite of the prior partial/incomplete input directory.
    # If a retry fails for a separate reason, the following index is free.
    for idx in range(1,100):
        cards=work/f"new64-source-cards-retry-{idx:02d}"
        results=work/f"new64-native-results-retry-{idx:02d}"
        if not cards.exists() and not results.exists():
            break
    else:
        raise FileExistsError("Too many previous source-64 attempts; inspect work directory")
    print("ZEE_LFV64_VERIFIED_BUILD_RESUME",str(work),"INPUTS",str(cards),flush=True)
    compile_cards(source_json,template,cards)
    raw=evaluate_cards(source_json,template,cards,executable,originals,results,
                       corrected_nuclear_attestation=receipt)
    final=classify(raw,receipt)
    out=work/"source-1loop-64-mu3e-conversion-90CL-SCOPED.json"
    if out.exists():
        raise FileExistsError("Refuse overwrite of earlier validated 64 physical-screen result")
    out.write_text(json.dumps(final,allow_nan=False,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_ZEETYPEII_SOURCE64_RESUME_EXECUTION_COMPLETED",
          "MU3E",final["n_mu3e_one_loop_below_bound"],"/64",
          "AU",final["n_Au_one_loop_historical_nuclear_below_bound"],"/64",
          "FULL_LFV_UNKNOWN",flush=True)
    print("PRIVATE_RESULT",out)
    return out

def main():
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument("--source-json",type=Path,required=True,
                    help="The original 64-family zee-16x4-sourced-models.json artifact")
    pa.add_argument("--template",type=Path,required=True,
                    help="A separately validated ORIGINAL ZeeTypeII tree-scheme input")
    pa.add_argument("--original-zip",type=Path,required=True,
                    help="The original five SHA-matched Fortran source archive")
    pa.add_argument("--original-spheno",type=Path,default=None,
                    help="Full original local SPheno-4.0.5 installation")
    pa.add_argument("--generated-model",type=Path,default=None,
                    help="Full original SARAH EWSB/SPheno generated model tree")
    pa.add_argument("--work",type=Path,required=True,
                    help="New/private scratch directory; must not exist")
    pa.add_argument("--jobs",type=int,default=1,
                    help="Caller preference; SPheno 4.0.5 compilation is always forced serial (-j1) for archive safety")
    pa.add_argument("--resume-verified-build",action="store_true",
                    help="Use the completed original corrected SPheno build (SHA-verified), skip recompilation")
    a=pa.parse_args()
    if not 1<=a.jobs<=32:pa.error("jobs must be 1..32")
    if a.resume_verified_build:
        resume_verified_build(a.source_json,a.template,a.original_zip,a.work)
    else:
        if a.original_spheno is None or a.generated_model is None:
            pa.error("--original-spheno and --generated-model required for a new build")
        rebuild_and_evaluate(a.source_json,a.template,a.original_zip,
                             a.original_spheno,a.generated_model,a.work,a.jobs)
if __name__=="__main__": main()
