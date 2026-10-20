"""Q4v12 independent general Weyl one-loop complex Zee Yukawa test suite.

Independent source: Schienbein et al., NPB939 (2019), Eq. 5.11;
physical source limits: Kanemura 2001 A13, FLS 2010 Eq.5.
Mocks only exercise comparator machinery; real AF generated RGEs checked later.
"""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_independent_complex_weyl_yukawas import (
    zeros,independent_weyl_tensors,universal_weyl_beta,
    extracted_lepton_betas,independent_betas,numeric_case,mixed_quark_case,
)
from zee_section8_Q4_independent_f_quartic_gate import synthetic_f
from zee_section8_Q4_independent_yukawa_quartic_gate import synthetic_yukawas
from zee_section8_Q4_complex_lepton_scalar_covariance_gate import (
    independent_fls_lepton,
)

def fake_generator(f_scale=1.,ye_increment_scale=1.):
    # The independent formula is used as a FAKE generator fixture here;
    # this is a software comparator test, NOT independent physics evidence.
    def calculate(Ye1,Ye2,f,gp,g2):
        yy=zeros()
        yy['Ye1']=np.asarray(Ye1,complex)
        yy['Ye2']=np.asarray(Ye2,complex)
        beta,_=independent_betas(yy,np.asarray(f,complex),gp=gp,g2=g2)
        atzero,_=independent_betas(
            yy,np.zeros((3,3),complex),gp=gp,g2=g2)
        return {
            'f':f_scale*beta['f'],
            'Ye1':atzero['Ye1']+
                  ye_increment_scale*(beta['Ye1']-atzero['Ye1']),
            'Ye2':atzero['Ye2']+
                  ye_increment_scale*(beta['Ye2']-atzero['Ye2'])
        }
    def beta_f(nLoop,Ye1,Ye2,f,gp,g2):
        return calculate(Ye1,Ye2,f,gp,g2)['f']
    def beta_Ye1(nLoop,Ye1,Ye2,f,gp,g2):
        return calculate(Ye1,Ye2,f,gp,g2)['Ye1']
    def beta_Ye2(nLoop,Ye1,Ye2,f,gp,g2):
        return calculate(Ye1,Ye2,f,gp,g2)['Ye2']
    return SimpleNamespace(beta_f=beta_f,beta_Ye1=beta_Ye1,beta_Ye2=beta_Ye2)

class TestQ4IndependentComplexWeyl(unittest.TestCase):
    def setUp(self):
        self.yy=zeros()
        more=synthetic_yukawas(20261019)
        self.yy['Ye1']=more['Ye1']
        self.yy['Ye2']=more['Ye2']
        self.f=synthetic_f(20261019)

    def test_ten_real_scalar_weyl_tensors_symmetric(self):
        T=independent_weyl_tensors(
            self.yy['Ye1'],self.yy['Ye2'],self.f)
        self.assertEqual(T.shape,(10,9,9))
        np.testing.assert_allclose(T,T.transpose(0,2,1),atol=1e-14)

    def test_generic_symmetric_weyl_one_loop_tensors(self):
        T=independent_weyl_tensors(
            self.yy['Ye1'],self.yy['Ye2'],self.f)
        BT=universal_weyl_beta(T)
        self.assertEqual(BT.shape,(10,9,9))
        np.testing.assert_allclose(BT,BT.transpose(0,2,1),atol=1e-13)

    def test_wrong_shape_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'symmetric square'):
            universal_weyl_beta(np.ones((10,9,8)))

    def test_nonsymmetric_input_fails_closed(self):
        T=independent_weyl_tensors(
            self.yy['Ye1'],self.yy['Ye2'],self.f)
        T[0,0,6]+=.5
        with self.assertRaisesRegex(ValueError,'symmetric'):
            universal_weyl_beta(T)

    def test_projection_many_components_agree(self):
        T=independent_weyl_tensors(
            self.yy['Ye1'],self.yy['Ye2'],self.f)
        bet,projection=extracted_lepton_betas(universal_weyl_beta(T))
        self.assertEqual(set(bet),{'f','Ye1','Ye2'})
        self.assertLess(max(projection.values()),1e-12)
        self.assertLess(np.max(abs(bet['f']+bet['f'].T)),1e-12)

    def test_fls_lepton_f_zero_with_nondiagonal_complex_matrices(self):
        ref=independent_fls_lepton(self.yy,0.,0.)
        out,_=independent_betas(self.yy,np.zeros((3,3)),gp=0.,g2=0.)
        for k in ('Ye1','Ye2'):
            self.assertLess(np.max(abs(out[k]-ref[k])),1e-12)

    def test_fls_lepton_f_zero_with_gauge_terms(self):
        ref=independent_fls_lepton(self.yy,.36,.65)
        out,_=independent_betas(self.yy,np.zeros((3,3)),gp=.36,g2=.65)
        for k in ('Ye1','Ye2'):
            self.assertLess(np.max(abs(out[k]-ref[k])),1e-12)

    def test_Kanemura_f_real_cubic_only(self):
        f=np.zeros((3,3),float)
        f[0,1]=.12;f[0,2]=-.07;f[1,2]=.04
        f=f-f.T
        q=float(np.sum(np.triu(f,1)**2))
        out,_=independent_betas(zeros(),f,gp=0.,g2=0.)
        np.testing.assert_allclose(out['f'],12*q*f,atol=1e-12)
        np.testing.assert_allclose(out['Ye1'],np.zeros((3,3)),atol=1e-14)

    def test_Kanemura_f_real_with_gauge(self):
        f=np.zeros((3,3),float)
        f[0,1]=.12;f[0,2]=-.07;f[1,2]=.04
        f=f-f.T
        q=float(np.sum(np.triu(f,1)**2))
        out,_=independent_betas(zeros(),f,gp=.36,g2=.65)
        np.testing.assert_allclose(out['f'],
             (12*q-1.5*.36**2-4.5*.65**2)*f,atol=1e-12)

    def test_complex_f_antisymmetry_and_phase_covariance(self):
        a,_=independent_betas(self.yy,self.f,gp=.36,g2=.65)
        b,_=independent_betas(self.yy,np.exp(.72j)*self.f,gp=.36,g2=.65)
        np.testing.assert_allclose(a['f'],np.exp(.72j)*b['f']*
                                   np.exp(-1.44j),atol=1e-12)
        # Equivalent b_f=phase*a_f; Ye f-wave feedback invariant.
        np.testing.assert_allclose(b['f'],np.exp(.72j)*a['f'],atol=1e-12)
        for k in ('Ye1','Ye2'):
            np.testing.assert_allclose(a[k],b[k],atol=1e-12)

    def test_f_lepton_feedback_nonzero_for_generic_point(self):
        a,_=independent_betas(self.yy,self.f,gp=.36,g2=.65)
        b,_=independent_betas(self.yy,np.zeros((3,3)),gp=.36,g2=.65)
        for k in ('Ye1','Ye2'):
            self.assertGreater(np.max(abs(a[k]-b[k])),1e-9)

    def test_gauge_casimir_terms_are_expected(self):
        g,_=independent_betas(self.yy,self.f,gp=.36,g2=.65)
        z,_=independent_betas(self.yy,self.f,gp=0.,g2=0.)
        np.testing.assert_allclose(
            g['f']-z['f'],(-1.5*.36**2-4.5*.65**2)*self.f,atol=1e-12)
        for k in ('Ye1','Ye2'):
            np.testing.assert_allclose(
                g[k]-z[k],(-3.75*.36**2-2.25*.65**2)*self.yy[k],atol=1e-12)

    def test_positive_fake_generator_matches_direct(self):
        out=numeric_case(fake_generator(),self.yy,self.f)
        self.assertTrue(all(v['pass'] for k in ('direct','f_increments')
                            for v in out[k].values()),out)

    def test_wrong_f_normalization_is_detected(self):
        out=numeric_case(fake_generator(f_scale=2.),self.yy,self.f)
        self.assertFalse(out['direct']['f']['pass'])

    def test_wrong_Ye_f_feedback_is_detected(self):
        out=numeric_case(fake_generator(ye_increment_scale=2.),self.yy,self.f)
        self.assertFalse(out['direct']['Ye1']['pass'])
        self.assertFalse(out['f_increments']['f_increment_Ye2']['pass'])

    def test_quark_independent_f_increment_comparison(self):
        yy=synthetic_yukawas(20261020)
        out=mixed_quark_case(fake_generator(),yy,synthetic_f(20261020))
        self.assertEqual(len(out),3)
        self.assertTrue(all(v['pass'] for v in out.values()),out)

    def test_wrong_quark_environment_f_coupling_is_detected(self):
        yy=synthetic_yukawas(20261020)
        mod=fake_generator()
        old=mod.beta_f
        def bad_beta_f(nLoop,Ye1,Ye2,f,gp,g2,Yu1):
            return old(nLoop,Ye1,Ye2,f,gp,g2)+.04*Yu1
        mod.beta_f=bad_beta_f
        out=mixed_quark_case(mod,yy,synthetic_f(20261020))
        self.assertFalse(out['full_f_beta_no_quark_direct_term']['pass'])

if __name__=='__main__':
    unittest.main()
