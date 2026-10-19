#!/usr/bin/env python3
"""Gate C2: paired UV-perturbativity RESCUE experiment, not an allowed Zee scan.

Scientific question: C1 v2 found 30/30 selected scalar spectra cross the
heuristic |lambda|=4*pi boundary below 10 TeV, driven by lh (18/30)
or l1 (12/30). Can we rescue these SAME charged-scalar masses and
mixing by decreasing the charged-singlet self quartic lh=lc and/or
tuning the neutral-doublet quartic l1, while retaining tree
boundedness, unitarity and the same exact neutrino-mass closure?

Use 30 existing B4 spectra. For each, construct 8 PAIRED counterfactual
scalar potentials (240 candidates) with unchanged charged H1/H2 masses,
neutral h/H/A masses, alpha, beta, gamma and therefore unchanged S,T,U
and neutrino loop prefactor. Only lc and/or soft m12sq are varied.
To target a desired lambda1, analytically invert the tree scalar
mass reconstruction:
 m12sq=(m_h^2 cos^2(alpha)+m_H^2 sin^2(alpha)
               - target_l1 * v^2 cos^2(beta))/tan(beta).
This preserves physical tree masses by reconstructing all other
lambda1..5 consistently; it changes the scalar potential and cubic
decay rates. Never claim that all original constraints remain valid.

Each variant is independently required to satisfy the SAME Gate6
sufficient BFB, tree unitarity and reconstructed mass eigenvalues
before running the complete PyR@TE-saved Zee 26-equation one-loop RGE.
For retained spectra the B2 (f,Y) neutrino matrix is rechecked and
complex lepton Yukawas are re-rotated into the symmetry RGE basis.
Each RGE is integrated with 24/48 (configurable) RK4 steps up to 10 TeV,
with exact heuristic first-crossing bisection and convergence checks.

A saved C1 90-solution cohort report with matching B4/B2 hashes is
REQUIRED; original baseline rank1 crossing and driver are reproduced
within explicit tolerance before comparing counterfactuals.

The potential scan is PAIRED, SELECTED, NOT representative of the
complete Zee parameter space, and uses C1 toy CKM=I quark inputs.
Passing to 10 TeV is ONE-LOOP HEURISTIC ONLY, NOT validated physical
UV consistency or allowed Zee physics: no full LFV, HiggsTools,
modern two-charged b->s gamma, global minimum, scale-dependent
complex BFB/unitarity, CKM, threshold matching or collider likelihood.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import math
import statistics
import sys
import traceback
from pathlib import Path
import numpy as np

from gateB3_general_zee_charged_lepton_widths import (
    complex_matrix,evaluate as provisional_widths,read_b1
)
from gateA1b_hierarchical_no_seed import target_neutrino_matrix
from zee_section8_Q4_generated_source_limit_probe import find_rges,load_generated
from zee_gateC1_joined_uv_pilot import (
    VEV,digest,scalar_lagrangian,build_model_state,run_flow,vector_distance,
    verify_rge_validation,QUARTIC_KEYS
)

STATUS='GATE_C2_PAIRED_ZEE_SCALAR_RESCUE_ONE_LOOP_DIAGNOSTIC_NOT_ALLOWED'
# (name, max_lh, lambda1_target)
VARIANTS=(
    ('baseline',None,None),
    ('cap_lh_1',1.,None),
    ('cap_lh_0p4',.4,None),
    ('target_l1_1',None,1.),
    ('target_l1_0p5',None,.5),
    ('both_lh1_l1_1',1.,1.),
    ('both_lh0p4_l1_1',.4,1.),
    ('both_lh0p4_l1_0p5',.4,.5),
)

def varied_point(base,max_lh,target_l1):
    p=dict(base)
    # Do not accidentally make an already-small singlet quartic larger.
    if max_lh is not None:
        p['lc']=min(float(base['lc']),float(max_lh))
    if target_l1 is not None:
        alpha,beta=float(base['alpha']),float(base['beta'])
        m11=125.**2*math.cos(alpha)**2+float(base['mh2'])**2*math.sin(alpha)**2
        soft=(m11-target_l1*VEV**2*math.cos(beta)**2)/math.tan(beta)
        if not(math.isfinite(soft) and soft>0):
            raise ValueError('lambda1 target requires nonpositive soft mass')
        p['m12sq']=float(soft)
    if max_lh is not None or target_l1 is not None:
        # Cached B4 inverse-lambda input is valid ONLY for baseline.
        for i in range(1,6):p.pop(f'lambda{i}',None)
    return p

def read_cohort_reference(path,b4,b2,rges):
    data=json.loads(Path(path).read_text())
    if (data.get('B4_sha256')!=digest(b4)
        or data.get('B2_sha256')!=digest(b2)
        or data.get('RGE_sha256')!=digest(rges)
        or data.get('row_count')!=90
        or len(data.get('rows',[]))!=90):
        raise ValueError('C1 90-solution cohort has different inputs/RGEs or missing records')
    expected={}
    for row in data['rows']:
        if row.get('B2_solution_rank')!=1:continue
        point=row.get('candidate_id')
        full=row.get('full_step',{})
        bracket=full.get('boundary_bracket')
        if (point in expected or not bracket or
            not full.get('limiting_couplings') or
            full.get('status')!='DIAGNOSTIC_BOUNDARY_REACHED_NOT_PHYSICAL_CUTOFF'):
            raise ValueError('C1 cohort rank1 boundary report incomplete')
        expected[point]=(
            float(bracket['estimated_boundary_GeV']),
            str(full['limiting_couplings'][0]['coupling']))
    if len(expected)!=30:
        raise ValueError('C1 cohort lacks exactly 30 baseline spectra')
    return expected

def load_cohort(b4_path,b2_path,limit):
    points=read_b1(b4_path)
    with Path(b4_path).open(newline='') as stream:
        rows=list(csv.DictReader(stream))
    raw={str(x['id']):x for x in rows}
    if len(raw)!=len(rows) or set(raw)!=set(points):
        raise ValueError('Duplicate/missing B4 IDs')
    for key,p in points.items():
        for i in range(1,6):
            item=f'lambda{i}'
            if item not in raw[key]:
                raise ValueError('Original B4 stored inverse quartic missing: '+item)
            p[item]=float(raw[key][item])
    sols=json.loads(Path(b2_path).read_text())
    if set(points)!=set(sols):
        raise ValueError('B2 solution IDs do not match B4 shortlist')
    if any(not isinstance(v,list) or not v for v in sols.values()):
        raise ValueError('Invalid B2 solution list')
    priority=lambda k:float(raw[k]['production_weighted_nonleptonic_cascade_upper_proxy'])
    selected=sorted(points,key=priority,reverse=True)[:limit]
    return points,sols,selected

def compare_flows(coarse,refined):
    if coarse['status']!=refined['status']:
        return False,'different_flow_outcomes',None
    if coarse['endpoint'] is not None and refined['endpoint'] is not None:
        relative=max(vector_distance(coarse['endpoint'],
                                     refined['endpoint']).values())
        return relative<2e-4,'end_scale',relative
    if coarse['boundary_bracket'] is not None and refined['boundary_bracket'] is not None:
        a=coarse['boundary_bracket']['estimated_boundary_GeV']
        b=refined['boundary_bracket']['estimated_boundary_GeV']
        rel=abs(a-b)/max(1.,a,b)
        ca=coarse['limiting_couplings'][0]['coupling']
        cb=refined['limiting_couplings'][0]['coupling']
        return rel<=.05 and ca==cb,'boundary_scale_and_driver',rel
    return False,'nonconvergent_or_unresolved',None

def widths_for_point(p,sol,neutrino_target):
    f=complex_matrix(sol['f'],'f')
    Y=complex_matrix(sol['Y'],'Y')
    # Tree/included-channel proxy, not the total physical BR.
    o=provisional_widths(p,f,Y,neutrino_target)
    return {
        'BR_H2_H1Z_LO_included_only':o['BR_H2_H1Z_included_general_Zee'],
        'BR_H1_tb_LO_included_only':o['BR_H1_tb_included_general_Zee'],
        'production_weighted_cascade_proxy_LO_included_only':
            o['production_weighted_partial_cascade_proxy'],
    }

def analyze_variant(mod,base,solution,variant,*,steps,upper,nu_target):
    name,max_lh,target_l1=variant
    out={
        'candidate_id':base['id'],'variant':name,
        'physical_Zee_allowed':'UNKNOWN',
        'reconstructed_tree_theory':'NOT_EVALUATED',
        'B2_neutrino_closure':'NOT_EVALUATED',
        'flavor_HiggsTools_global_vacuum_thresholds':'NOT_EVALUATED',
        'one_loop_uv_heuristic_only':True,
        'status':'NOT_EVALUATED',
    }
    try:
        p=varied_point(base,max_lh,target_l1)
        scalar,pre=scalar_lagrangian(p)
    except (ValueError,ArithmeticError,KeyError) as exc:
        out.update(status='TREE_SCALAR_REJECTED',
                   reason=str(exc))
        return out
    out.update({
        'reconstructed_tree_theory':'BFB_SUFFICIENT_AND_UNITARITY_PASS',
        'mH1_GeV':p['mH1'],'mH2_GeV':p['mH2'],
        'm12sq_GeV2':p['m12sq'],
        'lambda1_matching':float(scalar['l1']),
        'lambda_h_matching':float(scalar['lh']),
        'lambda3_matching':float(scalar['l3']),
        'lambda4_matching':float(scalar['l4']),
        'lambda5_matching':float(scalar['l5']),
        'quartic_max_at_matching':max(float(abs(scalar[k])) for k in QUARTIC_KEYS),
        'scalar_muZee_GeV':float(scalar['muZee']),
        'partial_widths':None,
    })
    if target_l1 is not None:
        if abs(float(scalar['l1'])-target_l1)>1e-8:
            raise ValueError('Tree scalar inversion did not reach lambda1 target')
    state,preflight=build_model_state(p,solution)
    out['B2_neutrino_closure']=preflight['neutrino_matrix_closure_eV']
    try:
        out['partial_widths']=widths_for_point(p,solution,nu_target)
    except (ValueError,ArithmeticError,KeyError) as exc:
        out['partial_widths_error']=repr(exc)
        # Do NOT equate missing included widths with physical exclusion.
    mu0=float(p['mH2'])
    coarse=run_flow(mod,state,mu0=mu0,mu1=upper,steps=steps)
    refined=run_flow(mod,state,mu0=mu0,mu1=upper,steps=2*steps)
    stable,kind,delta=compare_flows(coarse,refined)
    lead=coarse['limiting_couplings'][0]
    bracket=coarse['boundary_bracket']
    out.update({
        'status':('UV_DIAGNOSTIC_SOLVER_STABLE_NOT_ALLOWED' if stable
                  else 'INCONCLUSIVE_SOLVER_NOT_ALLOWED'),
        'flow_status':coarse['status'],
        'RGE_stepdoubling_compatible':stable,
        'RGE_stepdoubling_metric':kind,
        'RGE_stepdoubling_difference':delta,
        'estimated_4pi_crossing_GeV':(
            bracket['estimated_boundary_GeV'] if bracket else None),
        'boundary_bracket_relative_width':(
            bracket['relative_bracket_width'] if bracket else None),
        'first_limiting_coupling':lead['coupling'],
        'first_limiting_sector':lead['sector'],
        'first_limiting_ratio':lead['ratio'],
        'reached_10TeV_heuristic':bool(
            stable and coarse['endpoint'] is not None and
            refined['endpoint'] is not None),
        'max_abs_quartic_at_final_record':max(
            row['max_abs_scalar_quartic'] for row in coarse['history']
        ) if coarse['history'] else None,
        'generated_lambda6_final_record':(
            coarse['history'][-1]['lambda6_abs'] if coarse['history'] else None),
        'generated_lambda7_final_record':(
            coarse['history'][-1]['lambda7_abs'] if coarse['history'] else None),
    })
    return out

def validate_baseline(row,reference):
    if row['variant']!='baseline':
        raise ValueError('Reference must apply only to original spectrum')
    if not row['RGE_stepdoubling_compatible']:
        raise ValueError('Baseline RGE numerical control failed')
    expected_mu,expected_driver=reference
    found_mu=row['estimated_4pi_crossing_GeV']
    found_driver=row['first_limiting_coupling']
    if (found_mu is None or
        abs(found_mu-expected_mu)/expected_mu>3e-4
        or found_driver!=expected_driver):
        raise ValueError(
            f'Original C1 90-solution baseline does not reproduce: '
            f'got {(found_mu,found_driver)} expected {reference}')

def summarize(rows):
    points=collections.defaultdict(list)
    for row in rows:
        points[row['candidate_id']].append(row)
    variants=[v[0] for v in VARIANTS]
    result={}
    for label in variants:
        subset=[x for x in rows if x['variant']==label]
        passed=[x for x in subset if x.get('reached_10TeV_heuristic')]
        valid=[x for x in subset if x['status']=='UV_DIAGNOSTIC_SOLVER_STABLE_NOT_ALLOWED']
        result[label]={
            'total_pairs':len(subset),
            'tree_accepted':sum(x['reconstructed_tree_theory']==
                                'BFB_SUFFICIENT_AND_UNITARITY_PASS' for x in subset),
            'numerically_stable_flow':len(valid),
            'reached_10TeV_heuristic':len(passed),
            'boundary_median_GeV':statistics.median(
                [x['estimated_4pi_crossing_GeV'] for x in valid
                 if x['estimated_4pi_crossing_GeV'] is not None])
                 if any(x['estimated_4pi_crossing_GeV'] is not None for x in valid)
                 else None,
            'limiting_coupling_counts':dict(collections.Counter(
                x['first_limiting_coupling'] for x in valid)),
        }
    baseline={k:next(z for z in lst if z['variant']=='baseline')
              for k,lst in points.items()}
    rescued={
        k:[row['variant'] for row in rr
           if row['variant']!='baseline' and row.get('reached_10TeV_heuristic')]
        for k,rr in points.items()
    }
    return {
        'variant_summary':result,
        'original_spectra':len(points),
        'original_baseline_trigger_counts':dict(collections.Counter(
            r['first_limiting_coupling'] for r in baseline.values())),
        'number_original_spectra_with_at_least_one_uv_heuristic_rescue':
            sum(bool(v) for v in rescued.values()),
        'per_spectrum_rescuing_variants':rescued,
        'selected_cascade_biased_input_not_Zee_prior':True,
        '10TeV_diagnostic_survival_not_global_Zee_allowed':True,
        'full_LFV_not_evaluated':True,
        'running_BFB_unitarity_not_evaluated':True,
        'quark_CKM_and_matching_not_validated':True,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--b4-csv',type=Path,required=True)
    ap.add_argument('--b2-json',type=Path,required=True)
    ap.add_argument('--generator-output',type=Path,required=True)
    ap.add_argument('--q4v13-report',type=Path,required=True)
    ap.add_argument('--c1-cohort-summary',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--max-spectra',type=int,default=30)
    ap.add_argument('--steps',type=int,default=24)
    ap.add_argument('--upper-GeV',type=float,default=10000.)
    opts=ap.parse_args()
    if not(1<=opts.max_spectra<=30 and 8<=opts.steps<=120 and
           opts.steps%4==0 and 1000<opts.upper_GeV<=1e6):
        ap.error('Invalid experiment settings')
    if opts.output_dir.exists() and any(opts.output_dir.iterdir()):
        ap.error('Refuse nonempty output directory')
    opts.output_dir.mkdir(parents=True,exist_ok=True)
    report={
        'status':STATUS,
        'physically_allowed':None,'modern_two_state_B_to_XsGamma':'NOT_EVALUATED',
        'full_Zee_LFV':'NOT_EVALUATED',
        'HiggsTools':'NOT_EVALUATED','global_vacuum':'NOT_EVALUATED',
        'running_complex_BFB_and_unitarity':'NOT_EVALUATED',
        'CKM_quark_matching':'NOT_EVALUATED','UV_thresholds':'NOT_EVALUATED',
    }
    try:
        src=find_rges(opts.generator_output)
        report['RGE_validation']=verify_rge_validation(opts.q4v13_report,src)
        ref=read_cohort_reference(
            opts.c1_cohort_summary,opts.b4_csv,opts.b2_json,src)
        points,sols,names=load_cohort(
            opts.b4_csv,opts.b2_json,opts.max_spectra)
        report['provenance']={name:digest(p) for name,p in (
            ('B4',opts.b4_csv),('B2',opts.b2_json),
            ('C1_cohort',opts.c1_cohort_summary),('RGE_source',src))}
        module=load_generated(src)
        target,_=target_neutrino_matrix()
        rows=[]
        for index,ident in enumerate(names):
            base=points[ident]
            solution=sols[ident][0]
            if str(solution.get('candidate_id'))!=ident:
                raise ValueError('B2 solution identity mismatch')
            for variant in VARIANTS:
                rec=analyze_variant(
                    module,base,solution,variant,
                    steps=opts.steps,upper=opts.upper_GeV,nu_target=target)
                if variant[0]=='baseline':
                    validate_baseline(rec,ref[ident])
                rows.append(rec)
                print('C2_PAIRED_UV',
                      f'{index+1}/{len(names)}',
                      ident,variant[0],
                      'tree',rec['reconstructed_tree_theory'],
                      'status',rec['status'],
                      'limiter',rec.get('first_limiting_coupling','NA'),
                      'boundary_GeV',rec.get('estimated_4pi_crossing_GeV'),
                      'reaches_10TeV',rec.get('reached_10TeV_heuristic',False),
                      flush=True)
        report['cohort']=summarize(rows)
        report['tested_interventions']=len(rows)
        report['rows']=rows
        report['status']=STATUS
        flat=[]
        for x in rows:
            y={k:v for k,v in x.items() if k not in ('partial_widths',)}
            wd=x.get('partial_widths') or {}
            y.update(wd)
            flat.append(y)
        columns=list(dict.fromkeys(k for row in flat for k in row))
        dest=opts.output_dir/'paired_uv_rescue_diagnostics_NOT_ALLOWED.csv'
        with dest.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=columns)
            writer.writeheader();writer.writerows(flat)
        report['output_csv']=str(dest)
        print('C2_PAIRED_INTERVENTIONS',len(rows))
        print('C2_VARIANT_COUNTS',json.dumps(report['cohort']['variant_summary']))
        print('C2_SPECTRA_WITH_HEURISTIC_10TEV_RESCUE',
              report['cohort'][
                  'number_original_spectra_with_at_least_one_uv_heuristic_rescue'])
        print('C2_FULL_PHYSICAL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as exc:
        report.update(status='GATE_C2_FAILED_CLOSED_NOT_ALLOWED',
                      error=repr(exc),traceback=traceback.format_exc())
        print('C2_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        output=opts.output_dir/'summary.json'
        output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('C2_SUMMARY',output,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
