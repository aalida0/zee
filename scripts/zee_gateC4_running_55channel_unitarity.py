#!/usr/bin/env python3
"""Gate C4: FULL general-complex Zee tree-level scalar 2->2 unitarity in RG flow.

Construct the complete 55 x 55 symmetric two-particle contact-amplitude
matrix for the 10 CANONICALLY NORMALIZED REAL scalar fields of the general
Zee model (two complex SU2 doublets, one complex charged singlet).

For q_a=(1/2)phi_i A^a_ij phi_j and V4=q^T C q, the fourth derivative is
  T_ijkl = 2 sum_ab C_ab *
      (A^a_ij A^b_kl + A^a_ik A^b_jl + A^a_il A^b_jk).
Pair states |ij> are normalized with 1/sqrt(1+delta_ij).
M_(ij),(kl) = T_ijkl /
                  sqrt[(1+delta_ij)(1+delta_kl)].
Eigenvalues of this matrix are to be compared to 8*pi for a0=M/(16*pi).

Calibration: the restricted 2021 Gate6 benchmark yields EXACT same
maximum absolute eigenvalue, 18.13677908573, as its published Appendix
C Q2Y1/Q1Y1/Q1Y0/Q0Y0 scattering blocks. General complex l5,6,7,10
are supported here even when generated radiatively.

For 30 C2-rescued spectra x 2 potential counterfactuals, evolve the full
26 one-loop Zee RGEs toward 10 TeV and check at every scale:
  (a) the complete 55x55 contact scattering eigenvalue bound <8pi,
  (b) the Gate C3 conservative complex-quartic BFB certificate or a
      concrete gauge-orbit negative witness,
  (c) the C2 perturbativity heuristic |quartic|<4pi.
If the unitarity bound crosses during a step before the perturbative
stop, bracket the crossing using RK4 bisection. Do not conflate tree
unitarity at a running scale with full physical S-matrix unitarity.

All matches and safety reports are provenance-locked to C3 / C2 /
Q4v13 with unchanged B4, B2, RGE hashes and shared trajectory inputs.
No candidate receives a physical Zee-model ALLOWED designation:
LFV, B->Xs gamma, HiggsTools, EWPO global fit, thresholds, CKM
matching, global charge-breaking vacuum are still incomplete.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
import math
import sys
import traceback
from pathlib import Path
import numpy as np

from zee_section8_Q4_independent_scalar_hessian_gate import (
    A,PHYSICAL_QUARTICS,tensor_for_quartics
)
from zee_gateC3_running_complex_bfb import (
    TARGET_VARIANTS,orbit_design,quartic_bfb,verify_c2
)
from zee_gateC2_paired_uv_rescue import (
    VARIANTS,load_cohort,varied_point
)
from zee_gateC1_joined_uv_pilot import (
    build_model_state,digest,verify_rge_validation,
    numerical_control,limiting_couplings
)
from zee_section8_Q4_generated_source_limit_probe import find_rges,load_generated
from zee_section8_Q4_large_integrated_one_loop_gate import rk4_step

STATUS='GATE_C4_FULL_COMPLEX_55CHANNEL_RUNNING_SCALAR_UNITARITY_NOT_ALLOWED'
N_FIELDS=10
PAIR_I,PAIR_J=np.triu_indices(N_FIELDS)
N_PAIRS=len(PAIR_I)
NORMALIZATION=np.sqrt(
    (1.+(PAIR_I==PAIR_J).astype(float))[:,None] *
    (1.+(PAIR_I==PAIR_J).astype(float))[None,:]
)
LIMIT=8*math.pi
# Geometry-only, quartic-independent response of all pair channels:
# contact response is linear in the 15 real quartic degrees of freedom.
def amplitude_response():
    vectors=np.zeros((N_PAIRS,N_PAIRS,5,5),float)
    for a in range(5):
        for b in range(5):
            Aa=A[a];Ab=A[b]
            m=np.empty((N_PAIRS,N_PAIRS),float)
            for i,(p,q) in enumerate(zip(PAIR_I,PAIR_J)):
                r,s=PAIR_I,PAIR_J
                m[i]=2*(Aa[p,q]*Ab[r,s]+Aa[p,r]*Ab[q,s]+Aa[p,s]*Ab[q,r])
            vectors[:,:,a,b]=m/NORMALIZATION
    return vectors

RESPONSE=amplitude_response()

def scatter_matrix(quartics):
    C=tensor_for_quartics(quartics)
    result=np.einsum('ijab,ab->ij',RESPONSE,C,optimize=True)
    if result.shape!=(55,55) or np.max(abs(result-result.T))>2e-10:
        raise ValueError('10-real-field scalar amplitude not symmetric')
    return .5*(result+result.T)

def scattering_eigenvalues(quartics):
    return np.linalg.eigvalsh(scatter_matrix(quartics))

def scattering_limit(state):
    q={k:state[k] for k in PHYSICAL_QUARTICS}
    eig=scattering_eigenvalues(q)
    arg=int(np.argmax(abs(eig)))
    limit=float(abs(eig[arg]))
    return {
        'max_abs_eigenvalue':limit,
        'leading_eigenvalue_signed':float(eig[arg]),
        'a0_max_abs':limit/(16*math.pi),
        'ratio_to_8pi':limit/LIMIT,
        'passes_strict_8pi':bool(limit<LIMIT),
        'eigenvalue_count':len(eig),
    }

def locate_unitarity_crossing(mod,start,delta,mu0,iterations=12):
    """Bisection on a contiguous RGE step with a strict 8pi crossing."""
    at0=scattering_limit(start)
    if not at0['passes_strict_8pi']:
        return {
            'first_failure_GeV':float(mu0),
            'lower_GeV':float(mu0),
            'upper_GeV':float(mu0),
            'relative_bracket_width':0.,
            'failure_eigenvalue':at0['max_abs_eigenvalue'],
        }
    low=0.;high=delta
    for _ in range(iterations):
        mid=(low+high)/2
        s=rk4_step(mod,start,mid)
        if scattering_limit(s)['passes_strict_8pi']:
            low=mid
        else:
            high=mid
    crossing=float(mu0*math.exp((low+high)/2))
    return {
        'first_failure_GeV':crossing,
        'lower_GeV':float(mu0*math.exp(low)),
        'upper_GeV':float(mu0*math.exp(high)),
        'relative_bracket_width':float(math.exp(high-low)-1),
    }

def full_trajectory(mod,start,*,mu0,upper,steps,orbits):
    """Measure complete BFB and unitarity paths even *after* unitarity fails."""
    if steps<4 or not(0<mu0<upper):
        raise ValueError('Bad C4 running scales')
    delta=math.log(upper/mu0)/steps
    trace=[]
    s=start
    crossing=None
    reason=None
    for n in range(steps+1):
        mu=float(mu0*math.exp(delta*n))
        bound=quartic_bfb(s,orbits)
        eig=scattering_limit(s)
        trace.append({
            'step':n,'mu_GeV':mu,
            'max_eigenvalue':eig['max_abs_eigenvalue'],
            'unitarity_ratio_to_8pi':eig['ratio_to_8pi'],
            'unitarity_pass':eig['passes_strict_8pi'],
            'BFB_verdict':bound['verdict'],
            'BFB_copositive_sufficient':bound['copositivity_lower_bound'],
            'min_sampled_quartic':bound['sample_min_v4_normalized'],
            'top_couplings':limiting_couplings(s,3),
            'abs_lambda6':float(abs(s['l6'])),
            'abs_lambda7':float(abs(s['l7'])),
            'abs_lambda10':float(abs(s['l10'])),
        })
        if n==0 and not eig['passes_strict_8pi']:
            crossing=locate_unitarity_crossing(mod,s,delta,mu)
        if n>0 and not eig['passes_strict_8pi'] and crossing is None:
            # Use prior accepted start of segment and independently
            # RK4 bisection. This estimates a tree-level scale bound.
            previous=previous_state
            crossing=locate_unitarity_crossing(
                mod,previous,delta,float(mu0*math.exp(delta*(n-1))))
        if bound['verdict']=='BFB_NEGATIVE_WITNESS':
            reason='EXPLICIT_QUARTIC_INSTABILITY_WITNESS'
            break
        if n==steps:break
        if numerical_control(s):
            reason='NUMERICAL_PERTURBATIVITY_HEURISTIC_REACHED'
            break
        previous_state=s
        try:
            nxt=rk4_step(mod,s,delta)
            if numerical_control(nxt):
                reason='NUMERICAL_PERTURBATIVITY_HEURISTIC_IN_STEP'
                break
        except (ValueError,OverflowError,FloatingPointError) as exc:
            reason='INTEGRATOR_ERROR_'+type(exc).__name__
            break
        s=nxt
    bfb=collections.Counter(t['BFB_verdict'] for t in trace)
    reached=(reason is None and trace[-1]['step']==steps)
    certified=(reached and bfb['BFB_SUFFICIENT_CERTIFIED']==steps+1)
    unitary=(reached and all(x['unitarity_pass'] for x in trace))
    return {
        'status':'COMPLETE_TO_10TEV' if reached else
                 ('STOPPED_'+str(reason)),
        'reached_end_scale':reached,
        'BFB_sufficient_at_all_sampled_steps':certified,
        'tree_unitarity_8pi_at_all_sampled_steps':unitary,
        'BFB_negative_witness':bfb['BFB_NEGATIVE_WITNESS']>0,
        'first_tree_unitarity_crossing':crossing,
        'maximum_scattering_eigenvalue_encountered':
            max(x['max_eigenvalue'] for x in trace),
        'max_abs_eigenvalue_at_matching':trace[0]['max_eigenvalue'],
        'max_abs_eigenvalue_at_last_recorded_scale':trace[-1]['max_eigenvalue'],
        'sampled_steps':len(trace),
        'first_BFB_uncertified_scale_GeV':next(
            (x['mu_GeV'] for x in trace if x['BFB_verdict']!='BFB_SUFFICIENT_CERTIFIED'),
            None),
        'first_tree_unitarity_uncertified_scale_GeV':next(
            (x['mu_GeV'] for x in trace if not x['unitarity_pass']),None),
        'trace':trace,
    }

def verify_c3(path,b4,b2,c2,rge):
    obj=json.loads(Path(path).read_text())
    prov=obj.get('provenance',{})
    if (obj.get('status')!='GATE_C3_COMPLEX_QUARTIC_RUNNING_BFB_DIAGNOSTIC_NOT_ALLOWED'
        or obj.get('tested')!=60 or len(obj.get('rows',[]))!=60
        or prov.get('B4')!=digest(b4) or
           prov.get('B2')!=digest(b2) or
           prov.get('C2')!=digest(c2) or
           prov.get('RGEs')!=digest(rge)):
        raise ValueError('C3 reference does not match exact B4/B2/C2/RGEs inputs')
    mapping={}
    for row in obj['rows']:
        key=(row.get('candidate_id'),row.get('variant'))
        if key in mapping:raise ValueError('Duplicate C3 candidate/variant')
        mapping[key]=row
    if len(mapping)!=60:raise ValueError('C3 missing cases')
    return mapping

def cohort_summary(rows):
    summary={}
    for variant in TARGET_VARIANTS:
        subset=[r for r in rows if r['variant']==variant]
        summary[variant]={
            'tested':len(subset),
            'reach_10TeV_C2_heuristic':sum(r['C2_10TeV_heuristic'] for r in subset),
            'C3_BFB_sufficient_at_all_sampled_scales':sum(r['C3_BFB_sufficient_all'] for r in subset),
            'full_55x55_unitarity_through_10TeV':sum(r['full_55x55_unitarity_through_10TeV'] for r in subset),
            'both_BFB_and_full_tree_unitarity_through_10TeV':sum(r['both_running_theory_screens_pass'] for r in subset),
            'initial_55x55_unitarity_failures':sum(not r['unitary_at_matching'] for r in subset),
            'first_tree_unitarity_crossings_recorded':sum(r['unitarity_crossing_GeV'] is not None for r in subset),
        }
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--b4-csv',type=Path,required=True)
    p.add_argument('--b2-json',type=Path,required=True)
    p.add_argument('--generator-output',type=Path,required=True)
    p.add_argument('--q4v13-report',type=Path,required=True)
    p.add_argument('--c2-summary',type=Path,required=True)
    p.add_argument('--c3-summary',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--max-spectra',type=int,default=30)
    p.add_argument('--steps',type=int,default=24)
    p.add_argument('--orbit-samples',type=int,default=2048)
    p.add_argument('--upper-GeV',type=float,default=10000.)
    a=p.parse_args()
    if (not(1<=a.max_spectra<=30 and 8<=a.steps<=96 and a.steps%4==0
           and 256<=a.orbit_samples<=32768 and a.upper_GeV>=10000)):
        p.error('Invalid unitarity audit parameters')
    if a.output_dir.exists() and any(a.output_dir.iterdir()):
        p.error('Refusing to overwrite a nonempty output directory')
    a.output_dir.mkdir(parents=True,exist_ok=True)
    result={'status':STATUS,'physical_Zee_allowed':None,
            'EFT_thresholds':'NOT_EVALUATED',
            'global_charge_breaking_vacuum':'NOT_EVALUATED',
            'full_LFV_neutrino_fit':'NOT_EVALUATED',
            'quark_CKM_matched_flavor':'NOT_EVALUATED',
            'HiggsTools_and_experimental_constraints':'NOT_EVALUATED',
            'general_complex_unitarity':'EVALUATED_ONLY_AT_TREE_AND_SAMPLED_SCALES'}
    try:
        rge=find_rges(a.generator_output)
        result['Q4v13_provenance']=verify_rge_validation(a.q4v13_report,rge)
        c2=verify_c2(a.c2_summary,a.b4_csv,a.b2_json,rge)
        c3=verify_c3(a.c3_summary,a.b4_csv,a.b2_json,a.c2_summary,rge)
        points,sols,names=load_cohort(a.b4_csv,a.b2_json,a.max_spectra)
        mod=load_generated(rge)
        orbits=orbit_design(a.orbit_samples)
        rows=[]
        for i,name in enumerate(names,1):
            for variant in TARGET_VARIANTS:
                vv=next(v for v in VARIANTS if v[0]==variant)
                pot=varied_point(points[name],vv[1],vv[2])
                first,checks=build_model_state(pot,sols[name][0])
                previous_c2=c2[(name,variant)]
                previous_c3=c3[(name,variant)]
                if (not previous_c2.get('RGE_stepdoubling_compatible') or
                    previous_c2.get('status')!='UV_DIAGNOSTIC_SOLVER_STABLE_NOT_ALLOWED'):
                    raise ValueError('C2 model trajectory not numerically certified')
                check=full_trajectory(mod,first,mu0=pot['mH2'],
                                      upper=a.upper_GeV,steps=a.steps,orbits=orbits)
                refined=full_trajectory(mod,first,mu0=pot['mH2'],
                                      upper=a.upper_GeV,steps=2*a.steps,orbits=orbits)
                if check['reached_end_scale']!=refined['reached_end_scale']:
                    raise ValueError('C4 RK4 coarse/refined reaching target disagreement')
                c0=check['first_tree_unitarity_crossing']
                c1=refined['first_tree_unitarity_crossing']
                if (c0 is None)!=(c1 is None):
                    raise ValueError('C4 coarse/refined classification of unitarity crossing differs')
                crossing_delta=None
                if c0 is not None:
                    u=c0['first_failure_GeV'];v=c1['first_failure_GeV']
                    crossing_delta=abs(u-v)/max(1.,u,v)
                    if crossing_delta>.05:
                        raise ValueError('C4 coarse/refined unitarity crossing discrepancy >5%')
                if check['BFB_negative_witness'] != refined['BFB_negative_witness']:
                    raise ValueError('C4 coarse/refined negative BFB witness differs')
                if (check['reached_end_scale'] !=
                    bool(previous_c2['reached_10TeV_heuristic'])):
                    raise ValueError('C4/C2 perturbativity contradiction '+name+'/'+variant)
                if (check['BFB_sufficient_at_all_sampled_steps'] !=
                    bool(previous_c3['certified_quartic_BFB_along_sampled_path'])):
                    raise ValueError('C4/C3 full-quartic BFB contradiction '+name+'/'+variant)
                crossing=check['first_tree_unitarity_crossing']
                row={
                    'candidate_id':name,'variant':variant,
                    'C2_10TeV_heuristic':bool(previous_c2['reached_10TeV_heuristic']),
                    'C3_BFB_sufficient_all':bool(previous_c3['certified_quartic_BFB_along_sampled_path']),
                    'C4_trajectory_status':check['status'],
                    'unitary_at_matching':check['max_abs_eigenvalue_at_matching']<LIMIT,
                    'max_55channel_eigenvalue_initial':check['max_abs_eigenvalue_at_matching'],
                    'max_55channel_eigenvalue_seen':check['maximum_scattering_eigenvalue_encountered'],
                    'max_55channel_eigenvalue_final_record':check['max_abs_eigenvalue_at_last_recorded_scale'],
                    'unitarity_crossing_GeV':crossing['first_failure_GeV'] if crossing else None,
                    'unitarity_crossing_relative_bracket_width':crossing['relative_bracket_width'] if crossing else None,
                    'full_55x55_unitarity_through_10TeV':bool(
                        check['tree_unitarity_8pi_at_all_sampled_steps'] and
                        refined['tree_unitarity_8pi_at_all_sampled_steps']),
                    'both_running_theory_screens_pass':bool(
                        check['tree_unitarity_8pi_at_all_sampled_steps'] and
                        refined['tree_unitarity_8pi_at_all_sampled_steps'] and
                        check['BFB_sufficient_at_all_sampled_steps'] and
                        refined['BFB_sufficient_at_all_sampled_steps']),
                    'refined_48_step_BFB_certified':refined['BFB_sufficient_at_all_sampled_steps'],
                    'refined_48_step_55channel_unitary':refined['tree_unitarity_8pi_at_all_sampled_steps'],
                    'unitarity_RK4_coarse_refined_relative_crossing_scale_delta':crossing_delta,
                    'BFB_negative_witness':bool(
                        check['BFB_negative_witness'] or refined['BFB_negative_witness']),
                    'first_BFB_uncertified_scale_GeV':check['first_BFB_uncertified_scale_GeV'],
                    'first_unitarity_uncertified_sample_GeV':check['first_tree_unitarity_uncertified_scale_GeV'],
                    'first_limit_diagnostic':(
                        'TREE_UNITARITY_8PI' if crossing is not None and (
                            previous_c2.get('estimated_4pi_crossing_GeV') is None or
                            crossing['first_failure_GeV'] <
                                previous_c2['estimated_4pi_crossing_GeV'])
                        else 'QUARTIC_OR_YUKAWA_4PI_DIAGNOSTIC'
                        if previous_c2.get('estimated_4pi_crossing_GeV') is not None
                        else 'NO_TESTED_LIMIT_CROSSED_BEFORE_10TEV'),
                    'physical_Zee_allowed':'UNKNOWN',
                    'global_vacuum_and_flavor':'NOT_EVALUATED',
                }
                rows.append(row)
                print('C4_FULL_COMPLEX_UNITARITY',f'{i}/{len(names)}',name,variant,
                      'BFB_sufficient',row['C3_BFB_sufficient_all'],
                      'unitarity_matching',row['unitary_at_matching'],
                      'unitarity_10TeV',row['full_55x55_unitarity_through_10TeV'],
                      'first_unitarity_crossing_GeV',row['unitarity_crossing_GeV'],
                      'max_eigen_seen',row['max_55channel_eigenvalue_seen'],
                      'physical_allowed_UNKNOWN',flush=True)
        result.update({'cases':rows,'tested':len(rows),
                       'cohort':cohort_summary(rows),
                       'number_real_scalar_fields':N_FIELDS,
                       'number_symmetric_two_scalar_channels':N_PAIRS,
                       's_wave_real_tree_eigenvalue_limit_8pi':LIMIT,
                       'quartic_BFB_sufficient_only_at_sampled_scales':True,
                       'source_checksums':{
                          'B4':digest(a.b4_csv),'B2':digest(a.b2_json),
                          'C2':digest(a.c2_summary),'C3':digest(a.c3_summary),
                          'RGEs':digest(rge)}})
        columns=list(rows[0])
        target=a.output_dir/'running_55channel_unitarity_NOT_ALLOWED.csv'
        with target.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=columns)
            writer.writeheader();writer.writerows(rows)
        result['csv']=str(target)
        print('C4_FULL_COMPLEX_CHANNELS',N_PAIRS)
        print('C4_COMPLETE',len(rows),'COHORT',json.dumps(result['cohort']))
        print('C4_PHYSICAL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as exc:
        result.update(status='GATE_C4_FAIL_CLOSED_NOT_ALLOWED',
                      error=repr(exc),traceback=traceback.format_exc())
        print('C4_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        dst=a.output_dir/'summary.json'
        dst.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('C4_SUMMARY',dst,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
