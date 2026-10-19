"""D5 Higgs125 LFV direct-decay exact tree partial-width and source tests.

Validate distinct charge conjugate final state factor, two complex
chiral Yukawa couplings, physical final lepton masses, exact alignment,
SM diagonal widths, lepton-modified total width and D4 SHA ancestry.
"""
from pathlib import Path
import sys
import json
import math
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from gateA1b_hierarchical_no_seed import ME,MMU,MTAU,ML
from gateA1d_neutral_tree_lfv import scalar_couplings
from zee_gateC1_joined_uv_pilot import digest
from zee_gateD4_W_photon_barr_zee_27 import STATUS as D4_STATUS
from zee_gateD5_h125_direct_LFV_27 import (
    STATUS,MH,VEV,GAMMA_H_SM_REF,CHANNELS,
    exact_flavor_width,exact_diagonal_width,kallen,h125_widths,
    verify_d4,process,summarise,
)

def point():
    return {'id':'D5_TEST_ONLY','mh2':580.7,'ma':633.7,
            'alpha':1.398,'beta':1.394,'gamma':1.089,
            'mH1':300.,'mH2':700.}

def Y0():
    return np.zeros((3,3),complex)

class TestD5H125LFV(unittest.TestCase):
    def test_three_2023_published_direct_limits(self):
        self.assertEqual(set(CHANNELS),
                         {'h_to_e_mu','h_to_e_tau','h_to_mu_tau'})
        self.assertEqual(CHANNELS['h_to_e_mu'][2],4.4e-5)
        self.assertEqual(CHANNELS['h_to_e_tau'][2],.002)
        self.assertEqual(CHANNELS['h_to_mu_tau'][2],.0018)
        self.assertTrue(all(k[3].startswith('https://') for k in CHANNELS.values()))

    def test_sm_charged_lepton_matrix_is_diagonal_mass_over_vev(self):
        sm=np.asarray(ML,complex)/VEV
        self.assertEqual(sm.shape,(3,3))
        np.testing.assert_allclose(np.diag(sm),[ME,MMU,MTAU]/np.array([VEV]*3))

    def test_zero_off_diagonal_flavor_width(self):
        C=np.zeros((3,3),complex)
        for i,j,_ ,_ in CHANNELS.values():
            self.assertEqual(exact_flavor_width(C,mh=125.,i=i,j=j),0.)

    def test_one_chiral_off_diagonal_massless_formula(self):
        C=np.zeros((3,3),complex)
        C[0,1]=.01+.02j
        got=exact_flavor_width(C,mh=MH,i=0,j=1)
        approx=MH/(8*math.pi)*abs(C[0,1])**2
        self.assertAlmostEqual(got/approx,1.,delta=2e-6)

    def test_both_chiral_off_diagonal_add_without_spurious_factor_two(self):
        C=np.zeros((3,3),complex)
        C[0,1]=.01;C[1,0]=.02j
        got=exact_flavor_width(C,mh=MH,i=0,j=1)
        expected=MH/(8*math.pi)*(.01**2+.02**2)
        self.assertAlmostEqual(got/expected,1.,delta=2e-6)

    def test_general_complex_phase_cross_term_is_real_and_symmetric(self):
        C=np.zeros((3,3),complex)
        C[0,2]=.002+.004j
        C[2,0]=.003-.001j
        x=exact_flavor_width(C,mh=MH,i=0,j=2)
        self.assertAlmostEqual(x,exact_flavor_width(C,mh=MH,i=2,j=0))
        self.assertGreater(x,0)

    def test_finite_tau_mass_reduces_rate_relative_massless_approx(self):
        C=np.zeros((3,3),complex)
        C[0,2]=1.
        got=exact_flavor_width(C,mh=MH,i=0,j=2)
        self.assertLess(got,MH/(8*math.pi))

    def test_threshold_closure_makes_width_zero(self):
        C=np.zeros((3,3),complex)
        C[0,2]=.5
        self.assertEqual(exact_flavor_width(
            C,mh=MTAU+ME-1e-4,i=0,j=2),0.)

    def test_exact_alignment_alpha_beta_h_has_zero_tree_lfv(self):
        p=point()
        p['alpha']=p['beta']
        Y=Y0();Y[0,1]=.3;Y[2,1]=.1j
        w=h125_widths(p,Y)
        self.assertTrue(all(abs(z)<1e-20 for z in
                            w['h125_LFV_partial_widths_GeV'].values()))
        self.assertAlmostEqual(w['kappa_V_tree'],1.)

    def test_sm_yukawas_at_alignment_reproduce_SM_total_width(self):
        p=point()
        p['alpha']=p['beta']
        w=h125_widths(p,Y0())
        self.assertAlmostEqual(
            w['h125_leptonic_only_width_updated_GeV'],
            GAMMA_H_SM_REF,delta=1e-11)

    def test_complex_diag_pseudoscalar_rate_threshold_correct(self):
        C=np.zeros((3,3),complex)
        C[2,2]=.04j
        gamma=exact_diagonal_width(C,mh=MH,i=2)
        expected=MH/(8*math.pi)*.04**2*math.sqrt(1-4*MTAU**2/MH**2)
        self.assertAlmostEqual(gamma,expected,delta=1e-12)

    def test_partial_width_and_provisional_total_denominator(self):
        p=point()
        p['alpha']=p['beta']-.25
        Y=Y0();Y[0,1]=.003;Y[1,0]=.002j
        w=h125_widths(p,Y)
        part=w['h125_LFV_partial_widths_GeV']['h_to_e_mu']
        self.assertGreater(part,0.)
        self.assertAlmostEqual(
            w['nominal_SM_reference_BR']['h_to_e_mu'],
            part/GAMMA_H_SM_REF,delta=1e-12)
        self.assertAlmostEqual(
            w['leptonic_updated_BR_proxy']['h_to_e_mu'],
            part/w['h125_leptonic_only_width_updated_GeV'],delta=1e-12)
        self.assertTrue(w['h125_other_widths_kept_SM_like'])

    def test_reference_limit_screen_not_physical_exclusion(self):
        p=point()
        p['alpha']=p['beta']-.18
        Y=Y0();Y[0,1]=.05
        rec=process(p,{'Y':{
            'real':Y.real.tolist(),'imag':Y.imag.tolist()
        }},{'new_partial_score':1e-5})
        self.assertGreater(rec['worst_direct_Higgs_LFV_leptonic_updated_ratio'],1)
        self.assertEqual(rec['physical_Zee_allowed'],'UNKNOWN')
        self.assertEqual(rec['signal_strength_and_higgs_total_width_likelihood'],
                         'NOT_COMPUTED')

    def test_width_screen_acceptance_not_full_model_allowed(self):
        p=point()
        rec=process(p,{'Y':{
            'real':Y0().real.tolist(),'imag':Y0().imag.tolist()
        }},{'new_partial_score':.001})
        self.assertTrue(rec['all_three_direct_reference_BR_screens_below_one_NOT_ALLOWED'])
        self.assertEqual(rec['physical_Zee_allowed'],'UNKNOWN')

    def test_failed_D4_source_sha_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            names=('B4','B2','C2','C3','C4','C5','D1')
            sources={name:root/(name+'.txt') for name in names}
            for key,p in sources.items():p.write_text(key)
            d2=root/'D2.json';d3=root/'D3.json'
            d2.write_text('d2');d3.write_text('d3')
            report=root/'D4.json'
            rows=[{'candidate_id':f'B4_{i:07d}'} for i in range(27)]
            report.write_text(json.dumps({
                'status':D4_STATUS,'tested':27,'rows':rows,
                'source_sha256':{k:digest(p) for k,p in {
                    **sources,'D2':d2,'D3':d3}.items()}
            }))
            got=verify_d4(report,sources,d2,d3)
            self.assertEqual(len(got),27)
            d3.write_text('changed')
            with self.assertRaisesRegex(ValueError,'SHA'):
                verify_d4(report,sources,d2,d3)

    def test_large_27_spectrum_aggregation_tracks_direct_higgs_tension(self):
        rows=[]
        for i in range(27):
            rows.append({
                'candidate_id':str(i),
                'all_three_direct_reference_BR_screens_below_one_NOT_ALLOWED':i<17,
                'any_reference_screen_above_one_NOT_EXCLUSION':i>=17,
                'worst_direct_Higgs_LFV_leptonic_updated_ratio':float(i),
                'dominant_direct_Higgs_LFV_channel':
                    'h_to_e_mu' if i%2 else 'h_to_mu_tau'})
        s=summarise(rows)
        self.assertEqual(s['all_three_reference_limits_screen_below_one_NOT_ALLOWED'],17)
        self.assertEqual(s['at_least_one_direct_limit_reference_tension_NOT_EXCLUSION'],10)
        self.assertIsNone(s['physical_Zee_allowed'])

if __name__=='__main__':
    unittest.main()
