"""Bounded reference-comparison tests; a known source/paper failure is retained."""
import copy
import json
import os
from pathlib import Path
import sys
import unittest
import numpy as np
try:
    from .external_2hdm import PIN, capture, load_reference, run, strict_input, example_input
except ImportError:
    from external_2hdm import PIN, capture, load_reference, run, strict_input, example_input

ROOT=Path(os.environ.get('D16_REPO_ROOT',Path(__file__).resolve().parents[2]))
REFERENCE=ROOT/'research/wgamma_d16/local/general-2hdm-pheno'


def vector(value):
    a=np.array(value);return a[:,0]+1j*a[:,1]


class ExternalComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=run(ROOT,REFERENCE)
        cls.ref=load_reference(REFERENCE)

    def test_full_restricted_and_generic_failure_are_distinct(self):
        self.assertEqual(self.result['author_SHA'],PIN)
        records=self.result['records']
        self.assertEqual(len(records),12)
        self.assertEqual([r['full_published_comparison'] for r in records],['FAIL_HW']*6+['PASS']*6)
        for r in records:
            total=vector(r['author_c_LR'])
            self.assertTrue(np.all(abs(total.imag)>1e-9))
            self.assertTrue(np.all(abs(vector(r['groups_c_LR']['kin']))>1e-10))
            self.assertTrue(np.all(abs(vector(r['groups_c_LR']['tHp']))>1e-10))
            for key,res in r['group_max_relative_residual'].items():
                if key!='HW':self.assertLess(res,3e-11)

    def test_frozen_photon_quadratures_and_recorded_one_loop_difference(self):
        for r in self.result['records']:
            for a,b in [('photon_frozen','photon_author'),('scalar_photon_frozen','scalar_photon_author')]:
                np.testing.assert_allclose(vector(r[a]),vector(r[b]),rtol=3e-10,atol=1e-23)
        # Never mislabel the differently truncated frozen one-loop answer exact.
        self.assertGreater(max(abs(vector(self.result['records'][0]['one_loop_difference']))),1e-15)

    def test_complex_rephasing_and_index_orientation(self):
        x=copy.deepcopy(self.result['records'][0]['author_input'])
        original,_=capture(self.ref.thdm(x),2,1)
        phase=np.array([.37,-.81,.22])
        for i in range(3):
            for j in range(3):x[f'argrhol{i+1}{j+1}']+=phase[j]-phase[i]
        rotated,_=capture(self.ref.thdm(x),2,1)
        np.testing.assert_allclose(rotated,original*np.exp(1j*(phase[1]-phase[0])),rtol=2e-12,atol=1e-17)
        self.assertGreater(max(abs(rotated-original)),1e-4)

    def test_hw_dimensional_falsifier(self):
        for r in self.result['records'][:6]:
            mw=r['author_input']['MW']
            np.testing.assert_allclose(vector(r['published_HW_c_LR']),
                mw*mw*vector(r['groups_c_LR']['HW']),rtol=3e-11,atol=1e-19)
        checks=self.result['checks']
        np.testing.assert_allclose(vector(checks['HW_code_rescaling_c_at_doubled_mass']),
            vector(checks['HW_original'])/4,rtol=2e-13,atol=1e-22)

    def test_strict_limit_rejects_singlet_interactions(self):
        p=dict(self.result['records'][0]['physical'])
        x=self.result['records'][0]['author_input'];ml=[x[k] for k in ('melectron','mmuon','mtau')]
        for key in ('gamma','k1','k2','k12'):
            changed=dict(p);changed[key]=.01
            with self.assertRaises(ValueError):
                strict_input(self.ref,example_input(REFERENCE),changed,np.zeros((3,3),complex),ml)
        self.assertEqual(self.result['checks']['null_all_groups'],'PASS')
        self.assertEqual(self.result['checks']['removed_singlet_mass_independence'],'PASS')
        self.assertGreater(self.result['checks']['charged_mass_dependence_kin'],1e-12)

    def test_physical_zee_w_gate_remains_closed(self):
        self.assertEqual(self.result['physical_Zee_W'],dict(C_L=None,C_R=None,coherent_inclusion=False))
        from research.wgamma_d16.matching import example,evaluate
        r=evaluate(example())
        self.assertIsNone(r['C_L']);self.assertIsNone(r['C_R'])
        self.assertFalse(r['coherent_inclusion'])


if __name__=='__main__':unittest.main()
