"""Q4v11 independent scalar-only dimensionful RGE Hessian regression tests.

These are synthetic analytic/software tests; AF PyR@TE comparison is separate.
"""
from pathlib import Path
import sys
import unittest
import numpy as np
from types import SimpleNamespace

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_Q4_independent_dimensional_scalar_gate import (
    BASIS_NAMES, DIMENSIONFUL_NAMES,
    potential_quadratic,potential_cubic,quadratic_hessian,cubic_tensor,
    cubic_hessian,degree2_and3_counterterms,projected_bases,
    independent_dimensionful_scalar_beta,compare_generator,
)
from zee_section8_Q4_independent_scalar_hessian_gate import (
    potential,tensor_for_quartics,synthetic_quartics,
)

class TestQ4IndependentDimensionalScalar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=np.random.default_rng(20261019)
        cls.fields=rng.normal(size=(128,10))
        cls.basis=projected_bases(cls.fields)

    def test_independent_basis_is_rank7(self):
        quadratic,cubic,condition=self.basis
        self.assertEqual(len(BASIS_NAMES),7)
        self.assertEqual(quadratic.shape,(128,5))
        self.assertEqual(cubic.shape,(128,2))
        self.assertLess(condition["quadratic"],1e5)
        self.assertLess(condition["cubic"],1e5)

    def test_quadratic_mass_hessian_finite_differences(self):
        masses={"m1":81000.,"m2":252000.,"mchi":129000.,
                "m12":26000.+8000j}
        r=self.fields[3];h=.05;I=np.eye(10)
        exact=quadratic_hessian(masses)
        for i,j in ((0,0),(0,4),(1,5),(2,7),(8,9)):
            fd=(potential_quadratic(r+h*I[i]+h*I[j],masses)
                -potential_quadratic(r+h*I[i]-h*I[j],masses)
                -potential_quadratic(r-h*I[i]+h*I[j],masses)
                +potential_quadratic(r-h*I[i]-h*I[j],masses))/(4*h*h)
            self.assertAlmostEqual(exact[i,j],fd,delta=2e-5)

    def test_cubic_hessian_finite_differences(self):
        r=self.fields[7];mu=220.+55j
        exact=cubic_hessian(r,mu)
        h=.05;I=np.eye(10)
        for i,j in ((0,4),(0,6),(0,8),(4,9),(2,7),(3,6)):
            fd=(potential_cubic(r+h*I[i]+h*I[j],mu)
                -potential_cubic(r+h*I[i]-h*I[j],mu)
                -potential_cubic(r-h*I[i]+h*I[j],mu)
                +potential_cubic(r-h*I[i]-h*I[j],mu))/(4*h*h)
            self.assertAlmostEqual(exact[i,j],fd,delta=1e-8)

    def test_cubic_hessian_symmetric(self):
        t=cubic_tensor(220.+55j)
        self.assertEqual(t.shape,(10,10,10))
        np.testing.assert_allclose(t,t.transpose((1,0,2)))
        np.testing.assert_allclose(t,t.transpose((2,1,0)))
        for r in self.fields[:4]:
            np.testing.assert_allclose(cubic_hessian(r,220.+55j),
                                       cubic_hessian(r,220.+55j).T)

    def test_analytic_one_doublet_mass_beta_6_lambda_mass(self):
        lam=.41;m=81000.
        out,info=independent_dimensionful_scalar_beta(
            {"l1":lam},{"m1":m},0.,self.fields,self.basis)
        self.assertAlmostEqual(out["m1"],6*lam*m,delta=1e-7)
        for k in DIMENSIONFUL_NAMES:
            if k!="m1":self.assertLess(abs(out[k]),1e-7)
        self.assertLess(info["quadratic_residual"],1e-12)

    def test_analytic_complex_singlet_mass_beta_8_lambda_mass(self):
        lam=.31;m=129000.
        out,info=independent_dimensionful_scalar_beta(
            {"lh":lam},{"mchi":m},0.,self.fields,self.basis)
        self.assertAlmostEqual(out["mchi"],8*lam*m,delta=1e-7)
        for k in DIMENSIONFUL_NAMES:
            if k!="mchi":self.assertLess(abs(out[k]),1e-7)

    def test_pure_zee_mu_loop_induces_quadratic_masses(self):
        out,info=independent_dimensionful_scalar_beta(
            {},{},220.+55j,self.fields,self.basis)
        self.assertGreater(out["m1"],0.)
        self.assertAlmostEqual(out["m1"],out["m2"],delta=1e-9)
        self.assertAlmostEqual(out["mchi"],2*out["m1"],delta=1e-9)
        self.assertLess(abs(out["m12"]),1e-9)
        self.assertLess(abs(out["muZee"]),1e-9)

    def test_scaling_zee_mu_squared_vs_trilinear_mu(self):
        quartics=synthetic_quartics(20261020)
        mu=220.+55j
        a,_=independent_dimensionful_scalar_beta(quartics,{},mu,
                                                  self.fields,self.basis)
        bb,_=independent_dimensionful_scalar_beta(quartics,{},2*mu,
                                                   self.fields,self.basis)
        for k in ("m1","m2","m12","mchi"):
            self.assertLess(abs(bb[k]-4*a[k]),1e-7)
        self.assertLess(abs(bb["muZee"]-2*a["muZee"]),1e-9)

    def test_hessian_degree2_and3_polynomial_closure(self):
        quartics=synthetic_quartics(20261020)
        masses={"m1":81000.,"m2":252000.,"mchi":129000.,
                "m12":26000.+8000j}
        out,info=independent_dimensionful_scalar_beta(
            quartics,masses,220.+55j,self.fields,self.basis)
        self.assertLess(info["quadratic_residual"],1e-12)
        self.assertLess(info["cubic_residual"],1e-12)
        self.assertEqual(set(out),set(DIMENSIONFUL_NAMES))
        self.assertTrue(all(np.isfinite(abs(x)) for x in out.values()))

    def test_potential_rephasing_invariance(self):
        r=np.array(self.fields[3],copy=True)
        theta=.43;psi=-.76
        h2=(r[4:8:2]+1j*r[5:8:2])/np.sqrt(2)
        chi=(r[8]+1j*r[9])/np.sqrt(2)
        h2rot=np.exp(1j*theta)*h2
        chirot=np.exp(1j*psi)*chi
        s=r.copy()
        for j in (0,1):
            s[4+2*j]=np.sqrt(2)*h2rot[j].real
            s[5+2*j]=np.sqrt(2)*h2rot[j].imag
        s[8]=np.sqrt(2)*chirot.real
        s[9]=np.sqrt(2)*chirot.imag
        mass={"m1":81000.,"m2":252000.,"mchi":129000.,
              "m12":26000.+8000j}
        mu=220.+55j
        q=synthetic_quartics(20261020)
        before=potential_quadratic(r,mass)+potential_cubic(r,mu)+potential(
            r,tensor_for_quartics(q))
        mr={**mass,"m12":np.exp(-1j*theta)*mass["m12"]}
        qr={**q}
        qr["l5"]*=np.exp(-2j*theta)
        for name in ("l6","l7","l10"):
            qr[name]*=np.exp(-1j*theta)
        after=potential_quadratic(s,mr)+potential_cubic(
            s,mu*np.exp(1j*(-theta+psi)))+potential(
            s,tensor_for_quartics(qr))
        self.assertAlmostEqual(after,before,delta=1e-8)

    def test_cubic_beta_vanishes_when_mu_zero(self):
        quartics=synthetic_quartics(20261020)
        masses={"m1":81000.,"m2":252000.,"mchi":129000.,
                "m12":26000.+8000j}
        out,_=independent_dimensionful_scalar_beta(
            quartics,masses,0.,self.fields,self.basis)
        self.assertLess(abs(out["muZee"]),1e-10)

    def test_invalid_design_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"singular"):
            projected_bases(np.zeros((15,10),float))

    def test_mock_beta_matches_and_mismatch_detected(self):
        q={"l1":.41};m={"m1":81000.};mu=0.
        expected,_=independent_dimensionful_scalar_beta(
            q,m,mu,self.fields,self.basis)
        funcs={}
        for name,v in expected.items():
            def make(value):
                def beta(nLoop,m1):
                    return value if abs(m1)>0 else 0.
                return beta
            funcs["beta_"+name]=make(v)
        mod=SimpleNamespace(**funcs)
        got=compare_generator(mod,q,m,mu,expected)
        self.assertTrue(all(x["pass"] for x in got.values()),got)
        mod.beta_m1=lambda nLoop,m1:2*expected["m1"] if m1 else 0.
        bad=compare_generator(mod,q,m,mu,expected)
        self.assertFalse(bad["m1"]["pass"])

if __name__=="__main__":
    unittest.main()
