"""Synthetic source-limit regression for generated Zee functions; no physical acceptance."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from zee_section8_Q4_generated_source_limit_probe import (
    arg_map,deviation,evaluate,run_checks,KNOWN_COUPLINGS)
from zee_section8_quark_alignment_one_loop_gate import beta_quarks_2hdm

def fake_beta_module():
    """Independent toy functions with FLS quarks and Kanemura-reduced real f."""
    def beta_gp(nLoop,gp):return 22./3*gp**3
    def beta_g2(nLoop,g2):return -3*g2**3
    def beta_g3(nLoop,g3):return -7*g3**3
    def beta_f(nLoop,f,gp,g2):
        a=np.asarray(f,dtype=complex)
        q=np.sum(np.triu(a,1)**2)
        return (-(1.5*gp**2+4.5*g2**2)+8*q)*a-4*a@a@a
    def fls(which,Yd1,Yd2,Yu1,Yu2,Ye1,Ye2,gp,g2,g3):
        bg,bu=beta_quarks_2hdm(
            (np.asarray(Yd1),np.asarray(Yd2)),
            (np.asarray(Yu1),np.asarray(Yu2)),
            (np.asarray(Ye1),np.asarray(Ye2)),gp=gp,g2=g2,g3=g3)
        return {'Yd1':bg[0],'Yd2':bg[1],'Yu1':bu[0],'Yu2':bu[1]}[which]
    def beta_Yd1(nLoop,Yd1,Yd2,Yu1,Yu2,Ye1,Ye2,gp,g2,g3):
        return fls('Yd1',Yd1,Yd2,Yu1,Yu2,Ye1,Ye2,gp,g2,g3)
    def beta_Yd2(nLoop,Yd1,Yd2,Yu1,Yu2,Ye1,Ye2,gp,g2,g3):
        return fls('Yd2',Yd1,Yd2,Yu1,Yu2,Ye1,Ye2,gp,g2,g3)
    def beta_Yu1(nLoop,Yd1,Yd2,Yu1,Yu2,Ye1,Ye2,gp,g2,g3):
        return fls('Yu1',Yd1,Yd2,Yu1,Yu2,Ye1,Ye2,gp,g2,g3)
    def beta_Yu2(nLoop,Yd1,Yd2,Yu1,Yu2,Ye1,Ye2,gp,g2,g3):
        return fls('Yu2',Yd1,Yd2,Yu1,Yu2,Ye1,Ye2,gp,g2,g3)
    return SimpleNamespace(**{name:func for name,func in locals().items()
             if name.startswith('beta_')})

class TestGeneratedSourceLimits(unittest.TestCase):
    def test_positive_reference_probe(self):
        result=run_checks(fake_beta_module())
        self.assertEqual(len(result),11)
        self.assertTrue(all(x['pass'] for x in result.values()),result)
    def test_wrong_gauge_factor_is_detected(self):
        mod=fake_beta_module()
        mod.beta_gp=lambda nLoop,gp:22./3*(5./3)*gp**3
        r=run_checks(mod)
        self.assertFalse(r['gauge_gp']['pass'])
    def test_wrong_antisymmetric_f_factor_is_detected(self):
        mod=fake_beta_module()
        old=mod.beta_f
        mod.beta_f=lambda nLoop,f,gp,g2:2*old(nLoop,f,gp,g2)
        r=run_checks(mod)
        self.assertFalse(r['Kanemura_A13_restricted_real_f']['pass'])
    def test_complex_f_preserved_in_positive_reference(self):
        r=run_checks(fake_beta_module())
        self.assertTrue(r['complex_f_beta_antisymmetry']['pass'])
    def test_f_zero_is_fixed_point(self):
        r=run_checks(fake_beta_module())
        self.assertTrue(r['f_zero_is_fixed_point']['pass'])
    def test_bad_parameter_name_rejected(self):
        mod=fake_beta_module()
        mod.beta_gp=lambda nLoop,alien_coupling:0
        with self.assertRaisesRegex(ValueError,'Unmapped parameters'):
            evaluate(mod,'gp',arg_map())
    def test_missing_function_rejected(self):
        mod=fake_beta_module();delattr(mod,'beta_f')
        with self.assertRaisesRegex(ValueError,'beta_f is missing'):
            evaluate(mod,'f',arg_map())
    def test_matrix_shape_mismatch_detected(self):
        d=deviation(np.zeros((3,3)),np.zeros((2,2)))
        self.assertFalse(d['pass'])
    def test_no_unrecognized_couplings_in_test_input(self):
        kw=arg_map()
        self.assertEqual(set(kw),KNOWN_COUPLINGS)
        self.assertEqual(np.shape(kw['f']),(3,3))
        self.assertEqual(np.shape(kw['Ye2']),(3,3))

if __name__=='__main__':unittest.main()
