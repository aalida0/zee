#!/usr/bin/env python3
"""Q4v9: independent ONE-LOOP f=0 fermionic Zee quartic beta contributions.

GENERAL complex 2HDM quark/lepton Yukawas on arbitrary charged/neutral
doublet backgrounds; charged singlet external field remains in the quartic
projection but f is set EXACTLY ZERO. Independent Dirac-mass traces and
Higgs anomalous dimensions supply the Yukawa-box and lambda*Y^2 terms.
No full f-dependent scalar RGEs or physical Zee benchmark claimed.

Convention: V4=1/2 l1 x^2+1/2 l2 y^2+l3 xy+l4 |z|^2+
Re[l5 z^2+2(l6*x+l7*y) z]+lh s^2+
s(l8 x+l9 y+2 Re[l10 z]), with z=Phi1†Phi2.
16 pi² beta(V)|fermionic = -2[3 tr(Mq†Mq)^2+tr(Me†Me)^2]
  + (dV/dPhi_k) . (T_jk Phi_j) + c.c.
where T_kl=3tr(Yd_k Yd_l†+Yu_k†Yu_l)+tr(Ye_k Ye_l†),
and Mq is the 6x6 Dirac left-vs-right mass matrix, Me is 6x3.
All comparisons subtract beta_Y=0 at fixed scalar couplings.
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
from zee_section8_Q4_independent_gauge_quartic_gate import complex_doublets_and_singlet

STATUS='Q4_INDEPENDENT_F_ZERO_FERMION_QUARTIC_LIMIT_NOT_FULL_ZEE_RGES'
YU=('Yu1','Yu2')
YD=('Yd1','Yd2')
YE=('Ye1','Ye2')
YUKAWAS=YU+YD+YE
FERMION_MATRIX_SHAPE=(3,3)

def validate_yukawas(yy):
    if set(yy)!=set(YUKAWAS):
        raise ValueError(f'All six Yukawa matrices required, got {sorted(yy)}')
    result={}
    for key in YUKAWAS:
        v=np.asarray(yy[key],complex)
        if v.shape!=FERMION_MATRIX_SHAPE or not np.isfinite(v).all():
            raise ValueError(f'Invalid 3x3 finite Yukawa {key}: {v.shape}')
        result[key]=v
    return result

def dirac_masses(r,yy):
    """M_LR, i.e. (uL,dL)x(uR,dR) and (nuL,eL)x(eR)."""
    y=validate_yukawas(yy)
    h1,h2,_=complex_doublets_and_singlet(r)
    h=(h1,h2)
    du=sum(y[YD[k]]*h[k][0] for k in (0,1))
    dd=sum(y[YD[k]]*h[k][1] for k in (0,1))
    uu=sum(y[YU[k]]*h[k][1].conjugate() for k in (0,1))
    ud=-sum(y[YU[k]]*h[k][0].conjugate() for k in (0,1))
    ev=sum(y[YE[k]]*h[k][0] for k in (0,1))
    ee=sum(y[YE[k]]*h[k][1] for k in (0,1))
    return np.block([[uu,du],[ud,dd]]),np.vstack([ev,ee])

def yukawa_higgs_trace(yy):
    """T_kl in FLS2010 down/lepton Yukawa beta source convention."""
    y=validate_yukawas(yy)
    T=np.zeros((2,2),complex)
    for k in range(2):
        for l in range(2):
            T[k,l]=(3*np.trace(y[YD[k]]@y[YD[l]].conj().T+
                                 y[YU[k]].conj().T@y[YU[l]])+
                    np.trace(y[YE[k]]@y[YE[l]].conj().T))
    if np.max(abs(T-T.conj().T))>1e-12:
        raise AssertionError('Yukawa trace matrix is not Hermitian')
    return T

def delta_bilinears(r,yy):
    """Wavefunction counterterm induced by dPhi_l=sum_k T_kl Phi_k."""
    h1,h2,s=complex_doublets_and_singlet(r)
    h=[h1,h2]
    T=yukawa_higgs_trace(yy)
    dh=[sum(T[k,l]*h[k] for k in range(2)) for l in range(2)]
    dx=2*np.vdot(h[0],dh[0]).real
    dy=2*np.vdot(h[1],dh[1]).real
    dz=np.vdot(dh[0],h[1])+np.vdot(h[0],dh[1])
    return np.array((dx,dy,0.,dz.real,dz.imag))

def fermionic_quartic_polynomial(r,quartics,yy):
    """One-loop fermion box and Higgs wavefunction contribution."""
    C=tensor_for_quartics(quartics)
    Mq,Me=dirac_masses(r,yy)
    dq=delta_bilinears(r,yy)
    q=invariants(r)
    # tr[(M†M)^2] == sum_ij |(M†M)_ij|² (positive Hermitian).
    Q=Mq.conj().T@Mq;E=Me.conj().T@Me
    fermion_box=-2*(3*np.vdot(Q,Q).real+np.vdot(E,E).real)
    scalar_wave=2*dq@(C@q)
    return float(fermion_box+scalar_wave)

def yukawa_quartic_beta(quartics,yy,fields,design=None):
    B,cond=quartic_projection(fields) if design is None else design
    rhs=np.array([fermionic_quartic_polynomial(r,quartics,yy) for r in fields])
    result=np.linalg.lstsq(B,rhs,rcond=None)[0]
    err=np.max(abs(B@result-rhs))/max(1.,np.max(abs(rhs)))
    if err>1e-10:
        raise ValueError(f'Fermionic quartic polynomial not closed: {err}')
    return components_to_couplings(result),{
        'projection_residual':float(err),'condition_number':float(cond),
        'max_abs_fermionic_polynomial':float(np.max(abs(rhs))),
    }

def synthetic_yukawas(seed,scale=1.):
    rng=np.random.default_rng(seed)
    sizes={'Yu1':.12,'Yu2':.35,'Yd1':.06,'Yd2':.04,
           'Ye1':.025,'Ye2':.018}
    return {k:scale*size*(rng.standard_normal((3,3))+
                          1j*rng.standard_normal((3,3)))
            for k,size in sizes.items()}

def source_yukawa_delta(mod,quartics,yy):
    y=validate_yukawas(yy)
    baseline=arg_map(gp=0.,g2=0.,g3=0.)
    nominal=arg_map(gp=0.,g2=0.,g3=0.,yy=y)
    baseline.update(quartics);nominal.update(quartics)
    result={}
    for key in PHYSICAL_QUARTICS:
        raw=np.asarray(evaluate(mod,key,nominal)-evaluate(mod,key,baseline),
                       dtype=complex)
        if raw.size!=1:
            raise ValueError(f'Beta for {key} must be scalar, got {raw.shape}')
        result[key]=complex(raw.reshape(-1)[0])
    return result

def compare_source(mod,quartics,yy,independent):
    generated=source_yukawa_delta(mod,quartics,yy)
    comparisons={}
    for key in PHYSICAL_QUARTICS:
        actual=generated[key]
        ref=complex(independent[key])
        delta=abs(actual-ref)
        scale=max(1.,abs(actual),abs(ref))
        comparisons[key]={
            'pass':bool(delta<=2e-9*scale),
            'abs_difference':float(delta),
            'normalized_difference':float(delta/scale),
            'actual_re_im':[float(actual.real),float(actual.imag)],
            'independent_re_im':[float(ref.real),float(ref.imag)],
        }
    return comparisons

def run(mod):
    rng=np.random.default_rng(20261019)
    fields=rng.normal(size=(128,10))
    design=quartic_projection(fields)
    zero={name:np.zeros((3,3),complex) for name in YUKAWAS}
    top={**zero,'Yu2':np.diag((0,0,.93))}
    leptons={**zero,'Ye1':np.diag((.01,.05,.11))}
    cases={
        'top_only_zeroquartic':({},top),
        'top_only_withquartics':({'l1':.32,'l2':.41,'l3':.08,
                                  'l4':-.035,'l8':.13,'l9':.17,
                                  'l10':.017+.012j},top),
        'lepton_only_zeroquartic':({},leptons),
        'all_complex_yukawa_zeroquartic':({},synthetic_yukawas(20261019)),
        'all_complex_yukawa_fullquartic_seed0':(
            synthetic_quartics(20261020),synthetic_yukawas(20261019)),
        'all_complex_yukawa_fullquartic_seed1':(
            synthetic_quartics(20261021),synthetic_yukawas(20261021)),
        'complex_mixed_portal':(
            {'l1':.39,'l2':.36,'lh':.23,'l8':.12,'l9':.15,
             'l10':.035+.026j,'l5':.021-.031j,'l6':.016+.018j,
             'l7':-.022+.024j},
            synthetic_yukawas(20261022)),
    }
    records={}
    for label,(qs,yy) in cases.items():
        prediction,diagnostic=yukawa_quartic_beta(qs,yy,fields,design)
        comp=compare_source(mod,qs,yy,prediction)
        errors=[name for name,value in comp.items() if not value['pass']]
        records[label]={
            'comparisons':comp,
            'mismatches':errors,
            'projection':diagnostic,
            'yukawa_input_norms':{k:float(np.linalg.norm(v)) for k,v in yy.items()},
            'nonzero_quartic_inputs':list(qs),
        }
        print('Q4_YUKAWA_BOX',label,
              'PASS' if not errors else 'MISMATCH',
              f'{len(comp)-len(errors)}/{len(comp)}',
              'max_abs',max(v['abs_difference'] for v in comp.values()),
              flush=True)
    return records

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generator-output',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    args=p.parse_args()
    if args.report.exists():p.error('Refuse to overwrite report')
    result={
        'status':STATUS,
        'full_complex_Zee_betas_independently_validated':False,
        'f_dependent_quartics_independently_validated':False,
        'f_zero_yukawa_quartic_limit_validated':False,
        'physical_Zee_allowed':None,
    }
    try:
        path=find_rges(args.generator_output)
        result['source_SHA256']=hashlib.sha256(path.read_bytes()).hexdigest()
        cases=run(load_generated(path))
        failures=[f'{case}/{key}' for case,item in cases.items()
                  for key in item['mismatches']]
        n=sum(len(item['comparisons']) for item in cases.values())
        result.update({
            'cases':cases,'comparisons_total':n,
            'comparisons_passed':n-len(failures),
            'failed_comparisons':failures,
            'f_zero_yukawa_quartic_limit_validated':len(failures)==0,
            'method':'One-loop arbitrary-background Dirac mass fermion-box traces and FLS Higgs anomalous dimension'
        })
        print('Q4_INDEPENDENT_YUKAWA_QUARTIC',n-len(failures),'/',n,flush=True)
        print('Q4_COMPLETE_ZEE_RGES_VALIDATED False',flush=True)
        return 0 if not failures else 2
    except Exception as exc:
        result['error']=repr(exc)
        result['traceback']=traceback.format_exc()
        print('Q4_YUKAWA_BOX_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('Q4_YUKAWA_BOX_REPORT',args.report,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
