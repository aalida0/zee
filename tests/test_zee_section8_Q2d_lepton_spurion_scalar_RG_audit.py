"""Q2d Zee general-lepton scalar RG spurion structure regressions.

NOT a beta_lambda6/7 derivation or evidence of experimental allowed
Zee model. Only sourced tensor structures and derivative identities.
"""
import math
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_Q2d_lepton_spurion_scalar_RG_audit import (
    STATUS,structures,delta_trace,stored_audit
)
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,scalar_kappa
)

def encode(matrix):
    mat=np.asarray(matrix,complex)
    return {"real":mat.real.tolist(),"imag":mat.imag.tolist()}

class TestQ2dZeeSpurionStructures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=np.random.default_rng(891)
        cls.p1=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.04
        cls.p2=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.03
        cls.f=np.array([[0,.02,.03j],[-.02,0,-.01],[ -.03j,.01,0]],complex)

    def test_weak_lepton_basis_covariant_spurions(self):
        rng=np.random.default_rng(33)
        ul=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))[0]
        ur=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))[0]
        original=structures(self.p1,self.p2,self.f)
        moved=structures(ul.conj().T@self.p1@ur,
                         ul.conj().T@self.p2@ur,
                         ul.T@self.f@ul)
        for key in ("T21","I6","I7"):
            self.assertAlmostEqual(original[key].real,moved[key].real,places=12)
            self.assertAlmostEqual(original[key].imag,moved[key].imag,places=12)
        for key in ("f_frobenius_squared","f_quartic_invariant"):
            self.assertAlmostEqual(original[key],moved[key],places=12)

    def test_exact_typeII_lepton_Z2_zero_spurions(self):
        out=structures(self.p1,np.zeros((3,3),complex),self.f)
        self.assertEqual(out["T21_abs"],0)
        self.assertEqual(out["I6_abs"],0)
        self.assertEqual(out["I7_abs"],0)
        self.assertFalse(out["lambda6_lambda7_RG_stability_proven"])

    def test_generic_complex_leptons_have_nonzero_source_structures(self):
        row=structures(self.p1,self.p2,self.f)
        self.assertGreater(row["T21_abs"],1e-7)
        self.assertGreater(row["I6_abs"],1e-9)
        self.assertGreater(row["I7_abs"],1e-9)
        self.assertEqual(row["f_numerical_rank"],2)
        self.assertFalse(row["complete_Zee_f_beta_calculated"])

    def test_lepton_cross_trace_linear_variation_identity(self):
        rng=np.random.default_rng(96)
        dp1=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.02
        dp2=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.01
        delta=delta_trace(self.p1,self.p2,dp1,dp2)
        eps=1e-5
        t0=structures(self.p1,self.p2)["T21"]
        t1=structures(self.p1+eps*dp1,self.p2+eps*dp2)["T21"]
        self.assertLess(abs((t1-t0)/eps-delta),1e-6)
        self.assertFalse(structures(self.p1,self.p2)[
            "one_loop_quartic_beta_coefficient_calculated"])

    def test_hermitian_conjugation_matters_for_cp_phase(self):
        x=structures(self.p1,self.p2)
        t=np.trace(self.p2@self.p1.conj().T)
        wrong=np.trace(self.p2@self.p1.T)
        self.assertAlmostEqual(x["T21"].real,t.real,places=12)
        self.assertAlmostEqual(x["T21"].imag,t.imag,places=12)
        self.assertGreater(abs(t-wrong),1e-5)

    def test_f_antisymmetric_rank_two_invariant(self):
        x=structures(self.p1,self.p2,self.f)
        self.assertEqual(x["f_numerical_rank"],2)
        self.assertGreater(x["f_frobenius_squared"],0)
        self.assertGreater(x["f_quartic_invariant"],0)
        self.assertAlmostEqual(
            x["f_quartic_invariant"],
            x["f_frobenius_squared"]**2/2,
            places=13)

    def test_f_bad_matrix_rejected(self):
        bad=self.f.copy()
        bad[1,0]=.02
        with self.assertRaisesRegex(ValueError,"antisymmetric"):
            structures(self.p1,self.p2,bad)

    def test_bad_yukawas_or_delta_beta_shapes_rejected(self):
        with self.assertRaises(ValueError):
            structures(np.zeros((2,3)),self.p2)
        with self.assertRaises(ValueError):
            delta_trace(self.p1,self.p2,np.zeros((2,3)),self.p2)

    def test_old_B2_analgebraic_solution_one_matched_spurion(self):
        target,_=target_neutrino_matrix()
        f,_=antisymmetric_f_with_null_condition(target)
        Y,rank,_=solve_lepton_yukawa(
            f,target,kappa=scalar_kappa(300.,700.,1.089))
        self.assertEqual(rank,5)
        point={"id":"synthetic","mH1":300.,"mH2":700.,
               "gamma":1.089,"beta":math.atan(5.6)}
        sol={"candidate_id":"synthetic","mH1":300.,"mH2":700.,
             "gamma":1.089,"f":encode(f),"Y":encode(Y)}
        report=stored_audit({"synthetic":point},
                             {"synthetic":[sol]},top=1,expected=1)
        self.assertEqual(report["count"],1)
        self.assertLess(report["rows"][0]["nu_matrix_closure_eV"],1e-9)
        self.assertIsNone(report["rows"][0]["physically_allowed"])
        self.assertFalse(report["zero_lambda6_lambda7_at_all_scales_proven"])

    def test_fails_closed_on_mismatched_scalar_ids(self):
        with self.assertRaisesRegex(ValueError,"candidate sets differ"):
            stored_audit({"0":{}},{"1":[]},top=1,expected=1)

    def test_status_not_misrepresented_as_complete_RGE(self):
        self.assertIn("NOT_COMPLETE_QUARTIC_RGES",STATUS)

if __name__=="__main__":unittest.main()
