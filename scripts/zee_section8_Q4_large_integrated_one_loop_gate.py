#!/usr/bin/env python3
"""Q4v13 single integrated full-complex one-loop general-Zee audit.

This is a LARGE regression gate, not a scan of physically allowed points.
Compare ALL 26 saved PyR@TE one-loop beta functions against a composed,
independent reference in a common complex, interacting parameter point:
 - gauge: published Zee one-loop coefficients
 - quark Yukawas: FLS 2010 general 2HDM
 - charged leptons + f: Schienbein et al 2019 general Weyl tensors plus
   FLS quark wavefunction trace
 - quartics: 10-real-field scalar Hessian, gauge-boson mass trace,
   general fermion-box matrices, charged-singlet Weyl box and wave terms
 - dimensionful: degree-2/3 scalar Hessian PLUS independent gauge and
   general Yukawa (including f) external-leg anomalous dimensions.

The mixed dimensionful reference is NEW: source comparison at points
where the scalar, gauge, f, complex lepton and quark Yukawa sectors
ALL coexist. If it disagrees, FAIL and investigate coefficients or
conventions; do not silently renormalize the comparator.

Also evolve the saved beta functions with a deterministic RK4 short
one-loop trajectory. Cross-check snapshots with the independent RHS.
A Type-II quark-Yukawa boundary has its radiatively sourced wrong-doublet
quark Yukawas tracked, NOT tested against FCNC constraints.

No threshold decoupling, UV stability, BFB, two-loop matching, neutrino
likelihood or LFV/physical viability is asserted by this software test.
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
    KNOWN_COUPLINGS,arg_map,evaluate,find_rges,load_generated,
)
from zee_section8_Q4_complex_lepton_scalar_covariance_gate import (
    field_rephase,independent_fls_lepton,
)
from zee_section8_quark_alignment_one_loop_gate import beta_quarks_2hdm
from zee_section8_Q4_independent_scalar_hessian_gate import (
    PHYSICAL_QUARTICS,COMPLEX_QUARTICS,quartic_projection,
    independent_scalar_beta,synthetic_quartics,
)
from zee_section8_Q4_independent_gauge_quartic_gate import gauge_quartic_beta
from zee_section8_Q4_independent_yukawa_quartic_gate import (
    YUKAWAS,validate_yukawas,synthetic_yukawas,
    yukawa_quartic_beta,delta_bilinears,yukawa_higgs_trace,
)
from zee_section8_Q4_independent_f_quartic_gate import (
    synthetic_f,validate_f,independent_f_quartic_betas,
)
from zee_section8_Q4_independent_complex_weyl_yukawas import independent_betas
from zee_section8_Q4_independent_dimensional_scalar_gate import (
    DIMENSIONFUL_NAMES,independent_dimensionful_scalar_beta,
    projected_bases,potential_quadratic,potential_cubic,
)
from zee_section8_Q4_independent_scalar_hessian_gate import invariants

STATUS='Q4V13_LARGE_INTEGRATED_FULL_COMPLEX_ONE_LOOP_AUDIT_NOT_ALLOWED'
NAMES=tuple(sorted(KNOWN_COUPLINGS))
REAL_NAMES=frozenset(
    {'gp','g2','g3','l1','l2','l3','l4','lh','l8','l9','m1','m2','mchi'})
MATRIX_NAMES=frozenset((*YUKAWAS,'f'))
COMPLEX_NAMES=frozenset(NAMES)-REAL_NAMES-MATRIX_NAMES
ONELOOP=16*math.pi**2
GAUGE_BETAS={'gp':22/3.,'g2':-3.,'g3':-7.}
MASS_NAMES=('m1','m2','mchi','m12')

def validate_state(state):
    if set(state)!=set(NAMES):
        raise ValueError(f'State has missing/extra couplings: missing {set(NAMES)-set(state)}, extra {set(state)-set(NAMES)}')
    for name in NAMES:
        val=np.asarray(state[name],complex)
        if (val.shape!=(3,3) if name in MATRIX_NAMES else val.size!=1):
            raise ValueError(f'Incorrect size for {name}: {val.shape}')
        if not np.isfinite(val).all():
            raise ValueError(f'Nonfinite {name}')
        if name in REAL_NAMES and abs(complex(val.reshape(-1)[0]).imag)>1e-10:
            raise ValueError(f'Real coupling {name} is complex')
    if max(abs(float(state[k])) for k in GAUGE_BETAS)>3:
        raise ValueError('Pilot input outside chosen perturbative gauge diagnostic range')
    if any(float(state[k])<0 for k in GAUGE_BETAS):
        raise ValueError('Negative gauge coupling')
    validate_yukawas({k:state[k] for k in YUKAWAS})
    validate_f(state['f'])
    return state

def baseline(seed):
    """Nonphysical complex stress fixture, not a neutrino/flavor fit."""
    rng=np.random.default_rng(seed)
    state=arg_map(gp=.35+rng.random()*.045,
                  g2=.63+rng.random()*.048,
                  g3=1.13+rng.random()*.09,
                  f=synthetic_f(seed,scale=.07+rng.random()*.04),
                  yy=synthetic_yukawas(seed+137,scale=.60+rng.random()*.40))
    state.update(synthetic_quartics(seed+317))
    state.update({
        'm1':float((rng.random()-.6)*1.6e5),
        'm2':float(1e5+rng.random()*2e5),
        'mchi':float(5e4+rng.random()*1.8e5),
        'm12':complex(rng.normal()*17000,rng.normal()*13000),
        'muZee':complex(100.+rng.random()*250.,rng.normal()*120.)
    })
    return validate_state(state)

def typeii_boundary(seed=20261019):
    """Type-II QUARK Yukawa texture, generic complex lepton Yukawas."""
    out=baseline(seed)
    d=np.diag((1.e-4,.003,.10)).astype(complex)
    u=np.diag((1.e-5,.007,.91)).astype(complex)
    out['Yd1']=np.matrix(d)
    out['Yd2']=np.matrix(np.zeros((3,3),complex))
    out['Yu1']=np.matrix(np.zeros((3,3),complex))
    out['Yu2']=np.matrix(u)
    return validate_state(out)

def induced_fermion_mass_cubic_waves(state,fields):
    """Independent external-scalar wave contributions to V2 and V3."""
    y={k:state[k] for k in YUKAWAS}
    masses={k:state[k] for k in MASS_NAMES}
    mu=complex(state['muZee'])
    gp=float(state['gp']);g2=float(state['g2'])
    f=np.asarray(state['f'],complex)
    ftrace=float(np.trace(f.conj().T@f).real)
    T=yukawa_higgs_trace(y)
    # Gauge gauge-boson contributions to quadratic terms.
    gd=-(4.5*g2*g2+1.5*gp*gp)
    gs=-6.*gp*gp
    # Cubic: -3 * sum(C2_scalar) g^2 for two doublets & one singlet.
    gm=-4.5*(g2*g2+gp*gp)
    # Yukawa scalar anomalous dimensions:
    # delta Phi_l = sum_k T_{k,l} Phi_k (as validated in Q4v9).
    # charged-singlet delta chi = 4 Tr(f†f) chi (Q4v10).
    # d(Phi1^T epsilon Phi2)=Tr(T) det(Phi1,Phi2).
    cubic_coeff=gm+T[0,0].real+T[1,1].real+4.*ftrace
    mass_polynomial=[]
    for r in fields:
        x,yv,s,zr,zi=invariants(r)
        dz=delta_bilinears(r,y)
        lept_quark=(float(masses['m1'])*dz[0]+float(masses['m2'])*dz[1]
                    -2.*np.real(complex(masses['m12'])*complex(dz[3],dz[4])))
        gauge_doublet=gd*(
            float(masses['m1'])*x+float(masses['m2'])*yv
            -2*np.real(complex(masses['m12'])*complex(zr,zi)))
        gauge_singlet=gs*float(masses['mchi'])*s
        chi_wave=8*ftrace*float(masses['mchi'])*s
        mass_polynomial.append(float(
            lept_quark+gauge_doublet+gauge_singlet+chi_wave))
    return np.asarray(mass_polynomial,float),cubic_coeff*mu,{
        'higgs_trace_diagonal':[float(T[0,0].real),float(T[1,1].real)],
        'f_trace':ftrace,'gauge_doublet_mass_coeff':gd,
        'gauge_singlet_mass_coeff':gs,'gauge_mu_coeff':gm,
        'wave_mu_coefficient':float(cubic_coeff),
    }

def combined_dimensional_beta(state,fields,dim_projection=None):
    m={k:state[k] for k in MASS_NAMES}
    q={k:state[k] for k in PHYSICAL_QUARTICS}
    mu=complex(state['muZee'])
    proj=projected_bases(fields) if dim_projection is None else dim_projection
    base,scalar_fit=independent_dimensionful_scalar_beta(
        q,m,mu,fields,proj)
    wave_poly,wave_mu,wave_info=induced_fermion_mass_cubic_waves(
        state,fields)
    Q=proj[0]
    coeff,_,_,_=np.linalg.lstsq(Q,wave_poly,rcond=None)
    err=float(np.max(abs(Q@coeff-wave_poly))/
              max(1.,np.max(abs(wave_poly))))
    if err>1e-10:
        raise ValueError(f'Dimensionful wave polynomial not in Zee basis: {err}')
    out=dict(base)
    out['m1']+=float(coeff[0])
    out['m2']+=float(coeff[1])
    out['mchi']+=float(coeff[2])
    out['m12']+=complex(coeff[3],coeff[4])
    out['muZee']+=wave_mu
    return out,{
        'scalar_hessian':scalar_fit,
        'gauge_and_Yukawa_mass_projection_residual':err,
        'wave_coefficients':wave_info,
    }

def independent_full_beta(state,fields,quartic_design,dimension_design):
    validate_state(state)
    y={k:np.asarray(state[k],complex) for k in YUKAWAS}
    q={k:state[k] for k in PHYSICAL_QUARTICS}
    f=np.asarray(state['f'],complex)
    gp,g2,g3=(float(state[k]) for k in ('gp','g2','g3'))
    out={k:GAUGE_BETAS[k]*float(state[k])**3 for k in GAUGE_BETAS}
    BG,BU=beta_quarks_2hdm(
        (y['Yd1'],y['Yd2']),(y['Yu1'],y['Yu2']),
        (y['Ye1'],y['Ye2']),gp=gp,g2=g2,g3=g3)
    out.update(dict(zip(('Yd1','Yd2'),BG)))
    out.update(dict(zip(('Yu1','Yu2'),BU)))
    lepton,_=independent_betas(y,f,gp=gp,g2=g2)
    # Independent Schienbein lepton+f tensors lack quark contributions
    # to Higgs wavefunction. Add FLS general 2HDM trace, without
    # duplicating pure-lepton contributions already in lepton.
    for a,k in enumerate(('Ye1','Ye2')):
        quark_trace=np.zeros((3,3),complex)
        for l,yl in enumerate(('Ye1','Ye2')):
            qq=(3*np.trace(y['Yd'+str(a+1)]@
                           y['Yd'+str(l+1)].conj().T+
                           y['Yu'+str(a+1)].conj().T@
                           y['Yu'+str(l+1)]))
            quark_trace+=qq*y[yl]
        out[k]=lepton[k]+quark_trace
    out['f']=lepton['f']
    scalar,_=independent_scalar_beta(q,fields,quartic_design)
    gauge,_=gauge_quartic_beta(q,gp,g2,fields,quartic_design)
    yukawa,_=yukawa_quartic_beta(q,y,fields,quartic_design)
    f_quartic,_=independent_f_quartic_betas(
        q,y,f,fields,quartic_design)
    for name in PHYSICAL_QUARTICS:
        out[name]=scalar[name]+gauge[name]+yukawa[name]+f_quartic[name]
    dim,metrics=combined_dimensional_beta(state,fields,dimension_design)
    out.update(dim)
    if set(out)!=set(NAMES):
        raise ValueError(f'Independent beta missing {set(NAMES)-set(out)}')
    for name in NAMES:
        v=np.asarray(out[name],complex)
        if not np.isfinite(v).all():
            raise ValueError(f'Nonfinite independent beta_{name}')
        if name in REAL_NAMES and np.max(abs(v.imag))>1e-8:
            raise ValueError(f'Complex beta for real coupling {name}')
    return out,{'dimensionful':metrics}

def full_source_beta(mod,state):
    input_values=arg_map(gp=float(state['gp']),
                         g2=float(state['g2']),g3=float(state['g3']),
                         f=state['f'],
                         yy={k:state[k] for k in YUKAWAS})
    for k in set(NAMES)-MATRIX_NAMES-set(GAUGE_BETAS):
        input_values[k]=state[k]
    out={}
    for name in NAMES:
        v=np.asarray(evaluate(mod,name,input_values),complex)
        expected_shape=(3,3) if name in MATRIX_NAMES else ()
        if v.size!= (9 if name in MATRIX_NAMES else 1):
            raise ValueError(f'PyR@TE beta_{name} non-scalar/matrix {v.shape}')
        out[name]=v.reshape(expected_shape) if name in MATRIX_NAMES else complex(v.reshape(-1)[0])
        if name in REAL_NAMES:
            if abs(complex(out[name]).imag)>1e-8:
                raise ValueError(f'Non-real generated beta_{name}')
            out[name]=float(complex(out[name]).real)
    return out

def compare_state(generated,independent,rtol=3e-9,atol=3e-9):
    comparisons={}
    failed=[]
    for name in NAMES:
        v=np.asarray(generated[name],complex)
        w=np.asarray(independent[name],complex)
        if v.shape!=w.shape:
            raise ValueError(f'beta_{name}: incompatible shapes {v.shape} vs {w.shape}')
        delta=float(np.max(abs(v-w)))
        denom=max(1.,float(np.max(abs(v))),float(np.max(abs(w))))
        tol=atol+rtol*denom
        comparisons[name]={
            'pass':bool(delta<=tol),'max_abs_difference':delta,
            'relative_to_scale':float(delta/denom),
            'tolerance':float(tol),
        }
        if delta>tol:failed.append(name)
    return comparisons,failed

def add_state(s,b,scale):
    out={}
    for k in NAMES:
        v=np.asarray(s[k],complex)+scale*np.asarray(b[k],complex)/ONELOOP
        if k in REAL_NAMES:
            if v.size!=1 or abs(complex(v.reshape(-1)[0]).imag)>1e-9:
                raise ValueError(f'RK4 left real manifold: {k}')
            out[k]=float(v.real.reshape(-1)[0])
        elif k in MATRIX_NAMES:
            if v.shape!=(3,3):raise ValueError('RK4 matrix shape mismatch')
            out[k]=np.matrix(v)
        else:
            if v.size!=1:raise ValueError('RK4 scalar shape mismatch')
            out[k]=complex(v.reshape(-1)[0])
    if np.max(abs(np.asarray(out['f']+out['f'].T)))>1e-9:
        raise ValueError('RK4 left antisymmetric f manifold')
    return out

def rk4_step(mod,state,dt):
    k1=full_source_beta(mod,state)
    k2=full_source_beta(mod,add_state(state,k1,dt/2.))
    k3=full_source_beta(mod,add_state(state,k2,dt/2.))
    k4=full_source_beta(mod,add_state(state,k3,dt))
    combo={k:(np.asarray(k1[k],complex)+2*np.asarray(k2[k],complex)+
              2*np.asarray(k3[k],complex)+np.asarray(k4[k],complex))/6
           for k in NAMES}
    return add_state(state,combo,dt)

def run(mod,*,n_seeds=12,steps=8,field_count=96):
    rng=np.random.default_rng(20261019)
    fields=rng.normal(size=(field_count,10))
    quartic_basis=quartic_projection(fields)
    dim_basis=projected_bases(fields)
    fail=[];records={}
    def check(label,state):
        validate_state(state)
        reference,diagnostic=independent_full_beta(
            state,fields,quartic_basis,dim_basis)
        got=full_source_beta(mod,state)
        checks,bad=compare_state(got,reference)
        failed=[f'{label}/{name}' for name in bad]
        fail.extend(failed)
        summary={
            'passed':len(NAMES)-len(bad),
            'checked':len(NAMES),
            'mismatches':bad,
            'max_abs_difference':max(x['max_abs_difference'] for x in checks.values()),
            'max_relative_to_scale':max(x['relative_to_scale'] for x in checks.values()),
            'comparisons':checks,
            'projection':diagnostic
        }
        records[label]=summary
        print('Q4_INTEGRATED_CASE',label,
              'PASS' if not bad else 'MISMATCH',
              f'{26-len(bad)}/26',
              'max_abs',summary['max_abs_difference'],
              'failed',','.join(bad) if bad else 'none',flush=True)
        return summary

    base_states=[]
    for n in range(n_seeds):
        state=baseline(20261101+n)
        base_states.append(state)
        check(f'full_complex_seed{n:02d}',state)
    # Complex phase transformations of FULL interacting test points,
    # with neither gauge nor charged-singlet/fermion couplings switched off.
    for n,(theta,psi) in enumerate(((.41,-.73),(-.32,.62),
                                    (1.01,-.42),(-.83,-1.19))):
        check(f'full_complex_rephased{n:02d}',
              field_rephase(base_states[n],theta,psi))
    # Only proceed with RG trajectories if all direct comparisons pass:
    # this avoids interpreting a broken instantaneous RGE as a UV flow.
    if fail:
        print('Q4_INTEGRATED_TRAJECTORIES_SKIPPED_DIRECT_MISMATCH',
              len(fail),flush=True)
        return records,fail,{'skipped_due_to_direct_mismatch':True}

    trajectory={}
    for label,start in (('generic',base_states[0]),
                        ('typeII_quark_boundary',typeii_boundary())):
        t0=0.;dt=math.log(2000./700.)/steps
        state=start
        history=[]
        for step in range(steps+1):
            if step%2==0:
                check(f'flow_{label}_step{step:02d}',state)
            history.append({
                'step':step,'mu_GeV':float(700.*math.exp(step*dt)),
                'wrong_doublet_Yd2_norm':float(np.linalg.norm(state['Yd2'])),
                'wrong_doublet_Yu1_norm':float(np.linalg.norm(state['Yu1'])),
                'max_Yukawa_abs':max(float(np.max(abs(np.asarray(state[k]))))
                                     for k in MATRIX_NAMES),
                'max_quartic_abs':max(float(abs(state[k]))
                                     for k in PHYSICAL_QUARTICS)
            })
            if step<steps:
                state=rk4_step(mod,state,dt)
        trajectory[label]=history
        if label=='typeII_quark_boundary':
            if (history[-1]['wrong_doublet_Yd2_norm']<1e-12 or
                history[-1]['wrong_doublet_Yu1_norm']<1e-12):
                fail.append('typeII_wrong_doublet_radiative_source_missing')
            print('Q4_TYPEII_INDUCED_WRONG_DOUBLET',
                  'Yd2',history[-1]['wrong_doublet_Yd2_norm'],
                  'Yu1',history[-1]['wrong_doublet_Yu1_norm'],
                  'NOT_AN_FCNC_CONSTRAINT',flush=True)
    return records,fail,trajectory

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generator-output',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    p.add_argument('--n-seeds',type=int,default=12)
    p.add_argument('--steps',type=int,default=8)
    p.add_argument('--field-count',type=int,default=96)
    a=p.parse_args()
    if a.report.exists():p.error('Refusing to overwrite existing integrated report')
    if not (8<=a.n_seeds<=64 and a.steps%2==0 and 4<=a.steps<=40
            and 64<=a.field_count<=256):
        p.error('Require 8..64 seeds, even 4..40 steps, 64..256 real-field samples')
    result={'status':STATUS,'full_Zee_RGE_accepted':False,
            'one_loop_full_Zee_source_consistency_passed':False,
            'thresholds_validated':False,'UV_vacuum_stability_validated':False,
            'physical_Zee_point_allowed':None}
    try:
        src=find_rges(a.generator_output)
        result['source_SHA256']=hashlib.sha256(src.read_bytes()).hexdigest()
        mod=load_generated(src)
        records,fail,trajectories=run(
            mod,n_seeds=a.n_seeds,steps=a.steps,field_count=a.field_count)
        count=sum(row['checked'] for row in records.values())
        ok=sum(row['passed'] for row in records.values())
        result.update({'cases':records,
                       'trajectories':trajectories,
                       'compared_total':count,
                       'compared_passed':ok,
                       'failed_checks':fail,
                       'one_loop_full_Zee_source_consistency_passed':not fail,
                       'RGE_validation_scope':(
                           'one-loop full-complex source and independent composed RHS;'
                           ' no thresholds, no physical viability, no 2-loop'
                       )})
        print('Q4_LARGE_INTEGRATED_ONE_LOOP',ok,'/',count,flush=True)
        print('Q4_FULL_ZEE_RGE_ACCEPTED False',flush=True)
        return 0 if not fail else 2
    except Exception as exc:
        result['error']=repr(exc)
        result['traceback']=traceback.format_exc()
        print('Q4_LARGE_INTEGRATED_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('Q4_LARGE_INTEGRATED_REPORT',a.report,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
