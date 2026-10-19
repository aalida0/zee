#!/usr/bin/env python3
"""Q3 exact general Zee tree-level quartic and counterexample BFB screen.

Source: Schmidt & Vandeleur, JHEP 06 (2026) 006, Eq. (2.4).
NOT beta functions, not a global BFB proof, not an allowed Zee point.
D=16*pi*pi RGEs are NOT calculated here.
"""
from __future__ import annotations
import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

STATUS="Q3_EXACT_ZEE_QUARTIC_REDUCTION_AND_BFB_WITNESSES_NOT_FULL_RGE_OR_ALLOWED"
SOURCE="https://arxiv.org/abs/2512.17235"

@dataclass(frozen=True)
class Quartics:
    l1: float
    l2: float
    l3: float
    l4: float
    l5: complex
    l6: complex
    l7: complex
    lh: float
    l8: float
    l9: float
    l10: complex

    def __post_init__(self):
        for name in ('l1','l2','l3','l4','lh','l8','l9'):
            value=getattr(self,name)
            if isinstance(value,complex) or not math.isfinite(float(value)):
                raise ValueError(f'{name} must be finite and real')
        for name in ('l5','l6','l7','l10'):
            value=complex(getattr(self,name))
            if not (math.isfinite(value.real) and math.isfinite(value.imag)):
                raise ValueError(f'{name} must be finite')

def _physical(x,y,z,s=0.):
    z=complex(z)
    if not all(map(math.isfinite,(x,y,z.real,z.imag,s))):
        raise ValueError('Nonfinite field bilinears')
    if min(x,y,s)<0 or abs(z)**2>x*y+1e-13*max(1.,x*y):
        raise ValueError('Unphysical doublet Gram matrix or singlet norm')
    if (x==0 or y==0) and abs(z)>1e-13:
        raise ValueError('z must vanish when either doublet vanishes')

def doublet_quartic(p:Quartics,x:float,y:float,z:complex)->float:
    _physical(x,y,z)
    return float(.5*p.l1*x*x+.5*p.l2*y*y+p.l3*x*y+p.l4*abs(z)**2
                 +(p.l5*z*z+2*(p.l6*x+p.l7*y)*z).real)

def portal(p:Quartics,x:float,y:float,z:complex)->float:
    _physical(x,y,z)
    return float(p.l8*x+p.l9*y+2*(p.l10*z).real)

def quartic(p:Quartics,x:float,y:float,z:complex,s:float)->float:
    _physical(x,y,z,s)
    return doublet_quartic(p,x,y,z)+p.lh*s*s+portal(p,x,y,z)*s

def minimize_singlet_exact(p:Quartics,x:float,y:float,z:complex):
    """Analytically minimize over s=|charged singlet|^2 >= 0."""
    _physical(x,y,z)
    v0=doublet_quartic(p,x,y,z)
    a=portal(p,x,y,z)
    if p.lh<0 or (p.lh==0 and a<0):
        return {'v4_infimum':float('-inf'),'optimal_s':None,
                'singlet_runaway':True,'portal_A':a}
    if p.lh==0:
        return {'v4_infimum':v0,'optimal_s':0.,
                'singlet_runaway':False,'portal_A':a}
    s=max(0.,-a/(2*p.lh))
    v=v0-min(0.,a)**2/(4*p.lh)
    return {'v4_infimum':float(v),'optimal_s':float(s),
            'singlet_runaway':False,'portal_A':a}

def exact_single_doublet_necessary(p:Quartics):
    """Each isolated doublet+singlet BFB condition; NOT full BFB."""
    checks={}
    for label,l,k in (('H1_singlet',p.l1,p.l8),
                      ('H2_singlet',p.l2,p.l9)):
        checks[label]=(l>=0 and p.lh>=0 and
                       k>=-math.sqrt(max(0.,2*l*p.lh)))
    checks['singlet_only']=p.lh>=0
    checks['H1_only']=p.l1>=0
    checks['H2_only']=p.l2>=0
    checks['all_necessary_slices_pass']=all(checks.values())
    checks['sufficient_full_Zee_BFB']=False
    return checks

def portal_matrix_psd(p:Quartics):
    """Whether A is nonnegative on every physical doublet direction."""
    return p.l8>=0 and p.l9>=0 and p.l8*p.l9>=abs(p.l10)**2

def deterministic_counterexamples(p:Quartics):
    """A negative physical witness disproves BFB; no witness proves nothing."""
    checks=exact_single_doublet_necessary(p)
    if p.lh<0:
        return {'negative_witness':{'x':0.,'y':0.,'z_re':0.,'z_im':0.,
                                    's':1.,'v4':p.lh},
                'sampled_count':0,'absence_proves_BFB':False,
                'necessary_slices':checks}
    n=0
    best=None
    for x in [0.,.125,.25,.375,.5,.625,.75,.875,1.]:
        y=1.-x
        for rho in [0.,.25,.5,.75,1.]:
            for ip in range(32):
                phi=2*math.pi*ip/32
                z=math.sqrt(x*y)*rho*complex(math.cos(phi),math.sin(phi))
                record=minimize_singlet_exact(p,x,y,z)
                n+=1
                if record['singlet_runaway']:
                    w={'x':x,'y':y,'z_re':z.real,'z_im':z.imag,
                       's':None,'v4':'-Infinity'}
                    return {'negative_witness':w,'sampled_count':n,
                            'absence_proves_BFB':False,
                            'necessary_slices':checks}
                v=record['v4_infimum']
                if best is None or v<best['v4']:
                    best={'x':x,'y':y,'z_re':z.real,'z_im':z.imag,
                          's':record['optimal_s'],'v4':v}
    witness=best if best and best['v4'] < -1e-10 else None
    return {'negative_witness':witness,'smallest_sampled_v4':best,
            'sampled_count':n,'absence_proves_BFB':False,
            'necessary_slices':checks,'portal_matrix_PSD':portal_matrix_psd(p)}

def coverage_manifest():
    """Explicitly separate literature limits from ungenerated full betas."""
    return {
      'source_eq_2_4_generic_Zee_quartic_operators':15,
      'complex_quartics':['lambda5','lambda6','lambda7','lambda10'],
      'real_quartics':['lambda1','lambda2','lambda3','lambda4',
                       'lambda_h','lambda8','lambda9'],
      'dimensionful':['m11_squared','m22_squared','m12_squared_complex',
                      'mchi_squared','mu_Zee_complex'],
      'established':{'beta_gauge_1loop':True,
                     'FLS_pure_2HDM_quark_yukawa_limit':True,
                     'FLS_pure_2HDM_lepton_yukawa_limit':True,
                     'Kanemura_restricted_real_f_beta':True},
      'NOT_established':{'full_complex_beta_f':False,
                         'full_beta_Pi1_and_Pi2_with_f':False,
                         'full_beta_lambda6_lambda7_lambda10':False,
                         'full_beta_singlet_portals_and_selfquartic':False,
                         'full_beta_mu_Zee_and_scalar_masses':False,
                         'independently_crosschecked_generator_output':False,
                         'physical_finite_RGE_flow':False,
                         'model_and_experiment_accepted':False},
      'RG_scheme_for_future_generation':'MSbar, unbroken Zee theory',
      'matrix_convention':'FLS Pi_i=Lbar_L Phi_i e_R; f_ij=-f_ji',
      'model_completeness':'Full quartic operator basis, NOT full beta set'}

def reference_diagnostics():
    # Synthetic test potentials, neither is a Zee physics benchmark.
    stable=Quartics(.26,.40,.1,.05,0j,0j,0j,.2,.1,.2,0j)
    unstable=Quartics(.26,.40,.1,.05,0j,0j,0j,.2,-1.,.2,0j)
    return {'status':STATUS,'source':SOURCE,
       'synthetic_stable_example_no_negative_witness':deterministic_counterexamples(stable),
       'synthetic_unstable_example_has_negative_witness':deterministic_counterexamples(unstable),
       'rge_coverage':coverage_manifest(),
       'full_UV_Zee_betas_available':False,
       'physical_Zee_allowed':None}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists():ap.error('Refusing overwrite')
    data=reference_diagnostics()
    if (data['synthetic_stable_example_no_negative_witness']['negative_witness'] is not None
        or data['synthetic_unstable_example_has_negative_witness']['negative_witness'] is None):
        raise AssertionError('Quartic regression directions failed')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print('STATUS',STATUS)
    print('EXACT_SINGLET_QUARTIC_MINIMIZATION_VALIDATED True')
    print('UNSTABLE_SYNTHETIC_WITNESS_FOUND True')
    print('COMPLETE_ZEE_BETAS_AVAILABLE False')
    print('PHYSICAL_ZEE_ALLOWED Unknown')
    print('OUTPUT',a.output)

if __name__=='__main__':main()
