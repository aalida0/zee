#!/usr/bin/env python3
"""Gate E3: source-pinned 2026 Eq.(4) LO Wilson 27-spectrum FLAVOR/CASCADE frontier.

For each E1/E2 spectrum, independently re-run the previously audited A1S
C7,C8 matching probe at EXACT mu0=160 GeV for both physical charged
masses and identical tan(beta). This is a genuinely different LEFT
observable approximation from E1/E2's old SuperIso full legacy BR:

 Misiak et al., arXiv:2608.29863v1, Eq.(4):
  BR(B->Xs gamma)*1e4 = 3.54 -8.51 DeltaC7_LO -2.16 DeltaC8_LO,
  Gamma_cut=1.6 GeV, mu0=160 GeV.

The two charged mass eigenstates contribute at the WILSON LEVEL:
  DeltaC_i(x)=x*DeltaC_i(mH1)+(1-x)*DeltaC_i(mH2),
  x=cos²(gamma).
The Eq4 LO result is affine in x, in contrast to legacy E2's EXACT
quadratic Wilson-response BR. Build a parallel analytic minimum of Eq4
for the SAME five lower bounds on S_Z=sin²(2gamma) relative to the
original Zee vertex, and compare its qualitative trade-off with E2
without EVER combining the two perturbative schemes numerically.

Source-pin exact E1/E2/A1M/A1U SHA fingerprints. Recompile the original
A1S probe against the authenticated A1M library (no vendor modification).
Check all 27 physical inputs, equality of original E2/E1 spectrum
labels and gamma, 2026 SM=3.54 and Eq4 coefficients, sample orthogonal
endpoints, and interpolated direct LO matching at original angle.

NO EXPERIMENTAL ALLOWED/EXCLUDED. In particular:
 - Eq4 omits O(DeltaC²) terms, NLO/NNLO BSM matching, operators beyond
   Q7,Q8, matching-scheme uncertainties/correlations;
 - the 2026 published 670-GeV single-Type-II 95% CL limit was based
   on a FULL NNLO 2HDM-II calculation, not this Eq4 expansion;
 - E2/E3 altered gamma angles are fixed-mass counterfactuals:
   scalar vacuum, neutrino matrix, lepton flavor and UV running are
   untested at those counterfactual angles;
 - S_Z is a squared coupling proxy, NOT BR(H2->H1 Z), and production/
   total width are not recomputed.

This is one large 54-source-probe/27-spectrum joined experiment, not a
new physics allowed-point scan. Published modern Eq4 bounds require a
separate validated likelihood and scheme/matching treatment.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import statistics
import subprocess
import sys
import traceback
from pathlib import Path

from gateA1r_run_br_pilot import check_superiso_source,compile_pilot
from gateA1s_run_modern_2026_screen import (
    K7,K8,MU0_GEV,MODERN_SM,PDG_EXP,
    combine,parse_probe,linearized_2026
)
from zee_gateC1_joined_uv_pilot import digest
from zee_gateE2_flavor_cascade_mixing_frontier import (
    STATUS as E2_STATUS,SOURCE_STATUS as E1_STATUS,
    FLOOR_FACTORS,zee_z_vertex_strength_squared,
    optimum_under_Z_vertex_floor
)

STATUS='GATE_E3_2026_EQ4_LO_TWO_CHARGED_27_FRONTIER_NOT_EXCLUSION'
PROBE='gateA1s_probe_modern_2026_lo.c'
E1A1V='A1V_source_pinned_kernel/gateA1v_legacy_response.json'
MAX_SCALE=160.

def verify_inputs(e1_path,e2_path,a1m,a1u):
    e1=json.loads(Path(e1_path).read_text())
    e2=json.loads(Path(e2_path).read_text())
    source=Path(e1_path).parent/E1A1V
    if (e1.get('status')!=E1_STATUS or e1.get('tested')!=27 or
        len(e1.get('rows',[]))!=27 or
        not e1.get('cohort',{}).get('all_endpoint_controls_pass') or
        e1.get('2026_NNLO_full_two_state_validated') is not False):
        raise ValueError('E3 requires completed 27-row nonexclusion E1')
    if (e2.get('status')!=E2_STATUS or e2.get('tested')!=27 or
        len(e2.get('rows',[]))!=27 or
        e2.get('cohort',{}).get('vendor_independent_gamma_crosschecks')!=108 or
        e2.get('physical_Zee_allowed') is not None):
        raise ValueError('E3 requires complete 108-control nonexclusion E2')
    if (e1.get('provenance_sha256',{}).get('A1V_report')!=digest(source) or
        e2.get('source_SHA256',{}).get('E1')!=digest(e1_path)):
        raise ValueError('E3 legacy A1V/E1/E2 report provenance mismatch')
    for key,actual in (('A1M',a1m),('A1U',a1u)):
        for obj,tag in ((e1.get('provenance_sha256',{}),'E1'),
                        (e2.get('source_SHA256',{}),'E2')):
            if obj.get(key)!=digest(actual):
                raise ValueError(f'E3 {tag} {key} source provenance mismatch')
    old={r['candidate_id']:r for r in e1['rows']}
    newer={r['candidate_id']:r for r in e2['rows']}
    if len(old)!=27 or len(newer)!=27 or set(old)!=set(newer):
        raise ValueError('E3 E1/E2 candidates duplicate/missing')
    for name in old:
        a,b=old[name],newer[name]
        for x,y in [('mH1','mH1'),('mH2','mH2'),('gamma','original_gamma')]:
            if not math.isclose(float(a[x]),float(b[y]),
                                rel_tol=1e-12,abs_tol=1e-10):
                raise ValueError('E1/E2 spectrum/mixing identity mismatch '+name)
        if not math.isclose(float(a['B_to_Xs_gamma_legacy_Zee_BR']),
                            float(b['original_legacy_BR']),
                            rel_tol=1e-12,abs_tol=1e-14):
            raise ValueError('E3 old legacy branch ratio identity mismatch')
        if len(b['retained_Z_vertex_coupling_frontier'])!=len(FLOOR_FACTORS):
            raise ValueError('E3 previous E2 frontier grid incomplete')
        for k,floor in enumerate(FLOOR_FACTORS):
            got=b['retained_Z_vertex_coupling_frontier'][k]
            if not math.isclose(float(got[
                'relative_floor_fraction_of_original_Z_vertex_squared']),
                floor,abs_tol=1e-14):
                raise ValueError('E3 E2 frontier coverage changed')
    return old,newer,e1,e2

def modern_lo_coefficients(binary,mass,tanbeta):
    p=subprocess.run(
        [str(binary.resolve()),f'{mass:.17g}',f'{tanbeta:.17g}'],
        capture_output=True,text=True,check=False,timeout=90)
    if p.returncode:
        raise RuntimeError(
            f'A1S matching probe failed mass={mass} tanbeta={tanbeta}: '
            +p.stderr[-1400:]+p.stdout[-1000:])
    z=parse_probe(p.stdout,mass,tanbeta)
    if z['matching_scale_GeV']!=MU0_GEV:
        raise ValueError('E3 2026 Eq4 C7/C8 matching scale mismatch')
    return z,p.stdout

def modern_affine_profile(light,heavy,original_gamma):
    """BR Eq4 is affine in cos² gamma by LO Wilson superposition."""
    modern_light=linearized_2026(light['delta_C7_LO'],light['delta_C8_LO'])
    modern_heavy=linearized_2026(heavy['delta_C7_LO'],heavy['delta_C8_LO'])
    # E2 minimizer is general for A+B*x+C*x^2; here C=0 exactly.
    poly=(modern_heavy['linearized_predicted_central_times_1e4'],
          modern_light['linearized_predicted_central_times_1e4']-
              modern_heavy['linearized_predicted_central_times_1e4'],
          0.)
    return poly

def evaluate_case(row,e2,light,heavy):
    g=float(row['gamma'])
    original=combine(light,heavy,g)
    poly=modern_affine_profile(light,heavy,g)
    x=math.cos(g)**2
    expected=poly[0]+poly[1]*x
    actual=float(original['linearized_predicted_central_times_1e4'])
    if abs(expected-actual)>1e-11:
        raise ValueError('Modern Eq4 affine mixing closure failed')
    minima=[];legacy=e2['retained_Z_vertex_coupling_frontier']
    for j,floor in enumerate(FLOOR_FACTORS):
        opt=optimum_under_Z_vertex_floor(poly,g,floor)
        old=legacy[j]
        new_min=opt['minimum_legacy_BR']
        # Here optimum_under_Z_vertex_floor is only a generic math
        # quadratic minimizer, outputs same key for either input units.
        # Modern 'new_min' is in 1e-4 units, never mix with legacy BR.
        at_legacy_opt=combine(light,heavy,float(old['optimal_gamma_rad']))
        minimum_legacy_scheme=float(old['minimum_legacy_BR'])
        if abs(new_min-(poly[0]+poly[1]*math.cos(opt['optimal_gamma_rad'])**2))>1e-11:
            raise ValueError('E3 modern minimum not on exact analytic profile')
        minima.append({
            'Z_vertex_strength_fraction_of_original':floor,
            'modern_optimal_gamma_rad':float(opt['optimal_gamma_rad']),
            'modern_optimal_sin_squared_2gamma':float(opt['optimal_Z_vertex_squared']),
            'modern_minimum_Eq4_BR_times_1e4':float(new_min),
            'modern_Eq4_change_from_original_times_1e4':float(new_min-actual),
            'modern_Eq4_at_legacy_optimal_gamma_times_1e4':
                float(at_legacy_opt['linearized_predicted_central_times_1e4']),
            'legacy_optimized_BR_DONT_COMBINE_WITH_MODERN':minimum_legacy_scheme,
            'legacy_optimal_gamma_rad':float(old['optimal_gamma_rad']),
            'same_2026_and_legacy_best_gamma':math.isclose(
                float(opt['optimal_gamma_rad']),
                float(old['optimal_gamma_rad']),abs_tol=1e-8),
        })
    return {
        'candidate_id':row['candidate_id'],
        'mH1':float(row['mH1']),'mH2':float(row['mH2']),
        'tanbeta':float(row['tanbeta']),
        'original_gamma':g,
        'original_Z_vertex_squared':zee_z_vertex_strength_squared(g),
        'LO_delta_C7_light_mu0_160':light['delta_C7_LO'],
        'LO_delta_C8_light_mu0_160':light['delta_C8_LO'],
        'LO_delta_C7_heavy_mu0_160':heavy['delta_C7_LO'],
        'LO_delta_C8_heavy_mu0_160':heavy['delta_C8_LO'],
        'LO_delta_C7_Zee_mu0_160':original['LO_delta_C7_mu0_160'],
        'LO_delta_C8_Zee_mu0_160':original['LO_delta_C8_mu0_160'],
        '2026_Eq4_original_LO_linearized_BR_times_1e4':actual,
        '2026_Eq4_original_LO_linearized_NP_shift_times_1e4':
            original['linearized_shift_times_1e4'],
        'legacy_E1_original_BR_NOT_COMMENSURATE':
            float(row['B_to_Xs_gamma_legacy_Zee_BR']),
        'mixing_original_affine_check_abs_times_1e4':abs(expected-actual),
        '2026_Eq4_frontier':minima,
        'physical_Zee_model_allowed_or_excluded':'UNKNOWN',
        'full_NNLO_matching_or_BR_and_likelihood':False,
        'new_gamma_neutrino_scalar_flavor_theory_revalidated':False,
    }

def summarize(rows):
    same=[r['2026_Eq4_frontier'][-1] for r in rows]
    half=[r['2026_Eq4_frontier'][2] for r in rows]
    return {
        'spectra':len(rows),
        'charged_scalar_LO_matching_inputs_assembled':2*len(rows),
        'all_27_legacy_E2_complete_provenance':True,
        'eq4_160GeV_LO_modern_2026_source':"arxiv:2608.29863v1 Eq.(4)",
        'modern_original_median_BR_times_1e4':statistics.median(
            x['2026_Eq4_original_LO_linearized_BR_times_1e4'] for x in rows),
        'modern_original_min_BR_times_1e4':min(
            x['2026_Eq4_original_LO_linearized_BR_times_1e4'] for x in rows),
        'modern_original_max_BR_times_1e4':max(
            x['2026_Eq4_original_LO_linearized_BR_times_1e4'] for x in rows),
        'modern_min_half_Z_strength_median_BR_times_1e4':statistics.median(
            x['modern_minimum_Eq4_BR_times_1e4'] for x in half),
        'modern_min_same_Z_strength_median_BR_times_1e4':statistics.median(
            x['modern_minimum_Eq4_BR_times_1e4'] for x in same),
        'reduction_at_no_Z_coupling_loss':sum(
            x['modern_Eq4_change_from_original_times_1e4']<-1e-8
            for x in same),
        'reduction_keep_at_least_half_Z_strength':sum(
            x['modern_Eq4_change_from_original_times_1e4']<-1e-8
            for x in half),
        'same_gamma_minimizer_between_modern_linearized_and_legacy':
            sum(x['same_2026_and_legacy_best_gamma'] for x in half),
        '2026_full_TypeII_670GeV_bound_reused_as_Zee_exclusion':False,
        'modern_Eq4_small_NP_assumption_unquantified':True,
        'physical_Zee_allowed_or_excluded':None,
        'no_legacy_modern_absolute_BR_addition':True,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--e1-summary',type=Path,required=True)
    p.add_argument('--e2-summary',type=Path,required=True)
    p.add_argument('--vendor-root',type=Path,required=True)
    p.add_argument('--a1m-provenance',type=Path,required=True)
    p.add_argument('--a1u-result',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    opts=p.parse_args()
    if opts.output_dir.exists() and any(opts.output_dir.iterdir()):
        p.error('E3 requires new output dir')
    opts.output_dir.mkdir(parents=True,exist_ok=True)
    result={'status':'GATE_E3_FAIL_CLOSED_NOT_ALLOWED',
            'physical_Zee_allowed':None,
            'modern_2026_full_NNLO_two_charged_Zee_model':False,
            '2026_precision_matching_scheme_validated_for_Eq4':False,
            'LO_linearized_missing_quadratic_NP_terms':True,
            'E2_and_E3_changed_gamma_counterfactual_not_revalidated':True}
    try:
        old,new,e1,e2=verify_inputs(
            opts.e1_summary,opts.e2_summary,opts.a1m_provenance,opts.a1u_result)
        if (K7!=-8.51 or K8!=-2.16 or MU0_GEV!=160. or
            MODERN_SM['central_times_1e4']!=3.54 or
            PDG_EXP['central_times_1e4']!=3.49):
            raise ValueError('2026 published Eq4 numeric contract changed')
        source=check_superiso_source(opts.vendor_root,opts.a1m_provenance)
        driver=Path(__file__).with_name(PROBE)
        binary=opts.output_dir/'gateE3_2026_LO_matching_probe'
        built=compile_pilot(opts.vendor_root,binary,driver,False)
        cached={};raw=[];rows=[]
        for i,name in enumerate(sorted(old),1):
            row=old[name]
            probes=[]
            for mass in (float(row['mH1']),float(row['mH2'])):
                t=float(row['tanbeta'])
                key=(mass,t)
                if key not in cached:
                    cached[key],stdout=modern_lo_coefficients(binary,mass,t)
                    raw.append(f'SPECTRUM={name} mass={mass} tanbeta={t}\n'+stdout)
                probes.append(cached[key])
            outcome=evaluate_case(row,new[name],*probes)
            rows.append(outcome)
            half=outcome['2026_Eq4_frontier'][2]
            print('E3_MODERN_EQ4_WILSON_FRONTIER',f'{i}/27',name,
                  'dC7',outcome['LO_delta_C7_Zee_mu0_160'],
                  'dC8',outcome['LO_delta_C8_Zee_mu0_160'],
                  'Eq4_orig_times_1e4',outcome['2026_Eq4_original_LO_linearized_BR_times_1e4'],
                  'Eq4_halfZ_min_times_1e4',half['modern_minimum_Eq4_BR_times_1e4'],
                  'legacy_halfZ_min_separate_BR',half['legacy_optimized_BR_DONT_COMBINE_WITH_MODERN'],
                  'full_NNLO_exclusion_UNKNOWN',flush=True)
        if len(rows)!=27:
            raise ValueError('E3 incomplete source-matched Eq4 27 spectrum set')
        cohort=summarize(rows)
        cohort['actual_unique_vendor_LO_probes_run']=len(cached)
        cohort['cached_matching_inputs_reused']=54-len(cached)
        result.update(status=STATUS,tested=len(rows),rows=rows,cohort=cohort,
                      provenance={
                          'E1':digest(opts.e1_summary),
                          'E2':digest(opts.e2_summary),
                          'A1M':digest(opts.a1m_provenance),
                          'A1U':digest(opts.a1u_result),
                          'A1S_source_pinned_C_driver':digest(driver),
                          'A1M_build':built,
                          'A1M_source_check':source})
        (opts.output_dir/'A1S_54_charged_LO_matching_raw.log').write_text(
            '\n'.join(raw))
        filename=opts.output_dir/'2026_Eq4_LO_27_flavor_cascade_NOT_EXCLUSION.csv'
        keys=['candidate_id','mH1','mH2','tanbeta','original_gamma',
              'LO_delta_C7_Zee_mu0_160','LO_delta_C8_Zee_mu0_160',
              '2026_Eq4_original_LO_linearized_BR_times_1e4']
        with filename.open('w',newline='') as out:
            writer=csv.DictWriter(out,fieldnames=keys+
                ['modern_min_half_Z_strength_BR_times_1e4',
                 'legacy_min_half_Z_strength_BR_DIFFERENT_SCHEME'])
            writer.writeheader()
            for row in rows:
                a=row['2026_Eq4_frontier'][2]
                writer.writerow({**{k:row[k] for k in keys},
                    'modern_min_half_Z_strength_BR_times_1e4':
                        a['modern_minimum_Eq4_BR_times_1e4'],
                    'legacy_min_half_Z_strength_BR_DIFFERENT_SCHEME':
                        a['legacy_optimized_BR_DONT_COMBINE_WITH_MODERN']})
        result['csv']=str(filename)
        print('E3_COHORT',json.dumps(cohort))
        print('E3_FULL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as exc:
        result.update(error=repr(exc),traceback=traceback.format_exc())
        print('E3_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        dest=opts.output_dir/'summary.json'
        dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('E3_SUMMARY',dest,flush=True)

if __name__=='__main__':
    raise SystemExit(main())
