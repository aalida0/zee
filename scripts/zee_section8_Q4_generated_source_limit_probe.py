#!/usr/bin/env python3
"""Q4 first *numerical source-limit* gate for generated PyR@TE Zee RGEs.

Uses the existing PyR@TE-generated RGEs.py (never run.py).
Compares gauge one-loop coefficients, restricted real antisymmetric f
(Kanemura 2001 A13), and quark Yukawa f=0 limit (FLS 2010 Eqs. 3,4).
NO guesses, fitting, re-normalization, collider exclusions or UV validation.
A mismatch is a PHYSICS/CONVENTION INVESTIGATION result, not a reason to
silently rescale beta functions.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
import sys
import traceback
from pathlib import Path

import numpy as np

from zee_section8_Q2e_kanemura2001_reduced_f_RGE import beta_f_matrix
from zee_section8_quark_alignment_one_loop_gate import beta_quarks_2hdm

STATUS="Q4_SOURCE_LIMIT_PROBE_NOT_FULL_COMPLEX_ZEE_RGE_OR_ALLOWED"
KNOWN_COUPLINGS=set(
    "gp g2 g3 Yu1 Yu2 Yd1 Yd2 Ye1 Ye2 f "
    "l1 l2 l3 l4 l5 l6 l7 lh l8 l9 l10 m1 m2 m12 mchi muZee".split()
)
GAUGE={"gp":22/3,"g2":-3.,"g3":-7.}
PARAMETER_EXCEPTIONS={"nLoop"}

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def find_rges(root:Path)->Path:
    hits=list(root.rglob("RGEs.py"))
    if len(hits)!=1:
        raise ValueError(f"Expected one RGEs.py in {root}, found {len(hits)}")
    if hits[0].parent.name!="PythonOutput":
        raise ValueError(f"Wrong generated RGE path {hits[0]}")
    return hits[0]

def load_generated(path:Path):
    """Load exactly generated beta definitions. Never load generated run.py."""
    spec=importlib.util.spec_from_file_location("_q4_pinned_generated_rges",str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load generated RGE functions")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def arg_map(gp=.36,g2=.65,g3=1.18,f=None,yy=None):
    if yy is None:
        yy={k:np.matrix(np.zeros((3,3),complex))
            for k in ("Yu1","Yu2","Yd1","Yd2","Ye1","Ye2")}
    if f is None:f=np.matrix(np.zeros((3,3),complex))
    kw={name:0. for name in KNOWN_COUPLINGS}
    kw.update({k:np.matrix(v,copy=True) for k,v in yy.items()})
    kw.update({"gp":gp,"g2":g2,"g3":g3,"f":np.matrix(f)})
    return kw

def evaluate(module,name,values):
    fn=getattr(module,"beta_"+name,None)
    if not callable(fn):
        raise ValueError(f"Generated beta_{name} is missing")
    signature=inspect.signature(fn)
    unexpected=set(signature.parameters)-KNOWN_COUPLINGS-PARAMETER_EXCEPTIONS
    if unexpected:
        raise ValueError(f"Unmapped parameters for beta_{name}: {sorted(unexpected)}")
    arguments={key: (1 if key=="nLoop" else values[key])
               for key in signature.parameters}
    raw=fn(**arguments)
    val=np.asarray(raw,dtype=complex)
    if not np.isfinite(val).all():
        raise ValueError(f"Nonfinite beta_{name} result")
    return val

def deviation(got,ref):
    a=np.asarray(got,complex);b=np.asarray(ref,complex)
    if a.shape!=b.shape:
        return {"shape_mismatch":[list(a.shape),list(b.shape)],
                "max_abs_difference":None,"normalized_difference":None,
                "pass":False}
    delta=float(np.max(np.abs(a-b)))
    scale=max(1e-12,float(np.max(np.abs(a))),float(np.max(np.abs(b))))
    rel=delta/scale
    return {"max_abs_difference":delta,"normalized_difference":rel,
            "pass":bool(rel<1e-8 or delta<1e-11),
            "shape":list(a.shape)}

def run_checks(module):
    rows={}
    gvals=arg_map()
    for name,coefficient in GAUGE.items():
        got=evaluate(module,name,gvals)
        expected=np.asarray(coefficient*gvals[name]**3,complex)
        rows["gauge_"+name]=deviation(got,expected)
    antisym=np.zeros((3,3),float)
    antisym[0,1]=.11
    antisym[0,2]=-.08
    antisym[1,2]=.06
    antisym=antisym-antisym.T
    realf=np.matrix(antisym)
    vals=arg_map(f=realf)
    f_beta=evaluate(module,"f",vals)
    expected_f=beta_f_matrix(antisym,vals["gp"],vals["g2"])
    rows["Kanemura_A13_restricted_real_f"]=deviation(f_beta,expected_f)
    rows["real_f_beta_antisymmetry"]=deviation(f_beta+f_beta.T,np.zeros((3,3)))
    complexf=antisym.astype(complex).copy()
    complexf[0,1]*=(1+.7j)
    complexf[0,2]*=(1-.2j)
    complexf[1,2]*=(1+.35j)
    complexf=np.triu(complexf,1)
    complexf=complexf-complexf.T
    complex_beta=evaluate(module,"f",arg_map(f=np.matrix(complexf)))
    rows["complex_f_beta_antisymmetry"]=deviation(
        complex_beta+complex_beta.T,np.zeros((3,3)))
    nof=evaluate(module,"f",arg_map())
    rows["f_zero_is_fixed_point"]=deviation(nof,np.zeros((3,3)))
    rng=np.random.default_rng(20261019)
    yy={}
    for name,scale in (("Yu1",.12),("Yu2",.4),("Yd1",.065),
                       ("Yd2",.06),("Ye1",.02),("Ye2",.025)):
        yy[name]=scale*(rng.standard_normal((3,3))+1j*rng.standard_normal((3,3)))
    bg,bu=beta_quarks_2hdm(
        (yy["Yd1"],yy["Yd2"]),(yy["Yu1"],yy["Yu2"]),
        (yy["Ye1"],yy["Ye2"]),gp=.36,g2=.65,g3=1.18)
    expected={"Yd1":bg[0],"Yd2":bg[1],"Yu1":bu[0],"Yu2":bu[1]}
    for name,ref in expected.items():
        got=evaluate(module,name,arg_map(yy=yy))
        rows["FLS_f_zero_"+name]=deviation(got,ref)
    return rows

def signatures(path):
    tree=ast.parse(path.read_text())
    return {
        node.name:[a.arg for a in node.args.args]
        for node in tree.body if isinstance(node,ast.FunctionDef)
        and node.name.startswith("beta_")
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generator-output",type=Path,required=True)
    parser.add_argument("--report",type=Path,required=True)
    options=parser.parse_args()
    if options.report.exists():
        parser.error("Refuse overwrite of source-limit result")
    result={"status":STATUS,"complete_complex_Zee_RGE_validated":False,
            "full_Zee_allowed":None,"comparison_result":"FAIL_CLOSED"}
    try:
        src=find_rges(options.generator_output)
        result["RGEs_py"]=str(src.resolve())
        result["RGEs_py_SHA256"]=sha256(src)
        result["beta_signatures"]=signatures(src)
        mod=load_generated(src)
        checks=run_checks(mod)
        result["checks"]=checks
        passed=sum(entry.get("pass",False) for entry in checks.values())
        result["comparisons_passed"]=passed
        result["comparisons_total"]=len(checks)
        mismatch=[name for name,entry in checks.items() if not entry.get("pass")]
        result["mismatched_limits"]=mismatch
        result["comparison_result"]=(
            "ALL_TESTED_LIMITS_MATCH_BUT_FULL_ZEE_UNVALIDATED"
            if not mismatch else "SOURCE_LIMIT_MISMATCH_INVESTIGATE_CONVENTIONS")
        for key,entry in checks.items():
            print("Q4_SOURCE",key,"PASS" if entry["pass"] else "MISMATCH",
                  "DIFFERENCE",entry.get("normalized_difference"),flush=True)
        print("Q4_TESTED_LIMITS",passed,"/",len(checks),flush=True)
        print("Q4_FULL_ZEE_BETAS_INDEPENDENTLY_VALIDATED False",flush=True)
        return 0 if not mismatch else 2
    except Exception as exc:
        result["error"]=repr(exc)
        result["traceback"]=traceback.format_exc()
        print("Q4_SOURCE_LIMIT_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        options.report.parent.mkdir(parents=True,exist_ok=True)
        options.report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("Q4_SOURCE_LIMIT_REPORT",options.report,flush=True)

if __name__=="__main__":
    raise SystemExit(main())
