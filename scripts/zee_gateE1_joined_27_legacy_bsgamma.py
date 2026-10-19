#!/usr/bin/env python3
"""Gate E1: ONE 27-spectrum model-joined two-charged Zee b->s gamma LEGACY audit.

Physics task: C2--D5 found 27 neutrino-compatible, partial-LFV-suppressed,
running scalar-theory-screened charged Higgs spectra. Their Type-II quark
couplings generate a second, INDEPENDENT strong constraint from inclusive
B -> Xs gamma. Use the source-audited A1U/A1V coherent two-charged
SuperIso-v5 interface (not a naive average of charged-Higgs BRs) for
all 27 spectra and preserve all earlier report/input SHA fingerprints.

The pre-existing A1V tool compiles an unmodified A1M isolated SuperIso
library and wraps its hidden CW_calculator high-scale reload, so the
combined physical C7/C8 Wilson coefficients consistently enter BOTH
low-scale RG and nonperturbative/electromagnetic terms.

E1 additionally checks each sampled spectrum at gamma=0, pi/2, and
degenerate charged masses, verifying mixing endpoints at the observable
level. It logs linear vs quadratic NP terms via A1V's k-probe. This is a
27-point selected-sample quark-flavor SENSITIVITY STUDY, not a full 2026
NNLO two-state inclusive BR prediction, calibrated model likelihood or
exclusion. Legacy SuperIso SM baseline differs materially from current
Misiak et al (2026) central SM. Avoid assigning experiment-based CLs.

Inputs: original saved B4/B2/C2..C5/D1..D5 reports, source-pinned
A1M SuperIso and validated A1U 300/700 GeV source/endpoint report.
No regeneration or modification of any input.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
import math
import statistics
import subprocess
import sys
import traceback
from pathlib import Path

from gateA1b_hierarchical_no_seed import MZ
from gateA1v_run_legacy_response import (
    STATUS as A1V_POINT_STATUS,evaluate as superiso_evaluate,
    validate_inputs as validate_charged_inputs
)
from zee_gateC1_joined_uv_pilot import digest
from zee_gateD1_joint_300_neutrino_lfv_inventory import load_cohort
from zee_gateD5_h125_direct_LFV_27 import STATUS as D5_STATUS

STATUS="GATE_E1_JOINED_27_TWO_CHARGED_BSGAMMA_LEGACY_OBSERVABLE_NO_EXCLUSION"
A1V_REPORT_STATUS="GATE_A1V_LEGACY_RESPONSE_AND_SCAN_PILOT_NOT_EXCLUSION"
HFLAV_EXP_REFERENCE=3.49e-4
HFLAV_EXP_ERROR_REFERENCE=0.19e-4
MODERN_SM_REFERENCE=3.54e-4
MODERN_SM_THEORY_ERROR=0.14e-4
ENDPOINT_ABS_TOL=5e-10

def validate_provenance(paths):
    """Require exact SHA ancestry D5 -> D4 -> D3 -> D2 and original B4."""
    d5=json.loads(paths['D5'].read_text())
    if (d5.get('status')!=D5_STATUS or d5.get('tested')!=27 or
        len(d5.get('rows',[]))!=27 or
        len(d5.get('per_spectrum_details',{}))!=27):
        raise ValueError('D5 verified 27-spectrum provenance missing')
    required=('B4','B2','C2','C3','C4','C5','D1','D2','D3','D4')
    for name in required:
        if d5.get('input_SHA256',{}).get(name)!=digest(paths[name]):
            raise ValueError('D5 ancestor SHA mismatch for '+name)
    rows=d5['rows']
    names=[z.get('candidate_id') for z in rows]
    if len(set(names))!=27 or not all(isinstance(n,str) for n in names):
        raise ValueError('D5 duplicate/invalid candidate identity')
    for row in rows:
        if row.get('physical_Zee_allowed')!='UNKNOWN':
            raise ValueError('D5 improperly labelled physical acceptance')
    return {r['candidate_id']:r for r in rows}

def build_grid(model_points,names,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    for name in sorted(names):
        point=model_points[name]
        m1,m2,g=float(point['mH1']),float(point['mH2']),float(point['gamma'])
        beta=float(point['beta'])
        t=math.tan(beta)
        validate_charged_inputs(m1,m2,g,t)
        if m2-m1<=MZ:
            raise ValueError('Expected on-shell charged Higgs cascade closed: '+name)
        rows.append({'candidate_id':name,'mH1':m1,'mH2':m2,
                     'gamma':g,'tanbeta':t,
                     'mH2_minus_mH1_GeV':m2-m1,
                     'doublet_fraction_H1':math.cos(g)**2,
                     'doublet_fraction_H2':math.sin(g)**2})
    with dest.open('w',newline='') as f:
        fields=['mH1','mH2','gamma','tanbeta']
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k:r[k] for k in fields} for r in rows])
    return rows

def compare_legacy_result(inp,res):
    """A1V C driver parsed Wilson-level two-state BR via 5 NP strengths."""
    for key in ('mH1','mH2','gamma','tanbeta'):
        if not math.isclose(float(inp[key]),float(res['input'][key]),
                            rel_tol=1e-11,abs_tol=1e-9):
            raise ValueError('A1V charged input/grid order mismatch '+key)
    sm=float(res['SM_BR'])
    full=float(res['full_Zee_BR'])
    linear=float(res['linear_delta_BR'])
    quad=float(res['quadratic_delta_BR'])
    if not (0.<sm<.01 and 0.<full<.01 and
            math.isfinite(linear) and math.isfinite(quad)):
        raise ValueError('Invalid SuperIso legacy observable')
    if not math.isclose(full-sm,linear+quad,rel_tol=1e-8,abs_tol=1e-11):
        raise ValueError('A1V linear+quadratic decomposition not closed')
    if res.get('classification')!='LEGACY_FLAVOUR_OBSERVABLE_ONLY_NO_EXCLUSION':
        raise ValueError('A1V returned an unexpected classification')
    return {
        'SM_BR_legacy':sm,'B_to_Xs_gamma_legacy_Zee_BR':full,
        'NP_delta_BR_legacy':full-sm,
        'NP_linear_BR_term_legacy':linear,
        'NP_quadratic_BR_term_legacy':quad,
        'NP_fraction_of_legacy_SM_BR':(full-sm)/sm,
        'legacy_raw_difference_from_HFLAV_reference':full-HFLAV_EXP_REFERENCE,
        'legacy_difference_over_HFLAV_experimental_error_ONLY_NOT_PULL':
            (full-HFLAV_EXP_REFERENCE)/HFLAV_EXP_ERROR_REFERENCE,
        'legacy_NP_delta_over_experimental_error_ONLY_NOT_SIGNIFICANCE':
            (full-sm)/HFLAV_EXP_ERROR_REFERENCE,
        'modern_2026_SM_prediction_NOT_applied_to_legacy_rate':True,
        'theory_and_exp_likelihood_NOT_COMPUTED':True
    }

def endpoint_controls(exe,point,full):
    """Pure charged-doublet states and two-state equal-mass observable checks."""
    m1,m2,g,t=(point[k] for k in ('mH1','mH2','gamma','tanbeta'))
    light,_=superiso_evaluate(exe,m1,m2,0.,t)
    heavy,_=superiso_evaluate(exe,m1,m2,math.pi/2,t)
    deg,_=superiso_evaluate(exe,m1,m1,g,t)
    both_light,_=superiso_evaluate(exe,m1,m1,0.,t)
    vals=(light['full_Zee_BR'],heavy['full_Zee_BR'],
          deg['full_Zee_BR'],both_light['full_Zee_BR'])
    if any(not math.isfinite(v) for v in vals):
        raise ValueError('Nonfinite endpoint check')
    delta=abs(deg['full_Zee_BR']-both_light['full_Zee_BR'])
    if delta>ENDPOINT_ABS_TOL:
        raise ValueError('Degenerate charged-Higgs mixing invariance violated')
    # At gamma 0 and pi/2 the doublet fraction resides in exactly
    # one of the two charged physical states, regardless of the other mass.
    if not math.isclose(light['SM_BR'],full['SM_BR'],
                        rel_tol=5e-10,abs_tol=1e-12):
        raise ValueError('A1V standalone pure-state SM closure failed')
    if not math.isclose(heavy['SM_BR'],full['SM_BR'],
                        rel_tol=5e-10,abs_tol=1e-12):
        raise ValueError('A1V heavy endpoint SM closure failed')
    return {
        'pure_light_BR':vals[0],
        'pure_heavy_BR':vals[1],
        'equal_mass_BR':vals[2],
        'equal_mass_gamma_zero_BR':vals[3],
        'degenerate_mass_gamma_dependence_residual':delta,
        'pure_light_minus_SM_BR':vals[0]-full['SM_BR'],
        'pure_heavy_minus_SM_BR':vals[1]-full['SM_BR'],
        'all_source_pinned_endpoints_consistent':True,
    }

def aggregate(rows):
    return {
        'model_spectra':len(rows),
        'independent_observable_cases':len(rows),
        'legacy_Zee_BR_min':min(r['B_to_Xs_gamma_legacy_Zee_BR'] for r in rows),
        'legacy_Zee_BR_median':statistics.median(
            r['B_to_Xs_gamma_legacy_Zee_BR'] for r in rows),
        'legacy_Zee_BR_max':max(r['B_to_Xs_gamma_legacy_Zee_BR'] for r in rows),
        'median_NP_BR_delta_legacy':statistics.median(
            r['NP_delta_BR_legacy'] for r in rows),
        'num_positive_NP_shift':sum(r['NP_delta_BR_legacy']>0 for r in rows),
        'num_negative_NP_shift':sum(r['NP_delta_BR_legacy']<0 for r in rows),
        'num_NP_delta_larger_than_HFLAV_experimental_error_NOT_EXCLUSION':sum(
            abs(r['NP_delta_BR_legacy'])>HFLAV_EXP_ERROR_REFERENCE
            for r in rows),
        'all_endpoint_controls_pass':all(
            r['all_source_pinned_endpoints_consistent'] for r in rows),
        'legacy_SM_reference_differs_from_modern_SM':True,
        '2026_precision_SM_and_NP_scheme_consistently_combined':False,
        'experiment_correlated_theory_error_and_CL_NOT_IMPLEMENTED':True,
        'Zee_model_allowed_or_excluded':None,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('b4-csv','b2-json','c2-summary','c3-summary','c4-summary',
                 'c5-summary','d1-summary','d2-summary','d3-summary',
                 'd4-summary','d5-summary'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--vendor-root',type=Path,required=True)
    p.add_argument('--a1m-provenance',type=Path,required=True)
    p.add_argument('--a1u-result',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--skip-endpoint-controls',action='store_true')
    opts=p.parse_args()
    if opts.output_dir.exists() and any(opts.output_dir.iterdir()):
        p.error('Refuse overwriting output from a prior run')
    opts.output_dir.mkdir(parents=True,exist_ok=True)
    paths={
        'B4':opts.b4_csv,'B2':opts.b2_json,'C2':opts.c2_summary,
        'C3':opts.c3_summary,'C4':opts.c4_summary,
        'C5':opts.c5_summary,'D1':opts.d1_summary,'D2':opts.d2_summary,
        'D3':opts.d3_summary,'D4':opts.d4_summary,'D5':opts.d5_summary}
    report={
        'status':'GATE_E1_FAILED_CLOSED_NOT_ALLOWED',
        'physical_Zee_allowed':None,
        'BtoXsGamma_physical_exclusions':None,
        '2026_NNLO_full_two_state_validated':False,
        'HFLAV_experimental_reference':{
            'BR':HFLAV_EXP_REFERENCE,'experimental_error':HFLAV_EXP_ERROR_REFERENCE,
            'source':'https://hflav-eos.web.cern.ch/hflav-eos/rare/Apr2023/html/radll/Badmix/BR_Badmix_Xs_gamma.html'},
        '2026_modern_SM_REFERENCE_NOT_USED_IN_COMBINED_PREDICTION':{
            'BR':MODERN_SM_REFERENCE,
            'theory_error':MODERN_SM_THEORY_ERROR,
            'source':'https://arxiv.org/abs/2608.29863'},
        'full_matching_likelihood_NOT_IMPLEMENTED':True,
        'type_II_quark_Yukawa_symmetry_verified_UV':False,
        'combined_scalar_LFV_Higgs_flavor_model_allowed':None,
    }
    try:
        originals=validate_provenance(paths)
        model,_=load_cohort(opts.b4_csv,opts.b2_json)
        if not set(originals).issubset(model) or len(originals)!=27:
            raise ValueError('D5 selected model set is not in source B4/B2')
        cohort=build_grid(model,originals,opts.output_dir/'A1V_grid_27.csv')
        legacy=json.loads(opts.a1u_result.read_text())
        if (legacy.get('status')!=
            'GATE_A1U_FULL_LEGACY_SUPERISO_TWO_STATE_BR_ENDPOINT_CLOSED_NOT_2026_EXCLUSION'
            or not legacy.get('all_A1R_physical_endpoint_checks_pass')):
            raise ValueError('A1U legacy vendor model source control not validated')
        bench=legacy['benchmark']
        command=[
            sys.executable,str(Path(__file__).with_name('gateA1v_run_legacy_response.py')),
            '--vendor-root',str(opts.vendor_root),
            '--a1m-provenance',str(opts.a1m_provenance),
            '--a1u-result',str(opts.a1u_result),
            '--mH1',str(bench['mH1_GeV']),
            '--mH2',str(bench['mH2_GeV']),
            '--gamma',str(bench['gamma_rad']),
            '--tanbeta',str(bench['tanbeta']),
            '--grid-csv',str(opts.output_dir/'A1V_grid_27.csv'),
            '--max-points','27',
            '--skip-scale-diagnostic',
            '--output-dir',str(opts.output_dir/'A1V_source_pinned_kernel'),
        ]
        process=subprocess.run(
            command,capture_output=True,text=True,check=False,timeout=900)
        (opts.output_dir/'A1V_stdout.log').write_text(process.stdout)
        (opts.output_dir/'A1V_stderr.log').write_text(process.stderr)
        if process.returncode:
            raise RuntimeError('A1V source-pinned SuperIso driver failed: '+
                               process.stdout[-1500:]+process.stderr[-2000:])
        a1v_file=opts.output_dir/'A1V_source_pinned_kernel'/'gateA1v_legacy_response.json'
        a1v=json.loads(a1v_file.read_text())
        if (a1v.get('status')!=A1V_REPORT_STATUS or
            a1v.get('n_scan_points')!=27 or
            len(a1v.get('scan_flavour_only',[]))!=27 or
            a1v.get('modern_2026_full_NNLO_validated') is not False or
            a1v.get('experimental_likelihood_validated') is not False):
            raise ValueError('Invalid inherited A1V legacy 27-spectrum report')
        exe=opts.output_dir/'A1V_source_pinned_kernel'/'gateA1v_legacy_response'
        rows=[]
        for i,(inputs,res) in enumerate(zip(cohort,a1v['scan_flavour_only']),1):
            outcome=compare_legacy_result(inputs,res)
            if opts.skip_endpoint_controls:
                controls={'all_source_pinned_endpoints_consistent':None}
            else:
                controls=endpoint_controls(exe,inputs,res)
            name=inputs['candidate_id']
            d5=originals[name]
            row={
                'candidate_id':name,
                **inputs,**outcome,**controls,
                'D5_direct_higgs_LFV_ratio_NOT_EXCLUSION':float(
                    d5['worst_direct_higgs_LFV_ratio_NOT_PHYSICAL_EXCLUSION']),
                'D4_optimized_partial_LFV_ratio_NOT_EXCLUSION':float(
                    d5['previous_D4_partial_score_NOT_ALLOWED']),
                'D3_optimized_full_running_theory_screen_exists':bool(
                    d5['D3_some_theory_variant_pass']),
                'Zee_physically_allowed':'UNKNOWN',
            }
            rows.append(row)
            print('E1_LEGACY_BSGAMMA',f'{i}/27',name,
                'BR',row['B_to_Xs_gamma_legacy_Zee_BR'],
                'delta_from_SM_legacy',row['NP_delta_BR_legacy'],
                'linear',row['NP_linear_BR_term_legacy'],
                'quadratic',row['NP_quadratic_BR_term_legacy'],
                'reference_deviation_over_EXP_ERROR_ONLY',
                row['legacy_difference_over_HFLAV_experimental_error_ONLY_NOT_PULL'],
                'physical_exclusion_UNKNOWN',flush=True)
        if len(rows)!=27:raise ValueError('Incomplete 27-spectra E1 result')
        report.update(status=STATUS,rows=rows,tested=27,cohort=aggregate(rows),
            'provenance_sha256':{
                **{k:digest(v) for k,v in paths.items()},
                'A1U':digest(opts.a1u_result),
                'A1M':digest(opts.a1m_provenance),
                'A1V_report':digest(a1v_file),
            })
        outfile=opts.output_dir/'27_model_joined_legacy_bsgamma_NOT_EXCLUSION.csv'
        with outfile.open('w',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
        report['csv']=str(outfile)
        print('E1_27_LEGACY_BSGAMMA_COHORT',json.dumps(report['cohort']))
        print('E1_FULL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as exc:
        report['error']=repr(exc);report['traceback']=traceback.format_exc()
        print('E1_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        dest=opts.output_dir/'summary.json'
        dest.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('E1_SUMMARY',dest,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
