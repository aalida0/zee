#!/usr/bin/env python3
"""Q4 next-stage complex Zee RGE metamorphic and lepton-sector source gate.

Evaluate pinned PyR@TE-generated RGEs.py on synthetic, complex, physically
well-defined parameter tensors. No physical Zee candidate is tested.
Checks FLS2010 eq(5), independent U(1)_H2 x U(1)_chi field-rephasings,
complex-conjugation covariance, hermiticity of real scalar couplings,
and f-induced Yukawa feedback. Does NOT independently derive scalar betas.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
import traceback
from pathlib import Path
import numpy as np

from zee_section8_Q4_generated_source_limit_probe import (
    KNOWN_COUPLINGS, arg_map, evaluate, find_rges, load_generated, deviation,
)

STATUS="Q4_COMPLEX_REPHASING_AND_FLS_LEPTON_GATE_NOT_INDEPENDENT_FULL_ZEE_RGES"
MATRIX_NAMES={"Yu1","Yu2","Yd1","Yd2","Ye1","Ye2","f"}
COMPLEX_SCALAR={"l5","l6","l7","l10","m12","muZee"}
REAL_SCALAR=KNOWN_COUPLINGS - MATRIX_NAMES - COMPLEX_SCALAR
# Phi2_new = exp(+i theta) Phi2_old and chi_new=exp(+i psi) chi_old.
# Coefficients in the rewritten Lagrangian transform with these weights.
CHARGE={
    "Yu2":(+1,0),
    "Yd2":(-1,0),
    "Ye2":(-1,0),
    "f":(0,-1),
    "l5":(-2,0),
    "l6":(-1,0),
    "l7":(-1,0),
    "l10":(-1,0),
    "m12":(-1,0),
    "muZee":(-1,+1),
}
LEPTON_NAMES=("Ye1","Ye2")
QUARK_NAMES=("Yu1","Yu2","Yd1","Yd2")
ALL_NAMES=tuple(sorted(KNOWN_COUPLINGS))
SOURCE_FLS="https://arxiv.org/html/1001.2561"

def physical_complex_input(seed=20261019):
    rng=np.random.default_rng(seed)
    values=arg_map(gp=.36,g2=.65,g3=1.18)
    scales={"Yu1":.12,"Yu2":.35,"Yd1":.055,"Yd2":.05,
            "Ye1":.02,"Ye2":.035}
    for name,scale in scales.items():
        values[name]=np.matrix(scale*(rng.standard_normal((3,3))+
                                     1j*rng.standard_normal((3,3))))
    f=np.zeros((3,3),complex)
    for i,j in ((0,1),(0,2),(1,2)):
        f[i,j]=.04*(rng.normal()+1j*rng.normal())
    values["f"]=np.matrix(f-f.T)
    values.update({
        "l1":.38,"l2":.42,"l3":.13,"l4":-.05,
        "l5":.045+.025j,"l6":-.016+.032j,"l7":.012-.028j,
        "lh":.24,"l8":.13,"l9":.17,"l10":.025+.018j,
        "m1":81000.,"m2":252000.,"m12":(26000.+8000.j),
        "mchi":129000.,"muZee":220.+55.j,
    })
    if set(values)!=KNOWN_COUPLINGS:
        raise AssertionError("Incomplete complex input")
    return values

def field_rephase(values,theta,psi):
    # Keep np.matrix matrix multiplication semantics required by exporter.
    out={}
    for name,val in values.items():
        a,b=CHARGE.get(name,(0,0))
        out[name]=np.exp(1j*(a*theta+b*psi))*val if (a or b) else val
    return out

def independent_fls_lepton(yy,gp,g2):
    """FLS 2010 Eq.(5a-c), D=16*pi^2 d/dln(mu), symmetry basis."""
    G=[np.asarray(yy[x],complex) for x in ("Yd1","Yd2")]
    U=[np.asarray(yy[x],complex) for x in ("Yu1","Yu2")]
    P=[np.asarray(yy[x],complex) for x in LEPTON_NAMES]
    out=[]
    a=-9*g2*g2/4-15*gp*gp/4
    for k in range(2):
        bet=a*P[k].copy()
        for l in range(2):
            t=(3*np.trace(G[k]@G[l].conj().T+
                            U[k].conj().T@U[l])+
               np.trace(P[k]@P[l].conj().T))
            bet+=t*P[l]
            bet+=P[k]@P[l].conj().T@P[l]
            bet+=.5*P[l]@P[l].conj().T@P[k]
        out.append(bet)
    return dict(zip(LEPTON_NAMES,out))

def compare(got,reference,*,atol=2e-11,rtol=2e-8):
    # Reuses established residual accounting, but apply an explicit
    # combined tolerance; avoid treating normalized tiny-zero artifacts
    # as a physically significant antisymmetry violation.
    a=np.asarray(got,dtype=complex)
    b=np.asarray(reference,dtype=complex)
    result=deviation(a,b)
    if a.shape!=b.shape:
        return result
    absdiff=result["max_abs_difference"]
    norm=max(float(np.max(np.abs(b))),float(np.max(np.abs(a))),1e-12)
    result["pass"]=bool(absdiff <= atol+rtol*norm)
    result["tolerance"]=atol+rtol*norm
    return result

def check_covariance(module,values,theta=.43,psi=-.76):
    rephased=field_rephase(values,theta,psi)
    results={}
    for name in ALL_NAMES:
        ordinary=evaluate(module,name,values)
        transformed=evaluate(module,name,rephased)
        expected=field_rephase({name:ordinary},theta,psi)[name]
        results[name]=compare(transformed,expected)
        if name in REAL_SCALAR:
            results[name+"_realness"]=compare(ordinary.imag,0.)
    return results

def check_conjugation(module,values):
    # All real couplings and gauge coefficients are left real; all other
    # parameters and tensors are complex conjugated.
    conjugated={k:(v if k in REAL_SCALAR else np.conjugate(v))
                for k,v in values.items()}
    return {k:compare(evaluate(module,k,conjugated),
                      np.conjugate(evaluate(module,k,values)))
            for k in ALL_NAMES}

def check_lepton_limits(module,values):
    pure={**values,"f":np.matrix(np.zeros((3,3),complex))}
    reference=independent_fls_lepton(pure,pure["gp"],pure["g2"])
    rows={}
    for k in LEPTON_NAMES:
        rows["FLS_f_zero_"+k]=compare(evaluate(module,k,pure),reference[k])
    # Quark beta functions should not acquire direct one-loop f effects.
    for k in QUARK_NAMES:
        rows["quark_no_direct_f_"+k]=compare(
            evaluate(module,k,values),evaluate(module,k,pure))
    # Genuine f-mediated lepton wavefunction contribution, expected at
    # one loop for general nonzero f and both generic Pi matrices.
    # It is invariant under f -> exp(i alpha)f, and scales as |f|^2.
    phase=np.exp(.31j)
    phased={**values,"f":phase*values["f"]}
    doubled={**values,"f":2*values["f"]}
    for k in LEPTON_NAMES:
        f0=evaluate(module,k,pure)
        delta=evaluate(module,k,values)-f0
        rows["f_lepton_feedback_nonzero_"+k]={
            "pass":bool(np.max(np.abs(delta))>1e-9),
            "max_abs_f2_feedback":float(np.max(np.abs(delta))),
            "expected_generic_nonzero":True,
        }
        rows["f_feedback_phase_"+k]=compare(
            evaluate(module,k,phased)-f0,delta)
        rows["f_feedback_quadratic_"+k]=compare(
            evaluate(module,k,doubled)-f0,4*delta)
    # With only the single dimension-one Zee interaction, mu=0 is a
    # multiplicatively protected point in the unbroken one-loop theory.
    zero_mu={**values,"muZee":0.}
    rows["mu_zero_fixed_surface"]=compare(
        evaluate(module,"muZee",zero_mu),0.)
    return rows

def run_checks(module):
    values=physical_complex_input()
    group={}
    for theta,psi,label in ((.43,0.,"H2_only"),(0.,-.76,"chi_only"),
                            (.43,-.76,"combined")):
        group[label]=check_covariance(module,values,theta,psi)
    group["complex_conjugation"]=check_conjugation(module,values)
    group["lepton_FLS_and_f_feedback"]=check_lepton_limits(module,values)
    return group

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generator-output",type=Path,required=True)
    parser.add_argument("--report",type=Path,required=True)
    a=parser.parse_args()
    if a.report.exists():parser.error("Refuse to overwrite existing audit")
    record={"status":STATUS,"full_complex_Zee_RGEs_independently_validated":False,
            "physical_Zee_allowed":None,"validation_status":"FAIL_CLOSED"}
    try:
        src=find_rges(a.generator_output)
        record["RGEs_file"]=str(src.resolve())
        record["RGEs_SHA256"]=hashlib.sha256(src.read_bytes()).hexdigest()
        generated=load_generated(src)
        groups=run_checks(generated)
        record["checks"]=groups
        failed=[]
        total=0
        for group,entries in groups.items():
            for key,value in entries.items():
                total+=1
                if not value.get("pass",False):
                    failed.append(group+"/"+key)
                print("Q4_COMPLEX_CHECK",group,key,
                      "PASS" if value.get("pass",False) else "MISMATCH",
                      "abs",value.get("max_abs_difference",
                                      value.get("max_abs_f2_feedback")),
                      flush=True)
        record["checks_total"]=total
        record["checks_passed"]=total-len(failed)
        record["failed_checks"]=failed
        record["validation_status"]=(
            "SOURCE_LIMIT_AND_COVARIANCE_PASS_NOT_INDEPENDENT_FULL_ZEE"
            if not failed else "MODEL_CONVENTION_OR_GENERATOR_ISSUE")
        print("Q4_COMPLEX_CHECKS",total-len(failed),"/",total)
        print("Q4_INDEPENDENT_COMPLEX_SCALAR_BETAS_VALIDATED False")
        print("Q4_PHYSICAL_ZEE_ALLOWED UNKNOWN")
        return 0 if not failed else 2
    except Exception as exc:
        record["error"]=repr(exc)
        record["traceback"]=traceback.format_exc()
        print("Q4_COMPLEX_FAIL_CLOSED",repr(exc),file=sys.stderr)
        return 1
    finally:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
        print("Q4_COMPLEX_REPORT",a.report)

if __name__=="__main__":
    raise SystemExit(main())
