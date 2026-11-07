"""Physical h125 release checks; historical routing tests remain separate."""
import itertools
import json
import math
import unittest

import numpy as np

from research.full_constraints.higgs import zgamma as z
from research.full_constraints.higgs.zgamma_source_audit import HERE,ROOT,sha


class ZgammaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e=json.loads((HERE/'ZGAMMA_H125_EVIDENCE.json').read_text())

    def test_sources_and_fixed_cards(self):
        for path,digest in self.e['source_pins'].items():self.assertEqual(sha(ROOT/path),digest,path)
        for path,digest in self.e['independent_reference']['source_hashes'].items():self.assertEqual(sha(path),digest)
        for case in self.e['cases']:
            r=z.benchmark(case['name'])
            self.assertEqual(r['scalar_sha256'],case['scalar_sha256'])
            self.assertEqual(r['yukawa_sha256'],case['yukawa_sha256'])
            self.assertAlmostEqual(r['full']['width_GeV']/case['full']['width_GeV'],1,places=12)

    def test_independently_executed_SM_and_one_scalar_interference(self):
        self.assertLess(abs(self.e['SM_reference_relative_residual']),2e-12)
        self.assertLess(self.e['W_Hue20_relative_residual'],2e-12)
        for row in self.e['one_scalar_controls']:
            self.assertLess(abs(row['width_relative_residual']),2e-12)
            self.assertLess(abs(row['X']['real']-row['native_Fontes_C10_X']['real']),1e-11)
            self.assertLess(abs(row['X']['real']-row['HEPfit_mapped_X']['real']),1e-10)
        for a,b in zip(self.e['one_scalar_controls'][::2],self.e['one_scalar_controls'][1::2]):
            self.assertLess(a['calculated_width_GeV'],b['calculated_width_GeV'])

    def test_native_absorptive_fermion_and_CP_tensors(self):
        for f,row in self.e['native_equal_mass_comparisons'].items():
            self.assertLess(row['C0_relative_residual'],1e-10)
            self.assertLess(row['K_relative_residual'],1e-10)
            if f not in ('W','t'):self.assertNotEqual(row['C0']['imag'],0)
        for row in self.e['native_fermion_tensor_comparisons'].values():
            self.assertLess(row['even_residual'],1e-11)
            self.assertLess(row['odd_residual'],1e-11)

    def test_chiral_vector_sum_and_native_yukawa_conjugation(self):
        k={f:0 for f in z.MASSES if f!='W'};k['tau']=.4+.7j
        a=z.amplitude(125,0,k);b=z.amplitude(125,0,{f:complex(x).conjugate() for f,x in k.items()})
        self.assertAlmostEqual(a['even'],b['even']);self.assertAlmostEqual(a['odd'],-b['odd'])
        self.assertAlmostEqual(a['width_GeV'],b['width_GeV'])
        sw2=1-(80.379/91.1876)**2
        for row in a['chiral_currents'].values():
            expected=(row['T3']-2*row['Q']*sw2)/math.sqrt(sw2*(1-sw2))
            self.assertAlmostEqual(row['gL_over_e']+row['gR_over_e'],expected)
            self.assertAlmostEqual(row['gL_over_e']-row['gR_over_e'],row['T3']/math.sqrt(sw2*(1-sw2)))

    def test_unpolarized_CP_noninterference_and_width_prefactor(self):
        mh=125.;mz=91.1876;p=(mh*mh-mz*mz)/(2*mh);ez=(mh*mh+mz*mz)/(2*mh)
        q=np.array([p,0,0,p]);r=np.array([ez,0,0,-p]);metric=np.diag([1,-1,-1,-1]);dot=q@metric@r
        tensor=dot*metric-np.outer(r,q)
        eps=np.zeros((4,4,4,4))
        for perm in itertools.permutations(range(4)):
            inversions=sum(perm[i]>perm[j] for i in range(4) for j in range(i+1,4))
            eps[perm]=(-1)**inversions
        odd=np.einsum('mnab,a,b->mn',eps,metric@q,metric@r)
        photon=[np.array([0,1,0,0]),np.array([0,0,1,0])]
        zv=photon+[np.array([p/mz,0,0,-ez/mz])]
        even_vals=[];odd_vals=[]
        for a in photon:
            for b in zv:
                even_vals.append((metric@a)@tensor@(metric@b))
                odd_vals.append((metric@a)@odd@(metric@b))
        self.assertAlmostEqual(np.dot(even_vals,odd_vals),0)
        self.assertAlmostEqual(np.dot(even_vals,even_vals)/(2*dot*dot),1)
        self.assertAlmostEqual(np.dot(odd_vals,odd_vals)/(2*dot*dot),1)
        sm=self.e['SM_all_nine'];pref=p/(8*math.pi*mh**2)*2*dot**2*(sm['alpha_em']/(2*math.pi*246.21965))**2
        self.assertAlmostEqual(pref/sm['prefactor_GeV'],1)

    def test_signed_interference_is_material(self):
        for row in self.e['cases']:
            c=row['component_sums'];w=complex(c['W']['real'],c['W']['imag'])
            f=complex(c['fermions']['real'],c['fermions']['imag']);s=c['scalars']['real']
            self.assertLess(row['even_pair_interference_norm']['W_fermions'],0)
            self.assertLess(row['even_pair_interference_norm']['W_scalars'],0)
            self.assertGreater(abs(abs(w-f+s)**2/abs(w+f+s)**2-1),.2)
            self.assertGreater(abs(abs(w+f-s)**2/abs(w+f+s)**2-1),.02)

    def test_scalar_routing_and_quadrature_preserved(self):
        for row in self.e['cases']:
            self.assertLess(row['scalar_routing_preserved_absolute_residual'],1e-11)
            self.assertLess(row['quadrature_width_relative_residual_80_to_120'],1e-12)
            self.assertGreater(row['W_threshold_gap_GeV'],0)
            self.assertGreater(min(row['scalar_threshold_gaps_GeV']),0)

    def test_strict_domains_and_no_global_release(self):
        k={f:1 for f in z.MASSES if f!='W'}
        for mh in (90,400):
            with self.assertRaises(ValueError):z.amplitude(mh,1,k)
        with self.assertRaises(ValueError):z.scalar_terms(125,91,246,.3,[50],[[1]],[[1]])
        with self.assertRaises(ValueError):z.scalar_terms(125,91,246,.3,[-300],[[1]],[[1]])
        with self.assertRaises(ValueError):z.scalar_terms(125,91,246,.3,[300],[[1j]],[[1]])
        self.assertIsNone(self.e['global_acceptance']);self.assertIsNone(self.e['theory_sigma'])
        self.assertFalse(self.e['H_A_extension_executed']);self.assertEqual(self.e['scans_executed'],0)
        self.assertEqual(self.e['Higgs'],'HIGGS_FULL_COVERAGE_BLOCKED')


if __name__=='__main__':unittest.main(verbosity=2)
