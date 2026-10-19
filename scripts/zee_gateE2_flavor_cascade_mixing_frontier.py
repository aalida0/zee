#!/usr/bin/env python3
"""Gate E2: full-mixed Wilson-response flavor-vs-Z-H2-H1 mixing diagnostic.

NO independent scan of the general Zee Lagrangian is performed here.
At each fixed E1 scalar masses and tan(beta), vary ONLY the physical
charged-doublet/singlet mixing gamma. The resulting scalar potential,
neutrino mass operator, f/Y and full RG running have NOT been
recomputed, so changed-gamma points are formal charged-sector
COUNTERFACTUALS, NOT viable Zee-model benchmarks.

The source-audited A1V legacy b->s gamma observable is a quadratic
form in the CHARGED-DOUBLET FRACTION x=cos² gamma because the physical
C7/8 Wilson vectors at matching are
  C_SM + x C_H1 + (1-x) C_H2,
and the A1V response in NP Wilson strength k is demonstrably
a quadratic polynomial. Therefore BR_legacy(x) = A+B x+C x².
Three independently evaluated E1 points (pure-heavy, original,
pure-light) uniquely determine A,B,C. VALIDATE this analytic
continuation against a freshly rebuilt A1V SuperIso driver at
three nontrivial gamma choices per spectrum, plus E1 baseline.
Reject >1e-10 absolute BR residual.

The distinctive Zee cascade g_(Z H2 H1) ~ sin(2 gamma); its
strength-squared normalized to its kinematic maximum is
 S_Z=sin²(2 gamma)=4x(1-x).
This is neither BR(H2->H1Z), nor production times branching fraction,
nor a neutrino/flavor/UV fit.

Calculate per fixed-mass spectrum a continuous, analytically minimized
legacy BR for S_Z >= (0, .25, .50, .75, 1.00)*S_Z(original).
Last threshold follows the allowed gamma domain; no physical flavor
exclusion cut is applied. Record how much the legacy NP shift may
be reduced while retaining a specified fraction of the ORIGINAL
off-diagonal Z coupling squared. Most important tests: large flavor
gain vs the S_Z loss, and whether a lower flavor legacy rate
is possible for S_Z >= original (not just selecting gamma->pi/2
where the cascade vertex vanishes).

Strict input locks: E1 27 model summary, source A1V report, pinned A1M
SuperIso vendor library and A1U endpoint reference. Modern 2026
two-charged NNLO matching and SM, total cascade widths and theoretical
vacuum constraints at changed gamma remain NOT calculated.
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

from gateA1r_run_br_pilot import check_superiso_source
from gateA1u_run_legacy_two_state_br import audit_affine_internal_matching
from gateA1v_run_legacy_response import build,evaluate,validate_inputs
from zee_gateC1_joined_uv_pilot import digest

STATUS="GATE_E2_MIXING_QUADRATIC_BSGAMMA_VS_Z_VERTEX_COUNTERFACTUAL_NOT_ALLOWED"
SOURCE_STATUS="GATE_E1_JOINED_27_TWO_CHARGED_BSGAMMA_LEGACY_OBSERVABLE_NO_EXCLUSION"
VERIFY_GAMMAS=(.31,.79,1.33)
FLOOR_FACTORS=(0.,.25,.5,.75,1.)
ABS_BR_RESIDUAL_MAX=1e-10

def zee_z_vertex_strength_squared(gamma):
    """Squared g_ZH1H2 / maximum squared g: sin² 2gamma."""
    return float(math.sin(2*gamma)**2)

def mixing_quadratic_from_e1(row):
    """Exact polynomial interpolation in doublet weight x=cos² gamma."""
    x=math.cos(float(row['gamma']))**2
    if not 1e-5<x<1-1e-5:
        raise ValueError('E1 original gamma too close to a pure-state boundary')
    light=float(row['pure_light_BR'])
    heavy=float(row['pure_heavy_BR'])
    old=float(row['B_to_Xs_gamma_legacy_Zee_BR'])
    SM=float(row['SM_BR_legacy'])
    if not (0<min(light,heavy,old,SM) and
            max(light,heavy,old,SM)<.01):
        raise ValueError('Invalid E1 saved pure/mixed branching ratio')
    a=heavy
    diff=light-heavy
    curvature=(diff*x-(old-heavy))/(x*(1-x))
    slope=diff-curvature
    if abs((a+slope*x+curvature*x*x)-old)>1e-13:
        raise ValueError('E1 mixture polynomial interpolation failure')
    if abs(a+slope+curvature-light)>1e-13:
        raise ValueError('E1 pure-light polynomial endpoint failure')
    return (a,slope,curvature)

def eval_quadratic(poly,gamma):
    x=math.cos(gamma)**2
    a,b,c=poly
    return float((c*x+b)*x+a)

def optimum_under_Z_vertex_floor(poly,original_gamma,relative_floor):
    """Analytic quadratic minimization on one admissible x interval."""
    if not 0<=relative_floor<=1:
        raise ValueError('Z-coupling retention must lie in [0,1]')
    old_z=zee_z_vertex_strength_squared(original_gamma)
    target=old_z*relative_floor
    root=math.sqrt(max(0.,1.-target))
    left=(1-root)/2
    right=(1+root)/2
    xes=[left,right]
    a,b,c=poly
    if abs(c)>1e-16:
        v=-b/(2*c)
        if left<v<right:
            xes.append(v)
    bestx=min(xes,key=lambda x:a+b*x+c*x*x)
    g=math.acos(math.sqrt(bestx))
    val=a+b*bestx+c*bestx*bestx
    if zee_z_vertex_strength_squared(g)+2e-12<target:
        raise AssertionError('Optimized angle failed Z vertex-strength condition')
    return {
        'relative_floor_fraction_of_original_Z_vertex_squared':relative_floor,
        'required_absolute_Z_vertex_squared':target,
        'optimal_gamma_rad':g,
        'optimal_light_doublet_fraction_cos2gamma':bestx,
        'optimal_Z_vertex_squared':zee_z_vertex_strength_squared(g),
        'minimum_legacy_BR':val,
    }

def verify_e1(e1file,root,a1m,a1u):
    obj=json.loads(Path(e1file).read_text())
    if (obj.get('status')!=SOURCE_STATUS or
        obj.get('tested')!=27 or len(obj.get('rows',[]))!=27 or
        not obj.get('cohort',{}).get('all_endpoint_controls_pass') or
        obj.get('BtoXsGamma_physical_exclusions') is not None or
        obj.get('2026_NNLO_full_two_state_validated') is not False):
        raise ValueError('E1 27-spectrum complete and nonexclusion flags missing')
    source=Path(e1file).parent/'A1V_source_pinned_kernel'/'gateA1v_legacy_response.json'
    if obj.get('provenance_sha256',{}).get('A1V_report')!=digest(source):
        raise ValueError('E1 A1V original source report changed')
    if any(obj['provenance_sha256'].get(k)!=digest(p) for k,p in (
            ('A1M',a1m),('A1U',a1u))):
        raise ValueError('E1 A1M/A1U vendor provenance changed')
    predecessor=json.loads(source.read_text())
    if predecessor.get('n_scan_points')!=27:
        raise ValueError('Original A1V source-pinned grid missing 27 inputs')
    provenance=check_superiso_source(root,a1m)
    patch=audit_affine_internal_matching(root)
    if patch.get('internal_CW_mode')!='helper_reload' or provenance[
        'bsgamma_internal_CW_reload_detected']:
        raise ValueError('Original SuperIso-v5 nested helper reload mismatch')
    names=[r['candidate_id'] for r in obj['rows']]
    if len(set(names))!=27:
        raise ValueError('E1 duplicate spectrum')
    if not all(r.get('all_source_pinned_endpoints_consistent') for r in obj['rows']):
        raise ValueError('E1 endpoint audit missing for one spectrum')
    return obj,predecessor

def calculate_row(row,exe):
    orig_gamma=float(row['gamma'])
    original_strength=zee_z_vertex_strength_squared(orig_gamma)
    poly=mixing_quadratic_from_e1(row)
    m1,m2,t=float(row['mH1']),float(row['mH2']),float(row['tanbeta'])
    validated=[]
    residuals=[]
    for g in (*VERIFY_GAMMAS,orig_gamma):
        validate_inputs(m1,m2,g,t)
        actual,_=evaluate(exe,m1,m2,g,t)
        prediction=eval_quadratic(poly,g)
        err=abs(prediction-float(actual['full_Zee_BR']))
        if err>ABS_BR_RESIDUAL_MAX:
            raise ValueError('A1V full mixed Wilson gamma polynomial closure failed '
                             +str((row['candidate_id'],g,err)))
        validated.append({'gamma':g,'A1V_recomputed_BR':actual['full_Zee_BR'],
                          'quadratic_prediction_BR':prediction,
                          'absolute_BR_residual':err})
        residuals.append(err)
    profiles=[optimum_under_Z_vertex_floor(poly,orig_gamma,f) for f in FLOOR_FACTORS]
    old_br=float(row['B_to_Xs_gamma_legacy_Zee_BR'])
    for e in profiles:
        e['legacy_BR_change_from_original']=e['minimum_legacy_BR']-old_br
        e['legacy_BR_gain_relative_original_NP_shift']=(
            (old_br-e['minimum_legacy_BR'])/
            max(abs(float(row['NP_delta_BR_legacy'])),1e-30))
        e['model_is_full_neutrino_compatible_at_new_gamma']='UNTESTED'
        e['scalar_vacuum_RGE_valid_at_new_gamma']='UNTESTED'
    return {
        'candidate_id':row['candidate_id'],
        'mH1':m1,'mH2':m2,
        'original_gamma':orig_gamma,
        'original_legacy_BR':old_br,
        'original_legacy_NP_shift':row['NP_delta_BR_legacy'],
        'original_sin2_2gamma':original_strength,
        'quadratic_A_heavy_only':poly[0],
        'quadratic_B':poly[1],
        'quadratic_C':poly[2],
        'quadratic_curvature_nonnegative':poly[2]>=-1e-10,
        'maximum_direct_vendor_crosscheck_residual_BR':max(residuals),
        'direct_A1V_vendor_checks':validated,
        'retained_Z_vertex_coupling_frontier':profiles,
        'complete_h2_to_h1Z_branching_fraction':'NOT_COMPUTED_CHANGED_GAMMA',
        'full_scalar_neutrino_LFV_theory_at_altered_gamma':'NOT_RECHECKED',
        'experiment_exclusion_or_allowed':'UNKNOWN',
    }

def summarize(rows):
    baseline=[r['original_legacy_BR'] for r in rows]
    no_loss=[r['retained_Z_vertex_coupling_frontier'][-1] for r in rows]
    half=[r['retained_Z_vertex_coupling_frontier'][2] for r in rows]
    def reduced(e):
        return e['legacy_BR_change_from_original'] < -1e-9
    return {
        'spectra':len(rows),'vendor_independent_gamma_crosschecks':sum(
            len(r['direct_A1V_vendor_checks']) for r in rows),
        'largest_vendor_quadratic_BR_residual':max(
            r['maximum_direct_vendor_crosscheck_residual_BR'] for r in rows),
        'all_27_original_NP_shifts_positive':all(
            r['original_legacy_NP_shift']>0 for r in rows),
        'number_with_BR_reduction_at_same_or_higher_Z_vertex_strength_squared':
            sum(reduced(e) for e in no_loss),
        'number_with_BR_reduction_at_at_least_half_original_Z_vertex_strength_squared':
            sum(reduced(e) for e in half),
        'median_min_BR_at_same_Z_vertex_strength_squared':
            statistics.median(e['minimum_legacy_BR'] for e in no_loss),
        'median_min_BR_at_half_original_Z_vertex_strength_squared':
            statistics.median(e['minimum_legacy_BR'] for e in half),
        'gamma_counterfactuals_physical_allowed_or_excluded':None,
        'no_claim_about_cascade_branching_ratios':True,
        'no_modern_NNLO_matching_or_experimental_likelihood':True,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--e1-summary',type=Path,required=True)
    ap.add_argument('--vendor-root',type=Path,required=True)
    ap.add_argument('--a1m-provenance',type=Path,required=True)
    ap.add_argument('--a1u-result',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        ap.error('Refuse overwriting prior E2 run')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    result={
        'status':'GATE_E2_FAIL_CLOSED_NOT_ALLOWED',
        'physical_Zee_allowed':None,
        'full_NNLO_two_Hplus_inclusive_BR':False,
        'global_vacuum_retested_at_changed_gamma':False,
        'optimized_neutrino_LFV_retested_at_changed_gamma':False,
        'H2_to_H1Z_partial_width_ratio_recomputed':False,
        'gamma_only_fixed_masses_counterfactual':True,
    }
    try:
        source,predecessor=verify_e1(
            args.e1_summary,args.vendor_root,args.a1m_provenance,args.a1u_result)
        exe=args.output_dir/'gateE2_source_pinned_A1V'
        rebuilt=build(args.vendor_root,exe)
        previous=predecessor['build']
        for key in ('library_SHA256','driver_SHA256'):
            if rebuilt[key]!=previous[key]:
                raise ValueError('E2 rebuilt vendor/source disagrees with E1 '+key)
        rows=[]
        for i,r in enumerate(source['rows'],1):
            item=calculate_row(r,exe)
            rows.append(item)
            print('E2_FLAVOR_CASCADE_ANGLE',f'{i}/27',r['candidate_id'],
                  'original_gamma',item['original_gamma'],
                  'Zstrength2',item['original_sin2_2gamma'],
                  'old_BR',item['original_legacy_BR'],
                  'best_BR_keep_Zstrength',item[
                      'retained_Z_vertex_coupling_frontier'][-1]['minimum_legacy_BR'],
                  'best_BR_keep_half_Zstrength',item[
                      'retained_Z_vertex_coupling_frontier'][2]['minimum_legacy_BR'],
                  'max_VENDOR_BR_residual',item[
                      'maximum_direct_vendor_crosscheck_residual_BR'],flush=True)
        if len(rows)!=27:
            raise ValueError('Incomplete E2 cohort')
        cohort=summarize(rows)
        result.update(
            status=STATUS, tested=len(rows), rows=rows, cohort=cohort,
            not_an_experimental_exclusion=True,
        )
        target=args.output_dir/'mixing_Zvertex_vs_legacy_bsgamma_27_NOT_ALLOWED.csv'
        with target.open('w',newline='') as f:
            keys=['candidate_id','mH1','mH2','original_gamma',
                  'original_sin2_2gamma','original_legacy_BR',
                  'original_legacy_NP_shift',
                  'maximum_direct_vendor_crosscheck_residual_BR']
            keys +=['min_BR_keep_Zstrength2_fraction_'+str(frac).replace('.','p')
                    for frac in FLOOR_FACTORS]
            writer=csv.DictWriter(f,fieldnames=keys)
            writer.writeheader()
            for r in rows:
                entry={k:r[k] for k in keys[:8]}
                for j,frac in enumerate(FLOOR_FACTORS):
                    entry[keys[8+j]]=r['retained_Z_vertex_coupling_frontier'][j][
                        'minimum_legacy_BR']
                writer.writerow(entry)
        result['csv']=str(target)
        result['source_SHA256']={
            'E1':digest(args.e1_summary),
            'A1M':digest(args.a1m_provenance),
            'A1U':digest(args.a1u_result),
            'rebuilt_driver':rebuilt['driver_SHA256'],
            'rebuilt_vendor_library':rebuilt['library_SHA256'],
        }
        print('E2_COHORT',json.dumps(cohort))
        print('E2_PHYSICAL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as exc:
        result.update(error=repr(exc),traceback=traceback.format_exc())
        print('E2_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        file=args.output_dir/'summary.json'
        file.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('E2_SUMMARY',file,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
