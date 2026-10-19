#!/usr/bin/env python3
"""Gate C1: one LARGE joined Zee candidate -> full-one-loop UV screening pilot.

Joins the EXISTING B4 scalar/EWPO screened spectra with B2 neutrino-closed
(f,Y) families, reconstructs the FULL restricted 2021 Zee scalar potential,
converts charged-lepton Higgs-basis Y into symmetry-basis Ye1,Ye2, then
runs ALL 26 independently checked one-loop full-Zee beta functions
toward 10 TeV using RK4 and a step-doubling convergence check.

This is the FIRST PHYSICS-CONNECTED MODEL/RGE pilot, NOT full viability.
It does NOT recompute neutrino oscillations along the RG flow, impose
full LFV/Barr-Zee/meson FCNC/HiggsTools, test global vacuum minima or
establish an MS-bar threshold/mass/CKM matched 2026 quark input scheme.
Short-flow perturbativity-loss scales are indicative ONLY and MUST NOT
be presented as physical UV cutoff exclusions.

Basis: B2 Y in Chen/Herrero mass/Higgs basis is the coefficient of
  -sqrt(2) bar(ell_R) Y nu_L H_perp^- + h.c.
so conventional -bar(L) rho_e H_perp ell_R has rho_e= sqrt(2) Y†.
With kappa_e=sqrt(2) diag(m_e,m_mu,m_tau)/v:
  Ye1=cos(beta) kappa_e - sin(beta) rho_e,
  Ye2=sin(beta) kappa_e + cos(beta) rho_e.
The f matrix acts on L_i L_j and is unchanged under the Higgs-doublet
rotation (subject to the pinned charged-singlet phase convention).

Scalar map of Florentino Eq.16:
  l1..l5=lambda1..lambda5, l6=l7=0;
  lh=lc, l8=k1, l9=k2, l10=-k12.
  m12=m12sq, muZee=mu4, mchi=mc2.
  m1,m2 fixed by exact tree-level neutral tadpoles.

The Type-II quark input is an explicitly ILLUSTRATIVE boundary with
DIAGONAL (CKM=I) running quark mass Yukawas, not a physical quark fit.
Use this ONLY to identify numerical flow/large-coupling bottlenecks.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import traceback
from pathlib import Path

import numpy as np

from gate6_benchmark import benchmark
from gateA1b_hierarchical_no_seed import (
    ML,target_neutrino_matrix,reconstruct_neutrino,scalar_kappa
)
from gateB3_general_zee_charged_lepton_widths import (
    read_b1,complex_matrix,ensure_neutrino_closure,
)
from zee_section8_Q4_generated_source_limit_probe import (
    arg_map,find_rges,load_generated
)
from zee_section8_Q4_large_integrated_one_loop_gate import (
    NAMES,REAL_NAMES,MATRIX_NAMES,
    validate_state,rk4_step,full_source_beta,
)

STATUS='GATE_C1_JOINT_ZEE_MODEL_ONE_LOOP_UV_DIAGNOSTIC_NOT_ALLOWED'
VEV=246.21965
MATRIX_KEYS=set(MATRIX_NAMES)
QUARTIC_KEYS=('l1','l2','l3','l4','l5','l6','l7','lh','l8','l9','l10')
QUARK_BOUNDARY={
   'yu':(1.2e-5,.0069,.93),  # dimensionless SM Yukawas, NOT masses
   'yd':(2.5e-5,.00056,.024),  # dimensionless SM Yukawas, NOT masses
}
DEFAULT_EW_GAUGE={'gp':.36,'g2':.65,'g3':1.10}
PRE_FLIGHT_CLOSURE_GEV=1e-5

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def scalar_lagrangian(point):
    """Reconstruct ALL independent dimensionful/quartic model inputs."""
    p=point
    v=benchmark(
        beta=p['beta'],mH1=p['mH1'],mH2=p['mH2'],
        alpha=p['alpha'],gamma=p['gamma'],m12sq=p['m12sq'],
        mh2=p['mh2'],ma=p['ma'],lc=p['lc'],k1=p['k1'],
        k2=p['k2'],k12=p['k12'])
    if not v['sufficient_global_quartic_BFB'] or not v['tree_unitarity_pass']:
        raise ValueError('B4 input does not reproduce certified restricted scalar screen')
    reconstructed=(v['rebuilt_charged_masses_GeV'],
                   v['rebuilt_neutral_masses_GeV'])
    for actual,reference in zip(reconstructed[0],(p['mH1'],p['mH2'])):
        if abs(actual-reference)>PRE_FLIGHT_CLOSURE_GEV:
            raise ValueError('Charged mass mismatch')
    for actual,reference in zip(reconstructed[1],(125.,p['mh2'])):
        if abs(actual-reference)>PRE_FLIGHT_CLOSURE_GEV:
            raise ValueError('Neutral mass mismatch')
    if abs(v['reconstructed_pseudoscalar_mass_GeV']-p['ma'])>PRE_FLIGHT_CLOSURE_GEV:
        raise ValueError('Pseudoscalar mass mismatch')
    mapping={f'l{i}':v['quartics'][f'lambda{i}'] for i in range(1,6)}
    for i in range(1,6):
        key=f'lambda{i}'
        if key in p and not math.isclose(float(p[key]),float(v['quartics'][key]),
                                          rel_tol=1e-8,abs_tol=1e-7):
            raise ValueError(f'Stored B4 quartic {key} does not reproduce')
    mapping.update({'l6':0.,'l7':0.,'lh':p['lc'],
                    'l8':p['k1'],'l9':p['k2'],'l10':-p['k12']})
    beta=p['beta'];sb,cb=math.sin(beta),math.cos(beta)
    s12=p['m12sq']
    t=v['quartics']
    l345=t['lambda3']+t['lambda4']+t['lambda5']
    m1=s12*sb/cb-.5*VEV**2*(t['lambda1']*cb**2+l345*sb**2)
    m2=s12*cb/sb-.5*VEV**2*(t['lambda2']*sb**2+l345*cb**2)
    mapping.update({'m1':m1,'m2':m2,'m12':s12,
                    'mchi':v['mc2_GeV2'],'muZee':v['mu4_GeV']})
    return mapping,{
        'scalar_mass_closure':'PASS',
        'quartic_BFB_sufficient_at_matching':True,
        'tree_unitarity_at_matching':True,
        'max_unitarity_eigenvalue':v['max_abs_unitarity_eigenvalue'],
        'mu4_GeV':v['mu4_GeV'],
        'mchi_squared_GeV2':v['mc2_GeV2'],
        'm1_squared_GeV2':m1,'m2_squared_GeV2':m2,
        'restricted_lambda6_lambda7_initially_zero':True,
        'k12_hard_Z2_breaking_nonzero':bool(abs(p['k12'])>1e-14),
    }

def convert_higgs_basis_Y(Y,beta):
    """Chen-normalized H_perp Yukawa -> two symmetry-basis matrices."""
    Y=np.asarray(Y,complex)
    if Y.shape!=(3,3) or not np.isfinite(Y).all():
        raise ValueError('Higgs-basis Y is not a finite 3x3 matrix')
    sb,cb=math.sin(beta),math.cos(beta)
    kappa=np.sqrt(2.)*ML/VEV
    rho=np.sqrt(2.)*Y.conj().T
    ye1=cb*kappa-sb*rho
    ye2=sb*kappa+cb*rho
    back_kappa=cb*ye1+sb*ye2
    back_rho=-sb*ye1+cb*ye2
    if max(np.max(abs(back_kappa-kappa)),
           np.max(abs(back_rho-rho)))>1e-12:
        raise ValueError('Lepton Higgs basis invertibility failed')
    return ye1,ye2,{
        'Y_from_rho_dagger_over_sqrt2_max_abs':
           float(np.max(abs(back_rho.conj().T/np.sqrt(2.)-Y))),
        'charged_lepton_mass_closure_GeV':
           float(np.max(abs(back_kappa*VEV/np.sqrt(2.)-ML))),
        'matrix_norm_Y_higgs':float(np.linalg.norm(Y)),
        'matrix_norm_Ye1':float(np.linalg.norm(ye1)),
        'matrix_norm_Ye2':float(np.linalg.norm(ye2)),
        'basis_convention':'Y is bar(e_R) Y L_L neutral current; Ye_k are bar(L) Ye_k e_R',
    }

def illustrative_quarks(beta):
    sb,cb=math.sin(beta),math.cos(beta)
    zero=np.zeros((3,3),complex)
    return {
        'Yu1':zero,
        'Yu2':np.diag(QUARK_BOUNDARY['yu'])/sb,
        'Yd1':np.diag(QUARK_BOUNDARY['yd'])/cb,
        'Yd2':zero
    }

def build_model_state(point,solution):
    if 'NOT_ALLOWED' not in str(solution.get('status','')):
        raise ValueError('B2 source must explicitly retain NOT_ALLOWED status')
    fields,scalar=scalar_lagrangian(point)
    f=complex_matrix(solution['f'],'f')
    Y=complex_matrix(solution['Y'],'Y')
    target,_=target_neutrino_matrix()
    closure=ensure_neutrino_closure(point,f,Y,target)
    saved=float(solution['neutrino_matrix_closure_eV'])
    if not math.isclose(closure,saved,rel_tol=2e-5,abs_tol=1e-22):
        raise ValueError('Recomputed B2 neutrino closure does not match saved solution')
    ye1,ye2,basis=convert_higgs_basis_Y(Y,point['beta'])
    quarks=illustrative_quarks(point['beta'])
    vals=arg_map(gp=DEFAULT_EW_GAUGE['gp'],
                 g2=DEFAULT_EW_GAUGE['g2'],
                 g3=DEFAULT_EW_GAUGE['g3'],
                 f=np.matrix(f),
                 yy={'Ye1':np.matrix(ye1),'Ye2':np.matrix(ye2),
                     **{k:np.matrix(v) for k,v in quarks.items()}})
    vals.update(fields)
    vals=validate_state(vals)
    return vals,{
        **scalar,
        'neutrino_matrix_closure_eV':float(closure),
        'B2_partial_LFV_score_NOT_EXCLUSION':
           float(solution['partial_LFV_score_NOT_EXCLUSION']),
        'lepton_basis':basis,
        'quark_matching':'DIAGONAL_TOY_CKM_IDENTITY_NOT_A_QUARK_FLAVOR_FIT',
        'gauge_matching':'APPROXIMATE_FIXED_INPUTS_NOT_PRECISION_MS_BAR',
        'full_LFV_tested':False,'modern_bsgamma_tested':False,
        'HiggsTools_tested':False,'global_vacuum_tested':False
    }

def diagnostics(state):
    maxq=max(float(abs(state[k])) for k in QUARTIC_KEYS)
    maxy=max(float(np.max(abs(state[k]))) for k in MATRIX_KEYS)
    wrong={k:float(np.linalg.norm(state[k])) for k in ('Yu1','Yd2')}
    return {
        'max_abs_scalar_quartic':maxq,
        'max_abs_Yukawa_or_f_entry':maxy,
        'lambda6_abs':float(abs(state['l6'])),
        'lambda7_abs':float(abs(state['l7'])),
        'lambda10_abs':float(abs(state['l10'])),
        'wrong_doublet_quark_norms':wrong,
        'scalar_mass_mchi_squared_GeV2':float(state['mchi']),
    }

def numerical_control(state):
    d=diagnostics(state)
    if d['max_abs_scalar_quartic']>=4*math.pi:
        return 'QUARTIC_ABS_GE_4PI'
    if d['max_abs_Yukawa_or_f_entry']>=math.sqrt(4*math.pi):
        return 'YUKAWA_ENTRY_ABS_GE_SQRT4PI'
    if min(float(state[k]) for k in ('gp','g2','g3'))<0 or max(
            float(state[k]) for k in ('gp','g2','g3'))>=3:
        return 'GAUGE_DIAGNOSTIC_BOUND'
    return None

def vector_distance(a,b):
    out={}
    for name in NAMES:
        lhs=np.asarray(a[name],complex)
        rhs=np.asarray(b[name],complex)
        denom=max(1.,np.max(abs(lhs)),np.max(abs(rhs)))
        out[name]=float(np.max(abs(lhs-rhs))/denom)
    return out

def run_flow(mod,start,*,mu0,mu1,steps,record_every=4):
    if not (0<mu0<mu1 and steps>=4):
        raise ValueError('Invalid evolution scales')
    if steps%record_every:
        raise ValueError('steps must be a multiple of record_every')
    dt=math.log(mu1/mu0)/steps
    state=start
    history=[]
    initial_condition=numerical_control(state)
    if initial_condition:
        return {'status':'INITIAL_PERTURBATIVITY_CONTROL_FAILED',
                'reason':initial_condition,
                'first_diagnostic_boundary_GeV':float(mu0),
                'history':history,'endpoint':None}
    for i in range(steps+1):
        if i%record_every==0 or i==steps:
            hist={'mu_GeV':float(mu0*math.exp(i*dt)),
                  'step':i,**diagnostics(state)}
            history.append(hist)
        if i==steps:break
        try:
            next_state=rk4_step(mod,state,dt)
            reason=numerical_control(next_state)
        except (ValueError,OverflowError,FloatingPointError) as exc:
            reason='NONFINITE_OR_INVALID_RGE_STEP:'+type(exc).__name__
            next_state=None
        if reason:
            return {
                'status':'DIAGNOSTIC_BOUNDARY_REACHED_NOT_PHYSICAL_CUTOFF',
                'reason':reason,
                'first_diagnostic_boundary_GeV':
                    float(mu0*math.exp((i+1)*dt)),
                'history':history,'endpoint':None}
        state=next_state
    return {
        'status':'REACHED_END_SCALE_ONE_LOOP_DIAGNOSTIC_ONLY',
        'reason':None,'first_diagnostic_boundary_GeV':None,
        'history':history,'endpoint':state}

def choose_rows(b4_csv,b2_json,top,solutions):
    p=read_b1(b4_csv)
    with Path(b4_csv).open(newline='') as f:
        reader=csv.DictReader(f)
        ranked=list(reader)
    b2=json.loads(Path(b2_json).read_text())
    if set(p)!=set(b2):
        raise ValueError('B2 solutions and B4 candidate IDs are not identical')
    if any(not row or not isinstance(row,list) for row in b2.values()):
        raise ValueError('Empty or malformed B2 solution lists')
    names=sorted(p,key=lambda c:float(next(
        r['production_weighted_nonleptonic_cascade_upper_proxy']
        for r in ranked if r['id']==c)),reverse=True)[:top]
    return [(p[n],j+1,b2[n][j]) for n in names
            for j in range(min(solutions,len(b2[n])))]

def public_row(point,rank,preflight,flow,step_convergence):
    h=flow['history']
    last=h[-1] if h else None
    return {
        'candidate_id':point['id'],
        'B2_solution_rank':rank,
        'mH1_GeV':point['mH1'],'mH2_GeV':point['mH2'],
        'neutrino_closure_eV':preflight['neutrino_matrix_closure_eV'],
        'matching_scalar_BFB_sufficient':preflight['quartic_BFB_sufficient_at_matching'],
        'matching_tree_unitarity':preflight['tree_unitarity_at_matching'],
        'B2_partial_LFV_NOT_EXCLUSION':preflight['B2_partial_LFV_score_NOT_EXCLUSION'],
        'one_loop_RGE_diagnostic_status':flow['status'],
        'last_recorded_mu_GeV':None if not last else last['mu_GeV'],
        'first_diagnostic_boundary_GeV':flow['first_diagnostic_boundary_GeV'],
        'max_abs_quartic_last_recorded':None if not last else last['max_abs_scalar_quartic'],
        'max_abs_lambda6_last_recorded':None if not last else last['lambda6_abs'],
        'max_abs_lambda7_last_recorded':None if not last else last['lambda7_abs'],
        'wrong_doublet_Yd2_norm_last':None if not last else last['wrong_doublet_quark_norms']['Yd2'],
        'wrong_doublet_Yu1_norm_last':None if not last else last['wrong_doublet_quark_norms']['Yu1'],
        'RK4_full_half_convergence_max_scaled_difference':step_convergence,
        'UV_vacuum_consistency':'NOT_EVALUATED',
        'full_LFV':'NOT_EVALUATED',
        'flavor_FCNC':'NOT_EVALUATED',
        'HiggsTools':'NOT_EVALUATED',
        'modern_BtoXsGamma':'NOT_EVALUATED',
        'physically_allowed':'UNKNOWN',
    }

def main():
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument('--b4-csv',type=Path,required=True)
    pa.add_argument('--b2-json',type=Path,required=True)
    pa.add_argument('--generator-output',type=Path,required=True)
    pa.add_argument('--output-dir',type=Path,required=True)
    pa.add_argument('--top-candidates',type=int,default=3)
    pa.add_argument('--solutions-per-candidate',type=int,default=2)
    pa.add_argument('--steps',type=int,default=24)
    pa.add_argument('--upper-GeV',type=float,default=10000.)
    opts=pa.parse_args()
    if not(1<=opts.top_candidates<=30 and 1<=opts.solutions_per_candidate<=10
           and 8<=opts.steps<=240 and opts.steps%4==0
           and 1000.<=opts.upper_GeV<=1e7):
        pa.error('Invalid integrated pilot settings')
    if opts.output_dir.exists() and any(opts.output_dir.iterdir()):
        pa.error('Refuse nonempty output directory')
    summary={
        'status':STATUS,'physical_allowed_points':None,
        'full_Zee_LFV_validated':False,
        'flavor_FCNC_validated':False,
        'modern_BtoXsGamma_likelihood_validated':False,
        'HiggsTools_full_prediction_validated':False,
        'global_vacuum_validated':False,
        'RG_threshold_matching_validated':False,
        'quark_CKM_and_running_masses_matched':False,
    }
    opts.output_dir.mkdir(parents=True,exist_ok=True)
    try:
        src=find_rges(opts.generator_output)
        summary['RGE_sha256']=digest(src)
        summary['B4_sha256']=digest(opts.b4_csv)
        summary['B2_sha256']=digest(opts.b2_json)
        mod=load_generated(src)
        rows=choose_rows(opts.b4_csv,opts.b2_json,
                         opts.top_candidates,opts.solutions_per_candidate)
        reports=[];public=[]
        for point,rank,solution in rows:
            if str(solution.get('candidate_id'))!=point['id']:
                raise ValueError('B2 solution/provenance mismatch')
            start,preflight=build_model_state(point,solution)
            mu0=float(point['mH2'])
            if opts.upper_GeV<=mu0:raise ValueError('UV end below heaviest charged Higgs')
            flow=run_flow(mod,start,mu0=mu0,mu1=opts.upper_GeV,
                          steps=opts.steps)
            # Independent integration with twice as many RK4 steps controls
            # the numerical solver, NOT the physics truncation error.
            half=run_flow(mod,start,mu0=mu0,mu1=opts.upper_GeV,
                          steps=2*opts.steps)
            if flow['endpoint'] is not None and half['endpoint'] is not None:
                per=vector_distance(flow['endpoint'],half['endpoint'])
                max_diff=max(per.values())
                if max_diff>=2e-4:
                    raise ValueError(f'RK4 step doubling does not converge: {max_diff}')
                convergence=max_diff
            else:
                convergence=None
            if flow['status']!=half['status']:
                raise ValueError('RK4 coarse/refined path boundary outcome differs')
            view=public_row(point,rank,preflight,flow,convergence)
            public.append(view)
            reports.append({
                'candidate_id':point['id'],'B2_solution_rank':rank,
                'initial':preflight,'full_step':{k:v for k,v in flow.items()
                                  if k!='endpoint'},
                'half_step':{k:v for k,v in half.items()
                                  if k!='endpoint'},
                'RK4_relative_step_convergence':convergence,
                'status':'RG_SCREEN_ONLY_NOT_PHYSICAL_CUTOFF_OR_ALLOWED'
            })
            print('C1_JOINED_UV',point['id'],'rank',rank,
                  flow['status'],
                  'last_mu',view['last_recorded_mu_GeV'],
                  'max_quartic',view['max_abs_quartic_last_recorded'],
                  'rk4_control',convergence,flush=True)
        summary['rows']=reports
        summary['row_count']=len(public)
        summary['diagnostic_boundary_count']=sum(
            r['one_loop_RGE_diagnostic_status']!='REACHED_END_SCALE_ONE_LOOP_DIAGNOSTIC_ONLY'
            for r in public)
        summary['status']=STATUS
        file=opts.output_dir/'joined_uv_diagnostics_NOT_ALLOWED.csv'
        with file.open('w',newline='') as f:
            fields=list(public[0]) if public else []
            writer=csv.DictWriter(f,fieldnames=fields)
            writer.writeheader();writer.writerows(public)
        summary['output_csv']=str(file)
        print('C1_SAVED_MODEL_RGE_DIAGNOSTICS',len(public),flush=True)
        print('C1_FULL_PHYSICAL_ZEE_ALLOWED UNKNOWN',flush=True)
        return 0
    except Exception as exc:
        summary['error']=repr(exc)
        summary['traceback']=traceback.format_exc()
        summary['status']='GATE_C1_FAIL_CLOSED_NOT_ALLOWED'
        print('C1_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        (opts.output_dir/'summary.json').write_text(
            json.dumps(summary,indent=2,sort_keys=True)+'\n')
        print('C1_SUMMARY',opts.output_dir/'summary.json',flush=True)

if __name__=='__main__':
    raise SystemExit(main())
