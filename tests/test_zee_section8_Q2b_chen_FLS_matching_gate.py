"""Q2b Chen-FLS lepton convention bridge: exact algebraic unit tests.

No global physical Zee or LFV allowed inference. Only NumPy is needed.
"""
import math
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    scalar_kappa,solve_lepton_yukawa
)
from zee_section8_Q2b_chen_FLS_matching_gate import (
    STATUS,V,LEPTON_MASSES,bridge_chen_y_to_fls,
    local_alignment_source,validate_B2_solution
)
from zee_section8_quark_alignment_one_loop_gate import (
    beta_quarks_2hdm
)

def encode(mat):
    a=np.asarray(mat,complex)
    return {"real":a.real.tolist(),"imag":a.imag.tolist()}

class TestQ2bChenFLSBridge(unittest.TestCase):
    def test_chen_charged_vertex_requires_hermitian_conjugation(self):
        y=np.array([[.02,.005j,.003],
                    [-.007,.1,.03j],
                    [.001j,.005,.06]],complex)
        result=bridge_chen_y_to_fls(y,5.6)
        rho=result["rho"]
        np.testing.assert_allclose(rho,math.sqrt(2)*y.conj().T,
                                   atol=1e-15,rtol=1e-14)
        self.assertGreater(np.max(abs(rho-math.sqrt(2)*y)),1e-3)
        np.testing.assert_allclose(rho.conj().T/math.sqrt(2),y,
                                   atol=1e-15,rtol=1e-14)

    def test_higgs_basis_round_trip_nonhermitian_complex_y(self):
        y=np.arange(9,dtype=float).reshape(3,3)*.0001
        y=y+1j*y[::-1,:]
        for tb in (.5,5.6,20.):
            with self.subTest(tanbeta=tb):
                b=bridge_chen_y_to_fls(y,tb)
                c=1/math.hypot(1,tb);s=tb*c
                np.testing.assert_allclose(
                    c*b["Pi1"]+s*b["Pi2"],b["kappa"],
                    atol=1e-15,rtol=1e-13)
                np.testing.assert_allclose(
                    -s*b["Pi1"]+c*b["Pi2"],b["rho"],
                    atol=1e-15,rtol=1e-13)

    def test_2HDM_beta_source_tangent_matches_complex_trace(self):
        rng=np.random.default_rng(23)
        Y=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.02
        b=bridge_chen_y_to_fls(Y,5.6)
        T=np.trace(b["Pi2"]@b["Pi1"].conj().T)
        G=np.array([[.02,.001,0],[.002,.012,0],[0,0,.04]],complex)
        D=np.array([[.8,.02,.01],[.03,.03,0],[0,.001,.002]],complex)
        Z=np.zeros((3,3),complex)
        bg,bd=beta_quarks_2hdm(
            (G,Z),(Z,D),(b["Pi1"],b["Pi2"]),
            g3=1.18,g2=.65,gp=.36)
        np.testing.assert_allclose(bg[1],T*G,atol=1e-14,rtol=1e-12)
        np.testing.assert_allclose(bd[0],T*D,atol=1e-14,rtol=1e-12)

    def test_trace_basis_invariance_under_unitary_leptons(self):
        rng=np.random.default_rng(87)
        Y=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.003
        b=bridge_chen_y_to_fls(Y,15)
        UL=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))[0]
        UR=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))[0]
        new1=UL.conj().T@b["Pi1"]@UR
        new2=UL.conj().T@b["Pi2"]@UR
        old=np.trace(b["Pi2"]@b["Pi1"].conj().T)
        new=np.trace(new2@new1.conj().T)
        self.assertAlmostEqual(old.real,new.real,places=12)
        self.assertAlmostEqual(old.imag,new.imag,places=12)

    def test_cp_odd_trace_is_independent_of_tanbeta_for_fixed_Higgs_Y(self):
        y=np.array([[.008+.003j,.004,-.002j],
                    [-.001j,.004,.009],
                    [.01,.002j,.04-.005j]],complex)
        vals=[local_alignment_source(y,t)["T_complex"].imag
              for t in (.4,1,5.6,20)]
        self.assertLess(max(vals)-min(vals),1e-14)

    def test_exact_typeII_lepton_alignment_has_zero_source(self):
        tb=5.6
        k=np.diag(np.sqrt(2)*LEPTON_MASSES/V)
        rho=-tb*k
        # In Chen convention Y=rho_dagger/sqrt2
        y=rho.conj().T/math.sqrt(2)
        res=local_alignment_source(y,tb)
        self.assertLess(abs(res["T_complex"]),1e-16)

    def test_old_B2_neutrino_solution_closes_and_matches_charged_widths(self):
        M,_=target_neutrino_matrix()
        f,_=antisymmetric_f_with_null_condition(M)
        gamma=1.089
        Y,rank,_=solve_lepton_yukawa(
            f,M,kappa=scalar_kappa(300.,700.,gamma))
        self.assertEqual(rank,5)
        point={"id":"synthetic",
               "mH1":300.,"mH2":700.,"gamma":gamma,
               "beta":math.atan(5.6)}
        sol={"candidate_id":"synthetic","mH1":300.,
             "mH2":700.,"gamma":gamma,
             "f":encode(f),"Y":encode(Y)}
        out=validate_B2_solution(point,sol,M)
        self.assertLess(out["neutrino_matrix_closure_eV"],1e-9)
        self.assertLess(out["chen_y_reconstruction_error"],1e-13)
        self.assertTrue(out["B2_neutrino_target_is_old_NO_fixed"])
        self.assertFalse(out["complete_LFV"])
        self.assertFalse(out["full_NuFIT61_likelihood"])
        self.assertIsNone(out["physical_Zee_allowed"])
        self.assertIn("NOT_LFV_FCNC_OR_ALLOWED",STATUS)

    def test_mismatched_scalar_solution_fails_closed(self):
        M,_=target_neutrino_matrix()
        f,_=antisymmetric_f_with_null_condition(M)
        Y,_,_=solve_lepton_yukawa(f,M)
        p={"id":"synthetic","mH1":300.,"mH2":700.,
           "gamma":1.089,"beta":math.atan(5.6)}
        s={"candidate_id":"other","mH1":300.,
           "mH2":700.,"gamma":1.089,
           "f":encode(f),"Y":encode(Y)}
        with self.assertRaisesRegex(ValueError,"candidate ID"):
            validate_B2_solution(p,s,M)
        s["candidate_id"]="synthetic"
        s["mH2"]=720.
        with self.assertRaisesRegex(ValueError,"spectrum mismatch"):
            validate_B2_solution(p,s,M)

    def test_bad_Y_rejected(self):
        for y in (np.zeros((2,3)),np.full((3,3),float("nan"))):
            with self.assertRaises(ValueError):
                bridge_chen_y_to_fls(y,5.6)

if __name__=="__main__":
    unittest.main()
