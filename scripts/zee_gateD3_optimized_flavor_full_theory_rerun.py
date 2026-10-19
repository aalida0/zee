#!/usr/bin/env python3
"""Gate D3: FULL 26-RGE theory recheck of D2 neutrino-exact LFV-optimized f/Y.

D2 obtained partial-LFV-subset scores far below one for 27 scalar spectra,
but its optimized Yukawas are NOT those used in C1--C4. D3 rebuilds
each complete matched Zee model (two C2 potential interventions each)
with EXACT D2 f/Y, and reruns full complex RGE, sufficient quartic BFB
and 55-channel tree unitarity to 10 TeV on 24 and 48 logarithmic steps.

Also recompute optimized partial LFV score using existing D1 backend
and test local 1e-3 / 1e-2 relative null-Y and f-scale perturbations
without violating neutrino matrix closure.

A robust numerical *THEORY SCREEN* pass here is NOT "physically allowed":
- quark Yukawas are illustrative diagonal CKM=I, not MSbar matching;
- no field thresholds, full PMNS likelihood, complete Barr-Zee LFV,
  3-body penguins/boxes or mu-e conversion;
- no modern two-charged b->s gamma, meson FCNC or HiggsTools;
- C5 absent deeper witness is NOT a proof of global minimum;
- tree unitarity and sufficient BFB checked at finite RG sample scales.
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

from gateA1b_hierarchical_no_seed import target_neutrino_matrix,scalar_kappa,reconstruct_neutrino
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_section8_Q4_generated_source_limit_probe import find_rges,load_generated
from zee_gateC1_joined_uv_pilot import build_model_state,digest,verify_rge_validation
from zee_gateC2_paired_uv_rescue import VARIANTS,varied_point
from zee_gateC3_running_complex_bfb import TARGET_VARIANTS,orbit_design
from zee_gateC4_running_55channel_unitarity import full_trajectory,verify_c3
from zee_gateC5_charge_breaking_vacuum_search import c4_provenance
from zee_gateD1_joint_300_neutrino_lfv_inventory import (
    load_cohort,verify_c5,candidate_flavor,classify_theory_cases
)
from zee_gateD2_neutrino_exact_partial_LFV_optimization import (
    STATUS as D2_STATUS,neutrino_family,make_yukawas,amplitude_subset,
    optimize_kernels_cache
)

STATUS="GATE_D3_OPTIMIZED_YUKAWA_FULL_ZEE_RUNNING_THEORY_RECHECK_NOT_ALLOWED"
MAX_MATCHING_RELATIVE_SCORE_ERROR=5e-8

def verify_d2(path,b4,b2,c2,c3,c4,c5,d1):
    report=json.loads(Path(path).read_text())
    required=dict(B4=b4,B2=b2,C2=c2,C3=c3,C4=c4,C5=c5,D1=d1)
    if (report.get('status')!=D2_STATUS
        or any(report.get('inputs_SHA256',{}).get(k)!=digest(v)
               for k,v in required.items())
        or report.get('tested_spectra')!=27
        or report.get('optimization_runs')!=54):
        raise ValueError('D2 27-spectrum/54-run source-provenance mismatch')
    rows=report.get('rows',[])
    details=report.get('optimized_full_f_Y_and_partial_flavor_provenance',{})
    if len(rows)!=27 or len(details)!=27:
        raise ValueError('D2 missing optimized spectrum inventory')
    mapping={}
    for row in rows:
        name=row.get('candidate_id')
        if not isinstance(name,str) or name in mapping or name not in details:
            raise ValueError('D2 duplicate or incorrect candidate identity')
        item=details[name]
        if item.get('chosen',{}).get('solution',{}).get('candidate_id')!=name:
            raise ValueError('D2 optimized f/Y identity mismatch')
        if item.get('parent_rank')!=row.get('best_optimized_from_rank'):
            raise ValueError('D2 root rank mismatched final objective')
        if not math.isclose(
            float(item['chosen']['best_score']),
            float(row['new_best_partial_score_NOT_EXCLUSION']),
            rel_tol=1e-10,abs_tol=1e-14):
            raise ValueError('D2 reported best score inconsistently')
        mapping[name]=(row,item)
    return mapping

def check_flavor_input(point,d2row,chosen):
    sol=chosen['solution']
    flavor=candidate_flavor(point,sol,0)
    original=float(d2row['new_best_partial_score_NOT_EXCLUSION'])
    measured=float(flavor['joint_incomplete_LFV_score_NOT_EXCLUSION'])
    if not math.isclose(original,measured,
                         rel_tol=MAX_MATCHING_RELATIVE_SCORE_ERROR,abs_tol=1e-14):
        raise ValueError('Recomputed D2/D1 amplitude diagnostic mismatch')
    if (measured>=1 or flavor['neutrino_closure_eV']>=1e-9):
        raise ValueError('D2 optimized f/Y does not meet intended partial-LFV diagnostic/closure')
    return flavor

def local_lfv_robustness(point,sol,*,seed,trials=12):
    """Probe near-optimum incomplete LFV scores, preserving neutrino algebra."""
    family=neutrino_family(point,sol)
    baseline=amplitude_subset(point,*make_yukawas(family,family['starting_coords']))
    reference=max(baseline.values())
    rng=np.random.default_rng(seed)
    samples=[]
    for radius in (1e-3,1e-2):
        scores=[]
        perturbative=True
        for _ in range(trials):
            shift=rng.normal(size=9)
            shift/=np.linalg.norm(shift)
            x=family['starting_coords']+radius*shift
            f,Y=make_yukawas(family,x)
            err=np.max(abs(reconstruct_neutrino(
                f,Y,kappa=family['kappa'])-family['target']))
            if not np.isfinite(err) or err>=1e-9:
                raise ValueError('Local nullspace perturbation broke neutrino closure')
            max_coupling=max(np.max(abs(f)),np.max(abs(Y)))
            if max_coupling>=math.sqrt(4*math.pi):
                perturbative=False
                continue
            score=max(amplitude_subset(point,f,Y).values())
            if not math.isfinite(score):
                raise ValueError('Nonfinite local LFV score')
            scores.append(float(score))
        samples.append({
            'relative_null_coordinate_perturbation':radius,
            'trials_attempted':trials,
            'perturbative_trials':len(scores),
            'all_trials_perturbative':perturbative,
            'max_score':max(scores) if scores else None,
            'median_score':statistics.median(scores) if scores else None,
            'maximum_relative_score_vs_central':max(scores)/reference if scores else None,
            'partial_scores_below_one':sum(s<1 for s in scores),
            'not_a_physical_uncertainty_or_fine_tuning_measure':True,
        })
    return samples

def classify_flow(coarse,refined):
    if coarse['reached_end_scale']!=refined['reached_end_scale']:
        raise ValueError('D3 RGE coarse/refined 10 TeV reach disagreement')
    if coarse['BFB_negative_witness']!=refined['BFB_negative_witness']:
        raise ValueError('D3 RGE coarse/refined negative BFB witness disagreement')
    c0=coarse['first_tree_unitarity_crossing']
    c1=refined['first_tree_unitarity_crossing']
    if (c0 is None)!=(c1 is None):
        raise ValueError('D3 unitarity crossing differs between step sizes')
    relative=None
    if c0 is not None:
        a,b=c0['first_failure_GeV'],c1['first_failure_GeV']
        relative=abs(a-b)/max(1.,a,b)
        if relative>.05:
            raise ValueError('D3 tree-unitarity crossing mismatch >5%')
    if coarse['reached_end_scale'] and (
        coarse['BFB_sufficient_at_all_sampled_steps'] !=
        refined['BFB_sufficient_at_all_sampled_steps']):
        raise ValueError('D3 sufficient BFB classification changed with grid')
    both=(coarse['reached_end_scale'] and refined['reached_end_scale']
          and coarse['BFB_sufficient_at_all_sampled_steps']
          and refined['BFB_sufficient_at_all_sampled_steps']
          and coarse['tree_unitarity_8pi_at_all_sampled_steps']
          and refined['tree_unitarity_8pi_at_all_sampled_steps'])
    return bool(both),relative

def summarize(rows):
    result={}
    for label in TARGET_VARIANTS:
        selected=[r for r in rows if r['variant']==label]
        result[label]={
            'tested':len(selected),
            'optimized_full_26RGE_reaches_10TeV':sum(
                r['optimized_RGE_reaches_10TeV'] for r in selected),
            'optimized_all_sampled_BFB_sufficient':sum(
                r['optimized_BFB_sufficient_to_10TeV'] for r in selected),
            'optimized_all_sampled_55channel_unitarity':sum(
                r['optimized_55channel_unitarity_to_10TeV'] for r in selected),
            'all_three_running_theory_screens_after_fY_optimization':sum(
                r['D3_joint_running_theory_screen_pass'] for r in selected),
            'no_C5_deeper_tree_vacuum_witness':sum(
                r['C5_no_deeper_witness_NOT_global_certification'] for r in selected),
            'prior_C4_rank1_family_joint_running_pass':sum(
                r['old_C4_rank1_family_running_screen_pass'] for r in selected),
        }
    candidates=collections.defaultdict(list)
    for r in rows:
        candidates[r['candidate_id']].append(r)
    return {
        'variant_breakdown':result,
        'unique_spectra_with_at_least_one_revalidated_theory_variant':sum(
            any(c['D3_joint_running_theory_screen_pass']
                and c['C5_no_deeper_witness_NOT_global_certification'] for c in pairs)
            for pairs in candidates.values()),
        'neutrino_optimized_theory_spectra_tested':len(candidates),
        'full_LFV_and_other_experimental_constraints_unknown':True,
        'sampled_scale_criteria_not_continuous_proof':True,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('b4-csv','b2-json','c2-summary','c3-summary',
                 'c4-summary','c5-summary','d1-summary','d2-summary',
                 'generator-output','q4v13-report'):
        ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--steps',type=int,default=24)
    ap.add_argument('--orbit-samples',type=int,default=2048)
    ap.add_argument('--upper-GeV',type=float,default=10000.)
    ap.add_argument('--local-trials',type=int,default=12)
    args=ap.parse_args()
    if (not (8<=args.steps<=120 and args.steps%4==0
             and 256<=args.orbit_samples<=32768
             and 10000<=args.upper_GeV<=1e6
             and 4<=args.local_trials<=128)):
        ap.error('Invalid D3 run configuration')
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        ap.error('Refuse overwrite of previous report')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    report={
        'status':STATUS,
        'physical_Zee_allowed':None,
        'complete_LFV_W_and_charged_scalar_Barr_Zee':'NOT_COMPUTED',
        'mu_to_e_conversion':'NOT_COMPUTED',
        'three_lepton_loop_penguin_box':'NOT_COMPUTED',
        'full_PMNS_likelihood':'NOT_COMPUTED',
        'two_charged_b_to_s_gamma_matched':'NOT_COMPUTED',
        'CKM_quark_running_scheme':'NOT_COMPUTED',
        'HiggsTools':'NOT_COMPUTED',
        'EW_vacuum_global_minimum_proof':False,
        'RG_threshold_matching':'NOT_COMPUTED',
        'theory_certificates_only_at_sampled_scales':True,
    }
    try:
        rges=find_rges(args.generator_output)
        report['Q4_validation']=verify_rge_validation(args.q4v13_report,rges)
        models=verify_d2(
            args.d2_summary,args.b4_csv,args.b2_json,args.c2_summary,
            args.c3_summary,args.c4_summary,args.c5_summary,args.d1_summary)
        prior_c4,sha=c4_provenance(
            args.c4_summary,args.b4_csv,args.b2_json,
            args.c2_summary,args.c3_summary)
        if sha!=digest(rges):
            raise ValueError('Q4v13 and C4 RGE source checksum discrepancy')
        prior_c5=verify_c5(
            args.c5_summary,args.b4_csv,args.b2_json,args.c2_summary,
            args.c3_summary,args.c4_summary)
        points,_=load_cohort(args.b4_csv,args.b2_json)
        module=load_generated(rges)
        orbits=orbit_design(args.orbit_samples)
        optimize_kernels_cache()
        rows=[];local_diagnostics={}
        for index,(name,(row,item)) in enumerate(models.items(),1):
            if name not in points:
                raise ValueError('D2 optimized candidate not in B4 scalar set')
            point=points[name]
            sol=item['chosen']['solution']
            flavor=check_flavor_input(point,row,item['chosen'])
            local=local_lfv_robustness(
                point,sol,seed=20261019+index*137,trials=args.local_trials)
            local_diagnostics[name]=local
            for label in TARGET_VARIANTS:
                v=next(x for x in VARIANTS if x[0]==label)
                pot=varied_point(point,v[1],v[2])
                initial,validation=build_model_state(pot,sol)
                old=prior_c4[(name,label)]
                vacuum=prior_c5[(name,label)]
                if bool(vacuum['C4_running_theory_pass'])!=bool(
                    old['both_running_theory_screens_pass']):
                    raise ValueError('D3 earlier C4/C5 inconsistent')
                coarse=full_trajectory(module,initial,mu0=pot['mH2'],
                                       upper=args.upper_GeV,steps=args.steps,
                                       orbits=orbits)
                refined=full_trajectory(module,initial,mu0=pot['mH2'],
                                        upper=args.upper_GeV,steps=2*args.steps,
                                        orbits=orbits)
                good,relative=classify_flow(coarse,refined)
                entry={
                    'candidate_id':name,'variant':label,
                    'fY_source':'D2_OPTIMIZED_NOT_B2_RANK1',
                    'D2_optimized_partial_LFV_score_NOT_EXCLUSION':
                        float(row['new_best_partial_score_NOT_EXCLUSION']),
                    'D2_partial_diagnostic_below_one_NOT_A_PASS':bool(
                        row['partial_score_below_one_NOT_A_PASS']),
                    'neutrino_closure_eV_with_optimized_fY':
                        float(validation['neutrino_matrix_closure_eV']),
                    'original_B2_rank1_neutrino_not_reused':True,
                    'max_f_entry':float(flavor['max_abs_f']),
                    'max_Higgs_basis_Y_entry':float(flavor['max_abs_Y']),
                    'old_C4_rank1_family_running_screen_pass':bool(
                        old['both_running_theory_screens_pass']),
                    'C5_no_deeper_witness_NOT_global_certification':
                        not bool(vacuum['C5_deeper_witness']),
                    'optimized_RGE_reaches_10TeV':bool(
                        coarse['reached_end_scale'] and refined['reached_end_scale']),
                    'optimized_BFB_sufficient_to_10TeV':bool(
                        coarse['BFB_sufficient_at_all_sampled_steps'] and
                        refined['BFB_sufficient_at_all_sampled_steps']),
                    'optimized_55channel_unitarity_to_10TeV':bool(
                        coarse['tree_unitarity_8pi_at_all_sampled_steps'] and
                        refined['tree_unitarity_8pi_at_all_sampled_steps']),
                    'D3_joint_running_theory_screen_pass':good,
                    'coarse_flow_status':coarse['status'],
                    'refined_flow_status':refined['status'],
                    'first_tree_unitarity_boundary_GeV':(
                        coarse['first_tree_unitarity_crossing']['first_failure_GeV']
                        if coarse['first_tree_unitarity_crossing'] else None),
                    'unitarity_coarse_refined_relative_boundary_delta':relative,
                    'max_scattering_eigenvalue_seen':max(
                        coarse['maximum_scattering_eigenvalue_encountered'],
                        refined['maximum_scattering_eigenvalue_encountered']),
                    'first_BFB_uncertified_scale_GeV':
                        coarse['first_BFB_uncertified_scale_GeV'],
                    'first_unitarity_uncertified_scale_GeV':
                        coarse['first_tree_unitarity_uncertified_scale_GeV'],
                    'max_local_1percent_flavor_subset_score':
                        local[1]['max_score'],
                    'local_1percent_perturbative_count':
                        local[1]['perturbative_trials'],
                    'local_1percent_partial_below_one_count':
                        local[1]['partial_scores_below_one'],
                    'global_vacuum_allowed':'UNKNOWN',
                    'full_flavor_experimental_allowed':'UNKNOWN',
                }
                rows.append(entry)
                print('D3_OPTIMIZED_FY_FULL_RGE',f'{index}/{len(models)}',
                    name,label,'old_C4',entry['old_C4_rank1_family_running_screen_pass'],
                    'new_reached_10TeV',entry['optimized_RGE_reaches_10TeV'],
                    'new_BFB',entry['optimized_BFB_sufficient_to_10TeV'],
                    'new_55chan',entry['optimized_55channel_unitarity_to_10TeV'],
                    'joint_screen',good,
                    'partial_score',entry['D2_optimized_partial_LFV_score_NOT_EXCLUSION'],
                    flush=True)
        if len(rows)!=54:
            raise ValueError('D3 optimized fY cohort must have exactly 54 model configurations')
        report.update({
            'row_count':len(rows),'rows':rows,'local_amplitude_perturbations':local_diagnostics,
            'cohort':summarize(rows),
            'source_SHA256':{
                k:digest(path) for k,path in (
                  ('B4',args.b4_csv),('B2',args.b2_json),
                  ('C2',args.c2_summary),('C3',args.c3_summary),
                  ('C4',args.c4_summary),('C5',args.c5_summary),
                  ('D1',args.d1_summary),('D2',args.d2_summary),
                  ('RGEs',rges))},
            'constraints_not_validated_for_physical_exclusions':True,
        })
        filename=args.output_dir/'revalidated_optimized_fY_theory_NOT_ALLOWED.csv'
        with filename.open('w',newline='') as h:
            writer=csv.DictWriter(h,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
        report['csv']=str(filename)
        print('D3_FULL_THEORY_COHORT',json.dumps(report['cohort']))
        print('D3_FULL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as exc:
        report.update(status='GATE_D3_FAIL_CLOSED_NOT_ALLOWED',
                      error=repr(exc),traceback=traceback.format_exc())
        print('D3_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        dest=args.output_dir/'summary.json'
        dest.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('D3_SUMMARY',dest,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
