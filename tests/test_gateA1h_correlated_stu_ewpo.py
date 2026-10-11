"""Gate A1H validation: Grimus S,U integrals and correlated fit."""
import pathlib
import sys
import unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1h_correlated_stu_ewpo import (
    grimus_G,grimus_Ghat,florentino_mixing,stu_S_U,
    correlated_fit,report
)

class TestZeeSTU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=report()

    def test_G_closed_form_independent_C2_reference(self):
        # Grimus Appendix C2 evaluated at high-precision using its
        # closed log/arctan form (not this implementation's quadrature).
        actual=grimus_G(300**2,700**2,91.1876**2)
        self.assertAlmostEqual(actual,0.5322671520071151,delta=2e-10)

    def test_Ghat_asymptotic_C11(self):
        I=2000**2;Q=91.1876**2
        leading=np.log(I/Q)-5/3-8.5*Q/I
        self.assertAlmostEqual(grimus_Ghat(I,Q),leading,delta=0.002)

    def test_quadrature_convergence(self):
        x=stu_S_U(n=80)
        y=stu_S_U(n=200)
        self.assertAlmostEqual(x["S"],y["S"],delta=2e-9)
        self.assertAlmostEqual(x["U"],y["U"],delta=2e-9)

    def test_mixing_unitarity_and_h125_alignment(self):
        u,v=florentino_mixing()
        p=u.conj().T@u
        self.assertAlmostEqual(p[1,2].real,
                               -np.sin(1.089)*np.cos(1.089),places=12)
        self.assertAlmostEqual(abs((v.conj().T@v)[0,1].imag),
                               abs(np.cos(1.394-1.398)),places=12)
        self.assertAlmostEqual(self.data["loop_diagnostics"][
            "UV_mixing_closure_log_weight"],0.,places=12)

    def test_charged_degenerate_rotational_basis_independence(self):
        a=stu_S_U(m1=600,m2=600,gamma=0.25)
        b=stu_S_U(m1=600,m2=600,gamma=1.15)
        self.assertAlmostEqual(a["S"],b["S"],delta=2e-10)
        self.assertAlmostEqual(a["U"],b["U"],delta=2e-10)

    def test_independent_T_regression_and_vector(self):
        r=self.data["scalar_STU"]
        self.assertAlmostEqual(r["S"],0.0044404330206622,delta=2e-8)
        self.assertAlmostEqual(r["T"],-0.00490217831758,delta=1e-8)
        self.assertAlmostEqual(r["U"],0.00005733708113235,delta=2e-8)

    def test_covariance_positive_and_correlated_fit(self):
        for name,fit in self.data["correlated_fit_screens"].items():
            self.assertGreater(np.linalg.eigvalsh(fit["covariance_STU"]).min(),0)
            self.assertTrue(fit["inside_95percent_3D_gaussian_ellipsoid"])
        self.assertAlmostEqual(
            self.data["correlated_fit_screens"]["Gfitter_2026_U_floating"][
                "chi2_relative_to_fit_minimum"],0.8726172333965,delta=2e-5)
        self.assertAlmostEqual(
            self.data["correlated_fit_screens"]["PDG_2025_U_floating"][
                "chi2_relative_to_fit_minimum"],1.6726858974967,delta=2e-5)

    def test_not_global_Zee_validation(self):
        self.assertIn("NOT_GLOBAL",self.data["status"])
        self.assertGreaterEqual(len(self.data["not_checked"]),4)

if __name__=="__main__":
    unittest.main()
