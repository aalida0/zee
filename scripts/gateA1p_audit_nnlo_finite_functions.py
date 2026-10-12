#!/usr/bin/env python3
"""Gate A1P: decompose remaining NNLO Type-II C7/C8 matching differences
into finite three-loop (cot^2 beta and Yukawa cross-term) coefficients.

This is a purpose-built validation diagnostic, NOT a matching patch,
a renormalization scale scan, or a physical B->Xs gamma calculation.

At a *fixed* mt(muW) input, evaluate HEPfit's original compiled
setWCbsg() with muW=mt input. Its lstmu=2 ln(muW/mt)=0, so the
returned raw C7/C8 are precisely the two independent finite
piecewise coefficients n72ct/tan^2+n72fr etc. HEPfit's actual
-20*C5 NNLO C8 basis shift must be undone first.

The original compiled SuperIso helper functions C7H2lulumt,
C7H2ldlumt, C8H2lulumt, C8H2ldlumt are evaluated at the same
x=mt(muW)^2/mH^2. SuperIso Type-II direct term is
fn_lulu(x)/tan^2 beta - fn_ldlu(x).

Run HEPfit at TWO tan(beta) values with identical mt,mH,muW to
separate the cot^2 term from the tan-independent cross term.
No HEPfit source formula is modified or recompiled.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess

from gateA1p_prepare_hepfit_matching import HEPFIT_BLOB,git_blob_sha
from gateA1p_compare_hepfit_matching import read_hepfit
from gateA1p_audit_effective_operator_basis import HEPFIT_CODE_Z,Y

MASSES=(300.,700.,1000.,2000.)
FIN=re.compile(r"^FINITE mH=([-+0-9.eE]+) op=([78]) term=(ct|fr) value=([-+0-9.eE]+)$")
INPUT=re.compile(r"^INPUT mt_fixed_GeV=([-+0-9.eE]+)$")

def read_finite(path,mt):
    lines=path.read_text().splitlines()
    if "STATUS GATE_A1P_ACTUAL_SUPERISO_THREE_LOOP_FINITE_HELPERS_NO_BR" not in lines:
        raise ValueError("Missing actual compiled SuperIso helper marker")
    inp=[INPUT.fullmatch(line) for line in lines]
    inp=[m for m in inp if m]
    if len(inp)!=1 or not math.isclose(float(inp[0][1]),mt,abs_tol=1e-12,rel_tol=0):
        raise ValueError("SuperIso finite helper top mass mismatch")
    results={}
    for line in lines:
        mat=FIN.fullmatch(line)
        if mat:
            m,op,term,value=float(mat[1]),int(mat[2]),mat[3],float(mat[4])
            key=(m,op,term)
            if key in results or not math.isfinite(value):
                raise ValueError(f"Duplicated/nonfinite SuperIso helper {key}")
            results[key]=value
    target={(m,op,term) for m in MASSES for op in (7,8) for term in ("ct","fr")}
    if set(results)!=target:
        raise ValueError(f"Missing/unexpected SuperIso finite helper values: {target^set(results)}")
    return results

def decompose(direct1,direct2,tan1,tan2):
    inv1=1./tan1**2
    inv2=1./tan2**2
    if not math.isfinite(inv1-inv2) or abs(inv1-inv2)<1e-6:
        raise ValueError("tanbeta controls are degenerate")
    ct=(direct1-direct2)/(inv1-inv2)
    fr=direct1-ct*inv1
    if not all(map(math.isfinite,(ct,fr))):
        raise ValueError("Nonfinite separated finite coefficient")
    if not math.isclose(ct*inv2+fr,direct2,rel_tol=1e-11,abs_tol=1e-11):
        raise ValueError("HEPfit tanbeta finite decomposition closure failure")
    return ct,fr

def source_hash_contract(superiso_source,a1m_provenance,
                         hepfit_source,hepfit_provenance):
    si=superiso_source.read_bytes()
    h=hepfit_source.read_bytes()
    simp=json.loads(a1m_provenance.read_text())
    hmp=json.loads(hepfit_provenance.read_text())
    if hashlib.sha256(si).hexdigest()!=simp.get("patched_wilson_sha256"):
        raise ValueError("A1M SuperIso source not pinned")
    if git_blob_sha(h)!=HEPFIT_BLOB or hmp.get("upstream_git_blob")!=HEPFIT_BLOB:
        raise ValueError("HEPfit independent source not pinned")
    text=si.decode()
    for name in ("C7H2lulumt","C7H2ldlumt","C8H2lulumt","C8H2ldlumt"):
        if not re.search(r"\bdouble\s+"+name+r"\s*\(double\s+r\)",text):
            raise ValueError(f"Original A1M SuperIso helper not found in source: {name}")
    return {
        "status":"PINNED_SUPERISO_THREE_LOOP_HELPERS_AND_HEPFIT_REFERENCE",
        "SuperIso_patched_wilson_sha256":hashlib.sha256(si).hexdigest(),
        "HEPfit_source_blob":git_blob_sha(h),
    }

def run_reference(binary,mass,tan,mt,extra_env):
    proc=subprocess.run(
        [str(binary),f"{tan:.17g}",f"{mt:.17g}",
         f"{mt:.17g}",f"{mass:.17g}"],
        check=False,text=True,capture_output=True,env=extra_env,timeout=40)
    if proc.returncode!=0:
        raise ValueError(f"HEPfit zero-log reference failed mass={mass} "
                         f"tanbeta={tan}: {proc.stderr[:1200]}")
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile("w+",suffix=".txt") as f:
        f.write(proc.stdout)
        f.flush()
        inp,vec=read_hepfit(f.name)
    if not math.isclose(inp["muW"],mt,rel_tol=0,abs_tol=1e-11):
        raise ValueError("HEPfit finite reference did not use muW=mt")
    if not math.isclose(inp["tanbeta"],tan,rel_tol=0,abs_tol=1e-11):
        raise ValueError("HEPfit finite reference tanbeta differs")
    return vec

def raw_hepfit(vec,op):
    weights=Y if op==7 else HEPFIT_CODE_Z
    return vec[2,op]-sum(w*vec[2,j] for j,w in weights.items())

# The 2026-02-01 Key4hep release used by the original AF reference.
# Search it only as a fallback if old/current LD_LIBRARY_PATH is incomplete.
# A local GATE_A1P_KEY4HEP_ROOT override can replace this release prefix.
DEFAULT_KEY4HEP_ROOT=Path(
    "/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/"
    "x86_64-almalinux9-gcc14.2.0-opt"
)

def select_existing_library_dirs(paths):
    """Return surviving real directories and missing/stale entries.

    Do NOT require all entries from the prior shell to still exist.
    The executable loader check, not existence of irrelevant directories,
    determines if an archived environment can be reused.
    """
    existing=[]
    stale=[]
    seen=set()
    for item in paths:
        name=str(item).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        if Path(name).is_dir():
            existing.append(name)
        else:
            stale.append(name)
    return existing,stale

def recover_hepfit_runtime(binary,library_paths,output_dir=None):
    """Recover minimal GSL/OpenBLAS runtime without rebuilding HEPfit.

    Keep existing directories from the original logged LD_LIBRARY_PATH
    and the present shell. Ignore stale unrelated paths. Discover actual
    GSL/OpenBLAS SONAME files in the SAME Key4hep architecture/release
    if needed; never manufacture ABI-unsafe library symlinks.
    A final ldd run must show zero missing shared libraries.
    """
    candidates=[]
    # Explicit per-library overrides receive first priority.
    for key,soname in (("GATE_A1P_GSL_LIBDIR","libgsl.so.28"),
                       ("GATE_A1P_OPENBLAS_LIBDIR","libopenblas.so.0")):
        raw=os.environ.get(key,"").strip()
        if raw:
            d=Path(raw)
            if not d.is_dir() or not (d/soname).is_file():
                raise ValueError(f"{key}={raw} does not contain {soname}")
            candidates.append(raw)

    current=os.environ.get("LD_LIBRARY_PATH","")
    candidates.extend(current.split(":"))

    if library_paths is not None and library_paths.is_file():
        content=library_paths.read_text().strip()
        if not content.startswith("LD_LIBRARY_PATH=") or "\n" in content:
            raise ValueError("Unrecognized A1P logged LD_LIBRARY_PATH format")
        candidates.extend(content[len("LD_LIBRARY_PATH="):].split(":"))

    # Discover GSL and the matching OpenBLAS in the *same* release.
    root=Path(os.environ.get("GATE_A1P_KEY4HEP_ROOT",str(DEFAULT_KEY4HEP_ROOT)))
    if root.is_dir():
        for pkg,soname in (("gsl","libgsl.so.28"),
                           ("openblas","libopenblas.so.0")):
            candidates.extend(
                str(p.parent) for libdir in ("lib","lib64")
                for p in sorted(root.glob(f"{pkg}/*/{libdir}/{soname}"))
                if p.is_file()
            )
    existing,stale=select_existing_library_dirs(candidates)
    # An executable may already resolve every dependency via system
    # loader defaults or its own RPATH, even if none of the archived
    # LD_LIBRARY_PATH directories remain. Only ldd decides success.
    env=os.environ.copy()
    env["LD_LIBRARY_PATH"]=":".join(existing)
    check=subprocess.run(
        ["ldd",str(binary.resolve())],
        env=env,text=True,capture_output=True,timeout=30,check=False)
    report=(check.stdout or "")+(check.stderr or "")
    if output_dir is not None:
        output_dir.mkdir(parents=True,exist_ok=True)
        (output_dir/"hepfit_finite_runtime_ldd.log").write_text(report)
        (output_dir/"hepfit_finite_runtime_paths.json").write_text(
            json.dumps({
                "status":"GATE_A1P_FINITE_HERMITIC_RUNTIME_RECOVERED_NOT_PHYSICS",
                "retained_library_directories":existing,
                "ignored_stale_LD_LIBRARY_PATH_entries":stale,
                "key4hep_root_searched":str(root),
                "ldd_exit_code":check.returncode,
                "ldd_missing_dependencies":(
                    re.findall(r"^\s*(\S+)\s+=>\s+not found\s*$",
                               report,re.M)),
            },indent=2)+"\n"
        )
    missing=re.findall(r"^\s*(\S+)\s+=>\s+not found\s*$",report,re.M)
    if check.returncode!=0 or missing:
        raise ValueError(
            "HEPfit runtime shared-library check failed "
            f"(ldd exit={check.returncode}, unresolved={missing}). "
            "Inspect hepfit_finite_runtime_ldd.log. Supply exact real "
            "GSL/OpenBLAS library dirs using GATE_A1P_GSL_LIBDIR / "
            "GATE_A1P_OPENBLAS_LIBDIR if necessary.")
    print("HEPFIT_RUNTIME_SHARED_LIBRARIES_RESOLVED",
          f"existing_dirs={len(existing)}",f"stale_ignored={len(stale)}")
    if stale:
        print("Ignored stale LD_LIBRARY_PATH entries:",len(stale))
    return env

def run_audit(result_path,mass_path,finite_file,binary,source_contract,library_paths):
    data=json.loads(result_path.read_text())
    inp=json.loads(mass_path.read_text())
    if inp.get("status")!="GATE_A1P_RUNNING_TOP_FROM_SUPERISO_FUNCTION_NOT_LO_INVERSION":
        raise ValueError("Require directly measured SuperIso running top mass")
    if data.get("compared_count")!=44 or len(data.get("compared_coefficients",[]))!=44:
        raise ValueError("Require original 44-row matching provenance")
    mt=float(inp["mt_muW_GeV"])
    t1=float(data["tanbeta"])
    t2=2.*t1
    mu_nominal=float(data["muW_GeV"])
    if not (math.isfinite(mt) and 100<mt<250 and t1>0 and mu_nominal>0):
        raise ValueError("Invalid A1P numerical inputs")
    finite=read_finite(finite_file,mt)
    if not binary.is_file():
        raise ValueError("Cannot locate original independently compiled HEPfit reference")
    # Runtime paths from another AF login session may include stale,
    # unrelated entries. Require ldd closure, not 100% old-path survival.
    env=recover_hepfit_runtime(binary,library_paths,binary.parent)
    original={(float(item["mass_GeV"]),int(item["order"]),item["operator"]):item
             for item in data["compared_coefficients"]}
    if len(original)!=44:
        raise ValueError("Duplicate original A1P rows")
    rows=[]
    for mass in MASSES:
        h1=run_reference(binary,mass,t1,mt,env)
        h2=run_reference(binary,mass,t2,mt,env)
        for op in (7,8):
            d1=raw_hepfit(h1,op)
            d2=raw_hepfit(h2,op)
            hct,hfr=decompose(d1,d2,t1,t2)
            sct=finite[mass,op,"ct"]
            sfr=-finite[mass,op,"fr"] # Type-II lambda_d*lambda_u=-1
            finite_diff_ct=sct-hct
            finite_diff_fr=sfr-hfr
            finite_diff=finite_diff_ct/t1**2+finite_diff_fr
            si_comb=sct/t1**2+sfr
            if abs((si_comb-d1)-finite_diff)>1e-11:
                raise ValueError(f"Finite difference closure failed mH={mass} C{op}")
            prev=original[mass,2,f"C{op}"]
            if not all(k in prev for k in ("superiso_isolated_delta",
                                          "independent_HEPfit_delta")):
                raise ValueError("Original A1P row missing")
            rows.append({
                "mass_GeV":mass,"operator":f"C{op}",
                "x_mt2_over_mH2":(mt/mass)**2,
                "HEPfit_zero_log_reference_at_tanbeta":d1,
                "HEPfit_zero_log_reference_at_double_tanbeta":d2,
                "HEPfit_finite_cotbeta2_coefficient":hct,
                "HEPfit_finite_lambda_d_lambda_u_typeII_coefficient":hfr,
                "SuperIso_compiled_finite_cotbeta2_coefficient":sct,
                "SuperIso_compiled_finite_lambda_d_lambda_u_typeII_coefficient":sfr,
                "SuperIso_minus_HEPfit_finite_cotbeta2_coefficient":finite_diff_ct,
                "SuperIso_minus_HEPfit_finite_cross_coefficient":finite_diff_fr,
                "SuperIso_minus_HEPfit_total_zero_log":finite_diff,
                "finite_cotbeta2_contribution_to_difference":finite_diff_ct/t1**2,
                "finite_cross_contribution_to_difference":finite_diff_fr,
                "HEPfit_scale_logs_zero_by_construction":True,
                "SuperIso_finite_functions_evaluated_without_matching_logs":True,
            })
    return {
        "status":"GATE_A1P_C7_C8_FINITE_THREE_LOOP_DISCREPANCY_DECOMPOSED_NOT_NNLO_VALIDATED",
        "scope":"Read-only comparison of independent finite Type-II three-loop functions "
                "at fixed x, not physical matching-scale variation or exclusion",
        "reference_source":source_contract,
        "mt_running_held_fixed_GeV":mt,
        "zero_log_matching_scale_GeV":mt,
        "previous_actual_muW_GeV":mu_nominal,
        "tanbeta_controls":[t1,t2],
        "HEPfit_C8_wrong_sign_undone":True,
        "SuperIso_library_modified":False,
        "HEPfit_source_modified":False,
        "rows":rows,
        "source_theory_correctness_established":False,
        "full_NNLO_BR_validated":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("existing-result","mass-input","superiso-finite",
                "hepfit-binary","superiso-source","a1m-provenance",
                "hepfit-source","hepfit-provenance","output"):
        p.add_argument("--"+arg,required=True,type=Path)
    p.add_argument("--library-paths",type=Path)
    a=p.parse_args()
    source=source_hash_contract(
        a.superiso_source,a.a1m_provenance,
        a.hepfit_source,a.hepfit_provenance)
    result=run_audit(a.existing_result,a.mass_input,
        a.superiso_finite,a.hepfit_binary,source,a.library_paths)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS:",result["status"])
    for row in result["rows"]:
        print(f"mH={row['mass_GeV']:.0f}",
              row["operator"],
              f"finite_ct_diff={row['finite_cotbeta2_contribution_to_difference']:.9g}",
              f"finite_cross_diff={row['finite_cross_contribution_to_difference']:.9g}",
              f"finite_total_diff={row['SuperIso_minus_HEPfit_total_zero_log']:.9g}")
    print("NOT MATCHING/BR VALIDATED; NO ZEE EXCLUSION")
    print("Wrote",a.output)

if __name__=="__main__": main()
