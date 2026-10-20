#!/usr/bin/env python3
"""Independent one-loop PURE-SCALAR Zee quartic beta via 10-real-field Hessian.

V4 = q^T C q, q=(Phi1†Phi1, Phi2†Phi2, chi†chi, Re Phi1†Phi2, Im Phi1†Phi2).
For canonically-normalized real scalars r, M2_ij=d²V4/dr_i dr_j,
16*pi² beta(V4)|_scalar = (1/2) Tr(M2²) at one loop (MS-bar).

Projection onto 15 real quartic components uses independent field-space
samples and least squares, not PyR@TE formulas. Compare with previously
exported beta_l* at zero gauge, Yukawa, singlet-f and dimensionful terms.
No gauge/Yukawa/scalar-mass/fermion one-loop comparison here. This is
partial independent physics validation, not a complete UV Zee RGE proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import traceback
from pathlib import Path
import numpy as np

from zee_section8_Q4_generated_source_limit_probe import (
    arg_map, evaluate, find_rges, load_generated, deviation,
)

STATUS='Q4_INDEPENDENT_SCALAR_HESSIAN_QUARTIC_LIMIT_NOT_FULL_ZEE_RGE'
COMPONENTS=(
    'l1','l2','l3','l4','l5_re','l5_im','l6_re','l6_im',
    'l7_re','l7_im','lh','l8','l9','l10_re','l10_im')
PHYSICAL_QUARTICS=('l1','l2','l3','l4','l5','l6','l7','lh','l8','l9','l10')
COMPLEX_QUARTICS=frozenset(('l5','l6','l7','l10'))

# q_a = 1/2 r_i A^a_ij r_j; r=(Re/Im Phi1^1, Phi1^2,
# Re/Im Phi2^1, Phi2^2, Re/Im chi), all canonically normalized.
def invariant_matrices():
    A=np.zeros((5,10,10),float)
    for i in range(4):A[0,i,i]=1
    for i in range(4,8):A[1,i,i]=1
    for i in range(8,10):A[2,i,i]=1
    for i,j in ((0,4),(1,5),(2,6),(3,7)):
        A[3,i,j]=A[3,j,i]=.5
    for i,j,sign in ((0,5,1),(1,4,-1),(2,7,1),(3,6,-1)):
        A[4,i,j]=A[4,j,i]=.5*sign
    return A
A=invariant_matrices()

def tensor_for_quartics(values):
    """C symmetric: V4=q^T C q, exact general Zee quartic convention."""
    v={k:values.get(k,0.) for k in PHYSICAL_QUARTICS}
    C=np.zeros((5,5),float)
    C[0,0]=v['l1']/2;C[1,1]=v['l2']/2;C[2,2]=v['lh']
    C[0,1]=C[1,0]=v['l3']/2
    C[3,3]=v['l4']+np.real(v['l5'])
    C[4,4]=v['l4']-np.real(v['l5'])
    C[3,4]=C[4,3]=-np.imag(v['l5'])
    for i,k in ((0,'l6'),(1,'l7'),(2,'l10')):
        C[i,3]=C[3,i]=np.real(v[k]);C[i,4]=C[4,i]=-np.imag(v[k])
    C[0,2]=C[2,0]=v['l8']/2
    C[1,2]=C[2,1]=v['l9']/2
    if np.max(abs(C.imag))>0:raise ValueError('quartic potential nonreal')
    return C

def components_to_couplings(component_vector):
    w=dict(zip(COMPONENTS,component_vector))
    return {k:(w[k+'_re']+1j*w[k+'_im'] if k in COMPLEX_QUARTICS else float(w[k]))
            for k in PHYSICAL_QUARTICS}

def couplings_to_components(c):
    d={}
    for k in PHYSICAL_QUARTICS:
        val=c[k]
        if k in COMPLEX_QUARTICS:
            d[k+'_re']=float(np.real(val));d[k+'_im']=float(np.imag(val))
        else:
            if abs(np.imag(val))>1e-10:raise ValueError(f'Expected real {k}, got {val}')
            d[k]=float(np.real(val))
    return np.array([d[k] for k in COMPONENTS],float)

UNIT_C=np.stack([
    tensor_for_quartics(components_to_couplings(np.eye(15)[i]))
    for i in range(15)
])

def invariants(phi):
    return np.einsum('i,aij,j->a',phi,A,phi)/2

def potential(phi,C):
    q=invariants(phi)
    return float(q@C@q)

def hessian(phi,C):
    q=invariants(phi)
    grad_q=np.einsum('aij,j->ai',A,phi)
    return (2*np.einsum('a,aij->ij',C@q,A) +
            2*np.einsum('ab,ai,bj->ij',C,grad_q,grad_q))

def scalar_loop_polynomial(phi,C):
    h=hessian(phi,C)
    return float(np.trace(h@h)/2)

def quartic_projection(fields):
    B=np.array([[potential(phi,Ci) for Ci in UNIT_C] for phi in fields])
    s=np.linalg.svd(B,full_matrices=False,compute_uv=False)
    condition=s[0]/s[-1] if s[-1]>0 else np.inf
    if not (np.linalg.matrix_rank(B)==15 and condition<1e5):
        raise ValueError(f'Quartic orbit-basis projection singular: rank={np.linalg.matrix_rank(B)} cond={condition}')
    return B,float(condition)

def independent_scalar_beta(quartics,fields,design=None):
    C=tensor_for_quartics(quartics)
    B,condition=quartic_projection(fields) if design is None else design
    rhs=np.array([scalar_loop_polynomial(phi,C) for phi in fields])
    coeff=np.linalg.lstsq(B,rhs,rcond=None)[0]
    error=np.max(abs(B@coeff-rhs))/max(1.,np.max(abs(rhs)))
    if not error < 1e-10:
        raise ValueError(f'Scalar Hessian beta polynomial projection residual {error}')
    return components_to_couplings(coeff),{'projection_residual':float(error),'condition_number':condition}

def synthetic_quartics(seed):
    rng=np.random.default_rng(seed)
    vals={k:float(.1+rng.uniform(-.12,.20)) for k in PHYSICAL_QUARTICS}
    for k in COMPLEX_QUARTICS:
        vals[k]=(.06*rng.standard_normal()+1j*.06*rng.standard_normal())
    vals['l1']=.29+rng.random()*.12
    vals['l2']=.35+rng.random()*.08
    vals['lh']=.2+rng.random()*.09
    return vals

def compare_pyrate_scalar_betas(mod,quartics,expected):
    values=arg_map(gp=0,g2=0,g3=0)
    values.update(quartics)
    # All unprovided masses, Zee trilinear, and fermion/gauge inputs are zero.
    checks={}
    for k in PHYSICAL_QUARTICS:
        got=evaluate(mod,k,values)
        exp=np.asarray(expected[k],complex)
        comp=deviation(got,exp)
        absdiff=comp.get('max_abs_difference')
        if absdiff is not None:
            scale=max(1.,float(np.max(abs(got))),float(abs(exp)))
            comp['pass']=bool(absdiff<2e-9*scale)
        checks[k]=comp
    return checks

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--generator-output',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()
    if a.report.exists():ap.error('Refuse to overwrite report')
    report={'status':STATUS,'full_complex_Zee_RGEs_independently_validated':False,
            'physical_Zee_allowed':None,'scalar_only_quartic_limit_validated':False}
    try:
        path=find_rges(a.generator_output)
        report['rges_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        generated=load_generated(path)
        rng=np.random.default_rng(20261020)
        fields=rng.standard_normal((96,10))
        design=quartic_projection(fields)
        cases={
            'full_complex_seed0':synthetic_quartics(20261020),
            'full_complex_seed1':synthetic_quartics(20261021),
            'isolated_doublet1':{'l1':.41},
            'isolated_singlet':{'lh':.31},
            'pure_zee_portals':{'l8':.11,'l9':.15,'l10':.035+.027j},
            'doublet_mixed_complex':{
                'l1':.37,'l2':.42,'l3':.14,'l4':-.08,
                'l5':.036+.029j,'l6':-.02+.045j,'l7':.03-.015j},
        }
        records={};fail=[];total=0
        for case,q in cases.items():
            expected,metrics=independent_scalar_beta(q,fields,design)
            checks=compare_pyrate_scalar_betas(generated,q,expected)
            bad=[k for k,v in checks.items() if not v['pass']]
            fail.extend(f'{case}/{k}' for k in bad)
            total+=len(checks)
            records[case]={'fit':metrics,'quartics':{k:([v.real,v.imag] if isinstance(v,complex) else v) for k,v in q.items()},
                           'beta_components':{k:([v.real,v.imag] if isinstance(v,complex) else v) for k,v in expected.items()},
                           'checks':checks,'mismatches':bad}
            print('Q4_HESSIAN_CASE',case,'PASS' if not bad else 'MISMATCH',
                  f'{len(checks)-len(bad)}/{len(checks)}',
                  'max_normalized_residual',max((v.get('normalized_difference') or 0) for v in checks.values()),flush=True)
        report.update({'cases':records,'comparisons_total':total,
                       'comparisons_passed':total-len(fail),'failed':fail,
                       'scalar_only_quartic_limit_validated':len(fail)==0,
                       'projection_matrix_condition_number':design[1],
                       'source':'10 real fields, one-loop CW UV-log 1/2 Tr(Hessian(V4)^2)',
                       'independent_RGBeta_or_full_Zee_betas_validated':False})
        print('Q4_HESSIAN_SCALAR_QUARTIC',total-len(fail),'/',total,flush=True)
        print('Q4_FULL_ZEE_RGE_VALIDATED False',flush=True)
        return 0 if not fail else 2
    except Exception as exc:
        report['error']=repr(exc);report['traceback']=traceback.format_exc()
        print('Q4_HESSIAN_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('Q4_HESSIAN_REPORT',a.report,flush=True)

if __name__=='__main__':raise SystemExit(main())
