"""Pilot 64 neutrino-exact Zee textures suppressing direct LFV AND electron EDM spurion.

Impose D[e,mu]=D[mu,e]=D[e,e]=D[e,tau]=0 as FOUR COMPLEX LINEAR
constraints on four complex homogeneous neutrino inverse coefficients.
This is a new targeted texture set, not a scan volume or a full-model
viability proof. The exact original scalar/seed inputs are unchanged.

Validate neutrino closure and perturbativity; compute source-based leading
radiative LFV and, when supplied, the official corrected pure-2HDM EDM
control for EACH new texture. Do not silently transfer old 64 rates.
"""
from __future__ import annotations
import argparse,copy,json,math
from pathlib import Path
import numpy as np

from module2.interface import evaluate as nu_eval,decode,encode,canonical_hash
from module3.core import dipole_ledger,combine,radiative_width
from module14.scan import neutrino_input,digest,perturbativity
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.official_gitlab_control import make_input
from research.full_constraints.lfv_literature_closure_2026.official_64_edm import (
    original_edm_groups,official_class,BOUND_90CL,
)

SEEDS=(20261111,20261112)
ORDERS=('NO','IO')
ML=np.array([0.00051099895,0.1056583755,1.77686])
TAU_MU=2.1969811e-6
HBAR=6.582119569e-25
ALPHA0=1/137.035999084
LIM_MUEG=1.5e-13
CONSTRAINTS=((0,1),(1,0),(0,0),(0,2))

def build(row,ordering,seed,official):
    if row['gates']['vacuum']['assessment']!='PASS' or row['bsg_nominal_classification']!='APPROX_COMPATIBLE':
        raise ValueError('Original point lacks required source-specific preselection')
    source={'id':row['id'],'scalar':row['input_card'],'scalar_sha256':row['scalar_sha256']}
    _,_,inp=neutrino_input(source,seed,ordering,1)
    zero=copy.deepcopy(inp)
    zero['homogeneous_coefficients']={'real':[0.0]*4,'imag':[0.0]*4}
    initial=nu_eval(zero)
    D0=decode(initial['inverse']['D0'])
    H=decode(initial['inverse']['homogeneous'],(4,3,3))
    A=np.array([H[:,i,j] for i,j in CONSTRAINTS])
    rhs=-np.array([D0[i,j] for i,j in CONSTRAINTS])
    if np.linalg.matrix_rank(A,tol=1e-9)!=4:
        raise ValueError('Exact 3-complex texture constraints are not rank four')
    z,residuals,rank,sv=np.linalg.lstsq(A,rhs,rcond=None)
    if int(rank)!=3 or np.linalg.norm(A@z-rhs)>1e-10:
        raise ArithmeticError('Failed algebraic four-Yukawa zero solution')
    changed=copy.deepcopy(inp)
    changed['homogeneous_coefficients']=encode(np.asarray(z,dtype=complex))
    model=nu_eval(changed)
    D=decode(model['D']);F=decode(model['F'])
    zeroes=[float(abs(D[i,j])) for i,j in CONSTRAINTS]
    closure=float(model['inverse']['family_relative_residual'])
    if max(zeroes)>1e-10 or closure>=2e-9:
        raise ArithmeticError('Exact neutrino+Yukawa closure failed')
    pert=perturbativity(model)
    if not math.isfinite(pert['overall_max']):
        raise ArithmeticError('Nonfinite Yukawas')
    p=row['input_card']['physical']
    out={'id':row['id'],'ordering':ordering,'seed':seed,
         'source_scalar_sha256':row['scalar_sha256'],
         'new_neutrino_input_sha256':digest(changed),
         'new_Yukawa_D_sha256':canonical_hash(model['D']),
         'new_Yukawa_F_sha256':canonical_hash(model['F']),
         'Yukawas':{'F':model['F'],'D':model['D']},
         'oscillation_observables':model['observables'],
         'rank_complex_four_Yukawa_constraints':int(rank),
         'remaining_homogeneous_nullity_complex':0,
         'exact_direct_Yukawa_abs':{str(a)+str(b):v for (a,b),v in zip(CONSTRAINTS,zeroes)},
         'neutrino_reconstruction_relative':closure,
         'max_abs_Yukawa':float(pert['overall_max']),
         'perturbative':bool(pert['overall_max']<math.sqrt(4*math.pi)),
         'new_input':changed,
         'full_physical_LFV':None,'global_acceptance':None,
         'official_2HDM_proxy_EDM':None}
    if not out['perturbative']:return out
    c=combine(dipole_ledger(F,D,p,ML,1,0))
    br=radiative_width(c,ML[1],ML[0],ALPHA0)*TAU_MU/HBAR
    out['one_loop_muegamma_BR']=float(br)
    out['one_loop_muegamma_below_90CL']=bool(br<LIM_MUEG)
    if official is not None:
        fake={'id':f'{row["id"]}_{ordering}_{seed}_new',
              'module2_input':{'scalar':{'record':{'physical':p}}},
              'yukawas':{'D':model['D']}}
        inputs,_=make_input(fake,'bare')
        group=original_edm_groups(official(inputs))
        out['official_2HDM_proxy_EDM']=group
        out['proxy_EDM_below_JILA']=bool(abs(group['total_e_cm'])<BOUND_90CL)
    return out

def run(upstream=None):
    points=sorted(source_points(),key=lambda r:r['id'])
    if len(points)!=16:raise ValueError('Original scalar inventory changed')
    official=official_class(upstream) if upstream else None
    rows=[]
    for row in points:
        for order in ORDERS:
            for seed in SEEDS:
                try:
                    out=build(row,order,seed,official)
                    rows.append(out)
                    print('FOUR_ZERO_TEXTURE',out['id'],order,seed,
                          'NEUTRINO',out['neutrino_reconstruction_relative'],
                          'MAXY',out['max_abs_Yukawa'],
                          'MU_E_BR',out.get('one_loop_muegamma_BR'),
                          '2HDM_EDM',None if not out.get('official_2HDM_proxy_EDM')
                            else out['official_2HDM_proxy_EDM']['total_e_cm'],flush=True)
                except Exception as e:
                    rows.append({'id':row['id'],'ordering':order,'seed':seed,
                        'status':'FAIL_OR_UNKNOWN','error_type':type(e).__name__,
                        'error_message':str(e),'full_physical_LFV':None,'global_acceptance':None})
                    print('THREE_ZERO_FAILED',row['id'],order,seed,type(e).__name__,str(e),flush=True)
    if len(rows)!=64 or len({(x['id'],x['ordering'],x['seed']) for x in rows})!=64:
        raise ArithmeticError('Wrong original 64 source identities')
    good=[x for x in rows if x.get('perturbative') is True]
    return {'status':'FOUR_COMPLEX_YUKAWA_ZERO_EDM_TEXTURE_PILOT_ONLY',
       'zero_conditions':['D[e,mu]','D[mu,e]','D[e,e]','D[e,tau]'],
       'n_original_16x4':64,
       'n_neutrino_exact_perturbative':len(good),
       'n_below_MEGII_one_loop':sum(x.get('one_loop_muegamma_below_90CL') is True for x in good),
       'n_below_JILA_pure_2HDM_proxy':sum(x.get('proxy_EDM_below_JILA') is True for x in good) if official else None,
       'n_unresolved_or_nonperturbative':64-len(good),
       'maximum_new_mu_e_one_loop_BR':max((x['one_loop_muegamma_BR'] for x in good),default=None),
       'maximum_new_pure_2HDM_proxy_EDM':max((abs(x['official_2HDM_proxy_EDM']['total_e_cm']) for x in good),default=None) if official else None,
       'source_accuracy':'exact Zee one-loop neutrino inverse + Module3 one-loop muegamma + corrected pure 2HDM EDM proxy; fourth zero tests exact electron-row zero and independent neutrino compatibility. No all-Zee EDM or complete LFV',
       'physical_Zee_EDM':None,'full_LFV':None,'global_acceptance':None,
       'records':rows}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream',type=Path,help='Pinned corrected general-2HDM code checkout')
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('No overwrite of model evidence')
    result=run(a.upstream)
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('THREE_ZERO_64_DONE','PERTURBATIVE',result['n_neutrino_exact_perturbative'],
          'MUEG',result['n_below_MEGII_one_loop'],
          'EDM_PROXY',result['n_below_JILA_pure_2HDM_proxy'],flush=True)
    print('FULL_ZEE_LFV_UNKNOWN')
if __name__=='__main__':main()
