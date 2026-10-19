#!/usr/bin/env python3
"""Q4v10: independent f-dependent one-loop ZEE quartic beta comparison.

The full 9x9 complex SYMMETRIC lepton Weyl mass tensor is built in an
arbitrary unbroken 2HDM+charged-singlet scalar background with:
  (nu_L,e_L,e_R^c) three flavors each;
  M_{nu,eL}=2 f chi,  M_{(nu,eL),eR^c}=conj(Pi1 Phi1+Pi2 Phi2).
The f-induced fermion-box contribution to 16*pi² beta(V4) is
  -Tr[(M†M)^2-(M0†M0)^2], M0 is the identical f=0 Weyl mass matrix.
For real f and zero Pi, normalization is independently source-matched:
  beta_lh|f,box = -32 Tr[(f†f)^2]
  beta_lh|f,wave = +16 lh Tr(f†f)
(Kanemura hep-ph/0011357 A9-A11, reduced real-f convention).
The charged singlet wavefunction contributes
  8 Tr(f†f) s dV4/ds, s=|chi|².
No gauge/Yukawa-independent scalar/gauge quartic expressions are reused.

Results are checked against beta_l[PyR@TE](f)-beta_l[PyR@TE](f=0)
with all other couplings fixed; seven cases x 11 quartic functions.
This validates the f-dependent quartic sector only at tested points,
NOT complex beta_f/Yukawas, dimensionful RGEs or allowed Zee points.
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
    arg_map,evaluate,find_rges,load_generated,
)
from zee_section8_Q4_independent_scalar_hessian_gate import (
    PHYSICAL_QUARTICS,components_to_couplings,invariants,
    tensor_for_quartics,quartic_projection,synthetic_quartics,
)
from zee_section8_Q4_independent_yukawa_quartic_gate import (
    YUKAWAS, validate_yukawas, synthetic_yukawas,
)
from zee_section8_Q4_independent_gauge_quartic_gate import (
    complex_doublets_and_singlet,
)

STATUS='Q4_INDEPENDENT_ZEE_F_DEPENDENT_QUARTIC_LIMIT_NOT_FULL_ZEE_RGES'

def validate_f(f):
    f=np.asarray(f,complex)
    if f.shape!=(3,3) or not np.isfinite(f).all():
        raise ValueError('f must be finite complex 3x3')
    if np.max(abs(f+f.T))>1e-13:
        raise ValueError('Zee f must be antisymmetric in flavor')
    return f

def synthetic_f(seed=20261019,scale=.1):
    rng=np.random.default_rng(seed)
    a=np.zeros((3,3),complex)
    for i,j in ((0,1),(0,2),(1,2)):
        a[i,j]=scale*(rng.normal()+1j*rng.normal())
    return validate_f(a-a.T)

def lepton_weyl_mass(r,yy,f):
    """9x9 symmetric left-Weyl mass tensor, field and flavor explicit."""
    yy=validate_yukawas(yy)
    f=validate_f(f)
    h1,h2,chi=complex_doublets_and_singlet(r)
    # All three Weyl species are ordered (nu_L,e_L,e_R^c).
    # Pi* Phi* follows from 2-component left-handed e_R^c convention.
    upper=np.conjugate(yy['Ye1']*h1[0]+yy['Ye2']*h2[0])
    lower=np.conjugate(yy['Ye1']*h1[1]+yy['Ye2']*h2[1])
    D=np.vstack((upper,lower))
    charged=2*f*chi
    M=np.zeros((9,9),complex)
    M[:3,3:6]=charged
    M[3:6,:3]=charged.T
    M[:6,6:]=D
    M[6:,:6]=D.T
    if np.max(abs(M-M.T))>1e-13:
        raise AssertionError('Weyl mass tensor is not symmetric')
    return M

def fermion_box_delta(r,yy,f):
    """Weyl one-loop UV quartic: -Tr[(M†M)^2], subtract f=0."""
    f=validate_f(f)
    M=lepton_weyl_mass(r,yy,f)
    M0=lepton_weyl_mass(r,yy,np.zeros((3,3),complex))
    H=M.conj().T@M
    H0=M0.conj().T@M0
    return float(-(np.vdot(H,H).real-np.vdot(H0,H0).real))

def singlet_wave_delta(r,quartics,f):
    """f-induced 1-loop charged singlet scalar anomalous dimension."""
    f=validate_f(f)
    f2=float(np.trace(f.conj().T@f).real)
    q=invariants(r)
    C=tensor_for_quartics(quartics)
    # 8 tr(f†f) s ∂V/∂s with ∂V/∂s=2(Cq)_s.
    return float(16*f2*q[2]*(C@q)[2])

def f_quartic_polynomial(r,quartics,yy,f):
    return fermion_box_delta(r,yy,f)+singlet_wave_delta(r,quartics,f)

def independent_f_quartic_betas(quartics,yy,f,fields,design=None):
    yy=validate_yukawas(yy)
    f=validate_f(f)
    B,cond=quartic_projection(fields) if design is None else design
    rhs=np.asarray(
        [f_quartic_polynomial(r,quartics,yy,f) for r in fields],float)
    solution=np.linalg.lstsq(B,rhs,rcond=None)[0]
    residual=float(np.max(abs(B@solution-rhs))/max(1.,np.max(abs(rhs))))
    if residual>1e-10:
        raise ValueError(f'f-dependent quartic polynomial non-invariant or nonclosing: {residual}')
    return components_to_couplings(solution),{
        'projection_residual':residual,'projection_condition_number':float(cond),
        'max_abs_f_polynomial':float(np.max(abs(rhs))),
        'tr_f_dag_f':float(np.trace(f.conj().T@f).real),
        'tr_f_dag_f_squared':float(np.trace(
            (f.conj().T@f)@(f.conj().T@f)).real),
    }

def source_f_delta(mod,quartics,yy,f):
    y=validate_yukawas(yy);f=validate_f(f)
    base=arg_map(gp=0,g2=0,g3=0,yy=y)
    withf=arg_map(gp=0,g2=0,g3=0,yy=y,f=np.matrix(f))
    base.update(quartics);withf.update(quartics)
    out={}
    for k in PHYSICAL_QUARTICS:
        delta=np.asarray(evaluate(mod,k,withf)-evaluate(mod,k,base),
                         dtype=complex)
        if delta.size!=1:
            raise ValueError(f'beta_{k} must be scalar; got {delta.shape}')
        out[k]=complex(delta.reshape(-1)[0])
    return out

def compare_source(mod,quartics,yy,f,predicted):
    actual=source_f_delta(mod,quartics,yy,f)
    checks={}
    for k in PHYSICAL_QUARTICS:
        a=actual[k];b=complex(predicted[k])
        diff=float(abs(a-b))
        scale=max(1.,abs(a),abs(b))
        checks[k]={
            'pass':bool(diff<=2e-9*scale),
            'abs_difference':diff,'scaled_difference':float(diff/scale),
            'generated_re_im':[float(a.real),float(a.imag)],
            'independent_re_im':[float(b.real),float(b.imag)],
        }
    return checks

def evaluate_cases(mod):
    rng=np.random.default_rng(20261019)
    fields=rng.normal(size=(128,10))
    design=quartic_projection(fields)
    zero={k:np.zeros((3,3),complex) for k in YUKAWAS}
    realf=np.zeros((3,3),float)
    realf[0,1]=.12;realf[0,2]=-.08;realf[1,2]=.055
    realf=realf-realf.T
    f=synthetic_f()
    yy=synthetic_yukawas(20261020)
    cases={
       'real_f_only_no_quartics':({},zero,realf),
       'real_f_singlet_lh':({'lh':.27},zero,realf),
       'complex_f_only_no_quartics':({},zero,f),
       'complex_f_with_portals':(
           {'lh':.23,'l8':.11,'l9':.16,'l10':.021+.032j},zero,f),
       'mixed_f_ye_complex_zerolambda':({},yy,f),
       'mixed_f_ye_complex_fullquartic_seed0':(
           synthetic_quartics(20261020),yy,f),
       'mixed_f_ye_complex_fullquartic_seed1':(
           synthetic_quartics(20261021),
           synthetic_yukawas(20261021),synthetic_f(20261021)),
       'mixed_f_ye_portal_special':(
           {'lh':.29,'l8':.21,'l9':.13,'l10':-.023+.041j,
            'l5':.035-.02j,'l6':-.017+.014j,'l7':.024-.011j},
           synthetic_yukawas(20261022),synthetic_f(20261022)),
    }
    report={}
    for label,(quartics,yukawas,fmat) in cases.items():
        pred,metrics=independent_f_quartic_betas(
            quartics,yukawas,fmat,fields,design)
        checks=compare_source(mod,quartics,yukawas,fmat,pred)
        missing=[k for k,v in checks.items() if not v['pass']]
        report[label]={
            'checks':checks,'mismatches':missing,
            'projection':metrics,
            'quartic_input_nonzero':list(quartics),
            'Yukawa_norms':{k:float(np.linalg.norm(v)) for k,v in yukawas.items()},
        }
        print('Q4_F_BOX',label,'PASS' if not missing else 'MISMATCH',
              f'{11-len(missing)}/11',
              'max_abs',max(v['abs_difference'] for v in checks.values()),
              flush=True)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generator-output',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    if a.report.exists():p.error('Refuse to overwrite existing report')
    report={
        'status':STATUS,'full_Zee_complex_RGEs_validated':False,
        'full_complex_f_beta_independently_validated':False,
        'lepton_f_beta_independently_validated':False,
        'dimensional_scalar_betas_independently_validated':False,
        'f_dependent_quartic_limit_validated':False,
        'physical_Zee_allowed':None
    }
    try:
        file=find_rges(a.generator_output)
        report['RGE_SHA256']=hashlib.sha256(file.read_bytes()).hexdigest()
        cases=evaluate_cases(load_generated(file))
        failed=[f'{name}/{k}' for name,item in cases.items()
                for k in item['mismatches']]
        n=sum(len(item['checks']) for item in cases.values())
        report.update({'cases':cases,
                      'checks_total':n,'checks_passed':n-len(failed),
                      'failed_checks':failed,
                      'f_dependent_quartic_limit_validated':not failed,
                      'independent_method':'9x9 symmetric Weyl mass tensor box plus source-normalized chi wavefunction'})
        print('Q4_F_DEPENDENT_QUARTIC',n-len(failed),'/',n,flush=True)
        print('Q4_FULL_COMPLEX_ZEE_RGES_VALIDATED False',flush=True)
        return 0 if not failed else 2
    except Exception as exc:
        report['error']=repr(exc)
        report['traceback']=traceback.format_exc()
        print('Q4_F_BOX_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('Q4_F_BOX_REPORT',a.report,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
