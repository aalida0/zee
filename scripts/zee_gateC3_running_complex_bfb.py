#!/usr/bin/env python3
"""Gate C3: full-complex Zee quartic running BFB diagnostics for C2 rescue.

Physics objective: does the 10-TeV 4*pi "rescued" scalar potential remain
bounded from below (BFB) along the entire 26-coupling one-loop trajectory?

Use 30 existing B4 spectra and two paired C2 quartic interventions
(lh<=1,l1=1 and lh<=.4,l1=.5) = 60 complete one-loop flows.

Evaluate the *full complex* scalar quartic form
 V4=1/2*l1*x²+1/2*l2*y²+l3*x*y+l4*|z|²
    +Re(l5*z²)+2 Re[(l6*x+l7*y+l10*s)*z]
    +lh*s²+l8*x*s+l9*y*s,
 x=Phi1†Phi1>=0, y=Phi2†Phi2>=0, s=|chi|²>=0,
 |z|²<=xy, z=Phi1†Phi2.

Perform two logically separate, valid checks:
 A. A rigorous but conservative COPOSITIVE lower-bound certificate,
 obtained by absolute-valuing complex l5,l6,l7,l10 and AM-GM.
 B. A deterministic overconstrained gauge-orbit numerical search for
 V4<0. Any explicit negative orbit is a rigorous instability witness.
 No negative witness does NOT prove stability.

Three and ONLY three quartic verdicts:
  BFB_SUFFICIENT_CERTIFIED (mathematically conservative),
  BFB_NEGATIVE_WITNESS (explicit unbounded-from-below ray),
  BFB_INCONCLUSIVE (insufficient information).

Evaluate at every accepted step (25 points for 24-step RK4 trajectory).
Require exact Q4v13 RGE provenance and C2 240-variant hash/row consistency.
Reproduce C2's 10 TeV heuristic endpoints with solver step-doubling.

This is NOT full Zee vacuum consistency or an allowed physics benchmark:
global charge-breaking minimum, full complex 2->2 unitarity, physical
thresholds, top/CKM matching, LFV/meson flavor/HiggsTools are absent.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
import math
import statistics
import sys
import traceback
from pathlib import Path
import numpy as np

from zee_section8_Q4_independent_scalar_hessian_gate import (
    PHYSICAL_QUARTICS,tensor_for_quartics
)
from zee_section8_Q4_generated_source_limit_probe import find_rges,load_generated
from zee_section8_Q4_large_integrated_one_loop_gate import rk4_step
from zee_gateC1_joined_uv_pilot import (
    digest,build_model_state,numerical_control,limiting_couplings,
    verify_rge_validation,vector_distance
)
from zee_gateC2_paired_uv_rescue import (
    VARIANTS,load_cohort,varied_point,compare_flows
)

STATUS='GATE_C3_COMPLEX_QUARTIC_RUNNING_BFB_DIAGNOSTIC_NOT_ALLOWED'
TARGET_VARIANTS=('both_lh1_l1_1','both_lh0p4_l1_0p5')
BFB_VERDICTS=('BFB_SUFFICIENT_CERTIFIED','BFB_NEGATIVE_WITNESS','BFB_INCONCLUSIVE')

def quartic_lower_bound_matrix(q):
    """Proof: 2sqrt(xy)*x <= x²+xy; likewise y; 2sqrt(xy)*s <= (x+y)*s."""
    for k in PHYSICAL_QUARTICS:
        if k not in q or not np.isfinite(q[k]):
            raise ValueError('Incomplete/nonfinite scalar quartic '+k)
    l6,l7,l10=(abs(q[k]) for k in ('l6','l7','l10'))
    l5=abs(q['l5'])
    A=float(q['l1'])/2-l6
    B=float(q['l2'])/2-l7
    D=float(q['lh'])
    C=float(q['l3'])+min(0.,float(q['l4'])-l5)-l6-l7
    E=float(q['l8'])-l10
    F=float(q['l9'])-l10
    return np.array([[A,C/2,E/2],
                     [C/2,B,F/2],
                     [E/2,F/2,D]],float)

def copositive_3x3(M,atol=1e-10):
    """Necessary-and-sufficient copositivity test for a 3x3 REAL matrix.

    See Kaplan/Hadeler 3x3 copositivity criterion. Here copositivity
    of M only SUFFICES for positivity of the actual complex Zee quartic.
    """
    M=np.asarray(M,float)
    if M.shape!=(3,3) or not np.isfinite(M).all():
        raise ValueError('Need finite 3x3 real lower-bound matrix')
    if np.max(abs(M-M.T))>1e-12:
        raise ValueError('Require symmetric lower-bound matrix')
    a,b,c=(float(M[i,i]) for i in range(3))
    if min(a,b,c)<-atol:
        return False,{'condition':'negative_diagonal'}
    a=max(0.,a);b=max(0.,b);c=max(0.,c)
    x,y,z=(float(M[0,1]),float(M[0,2]),float(M[1,2]))
    barx=x+math.sqrt(a*b)
    bary=y+math.sqrt(a*c)
    barz=z+math.sqrt(b*c)
    if min(barx,bary,barz)<-atol:
        return False,{'condition':'negative_pair_bound'}
    positive_term=math.sqrt(a*b*c)+x*math.sqrt(c)+y*math.sqrt(b)+z*math.sqrt(a)
    rad=max(0.,2*max(0.,barx)*max(0.,bary)*max(0.,barz))
    total=positive_term+math.sqrt(rad)
    # A small positive margin is required for an unambiguous PASS.
    return bool(total>=atol),{
        'condition':'third_copositivity_condition','third_margin':total,
        'diagonals':[a,b,c],
        'pair_margins':[barx,bary,barz]
    }

def orbit_design(n,seed=20261019):
    """Gauge-invariant physical orbital samples on x+y+s=1, |z|²<=xy."""
    if n<256:raise ValueError('Use >=256 orbit samples')
    rng=np.random.default_rng(seed)
    fractions=rng.dirichlet((.7,.7,.7),size=n)
    xx,yy,ss=fractions.T
    rho=rng.uniform(0,1,n)
    phase=rng.uniform(-np.pi,np.pi,n)
    zr=np.sqrt(xx*yy)*rho*np.cos(phase)
    zi=np.sqrt(xx*yy)*rho*np.sin(phase)
    q=np.column_stack((xx,yy,ss,zr,zi))
    pure=np.array([[1,0,0,0,0],[0,1,0,0,0],[0,0,1,0,0]],float)
    edge=[]
    # Border |z|=sqrt(xy), singlet=0 and mixed three-orbit slices.
    for x,y,s in ((.5,.5,0.),(.333,.333,.334),
                  (.8,.1,.1),(.1,.8,.1),(.1,.1,.8)):
        for ph in (0.,math.pi/4,math.pi/2,3*math.pi/4,
                   math.pi,5*math.pi/4,3*math.pi/2,7*math.pi/4):
            z=math.sqrt(x*y)*np.exp(1j*ph)
            edge.append((x,y,s,z.real,z.imag))
            edge.append((x,y,s,.5*z.real,.5*z.imag))
    q=np.vstack((q,pure,np.asarray(edge,float)))
    if np.max(abs(q[:,:3].sum(axis=1)-1))>1e-12:
        raise AssertionError('Improper scalar orbit normalization')
    if np.max(q[:,3]**2+q[:,4]**2-q[:,0]*q[:,1])>1e-12:
        raise AssertionError('Impossible Higgs-doublet orbital points')
    return q

def quartic_orbit_values(q,orbits):
    C=tensor_for_quartics(q)
    x=np.asarray(orbits,float)
    if x.ndim!=2 or x.shape[1]!=5:
        raise ValueError('Physical quartic orbit must be N x 5')
    return np.einsum('ni,ij,nj->n',x,C,x,optimize=True)

def quartic_bfb(state,orbits):
    q={k:state[k] for k in PHYSICAL_QUARTICS}
    M=quartic_lower_bound_matrix(q)
    is_sufficient,proof=copositive_3x3(M)
    values=quartic_orbit_values(q,orbits)
    arg=int(np.argmin(values))
    minimum=float(values[arg])
    scale=max(1.,max(abs(q[k]) for k in PHYSICAL_QUARTICS))
    if minimum<-(1e-9*scale):
        verdict='BFB_NEGATIVE_WITNESS'
    elif is_sufficient:
        verdict='BFB_SUFFICIENT_CERTIFIED'
    else:
        verdict='BFB_INCONCLUSIVE'
    return {'verdict':verdict,'sample_min_v4_normalized':minimum,
            'sample_minimizer_orbit':[float(v) for v in orbits[arg]],
            'sufficient_lower_bound_matrix':M.tolist(),
            'copositivity_lower_bound':bool(is_sufficient),
            'copositivity_details':proof,
            'tested_physical_orbits':len(orbits)}

def path_with_bfb(mod,start,*,mu0,upper,steps,orbits):
    if steps<8 or not(0<mu0<upper):raise ValueError('Invalid UV path')
    dt=math.log(upper/mu0)/steps
    current=start
    trace=[]
    stop=None
    for i in range(steps+1):
        mu=mu0*math.exp(i*dt)
        bfb=quartic_bfb(current,orbits)
        trace.append({
            'step':i,'mu_GeV':mu,'bfb_verdict':bfb['verdict'],
            'min_sampled_quartic':bfb['sample_min_v4_normalized'],
            'orbit_witness':(bfb['sample_minimizer_orbit'] if
                bfb['verdict']=='BFB_NEGATIVE_WITNESS' else None),
            'copositive_sufficient':bfb['copositivity_lower_bound'],
            'largest_couplings':limiting_couplings(current,3),
            'abs_lambda6':abs(current['l6']),
            'abs_lambda7':abs(current['l7'])
        })
        if bfb['verdict']=='BFB_NEGATIVE_WITNESS':
            stop='NEGATIVE_QUARTIC_WITNESS'
            break
        if i==steps:
            break
        if numerical_control(current):
            stop='PERTURBATIVITY_CONTROL_AT_SAMPLE'
            break
        try:
            nxt=rk4_step(mod,current,dt)
        except (ValueError,OverflowError,FloatingPointError) as exc:
            stop='NUMERICAL_INTEGRATION_FAILURE:'+type(exc).__name__
            break
        if numerical_control(nxt):
            stop='PERTURBATIVITY_CONTROL_IN_SUBSTEP'
            break
        current=nxt
    n=collections.Counter(t['bfb_verdict'] for t in trace)
    all_certified=(stop is None and
                   n['BFB_SUFFICIENT_CERTIFIED']==steps+1)
    no_witness=(n['BFB_NEGATIVE_WITNESS']==0)
    return {
        'status':('COMPLETE_TO_TARGET' if stop is None else stop),
        'certified_sufficient_at_all_steps':all_certified,
        'no_negative_witness_at_sampled_steps':no_witness,
        'num_certified_steps':n['BFB_SUFFICIENT_CERTIFIED'],
        'num_inconclusive_steps':n['BFB_INCONCLUSIVE'],
        'num_negative_witness_steps':n['BFB_NEGATIVE_WITNESS'],
        'first_uncertified_mu_GeV':next(
            (x['mu_GeV'] for x in trace
             if x['bfb_verdict']!='BFB_SUFFICIENT_CERTIFIED'),None),
        'first_negative_witness_mu_GeV':next(
            (x['mu_GeV'] for x in trace
             if x['bfb_verdict']=='BFB_NEGATIVE_WITNESS'),None),
        'final_mu_GeV':trace[-1]['mu_GeV'],
        'trajectory':trace,
    }

def verify_c2(report,b4,b2,rge):
    obj=json.loads(Path(report).read_text())
    proven=obj.get('provenance',{})
    if (obj.get('tested_interventions')!=240 or len(obj.get('rows',[]))!=240
        or obj.get('status')!='GATE_C2_PAIRED_ZEE_SCALAR_RESCUE_ONE_LOOP_DIAGNOSTIC_NOT_ALLOWED'
        or proven.get('B4')!=digest(b4) or proven.get('B2')!=digest(b2)
        or proven.get('RGE_source')!=digest(rge)):
        raise ValueError('C2 report does not match 240-pair experiment and exact inputs')
    mapping={}
    for record in obj['rows']:
        key=(record.get('candidate_id'),record.get('variant'))
        if key in mapping:
            raise ValueError('C2 duplicate spectrum-variant record')
        mapping[key]=record
    if len(mapping)!=240:raise ValueError('Incomplete C2 mapping')
    return mapping

def summarise(rows):
    variants={}
    for name in TARGET_VARIANTS:
        selected=[x for x in rows if x['variant']==name]
        variants[name]={
            'tested':len(selected),
            'reached_10TeV_heuristic':sum(
                x['C2_heuristic_reached_10TeV'] for x in selected),
            'certified_quartic_BFB_along_all_sampled_steps':sum(
                x['certified_quartic_BFB_along_sampled_path'] for x in selected),
            'explicit_negative_quartic_witness_found':sum(
                x['any_explicit_negative_witness'] for x in selected),
            'no_explicit_negative_witness_but_not_certified':sum(
                x['no_witness_but_uncertified'] for x in selected),
            'not_reaching_10TeV':sum(
                not x['C2_heuristic_reached_10TeV'] for x in selected),
        }
    return {
        'variants':variants,
        'full_physical_Zee_benchmarks_allowed':None,
        'running_full_11_quartic_BFB_sufficiency_is_only_a_sufficient_test':True,
        'negative_witness_is_conclusive_if_present':True,
        'no_negative_witness_is_not_a_stability_proof':True,
        'full_11_quartic_tree_unitarity_not_computed':True,
        'global_vacuum_and_flavor_not_computed':True,
        'crossing_frequency_from_cherry_picked_cascade_sample_NOT_Zee_model_coverage':True,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--b4-csv',type=Path,required=True)
    p.add_argument('--b2-json',type=Path,required=True)
    p.add_argument('--generator-output',type=Path,required=True)
    p.add_argument('--q4v13-report',type=Path,required=True)
    p.add_argument('--c2-summary',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--max-spectra',type=int,default=30)
    p.add_argument('--steps',type=int,default=24)
    p.add_argument('--orbit-samples',type=int,default=2048)
    p.add_argument('--upper-GeV',type=float,default=10000.)
    a=p.parse_args()
    if (a.max_spectra<1 or a.max_spectra>30 or
        a.steps<8 or a.steps>120 or a.steps%4 or
        a.orbit_samples<256 or a.orbit_samples>32768 or
        a.upper_GeV<=1000):
        p.error('Invalid requested C3 diagnostic parameters')
    if a.output_dir.exists() and any(a.output_dir.iterdir()):
        p.error('Refuse to overwrite a nonempty output directory')
    a.output_dir.mkdir(parents=True,exist_ok=True)
    summary={'status':STATUS,'physically_allowed':None,
             'UV_vacuum_global_minimum':'NOT_EVALUATED',
             'general_complex_tree_unitarity':'NOT_EVALUATED',
             'full_LFV_mesons_HiggsTools':'NOT_EVALUATED',
             'threshold_matching_and_CKM':'NOT_EVALUATED'}
    try:
        source=find_rges(a.generator_output)
        summary['Q4_exact_source']=verify_rge_validation(a.q4v13_report,source)
        c2=verify_c2(a.c2_summary,a.b4_csv,a.b2_json,source)
        points,sols,names=load_cohort(a.b4_csv,a.b2_json,a.max_spectra)
        module=load_generated(source)
        orbits=orbit_design(a.orbit_samples)
        rows=[]
        for i,name in enumerate(names,1):
            point=points[name]
            solution=sols[name][0]
            if str(solution.get('candidate_id'))!=name:
                raise ValueError('Neutrino family mismatch for '+name)
            for label in TARGET_VARIANTS:
                variant=next(x for x in VARIANTS if x[0]==label)
                pnt=varied_point(point,variant[1],variant[2])
                initial,checks=build_model_state(pnt,solution)
                previous=c2[(name,label)]
                coarse=path_with_bfb(module,initial,
                    mu0=pnt['mH2'],upper=a.upper_GeV,steps=a.steps,
                    orbits=orbits)
                # Valid original C2 heuristic-to-10TeV interpretation is
                # checked independently against this new trajectory.
                c2_pass=bool(previous['reached_10TeV_heuristic'])
                observed=(coarse['status']=='COMPLETE_TO_TARGET' or
                          coarse['status']=='NEGATIVE_QUARTIC_WITNESS')
                # Explicit negative witness may stop earlier: C2 outcome
                # remains authoritative for the independent coupling bound.
                if (not c2_pass and coarse['status']=='COMPLETE_TO_TARGET'):
                    raise ValueError('C2/C3 disagree on perturbativity barrier')
                if (coarse['status']=='PERTURBATIVITY_CONTROL_IN_SUBSTEP' and c2_pass):
                    raise ValueError('C2/C3 disagree on 10 TeV acceptance')
                row={
                    'candidate_id':name,'variant':label,
                    'C2_heuristic_reached_10TeV':c2_pass,
                    'C3_path_status':coarse['status'],
                    'certified_quartic_BFB_along_sampled_path':
                        coarse['certified_sufficient_at_all_steps'],
                    'any_explicit_negative_witness':
                        not coarse['no_negative_witness_at_sampled_steps'],
                    'no_witness_but_uncertified':bool(
                        coarse['no_negative_witness_at_sampled_steps'] and
                        not coarse['certified_sufficient_at_all_steps']),
                    'num_BFB_certified':coarse['num_certified_steps'],
                    'num_BFB_inconclusive':coarse['num_inconclusive_steps'],
                    'num_BFB_negative_witness':coarse['num_negative_witness_steps'],
                    'first_uncertified_mu_GeV':coarse['first_uncertified_mu_GeV'],
                    'first_negative_witness_mu_GeV':coarse['first_negative_witness_mu_GeV'],
                    'last_BFB_evaluated_mu_GeV':coarse['final_mu_GeV'],
                    'lambda1_matching':float(initial['l1']),
                    'lambda_h_matching':float(initial['lh']),
                    'muZee_matching_GeV':abs(initial['muZee']),
                    'nu_closure_eV':checks['neutrino_matrix_closure_eV'],
                    'C2_provisional_cascade_proxy_LO_included_only':
                        (previous.get('partial_widths') or {}).get(
                            'production_weighted_cascade_proxy_LO_included_only'),
                    'physically_allowed':'UNKNOWN',
                }
                rows.append(row)
                print('C3_RUNNING_COMPLEX_BFB',f'{i}/{len(names)}',
                      name,label,
                      'C2_10TeV_heuristic',c2_pass,
                      'BFB',coarse['status'],
                      'sufficient_all',coarse['certified_sufficient_at_all_steps'],
                      'negative_witness',row['any_explicit_negative_witness'],
                      'first_not_certified_GeV',row['first_uncertified_mu_GeV'],
                      flush=True)
        summary.update({'tested':len(rows),'rows':rows,
                        'cohort':summarise(rows),
                        'provenance':{k:digest(v) for k,v in (
                            ('B4',a.b4_csv),('B2',a.b2_json),
                            ('C2',a.c2_summary),('RGEs',source))},
                        'orbit_samples':len(orbits)})
        columns=list(rows[0])
        filename=a.output_dir/'running_BFB_diagnostics_NOT_ALLOWED.csv'
        with filename.open('w',newline='') as stream:
            w=csv.DictWriter(stream,fieldnames=columns)
            w.writeheader();w.writerows(rows)
        summary['csv']=str(filename)
        print('C3_ALL_CASES',len(rows),
              'C3_COHORT',json.dumps(summary['cohort']['variants']),
              flush=True)
        print('C3_FULL_PHYSICAL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as exc:
        summary.update(status='GATE_C3_FAILED_CLOSED_NOT_ALLOWED',
                       error=repr(exc),traceback=traceback.format_exc())
        print('C3_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        file=a.output_dir/'summary.json'
        file.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        print('C3_SUMMARY',file)

if __name__=='__main__':
    raise SystemExit(main())
