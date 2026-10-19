#!/usr/bin/env python3
"""Gate D2: paired, neutrino-exact, continuously optimized partial Zee LFV.

D1 evaluated all 150 available B2 textures (five per each of 30
spectra) and found no incomplete-amplitude score <1 (lowest ~1.167).
This is not evidence of full-model exclusion: B2 saved only five
pre-ranked textures/spectrum and D1 did not optimize free Yukawas.

Gate D2 optimizes the FOUR COMPLEX neutrino-Yukawa homogeneous
directions plus ONE REAL f-normalization degree of freedom:
  Mnu = kappa * (f Ml Y + transpose) * 1e9 eV
  f(r)=r f0,
  Y(r,z)=Yparticular(f0)/r + reshape(N(f0) z), N†N=I, A(f0)N=0.
Every trial (including optimizer exploration) has the SAME EXACT
fixed central-NO neutrino matrix before numerical roundoff.
This parametrization DOES NOT cover varying null-vector orientation
of f; multiple original saved B2 f orientations seed the search.

Objective: min of the maximum implemented partial rate/reference bound:
  coherent scalar one-loop + top/bottom/tau fermion-photon BZ for
  mu->e gamma, tau->mu gamma and tau->e gamma;
  tree-only neutral h/H/A for five three-charged-lepton modes.
Use Powell bounded minimization from the TWO best B2/D1 roots for
each of the 27 scalar-spectra with at least one C4 running-theory
pass and no C5 deeper-vacuum witness. Full mathematical global
optimization is NOT claimed. Every final score is recomputed through
the original B2 + D1 backends (no new normalizations), with a hard
numerical closure and perturbativity check.

A small *in-process* memoization of the fixed scalar f(z),g(z) BZ
loop functions is used to avoid expensive identical quadratures.
The BZ functions' arguments are fixed by each scalar spectrum,
not by the optimized Yukawas, so this is exactly value preserving.
Do NOT change the underlying BZ formulas.

This is an LFV SUBSET optimization: W, charged-scalar, Z and other
two-loop diagrams, 3-body loop/penguin/boxes, mu-e conversion, PMNS
uncertainties/phases, LFV experimental likelihood are missing. Also
the optimized f/Y is NOT the B2 rank1 family used in C1..C4's RG
trajectories; previous scalar-only RG screens CANNOT be carried over
to optimized f/Y without rerunning RGEs. No physical allowed points.
"""
from __future__ import annotations
import argparse
import collections
import csv
import functools
import json
import math
import statistics
import sys
import traceback
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

import zee_barr_zee_fermion_dipoles as bz
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,scalar_kappa,solve_lepton_yukawa,reconstruct_neutrino
)
from gateB2_zee_neutrino_family_scan import (
    subset_lfv,linear_neutrino_operator
)
from gateA1c_charged_singlet_lfv import CHANNELS
from gateA1e_neutral_one_loop_dipoles import partial_radiative_br
from zee_lfv_backend import TREE_CHANNELS,general_neutral_tree_BR
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_gateC1_joined_uv_pilot import digest
from zee_gateD1_joint_300_neutrino_lfv_inventory import (
    STATUS as D1_STATUS,load_cohort,candidate_flavor
)

STATUS='GATE_D2_NEUTRINO_EXACT_PARTIAL_LFV_OPTIMIZATION_NOT_ALLOWED'
PERT=math.sqrt(4*math.pi)
MAX_NEUTRINO_ERROR_EV=1e-9

def optimize_kernels_cache():
    """Loop functions depend on fixed mass ratios, not on Yukawa values."""
    for func in ('scalar_f','pseudoscalar_g'):
        old=getattr(bz,func)
        if not hasattr(old,'cache_info'):
            setattr(bz,func,functools.lru_cache(maxsize=256)(old))

def verify_d1(report_path,b4,b2,c2,c3,c4,c5):
    data=json.loads(Path(report_path).read_text())
    required={'B4':b4,'B2':b2,'C2':c2,'C3':c3,'C4':c4,'C5':c5}
    if data.get('status')!=D1_STATUS:
        raise ValueError('D1 predecessor failed or unexpected status')
    if any(data.get('input_sha256',{}).get(k)!=digest(v)
           for k,v in required.items()):
        raise ValueError('D1 predecessor input SHA mismatch')
    records=data.get('all_available_incomplete_LFV_details',[])
    population=data.get('B2_saved_solution_count_per_candidate',{})
    if (len(records)!=150 or len(population)!=30 or
        sum(population.values())!=150 or
        data.get('cohort',{}).get('independent_complex_neutrino_solutions')!=150):
        raise ValueError('D1 150-solution predecessor inventory inconsistent')
    mapping={}
    for row in records:
        key=(row.get('candidate_id'),row.get('solution_rank_original_B2'))
        if key in mapping:raise ValueError('D1 duplicate saved flavor solution')
        mapping[key]=row
    if len(mapping)!=150:raise ValueError('D1 cannot reidentify all saved roots')
    return data,mapping

def neutrino_family(point,solution):
    """Exact complex-null parametrization from one saved B2 root."""
    f0=complex_matrix(solution['f'],'f')
    known=complex_matrix(solution['Y'],'Y')
    target,_=target_neutrino_matrix()
    kappa=scalar_kappa(point['mH1'],point['mH2'],point['gamma'])
    Y0,rank,_=solve_lepton_yukawa(f0,target,kappa=kappa)
    if rank!=5:raise ValueError('Expected neutrino rank five')
    op=linear_neutrino_operator(f0,kappa)
    _,sig,vh=np.linalg.svd(op,full_matrices=True)
    if np.sum(sig>sig[0]*1e-13)!=5:
        raise ValueError('Unexpected neutrino-constraint null-space rank')
    null=vh[5:,:].conj().T
    if null.shape!=(9,4) or np.max(abs(op@null))>1e-9:
        raise ValueError('Invalid 4-complex-dimensional lepton Yukawa null-space')
    z=np.conj(null).T@(np.asarray(known)-Y0).reshape(9)
    projected=Y0+(null@z).reshape(3,3)
    if np.max(abs(projected-known))>2e-9:
        raise ValueError('Saved neutrino-closed Yukawa not represented by null basis')
    scale=max(.001,float(np.linalg.norm(known)),float(np.linalg.norm(Y0)))
    vector=np.r_[0.,(z/scale).real,(z/scale).imag]
    fY=make_yukawas({
        'f0':f0,'Y0':Y0,'null':null,'scale':scale,
        'kappa':kappa,'target':target,'point':point
    },vector)
    if np.max(abs(fY[1]-known))>2e-9:
        raise ValueError('Neutrino parameterization fails seed roundtrip')
    return {
        'f0':f0,'Y0':Y0,'null':null,'scale':scale,
        'kappa':kappa,'target':target,'point':point,
        'starting_coords':vector,'starting_Y':known
    }

def make_yukawas(family,x):
    x=np.asarray(x,float)
    if x.shape!=(9,) or not np.isfinite(x).all():
        raise ValueError('Nine real optimizer parameters required')
    r=math.exp(float(x[0]))
    z=family['scale']*(x[1:5]+1j*x[5:9])
    f=r*family['f0']
    Y=family['Y0']/r+(family['null']@z).reshape(3,3)
    return f,Y

def amplitude_subset(point,f,Y):
    """Identical channel physics as D1, but bypass reserialization per eval."""
    ratios={}
    for key,settings in CHANNELS.items():
        ii,jj=settings['parent'],settings['daughter']
        a,b=bz.one_loop_amplitudes(point,f,Y,parent=ii,daughter=jj)
        c,d,_=bz.flav_bz_amplitudes(point,Y,parent=ii,daughter=jj)
        br=partial_radiative_br(a+c,b+d,norm_br=settings['norm_br'])
        ratios[key]=float(br/settings['limit'])
    for key,(ii,jj,sp,norm,lim) in TREE_CHANNELS.items():
        br,_=general_neutral_tree_BR(Y,parent=ii,daughter=jj,
            spectator=sp,norm_br=norm,mH=point['mh2'],ma=point['ma'],
            alpha=point['alpha'],beta=point['beta'])
        ratios[key]=float(br/lim)
    if any(not math.isfinite(v) or v<0 for v in ratios.values()):
        raise ValueError('Invalid flavor subset rate')
    return ratios

def objective(family,x):
    try:
        f,Y=make_yukawas(family,x)
        if max(float(np.max(abs(f))),float(np.max(abs(Y))))>=PERT:
            return 1e5+float(max(np.max(abs(f)),np.max(abs(Y))))
        rates=amplitude_subset(family['point'],f,Y)
        return math.log10(max(max(rates.values()),1e-100))
    except (ValueError,OverflowError,FloatingPointError,ArithmeticError):
        return 1e6

def encode(arr):
    z=np.asarray(arr,complex)
    return {'real':z.real.tolist(),'imag':z.imag.tolist()}

def final_solution(point,old,f,Y):
    target,_=target_neutrino_matrix()
    kappa=scalar_kappa(point['mH1'],point['mH2'],point['gamma'])
    err=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=kappa)-target)))
    if not math.isfinite(err) or err>MAX_NEUTRINO_ERROR_EV:
        raise ValueError('Final optimized Yukawa fails neutrino closure')
    if max(float(np.max(abs(f))),float(np.max(abs(Y))))>=PERT:
        raise ValueError('Final optimized Yukawa violates per-entry perturbativity')
    one_rates,one_ratios=subset_lfv(point,f,Y)
    temp={
        'candidate_id':point['id'],'mH1':point['mH1'],
        'mH2':point['mH2'],'gamma':point['gamma'],
        'f':encode(f),'Y':encode(Y),
        'status':'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED',
        'max_abs_f':float(np.max(abs(f))),
        'max_abs_Y':float(np.max(abs(Y))),
        'neutrino_matrix_closure_eV':err,
        'partial_LFV_rates_NOT_FULL':one_rates,
        'partial_LFV_ratios_NOT_EXCLUSION':one_ratios,
        'partial_LFV_score_NOT_EXCLUSION':max(one_ratios.values()),
    }
    output=candidate_flavor(point,temp,0)
    ratios=amplitude_subset(point,f,Y)
    numerical=max(ratios.values())
    final=output['joint_incomplete_LFV_score_NOT_EXCLUSION']
    if not math.isclose(numerical,final,rel_tol=2e-8,abs_tol=1e-14):
        raise ValueError('D1 legacy LFV rate backend disagrees with optimized objective')
    return temp,output,ratios

def optimize_start(point,solution,baseline,*,max_evals):
    fam=neutrino_family(point,solution)
    x0=fam['starting_coords']
    r0=amplitude_subset(point,fam['f0'],fam['starting_Y'])
    prior=max(r0.values())
    if not math.isclose(prior,float(baseline['joint_incomplete_LFV_score_NOT_EXCLUSION']),
                        rel_tol=2e-8,abs_tol=1e-11):
        raise ValueError('D2 original LFV does not reproduce exact D1 baseline')
    # Bounds centered about the ORIGINAL saved f/Y representation.
    # This is a local experiment, not a global Zee Yukawa bound.
    L=math.log(30)
    bounds=[(-L,L)]
    bounds +=[(float(a-3),float(a+3)) for a in x0[1:]]
    result=minimize(
        lambda x:objective(fam,x),x0,method='Powell',
        bounds=bounds,
        options={'maxfev':max_evals,'maxiter':max_evals,
                 'xtol':5e-4,'ftol':3e-4})
    candidates=[(x0,'saved_B2_start')]
    if np.isfinite(result.fun):
        candidates.append((np.asarray(result.x,float),'Powell_optimized'))
    tested=[]
    for x,label in candidates:
        f,Y=make_yukawas(fam,x)
        if max(np.max(abs(f)),np.max(abs(Y)))>=PERT:
            continue
        temp,checked,ratios=final_solution(point,solution,f,Y)
        tested.append((float(checked['joint_incomplete_LFV_score_NOT_EXCLUSION']),
                       label,temp,checked,ratios,x))
    if not tested:
        raise ValueError('Optimizer produced no valid neutrino/f-Y solution')
    best=min(tested,key=lambda t:t[0])
    if best[0]>prior*(1+1e-8):
        raise ValueError('Optimized objective worsens known starting result')
    return {
        'seed_original_score':prior,
        'best_score':best[0],
        'source':best[1],
        'solution':best[2],
        'D1_crosschecked_LFV':best[3],
        'all_channel_ratios':best[4],
        'optimized_variables':best[5].tolist(),
        'optimizer_status':{
            'message':str(result.message),'success':bool(result.success),
            'function_evaluations':int(result.nfev),
            'original_root_permitted_max_evaluations':int(max_evals)},
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('b4-csv','b2-json','c2-summary','c3-summary','c4-summary',
                'c5-summary','d1-summary'):
        ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--max-spectra',type=int,default=27)
    ap.add_argument('--starts-per-spectrum',type=int,default=2)
    ap.add_argument('--max-evals',type=int,default=240)
    args=ap.parse_args()
    if not(1<=args.max_spectra<=30 and 1<=args.starts_per_spectrum<=5
           and 80<=args.max_evals<=2000):
        ap.error('Invalid D2 partial-LFV optimization resource limits')
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        ap.error('Refuse existing output directory')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    report={
        'status':STATUS,'physical_Zee_allowed':None,
        'full_two_loop_dipoles':'NOT_COMPUTED',
        'full_three_lepton_amplitudes':'NOT_COMPUTED',
        'mu_to_e_conversion':'NOT_COMPUTED',
        'full_PMNS_likelihood':'NOT_COMPUTED',
        'CKM_and_modern_bsgamma':'NOT_COMPUTED',
        'HiggsTools':'NOT_COMPUTED',
        'recomputed_full_one_loop_RGE_for_new_optimized_Yukawas':False,
        'global_scalar_vacuum_proven':False,
    }
    try:
        d1,mapping=verify_d1(
            args.d1_summary,args.b4_csv,args.b2_json,args.c2_summary,
            args.c3_summary,args.c4_summary,args.c5_summary)
        points,sols=load_cohort(args.b4_csv,args.b2_json)
        if any(len(v)!=5 for v in sols.values()):
            raise ValueError('D2 pilot expects the exact D1 five-per-spectrum saved roots')
        optimize_kernels_cache()
        saved_theory=d1['model_variant_status']
        candidate_names=[name for name in sorted(points)
            if any(v['scalar_only_candidate_for_further_flavor_work']
                   for v in saved_theory[name].values())]
        if len(candidate_names)!=27:
            raise ValueError('D1 scalar-theory shortlist expected 27 spectra')
        selection=sorted(
            candidate_names,
            key=lambda n:min(
                mapping[(n,k)]['joint_incomplete_LFV_score_NOT_EXCLUSION']
                for k in range(1,len(sols[n])+1)))[:args.max_spectra]
        rows=[];details={}
        for i,name in enumerate(selection,1):
            scores=sorted(range(1,len(sols[name])+1),
                key=lambda rank:mapping[(name,rank)][
                    'joint_incomplete_LFV_score_NOT_EXCLUSION'])
            diagnostics=[]
            for rank in scores[:args.starts_per_spectrum]:
                item=optimize_start(
                    points[name],sols[name][rank-1],mapping[(name,rank)],
                    max_evals=args.max_evals)
                diagnostics.append((rank,item))
            rank,best=min(diagnostics,key=lambda t:t[1]['best_score'])
            baseline=min(mapping[(name,k)]['joint_incomplete_LFV_score_NOT_EXCLUSION']
                         for k in range(1,len(sols[name])+1))
            gain=baseline/max(best['best_score'],1e-100)
            row={
                'candidate_id':name,'roots_considered':len(diagnostics),
                'best_B2_saved_rank':scores[0],
                'best_optimized_from_rank':rank,
                'original_D1_best_partial_score_NOT_EXCLUSION':float(baseline),
                'new_best_partial_score_NOT_EXCLUSION':float(best['best_score']),
                'improvement_factor_of_partial_diagnostic':float(gain),
                'partial_score_below_one_NOT_A_PASS':best['best_score']<1.,
                'max_abs_f_optimized':best['solution']['max_abs_f'],
                'max_abs_Y_optimized':best['solution']['max_abs_Y'],
                'neutrino_closure_eV_optimized':best['solution']['neutrino_matrix_closure_eV'],
                'dominant_incomplete_LFV_channel':max(
                    best['all_channel_ratios'],
                    key=best['all_channel_ratios'].get),
                'any_scalar_variant_passes_C4_with_no_C5_vacuum_witness':True,
                'FULL_RGE_OF_NEW_YUKAWA_MATRICES':'NOT_RECHECKED',
                'FULL_LFV_ALLOWED':'UNKNOWN',
            }
            rows.append(row)
            details[name]={
                'parent_rank':rank,'chosen':best,
                'all_starts':[{ 'parent_rank':k,'best_score':v['best_score'],
                    'original_score':v['seed_original_score'],
                    'optimizer':v['optimizer_status']}
                    for k,v in diagnostics]}
            print('D2_NEUTRINO_EXACT_LFV_OPT',f'{i}/{len(selection)}',name,
                  'original',baseline,'best',best['best_score'],
                  'factor',gain,
                  'partial_score_below_one_NOT_A_PASS',row['partial_score_below_one_NOT_A_PASS'],
                  'dominant',row['dominant_incomplete_LFV_channel'],
                  flush=True)
        report.update({
            'tested_spectra':len(rows),
            'optimization_runs':len(rows)*args.starts_per_spectrum,
            'rows':rows,
            'optimized_full_f_Y_and_partial_flavor_provenance':details,
            'summary':{
                'below_one_PARTIAL_only_NOT_allowed':sum(
                    v['partial_score_below_one_NOT_A_PASS'] for v in rows),
                'largest_partial_diagnostic_improvement':max(
                    v['improvement_factor_of_partial_diagnostic'] for v in rows),
                'median_partial_improvement':statistics.median(
                    v['improvement_factor_of_partial_diagnostic'] for v in rows),
                'smallest_partial_score_found_NOT_A_FIT':min(
                    v['new_best_partial_score_NOT_EXCLUSION'] for v in rows),
                'dominant_partial_channels':dict(collections.Counter(
                    v['dominant_incomplete_LFV_channel'] for v in rows)),
                'full_flavor_viability_NOT_EVALUATED':True,
            },
            'inputs_SHA256':{k:digest(path) for k,path in (
                ('B4',args.b4_csv),('B2',args.b2_json),('C2',args.c2_summary),
                ('C3',args.c3_summary),('C4',args.c4_summary),
                ('C5',args.c5_summary),('D1',args.d1_summary))}
        })
        outfile=args.output_dir/'optimized_partial_LFV_cohort_NOT_ALLOWED.csv'
        with outfile.open('w',newline='') as h:
            writer=csv.DictWriter(h,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
        report['csv']=str(outfile)
        print('D2_COHORT',json.dumps(report['summary']),flush=True)
        print('D2_FULL_ZEE_ALLOWED UNKNOWN',flush=True)
        return 0
    except Exception as exc:
        report.update(status='GATE_D2_FAIL_CLOSED_NOT_ALLOWED',
                      error=repr(exc),traceback=traceback.format_exc())
        print('D2_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        outfile=args.output_dir/'summary.json'
        outfile.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('D2_SUMMARY',outfile,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
