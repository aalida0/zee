"""D4 W-photon Barr-Zee new amplitude numerical and physics regressions.

Check independent W f,g,h kernels, exact aligned/degenerate-scalar
cancellations, proportionality and chirality phases, and coherent
one-loop+fermion-photon+W-photon addition without any 'allowed' label.
"""
from pathlib import Path
import math
import json
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,scalar_kappa,reconstruct_neutrino
)
from gateB2_zee_neutrino_family_scan import subset_lfv
from gateA1c_charged_singlet_lfv import CHANNELS
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_barr_zee_kernels import f as scalar_f,g as pseudoscalar_g
from zee_gateC1_joined_uv_pilot import digest
from zee_gateD1_joint_300_neutrino_lfv_inventory import candidate_flavor
from zee_gateD2_neutrino_exact_partial_LFV_optimization import STATUS as D2_STATUS
from zee_gateD3_optimized_flavor_full_theory_rerun import STATUS as D3_STATUS
from zee_gateD4_W_photon_barr_zee_27 import (
    STATUS,VEV,MW_GEV,independent_h_integral,photon_W_kernel,
    w_photon_amplitudes,compare_partial,verify_d2_d3,summarize
)

def example_point():
    return {'id':'D4_TEST','beta':1.394,'alpha':1.398,'gamma':1.089,
            'mH1':300.,'mH2':700.,'mh2':580.7,'ma':633.7}

def starting_neutrino_solution(point):
    target,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(target)
    k=scalar_kappa(point['mH1'],point['mH2'],point['gamma'])
    Y,rank,_=solve_lepton_yukawa(f,target,kappa=k)
    assert rank==5
    error=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=k)-target)))
    one,ratios=subset_lfv(point,f,Y)
    def pack(z):
        z=np.asarray(z,complex)
        return {'real':z.real.tolist(),'imag':z.imag.tolist()}
    solution={'candidate_id':point['id'],
       'mH1':point['mH1'],'mH2':point['mH2'],'gamma':point['gamma'],
       'status':'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED',
       'neutrino_matrix_closure_eV':error,'f':pack(f),'Y':pack(Y),
       'partial_LFV_score_NOT_EXCLUSION':max(ratios.values()),
       'partial_LFV_rates_NOT_FULL':one,
       'partial_LFV_ratios_NOT_EXCLUSION':ratios,
       'max_abs_f':float(np.max(abs(f))),
       'max_abs_Y':float(np.max(abs(Y)))}
    return f,Y,solution

class TestGateD4WPhoton(unittest.TestCase):
    def test_haber_h_identity_matches_independent_integral(self):
        for z in (.0004,.014,.033,.1,.245,.255,.413,.9,2.5):
            g=pseudoscalar_g(z)[0]
            h=z*(2*g+math.log(z))/(1-4*z)
            independent=independent_h_integral(z)
            self.assertAlmostEqual(h,independent,delta=4e-8)

    def test_haber_h_degeneracy_z_quarter_is_finite(self):
        val=independent_h_integral(.25)
        self.assertTrue(math.isfinite(val))
        self.assertLess(val,0.)
        self.assertAlmostEqual(photon_W_kernel(.25),
            3*scalar_f(.25)[0]+23*pseudoscalar_g(.25)[0]/4+
            3*val/4+(scalar_f(.25)[0]-pseudoscalar_g(.25)[0])/(.5),
            delta=1e-8)

    def test_W_kernel_independent_direct_formula(self):
        for z in (.01,.04,.1,.413,1.):
            f=scalar_f(z)[0];g=pseudoscalar_g(z)[0]
            h=independent_h_integral(z)
            expected=3*f+5*g+.75*(g+h)+(f-g)/(2*z)
            self.assertAlmostEqual(photon_W_kernel(z),expected,
                                   delta=4e-8)

    def test_W_absent_for_CP_odd_A_and_no_phantom_third_part(self):
        p=example_point()
        Y=np.ones((3,3),complex)*.001
        _,_,parts=w_photon_amplitudes(p,Y,parent=1,daughter=0)
        self.assertEqual([z['CP_even_scalar'] for z in parts],['h','H'])

    def test_alignment_delta_zero_has_no_LFV_W_photon(self):
        p=example_point()
        p['alpha']=p['beta']
        Y=np.zeros((3,3),complex);Y[0,1]=.03
        cl,cr,_=w_photon_amplitudes(p,Y,parent=1,daughter=0)
        self.assertLess(abs(cl),1e-20)
        self.assertLess(abs(cr),1e-20)

    def test_degenerate_h_and_H_CPeven_W_cancels(self):
        p=example_point();p['mh2']=125.
        Y=np.zeros((3,3),complex);Y[0,1]=.025+1j*.015
        Y[1,0]=.042-1j*.016
        cl,cr,_=w_photon_amplitudes(p,Y,parent=1,daughter=0)
        self.assertLess(abs(cl),1e-17)
        self.assertLess(abs(cr),1e-17)

    def test_W_gamma_lepton_phases_follow_existing_chirality(self):
        p=example_point()
        Y=np.zeros((3,3),complex)
        Y[0,1]=.03+1j*.012
        Y[1,0]=.02+1j*.017
        a,b,_=w_photon_amplitudes(p,Y,parent=1,daughter=0)
        phase=np.exp(1j*.47)
        Y*=phase
        c,d,_=w_photon_amplitudes(p,Y,parent=1,daughter=0)
        self.assertAlmostEqual(abs(c-phase*a),0.,delta=1e-16)
        self.assertAlmostEqual(abs(d-phase.conjugate()*b),0.,delta=1e-16)

    def test_exact_mass_basis_mixing_product_reproduces_Davidson_W_signs(self):
        # A1D: C_h=-sin(delta)Y, C_H=cos(delta)Y, while
        # W couplings are cos(delta),sin(delta), respectively.
        from gateA1c_charged_singlet_lfv import ALPHA_EM
        p=example_point()
        p['alpha']=p['beta']-.17
        Y=np.zeros((3,3),complex)
        Y[0,1]=.024+.017j
        Y[1,0]=.015-.005j
        left,right,_=w_photon_amplitudes(
            p,Y,parent=1,daughter=0)
        delta=p['beta']-p['alpha']
        pref=ALPHA_EM/(16*math.pi**3*.1056583745*VEV)
        diff=(photon_W_kernel((MW_GEV/p['mh2'])**2)-
              photon_W_kernel((MW_GEV/125.)**2))
        mix=math.sin(delta)*math.cos(delta)
        self.assertAlmostEqual(abs(left-pref*mix*Y[0,1]*diff),
                               0.,delta=5e-17)
        self.assertAlmostEqual(abs(right-pref*mix*Y[1,0].conjugate()*diff),
                               0.,delta=5e-17)

    def test_W_diagrams_scale_linearly_in_offdiagonal_Y(self):
        p=example_point()
        Y=np.zeros((3,3),complex)
        Y[0,1]=.04+1j*.01
        Y[1,0]=.03
        a,b,_=w_photon_amplitudes(p,Y,parent=1,daughter=0)
        Y*=2.
        c,d,_=w_photon_amplitudes(p,Y,parent=1,daughter=0)
        self.assertLess(abs(c-2*a),1e-15)
        self.assertLess(abs(d-2*b),1e-15)

    def test_W_gamma_lepton_channel_taus_supported(self):
        p=example_point()
        Y=np.zeros((3,3),complex)
        Y[1,2]=.025;Y[2,0]=.036j
        for parent,daughter in ((2,1),(2,0)):
            a,b,_=w_photon_amplitudes(p,Y,parent=parent,daughter=daughter)
            self.assertTrue(math.isfinite(abs(a)+abs(b)))

    def test_invalid_W_channel_and_malformed_Y_rejected(self):
        p=example_point()
        with self.assertRaisesRegex(ValueError,'radiative LFV'):
            w_photon_amplitudes(p,np.zeros((3,3)),parent=0,daughter=1)
        with self.assertRaisesRegex(ValueError,'complex general Zee'):
            w_photon_amplitudes(p,np.zeros((2,3)),parent=1,daughter=0)

    def test_coherent_D2_partial_amplitudes_recovered_exactly(self):
        p=example_point()
        f,Y,s=starting_neutrino_solution(p)
        original=candidate_flavor(p,s,1)
        previous={'D1_crosschecked_LFV':original,
                  'best_score':original['joint_incomplete_LFV_score_NOT_EXCLUSION']}
        outcome=compare_partial(p,f,Y,previous)
        self.assertAlmostEqual(
            outcome['previous_max_partial_ratio_NOT_EXCLUSION'],
            previous['best_score'],
            delta=1e-8*max(1.,previous['best_score']))
        self.assertEqual(set(outcome['channel_details']),set(CHANNELS))
        self.assertTrue(math.isfinite(
            outcome['new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION']))

    def test_wrong_D2_baseline_fails_before_any_new_claim(self):
        p=example_point()
        f,Y,s=starting_neutrino_solution(p)
        original=candidate_flavor(p,s,1)
        original['radiative_channels']['mu_to_e_gamma'][
            'one_loop_plus_fermion_photon_BZ_subset_ratio_NOT_EXCLUSION']*=100.
        previous={'D1_crosschecked_LFV':original,
                  'best_score':original['joint_incomplete_LFV_score_NOT_EXCLUSION']}
        with self.assertRaisesRegex(ValueError,'did not reproduce'):
            compare_partial(p,f,Y,previous)

    def test_D2_D3_provenance_requires_27_textures_and_54_RGE_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            originals={k:root/f'{k}.txt' for k in ('B4','B2','C2','C3','C4','C5','D1')}
            for k,v in originals.items():v.write_text(k)
            d2=root/'D2.json';d3=root/'D3.json'
            results={}
            rows=[]
            for i in range(27):
                name=f'B4_{i:07d}'
                results[name]={
                    'chosen':{'solution':{'candidate_id':name},
                              'best_score':.005}}
                for variant in ('both_lh1_l1_1','both_lh0p4_l1_0p5'):
                    rows.append({'candidate_id':name,'variant':variant,
                        'C5_no_deeper_witness_NOT_global_certification':True,
                        'D2_optimized_partial_LFV_score_NOT_EXCLUSION':.005})
            d2.write_text(json.dumps({'status':D2_STATUS,
                'tested_spectra':27,'optimization_runs':54,
                'optimized_full_f_Y_and_partial_flavor_provenance':results,
                'inputs_SHA256':{k:digest(v) for k,v in originals.items()}}))
            d3.write_text(json.dumps({'status':D3_STATUS,
                'row_count':54,'rows':rows,
                'cohort':{'neutrino_optimized_theory_spectra_tested':27},
                'source_SHA256':{**{k:digest(v) for k,v in originals.items()},
                                 'D2':digest(d2)}}))
            got,mapping=verify_d2_d3(d2,d3,originals)
            self.assertEqual(len(got),27)
            self.assertEqual(len(mapping),54)
            originals['B4'].write_text('different inputs')
            with self.assertRaisesRegex(ValueError,'provenance'):
                verify_d2_d3(d2,d3,originals)

    def test_summary_refuses_to_equate_partial_to_allowed(self):
        rows=[{'candidate_id':str(i),
            'old_partial_score':.0001,
            'new_partial_score':.02 if i<13 else 8.,
            } for i in range(27)]
        result=summarize(rows)
        self.assertEqual(result['W_gamma_extended_partial_score_below_one_NOT_ALLOWED'],13)
        self.assertEqual(result['W_gamma_extended_partial_score_ge_one_NOT_EXCLUSION'],14)
        self.assertFalse(result['full_physical_LFV_exclusions_made'])

if __name__=='__main__':
    unittest.main()
