"""Independent mathematical checks of Zee Type-II two-Higgs LO b->s gamma.

Uses standalone high precision mpmath transcription of SuperIso Eq. 49,
NOT production functions, plus exact Zee mixing identities from EPJC 2021.
No branching ratios or exclusion calculation.
"""
import copy
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from module5.bsgamma_lo import loop_functions,compute,STATUS

def oracle(x):
    with mp.workdps(90):
        y=mp.mpf(str(x))
        if y==1: return dict(F7_1=mp.mpf(-5)/48,F8_1=mp.mpf(-1)/16,F7_2=mp.mpf(-7)/36,F8_2=mp.mpf(-1)/6)
        d=y-1
        return dict(F7_1=y*(7-5*y-8*y*y)/(24*d**3)+y*y*(3*y-2)*mp.log(y)/(4*d**4),
                    F8_1=y*(2+5*y-y*y)/(8*d**3)-3*y*y*mp.log(y)/(4*d**4),
                    F7_2=y*(3-5*y)/(12*d**2)+y*(3*y-2)*mp.log(y)/(6*d**3),
                    F8_2=y*(3-y)/(4*d**2)-y*mp.log(y)/(2*d**3))

class LoMatchingTests(unittest.TestCase):
    def setUp(self):
        self.common={'beta_rad':math.atan(5.3),'gamma_rad':1.09,
                     'mt_MSbar_GeV':163.0,'matching_scale_GeV':160.0}
        self.masses={'mH1_GeV':550.,'mH2_GeV':900.}

    def result(self,**changes):
        p={**self.common,**self.masses,**changes}
        return compute(**p)

    def test_loop_functions_90digit_values(self):
        for x in (1e-5,0.01,0.05,0.1,0.5,0.98,0.99999999,1.0,1.00000001,1.02,2.,10.,200.):
            vals=loop_functions(x);ind=oracle(x)
            for name,v in vals.items():
                self.assertAlmostEqual(v/float(ind[name]),1.,delta=2e-11,msg=f'{name} at x={x}')

    def test_exact_x_one_limits(self):
        expected={'F7_1':-5/48,'F8_1':-1/16,'F7_2':-7/36,'F8_2':-1/6}
        self.assertEqual(loop_functions(1.),expected)

    def test_source_superiso_type_ii_sign_and_quark_weights(self):
        r=self.result(gamma_rad=0)
        self.assertEqual(r['charged_scalars'][1]['delta_C7'],0.)
        self.assertEqual(r['charged_scalars'][1]['delta_C8'],0.)
        f=oracle((163/550)**2)
        tanb=5.3
        c7=float(f['F7_1'])/(3*tanb**2)+float(f['F7_2'])
        c8=float(f['F8_1'])/(3*tanb**2)+float(f['F8_2'])
        self.assertAlmostEqual(r['delta_C7_LO_at_matching_scale'],c7,delta=1e-13)
        self.assertAlmostEqual(r['delta_C8_LO_at_matching_scale'],c8,delta=1e-13)
        self.assertLess(c7,0.)
        self.assertLess(c8,0.)

    def test_two_scalar_high_precision_independent_evaluation(self):
        r=self.result()
        weights=[mp.cos(mp.mpf('1.09'))**2,mp.sin(mp.mpf('1.09'))**2]
        with mp.workdps(80):
            b=mp.mpf('5.3')
            for i,mass in enumerate((550,900)):
                y=(mp.mpf(163)/mass)**2
                f=oracle(y)
                a=r['charged_scalars'][i]
                exp7=weights[i]*(f['F7_1']/(3*b*b)+f['F7_2'])
                exp8=weights[i]*(f['F8_1']/(3*b*b)+f['F8_2'])
                self.assertAlmostEqual(a['delta_C7'],float(exp7),delta=3e-14)
                self.assertAlmostEqual(a['delta_C8'],float(exp8),delta=3e-14)
                self.assertAlmostEqual(a['XY_conjugate_coupling'],a['doublet_fraction'])
                self.assertAlmostEqual(a['YY_coupling_squared']*b*b,a['doublet_fraction'])

    def test_degenerate_scalar_mixing_independence(self):
        baseline=self.result(mH1_GeV=550.,mH2_GeV=550.,gamma_rad=0.)
        for gamma in (0.3,1.09,math.pi/4,math.pi/2,math.pi):
            check=self.result(mH1_GeV=550.,mH2_GeV=550.,gamma_rad=gamma)
            for key in ('delta_C7_LO_at_matching_scale','delta_C8_LO_at_matching_scale'):
                self.assertAlmostEqual(check[key],baseline[key],delta=1e-14)

    def test_swap_invariance(self):
        base=self.result();swap=self.result(mH1_GeV=900,mH2_GeV=550,gamma_rad=math.pi/2-1.09)
        for key in ('delta_C7_LO_at_matching_scale','delta_C8_LO_at_matching_scale'):
            self.assertAlmostEqual(base[key],swap[key],delta=1e-14)

    def test_singlet_decoupling(self):
        baseline=self.result(gamma_rad=0.)
        after=self.result(gamma_rad=math.pi/2)
        self.assertAlmostEqual(baseline['charged_scalars'][0]['doublet_fraction'],1)
        self.assertAlmostEqual(after['charged_scalars'][1]['doublet_fraction'],1)
        self.assertAlmostEqual(after['charged_scalars'][0]['delta_C8'],0.,delta=1e-30)

    def test_large_mass_decoupling(self):
        a=self.result(mH1_GeV=1e4,mH2_GeV=2e4)
        b=self.result(mH1_GeV=1e6,mH2_GeV=2e6)
        self.assertLess(abs(b['delta_C7_LO_at_matching_scale']),abs(a['delta_C7_LO_at_matching_scale']))
        self.assertLess(abs(b['delta_C8_LO_at_matching_scale']),abs(a['delta_C8_LO_at_matching_scale']))

    def test_tanbeta_dependence_only_yy(self):
        low=self.result(beta_rad=math.atan(2))
        high=self.result(beta_rad=math.atan(20))
        for a,b in zip(low['charged_scalars'],high['charged_scalars']):
            self.assertAlmostEqual(a['delta_C7_XY'],b['delta_C7_XY'],delta=1e-15)
            self.assertAlmostEqual(a['delta_C8_XY'],b['delta_C8_XY'],delta=1e-15)
            self.assertAlmostEqual(a['delta_C7_YY']/b['delta_C7_YY'],100.,delta=1e-9)

    def test_fail_closed_physics_and_input_validation(self):
        r=self.result()
        self.assertEqual(r['status'],STATUS)
        self.assertEqual(r['experimental_comparison'],'NOT_EVALUATED')
        self.assertIsNone(r['global_zee_acceptance'])
        self.assertNotIn('partial_BR',str(r))
        for bad in (dict(mH1_GeV=-1),dict(mt_MSbar_GeV=0),
                    dict(beta_rad=0),dict(beta_rad=math.pi/2),
                    dict(gamma_rad=float('nan')),dict(mH2_GeV=float('inf')),
                    dict(matching_scale_GeV=0),dict(beta_rad=True)):
            with self.assertRaises(ValueError):self.result(**bad)

    def test_no_mutation_or_derived_mass_scheme(self):
        inputs={**self.common,**self.masses};old=copy.deepcopy(inputs)
        a=compute(**inputs)
        self.assertEqual(inputs,old)
        self.assertEqual(a['input']['mt_MSbar_GeV'],163.0)
        self.assertEqual(a['input']['matching_scale_GeV'],160.0)
        self.assertIn('NO_RUNNING',a['input']['top_mass_input_definition'])
        self.assertNotIn('BR_BtoXsGamma',a)
        self.assertNotIn('allowed',str(a).lower())

if __name__=='__main__':unittest.main()
