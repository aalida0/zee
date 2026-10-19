#!/usr/bin/env python3
"""Gate D4: bosonic W-PHOTON Barr-Zee contribution to D3 Zee LFV amplitudes.

ADD A GENUINE MISSING AMPLITUDE to the 27 D3 optimized f/Y solutions:
  C^{Wgamma}_{L,R} = alpha / (16 pi^3 m_parent v)
      sum_{phi=h,H} g_phiWW F^{phi,L/R}_{daughter,parent} K(mW^2/mphi^2)
  K(z)=3 f(z)+(23/4)g(z)+(3/4)h(z)+(f(z)-g(z))/(2z).

Source: S. Davidson, EPJC 76 (2016) 258, Eq.(24), in the
Chang-Hou-Keung convention for photon-exchange W-Barr-Zee amplitude;
independently compatible with photon-only terms of Eq.(B.28),
arXiv:2111.10464. Haber Barr-Zee f,g,h kernel definitions:
  f=z(2+ln z)+(1-2z)g
  h=z(2g+ln z)/(1-4z).
Our A1D physical scalar definitions:
  h=cos(delta) H_vev -sin(delta) H_perp;
  H=sin(delta) H_vev +cos(delta) H_perp, delta=beta-alpha.
Thus g_hWW=cos(delta), g_HWW=sin(delta), and A1D C_h,C_H
are the actual lepton scalar chiral vertex matrices. The W loop
uses the *CP-even* fields only. We keep the external chirality and
complex-conjugation convention pinned to the existing Davidson-
converted fermion-photon amplitudes in zee_barr_zee_fermion_dipoles.

Important: This is the W-PHOTON neutral CP-even diagram class ONLY.
No W-Z, charged-Higgs/photon or Goldstone-trilinear-beyond-W subset,
full electroweak two-loop, Z penguins, 3body boxes, mu-e conversion.
No physical LFV exclusion, allowed status or final global likelihood.

All 27 D2 optimized complex f/Y are re-read, their exact D3 full-
coupling 10-TeV running classifications retained with D1/D2/D3
source checksum locks. Three radiative channels coherently include:
  A_one_loop + A_(top,bottom,tau gamma) + A_(W gamma)
and all five original tree-level three-lepton subsets remain in
the overall *PARTIAL* score. Numerical kernel, field mixing, and
original D2/D1 baseline are independently tested.
"""
from __future__ import annotations
import argparse
import collections
import csv
from functools import lru_cache
import json
import math
import statistics
import sys
import traceback
from pathlib import Path
import numpy as np
from scipy.integrate import quad

from gateA1b_hierarchical_no_seed import ME,MMU,MTAU
from gateA1c_charged_singlet_lfv import CHANNELS,ALPHA_EM
from gateA1d_neutral_tree_lfv import scalar_couplings
from gateA1e_neutral_one_loop_dipoles import partial_radiative_br
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_barr_zee_kernels import f as scalar_f,g as pseudoscalar_g
import zee_barr_zee_fermion_dipoles as existing
from zee_gateC1_joined_uv_pilot import digest
from zee_gateD1_joint_300_neutrino_lfv_inventory import candidate_flavor,load_cohort
from zee_gateD2_neutrino_exact_partial_LFV_optimization import (
    STATUS as D2_STATUS,optimize_kernels_cache
)
from zee_gateD3_optimized_flavor_full_theory_rerun import STATUS as D3_STATUS

STATUS='GATE_D4_W_PHOTON_TWO_LOOP_EXTENSION_PARTIAL_LFV_NOT_ALLOWED'
MW_GEV=80.377
VEV=246.21965
MASSES=(ME,MMU,MTAU)
TREE_CHANNELS=('mu_to_3e_tree','tau_to_3e_tree','tau_to_3mu_tree',
               'tau_to_mu_ee_tree','tau_to_e_mumu_tree')
SOURCE='Davidson_2016_Eq24_and_arXiv2111.10464_AppB28_PHOTON_W_ONLY'

def independent_h_integral(z):
    """Direct Haber Eq.(59), stable at x(1-x)=z using a t series."""
    z=float(z)
    if not(1e-10<z<1e6) or not math.isfinite(z):
        raise ValueError('Invalid h(z) ratio')
    def fun(x):
        u=x*(1-x)
        t=(u-z)/z
        if abs(t)<1e-4:
            return -.25+t/6-t*t/8+t**3/10-t**4/12
        return -.5*(1/t-math.log1p(t)/(t*t))
    r,e=quad(fun,0,1,epsabs=5e-11,epsrel=5e-11,limit=450)
    if not(math.isfinite(r) and e<=1e-7):
        raise ValueError('Haber h integral failed numerical control')
    return float(r)

@lru_cache(maxsize=256)
def photon_W_kernel(z):
    """Independent f,g,h representations cross-check each other."""
    z=float(z)
    f=scalar_f(z)[0];g=pseudoscalar_g(z)[0]
    if abs(1-4*z)>1e-5:
        h=z*(2*g+math.log(z))/(1-4*z)
    else:
        h=independent_h_integral(z)
    if not all(math.isfinite(v) for v in (f,g,h)):
        raise ValueError('Nonfinite W two-loop kernel')
    result=3*f+23*g/4+3*h/4+(f-g)/(2*z)
    if not math.isfinite(result):
        raise ValueError('Nonfinite W Barr-Zee K(z)')
    return float(result)

def w_photon_amplitudes(point,Y,*,parent,daughter):
    """Output same GeV^-2 C_L/C_R convention as D1 fermion BZ backend."""
    if not(parent in (1,2) and daughter in (0,1) and daughter<parent):
        raise ValueError('Invalid radiative LFV channel')
    Y=np.asarray(Y,complex)
    if Y.shape!=(3,3) or not np.isfinite(Y).all():
        raise ValueError('Expected finite complex general Zee Y')
    delta=float(point['beta'])-float(point['alpha'])
    cd,sd=math.cos(delta),math.sin(delta)
    mats=scalar_couplings(
        Y,mh=125.,mH=point['mh2'],mA=point['ma'],
        alpha=point['alpha'],beta=point['beta'])
    mi=MASSES[parent]
    CL=0j;CR=0j;parts=[]
    prefactor=ALPHA_EM/(16*math.pi**3*mi*VEV)
    for phi,(C,mp),gww in zip(('h','H'),mats[:2],(cd,sd)):
        k=photon_W_kernel((MW_GEV/mp)**2)
        # Compatible with the existing CL,CR convention used for fermion BZ.
        left=C[daughter,parent]
        right=np.conj(C[parent,daughter])
        al=prefactor*gww*left*k
        ar=prefactor*gww*right*k
        CL+=al;CR+=ar
        parts.append({'CP_even_scalar':phi,'mass_GeV':mp,
                      'normalized_phiWW':gww,'K_W_gamma':k,
                      'C_L':[al.real,al.imag],
                      'C_R':[ar.real,ar.imag]})
    return complex(CL),complex(CR),parts

def compare_partial(point,f,Y,previous):
    """Coherently include Wgamma and independently reproduce old D2 rate."""
    data={};radiative_new=[]
    tree=max(float(previous['D1_crosschecked_LFV']['max_tree_3lepton_over_limit_NOT_EXCLUSION']),0.)
    old_dipoles=[]
    for channel,meta in CHANNELS.items():
        parent,daughter=meta['parent'],meta['daughter']
        l,r=existing.one_loop_amplitudes(point,f,Y,parent=parent,daughter=daughter)
        bl,br,_=existing.flav_bz_amplitudes(
            point,Y,parent=parent,daughter=daughter)
        wl,wr,parts=w_photon_amplitudes(
            point,Y,parent=parent,daughter=daughter)
        old=partial_radiative_br(l+bl,r+br,norm_br=meta['norm_br'])/meta['limit']
        new=partial_radiative_br(l+bl+wl,r+br+wr,
                                norm_br=meta['norm_br'])/meta['limit']
        ref=previous['D1_crosschecked_LFV']['radiative_channels'][channel][
            'one_loop_plus_fermion_photon_BZ_subset_ratio_NOT_EXCLUSION']
        if not math.isclose(old,float(ref),rel_tol=2e-8,abs_tol=1e-14):
            raise ValueError('Original D1/D2 partial radiative amplitude did not reproduce')
        if not all(math.isfinite(t) and t>=0 for t in (old,new)):
            raise ValueError('Nonfinite radiative W extension')
        data[channel]={
            'one_loop_plus_fermion_gamma_ratio_NOT_EXCLUSION':float(old),
            'one_loop_plus_fermion_gamma_plus_W_gamma_ratio_NOT_EXCLUSION':float(new),
            'W_gamma_C_L':[wl.real,wl.imag],
            'W_gamma_C_R':[wr.real,wr.imag],
            'W_gamma_amplitude_over_previous_amplitude_norm':
                float(math.hypot(abs(wl),abs(wr))/
                      max(math.hypot(abs(l+bl),abs(r+br)),1e-100)),
            'W_gamma_diagram_parts':parts,
        }
        old_dipoles.append(old)
        radiative_new.append(new)
    old_score=max(old_dipoles+[tree])
    new_score=max(radiative_new+[tree])
    if not math.isclose(old_score,float(previous['best_score']),
                        rel_tol=2e-8,abs_tol=1e-14):
        raise ValueError('D2 partial LFV score not reproduced by D4')
    return {
        'previous_max_partial_ratio_NOT_EXCLUSION':old_score,
        'new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION':new_score,
        'max_tree_3lepton_partial_ratio_UNCHANGED':tree,
        'new_radiative_dominant_channel':
            max(data,key=lambda k:data[k][
                'one_loop_plus_fermion_gamma_plus_W_gamma_ratio_NOT_EXCLUSION']),
        'partial_new_score_below_one_NOT_AN_ALLOWED_CLAIM':bool(new_score<1.),
        'channel_details':data,
    }

def verify_d2_d3(d2file,d3file,originals):
    d2=json.loads(Path(d2file).read_text())
    d3=json.loads(Path(d3file).read_text())
    expected=dict(B4=originals['B4'],B2=originals['B2'],C2=originals['C2'],
                  C3=originals['C3'],C4=originals['C4'],C5=originals['C5'],
                  D1=originals['D1'])
    if (d2.get('status')!=D2_STATUS or
        d2.get('tested_spectra')!=27 or
        d2.get('optimization_runs')!=54 or
        any(d2.get('inputs_SHA256',{}).get(k)!=digest(v)
            for k,v in expected.items())):
        raise ValueError('D2 input/provenance mismatch')
    if (d3.get('status')!=D3_STATUS or
        d3.get('row_count')!=54 or len(d3.get('rows',[]))!=54 or
        d3.get('cohort',{}).get('neutrino_optimized_theory_spectra_tested')!=27 or
        any(d3.get('source_SHA256',{}).get(k)!=digest(v)
            for k,v in {**expected,'D2':d2file}.items())):
        raise ValueError('D3 54-case full-theory provenance mismatch')
    details=d2.get('optimized_full_f_Y_and_partial_flavor_provenance',{})
    if len(details)!=27:raise ValueError('D2 optimized f/Y missing 27 spectra')
    map3={}
    for row in d3['rows']:
        key=row.get('candidate_id'),row.get('variant')
        if key in map3:raise ValueError('Duplicate D3 model configuration')
        map3[key]=row
    if len(map3)!=54:raise ValueError('Incomplete D3 model configurations')
    for name,item in details.items():
        if str(item['chosen']['solution']['candidate_id'])!=name:
            raise ValueError('D2 optimized spectrum ID corrupted')
        for label in ('both_lh1_l1_1','both_lh0p4_l1_0p5'):
            row=map3.get((name,label))
            if row is None or not row.get('C5_no_deeper_witness_NOT_global_certification'):
                raise ValueError('D3 lost required charge-breaking witness status')
            if not math.isclose(
                float(row['D2_optimized_partial_LFV_score_NOT_EXCLUSION']),
                float(item['chosen']['best_score']),rel_tol=1e-9,abs_tol=1e-14):
                raise ValueError('D2/D3 optimized partial LFV mismatch')
    return details,map3

def summarize(rows):
    return {
        'spectra':len(rows),
        'previous_partial_score_below_one':sum(
            row['old_partial_score']<1 for row in rows),
        'W_gamma_extended_partial_score_below_one_NOT_ALLOWED':sum(
            row['new_partial_score']<1 for row in rows),
        'W_gamma_extended_partial_score_ge_one_NOT_EXCLUSION':sum(
            row['new_partial_score']>=1 for row in rows),
        'median_W_gamma_extended_partial_score':statistics.median(
            row['new_partial_score'] for row in rows),
        'worst_new_partial_score':max(row['new_partial_score'] for row in rows),
        'best_new_partial_score':min(row['new_partial_score'] for row in rows),
        'largest_amplitude_expansion_factor':max(
            row['new_partial_score']/max(row['old_partial_score'],1e-100)
            for row in rows),
        'full_physical_LFV_exclusions_made':False,
        'missing_Z_W_and_charged_scalar_BZ_and_3body_loops':True,
        'all_original_C4_C5_theory_screen_flags_preserved':True,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('b4-csv','b2-json','c2-summary','c3-summary','c4-summary',
                'c5-summary','d1-summary','d2-summary','d3-summary'):
        ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        ap.error('Refuse reuse of populated output directory')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    report={
        'status':STATUS,'physically_allowed':None,
        'genuine_new_amplitude_class':'NEUTRAL_CP_EVEN_W_PHOTON_BARR_ZEE_ONLY',
        'full_EW_TWO_LOOP_CALCULATED':False,
        'full_LFV_3LEPTON_CONVERSION':False,
        'modern_two_Hplus_BtoXsGamma':'NOT_COMPUTED',
        'HiggsTools':'NOT_COMPUTED',
        'CKM_quark_matching':'NOT_COMPUTED',
        'global_EW_vacuum_minimum_PROVEN':False,
        'W_kernel_formula':SOURCE,
    }
    try:
        originals={
            'B4':args.b4_csv,'B2':args.b2_json,'C2':args.c2_summary,
            'C3':args.c3_summary,'C4':args.c4_summary,
            'C5':args.c5_summary,'D1':args.d1_summary}
        details,models=verify_d2_d3(args.d2_summary,args.d3_summary,originals)
        points,_=load_cohort(args.b4_csv,args.b2_json)
        optimize_kernels_cache()
        rows=[];out={}
        for name in sorted(details):
            if name not in points:raise ValueError('D2 candidate absent from B4 scalar spectra')
            chosen=details[name]['chosen']
            sol=chosen['solution']
            f=complex_matrix(sol['f'],'f');Y=complex_matrix(sol['Y'],'Y')
            # Baseline chosen['D1_crosschecked_LFV'] was itself
            # checked against all unmodified D1 backend rates in D3.
            score=compare_partial(points[name],f,Y,chosen)
            models_flags={
                lab:bool(models[name,lab]['D3_joint_running_theory_screen_pass'])
                for lab in ('both_lh1_l1_1','both_lh0p4_l1_0p5')}
            row={
                'candidate_id':name,
                'old_partial_score':score['previous_max_partial_ratio_NOT_EXCLUSION'],
                'new_partial_score':score['new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION'],
                'W_gamma_score_shift_factor':(
                    score['new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION']/
                    max(score['previous_max_partial_ratio_NOT_EXCLUSION'],1e-100)),
                'new_dominant_radiative_channel':score['new_radiative_dominant_channel'],
                'mu_to_e_gamma_new_partial_ratio':score['channel_details']['mu_to_e_gamma'][
                    'one_loop_plus_fermion_gamma_plus_W_gamma_ratio_NOT_EXCLUSION'],
                'W_to_original_mu_e_amplitude_norm':score['channel_details']['mu_to_e_gamma'][
                    'W_gamma_amplitude_over_previous_amplitude_norm'],
                'D3_full_theory_any_variant_pass':any(models_flags.values()),
                'D3_full_theory_variant_count':sum(models_flags.values()),
                'W_gamma_extended_score_below_one_NOT_A_PHYSICAL_PASS':
                    score['partial_new_score_below_one_NOT_AN_ALLOWED_CLAIM'],
                'physically_allowed':'UNKNOWN'}
            rows.append(row)
            out[name]={'flavor':score,'D3_theory_screen_variants':models_flags}
            print('D4_W_PHOTON_LFV',len(rows),'/27',name,
                  'old',row['old_partial_score'],
                  'with_Wgamma',row['new_partial_score'],
                  'W_amplitude_rel',row['W_to_original_mu_e_amplitude_norm'],
                  'below_one_PARTIAL_NOT_ALLOWED',row[
                      'W_gamma_extended_score_below_one_NOT_A_PHYSICAL_PASS'],
                  flush=True)
        if len(rows)!=27:raise ValueError('Expected 27 unique optimized D2 spectra')
        report.update({
            'tested':len(rows),'cohort':summarize(rows),
            'rows':rows,'per_channel_amplitude_parts':out,
            'source_sha256':{k:digest(v) for k,v in {
                **originals,'D2':args.d2_summary,'D3':args.d3_summary}.items()}})
        f=args.output_dir/'27_W_photon_extended_LFV_diagnostics_NOT_ALLOWED.csv'
        with f.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
        report['csv']=str(f)
        print('D4_COHORT',json.dumps(report['cohort']))
        print('D4_FULL_ZEE_ALLOWED UNKNOWN')
        return 0
    except Exception as exc:
        report.update(status='GATE_D4_FAIL_CLOSED_NOT_ALLOWED',
                      error=repr(exc),traceback=traceback.format_exc())
        print('D4_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        target=args.output_dir/'summary.json'
        target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('D4_SUMMARY',target)

if __name__=='__main__':
    raise SystemExit(main())
