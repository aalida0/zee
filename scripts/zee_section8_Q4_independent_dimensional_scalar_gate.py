#!/usr/bin/env python3
"""Q4v11 independent one-loop PURE-SCALAR dimensionful general-Zee RGEs.

Use unbroken 10-real-field V=V2+V3+V4, with
V2=m1*x+m2*y+mchi*s-2 Re(m12*z)
V3=2 Re[muZee*(Phi1^1 Phi2^2-Phi1^2 Phi2^1)*chi.conjugate()]
V4 as in the validated general Zee model.

16*pi² beta(V)|scalar = 1/2 Tr[H(V)^2].
H=H2 (constant)+H3 (linear in fields)+H4 (quadratic).
Quadratic counterterm: Tr(H2 H4)+1/2 Tr(H3²).
Cubic counterterm: Tr(H3 H4).
Project separately onto five real V2 components (m1,m2,mchi,
Re(m12),Im(m12)) and two real V3 components (Re(mu),Im(mu)).

This is an INDEPENDENT scalar-only crosscheck of existing PyR@TE
beta_m1/m2/m12/mchi/muZee. Excludes gauge, lepton f, quark/lepton
Yukawa contributions and complete complex Zee UV RGE acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import traceback
from itertools import permutations
from pathlib import Path
import numpy as np

from zee_section8_Q4_independent_scalar_hessian_gate import (
    A,invariants,hessian,tensor_for_quartics,quartic_projection,
    synthetic_quartics,
)
from zee_section8_Q4_generated_source_limit_probe import (
    arg_map,evaluate,find_rges,load_generated,
)

STATUS="Q4_INDEPENDENT_SCALAR_ONLY_DIMENSIONFUL_BETA_NOT_FULL_ZEE"
MASS_NAMES=("m1","m2","mchi","m12")
DIMENSIONFUL_NAMES=("m1","m2","m12","mchi","muZee")
BASIS_NAMES=("m1","m2","mchi","m12_re","m12_im","mu_re","mu_im")
COMPLEX_NAMES=frozenset(("m12","muZee"))

def source_dimensions(masses,mu):
    return {**masses,"muZee":mu}

def potential_quadratic(phi,masses):
    x,y,s,zr,zi=invariants(phi)
    m12=complex(masses.get("m12",0.))
    return float(masses.get("m1",0.)*x+masses.get("m2",0.)*y+
                 masses.get("mchi",0.)*s-2*(m12.real*zr-m12.imag*zi))

def potential_cubic(phi,mu):
    phi=np.asarray(phi,float)
    p1=(phi[0:4:2]+1j*phi[1:4:2])/np.sqrt(2)
    p2=(phi[4:8:2]+1j*phi[5:8:2])/np.sqrt(2)
    chi=(phi[8]+1j*phi[9])/np.sqrt(2)
    return float(2*np.real(mu*(p1[0]*p2[1]-p1[1]*p2[0])*chi.conjugate()))

def quadratic_hessian(masses):
    m12=complex(masses.get("m12",0.))
    coeff=np.array([
        masses.get("m1",0.),masses.get("m2",0.),
        masses.get("mchi",0.),-2*m12.real,2*m12.imag],float)
    return np.einsum("a,aij->ij",coeff,A)

def cubic_tensor(mu):
    # V3=(1/6) T_ijk phi_i phi_j phi_k; i in Phi1,
    # j in Phi2, k in chi. The 6 permutations have T_ijk equal
    # to the polynomial monomial coefficient.
    T=np.zeros((10,10,10),float)
    c=complex(mu)
    for i in range(4):
        ai=i//2
        ai_complex=(1j if i%2 else 1)/np.sqrt(2)
        for j in range(4,8):
            bj=(j-4)//2
            if ai==bj:
                continue
            bj_complex=(1j if (j-4)%2 else 1)/np.sqrt(2)
            epsilon=1 if (ai,bj)==(0,1) else -1
            for k in (8,9):
                singlet_complex=(-1j if k==9 else 1)/np.sqrt(2)
                monomial=2*np.real(
                    c*epsilon*ai_complex*bj_complex*singlet_complex)
                for indices in permutations((i,j,k)):
                    T[indices]=monomial
    return T

def cubic_hessian(phi,mu):
    return np.einsum("ijk,k->ij",cubic_tensor(mu),phi)

def degree2_and3_counterterms(phi,quartics,masses,mu):
    H4=hessian(phi,tensor_for_quartics(quartics))
    H3=cubic_hessian(phi,mu)
    H2=quadratic_hessian(masses)
    degree2=float(np.trace(H2@H4)+.5*np.trace(H3@H3))
    degree3=float(np.trace(H3@H4))
    return degree2,degree3

def projected_bases(fields):
    phi=np.asarray(fields,float)
    if phi.ndim!=2 or phi.shape[1]!=10 or not np.isfinite(phi).all():
        raise ValueError("Require N x 10 finite scalar backgrounds")
    quadratic=np.zeros((len(phi),5),float)
    cubic=np.zeros((len(phi),2),float)
    for n,p in enumerate(phi):
        quadratic[n]=(
            potential_quadratic(p,{"m1":1}),
            potential_quadratic(p,{"m2":1}),
            potential_quadratic(p,{"mchi":1}),
            potential_quadratic(p,{"m12":1}),
            potential_quadratic(p,{"m12":1j}),
        )
        cubic[n]=(potential_cubic(p,1.),potential_cubic(p,1j))
    condition={}
    for label,B,n in (("quadratic",quadratic,5),("cubic",cubic,2)):
        rank=np.linalg.matrix_rank(B)
        singular=np.linalg.svd(B,compute_uv=False)
        c=float(singular[0]/singular[-1]) if singular[-1]>0 else float("inf")
        if rank!=n or c>1e5:
            raise ValueError(f"{label} projection singular rank {rank} cond {c}")
        condition[label]=c
    return quadratic,cubic,condition

def independent_dimensionful_scalar_beta(quartics,masses,mu,fields,design=None):
    if design is None:design=projected_bases(fields)
    quadratic,cubic,condition=design
    rhs=np.array([degree2_and3_counterterms(p,quartics,masses,mu)
                  for p in fields])
    quad,_,_,_=np.linalg.lstsq(quadratic,rhs[:,0],rcond=None)
    cub,_,_,_=np.linalg.lstsq(cubic,rhs[:,1],rcond=None)
    e2=float(np.max(abs(quadratic@quad-rhs[:,0]))/max(1.,np.max(abs(rhs[:,0]))))
    e3=float(np.max(abs(cubic@cub-rhs[:,1]))/max(1.,np.max(abs(rhs[:,1]))))
    if e2>1e-10 or e3>1e-10:
        raise ValueError(f"Dimensionful beta projection not closed e2={e2} e3={e3}")
    betas={
        "m1":float(quad[0]),"m2":float(quad[1]),
        "mchi":float(quad[2]),"m12":complex(quad[3],quad[4]),
        "muZee":complex(cub[0],cub[1]),
    }
    return betas,{
        "quadratic_residual":e2,"cubic_residual":e3,
        "condition_numbers":condition,
    }

def compare_generator(mod,quartics,masses,mu,expected):
    args=arg_map(gp=0.,g2=0.,g3=0.)
    args.update(quartics)
    args.update(masses)
    args["muZee"]=mu
    baseline=arg_map(gp=0.,g2=0.,g3=0.)
    baseline.update(quartics)
    results={}
    for k in DIMENSIONFUL_NAMES:
        got=np.asarray(evaluate(mod,k,args)-evaluate(mod,k,baseline),complex)
        if got.size!=1:
            raise ValueError(f"beta_{k} must be scalar, got {got.shape}")
        got=complex(got.reshape(-1)[0])
        ref=complex(expected[k])
        diff=float(abs(got-ref))
        scale=max(1.,abs(got),abs(ref))
        results[k]={
            "pass":bool(diff<=3e-9*scale),
            "abs_difference":diff,"scaled_difference":float(diff/scale),
            "generated_re_im":[got.real,got.imag],
            "independent_re_im":[ref.real,ref.imag]
        }
    return results

def run_cases(mod):
    rng=np.random.default_rng(20261019)
    fields=rng.normal(size=(128,10))
    basis=projected_bases(fields)
    cases={
        "only_doublet1_mass_and_lambda":(
            {"l1":.41},{"m1":81000.},0.),
        "only_charged_singlet_mass_and_lambda":(
            {"lh":.31},{"mchi":100000.},0.),
        "only_complex_mu_no_quartics":(
            {},{},220.+45j),
        "only_complex_m12_general_quartics":(
            synthetic_quartics(20261019),{"m12":26000.+8000j},0.),
        "general_real_masses_complex_mu":(
            synthetic_quartics(20261020),
            {"m1":-8000.,"m2":151000.,"mchi":137000.},190.+42j),
        "full_complex_seed0":(
            synthetic_quartics(20261020),
            {"m1":81000.,"m2":252000.,"mchi":129000.,
             "m12":26000.+8000.j},220.+55j),
        "full_complex_seed1":(
            synthetic_quartics(20261021),
            {"m1":-15100.,"m2":170000.,"mchi":81000.,
             "m12":-18300.+9500j},-330.+73j),
    }
    out={}
    for label,(quartics,masses,mu) in cases.items():
        independent,metrics=independent_dimensionful_scalar_beta(
            quartics,masses,mu,fields,basis)
        comparisons=compare_generator(mod,quartics,masses,mu,independent)
        bad=[k for k,v in comparisons.items() if not v["pass"]]
        out[label]={
            "projection":metrics,"mismatches":bad,"comparisons":comparisons,
            "source_betas_re_im":{k:[complex(v).real,complex(v).imag]
                                  for k,v in independent.items()},
        }
        print("Q4_DIM_SCALAR",label,
              "PASS" if not bad else "MISMATCH",
              f"{5-len(bad)}/5",
              "max_abs",max(v["abs_difference"] for v in comparisons.values()),
              flush=True)
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--generator-output",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    if a.report.exists():p.error("Refuse overwrite of existing report")
    out={"status":STATUS,"full_Zee_RGEs_validated":False,
         "scalar_only_dimensional_RGEs_validated":False,
         "physical_Zee_allowed":None}
    try:
        source=find_rges(a.generator_output)
        out["RGEs_sha256"]=hashlib.sha256(source.read_bytes()).hexdigest()
        cases=run_cases(load_generated(source))
        failed=[f"{label}/{name}" for label,case in cases.items()
                for name in case["mismatches"]]
        total=sum(len(case["comparisons"]) for case in cases.values())
        out.update({"cases":cases,"comparisons_total":total,
                    "comparisons_passed":total-len(failed),
                    "failed":failed,
                    "scalar_only_dimensional_RGEs_validated":len(failed)==0,
                    "full_gauge_yukawa_f_dimensional_beta_validated":False})
        print("Q4_DIMENSIONFUL_SCALAR_ONLY",total-len(failed),"/",total)
        print("Q4_FULL_ZEE_RGES_VALIDATED False")
        return 0 if not failed else 2
    except Exception as exc:
        out["error"]=repr(exc);out["traceback"]=traceback.format_exc()
        print("Q4_DIM_SCALAR_FAIL_CLOSED",repr(exc),file=sys.stderr)
        return 1
    finally:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print("Q4_DIM_SCALAR_REPORT",a.report)

if __name__=="__main__":
    raise SystemExit(main())
