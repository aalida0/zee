"""Literature-derived local quark-alignment regression, no SciPy required.

The toy examples cannot be used as Zee neutrino, LFV, or FCNC benchmarks.
Source: Ferreira-Lavoura-Silva, arXiv:1001.2561, Eqs.(3)-(4).
"""
import math
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_quark_alignment_one_loop_gate import (
    STATUS,beta_quarks_2hdm,higgs_to_symmetry_leptons,
    audit_quark_tangent,toy_example
)

class TestZeeQuarkAlignmentOneLoop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=np.random.default_rng(101)
        cls.G=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        cls.D=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        cls.P1=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        cls.P2=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))

    def test_generic_complex_lepton_trace_and_source_identities(self):
        a=audit_quark_tangent(self.G,self.D,self.P1,self.P2)
        t=np.trace(self.P2@self.P1.conj().T)
        self.assertAlmostEqual(a["T_real"],t.real)
        self.assertAlmostEqual(a["T_imag"],t.imag)
        self.assertLess(a["normalized_beta_Gamma2_error"],1e-13)
        self.assertLess(a["normalized_beta_Delta1_error"],1e-13)
        self.assertTrue(a["wrong_doublet_source_nonzero"])
        self.assertIsNone(a["fully_allowed_Zee"])

    def test_noncommuting_quark_generations_do_not_break_tangent_proportionality(self):
        self.assertGreater(np.linalg.norm(self.G@self.G.conj().T@self.D-
                             self.D@self.D.conj().T@self.G),1)
        a=audit_quark_tangent(self.G,self.D,self.P1,self.P2)
        self.assertLess(a["normalized_beta_Gamma2_error"],1e-13)
        self.assertLess(a["normalized_beta_Delta1_error"],1e-13)

    def test_orthogonal_leptons_remove_local_wrong_doublet_source(self):
        a=np.diag([.001,.002,.003])
        b=np.array([[0.,.005,0.],[0.,0.,.002],[0.,0.,0.]],complex)
        r=audit_quark_tangent(self.G,self.D,a,b)
        self.assertLess(r["beta_Gamma2_frobenius"],1e-12)
        self.assertLess(r["beta_Delta1_frobenius"],1e-12)
        self.assertFalse(r["wrong_doublet_source_nonzero"])
        self.assertFalse(r["TypeII_texture_RG_invariant_for_generic_leptons"])

    def test_typeII_leptons_give_exact_zero_trace(self):
        t=5.6
        k=np.diag([.001,.002,.003])
        a,b=higgs_to_symmetry_leptons(k,-t*k,t)
        self.assertLess(np.linalg.norm(b),1e-14)
        r=audit_quark_tangent(self.G,self.D,a,b)
        self.assertLess(r["beta_Gamma2_frobenius"],1e-13)

    def test_weak_lepton_basis_trace_invariance(self):
        qL,_=np.linalg.qr(self.G)
        qR,_=np.linalg.qr(self.D)
        r1=audit_quark_tangent(self.G,self.D,self.P1,self.P2)
        r2=audit_quark_tangent(
            self.G,self.D,
            qL.conj().T@self.P1@qR,
            qL.conj().T@self.P2@qR)
        self.assertAlmostEqual(r1["T_real"],r2["T_real"],places=11)
        self.assertAlmostEqual(r1["T_imag"],r2["T_imag"],places=11)

    def test_higgs_rotation_inverse(self):
        t=7.
        p1,p2=higgs_to_symmetry_leptons(self.P1,self.P2,t)
        c=1/math.hypot(1,t);s=t*c
        np.testing.assert_allclose(c*p1+s*p2,self.P1,atol=1e-14)
        np.testing.assert_allclose(-s*p1+c*p2,self.P2,atol=1e-14)

    def test_gauge_terms_do_not_affect_wrong_doublet_boundary_source(self):
        z=np.zeros((3,3),complex)
        T=np.trace(self.P2@self.P1.conj().T)
        for g in ((0.,0.,0.),(1.2,.65,.36)):
            bg,bd=beta_quarks_2hdm(
                (self.G,z),(z,self.D),(self.P1,self.P2),
                g3=g[0],g2=g[1],gp=g[2])
            np.testing.assert_allclose(bg[1],T*self.G,rtol=2e-14,atol=2e-14)
            np.testing.assert_allclose(bd[0],T*self.D,rtol=2e-14,atol=2e-14)

    def test_no_phenomenological_allowed_claim(self):
        r=toy_example(5.6)
        self.assertIn("NOT_FCNC_ALLOWED",STATUS)
        self.assertFalse(r["quark_FCNC_limits_completed"])
        self.assertFalse(r["finite_running_completed"])
        self.assertFalse(r["neutrino_LFV_fit_completed"])
        self.assertTrue(r["toy_lepton_matrices_NOT_a_flavor_fit"])
        self.assertIsNone(r["fully_allowed_Zee"])

if __name__=="__main__":
    unittest.main()
