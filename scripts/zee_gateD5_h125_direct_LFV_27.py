#!/usr/bin/env python3
"""Gate D5: NEW exact leading-order 125-GeV Higgs LFV decays for D4 Zee cohort.

D4's 27 optimized general-Zee f,Y configurations satisfy the partial
one-loop+fermion-photon+W-photon LFV diagnostics and D3 scalar running
screen (at least one potential choice each). HOWEVER the Yukawa freedom
used to suppress dipoles can enhance H125 -> e mu, e tau, mu tau at TREE
level, which is not screened by the existing low-energy LFV objective.

Compute all three charged-conjugate summed tree h decays including exact
final-state lepton masses and fully complex physical h Yukawa C_h,
where L=-h bar(ell)_i(C_ij P_L+C*_ji P_R)ell_j:
  Gamma(h->ell_i^- ell_j^+ + ell_i^+ ell_j^-) =
  sqrt(lambda(mh²,mi²,mj²)) / (8 pi mh³)
    * [(|Cij|²+|Cji|²)(mh²-mi²-mj²)
       -4 mi mj Re(Cij*Cji)]
for i!=j. This tends to mh/(8pi)(|Cij|²+|Cji|²).

Also recompute exact h -> charged diagonal leptons at LO and include
them in a LEPTON-ONLY width-corrected proxy:
  Gamma(h)_proxy=Gamma_SM_reference
      -sum_l Gamma_SM(h->ll) +sum_l Gamma_model(h->ll)
      +sum_LFV Gamma_model(h->li lj).
Non-leptonic Higgs partial widths, loop-induced hgg/hγγ (including
new charged scalar loops!), Higgs production categories/acceptance
and global HiggsTools fit are NOT calculated. Thus comparisons to
published search upper bounds are SM-production/reference-width
SCREENS, NOT physical exclusion or complete experimental likelihood.

Reference experimental observed 95% limits (available as of Oct 2026):
  CMS HIG-22-002 h->e mu <4.4e-5 (138/fb, 2023)
  ATLAS JHEP07(2023)166 h->e tau <.20%=.0020
  ATLAS JHEP07(2023)166 h->mu tau <.18%=.0018.
Provide exact source URLs, not guessed newer values.

Require exact B4/B2/C2/C3/C4/C5/D1/D2/D3/D4 input SHA
and D4 27-case source summary. Re-evaluate h physical coupling
matrix from unmodified A1D source and inspect κV/κt/κb for
production/decay-model mismatches. Do not double-count the two
identical-mass C2 scalar-potential variants. Output 27 rows and
per-spectrum h partial widths and reference-limit screen ratios.
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

from gateA1b_hierarchical_no_seed import ME,MMU,MTAU,ML
from gateA1d_neutral_tree_lfv import scalar_couplings
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_gateC1_joined_uv_pilot import digest
from zee_gateD1_joint_300_neutrino_lfv_inventory import load_cohort
from zee_gateD4_W_photon_barr_zee_27 import (
    STATUS as D4_STATUS,verify_d2_d3
)

STATUS="GATE_D5_TREE_H125_LFV_DECAY_27_CONSTRAINED_WIDTH_SCREEN_NOT_ALLOWED"
MH=125.
VEV=246.21965
GAMMA_H_SM_REF=0.00407 # GeV, conventional nominal reference
LEPTON_MASSES=(ME,MMU,MTAU)
CHANNELS={
    'h_to_e_mu':(0,1,4.4e-5,
        'https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-22-002/index.html'),
    'h_to_e_tau':(0,2,.0020,
        'https://link.springer.com/article/10.1007/JHEP07(2023)166'),
    'h_to_mu_tau':(1,2,.0018,
        'https://link.springer.com/article/10.1007/JHEP07(2023)166')
}
SOURCE_KIND="DIRECT_95CL_BR_LIMIT_SM_PRODUCTION_ASSUMPTION_ONLY"

def kallen(s,a,b):
    return float((s-a-b)**2-4*a*b)

def exact_flavor_width(C,*,mh,i,j):
    """Sum both distinct charge-conjugate final states, exact masses."""
    if i==j or not (0<=i<3 and 0<=j<3):
        raise ValueError('Flavor non-diagonal i!=j required')
    if np.shape(C)!=(3,3) or not np.isfinite(C).all():
        raise ValueError('Expect finite 3x3 complex physical scalar Yukawas')
    mi,mj=LEPTON_MASSES[i],LEPTON_MASSES[j]
    s=mh*mh
    if mh<=mi+mj:
        return 0.
    l=max(0.,kallen(s,mi*mi,mj*mj))
    cij,cji=C[i,j],C[j,i]
    spin=((abs(cij)**2+abs(cji)**2)*(s-mi*mi-mj*mj)-
          4*mi*mj*np.real(cij*cji))
    result=math.sqrt(l)/(8*math.pi*mh**3)*spin
    if not math.isfinite(result) or result<-1e-13:
        raise ValueError('Nonfinite/negative two-charge LFV partial width')
    return max(0.,float(result))

def exact_diagonal_width(C,*,mh,i):
    """Full diagonal complex scalar+pseudoscalar coupling convention."""
    mi=LEPTON_MASSES[i]
    if mh<=2*mi:return 0.
    c=complex(C[i,i])
    factor=1-4*(mi/mh)**2
    out=mh/(8*math.pi)*(
        c.real**2*factor**1.5+c.imag**2*factor**.5)
    if out<0 or not math.isfinite(out):
        raise ValueError('Negative/nonfinite diagonal charged lepton width')
    return float(out)

def h125_widths(point,Y):
    Y=np.asarray(Y,complex)
    h=scalar_couplings(Y,mh=MH,mH=point['mh2'],mA=point['ma'],
                       alpha=point['alpha'],beta=point['beta'])[0][0]
    d=float(point['beta'])-float(point['alpha'])
    kappaV=math.cos(d)
    kappa_t=kappaV-math.sin(d)/math.tan(float(point['beta']))
    kappa_b=kappaV+math.sin(d)*math.tan(float(point['beta']))
    partial={}
    for name,(i,j,limit,url) in CHANNELS.items():
        partial[name]=exact_flavor_width(h,mh=MH,i=i,j=j)
    # ML is the shared 3x3 diagonal physical charged-lepton mass matrix.
    smC=np.asarray(ML,complex)/VEV
    if smC.shape!=(3,3):
        raise ValueError('SM charged lepton mass matrix convention changed')
    old_leptonic=sum(exact_diagonal_width(smC,mh=MH,i=i) for i in range(3))
    new_leptonic=sum(exact_diagonal_width(h,mh=MH,i=i) for i in range(3))
    gamma_total=GAMMA_H_SM_REF-old_leptonic+new_leptonic+sum(partial.values())
    if not math.isfinite(gamma_total) or gamma_total<=0:
        raise ValueError('Unphysical nominal/leptonic-updated width estimate')
    return {
        'h125_LFV_partial_widths_GeV':partial,
        'h125_SM_charged_lepton_width_sum_GeV':old_leptonic,
        'h125_model_charged_lepton_width_sum_GeV':new_leptonic,
        'h125_nominal_SM_width_GeV':GAMMA_H_SM_REF,
        'h125_leptonic_only_width_updated_GeV':gamma_total,
        'h125_other_widths_kept_SM_like':True,
        'kappa_V_tree':kappaV,
        'kappa_top_TypeII_ansatz':kappa_t,
        'kappa_bottom_TypeII_ansatz':kappa_b,
        'h125_physical_Yukawa_C':{
            'real':h.real.tolist(),'imag':h.imag.tolist()},
        'nominal_SM_reference_BR':{
            key:width/GAMMA_H_SM_REF for key,width in partial.items()},
        'leptonic_updated_BR_proxy':{
            key:width/gamma_total for key,width in partial.items()},
    }

def verify_d4(d4_path,originals,d2,d3):
    data=json.loads(Path(d4_path).read_text())
    if data.get('status')!=D4_STATUS or data.get('tested')!=27:
        raise ValueError('D4 27-solution summary missing/not successful')
    refs={**originals,'D2':d2,'D3':d3}
    if any(data.get('source_sha256',{}).get(k)!=digest(path)
           for k,path in refs.items()):
        raise ValueError('D4 input provenance SHA does not match')
    rows=data.get('rows',[])
    if len(rows)!=27 or len(set(x.get('candidate_id') for x in rows))!=27:
        raise ValueError('D4 candidates duplicated/missing')
    return {x['candidate_id']:x for x in rows}

def process(point,sol,d4record):
    Y=complex_matrix(sol['Y'],'Y')
    widths=h125_widths(point,Y)
    nominal={}
    corrected={}
    for ch,(i,j,limit,url) in CHANNELS.items():
        nominal[ch]=widths['nominal_SM_reference_BR'][ch]/limit
        corrected[ch]=widths['leptonic_updated_BR_proxy'][ch]/limit
    if not all(np.isfinite(list(nominal.values())+list(corrected.values()))):
        raise ValueError('Nonfinite LFV Higgs score')
    return {
        'candidate_id':point['id'],
        'D4_partial_LFV_max_over_exp_ref_NOT_EXCLUSION':
            d4record['new_partial_score'],
        'h125_lfv_widths':widths,
        'experiment_limit_screen_ratios_SM_nominal_width':nominal,
        'experiment_limit_screen_ratios_leptonic_width_updated':corrected,
        'worst_direct_Higgs_LFV_nominal_ratio':max(nominal.values()),
        'worst_direct_Higgs_LFV_leptonic_updated_ratio':max(corrected.values()),
        'dominant_direct_Higgs_LFV_channel':max(
            corrected,key=lambda x:corrected[x]),
        'all_three_direct_reference_BR_screens_below_one_NOT_ALLOWED':
            max(corrected.values())<1,
        'any_reference_screen_above_one_NOT_EXCLUSION':
            max(corrected.values())>1,
        'signal_strength_and_higgs_total_width_likelihood':'NOT_COMPUTED',
        'physical_Zee_allowed':'UNKNOWN',
    }

def summarise(rows):
    return {
        'unique_neutrino_optimized_spectra':len(rows),
        'nominal_SM_Higgs_width_and_production_assumed':True,
        'h125_direct_LFV_three_channels':list(CHANNELS),
        'all_three_reference_limits_screen_below_one_NOT_ALLOWED':sum(
            x['all_three_direct_reference_BR_screens_below_one_NOT_ALLOWED']
            for x in rows),
        'at_least_one_direct_limit_reference_tension_NOT_EXCLUSION':sum(
            x['any_reference_screen_above_one_NOT_EXCLUSION'] for x in rows),
        'largest_Higgs_LFV_reference_ratio_width_proxy':max(
            x['worst_direct_Higgs_LFV_leptonic_updated_ratio'] for x in rows),
        'dominant_screen_channels':dict(collections.Counter(
            x['dominant_direct_Higgs_LFV_channel'] for x in rows)),
        'full_experimental_higgs_likelihood':'NOT_EVALUATED',
        'physical_Zee_allowed':None,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('b4-csv','b2-json','c2-summary','c3-summary','c4-summary',
                'c5-summary','d1-summary','d2-summary','d3-summary',
                'd4-summary'):
        ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    opts=ap.parse_args()
    if opts.output_dir.exists() and any(opts.output_dir.iterdir()):
        ap.error('Refuse overwriting an earlier report')
    opts.output_dir.mkdir(parents=True,exist_ok=True)
    report={
        'status':STATUS,'physical_Zee_allowed':None,
        'new_observables':'h125->e mu,e tau,mu tau exact tree partial widths',
        'h125_SM_width_GeV_reference':GAMMA_H_SM_REF,
        'h125_total_width_complete':'NOT_COMPUTED',
        'h125_production_signal_strength':'NOT_COMPUTED',
        'HiggsTools':'NOT_COMPUTED',
        'mu_e_conversion':'NOT_COMPUTED',
        'LFV_full_two_loop_and_threebody':'NOT_COMPUTED',
        'meson_quark_flavor':'NOT_COMPUTED',
        'global_tree_vacuum_proof':False,
        'experimental_direct_Higgs_LFV_limits':{
            k:{'observed_limit_95CL':x[2],'source':x[3],
               'limit_assumes_SM_like_production':True}
            for k,x in CHANNELS.items()},
    }
    try:
        original={
            'B4':opts.b4_csv,'B2':opts.b2_json,
            'C2':opts.c2_summary,'C3':opts.c3_summary,
            'C4':opts.c4_summary,'C5':opts.c5_summary,
            'D1':opts.d1_summary}
        results,d3_models=verify_d2_d3(opts.d2_summary,opts.d3_summary,original)
        d4=verify_d4(opts.d4_summary,original,opts.d2_summary,opts.d3_summary)
        points,_=load_cohort(opts.b4_csv,opts.b2_json)
        if set(results)!=set(d4):
            raise ValueError('D2/D4 optimized spectra inconsistent')
        rows=[];all_details={}
        for idx,name in enumerate(sorted(results),1):
            sol=results[name]['chosen']['solution']
            point=points[name]
            row=process(point,sol,d4[name])
            checked=all(d3_models[(name,v)]['C5_no_deeper_witness_NOT_global_certification']
                for v in ('both_lh1_l1_1','both_lh0p4_l1_0p5'))
            passes=any(d3_models[(name,v)]['D3_joint_running_theory_screen_pass']
                for v in ('both_lh1_l1_1','both_lh0p4_l1_0p5'))
            if not checked or not passes:
                raise ValueError('D3 scalar-theory parent not in 27 shortlist')
            rows.append({
                'candidate_id':name,
                'h_to_e_mu_BR_nominal':row['h125_lfv_widths']['nominal_SM_reference_BR']['h_to_e_mu'],
                'h_to_e_tau_BR_nominal':row['h125_lfv_widths']['nominal_SM_reference_BR']['h_to_e_tau'],
                'h_to_mu_tau_BR_nominal':row['h125_lfv_widths']['nominal_SM_reference_BR']['h_to_mu_tau'],
                'h_to_e_mu_BR_leptonic_updated':row['h125_lfv_widths']['leptonic_updated_BR_proxy']['h_to_e_mu'],
                'h_to_e_tau_BR_leptonic_updated':row['h125_lfv_widths']['leptonic_updated_BR_proxy']['h_to_e_tau'],
                'h_to_mu_tau_BR_leptonic_updated':row['h125_lfv_widths']['leptonic_updated_BR_proxy']['h_to_mu_tau'],
                'h125_leptonic_updated_total_width_proxy_GeV':
                    row['h125_lfv_widths']['h125_leptonic_only_width_updated_GeV'],
                'h125_kappa_V':row['h125_lfv_widths']['kappa_V_tree'],
                'h125_kappa_top_TypeII_approx':row['h125_lfv_widths']['kappa_top_TypeII_ansatz'],
                'h125_kappa_bottom_TypeII_approx':row['h125_lfv_widths']['kappa_bottom_TypeII_ansatz'],
                'worst_direct_higgs_LFV_ratio_NOT_PHYSICAL_EXCLUSION':
                    row['worst_direct_Higgs_LFV_leptonic_updated_ratio'],
                'dominant_higgs_LFV_reference_channel':
                    row['dominant_direct_Higgs_LFV_channel'],
                'three_direct_Higgs_reference_screens_below_one_NOT_ALLOWED':
                    row['all_three_direct_reference_BR_screens_below_one_NOT_ALLOWED'],
                'previous_D4_partial_score_NOT_ALLOWED':
                    row['D4_partial_LFV_max_over_exp_ref_NOT_EXCLUSION'],
                'D3_some_theory_variant_pass':True,
                'physical_Zee_allowed':'UNKNOWN',
            })
            all_details[name]=row
            print('D5_H125_DIRECT_LFV',idx,'/27',name,
                  'e_mu',rows[-1]['h_to_e_mu_BR_leptonic_updated'],
                  'e_tau',rows[-1]['h_to_e_tau_BR_leptonic_updated'],
                  'mu_tau',rows[-1]['h_to_mu_tau_BR_leptonic_updated'],
                  'max_to_reference_limit',
                      row['worst_direct_Higgs_LFV_leptonic_updated_ratio'],
                  'SM_production_ASSUMED_NOT_PHYSICAL_VETO',
                  flush=True)
        if len(rows)!=27:raise ValueError('Unexpected D5 cohort size')
        report.update({
            'tested':len(rows),'rows':rows,
            'per_spectrum_details':all_details,
            'cohort':summarise(list(all_details.values())),
            'input_SHA256':{k:digest(v) for k,v in {
                **original,'D2':opts.d2_summary,
                'D3':opts.d3_summary,'D4':opts.d4_summary}.items()},
        })
        target=opts.output_dir/'h125_direct_LFV_27_SM_production_assumed_NOT_ALLOWED.csv'
        with target.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
        report['csv']=str(target)
        print('D5_COHORT',json.dumps(report['cohort']))
        print('D5_FULL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as e:
        report.update(status='GATE_D5_FAIL_CLOSED_NOT_ALLOWED',
                      error=repr(e),traceback=traceback.format_exc())
        print('D5_FAIL_CLOSED',repr(e),file=sys.stderr,flush=True)
        return 1
    finally:
        file=opts.output_dir/'summary.json'
        file.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('D5_SUMMARY',file)

if __name__=='__main__':
    raise SystemExit(main())
