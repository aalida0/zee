#!/usr/bin/env python3
"""Gate D1: joined 30-spectrum x 10-neutrino-family flavor amplitude inventory.

This is ONE sizeable PHYSICS-oriented 300-Yukawa-solution analysis,
not a string of beta-function tests or a physically allowed scan.

Select the 30 C2 scalar spectra and all 10 saved B2 neutrino-closed
complex (f,Y) solutions for EACH spectrum. Recheck neutrino closure.
Join:
 - EXACT B2 coherent scalar ONE-LOOP l_i -> l_j photon amplitudes;
 - fermion-PHOTON top, bottom, tau Barr--Zee subset coherently combined
   with one-loop amplitudes, for mu->e gamma, tau->e gamma, tau->mu gamma;
 - general Zee tree-only neutral mu->3e, tau->3e, tau->3mu,
   tau->mu ee, tau->e mumu;
 - charged-singlet f-only leptonic universality shifts;
 - complete 2026 scalar C2/C3/C4/C5 provenance: flags for each
   of the two same-spectrum paired scalar-potential interventions.

Spectrum preservation in C2 means Higgs masses, alpha, beta and charged
mixing gamma are the SAME for both scalar-potential interventions, so
the currently implemented LFV subsets are identical between variants.
Do NOT double count identical flavor configurations as 600 independent
points. C5 only assessed the rank-1 f,Y case but the scalar tree vacuum
depends on neither f nor Y at this order; tags are valid for all ranks,
subject to RG/backreaction of Yukawas across the full running range
remaining UNTESTED for ranks 2--10.

Flavor observable "over limit" ratios for incomplete amplitudes
are DIAGNOSTICS, NOT EXCLUSIONS or verified passes: the full
electroweak/Barr--Zee, Z-penguin, W, charged-scalar, box and conversion
effects are absent and can interfere. In particular do not use a
one-loop-only > limit as a robust experimental exclusion without bounding
missing interference. The saved B2 solutions were pre-ranked using
PARTIAL LFV; hence the 300-case distribution is SELECTION BIASED.

This gate produces a clear physics priority: for each scalar spectrum,
which existing neutrino family has the smallest jointly evaluated
but INCOMPLETE LFV amplitude-subset diagnostics, and whether additional
LFV components could plausibly be important. It does NOT certify any
flavor fit, complete physical viable points, EFT threshold, meson FCNC,
modern matched b->s gamma, global vacuum, HiggsTools, or PMNS likelihood.
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
from gateB3_general_zee_charged_lepton_widths import (
    complex_matrix,ensure_neutrino_closure,read_b1
)
from gateA1b_hierarchical_no_seed import target_neutrino_matrix
from gateA1c_charged_singlet_lfv import CHANNELS
from zee_lfv_backend import evaluate_candidate as partial_three_lepton
from zee_barr_zee_fermion_dipoles import compute as partial_barr_zee
from zee_gateC1_joined_uv_pilot import digest,build_model_state
from zee_gateC2_paired_uv_rescue import (
    VARIANTS,varied_point
)
from zee_gateC3_running_complex_bfb import TARGET_VARIANTS
from zee_gateC5_charge_breaking_vacuum_search import c4_provenance

STATUS='GATE_D1_300_JOINT_ZEE_NEUTRINO_LFV_PARTIAL_DIAGNOSTIC_NOT_ALLOWED'
MAX_RELATIVE_ONELOOP_RECHECK=2e-8

def verify_c5(path,b4,b2,c2,c3,c4):
    v=json.loads(Path(path).read_text())
    checksum=v.get('inputs_sha256',{})
    expected={
        'B4':b4,'B2':b2,'C2':c2,'C3':c3,'C4':c4
    }
    if (v.get('status') !=
          'GATE_C5_NUMERICAL_FULL_ZEE_CHARGE_BREAKING_VACUUM_NOT_ALLOWED'
        or v.get('tested')!=60 or len(v.get('rows',[]))!=60
        or any(checksum.get(k)!=digest(p) for k,p in expected.items())):
        raise ValueError('C5 completed report/source hash or 60-case inventory mismatch')
    mapped={}
    for case in v['rows']:
        key=(case['candidate_id'],case['variant'])
        if key in mapped:
            raise ValueError('Duplicate C5 candidate/variant')
        mapped[key]=case
    if len(mapped)!=60:
        raise ValueError('Incomplete unique C5 model cases')
    return mapped

def classify_theory_cases(candidate,c4,c5):
    case_map={}
    for name in TARGET_VARIANTS:
        a=c4[(candidate,name)]
        b=c5[(candidate,name)]
        if bool(b['C4_running_theory_pass'])!=bool(a['both_running_theory_screens_pass']):
            raise ValueError('C4/C5 theory screen classification mismatch '+candidate+'/'+name)
        if (bool(b['C5_deeper_witness']) and
            b['C5_search_status']!='EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS'):
            raise ValueError('C5 witness provenance mismatch')
        case_map[name]={
            'running_perturbativity_BFB_and_55channel_unitarity_10TeV':
                bool(a['both_running_theory_screens_pass']),
            'explicit_deeper_charge_breaking_witness':
                bool(b['C5_deeper_witness']),
            'no_deeper_witness_found_NOT_global_proof':
                not bool(b['C5_deeper_witness']),
            'scalar_only_candidate_for_further_flavor_work':
                bool(a['both_running_theory_screens_pass']) and
                not bool(b['C5_deeper_witness']),
            'vacuum_status':b['C5_search_status']
        }
    return case_map

def load_cohort(b4_path,b2_path):
    points=read_b1(b4_path)
    with Path(b2_path).open() as stream:
        sols=json.load(stream)
    if set(points)!=set(sols) or len(points)!=30:
        raise ValueError('Expected exact B4/B2 thirty-spectrum provenance')
    for name,entries in sols.items():
        if not isinstance(entries,list) or len(entries)!=10:
            raise ValueError('Require all TEN saved B2 neutrino solutions for '+name)
        if any(str(z.get('candidate_id'))!=name for z in entries):
            raise ValueError('B2 candidate identity mismatch '+name)
    return points,sols

def matrix_max(m):
    return float(np.max(abs(np.asarray(m,complex))))

def candidate_flavor(point,solution,rank):
    if str(solution.get('status'))!='NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED':
        raise ValueError('Unexpected B2 status or unsafe accepted label')
    for k in ('mH1','mH2','gamma'):
        if not math.isclose(float(solution[k]),float(point[k]),
                            rel_tol=1e-11,abs_tol=1e-9):
            raise ValueError('B2 scalar mass/mixing identity mismatch '+k)
    f=complex_matrix(solution['f'],'f')
    Y=complex_matrix(solution['Y'],'Y')
    target,_=target_neutrino_matrix()
    closure=ensure_neutrino_closure(point,f,Y,target)
    if closure>=1e-9:
        raise ValueError('Neutrino mass matrix closure failed')
    three=partial_three_lepton(point,solution)
    dip=partial_barr_zee(point,f,Y,solution)
    if set(dip)!=set(CHANNELS):
        raise ValueError('Missing radiative LFV channel')
    if matrix_max(f)>=math.sqrt(4*math.pi) or matrix_max(Y)>=math.sqrt(4*math.pi):
        raise ValueError('LFV solution outside stored perturbativity boundary')
    detail={}
    ratios_one=[]
    ratios_combined=[]
    ratios_tree=[]
    max_bz_amplitude=0.
    for channel,info in CHANNELS.items():
        x=dip[channel]
        r=float(x['coherent_partial_over_limit_NOT_EXCLUSION'])
        r1=float(x['one_loop_only_BR'])/float(info['limit'])
        t=(math.hypot(*x['barr_zee_CL'])**2+
           math.hypot(*x['barr_zee_CR'])**2)
        l=(math.hypot(*x['one_loop_CL'])**2+
           math.hypot(*x['one_loop_CR'])**2)
        amp_ratio=math.sqrt(t/l) if l>0 else None
        if amp_ratio is not None:
            max_bz_amplitude=max(max_bz_amplitude,amp_ratio)
        if not math.isclose(
            r, float(x['coherent_one_loop_plus_fermion_photon_BR_NOT_PHYSICAL'])/
                   float(info['limit']),
            rel_tol=MAX_RELATIVE_ONELOOP_RECHECK,abs_tol=1e-20):
            raise ValueError('Inconsistent saved Barr-Zee branch ratio')
        detail[channel]={
            'experimental_limit_reference_90CL':float(info['limit']),
            'one_loop_only_ratio_NOT_EXCLUSION':r1,
            'one_loop_plus_fermion_photon_BZ_subset_ratio_NOT_EXCLUSION':r,
            'one_loop_only_BR':float(x['one_loop_only_BR']),
            'one_loop_plus_fermion_photon_BR_NOT_PHYSICAL':
                float(x['coherent_one_loop_plus_fermion_photon_BR_NOT_PHYSICAL']),
            'BZ_to_one_loop_dipole_amplitude_norm_ratio':amp_ratio
        }
        ratios_one.append(r1);ratios_combined.append(r)
    for name,obj in three['tree_only_3lepton_ratios_NOT_EXCLUSION'].items():
        ratios_tree.append(float(obj['tree_only_over_limit_NOT_EXCLUSION']))
    if not(all(np.isfinite(r) and r>=0 for r in
               ratios_one+ratios_combined+ratios_tree)):
        raise ValueError('Invalid normalized LFV ratio')
    max_one=max(ratios_one)
    max_coherent=max(ratios_combined)
    max_tree=max(ratios_tree)
    score=max(max_coherent,max_tree)
    # Only ranks of INCOMPLETE amplitudes, NEVER exclusion decisions.
    return {
        'candidate_id':point['id'],
        'solution_rank_original_B2':int(rank),
        'neutrino_closure_eV':float(closure),
        'max_abs_f':matrix_max(f),
        'max_abs_Y':matrix_max(Y),
        'stored_B2_partial_LFV_score_NOT_EXCLUSION':
            float(solution['partial_LFV_score_NOT_EXCLUSION']),
        'max_1loop_radiative_over_limit_NOT_EXCLUSION':max_one,
        'max_coherent_1loop_plus_fermionBZ_over_limit_NOT_EXCLUSION':max_coherent,
        'max_tree_3lepton_over_limit_NOT_EXCLUSION':max_tree,
        'joint_incomplete_LFV_score_NOT_EXCLUSION':score,
        'largest_BZ_to_1loop_amplitude_norm_ratio':max_bz_amplitude,
        'photon_BZ_amplitudes_can_interfere_with_one_loop':True,
        'experimental_LFV_allowed_or_excluded':'UNKNOWN',
        'PMNS_likelihood':'NOT_EVALUATED_FIXED_CENTRAL_TARGET_ONLY',
        'full_Zee_lepton_number_and_universality':'PARTIAL_F_ONLY',
        'full_two_loop_LFV':'NOT_COMPUTED',
        'mu_e_conversion':'NOT_COMPUTED',
        'neutral_3body_dipole_penguin_box':'NOT_COMPUTED',
        'radiative_channels':detail,
        'neutral_3lepton_tree_only_rates':three['tree_only_3lepton_rates_NOT_PHYSICAL_TOTAL'],
        'f_only_universality_shifts':three['f_only_universality_NOT_FULL'],
    }

def summarize(rows,models):
    by_spectrum=collections.defaultdict(list)
    for x in rows:
        by_spectrum[x['candidate_id']].append(x)
    answer=[]
    for name,group in sorted(by_spectrum.items()):
        best=min(group,key=lambda z:z['joint_incomplete_LFV_score_NOT_EXCLUSION'])
        original=min(group,key=lambda z:z['solution_rank_original_B2'])
        cases=models[name]
        answer.append({
            'candidate_id':name,
            'saved_B2_solutions':len(group),
            'theory_screen_10TeV_and_no_C5_witness_any_variant':
                any(z['scalar_only_candidate_for_further_flavor_work']
                    for z in cases.values()),
            'theory_screen_10TeV_and_no_C5_witness_variant_count':
                sum(z['scalar_only_candidate_for_further_flavor_work']
                    for z in cases.values()),
            'original_B2_best_rank':original['solution_rank_original_B2'],
            'new_best_incomplete_LFV_rank':best['solution_rank_original_B2'],
            'original_B2_rank1_partial_score':
                original['stored_B2_partial_LFV_score_NOT_EXCLUSION'],
            'best_joint_incomplete_LFV_score_NOT_EXCLUSION':
                best['joint_incomplete_LFV_score_NOT_EXCLUSION'],
            'best_joint_incomplete_LFV_mu_to_e_gamma_BZ_plus_1loop_ratio':
                best['radiative_channels']['mu_to_e_gamma'][
                   'one_loop_plus_fermion_photon_BZ_subset_ratio_NOT_EXCLUSION'],
            'min_joint_partial_diagnostic_below_one_NOT_A_PASS':
                best['joint_incomplete_LFV_score_NOT_EXCLUSION']<1.,
            'full_Zee_flavor_status':'UNKNOWN'
        })
    vals=[r['best_joint_incomplete_LFV_score_NOT_EXCLUSION'] for r in answer]
    return answer,{
        'spectra':len(by_spectrum),'independent_complex_neutrino_solutions':len(rows),
        'unique_spectra_with_theory_screens_no_vacuum_witness':
            sum(x['theory_screen_10TeV_and_no_C5_witness_any_variant']
                for x in answer),
        'unique_spectra_without_any_screened_variant':sum(
            not x['theory_screen_10TeV_and_no_C5_witness_any_variant']
            for x in answer),
        'median_best_incomplete_score_NOT_A_FIT':statistics.median(vals),
        'min_best_incomplete_score_NOT_A_FIT':min(vals),
        'max_best_incomplete_score_NOT_A_FIT':max(vals),
        'best_score_below_one_is_NOT_a_physical_acceptance':True,
        'no_full_LFV_exclusion_or_validation':True,
        'B2_sample_partially_ranked_and_not_statistical_prior':True,
    }

def main():
    a=argparse.ArgumentParser(description=__doc__)
    for key in ('b4-csv','b2-json','c2-summary','c3-summary',
                'c4-summary','c5-summary'):
        a.add_argument('--'+key,type=Path,required=True)
    a.add_argument('--output-dir',type=Path,required=True)
    a.add_argument('--solution-limit',type=int,default=10)
    options=a.parse_args()
    if options.solution_limit!=10:
        a.error('D1 requires all 10 saved B2 Yukawa solutions per spectrum')
    if options.output_dir.exists() and any(options.output_dir.iterdir()):
        a.error('Refuse to overwrite existing report')
    options.output_dir.mkdir(parents=True,exist_ok=True)
    result={
        'status':STATUS,'physical_Zee_allowed_points':None,
        'complete_NLO_or_two_loop_LFV':'NOT_COMPUTED',
        'matched_BtoXsGamma':'NOT_COMPUTED',
        'HiggsTools':'NOT_COMPUTED',
        'mu_e_conversion':'NOT_COMPUTED',
        'CKM_mass_scheme_and_RG_thresholds':'NOT_COMPUTED',
        'charge_breaking_global_minimum_certified':False,
        'PMNS_oscillation_global_likelihood':'NOT_EVALUATED',
    }
    try:
        previous_c4,rge_sha=c4_provenance(
            options.c4_summary,options.b4_csv,options.b2_json,
            options.c2_summary,options.c3_summary)
        previous_c5=verify_c5(
            options.c5_summary,options.b4_csv,options.b2_json,
            options.c2_summary,options.c3_summary,options.c4_summary)
        points,sols=load_cohort(options.b4_csv,options.b2_json)
        models={}
        table=[]
        full=[]
        for i,(name,point) in enumerate(sorted(points.items()),1):
            # C2 changed scalar self-couplings and soft masses,
            # not the charged Higgs masses/charged mixing/neutrino operator.
            models[name]=classify_theory_cases(name,previous_c4,previous_c5)
            for label in TARGET_VARIANTS:
                vv=next(z for z in VARIANTS if z[0]==label)
                model=varied_point(point,vv[1],vv[2])
                # Validate the scalar mapping and rank1 closure; flavor
                # states for all 10 ranks are tested independently below.
                build_model_state(model,sols[name][0])
            for rank,sol in enumerate(sols[name],1):
                row=candidate_flavor(point,sol,rank)
                table.append({k:v for k,v in row.items() if k not in (
                    'radiative_channels','neutral_3lepton_tree_only_rates',
                    'f_only_universality_shifts')})
                full.append(row)
            print('D1_FLAVOR_FAMILY',f'{i}/30',name,
                  'solutions',len(sols[name]),
                  'theory_screened_variants',sum(
                      v['scalar_only_candidate_for_further_flavor_work']
                      for v in models[name].values()),
                  'best_joint_partial_diagnostic',min(
                      z['joint_incomplete_LFV_score_NOT_EXCLUSION']
                      for z in full[-10:]),flush=True)
        if len(full)!=300:
            raise ValueError('D1 expected 300 unique B2 flavor configurations')
        by_spectrum,cohort=summarize(full,models)
        result.update({
            'cohort':cohort,
            'model_variant_status':models,
            'per_spectrum':by_spectrum,
            'all_300_incomplete_LFV_details':full,
            'RGEs_SHA256_from_C4':rge_sha,
            'input_sha256':{
                k:digest(v) for k,v in (
                  ('B4',options.b4_csv),('B2',options.b2_json),
                  ('C2',options.c2_summary),('C3',options.c3_summary),
                  ('C4',options.c4_summary),('C5',options.c5_summary))}
        })
        file=options.output_dir/'incomplete_flavor_diagnostics_300_NOT_ALLOWED.csv'
        with file.open('w',newline='') as stream:
            fields=list(table[0])
            writer=csv.DictWriter(stream,fieldnames=fields)
            writer.writeheader();writer.writerows(table)
        second=options.output_dir/'spectrum_flavor_shortlist_NOT_ALLOWED.csv'
        with second.open('w',newline='') as stream:
            fields=list(by_spectrum[0])
            writer=csv.DictWriter(stream,fieldnames=fields)
            writer.writeheader();writer.writerows(by_spectrum)
        result['full_csv']=str(file)
        result['shortlist_csv']=str(second)
        print('D1_TOTAL_NEUTRINO_LFV_CONFIGURATIONS',len(full))
        print('D1_COHORT',json.dumps(cohort))
        print('D1_PHYSICAL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as exc:
        result.update(status='GATE_D1_FAIL_CLOSED_NOT_ALLOWED',
                      error=repr(exc),traceback=traceback.format_exc())
        print('D1_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        dest=options.output_dir/'summary.json'
        dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('D1_SUMMARY',dest,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
