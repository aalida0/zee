#!/usr/bin/env python3
"""Q4 independent electroweak gauge contributions to general Zee quartic RGEs.

With all Yukawas zero:
  (16 pi²) beta(V4)|gauge =
      (3/2) Tr[(M_vector²)^2] - sum_i (3 C2_i g_i²) * quartic_i,
where the second term denotes each quartic's universal gauge-linear
wavefunction contribution, with Casimirs summed over its 4 scalar legs.

M_vector² is independently reconstructed from the scalar covariant kinetic
terms of two (2,Y=1/2) Higgs doublets and one (1,Y=1) charged singlet,
in arbitrary backgrounds of ten canonically normalized real scalars.

A 15-dimensional real orbit projection recovers all eleven complex/real
beta coefficients, comparing against (generated beta(g)-beta(g=0)).
No RGE regeneration; no independent Yukawa-dependent Zee RGE validation.
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
    arg_map,evaluate,find_rges,load_generated,deviation,
)
from zee_section8_Q4_independent_scalar_hessian_gate import (
    A,COMPONENTS,PHYSICAL_QUARTICS,
    components_to_couplings,couplings_to_components,potential,
    tensor_for_quartics,quartic_projection,synthetic_quartics,
)

STATUS='Q4_INDEPENDENT_ELECTROWEAK_GAUGE_QUARTIC_LIMIT_NOT_FULL_ZEE'
SIGMA=np.array((
    ((0,1),(1,0)),
    ((0,-1j),(1j,0)),
    ((1,0),(0,-1)),
),complex)
DOUBLETS=frozenset(('l1','l2','l3','l4','l5','l6','l7'))
PORTALS=frozenset(('l8','l9','l10'))
SINGLET=frozenset(('lh',))

def complex_doublets_and_singlet(r):
    r=np.asarray(r,float)
    if r.shape!=(10,) or not np.isfinite(r).all():
        raise ValueError('Require ten finite canonically normalized real fields')
    h1=(r[0:4:2]+1j*r[1:4:2])/np.sqrt(2)
    h2=(r[4:8:2]+1j*r[5:8:2])/np.sqrt(2)
    s=(r[8]+1j*r[9])/np.sqrt(2)
    return h1,h2,s

def gauge_mass_squared(r,gp,g2):
    """Basis (W1,W2,W3,B), L_mass=1/2 A_mu M² A^mu."""
    h1,h2,s=complex_doublets_and_singlet(r)
    gp,g2=float(gp),float(g2)
    x=sum(np.vdot(h,h).real for h in (h1,h2))
    s2=abs(s)**2
    spin=np.array([
        sum(np.vdot(h,sigma@h).real for h in (h1,h2))
        for sigma in SIGMA
    ])
    m=np.zeros((4,4),float)
    m[:3,:3]=np.eye(3)*g2*g2*x/2
    m[3,3]=gp*gp*(x/2+2*s2)
    m[:3,3]=gp*g2*spin/2
    m[3,:3]=m[:3,3]
    if not np.allclose(m,m.T):
        raise AssertionError('Non-symmetric real gauge mass matrix')
    return m

def quartic_gauge_linear_coefficient(coupling,gp,g2):
    gp2,g22=gp*gp,g2*g2
    if coupling in DOUBLETS:
        return -(9*g22+3*gp2)
    if coupling in PORTALS:
        return -(4.5*g22+7.5*gp2)
    if coupling in SINGLET:
        return -12*gp2
    raise ValueError(f'Unknown quartic {coupling}')

def gauge_loop_polynomial(r,quartics,gp,g2):
    """Independent 1-loop g^4 vector CW term + lambda*g² anomalous term."""
    m=gauge_mass_squared(r,gp,g2)
    cw=1.5*np.trace(m@m)
    wave={k:quartic_gauge_linear_coefficient(k,gp,g2)*quartics.get(k,0.)
          for k in PHYSICAL_QUARTICS}
    return float(cw+potential(r,tensor_for_quartics(wave)))

def gauge_quartic_beta(quartics,gp,g2,fields,design=None):
    if not all(np.isfinite(x) and x>=0 for x in (gp,g2)):
        raise ValueError('Nonnegative finite gauge couplings required')
    B,cond=quartic_projection(fields) if design is None else design
    rhs=np.array([gauge_loop_polynomial(r,quartics,gp,g2) for r in fields])
    components=np.linalg.lstsq(B,rhs,rcond=None)[0]
    error=np.max(abs(B@components-rhs))/max(1.,np.max(abs(rhs)))
    if error>1e-10:
        raise ValueError(f'Gauge quartic beta polynomial projection failed {error}')
    return components_to_couplings(components),{
        'projection_residual':float(error),
        'condition_number':float(cond)
    }

def source_gauge_delta(module,quartics,gp,g2):
    zero=arg_map(gp=0.,g2=0.,g3=0.)
    gauged=arg_map(gp=gp,g2=g2,g3=0.)
    zero.update(quartics)
    gauged.update(quartics)
    delta={}
    for k in PHYSICAL_QUARTICS:
        raw=np.asarray(evaluate(module,k,gauged)-
                       evaluate(module,k,zero),dtype=complex)
        if raw.size!=1:
            raise ValueError(f'Expected scalar beta_{k}, got shape {raw.shape}')
        delta[k]=complex(raw.reshape(-1)[0])
    return delta

def compare_generator(module,quartics,gp,g2,independent):
    actual=source_gauge_delta(module,quartics,gp,g2)
    rows={}
    for k in PHYSICAL_QUARTICS:
        got=actual[k];reference=independent[k]
        residual=abs(got-reference)
        tolerance=2e-9*max(1.,abs(got),abs(reference))
        rows[k]={
            'pass':bool(residual<=tolerance),
            'abs_difference':float(residual),
            'relative_to_nonzero_scale':float(residual/max(1.,abs(got),abs(reference))),
            'tolerance':float(tolerance),
            'actual_re_im':[float(got.real),float(got.imag)],
            'independent_re_im':[float(complex(reference).real),
                                 float(complex(reference).imag)]
        }
    return rows

def run(module):
    rng=np.random.default_rng(20261020)
    fields=rng.normal(size=(128,10))
    design=quartic_projection(fields)
    cases={
      'SU2_only_zerolambda':(0.,.65,{}),
      'U1_only_zerolambda':(.36,0.,{}),
      'mixed_gauge_zerolambda':(.36,.65,{}),
      'mixed_gauge_full_complex_seed0':(.36,.65,synthetic_quartics(20261020)),
      'mixed_gauge_full_complex_seed1':(.36,.65,synthetic_quartics(20261021)),
      'mixed_gauge_complex_portals':(.36,.65,{
          'l8':.13,'l9':.17,'l10':.025+.018j,'lh':.24,
          'l6':-.016+.032j,'l7':.012-.028j}),
    }
    results={}
    for name,(gp,g2,quartics) in cases.items():
        independent,fit=gauge_quartic_beta(quartics,gp,g2,fields,design)
        comparisons=compare_generator(module,quartics,gp,g2,independent)
        failed=[k for k,v in comparisons.items() if not v['pass']]
        results[name]={
            'couplings':{k:([float(complex(v).real),float(complex(v).imag)]
                            if np.iscomplexobj(v) else float(v))
                         for k,v in quartics.items()},
            'gp':gp,'g2':g2,'projection':fit,'comparisons':comparisons,
            'mismatches':failed
        }
        print('Q4_GAUGE_HESSIAN',name,
              'PASS' if not failed else 'MISMATCH',
              f'{11-len(failed)}/11',
              'max_abs',max(v['abs_difference'] for v in comparisons.values()),
              flush=True)
    return results

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--generator-output',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    args=ap.parse_args()
    if args.report.exists():ap.error('Refusing to overwrite report')
    report={'status':STATUS,'independent_full_Zee_RGEs_validated':False,
            'physical_Zee_allowed':None,'gauge_quartic_limit_validated':False}
    try:
        generated=find_rges(args.generator_output)
        report['source_sha256']=hashlib.sha256(generated.read_bytes()).hexdigest()
        result=run(load_generated(generated))
        failures=[f'{case}/{name}' for case,info in result.items()
                  for name in info['mismatches']]
        total=sum(len(info['comparisons']) for info in result.values())
        report.update({'cases':result,'comparisons_total':total,
                       'comparisons_passed':total-len(failures),
                       'mismatches':failures,
                       'gauge_quartic_limit_validated':len(failures)==0,
                       'Yukawa_dependent_quartic_terms_independently_validated':False,
                       'full_Zee_quartic_beta_independently_validated':False,
                       'method':'10 real-field gauge mass matrix, vector CW and Casimir anomalous dimensions'})
        print('Q4_INDEPENDENT_GAUGE_QUARTIC',total-len(failures),'/',total,flush=True)
        print('Q4_FULL_ZEE_RGE_VALIDATED False',flush=True)
        return 0 if not failures else 2
    except Exception as exc:
        report['error']=repr(exc)
        report['traceback']=traceback.format_exc()
        print('Q4_GAUGE_HESSIAN_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('Q4_GAUGE_HESSIAN_REPORT',args.report,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
