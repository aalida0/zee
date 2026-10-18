"""Single-command integrated Q2 audit runner regression, with synthetic B2 data.

No physical Zee benchmark or constraints accepted by this test.
"""
import math
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,scalar_kappa
)
from zee_section8_run_integrated_Q2_validation import (
    STATUS,quark_boundary,check_matched_finite_flow,digest,
    MISSING_PHYSICS
)
from zee_section8_Q2b_chen_FLS_matching_gate import bridge_chen_y_to_fls

def serialized(matrix):
    mat=np.asarray(matrix,complex)
    return {"real":mat.real.tolist(),"imag":mat.imag.tolist()}

class TestIntegratedZeeQ2Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        M,_=target_neutrino_matrix()
        f,_=antisymmetric_f_with_null_condition(M)
        y,rank,_=solve_lepton_yukawa(
            f,M,kappa=scalar_kappa(300,700,1.089))
        assert rank==5
        cls.point={"id":"synthetic","mH1":300.,"mH2":700.,
                   "gamma":1.089,"beta":math.atan(5.6)}
        cls.sol={"candidate_id":"synthetic",
                 "mH1":300.,"mH2":700.,"gamma":1.089,
                 "f":serialized(f),"Y":serialized(y)}

    def test_matched_B2_neutrino_and_truncated_RGE_round_trip(self):
        r=check_matched_finite_flow(
            {"synthetic":self.point},
            {"synthetic":[self.sol]},top=1,steps=12,
            high=10000.,low=700.)
        self.assertEqual(r["n_checked"],1)
        row=r["cases"][0]
        self.assertLess(row["neutrino_algebraic_closure_eV"],1e-9)
        self.assertLess(row["beta_trace_residual_down"],1e-11)
        self.assertLess(row["beta_trace_residual_up"],1e-11)
        self.assertLess(
            r["control_typeII_leptons_final"]["down_max_abs_rho_offdiag"],
            1e-12)
        self.assertLess(
            r["control_typeII_leptons_final"]["up_max_abs_rho_offdiag"],
            1e-12)
        self.assertFalse(r["model_rge_complete"])
        self.assertFalse(r["physical_FCNC_exclusions"])
        self.assertIsNone(r["physical_Zee_allowed"])

    def test_no_missing_B2_rows_accepted(self):
        with self.assertRaisesRegex(ValueError,"Fewer saved B2"):
            check_matched_finite_flow(
                {"synthetic":self.point},{"synthetic":[]},
                top=1,steps=8,high=10000.,low=700.)

    def test_mismatched_candidate_sets_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"scalar IDs differ"):
            check_matched_finite_flow(
                {"synthetic":self.point},{"other":[self.sol]},
                top=1,steps=8,high=10000.,low=700.)

    def test_boundary_typeii_quarks(self):
        y=np.asarray(self.sol["Y"]["real"])+1j*np.asarray(self.sol["Y"]["imag"])
        leptons=bridge_chen_y_to_fls(y,5.6)
        x=quark_boundary(5.6,leptons["Pi1"],leptons["Pi2"])
        np.testing.assert_allclose(x[1],0,atol=0)
        np.testing.assert_allclose(x[2],0,atol=0)
        self.assertEqual(x.shape,(6,3,3))

    def test_missing_physics_explicit_not_allowed(self):
        self.assertIn("NOT_FULL_ZEE_OR_ALLOWED",STATUS)
        self.assertGreater(len(MISSING_PHYSICS),4)
        self.assertTrue(any("LFV" in x for x in MISSING_PHYSICS))

    def test_digest_changes_with_content(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"data"
            p.write_text("first")
            a=digest(p)
            p.write_text("second")
            b=digest(p)
            self.assertNotEqual(a,b)

if __name__=="__main__":
    unittest.main()
