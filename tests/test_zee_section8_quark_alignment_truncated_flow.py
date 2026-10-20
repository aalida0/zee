"""Truncated pure-2HDM one-loop flow controls; NOT complete Zee RGEs."""
import math
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_quark_alignment_truncated_flow import (
    STATUS,beta_all,beta_leptons,evolve,physical_offdiagonals,example
)
from zee_section8_quark_alignment_one_loop_gate import (
    higgs_to_symmetry_leptons,V
)

class TestTruncatedZeeQuarkFlow(unittest.TestCase):
    def test_flow_initial_typeII_quarks_has_no_neutral_fcnc(self):
        row=example(steps=20)
        self.assertLess(row["initial"]["down_max_abs_rho_offdiag"],1e-16)
        self.assertLess(row["initial"]["up_max_abs_rho_offdiag"],1e-15)
        self.assertTrue(row["truncated_pure_2HDM_only"])

    def test_generic_leptons_induce_nonzero_offdiagonals_in_toy(self):
        row=example(steps=60)
        self.assertGreater(row["final"]["down_max_abs_rho_offdiag"],1e-10)
        self.assertGreater(row["final"]["up_max_abs_rho_offdiag"],1e-12)
        self.assertLess(row["final"]["down_max_abs_rho_offdiag"],1e-5)
        self.assertIsNone(row["allowed_Zee_point"])
        self.assertFalse(row["full_Zee_f_coupled_RGE"])

    def test_typeII_leptons_control_preserves_quark_NFC(self):
        row=example(steps=80,typeii_leptons=True)
        self.assertLess(row["final"]["down_max_abs_rho_offdiag"],1e-13)
        self.assertLess(row["final"]["up_max_abs_rho_offdiag"],1e-13)
        self.assertTrue(row["typeII_leptons_control"])

    def test_rk4_step_halving_stability(self):
        a=example(steps=60)
        b=example(steps=120)
        self.assertAlmostEqual(
            a["final"]["down_max_abs_rho_offdiag"],
            b["final"]["down_max_abs_rho_offdiag"],
            delta=1e-10)
        self.assertAlmostEqual(
            a["final"]["up_max_abs_rho_offdiag"],
            b["final"]["up_max_abs_rho_offdiag"],
            delta=1e-11)

    def test_no_running_equals_initial(self):
        t=5.6
        z=np.zeros((3,3),complex)
        k=np.diag([.001,.002,.003])
        r=np.array([[0.,.004,0],[0.,0.,0.],[0.,0.,.001]])
        p1,p2=higgs_to_symmetry_leptons(k,r,t)
        Y=np.asarray([np.diag([.001,.005,.04]),z,z,
            np.diag([.001,.03,.9]),p1,p2],complex)
        result=evolve(Y,1000.,1000.*(1.-1e-12),steps=4)
        np.testing.assert_allclose(result,Y,rtol=1e-8,atol=1e-10)

    def test_lepton_beta_finite_and_not_misread_as_Zee_full(self):
        z=np.zeros((3,3),complex)
        E=np.eye(3,dtype=complex)
        beta=beta_leptons([E,z],[z,E],[E,.1*E],
                          g2=.65,gp=.36)
        self.assertEqual(len(beta),2)
        self.assertTrue(np.isfinite(beta).all())
        self.assertIn("NOT_PHYSICAL_FCNC_BOUND",STATUS)

if __name__=="__main__":
    unittest.main()
