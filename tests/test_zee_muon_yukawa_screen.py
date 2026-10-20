"""Paper2 muon-specific Yukawa column screening; not a cross section."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_muon_yukawa_screen import evaluate,STATUS


def enc(a):
    return {"real":np.asarray(a).real.tolist(),
            "imag":np.asarray(a).imag.tolist()}


def fake():
    f=np.array([[0,1e-3,0],[-1e-3,0,2e-3],
                [0,-2e-3,0]],complex)
    Y=np.zeros((3,3),complex)
    Y[0,1]=.003+.004j
    Y[1,0]=.1
    Y[2,1]=.001
    return {
        "candidate_id":"B4_TEST",
        "gamma":math.pi/4,
        "mH1":220.,"mH2":700.,
        "Y":enc(Y),"f":enc(f),
        "partial_LFV_score_NOT_EXCLUSION":1e-5,
        "neutrino_matrix_closure_eV":1e-16,
        "max_abs_Y":float(np.max(abs(Y))),
        "max_abs_f":float(np.max(abs(f))),
    }


class TestMuonYukawaScreen(unittest.TestCase):
    def test_status_no_cross_section_or_allowed_claim(self):
        self.assertIn("NOT_TCHANNEL_RATE_OR_ALLOWED",STATUS)

    def test_correct_column_not_row(self):
        x=evaluate(fake(),1)
        self.assertAlmostEqual(x["Y_muon_column_norm_squared"],
                               26e-6,delta=1e-15)
        self.assertAlmostEqual(x["Y_muon_ROW_norm_CONTROL"],.1,delta=1e-15)
        self.assertAlmostEqual(x["abs_mixing_overlap_Y_Y"],13e-6,
                               delta=1e-15)

    def test_complex_rephasing_does_not_change_norm(self):
        sol=fake()
        a=evaluate(sol,1)
        for k in ("f","Y"):
            x=np.array(sol[k]["real"])+1j*np.array(sol[k]["imag"])
            sol[k]=enc(x*np.exp(1j*.7))
        b=evaluate(sol,1)
        for k in ("abs_mixing_overlap_Y_Y","abs_mixing_overlap_f_f"):
            self.assertAlmostEqual(a[k],b[k],delta=1e-16)

    def test_no_mixing_implies_zero_overlap(self):
        sol=fake()
        sol["gamma"]=1e-11
        result=evaluate(sol,1)
        self.assertLess(result["abs_mixing_overlap_Y_Y"],1e-15)

    def test_reject_nonantisymmetric_f(self):
        sol=fake()
        sol["f"]=enc(np.eye(3))
        with self.assertRaisesRegex(ValueError,"Non-antisymmetric"):
            evaluate(sol,1)

    def test_reject_bad_neutrino_closure(self):
        sol=fake()
        sol["neutrino_matrix_closure_eV"]=1e-7
        with self.assertRaisesRegex(ValueError,"Invalid B2"):
            evaluate(sol,1)

    def test_reject_nonfinite_complex_yukawas(self):
        sol=fake()
        sol["Y"]["real"][0][1]=float("nan")
        with self.assertRaisesRegex(ValueError,"Invalid complex"):
            evaluate(sol,1)


if __name__=="__main__":
    unittest.main()
