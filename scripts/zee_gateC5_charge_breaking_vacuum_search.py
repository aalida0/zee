#!/usr/bin/env python3
"""Gate C5: nonconvex FULL Zee tree-scalar vacuum search on C4 cohort.

This is a substantial PHYSICS-ORIENTED audit of the dimensionful
potential including the Zee charged-doublet-singlet trilinear. C2..C4
only checked the positive quartic part and/or high-energy scattering;
neither ensures the EW Higgs vacuum is globally deepest.

Exact scalar potential in the saved PyR@TE field convention:
 V2=m1*x+m2*y+mchi*s-2 Re(m12*z);
 V3=2 Re[muZee*(Phi1^1 Phi2^2-Phi1^2 Phi2^1)*chi*];
 V4=general complex eleven-coupling quartic polynomial.

Gauge fix Phi1=(0,v1)/sqrt2, Phi2=(u,v2+i*v3)/sqrt2,
singlet chi=(sR+i*sI)/sqrt2. The residual electromagnetic
rephasing permits the charged Phi2 component u to be real; this
six-real-variable orbit covers generic nonzero Phi1 extrema,
including charged and CP breaking. Phi1=0 axes are explicitly seeded.

Use analytic 10-real gradients and Hessians, projected onto six
physical gauge-fixed coordinates. Validate the normal EW vacuum
against exact first derivatives and the seven known physical scalar
masses (three zero Goldstones) before ANY minimization.

Run >=64 reproducible local multi-start minimizations per model
at the MATCHING scale, with starting points across neutral,
charge-breaking singlet/doublet and mixed directions. For any point
whose scalar-potential value is reproducibly below V_EW by >1e-6 v^4,
record a mathematically valid *deeper-field witness*. Optimizer
success or stationary convergence is NOT needed to validate the
explicit field-value inequality; repeat its evaluation analytically
and report gradient/residual. Absence of a witness after finite
sampling CANNOT CERTIFY the EW vacuum is global.

C5 checks 30 C2/C3/C4 spectra x 2 paired scalar quartic
counterfactuals (60 potentials) with C4 exact hash provenance
and full C1/B2 neutrino consistency at input. Requires scipy.
No finite-temperature tunnelling; no loop-corrected effective
potential; no all-extrema/global-minimum mathematical certificate;
no full LFV/meson quark matching/HiggsTools/thresholds.
NEVER label an EW vacuum "globally proven" from this tool.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import math
import sys
import traceback
from pathlib import Path
import numpy as np

from scipy.optimize import minimize

from zee_section8_Q4_independent_scalar_hessian_gate import (
    A,tensor_for_quartics,hessian,invariants,PHYSICAL_QUARTICS
)
from zee_section8_Q4_independent_dimensional_scalar_gate import (
    quadratic_hessian,cubic_tensor,potential_quadratic,
    potential_cubic
)
from zee_gateC1_joined_uv_pilot import (
    VEV,build_model_state,digest,scalar_lagrangian
)
from zee_gateC2_paired_uv_rescue import (
    VARIANTS,load_cohort,varied_point
)
from zee_gateC3_running_complex_bfb import TARGET_VARIANTS
from zee_gateC4_running_55channel_unitarity import verify_c3

STATUS='GATE_C5_NUMERICAL_FULL_ZEE_CHARGE_BREAKING_VACUUM_NOT_ALLOWED'
EMBED=np.array([2,4,6,7,8,9],int)
TWO_PI=2*math.pi
WITNESS_MARGIN=1.e-6 # VEV^4 units, avoids false near-degeneracies
GRAD_SCALED_TOL=3e-5

def full_field(t):
    x=np.asarray(t,float)
    if x.shape!=(6,) or not np.isfinite(x).all():
        raise ValueError('Expected finite six-component gauge-fixed field')
    r=np.zeros(10,float)
    r[EMBED]=x
    return r

def scalar_cache(state):
    q={k:state[k] for k in PHYSICAL_QUARTICS}
    masses={k:state[k] for k in ('m1','m2','m12','mchi')}
    mu=complex(state['muZee'])
    return {
        'quartics':q,'mass_terms':masses,'muZee':mu,
        'C':tensor_for_quartics(q),
        'H2':quadratic_hessian(masses),
        'T3':cubic_tensor(mu),
    }

def potential_gradient_hessian(r,cache):
    r=np.asarray(r,float)
    if r.shape!=(10,) or not np.isfinite(r).all():
        raise ValueError('Expected finite ten-real-field state')
    C=cache['C'];H2=cache['H2'];T=cache['T3']
    q=invariants(r)
    gq=np.einsum('aij,j->ai',A,r)
    v2=float(r@H2@r/2)
    v3=float(np.einsum('ijk,i,j,k->',T,r,r,r,optimize=True)/6)
    v4=float(q@C@q)
    value=v2+v3+v4
    gradient=H2@r+np.einsum('ijk,j,k->i',T,r,r,optimize=True)/2
    gradient+=2*np.einsum('a,ai->i',C@q,gq)
    h2=H2
    h3=np.einsum('ijk,k->ij',T,r,optimize=True)
    h4=hessian(r,C)
    return float(value),np.asarray(gradient,float),h2+h3+h4

def gauge_value_and_gradient(t,cache):
    """Fast analytic gradient: omit expensive full Hessian at each optimizer step."""
    r=full_field(np.asarray(t,float)*VEV)
    C=cache['C'];H2=cache['H2'];T=cache['T3']
    q=invariants(r)
    gq=np.einsum('aij,j->ai',A,r,optimize=False)
    cubic_gradient=np.einsum('ijk,j,k->i',T,r,r,optimize=False)
    v2=float(r@H2@r/2)
    v3=float(r@cubic_gradient/6)
    v4=float(q@C@q)
    gradient=H2@r+cubic_gradient/2
    gradient+=2*np.einsum('a,ai->i',C@q,gq,optimize=False)
    return float((v2+v3+v4)/VEV**4),gradient[EMBED]/VEV**3

def electroweak_check(point,cache,strict=True):
    beta=float(point['beta'])
    r=np.zeros(10,float)
    r[2]=VEV*math.cos(beta)
    r[6]=VEV*math.sin(beta)
    val,grad,H=potential_gradient_hessian(r,cache)
    eig=np.linalg.eigvalsh(H)
    physical=sorted([
        125.**2,float(point['mh2'])**2,float(point['ma'])**2,
        float(point['mH1'])**2,float(point['mH1'])**2,
        float(point['mH2'])**2,float(point['mH2'])**2,
    ])
    gold=eig[:3]
    expected=np.asarray([0,0,0,*physical])
    rel=float(np.max(abs(eig-expected)/np.maximum(1.,abs(expected))))
    gn=float(np.max(abs(grad))/VEV**3)
    out={
        'vacuum_V_over_v4':float(val/VEV**4),
        'stationarity_max_gradient_over_v3':gn,
        'physical_plus_goldstone_spectrum_relmax':rel,
        'physical_eigenvalues_GeV2':[float(x) for x in eig[3:]],
        'goldstone_eigenvalues_GeV2':[float(x) for x in gold],
    }
    if strict and (gn>1e-9 or rel>1e-7):
        raise ValueError('EW stationary point or full physical scalar Hessian mismatch '+str(out))
    return out

def candidate_starts(n,seed):
    if n<64:raise ValueError('Require >=64 multistart initial conditions')
    rng=np.random.default_rng(seed)
    starts=[
        [0,0,0,0,0,0],
        [1,0,0,0,0,0],[0,1,0,0,0,0],
        [0,0,1,0,0,0],[0,0,0,1,0,0],
        [0,0,0,0,1,0],[0,0,0,0,0,1],
        [-1,0,0,0,0,0],[0,0,-1,0,0,0],
    ]
    modes=[
        (1,0,0,0,0,0), (0,0,1,0,0,0),
        (1,0,1,0,0,0), (1,1,1,0,0,0),
        (1,0,1,1,0,0), (1,0,1,0,1,0),
        (1,1,1,0,1,0), (1,1,1,1,1,1),
        (0,1,0,0,1,0), (1,1,0,0,1,1),
    ]
    for k in range(n-len(starts)):
        sd=float((.25,.6,1.2,2.4,4.0)[k%5])
        arr=rng.normal(size=6)*sd
        mask=np.array(modes[(k//5)%len(modes)],bool)
        arr[~mask]=0.
        starts.append(arr.tolist())
    return np.asarray(starts,float)

def evaluate_multistart(point,state,starts,*,maxiter=1000):
    cache=scalar_cache(state)
    ewsb=electroweak_check(point,cache)
    vew=float(ewsb['vacuum_V_over_v4'])
    row=[]
    first_deeper=None
    lowest=None
    rad_bound=12.
    # Numerical optimizer bound is NOT a proof that field space outside
    # ±12*v is safe. A found deeper point inside it IS a valid witness.
    bounds=[(-rad_bound,rad_bound)]*6
    ew=np.array([math.cos(point['beta']),0.,math.sin(point['beta']),0.,0.,0.])
    all_starts=np.vstack((starts,ew,-ew))
    for idx,x0 in enumerate(all_starts):
        try:
            result=minimize(
                gauge_value_and_gradient,x0,args=(cache,),
                jac=True,method='L-BFGS-B',bounds=bounds,
                options={'maxiter':maxiter,'ftol':1e-13,
                         'gtol':1e-10,'maxls':40})
        except (ValueError,FloatingPointError,OverflowError) as exc:
            row.append({'seed_index':idx,'error':repr(exc)})
            continue
        x=np.asarray(result.x,float)
        if not np.isfinite(x).all() or np.max(abs(x))>rad_bound+1e-10:
            row.append({'seed_index':idx,'error':'nonfinite_outside_limit'})
            continue
        # Recompute exact polynomial independently of scipy's result.fun.
        r=full_field(x*VEV)
        value,grad,H=potential_gradient_hessian(r,cache)
        direct=(potential_quadratic(r,cache['mass_terms'])+
                potential_cubic(r,cache['muZee'])+
                float(invariants(r)@cache['C']@invariants(r)))/VEV**4
        scaled=float(value/VEV**4)
        if abs(scaled-direct)>2e-9:
            raise ValueError('Full scalar potential tensor and component conventions disagree')
        gradient_norm=float(np.max(abs(grad[EMBED]))/VEV**3)
        negative_gap=scaled-vew
        classification=('CHARGE_BREAKING' if
                        max(abs(x[1]),abs(x[4]),abs(x[5]))>1e-4
                        else 'NEUTRAL_COMPLEX' if abs(x[3])>1e-4
                        else 'NEUTRAL_REAL')
        candidate={
            'seed_index':idx,'value_over_v4':scaled,
            'difference_from_EW_over_v4':float(negative_gap),
            'gauge_fixed_fields_over_v':x.tolist(),
            'gradient_norm_over_v3':gradient_norm,
            'on_artificial_search_boundary':bool(
                np.any(abs(x)>=rad_bound-1e-6)),
            'kind':classification,
            'optimizer_success':bool(result.success),
            'optimizer_message':str(result.message),
            'local_gauge_fixed_hessian_min_eigen_over_v2':
                float(np.min(np.linalg.eigvalsh(H[np.ix_(EMBED,EMBED)]))/VEV**2),
        }
        row.append(candidate)
        if lowest is None or scaled<lowest['value_over_v4']:
            lowest=candidate
        if negative_gap < -WITNESS_MARGIN:
            if first_deeper is None or scaled<first_deeper['value_over_v4']:
                first_deeper=candidate
    failures=sum('error' in z for z in row)
    verdict=('EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS' if first_deeper
             else 'NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE')
    return {
        'status':verdict,'ew':ewsb,
        'starts_requested':len(all_starts),'optimizer_failures':failures,
        'successful_field_evaluations':len(row)-failures,
        'most_negative_witness':first_deeper,'lowest_point_found':lowest,
        'negative_witness_count':sum(
            z.get('difference_from_EW_over_v4',math.inf)<-WITNESS_MARGIN
            for z in row),
        'neutral_real_points':sum(z.get('kind')=='NEUTRAL_REAL' for z in row),
        'charged_breaking_points':sum(z.get('kind')=='CHARGE_BREAKING' for z in row),
        'boundary_hits':sum(z.get('on_artificial_search_boundary',False) for z in row),
        'search_is_not_a_global_minimization_certificate':True,
    }

def c4_provenance(path,b4,b2,c2,c3):
    obj=json.loads(Path(path).read_text())
    src=obj.get('source_checksums',{})
    if (obj.get('status')!='GATE_C4_FULL_COMPLEX_55CHANNEL_RUNNING_SCALAR_UNITARITY_NOT_ALLOWED'
        or obj.get('tested')!=60 or len(obj.get('cases',[]))!=60
        or any(src.get(name)!=digest(filepath) for name,filepath in (
            ('B4',b4),('B2',b2),('C2',c2),('C3',c3)))):
        raise ValueError('C4 60 trajectory model provenance invalid')
    mapping={}
    for item in obj['cases']:
        pair=(item['candidate_id'],item['variant'])
        if pair in mapping:raise ValueError('Duplicate C4 case')
        mapping[pair]=item
    if len(mapping)!=60:raise ValueError('Incomplete C4 cohort')
    return mapping,obj['source_checksums']['RGEs']

def cohort_summary(rows):
    summary={}
    for key in TARGET_VARIANTS:
        group=[z for z in rows if z['variant']==key]
        summary[key]={
            'tested':len(group),
            'C4_running_theory_pass':sum(z['C4_running_theory_pass'] for z in group),
            'explicit_deeper_tree_potential_witness':sum(z['C5_deeper_witness'] for z in group),
            'no_deeper_witness_found_NOT_global_proof':sum(
                not z['C5_deeper_witness'] for z in group),
            'C4_pass_and_no_C5_deeper_witness_found_NOT_allowed':sum(
                z['C4_running_theory_pass'] and not z['C5_deeper_witness']
                for z in group),
        }
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--b4-csv',type=Path,required=True)
    p.add_argument('--b2-json',type=Path,required=True)
    p.add_argument('--c2-summary',type=Path,required=True)
    p.add_argument('--c3-summary',type=Path,required=True)
    p.add_argument('--c4-summary',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--max-spectra',type=int,default=30)
    p.add_argument('--multistart',type=int,default=128)
    p.add_argument('--maxiter',type=int,default=1000)
    p.add_argument('--seed',type=int,default=20261019)
    args=p.parse_args()
    if not (1<=args.max_spectra<=30 and
            64<=args.multistart<=1024 and
            200<=args.maxiter<=6000):
        p.error('Invalid C5 search resource settings')
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        p.error('Refuse nonempty output directory')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    report={'status':STATUS,'physical_Zee_allowed':None,
            'full_global_vacuum_certified':False,
            'charge_breaking_global_minimum_certified':False,
            'one_loop_effective_potential':'NOT_COMPUTED',
            'full_LFV_HiggsTools_bsgamma_CKM':'NOT_COMPUTED',
            'threshold_scheme':'NOT_COMPUTED'}
    try:
        c4,rge_sha=c4_provenance(
            args.c4_summary,args.b4_csv,args.b2_json,
            args.c2_summary,args.c3_summary)
        points,sols,names=load_cohort(
            args.b4_csv,args.b2_json,args.max_spectra)
        rows=[]
        for i,name in enumerate(names,1):
            for variant in TARGET_VARIANTS:
                v=next(z for z in VARIANTS if z[0]==variant)
                pnt=varied_point(points[name],v[1],v[2])
                state,model=build_model_state(pnt,sols[name][0])
                # Seed is stable under arbitrary Python hash salt.
                seed=(args.seed+int.from_bytes(hashlib.sha256(
                    (name+'/'+variant).encode()).digest()[:4],'big'))
                starts=candidate_starts(args.multistart,seed)
                search=evaluate_multistart(
                    pnt,state,starts,maxiter=args.maxiter)
                last=c4[(name,variant)]
                entry={
                    'candidate_id':name,'variant':variant,
                    'C4_running_theory_pass':
                        bool(last['both_running_theory_screens_pass']),
                    'C5_deeper_witness':bool(
                        search['most_negative_witness'] is not None),
                    'C5_search_status':search['status'],
                    'EW_V_over_v4':search['ew']['vacuum_V_over_v4'],
                    'EW_tree_stationarity_max_scaled':
                        search['ew']['stationarity_max_gradient_over_v3'],
                    'EW_tree_mass_eigenvalue_rel_error':
                        search['ew']['physical_plus_goldstone_spectrum_relmax'],
                    'lowest_potential_value_found_over_v4':
                        None if search['lowest_point_found'] is None
                        else search['lowest_point_found']['value_over_v4'],
                    'deepest_gap_from_EW_over_v4':
                        None if search['lowest_point_found'] is None
                        else search['lowest_point_found']['difference_from_EW_over_v4'],
                    'witness_kind':
                        None if search['most_negative_witness'] is None
                        else search['most_negative_witness']['kind'],
                    'witness_fields_over_v':
                        None if search['most_negative_witness'] is None
                        else search['most_negative_witness']['gauge_fixed_fields_over_v'],
                    'witness_gradient_scaled':
                        None if search['most_negative_witness'] is None
                        else search['most_negative_witness']['gradient_norm_over_v3'],
                    'multistarts':search['starts_requested'],
                    'optimizer_field_failures':search['optimizer_failures'],
                    'optimizer_artificial_boundary_hits':search['boundary_hits'],
                    'B2_neutrino_closure_eV':model['neutrino_matrix_closure_eV'],
                    'EW_vacuum_global_PROVEN':False,
                    'physical_Zee_allowed':'UNKNOWN',
                }
                rows.append(entry)
                print('C5_TREE_VACUUM',f'{i}/{len(names)}',name,variant,
                      'C4_pass',entry['C4_running_theory_pass'],
                      'deeper_witness',entry['C5_deeper_witness'],
                      'witness_kind',entry['witness_kind'],
                      'DeltaV_over_v4',entry['deepest_gap_from_EW_over_v4'],
                      'n_starts',entry['multistarts'],
                      flush=True)
        report.update({
            'tested':len(rows),'rows':rows,
            'cohort':cohort_summary(rows),
            'C4_RGE_SHA256':rge_sha,
            'inputs_sha256':{k:digest(v) for k,v in (
                ('B4',args.b4_csv),('B2',args.b2_json),
                ('C2',args.c2_summary),('C3',args.c3_summary),
                ('C4',args.c4_summary))},
            'gauge_fixed_real_orbit_dimensions':6,
            'tree_level_global_stability_NOT_certified_by_absence_of_witness':True,
        })
        outfile=args.output_dir/'charge_breaking_vacuum_screen_NOT_ALLOWED.csv'
        with outfile.open('w',newline='') as f:
            cols=[c for rr in rows for c in rr]
            cols=list(dict.fromkeys(cols))
            writer=csv.DictWriter(f,fieldnames=cols)
            writer.writeheader();writer.writerows(rows)
        report['csv']=str(outfile)
        print('C5_COHORT',json.dumps(report['cohort']),flush=True)
        print('C5_PHYSICAL_ZEE_ALLOWED UNKNOWN',flush=True)
        return 0
    except Exception as exc:
        report.update(status='GATE_C5_FAIL_CLOSED_NOT_ALLOWED',
                      error=repr(exc),traceback=traceback.format_exc())
        print('C5_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        outfile=args.output_dir/'summary.json'
        outfile.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('C5_SUMMARY',outfile,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
